import os
import requests
import json
import urllib3
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

WAZUH_IP = os.getenv("WAZUH_IP")
INDEXER_USER = os.getenv("INDEXER_USERNAME")
INDEXER_PASS = os.getenv("INDEXER_PASS")

if not all([WAZUH_IP, INDEXER_USER, INDEXER_PASS]):
    print("[-] エラー: .envファイルからIndexerの環境変数を取得できない。")
    exit(1)

# SSL警告の抑止
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Wazuh Indexer APIエンドポイント（アラートのインデックスを指定）
INDEXER_URL = f"https://{WAZUH_IP}:9200/wazuh-alerts*/_search"

def fetch_recent_alerts():
    print(f"[*] Wazuh Indexer ({WAZUH_IP}:9200) へログ抽出リクエストを送信中...")
    
    # OpenSearchに対する検索クエリ
    # 条件: 深刻度(rule.level)が5以上のアラートを、最新順(desc)に5件取得
    query = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"rule.level": {"gte": 5}}}
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": 5
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
            data = response.json()
            hits = data.get("hits", {}).get("hits", [])
            print(f"[+] ログ抽出成功。{len(hits)}件のアラートを取得した。\n")
            
            for hit in hits:
                source = hit["_source"]
                timestamp = source.get("@timestamp")
                rule = source.get("rule", {})
                level = rule.get("level")
                description = rule.get("description")
                
                print(f"[{timestamp}] Level: {level} | {description}")
            
            return hits
        else:
            print(f"[-] リクエスト失敗。HTTP Status: {response.status_code}")
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"[-] ネットワーク通信エラーが発生: {e}")
        return None

if __name__ == "__main__":
    fetch_recent_alerts()