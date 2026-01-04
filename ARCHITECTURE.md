# app-auto-monitor - アーキテクチャ設計書

## 1. システム全体像

```
┌─────────────────────────────────────────────────┐
│                  macOS System                   │
├─────────────────────────────────────────────────┤
│  LaunchAgent (自動起動・常駐)                    │
│    ↓                                            │
│  menubar_app.py (ツールバーUI)                   │
│    ├─ rumps (メニューバーアプリフレームワーク)    │
│    └─ Timer (定期実行: 5分ごと)                  │
│         ↓                                       │
│  monitor.py (監視ロジック)                       │
│    ├─ プロセス稼働確認 (launchctl)               │
│    ├─ ログ解析 (log_analyzer.py)                │
│    └─ 状態判定                                   │
│         ↓                                       │
│  status_manager.py (状態管理)                    │
│    └─ status.json (永続化)                      │
│         ↓                                       │
│  notifier.py (通知機能)                          │
│    └─ osascript (macOS通知)                     │
└─────────────────────────────────────────────────┘
         ↓ 監視対象
┌─────────────────────────────────────────────────┐
│  監視対象ツール                                   │
│    ├─ app-ai-insights                           │
│    ├─ app-obsidian-insights                     │
│    └─ (将来的に追加されるツール)                  │
└─────────────────────────────────────────────────┘
```

## 2. モジュール設計

### 2.1 menubar_app.py

**役割**: ツールバーUIとメインの制御ロジック

**主要クラス**:
```python
class AutoMonitorApp(rumps.App):
    """メニューバー常駐アプリ"""

    def __init__(self):
        # アイコン・メニューの初期化
        # Timerの設定（5分ごとにcheck_statusを実行）

    def check_status(self, _):
        """定期的に状態をチェック"""
        # monitor.check_all_tools() を呼び出し
        # 状態に応じてアイコンを更新
        # エラーがあれば通知

    def show_logs(self, tool_name):
        """ログファイルを開く"""
        # subprocess.Popen(["open", "-t", log_path])

    def restart_all(self, _):
        """全ツールを再起動"""
        # restarter.restart_all_tools()

    def quit_app(self, _):
        """アプリを終了"""
        # LaunchAgentをunload
        # rumps.quit_application()
```

**依存関係**:
- rumps
- AppKit (Dock非表示用)
- monitor.py
- status_manager.py
- notifier.py
- restarter.py

### 2.2 monitor.py

**役割**: 各ツールの状態を監視

**主要関数**:
```python
def check_all_tools() -> dict:
    """全ツールの状態をチェック"""
    # config.MONITORED_TOOLSを巡回
    # 各ツールをcheck_tool_status()でチェック
    # 結果をstatus_manager.save_status()で保存
    # 返り値: {"overall": "ok/warning/error", "tools": {...}}

def check_tool_status(tool_config: dict) -> dict:
    """個別ツールの状態をチェック"""
    # 1. プロセス稼働確認 (is_process_running)
    # 2. ログファイルの最終更新時刻 (get_last_run_time)
    # 3. エラーログの確認 (log_analyzer.check_errors)
    # 4. 総合判定 (determine_status)
    # 返り値: {"status": "ok/warning/error", "last_run": datetime, ...}

def is_process_running(plist_name: str) -> bool:
    """LaunchAgentのプロセスが稼働しているか確認"""
    # launchctl list | grep <plist_name>

def get_last_run_time(log_path: Path) -> Optional[datetime]:
    """ログファイルの最終更新時刻を取得"""
    # log_path.stat().st_mtime

def determine_status(process_running: bool, last_run: datetime,
                    has_error: bool) -> str:
    """総合的な状態を判定"""
    # エラーあり → "error"
    # プロセス停止 → "error"
    # 長時間実行なし → "warning"
    # それ以外 → "ok"
```

### 2.3 log_analyzer.py

**役割**: ログファイルを解析してエラーを検出

