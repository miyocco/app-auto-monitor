# 新ツール作成ガイド

このドキュメントは、新しい自動分析ツールを作成し、LaunchAgentで自動化して、app-auto-monitorに登録するまでの完全ガイドです。

---

## 対象ツール

このガイドは以下のような自動分析ツールに適用できます:
- 定期的にデータを取得・分析するツール
- バックグラウンドで稼働するツール
- エラー時に通知が必要なツール

例: app-ai-insights, app-obsidian-insights, app-feedly-insights

---

## Part 1: 最小構成（自動化に必須）

### 1.1 必要なファイル構造

```
app-[tool-name]/
├── main.py                            # 実行スクリプト（必須）
├── logs/
│   ├── scheduler.log                  # 標準出力ログ（自動生成）
│   └── scheduler.err                  # エラーログ（自動生成）
└── com.miyocco.app-[tool-name].plist  # LaunchAgent設定（必須）
```

**注意**: 上記は自動化に必要な最小構成です。プロジェクト管理のために以下を追加することを推奨しますが、自動化には不要です:
- `config.py`, `requirements.txt`, `.env`, `.gitignore`
- `README.md`, `SPEC.md`, `ARCHITECTURE.md`, `TODO.md`, `CHANGELOG.md`

### 1.2 main.py テンプレート

```python
#!/usr/bin/env python3
"""
app-[tool-name]

[ツールの説明をここに記載]
"""

import logging

# ロガー設定（LaunchAgentがログファイルにリダイレクト）
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """メイン処理"""
    logger.info("=== 処理開始 ===")

    try:
        # ここにメイン処理を記述
        # 例: データ取得、分析、保存など

        logger.info("=== 処理完了 ===")

    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise  # エラーを再発生させて終了ステータスを1にする


if __name__ == "__main__":
    main()
```

**ポイント**:
- `logs/`ディレクトリの作成は不要（LaunchAgentが自動で作成）
- ログファイルへの出力はLaunchAgentのplistで設定
- エラー時は`raise`で例外を再発生させれば、標準エラーに出力される

### 1.3 LaunchAgent plist テンプレート

ファイル名: `com.miyocco.app-[tool-name].plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- ラベル（一意の識別子） -->
    <key>Label</key>
    <string>com.miyocco.app-[tool-name]</string>

    <!-- 実行するコマンド -->
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]/main.py</string>
    </array>

    <!-- 起動時に自動実行 -->
    <key>RunAtLoad</key>
    <true/>

    <!-- 定期実行（例: 1時間ごと） -->
    <key>StartInterval</key>
    <integer>3600</integer>

    <!-- プロセスが終了しても再起動しない（定期実行のみ） -->
    <key>KeepAlive</key>
    <false/>

    <!-- 標準出力のリダイレクト先 -->
    <key>StandardOutPath</key>
    <string>/Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]/logs/scheduler.log</string>

    <!-- 標準エラーのリダイレクト先 -->
    <key>StandardErrorPath</key>
    <string>/Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]/logs/scheduler.err</string>

    <!-- 作業ディレクトリ -->
    <key>WorkingDirectory</key>
    <string>/Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]</string>

    <!-- 環境変数 -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

### 1.4 実行間隔の設定オプション

#### パターン1: 定期実行（推奨）

```xml
<!-- 1時間ごと -->
<key>StartInterval</key>
<integer>3600</integer>

<key>KeepAlive</key>
<false/>
```

#### パターン2: 常駐アプリ（ツールバーアプリなど）

```xml
<!-- StartIntervalは削除 -->

<key>KeepAlive</key>
<true/>
```

#### パターン3: 特定時刻に実行

```xml
<!-- 毎日9時に実行 -->
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

---

## Part 2: ログ出力（重要）

app-auto-monitorが正しく監視できるように、ログを`logs/scheduler.log`と`logs/scheduler.err`に出力してください。

### 2.1 推奨ログフォーマット

すべてのツールで以下のフォーマットを**推奨**します（必須ではありません）:

```
[YYYY-MM-DD HH:MM:SS] LEVEL: message
```

**出力例**:
```
[2026-01-05 10:30:45] INFO: === 処理開始 ===
[2026-01-05 10:30:46] INFO: データ取得完了: 10件
[2026-01-05 10:30:47] INFO: 分析完了: 5件の新規記事
[2026-01-05 10:30:48] INFO: === 処理完了 ===
[2026-01-05 10:30:50] ERROR: API接続エラー: timeout
```

**推奨する理由**:
- **パース可能**: app-auto-monitorがログ解析しやすい
- **視認性**: 時刻、重要度、内容が一目でわかる
- **一貫性**: すべてのツールで同じ形式

**ただし柔軟性を保つ**:
- ツールの性質によっては異なる形式が適切な場合もある
- 最低限「タイムスタンプ + メッセージ」があればOK

### 2.2 ログ出力の実装方法

#### 方法1: LaunchAgentで自動リダイレクト（推奨）

plistファイルで`StandardOutPath`と`StandardErrorPath`を設定すれば、自動的にログファイルに出力されます。

