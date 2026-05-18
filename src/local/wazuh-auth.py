import os
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# .envファイルから環境変数をロード
load_dotenv()

# 環境変数から設定値を取得
WAZUH_IP = os.getenv("WAZUH_IP")
USERNAME = os.getenv("WAZUH_USERNAME")
PASSWORD = os.getenv("WAZUH_PASS")

# 環境変数の読み込み漏れを検証（フェイルセーフ）
if not all([WAZUH_IP, USERNAME, PASSWORD]):
    print("[-] エラー: .envファイルから環境変数を取得できない。設定を確認すること。")
    exit(1)

# Wazuh Manager APIエンドポイント
API_URL = f"https://{WAZUH_IP}:55000/security/user/authenticate"

# 自己署名証明書（Self-Signed Certificate）に対するSSL警告を抑止
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_wazuh_token():
    print(f"[*] Wazuh API ({WAZUH_IP}) に対して認証リクエストを送信中...")
    
    try:
        # Basic認証プロトコルによるGETリクエストの発行
        response = requests.get(
            API_URL,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            verify=False  # TLS/SSL証明書の検証をバイパス
        )

        # HTTPステータスコードの評価
        if response.status_code == 200:
            # JSONレスポンスからJWTトークンをパース
            token = response.json()['data']['token']
            print("[+] 認証成功。JWTトークンを取得した。\n")
            
            # トークンの先頭50文字を出力（デバッグ用）
            print(f"Token: {token[:50]}...")
            return token
            
        else:
            print(f"[-] 認証失敗。HTTP Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[-] ネットワーク通信エラーが発生: {e}")
        return None

if __name__ == "__main__":
    get_wazuh_token()