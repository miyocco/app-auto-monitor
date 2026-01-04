# app-auto-monitor - 仕様書

## 1. 概要

### 1.1 目的
複数の自動分析ツール（feedly-insights, ai-insights, obsidian-insights等）の稼働状況を1つのツールバーアイコンで統合管理し、エラー検知・ログ確認・一括再起動を可能にする。

### 1.2 背景
- 現在、複数の自動分析ツールが独立して稼働している
- 各ツールの状態を個別に確認するのは手間がかかる
- エラーが発生しても気づきにくい
- ツールバーが複数のアイコンで混雑する問題を避けたい
- 今後もツールが増える可能性がある（5〜10個程度まで拡張）

### 1.3 ユーザー体験

#### 正常時
```
[ツールバー]
📊 ← クリック

[ドロップダウンメニュー]
📊 Auto Monitor
────────────────
🟢 feedly-insights     正常稼働中
🟢 ai-insights         正常稼働中
🟢 obsidian-insights   正常稼働中
────────────────
🔄 すべて再起動
📋 ログを表示
❌ 終了
```

#### エラー発生時
```
[ツールバー]
🔴 ← アイコンが赤く変化（通知も表示）

[ドロップダウンメニュー]
📊 Auto Monitor
────────────────
🟢 feedly-insights     正常稼働中
🔴 ai-insights         エラー発生
🟢 obsidian-insights   正常稼働中
────────────────
🔄 すべて再起動
📋 ログを表示
❌ 終了
```

#### ログ表示
```
[各ツール名をクリック]
→ そのツールのログファイルをデフォルトエディタで開く

例: ai-insights をクリック
→ ~/cursor/miyocco/app-ai-insights/logs/auto_monitor.log を開く
```

---

## 2. 機能要件

### 2.1 状態監視機能
- **監視対象**: 設定ファイルで指定されたツール（初期値: feedly-insights, ai-insights, obsidian-insights）
- **監視項目**:
  - プロセスの稼働状態（LaunchAgentによる起動確認）
  - 最終実行時刻（ログファイルの最終更新時刻）
  - エラーログの有無（*.errファイルの内容チェック）
- **監視間隔**: 5分ごと（設定可能）
- **状態の種類**:
  - 🟢 正常: プロセス稼働中、エラーなし
  - 🟡 警告: プロセス稼働中だが、しばらく実行されていない
  - 🔴 エラー: プロセス停止、またはエラーログあり
  - ⚪ 停止中: 意図的に停止されている

### 2.2 通知機能
- **通知タイミング**: エラー検知時（🔴状態になったとき）
- **通知内容**: 「[ツール名] がエラーを検出しました」
- **通知方式**: macOS通知センター（osascript使用）
- **通知頻度制限**: 同じエラーは1時間に1回まで

### 2.3 ログ表示機能
- **表示方法**: 各ツール名をクリック → ログファイルをデフォルトエディタで開く
- **対象ログ**:
  - 標準出力ログ: `~/cursor/miyocco/app-[tool-name]/logs/auto_monitor.log`
  - エラーログ: `~/cursor/miyocco/app-[tool-name]/logs/auto_monitor.err`
- **複数ログ対応**: 両方のファイルが存在する場合は両方開く

### 2.4 一括再起動機能
- **対象**: 監視対象の全ツール
- **実行内容**:
  1. 各ツールのLaunchAgentを`launchctl unload`で停止
  2. 2秒待機
  3. 各ツールのLaunchAgentを`launchctl load`で再起動
- **実行確認**: 再起動後、5秒待ってから状態を再チェック
- **エラーハンドリング**: 再起動失敗時は通知で警告

### 2.5 ツールバーUI
- **アイコン表示**:
  - 正常時: 📊（緑色）
  - 警告時: 📊（黄色）
  - エラー時: 📊（赤色）
- **Dock非表示**: `LSUIElement = 1` でDockに表示しない
- **メニュー構成**:
  ```
  📊 Auto Monitor
  ────────────────
  [監視対象ツール一覧]（各行クリックでログ表示）
  ────────────────
  🔄 すべて再起動
  📋 ログを表示（全ツールのログを一括表示）
  ❌ 終了
  ```

---

## 3. 非機能要件

### 3.1 パフォーマンス
- 状態チェック時間: 1秒以内（全ツール合計）
- メモリ使用量: 50MB以下
- CPU使用率: アイドル時1%以下

### 3.2 ユーザビリティ
- ツールバーアイコン1つで全体を把握できる
- エラー時は即座に視覚的にわかる
- ログ表示は1クリックでアクセス可能

### 3.3 拡張性
- 監視対象ツールの追加・削除が簡単（設定ファイル編集）
- 将来的に10個までのツールに対応可能
- 新しいツールの監視ロジックを追加しやすい設計

