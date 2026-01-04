# app-auto-monitor - TODO

## 現在の状態

**Phase**: 初期設定
**最終更新**: 2026-01-05

---

## 実装タスク

### Phase 1: MVP（基本機能）

#### プロジェクト構造
- [x] プロジェクトフォルダ作成
- [x] GitHubリポジトリ作成
- [x] 標準ドキュメント作成（README, SPEC, ARCHITECTURE, TODO, CHANGELOG）
- [ ] requirements.txt作成
- [ ] .gitignore作成
- [ ] .env.example作成
- [ ] ディレクトリ構造作成（data/, logs/, assets/, docs/）

#### 設定ファイル
- [ ] config.py実装
  - [ ] MONITORED_TOOLS設定
  - [ ] 監視設定（間隔、閾値）
  - [ ] パス設定
  - [ ] 通知設定

#### 監視ロジック
- [ ] monitor.py実装
  - [ ] check_all_tools()
  - [ ] check_tool_status()
  - [ ] is_process_running()
  - [ ] get_last_run_time()
  - [ ] determine_status()

#### ログ解析
- [ ] log_analyzer.py実装
  - [ ] check_errors()
  - [ ] parse_log_timestamp()

#### 状態管理
- [ ] status_manager.py実装
  - [ ] save_status()
  - [ ] load_status()
  - [ ] get_overall_status()

#### ツールバーUI
- [ ] menubar_app.py実装
  - [ ] AutoMonitorApp基本構造
  - [ ] アイコン設定
  - [ ] メニュー構成
  - [ ] Dock非表示設定（LSUIElement）
  - [ ] check_status()タイマー実装
  - [ ] 状態表示UI

#### LaunchAgent
- [ ] com.miyocco.app-auto-monitor.plist作成
- [ ] インストールスクリプト作成

---

### Phase 2: 通知・ログ表示

#### 通知機能
- [ ] notifier.py実装
  - [ ] send_notification()
  - [ ] should_notify()（頻度制限）
  - [ ] record_notification()

#### ログ表示機能
- [ ] show_logs()実装
  - [ ] 個別ツールのログ表示
  - [ ] 全ツールのログ一括表示
  - [ ] エラーログと標準ログの両方を開く

---

### Phase 3: 再起動機能

#### 再起動ロジック
- [ ] restarter.py実装
  - [ ] restart_all_tools()
  - [ ] restart_tool()
  - [ ] 再起動後の状態確認

#### UI統合
- [ ] 「すべて再起動」メニュー項目
- [ ] 再起動中の表示
- [ ] 再起動結果の通知

---

### Phase 4: 改善・最適化

#### UI改善
- [ ] カスタムアイコン作成（assets/monitor-iconTemplate.png）
- [ ] 状態別のアイコン表示（🟢🟡🔴）
- [ ] メニュー項目のレイアウト調整

#### パフォーマンス最適化
- [ ] ログファイルの読み込み最適化（tail相当）
- [ ] 状態チェックの並列化
- [ ] メモリ使用量の削減

#### エラーハンドリング
- [ ] 監視アプリ自体のエラーログ記録
- [ ] 例外処理の追加
- [ ] リトライロジック

#### ログローテーション
- [ ] 古いログの自動削除
- [ ] ログファイルサイズ制限
- [ ] 通知履歴の定期クリーンアップ

---

### Phase 5: ドキュメント・テンプレート

#### 自動化テンプレート
- [ ] docs/TOOL_TEMPLATE.md作成
  - [ ] 新ツール作成時のチェックリスト
  - [ ] LaunchAgent plistテンプレート
  - [ ] ログフォーマット仕様

#### AI用ガイド
- [ ] docs/AI_AUTOMATION_GUIDE.md作成
  - [ ] 自動化の完全な手順
  - [ ] app-auto-monitorへの登録方法
  - [ ] 推奨ログフォーマット

---

## テストタスク

### 単体テスト
- [ ] monitor.pyのテスト
- [ ] log_analyzer.pyのテスト
- [ ] status_manager.pyのテスト
- [ ] notifier.pyのテスト
- [ ] restarter.pyのテスト

### 統合テスト
- [ ] 起動〜状態チェックのフロー
- [ ] エラー検知〜通知のフロー
- [ ] ログ表示機能
- [ ] 再起動機能

### 手動テスト
- [ ] ツールバーUI操作
- [ ] 通知表示
- [ ] Dock非表示確認
- [ ] 実際のツールで動作確認

---

## 既知の課題

現在なし

---

## 今後の拡張案

### 機能追加
- [ ] 統計情報表示（稼働時間、エラー回数）
- [ ] ダッシュボード機能（Web UI）
- [ ] 自動修復機能（エラー検知時に自動再起動）
- [ ] リモート監視（複数Mac対応）

### 対応ツール追加
- [ ] app-feedly-insights（自動化後）
- [ ] 将来的に追加される新ツール

---

## 優先度

**高**: Phase 1（MVP機能）
**中**: Phase 2〜3（通知・再起動）
**低**: Phase 4〜5（改善・ドキュメント）

---

## メモ

- app-feedly-insightsはまだ自動化していないため、初期の監視対象から除外
- ツール追加を簡単にするためのテンプレート作成が重要
- AI向けガイドを充実させて、新ツール追加の自動化を促進
