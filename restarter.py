"""
再起動機能モジュール
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, Any
import config
import monitor


def restart_all_tools() -> Dict[str, Any]:
    """
    全ツールを再起動

    Returns:
        {"success": bool, "results": {...}}
    """
    results = {}

    for tool_config in config.MONITORED_TOOLS:
        tool_name = tool_config["name"]
        results[tool_name] = restart_tool(tool_config)

    # 全て成功したか判定
    all_success = all(result["success"] for result in results.values())

    return {
        "success": all_success,
        "results": results
    }


def restart_tool(tool_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    個別ツールを再起動

    Args:
        tool_config: ツールの設定

    Returns:
        {"success": bool, "message": str}
    """
    plist_name = tool_config["plist"].replace(".plist", "")
    plist_path = Path.home() / "Library" / "LaunchAgents" / tool_config["plist"]

    if not plist_path.exists():
        return {
            "success": False,
            "message": f"plistファイルが見つかりません: {plist_path}"
        }

    try:
        # 1. unload
        subprocess.run(
            ["launchctl", "unload", str(plist_path)],
            capture_output=True,
            text=True
        )

        # 2. 2秒待機
        time.sleep(2)

        # 3. load
        subprocess.run(
            ["launchctl", "load", str(plist_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # 4. 5秒待機
        time.sleep(5)

        # 5. 状態確認
        status = monitor.check_tool_status(tool_config)
        if status["process_running"]:
            return {
                "success": True,
                "message": "再起動成功"
            }
        else:
            return {
                "success": False,
                "message": "再起動後もプロセスが起動していません"
            }

    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"再起動失敗: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"予期しないエラー: {e}"
        }
