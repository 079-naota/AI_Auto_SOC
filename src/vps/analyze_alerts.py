import json
import os
import time
import datetime
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from google import genai


# 1. パスの固定と環境変数の読み込み

# __file__ は VPS/analyze_alerts.py を指すため、.parent.parent で Auto_soc を指定
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

ENV_PATH = PROJECT_ROOT / '.env'
REPORTS_DIR = PROJECT_ROOT / "Reports/3h"
JSON_LOG_DIR = PROJECT_ROOT / "Json-Log"
DATASET_FILE = PROJECT_ROOT / "soc_training_dataset.jsonl"
HISTORY_FILE = PROJECT_ROOT / "analyzed_ips.json"  

load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.environ.get('GEMINI_API_KEY')
LOG_FILE_PATH = os.environ.get('WAZUH_ALERT_LOG_PATH')
TARGET_RULE_ID = os.environ.get('TARGET_RULE_ID')

vpn_ip = os.environ.get('VPN_IP_ADRESS')
public_ip = os.environ.get('PUBLIC_IP_ADRESS')
IGNORE_IPS = [ip for ip in (vpn_ip, public_ip) if ip is not None]

#同じIPは12時間再分析しない
COOL_OFF_HOURS = 12

# 新しいGemini SDKのクライアント初期化
client = genai.Client(api_key=API_KEY)
MODEL_NAME = 'gemini-2.5-flash'


# 2. ログの集約 (攻撃者IPごとのキルチェーン構築)

attack_chains = {}
try:
    with open(LOG_FILE_PATH, 'r') as f:
        for line in f:
            try:
                alert = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            
            if alert.get('rule', {}).get('id') == TARGET_RULE_ID:
                data = alert.get('data', {})
                src_ip = data.get('src_ip')
                
                if src_ip and (src_ip not in IGNORE_IPS):
                    if src_ip not in attack_chains:
                        attack_chains[src_ip] = []
                    attack_chains[src_ip].append(data)
except FileNotFoundError:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] エラー: ログファイルが見つかりません")
    exit(1)

if not attack_chains:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 新しいログがありません。")
    exit()


# 3. 分析対象の選定

current_time = datetime.datetime.now()

# 過去の分析履歴を読み込む
analyzed_history = {}
if HISTORY_FILE.exists():
    with open(HISTORY_FILE, 'r') as f:
        try:
            analyzed_history = json.load(f)
        except json.JSONDecodeError:
            pass

# 期限切れ（12時間経過）の履歴を掃除する
active_history = {}
for ip, timestamp_str in analyzed_history.items():
    last_analyzed = datetime.datetime.fromisoformat(timestamp_str)
    if current_time - last_analyzed < datetime.timedelta(hours=COOL_OFF_HOURS):
        active_history[ip] = timestamp_str # まだクーリングオフ期間中

# 攻撃回数順にソートし、クーリングオフ中のIPを除外して上位5件を決定
sorted_ips = sorted(attack_chains, key=lambda k: len(attack_chains[k]), reverse=True)
target_ips = [ip for ip in sorted_ips if ip not in active_history][:5]

current_time_str = current_time.strftime('%Y%m%d_%H%M%S')

if not target_ips:
    print(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 新規の脅威IPはありません（すべてクーリングオフ期間中）。")
    exit()

print(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] === トップ {len(target_ips)}件の分析開始 ===")



# 4. トークン圧縮とAI分析・ファイル保存 (リトライ機能付き)

for i, ip in enumerate(target_ips, 1):
    target_logs = attack_chains[ip][:150]
    
    # 生ログ(JSON)保存
    raw_log_filename = JSON_LOG_DIR / f"raw_log_{ip}_{current_time_str}.json"
    with open(raw_log_filename, 'w', encoding='utf-8') as f:
        json.dump(target_logs, f, ensure_ascii=False, indent=2)

    summary_lines = []
    for log in target_logs:
        event = log.get('eventid', '')
        ts = log.get('timestamp', '')
        detail = ""
        if event in ['cowrie.login.failed', 'cowrie.login.success']:
            detail = f"ユーザー名: {log.get('username')}, パス: {log.get('password')}"
        elif event == 'cowrie.command.input':
            detail = f"入力コマンド: {log.get('input')}"
        elif event == 'cowrie.session.connect':
            detail = "SSH接続開始"
        elif event == 'cowrie.session.closed':
            detail = "SSH接続終了"
        summary_lines.append(f"[{ts}] {event} - {detail}")

    log_summary_text = "\n".join(summary_lines)
    prompt = f"""あなたは優秀なSOCアナリストです。以下の攻撃ログを分析しレポートを作成してください。
【攻撃元IP】: {ip}
【行動履歴】:\n{log_summary_text}
【出力形式】
1. 攻撃の概要と目的
2. 推測される手法・使用ツール
3. 脅威レベルとその理由
4. 推奨アクション"""

    # --- リトライ機能の実装 ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            
            # レポート(MD)保存
            md_filename = REPORTS_DIR / f"report_{ip}_{current_time_str}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(f"# SOC自動分析レポート: {ip}\n\n**生成日時:** {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{response.text}")

            # データセット(JSONL)追記と自動ローテーション（40MB制限）
            MAX_FILE_SIZE_MB = 40
            if DATASET_FILE.exists() and DATASET_FILE.stat().st_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
                archive_name = DATASET_FILE.with_name(f"soc_training_dataset_{current_time_str}.jsonl")
                DATASET_FILE.rename(archive_name)
                print(f"データセットを {archive_name.name} に退避しました。")

            dataset_entry = {"messages": [{"role": "user", "content": prompt}, {"role": "model", "content": response.text}]}
            with open(DATASET_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(dataset_entry, ensure_ascii=False) + "\n")
                
            print(f"  [{i}/{len(target_ips)}] IP: {ip} -> 保存完了")
            active_history[ip] = current_time.isoformat()
            break # 成功したらリトライループを抜ける
            
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"  [{i}/{len(target_ips)}] IP: {ip} -> 503混雑エラー。15秒後に再試行します... ({attempt+1}/{max_retries})")
                time.sleep(15)
            else:
                print(f"  [{i}/{len(target_ips)}] IP: {ip} -> 予期せぬエラー: {e}")
                break # 503以外の致命的なエラーは諦める
    else:
        print(f"  [{i}/{len(target_ips)}] IP: {ip} -> 3回再試行しましたが失敗しました。")

    if i < len(target_ips): time.sleep(10)

with open(HISTORY_FILE, 'w') as f:
    json.dump(active_history, f, indent=2)


# 5. Gitリポジトリへの自動Push

print("\nGitへの自動Pushを開始")
try:
    branch_proc = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=PROJECT_ROOT)
    current_branch = branch_proc.stdout.strip() or "main"

    # --- ファイル追加（存在するファイル・フォルダだけをリストアップ） ---
    target_paths = ["VPS/analyze_alerts.py", "Reports",  "soc_training_dataset.jsonl"]
    valid_paths = [p for p in target_paths if (PROJECT_ROOT / p).exists()]
    
    subprocess.run(["git", "add"] + valid_paths, check=True, cwd=PROJECT_ROOT)
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=PROJECT_ROOT)
    
    if status.stdout.strip():
        commit_msg = f"Auto SOC Update: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=PROJECT_ROOT)
        subprocess.run(["git", "push", "-u", "origin", current_branch], check=True, cwd=PROJECT_ROOT)
        print(f"'{current_branch}' ブランチへのPush完了")
    else:
        print("変更なし")
except Exception as e:
    print(f"Git操作エラー: {e}")
