# app-auto-monitor

複数の自動分析ツールの稼働状況を1つのツールバーアイコンで統合管理するmacOS専用アプリケーション。

## 概要

このツールは、以下のような自動分析ツールの状態を監視し、エラー検知・ログ確認・一括再起動を可能にします:

- app-ai-insights
- app-obsidian-insights
- *(将来的に5〜10個まで拡張可能)*

### 主な機能

- 🔍 **状態監視**: 各ツールのプロセス稼働状況とログを定期チェック
- 🔔 **エラー通知**: 問題発生時にmacOS通知で即座にお知らせ
- 📋 **ログ表示**: 各ツールのログを1クリックで確認
- 🔄 **一括再起動**: 全ツールをまとめて再起動
- 🚫 **Dock非表示**: ツールバーのみに表示され、Dockを混雑させない

## インストール

### 1. 依存パッケージのインストール

```bash
cd /Users/miyoshi-koichi/cursor/miyocco/app-auto-monitor
pip3 install -r requirements.txt
```

### 2. 環境変数の設定（必要に応じて）

```bash
cp .env.example .env
# .envファイルを編集（現状は不要）
```

### 3. 監視対象ツールの設定

[config.py](config.py) で監視対象のツールを設定できます。

### 4. LaunchAgentに登録

```bash
# plistファイルをLaunchAgentsにコピー
cp com.miyocco.app-auto-monitor.plist ~/Library/LaunchAgents/

# 起動
launchctl load ~/Library/LaunchAgents/com.miyocco.app-auto-monitor.plist
```

## 使い方

### ツールバーからの操作

1. **状態確認**: ツールバーのアイコンをクリックして各ツールの状態を確認
   - 🟢 正常稼働中
   - 🟡 警告あり
   - 🔴 エラー発生

2. **ログ表示**: ツール名をクリックしてログファイルを開く

3. **一括再起動**: メニューから「🔄 すべて再起動」を選択

4. **終了**: メニューから「❌ 終了」を選択

### 手動実行（デバッグ用）

```bash
python3 menubar_app.py
```

### 停止方法

```bash
launchctl unload ~/Library/LaunchAgents/com.miyocco.app-auto-monitor.plist
```

## 新しいツールの追加

新しい自動分析ツールを監視対象に追加する手順は [docs/TOOL_TEMPLATE.md](docs/TOOL_TEMPLATE.md) を参照してください。

## トラブルシューティング

### ツールバーにアイコンが表示されない

```bash
# LaunchAgentの状態を確認
launchctl list | grep app-auto-monitor

# ログを確認
cat ~/cursor/miyocco/app-auto-monitor/logs/monitor.log
```

### 監視が動作しない

1. [config.py](config.py) の設定を確認
2. 監視対象ツールが正しくインストールされているか確認
3. ログファイルのパスが正しいか確認

## 開発情報

- **言語**: Python 3.8+
- **ツールバーアプリ**: rumps（macOS専用）
- **プロセス管理**: subprocess + launchctl
- **通知**: osascript（macOS通知センター）

詳細は以下のドキュメントを参照:

- [SPEC.md](SPEC.md): 詳細な仕様書
- [ARCHITECTURE.md](ARCHITECTURE.md): 技術設計書
- [TODO.md](TODO.md): 開発タスク
- [CHANGELOG.md](CHANGELOG.md): 変更履歴

## ライセンス

個人用プロジェクト
