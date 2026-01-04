"""
通知機能モジュール
"""

import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import config


def send_notification(title: str, message: str, sound: str = "default") -> None:
    """
    macOS通知を送信

    Args:
        title: 通知タイトル
        message: 通知メッセージ
        sound: 通知音（"default"など）
    """
    if not config.ENABLE_NOTIFICATIONS:
        return

    try:
        script = f'display notification "{message}" with title "{title}" sound name "{sound}"'
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"通知の送信に失敗: {e}")


def should_notify(tool_name: str, error_message: str) -> bool:
    """
    通知すべきかどうかを判定（頻度制限）

    Args:
        tool_name: ツール名
        error_message: エラーメッセージ

    Returns:
        通知すべきならTrue
    """
    history = load_notification_history()

    # このツールの通知履歴を確認
    if tool_name in history:
        last_notification_str = history[tool_name].get("last_notification")
        last_error = history[tool_name].get("error_message")

        if last_notification_str and last_error == error_message:
            last_notification = datetime.fromisoformat(last_notification_str)
            time_since_last = datetime.now() - last_notification

            # 同じエラーが cooldown 時間内なら通知しない
            if time_since_last.total_seconds() < config.NOTIFICATION_COOLDOWN:
                return False

    return True


def record_notification(tool_name: str, error_message: str) -> None:
    """
    通知履歴を記録

    Args:
        tool_name: ツール名
        error_message: エラーメッセージ
    """
    history = load_notification_history()

    history[tool_name] = {
        "last_notification": datetime.now().isoformat(),
        "error_message": error_message
    }

    save_notification_history(history)


def load_notification_history() -> Dict[str, Any]:
    """
    通知履歴を読み込み

    Returns:
        通知履歴
    """
    if not config.NOTIFICATION_HISTORY_FILE.exists():
        return {}

    try:
        with open(config.NOTIFICATION_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_notification_history(history: Dict[str, Any]) -> None:
    """
    通知履歴を保存

    Args:
        history: 通知履歴
    """
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(config.NOTIFICATION_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
