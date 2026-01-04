"""
状態管理モジュール
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import config


def save_status(status: Dict[str, Any]) -> None:
    """
    状態をstatus.jsonに保存

    Args:
        status: 状態データ
    """
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # datetimeをISO形式の文字列に変換
    status_serializable = _make_serializable(status)

    with open(config.STATUS_FILE, 'w') as f:
        json.dump(status_serializable, f, indent=2, ensure_ascii=False)


def load_status() -> Dict[str, Any]:
    """
    status.jsonから状態を読み込み

    Returns:
        状態データ、ファイルがなければデフォルト値
    """
    if not config.STATUS_FILE.exists():
        return _get_default_status()

    try:
        with open(config.STATUS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return _get_default_status()


def get_overall_status(tools_status: Dict[str, Dict[str, Any]]) -> str:
    """
    全体の状態を判定

    Args:
        tools_status: 各ツールの状態

    Returns:
        "ok", "warning", "error", "unknown"のいずれか
    """
    statuses = [tool["status"] for tool in tools_status.values()]

    if "error" in statuses:
        return "error"
    elif "warning" in statuses:
        return "warning"
    elif "unknown" in statuses:
        return "unknown"
    else:
        return "ok"


def _make_serializable(obj: Any) -> Any:
    """
    オブジェクトをJSON serializable に変換
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: _make_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    else:
        return obj


def _get_default_status() -> Dict[str, Any]:
    """
    デフォルトの状態を返す
    """
    return {
        "last_check": None,
        "overall_status": "unknown",
        "tools": {}
    }