**主要関数**:
```python
def check_errors(log_path: Path, err_path: Path) -> tuple[bool, Optional[str]]:
    """エラーログをチェック"""
    # err_pathのファイルサイズが0より大きければエラーあり
    # 最後の1行を取得してエラーメッセージとして返す
    # 返り値: (has_error, error_message)

def parse_log_timestamp(log_line: str) -> Optional[datetime]:
    """ログの行からタイムスタンプを抽出"""
    # [2026-01-05 10:30:00] のような形式を想定
    # 正規表現でパース
```

### 2.4 status_manager.py

**役割**: 状態をJSONファイルで永続化

**主要関数**:
```python
def save_status(status: dict) -> None:
    """状態をstatus.jsonに保存"""
    # data/status.json に書き込み

def load_status() -> dict:
    """status.jsonから状態を読み込み"""
    # data/status.json から読み込み
    # ファイルがなければデフォルト値を返す

def get_overall_status(tools_status: dict) -> str:
    """全体の状態を判定"""
    # いずれかが "error" なら "error"
    # いずれかが "warning" なら "warning"
    # すべて "ok" なら "ok"
```

**データ形式**:
```json
{
  "last_check": "2026-01-05T10:30:00",
  "overall_status": "ok",
  "tools": {
    "ai-insights": {
      "status": "ok",
      "last_run": "2026-01-05T10:25:00",
      "process_running": true,
      "error_message": null
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

### 2.5 notifier.py

**役割**: macOS通知センターに通知を表示

**主要関数**:
```python
def send_notification(title: str, message: str, sound: str = "default") -> None:
    """macOS通知を送信"""
    # osascript を使用
    # display notification "message" with title "title" sound name "sound"

def should_notify(tool_name: str, error_message: str) -> bool:
    """通知すべきかどうかを判定（頻度制限）"""
    # notification_history.json を確認
    # 同じエラーが1時間以内に通知済みならFalse
    # そうでなければTrue

def record_notification(tool_name: str, error_message: str) -> None:
    """通知履歴を記録"""
    # notification_history.json に追記
```

**通知履歴形式**:
```json
{
  "ai-insights": {
    "last_notification": "2026-01-05T10:30:00",
    "error_message": "Process not running"
  }
}
```

### 2.6 restarter.py

**役割**: ツールの再起動処理

**主要関数**:
```python
def restart_all_tools() -> dict:
    """全ツールを再起動"""
    # config.MONITORED_TOOLSを巡回
    # 各ツールをrestart_tool()で再起動
    # 返り値: {"success": bool, "results": {...}}

def restart_tool(tool_config: dict) -> bool:
    """個別ツールを再起動"""
    # 1. launchctl unload <plist>
    # 2. 2秒待機
    # 3. launchctl load <plist>
    # 4. 5秒待機
    # 5. monitor.check_tool_status()で確認
    # 返り値: True (成功) / False (失敗)
```

### 2.7 config.py

**役割**: 設定の一元管理

**主要設定**:
```python
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
]

# 監視設定
CHECK_INTERVAL = 300  # 5分（秒単位）
STALE_THRESHOLD = 3600  # 1時間実行されていなければ警告
NOTIFICATION_COOLDOWN = 3600  # 同じエラーの通知は1時間に1回まで

# パス設定
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
STATUS_FILE = DATA_DIR / "status.json"
NOTIFICATION_HISTORY_FILE = DATA_DIR / "notification_history.json"

# 通知設定
ENABLE_NOTIFICATIONS = True
NOTIFICATION_SOUND = "default"
```

## 3. データフロー

### 3.1 起動時のフロー

```
1. LaunchAgent起動
   ↓
2. menubar_app.py実行
   ↓
3. AppKit.NSBundle で LSUIElement = 1 設定（Dock非表示）
   ↓
4. AutoMonitorApp初期化
   ↓
5. rumps.Timer設定（5分ごと）
   ↓
6. 初回check_status()実行
   ↓
7. ツールバーにアイコン表示
```

### 3.2 定期チェックのフロー

```
1. Timer発火（5分ごと）
   ↓
2. check_status()呼び出し
   ↓
3. monitor.check_all_tools()
   ↓
4. 各ツールをチェック
   ├─ プロセス稼働確認
   ├─ ログファイル確認
   └─ エラーログ確認
   ↓
5. status_manager.save_status()
   ↓
6. 状態に応じてアイコン更新
   ↓
