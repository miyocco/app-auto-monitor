"""
監視ロジックモジュール
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import config
import log_analyzer
import status_manager


def check_all_tools() -> Dict[str, Any]:
    """
    全ツールの状態をチェック

    Returns:
        {"overall_status": str, "tools": {...}}
    """
    tools_status = {}

    for tool_config in config.MONITORED_TOOLS:
        tools_status[tool_config["name"]] = check_tool_status(tool_config)

    overall = status_manager.get_overall_status(tools_status)

    result = {
        "last_check": datetime.now(),
        "overall_status": overall,
        "tools": tools_status
    }

    # 状態を保存
    status_manager.save_status(result)

    return result


def check_tool_status(tool_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    個別ツールの状態をチェック

    Args:
        tool_config: ツールの設定

    Returns:
        {"status": str, "last_run": datetime, "process_running": bool, "error_message": str}
    """
    status = {
        "status": "unknown",
        "last_run": None,
        "process_running": False,
        "error_message": None
    }

    # 1. プロセスの稼働確認
    plist_name = tool_config["plist"].replace(".plist", "")
    status["process_running"] = is_process_running(plist_name)

    # 2. ログファイルの最終更新時刻
    log_path = tool_config["path"] / tool_config["log_file"]
    last_run = log_analyzer.get_last_log_time(log_path)
    status["last_run"] = last_run

    # 3. エラーログの確認
    err_path = tool_config["path"] / tool_config["err_file"]
    has_error, error_message = log_analyzer.check_errors(log_path, err_path)
    if has_error:
        status["error_message"] = error_message

    # 4. 総合判定
    status["status"] = determine_status(
        status["process_running"],
        last_run,
        has_error
    )

    return status


def is_process_running(plist_name: str) -> bool:
    """
    LaunchAgentのプロセスが稼働しているか確認

    Args:
        plist_name: plistファイル名（拡張子なし）

    Returns:
        稼働中ならTrue
    """
    try:
        result = subprocess.run(
            ["launchctl", "list", plist_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def determine_status(process_running: bool, last_run: datetime, has_error: bool) -> str:
    """
    総合的な状態を判定

    Args:
        process_running: プロセスが稼働中か
        last_run: 最終実行時刻
        has_error: エラーがあるか

    Returns:
        "ok", "warning", "error"
    """
    if has_error:
        return "error"

    if not process_running:
        return "error"

    if last_run:
        time_since_last_run = datetime.now() - last_run
        if time_since_last_run.total_seconds() > config.STALE_THRESHOLD:
            return "warning"

    if last_run:
        return "ok"

    return "unknown"