### 3.4 信頼性
- 監視アプリ自体が落ちても自動再起動（LaunchAgentのKeepAlive）
- エラー通知の重複を防ぐ
- ログファイルが大きくなりすぎないようローテーション

---

## 4. 技術仕様

### 4.1 システム構成
```
[macOS LaunchAgent]
  ↓ 起動
[menubar_app.py] ← メインエントリーポイント（rumps使用）
  ↓ 定期実行（5分ごと）
[monitor.py] ← 監視ロジック
  ↓ チェック
[各ツールのログファイル・プロセス状態]
  ↓ 結果
[状態管理] (status.json)
  ↓ 更新
[ツールバーUI] ← ユーザーに表示
```

### 4.2 技術スタック
- **言語**: Python 3.8以上
- **ツールバーアプリ**: rumps（macOS専用）
- **プロセス管理**: subprocess + launchctl
- **通知**: osascript（macOS通知センター）
- **状態管理**: JSON形式のファイル
- **ログ解析**: 正規表現パターンマッチング

### 4.3 ファイル構成
```
app-auto-monitor/
├── menubar_app.py                # ツールバーアプリ（メイン）
├── monitor.py                    # 監視ロジック
├── config.py                     # 設定ファイル
├── status_manager.py             # 状態管理
├── log_analyzer.py               # ログ解析
├── notifier.py                   # 通知機能
├── restarter.py                  # 再起動ロジック
├── com.miyocco.app-auto-monitor.plist  # LaunchAgent設定
├── assets/
│   └── monitor-iconTemplate.png  # ツールバーアイコン
├── logs/
│   ├── monitor.log               # 監視ログ
│   └── monitor.err               # エラーログ
├── data/
│   ├── status.json               # 現在の状態
│   └── notification_history.json # 通知履歴
├── requirements.txt              # 依存パッケージ
├── .env.example                  # 環境変数テンプレート
├── README.md                     # 使い方
├── SPEC.md                       # この仕様書
├── ARCHITECTURE.md               # 技術設計書
├── TODO.md                       # タスク管理
└── CHANGELOG.md                  # 変更履歴
```

### 4.4 設定項目
```python
# config.py
import os
from pathlib import Path

# 監視対象ツール
MONITORED_TOOLS = [
    {
        "name": "ai-insights",
        "display_name": "ai-insights",
        "path": Path.home() / "cursor" / "miyocco" / "app-ai-insights",
        "plist": "com.miyocco.app-ai-insights.scheduler.plist",
        "log_file": "logs/scheduler.log",
        "err_file": "logs/scheduler.err",
    },
    {
        "name": "obsidian-insights",
        "display_name": "obsidian-insights",
        "path": Path.home() / "cursor" / "miyocco" / "app-obsidian-insights",
        "plist": "com.miyocco.app-obsidian-insights.plist",
        "log_file": "logs/scheduler.log",
        "err_file": "logs/scheduler.err",
    },
    # feedly-insightsは未自動化のため除外
]

# 監視設定
CHECK_INTERVAL = 300  # 5分（秒単位）
STALE_THRESHOLD = 3600  # 1時間実行されていなければ警告（秒単位）
NOTIFICATION_COOLDOWN = 3600  # 同じエラーの通知は1時間に1回まで（秒単位）

# パス設定
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
STATUS_FILE = DATA_DIR / "status.json"
NOTIFICATION_HISTORY_FILE = DATA_DIR / "notification_history.json"

# 通知設定
ENABLE_NOTIFICATIONS = True
NOTIFICATION_SOUND = "default"  # macOS通知音
```

### 4.5 状態管理フォーマット
```json
{
  "last_check": "2026-01-05T10:30:00",
  "overall_status": "error",
  "tools": {
    "feedly-insights": {
      "status": "ok",
      "last_run": "2026-01-05T10:25:00",
      "process_running": true,
      "error_message": null
    },
    "ai-insights": {
      "status": "error",
      "last_run": "2026-01-05T08:00:00",
      "process_running": false,
      "error_message": "Process not running"
    },
    "obsidian-insights": {
      "status": "ok",
      "last_run": "2026-01-05T10:20:00",
      "process_running": true,
      "error_message": null
    }
  }
}
```

### 4.6 Dock非表示の実装
#### menubar_app.py
```python
import AppKit
import rumps

if __name__ == "__main__":
    # Dockアイコンを非表示にする（アプリ起動前に設定）
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info["LSUIElement"] = "1"

    app = AutoMonitorApp()
    app.run()
```

#### com.miyocco.app-auto-monitor.plist
```xml
<key>EnvironmentVariables</key>
<dict>
    <key>LSUIElement</key>
    <string>1</string>
</dict>
```