7. エラーがあれば通知
   ├─ notifier.should_notify()で頻度チェック
   └─ notifier.send_notification()
```

### 3.3 ユーザー操作のフロー

#### ログ表示
```
1. ツール名クリック
   ↓
2. show_logs(tool_name)
   ↓
3. ログファイルパスを取得
   ↓
4. subprocess.Popen(["open", "-t", log_path])
```

#### 一括再起動
```
1. 「すべて再起動」クリック
   ↓
2. restart_all()
   ↓
3. restarter.restart_all_tools()
   ↓
4. 各ツールを順番に再起動
   ├─ launchctl unload
   ├─ 2秒待機
   ├─ launchctl load
   └─ 5秒待機
   ↓
5. 状態を再チェック
   ↓
6. 結果を通知
```

## 4. エラーハンドリング

### 4.1 監視対象ツールのエラー
- **検出方法**: エラーログファイルのサイズチェック、プロセス稼働確認
- **対応**: 状態を"error"に変更、通知を送信、アイコンを🔴に変更

### 4.2 監視アプリ自体のエラー
- **ログへの記録**: logs/monitor.errに記録
- **再起動**: LaunchAgentのKeepAliveで自動再起動
- **通知**: 可能であれば通知を送信

### 4.3 再起動失敗
- **検出方法**: 再起動後の状態チェック
- **対応**: 通知で警告、ログに記録

## 5. パフォーマンス最適化

### 5.1 状態チェックの最適化
- ファイル存在確認を最初に実行
- プロセスチェックは`launchctl list`を1回だけ実行
- ログファイルは最後の数行のみ読み込む（tail相当）

### 5.2 メモリ使用量の最適化
- 大きなログファイルは全読み込みしない
- status.jsonは必要時のみ読み込み
- 通知履歴は古いエントリを定期的に削除

### 5.3 CPU使用量の最適化
- チェック間隔は5分（頻繁すぎない）
- 状態が変わらない場合はアイコン更新をスキップ

## 6. セキュリティ考慮事項

### 6.1 ファイルアクセス
- ログファイルは読み取り専用でアクセス
- status.jsonは適切な権限で保存（644）

### 6.2 プロセス操作
- launchctlは現在のユーザーのプロセスのみ操作
- sudoは使用しない

### 6.3 通知
- エラーメッセージにセンシティブな情報を含めない
- 通知頻度制限でスパムを防止

## 7. 拡張性

### 7.1 新しいツールの追加
- config.pyのMONITORED_TOOLSに追加するだけ
- ログフォーマットが統一されていれば自動的に監視可能

### 7.2 監視項目の追加
- monitor.pyのcheck_tool_status()を拡張
- 例: CPU使用率、メモリ使用量、実行回数など

### 7.3 通知方法の追加
- notifier.pyを拡張
- 例: Slack通知、メール通知など

## 8. テスト戦略

### 8.1 単体テスト
- 各モジュールの関数を個別にテスト
- モック使用（subprocess, osascript等）

### 8.2 統合テスト
- ダミーのツールを作成して実際に監視
- エラー状態を意図的に作ってテスト

### 8.3 手動テスト
- 実際にツールバーから操作
- 通知の表示確認
- 再起動機能の動作確認

## 9. デプロイ手順

1. 依存パッケージのインストール
   ```bash
   pip3 install -r requirements.txt
   ```

2. LaunchAgent登録
   ```bash
   cp com.miyocco.app-auto-monitor.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.miyocco.app-auto-monitor.plist
   ```

3. 動作確認
   - ツールバーにアイコンが表示されるか
   - メニューが正しく動作するか
   - 状態チェックが正しく行われるか

## 10. トラブルシューティング

### アイコンが表示されない
- LaunchAgentが起動しているか確認: `launchctl list | grep app-auto-monitor`
- ログを確認: `cat logs/monitor.log`

### 監視が動作しない
- config.pyの設定を確認
- 監視対象ツールのパスが正しいか確認
- ログファイルが存在するか確認

### 通知が表示されない
- ENABLE_NOTIFICATIONS=Trueか確認
- 通知権限が許可されているか確認（システム設定）
- 通知頻度制限に引っかかっていないか確認
