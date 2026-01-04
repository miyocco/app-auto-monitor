#!/usr/bin/env python3
"""
メニューバーアプリ
rumpsを使用したメニューバー常駐アプリケーション
"""

import rumps
import subprocess
import sys
from pathlib import Path
import AppKit

import config
import monitor
import notifier
import restarter
import status_manager


class AutoMonitorApp(rumps.App):
    """メニューバー常駐アプリ"""

    def __init__(self):
        # アイコンのパスを取得
        project_root = Path(__file__).parent
        icon_path = project_root / "assets" / "monitor-iconTemplate.png"

        # アイコンが使えない場合は絵文字をフォールバック
        icon = str(icon_path) if icon_path.exists() else None

        super(AutoMonitorApp, self).__init__(
            "📊",  # アイコンが使えない場合のフォールバック
            icon=icon,
            quit_button=None,
            template=True
        )

        # 初期メニューを作成
        self.update_menu()

        # 5分ごとにチェック
        self.timer = rumps.Timer(self.check_status, config.CHECK_INTERVAL)
        self.timer.start()

        # 起動時に即座にチェック実行
        self.check_status(None)

    def update_menu(self):
        """メニューを更新"""
        # 現在の状態を読み込み
        status = status_manager.load_status()
        tools_status = status.get("tools", {})

        menu_items = ["📊 Auto Monitor", None]  # ヘッダーとセパレータ

        # 各ツールの状態を表示
        for tool_config in config.MONITORED_TOOLS:
            tool_name = tool_config["name"]
            display_name = tool_config["display_name"]

            if tool_name in tools_status:
                tool_status = tools_status[tool_name]["status"]
                icon = self._get_status_icon(tool_status)
                status_text = self._get_status_text(tool_status)
                menu_items.append(f"{icon} {display_name}: {status_text}")
            else:
                menu_items.append(f"⚪️ {display_name}: 不明")

        # セパレータと操作メニュー
        menu_items.extend([
            None,
            "🔄 すべて再起動",
            "📋 ログを表示",
            None,
            "❌ 終了"
        ])

        self.menu.clear()
        for item in menu_items:
            if item is None:
                self.menu.add(rumps.separator)
            elif item.startswith("🔄"):
                self.menu.add(rumps.MenuItem(item, callback=self.restart_all))
            elif item.startswith("📋"):
                self.menu.add(rumps.MenuItem(item, callback=self.show_all_logs))
            elif item.startswith("❌"):
                self.menu.add(rumps.MenuItem(item, callback=self.quit_app))
            elif item.startswith(("🟢", "🟡", "🔴", "⚪️")):
                # ツール名の行はクリック可能にしてログ表示
                tool_name = self._extract_tool_name(item)
                self.menu.add(rumps.MenuItem(item, callback=lambda sender, tn=tool_name: self.show_tool_log(sender, tn)))
            else:
                self.menu.add(item)

    def check_status(self, _):
        """定期的に状態をチェック"""
        try:
            # 全ツールの状態をチェック
            status = monitor.check_all_tools()

            # メニューを更新
            self.update_menu()

            # アイコンを更新
            overall_status = status["overall_status"]
            self._update_icon(overall_status)

            # エラーがあれば通知
            for tool_name, tool_status in status["tools"].items():
                if tool_status["status"] == "error" and tool_status["error_message"]:
                    if notifier.should_notify(tool_name, tool_status["error_message"]):
                        notifier.send_notification(
                            "Auto Monitor",
                            f"{tool_name} でエラーを検出しました",
                            config.NOTIFICATION_SOUND
                        )
                        notifier.record_notification(tool_name, tool_status["error_message"])

        except Exception as e:
            print(f"状態チェック中にエラー: {e}")

    def show_tool_log(self, _, tool_name: str):
        """ツールのログを表示"""
        # ツール設定を検索
        tool_config = None
        for tc in config.MONITORED_TOOLS:
            if tc["name"] == tool_name:
                tool_config = tc
                break

        if not tool_config:
            rumps.alert(title="エラー", message=f"ツール '{tool_name}' の設定が見つかりません")
            return

        # ログファイルを開く
        log_path = tool_config["path"] / tool_config["log_file"]
        err_path = tool_config["path"] / tool_config["err_file"]

        if log_path.exists():
            subprocess.Popen(["open", "-t", str(log_path)])

        if err_path.exists():
            subprocess.Popen(["open", "-t", str(err_path)])

    def show_all_logs(self, _):
        """全ツールのログを表示"""
        for tool_config in config.MONITORED_TOOLS:
            log_path = tool_config["path"] / tool_config["log_file"]
            err_path = tool_config["path"] / tool_config["err_file"]

            if log_path.exists():
                subprocess.Popen(["open", "-t", str(log_path)])

            if err_path.exists():
                subprocess.Popen(["open", "-t", str(err_path)])

    def restart_all(self, _):
        """全ツールを再起動"""
        # 確認ダイアログ
        response = rumps.alert(
            title="確認",
            message="全ツールを再起動しますか？",
            ok="再起動",
            cancel="キャンセル"
        )

        if response == 1:  # OK
            try:
                result = restarter.restart_all_tools()

                if result["success"]:
                    rumps.alert(title="成功", message="全ツールの再起動が完了しました")
                else:
                    failed = [name for name, r in result["results"].items() if not r["success"]]
                    rumps.alert(
                        title="一部失敗",
                        message=f"以下のツールの再起動に失敗しました:\n" + "\n".join(failed)
                    )

                # 状態を再チェック
                self.check_status(None)

            except Exception as e:
                rumps.alert(title="エラー", message=f"再起動中にエラーが発生しました:\n{e}")

    def quit_app(self, _):
        """アプリを終了"""
        try:
            plist_file = Path.home() / "Library" / "LaunchAgents" / "com.miyocco.app-auto-monitor.plist"

            # LaunchAgentを停止
            if plist_file.exists():
                subprocess.run(["launchctl", "unload", str(plist_file)])

            # アプリを終了
            rumps.quit_application()
        except Exception as e:
            rumps.alert(title="終了エラー", message=str(e))
            rumps.quit_application()

    def _get_status_icon(self, status: str) -> str:
        """状態に応じたアイコンを返す"""
        if status == "ok":
            return "🟢"
        elif status == "warning":
            return "🟡"
        elif status == "error":
            return "🔴"
        else:
            return "⚪️"

    def _get_status_text(self, status: str) -> str:
        """状態に応じたテキストを返す"""
        if status == "ok":
            return "正常稼働中"
        elif status == "warning":
            return "警告あり"
        elif status == "error":
            return "エラー発生"
        else:
            return "不明"

    def _update_icon(self, overall_status: str):
        """アイコンを更新"""
        icon_emoji = self._get_status_icon(overall_status)
        self.title = icon_emoji

    def _extract_tool_name(self, menu_item: str) -> str:
        """メニュー項目からツール名を抽出"""
        # "🟢 ai-insights     正常稼働中" のような形式から "ai-insights" を抽出
        parts = menu_item.split()
        if len(parts) >= 2:
            return parts[1]
        return ""


if __name__ == "__main__":
    # Dockアイコンを非表示にする（アプリ起動前に設定）
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info["LSUIElement"] = "1"

    app = AutoMonitorApp()
    app.run()
