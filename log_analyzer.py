"""
ログファイル解析モジュール
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import re


def check_errors(log_path: Path, err_path: Path) -> Tuple[bool, Optional[str]]:
    """
    エラーログをチェック

    Args:
        log_path: 標準ログファイルのパス
        err_path: エラーログファイルのパス

    Returns:
        (has_error, error_message)
    """
    # エラーログファイルが存在し、サイズが0より大きければエラーあり
    if err_path.exists() and err_path.stat().st_size > 0:
        try:
            with open(err_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    # 最後の1行を取得
                    last_error = lines[-1].strip()
                    return (True, last_error)
        except Exception:
            return (True, "エラーログの読み込みに失敗")

    return (False, None)


def get_last_log_time(log_path: Path) -> Optional[datetime]:
    """
    ログファイルの最終更新時刻を取得

    Args:
        log_path: ログファイルのパス

    Returns:
        最終更新時刻（datetime）、存在しない場合はNone
    """
    if log_path.exists():
        return datetime.fromtimestamp(log_path.stat().st_mtime)
    return None


def parse_log_timestamp(log_line: str) -> Optional[datetime]:
    """
    ログの行からタイムスタンプを抽出

    Args:
        log_line: ログの1行

    Returns:
        タイムスタンプ（datetime）、解析できない場合はNone
    """
    # [2026-01-05 10:30:00] のような形式を想定
    pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]'
    match = re.search(pattern, log_line)

    if match:
        try:
            timestamp_str = match.group(1)
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

    return None
