import os
from dotenv import load_dotenv
from google import genai

# .env から APIキーを読み込む
load_dotenv()
API_KEY = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=API_KEY)

print("🔍 今のAPIキーで使えるモデル一覧を検索中...\n")

try:
    # APIからモデルのリストを取得して、名前だけをシンプルに表示
    for model in client.models.list():
        print(f"- {model.name}")
except Exception as e:
    print(f"エラーが発生しました: {e}")