### 4.7 監視ロジックの詳細
```python
def check_tool_status(tool_config):
    """ツールの状態をチェック"""
    status = {
        "status": "unknown",
        "last_run": None,
        "process_running": False,
        "error_message": None
    }

    # 1. プロセスの稼働確認
    plist_path = Path.home() / "Library" / "LaunchAgents" / tool_config["plist"]
    if plist_path.exists():
        result = subprocess.run(
            ["launchctl", "list", tool_config["plist"].replace(".plist", "")],
            capture_output=True,
            text=True
        )
        status["process_running"] = result.returncode == 0

    # 2. ログファイルの最終更新時刻
    log_file = tool_config["path"] / tool_config["log_file"]
    if log_file.exists():
        status["last_run"] = datetime.fromtimestamp(log_file.stat().st_mtime)

    # 3. エラーログの確認
    err_file = tool_config["path"] / tool_config["err_file"]
    if err_file.exists() and err_file.stat().st_size > 0:
        with open(err_file, 'r') as f:
            last_error = f.readlines()[-1]  # 最後の1行
            status["error_message"] = last_error.strip()

    # 4. 総合判定
    if status["error_message"]:
        status["status"] = "error"
    elif not status["process_running"]:
        status["status"] = "error"
    elif status["last_run"]:
        time_since_last_run = datetime.now() - status["last_run"]
        if time_since_last_run.total_seconds() > STALE_THRESHOLD:
            status["status"] = "warning"
        else:
            status["status"] = "ok"
    else:
        status["status"] = "unknown"

    return status
```

---

## 5. 実装の優先順位

### Phase 1: MVP
- [ ] プロジェクト構造作成
- [ ] 設定ファイル（config.py）
- [ ] 監視ロジック（monitor.py）
  - [ ] プロセス稼働確認
  - [ ] ログ解析
  - [ ] 状態判定
- [ ] 状態管理（status_manager.py）
- [ ] ツールバーアプリ（menubar_app.py）
  - [ ] 基本UI
  - [ ] 状態表示
  - [ ] Dock非表示
- [ ] LaunchAgent設定

### Phase 2: 通知・ログ表示
- [ ] 通知機能（notifier.py）
  - [ ] エラー通知
  - [ ] 通知頻度制限
- [ ] ログ表示機能
  - [ ] 個別ツールのログ表示
  - [ ] 全ツールのログ一括表示

### Phase 3: 再起動機能
- [ ] 再起動ロジック（restarter.py）
  - [ ] 個別ツール再起動
  - [ ] 全ツール一括再起動
  - [ ] 再起動後の状態確認

### Phase 4: 改善
- [ ] アイコンのカスタマイズ
- [ ] ツール追加の自動検出
- [ ] ログローテーション
- [ ] 統計情報表示（稼働時間、エラー回数など）

---

## 6. 制約事項

### 6.1 技術的制約
- **macOS専用**: rumps、LaunchAgent、osascriptを使用
- **Python 3.8以上**: 型ヒント、pathlib等の機能を使用

### 6.2 運用上の制約
- **監視対象の制限**: 設定ファイルに登録されたツールのみ監視
- **ログフォーマット**: 各ツールのログが一定の形式である必要がある
- **権限**: LaunchAgentの操作に必要な権限が必要

---

## 7. テスト計画

### 7.1 単体テスト
- プロセス稼働確認が正しく動作するか
- ログ解析が正しくエラーを検出するか
- 状態判定ロジックが正しいか

### 7.2 統合テスト
- ツールバーアプリから監視ロジックまでの全フローが動作するか
- エラー発生時に通知が正しく表示されるか
- 再起動機能が正しく動作するか

### 7.3 ユーザビリティテスト
- ツールバーUIが直感的か
- エラー時にすぐに気づけるか
- ログ表示が使いやすいか

---

## 8. 参考情報

### 8.1 類似ツール
- Docker Desktop: 複数のコンテナを1つのアイコンで管理
- MenuMeters: システムモニターをツールバーに表示
- iStat Menus: 統合システム監視ツール

### 8.2 参照プロジェクト
- [app-idea-now/menubar_app.py](../app-idea-now/menubar_app.py): ツールバーアプリの実装例
- [app-idea-now/com.miyocco.app-idea-now.plist](../app-idea-now/com.miyocco.app-idea-now.plist): LaunchAgent設定例

---

## 9. 今後の拡張案

### 9.1 ダッシュボード機能
- Webブラウザで詳細な統計情報を表示
- グラフで稼働時間・エラー率を可視化

### 9.2 アラート設定
- 特定のツールだけ通知を無効化
- エラーの重要度に応じて通知方法を変更

### 9.3 自動修復機能
- エラー検知時に自動で再起動を試みる
- 再起動失敗時のみ通知

### 9.4 リモート監視
- 複数のMacを1つのダッシュボードで監視
- チームメンバーのツール稼働状況を共有
