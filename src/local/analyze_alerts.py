import os
import json
import requests
import urllib3
import argparse # 引数を受け取るためのモジュールを追加
from datetime import datetime, timedelta, timezone # 時間計算用
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from google import genai

# 環境変数のロード
load_dotenv()

# 各種APIキーと設定値の取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WAZUH_IP = os.getenv("WAZUH_IP")
INDEXER_USER = os.getenv("INDEXER_USERNAME")
INDEXER_PASS = os.getenv("INDEXER_PASS")

# フェイルセーフ
missing_vars = []
if not GEMINI_API_KEY: missing_vars.append("GEMINI_API_KEY")
if not WAZUH_IP: missing_vars.append("WAZUH_IP")
if not INDEXER_USER: missing_vars.append("INDEXER_USERNAME")
if not INDEXER_PASS: missing_vars.append("INDEXER_PASS")

if missing_vars:
    print(f"[-] エラー: .envファイルから以下の環境変数が取得できない: {', '.join(missing_vars)}")
    exit(1)

# SSL警告の抑止
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
INDEXER_URL = f"https://{WAZUH_IP}:9200/wazuh-alerts*/_search"

def fetch_recent_alerts(minutes):
    """Wazuh Indexerから指定した時間（分）前からのレベル5以上のアラートをすべて抽出する"""
    
    # 【変更点】Pythonでの複雑な時間計算（datetime）をすべて削除し、
    # Wazuh Indexerが直接理解できる "now-Xm"（今からX分前）という最強の書式を使います。
    
    query = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"rule.level": {"gte": 5}}},
                    {"range": {"@timestamp": {"gte": f"now-{minutes}m"}}} # ここを修正
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "asc"}}], # 時系列順（古い順）
        "size": 50
    }

    try:
        response = requests.post(
            INDEXER_URL,
            auth=HTTPBasicAuth(INDEXER_USER, INDEXER_PASS),
            headers={"Content-Type": "application/json"},
            data=json.dumps(query),
            verify=False
        )
        if response.status_code == 200:
            hits = response.json().get("hits", {}).get("hits", [])
            return [hit["_source"] for hit in hits] if hits else []
        else:
            print(f"[-] ログ抽出失敗。HTTP Status: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"[-] ネットワーク通信エラー: {e}")
        return []

def analyze_with_gemini(alert_data_list, minutes):
    """Gemini APIに複数のアラートリストを渡し、相関分析を行わせる"""
    print(f"[*] Geminiによる相関分析（対象: 過去{minutes}分間の {len(alert_data_list)}件のアラート）を実行中...")
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        あなたは高度なスキルを持つSOCアナリストである。
        以下のJSONデータは、過去{minutes}分間にシステムで発生した複数のセキュリティアラートを時系列（古い順）に並べた配列である。
        これらのアラートを個別の事象としてではなく、**「同一の攻撃者による一連のサイバー攻撃（相関関係）」**である可能性を考慮して深く分析し、必ず**Markdown形式**でレポートを作成せよ。
        
        【アラートデータ（時系列順）】
        {json.dumps(alert_data_list, indent=2, ensure_ascii=False)}
        
        【出力フォーマット】
        # セキュリティインシデント相関分析レポート
        
        ## 1. 攻撃キャンペーンの全体像
        (複数のアラートから読み取れる、攻撃者の真の目的と侵入のシナリオを時系列で解説)
        
        ## 2. 深刻度評価
        (Critical/High/Medium/Low のいずれかと、その技術的根拠。複合攻撃の場合は深刻度を高く見積もること)
        
        ## 3. 検知された主要な脅威 (MITRE ATT&CK)
        (どのアラートがどの戦術・技術に該当するかを箇条書きで整理)
        
        ## 4. 推奨される初動対応と封じ込め策
        (システム全体を守るために次に取るべき具体的なアクション、調査コマンドや緩和策など)
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"[-] Gemini API エラー: {e}"

if __name__ == "__main__":
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description="Wazuhアラートの相関分析スクリプト")
    parser.add_argument("--minutes", type=int, default=5, help="何分前までのアラートを取得するか (デフォルト: 5分)")
    args = parser.parse_args()

    print(f"[*] Wazuh Indexerから過去 {args.minutes} 分間のアラートを取得中...")
    alerts = fetch_recent_alerts(args.minutes)
    
    if alerts:
        print("="*60)
        print(f"[*] 取得完了。合計 {len(alerts)} 件のアラートを検知。")
        for i, alert in enumerate(alerts, 1):
             timestamp = alert.get('@timestamp')
             description = alert.get('rule', {}).get('description')
             print(f"    - [{i}] {timestamp}: {description}")
        
        # Geminiによる分析の実行
        analysis_result = analyze_with_gemini(alerts, args.minutes)
        
        # --- レポート＆生ログ保存処理 ---
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Markdownレポートの保存
        md_filename = f"correlation_report_{current_time}.md"
        md_filepath = os.path.join(report_dir, md_filename)
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(analysis_result)
            
        # 2. 生のJSONデータ（アーティファクト）の保存
        json_filename = f"correlation_raw_{current_time}.json"
        json_filepath = os.path.join(report_dir, json_filename)
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=4, ensure_ascii=False) # 複数のアラートのリストを保存
            
        print(f"\n[+] 分析完了。以下のパスに結果を保存した:")
        print(f"    - レポート: {md_filepath}")
        print(f"    - 生データ: {json_filepath}")
        print("="*60)
    else:
        print(f"[-] 過去 {args.minutes} 分間に分析対象のアラートは存在しなかった。")