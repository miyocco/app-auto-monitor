"""
設定ファイル
"""

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
        "plist": "com.miyocco.app-obsidian-insights.scheduler.plist",
        "log_file": "logs/scheduler.log",
        "err_file": "logs/scheduler.err",
    },
    {
        "name": "feedly-insights",
        "display_name": "feedly-insights",
        "path": Path.home() / "cursor" / "miyocco" / "app-feedly-insights",
        "plist": "com.miyocco.app-feedly-insights.plist",
        "log_file": "logs/scheduler.log",
        "err_file": "logs/scheduler.err",
    },
]

# 監視設定
CHECK_INTERVAL = 300  # 5分（秒単位）
STALE_THRESHOLD = 21600  # 6時間実行されていなければ警告（秒単位）※実行間隔4時間の1.5倍
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