```xml
<key>StandardOutPath</key>
<string>/Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]/logs/scheduler.log</string>

<key>StandardErrorPath</key>
<string>/Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]/logs/scheduler.err</string>
```

main.pyでは通常通り`logging`を使うだけでOKです:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

logger.info("処理開始")
logger.info("データ取得完了: 10件")
logger.info("処理完了")
```

#### 方法2: Python内で明示的にファイル出力

```python
import logging
from pathlib import Path

log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_dir / "scheduler.log"),
        logging.StreamHandler()
    ]
)
```

---

## Part 3: LaunchAgentの設定

### 3.1 LaunchAgentのインストール

```bash
# plistファイルをLaunchAgentsにコピー
cp com.miyocco.app-[tool-name].plist ~/Library/LaunchAgents/

# 起動
launchctl load ~/Library/LaunchAgents/com.miyocco.app-[tool-name].plist

# 状態確認
launchctl list | grep app-[tool-name]

# 停止
launchctl unload ~/Library/LaunchAgents/com.miyocco.app-[tool-name].plist
```

### 3.2 動作確認

```bash
# 手動実行してログを確認
cd /Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]
python3 main.py

# ログファイルを確認
cat logs/scheduler.log
cat logs/scheduler.err

# ログを監視
tail -f logs/scheduler.log
```

---

## Part 4: app-auto-monitorへの登録

### 4.1 config.pyに追加

ファイル: `/Users/miyoshi-koichi/cursor/miyocco/app-auto-monitor/config.py`

```python
MONITORED_TOOLS = [
    # 既存のツール...

    # 新しいツールを追加
    {
        "name": "[tool-name]",  # 内部識別名
        "display_name": "[Tool Name]",  # メニューに表示される名前
        "path": Path.home() / "cursor" / "miyocco" / "app-[tool-name]",
        "plist": "com.miyocco.app-[tool-name].plist",
        "log_file": "logs/scheduler.log",
        "err_file": "logs/scheduler.err",
    },
]
```

### 4.2 app-auto-monitorの再起動

```bash
# app-auto-monitorを再起動して設定を反映
launchctl unload ~/Library/LaunchAgents/com.miyocco.app-auto-monitor.plist
launchctl load ~/Library/LaunchAgents/com.miyocco.app-auto-monitor.plist
```

### 4.3 ツールバーで確認

1. ツールバーのapp-auto-monitorアイコンをクリック
2. 新しいツールが一覧に表示されているか確認
3. 状態が🟢（正常）になっているか確認

---

## Part 5: チェックリスト（AI向け）

新ツールの自動化を完了するために、以下のチェックリストを使用してください。

### Phase 1: 最小構成（自動化に必須）
- [ ] プロジェクトフォルダ作成
- [ ] main.py作成
- [ ] logs/ディレクトリ作成（空でOK）
- [ ] LaunchAgent plist作成
- [ ] 手動実行で動作確認
- [ ] LaunchAgentに登録
- [ ] 自動実行の動作確認

### Phase 2: 監視設定
- [ ] app-auto-monitor/config.pyに追加
- [ ] app-auto-monitorを再起動
- [ ] ツールバーで状態確認
- [ ] エラー通知のテスト

### Phase 3: プロジェクト管理（推奨だが自動化には不要）
- [ ] config.py作成
- [ ] requirements.txt作成
- [ ] .env.example作成
- [ ] .gitignore作成
- [ ] README.md, SPEC.md, ARCHITECTURE.md, TODO.md, CHANGELOG.md作成

---

## Part 6: トラブルシューティング

### LaunchAgentが起動しない

```bash
# ログを確認
cat /Users/miyoshi-koichi/cursor/miyocco/app-[tool-name]/logs/scheduler.err

# plistの構文チェック
plutil -lint com.miyocco.app-[tool-name].plist

# 権限を確認
ls -l ~/Library/LaunchAgents/com.miyocco.app-[tool-name].plist
```

### app-auto-monitorに表示されない

1. config.pyの設定を再確認
2. ログファイルのパスが正しいか確認
3. app-auto-monitorのログを確認: `cat /Users/miyoshi-koichi/cursor/miyocco/app-auto-monitor/logs/monitor.log`

### エラーログが記録されない

- plistのStandardErrorPathが正しいか確認
- ログディレクトリが存在するか確認
- Python内でもエラーハンドリングを追加

---

## Part 7: 参考例

既存のapp-ai-insightsの設定を確認してください:

- plist: `/Users/miyoshi-koichi/cursor/miyocco/app-ai-insights/com.miyocco.app-ai-insights.plist`
- config.py: `/Users/miyoshi-koichi/cursor/miyocco/app-auto-monitor/config.py`（MONITORED_TOOLS）

---

## まとめ

このガイドに従うことで、新しいツールを:
1. **自動化**（LaunchAgentで定期実行）
2. **監視**（app-auto-monitorで状態確認）
3. **通知**（エラー時に即座にお知らせ）

を一気に実現できます。

AIがこのガイドを読み込むことで、ユーザーの指示に従って迅速に自動化を完了できるようになります。
