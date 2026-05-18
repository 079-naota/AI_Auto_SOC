# 完全プライバシー保護型 自律AI-SOCシステム (Auto-SOC)

## 概要 (Project Overview)
本プロジェクトは、多様なハニーポット群が検知したセキュリティアラートを大規模言語モデル（LLM）を用いて自動で相関分析し、SOC（Security Operations Center）アナリストのトリアージ業務とインシデント対応を自律的に支援するシステムの実証実験コードです。

現在はクラウドAPIを用いた実脅威インテリジェンスの自動収集と分析（Phase 2）を稼働させつつ、最終的には企業の機密情報（ログ）を外部に送信しない**「ローカルLLM（Llama 3等）を用いた完全プライバシー保護環境での自律SOC（Phase 3）」**の構築を目指しています。

## アーキテクチャと実行環境 (Architecture & Environment)
システムは「マルチベクター・データ収集ノード」と「管理・分析ノード」に分離されています。

* **データ収集・監視ノード (Multi-Vector Honeypots & SIEM):**
  * インフラ: VPS
  * SIEM/IDS: Wazuh Manager
  * ハニーポット群: Cowrie (SSH), Snare/Tanner (Web), RedisHoneypot (DB), Dionaea (IoT/Malware)
* **管理・分析ノード (Analysis Plane):**
  * セキュア通信: Tailscale (VPNを用いたOut-of-Band管理)
  * データセット構築 (Current): Google Gemini API (プロンプト最適化と教師データ抽出用)
  * ローカル推論 (Planned): Llama 3 8B (NVIDIA RTX GPU環境でのQLoRA追加学習・推論)
  * 言語: Python 3.x

## 主な機能と研究テーマ (Key Features & Research Focus)
1. **マルチベクター相関分析:** SSH、Web、DB、IoTの異なる経路からの攻撃ログをWazuhで集約し、点のアラートを線（キルチェーン）としてAIに解読させます。
2. **チャンクサイズ（収集間隔）の最適化実験:** AIが攻撃の文脈（コンテキスト）を最も正確に理解できる最適なログの抽出間隔を決定するため、複数の時間軸（5分〜3時間）で並行して分析評価を行っています。
3. **高品質データセットの自動生成:** Llama 3などのローカルLLMをセキュリティ特化にファインチューニング（追加学習）するための、「生のログ・整形済みJSON・AIレポート」のペアデータを自動生成します。
4. **Git Auto-Push:** 分析結果を脅威インテリジェンスとして自動的に本リポジトリへコミット＆プッシュします。

## ディレクトリ構成 (Repository Structure)
実験のフェーズに合わせ、収集間隔（時間枠）ごとにディレクトリを分割してデータを評価しています。

```text
.
├── analyze_alerts.py       # メインの自動分析・Git連携スクリプト
├── .env                    # 環境変数（APIキー等 ※Git非公開）
├── .gitignore              # 機密ファイルやキャッシュの除外設定
└── data/reports/           # 収集間隔ごとの自動生成レポートディレクトリ
    ├── 5min/               # 5分間隔での分析結果
    ├── 10min/              # 10分間隔での分析結果
    ├── 30min/              # 30分間隔での分析結果
    ├── 1h/                 # 1時間間隔での分析結果
    └── 3h/                 # 3時間間隔での分析結果
        └── YYYYMMDDHHMMSS/ # 実行ごとのパッケージ
            ├── raw_logs.log  # 抽出した未加工の生アラート
            ├── data.json     # AI推論用に最適化されたデータ
            └── report.md     # キルチェーン・トリアージ結果
