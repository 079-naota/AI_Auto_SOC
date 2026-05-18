# SOC自動分析レポート: 14.103.63.16

**生成日時:** 2026-05-01 15:00:02

---

## SOCアナリストレポート

**報告日時**: 2026-05-01T02:10:00Z
**対象事象**: SSHブルートフォース攻撃と不正アクセス試行
**攻撃元IPアドレス**: 14.103.63.16

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `14.103.63.16` から、SSHサービスに対して継続的なブルートフォース攻撃が確認されました。この攻撃者は、複数のユーザー名とパスワードの組み合わせを試行し、最終的に2回にわたり `root` ユーザーとしてログインに成功しています。

ログイン成功後、攻撃者は以下の活動を試みており、その目的はシステムの乗っ取りと永続的なアクセス経路の確立、およびシステム情報の収集にあると推測されます。

*   自身のSSH公開鍵を `authorized_keys` に追加することによるバックドアの設置。
*   `root` ユーザーのパスワード変更。
*   システム情報（CPU、メモリ、OS、ディスク使用量、cronジョブなど）の広範な偵察。
*   既存のセキュリティメカニズムやマルウェア防御策の無効化（`/etc/hosts.deny` のクリア、特定のプロセスの停止など）。

### 2. 推測される手法・使用ツール

**【攻撃手法】**

1.  **ブルートフォース攻撃**: `ubuntu`, `test`, `oracle`, `admin`, `ftpadmin`, `user-backup` といった一般的なユーザー名や、`root` ユーザーに対して、複数の辞書的なパスワード（例: `5555555`, `zxcv123`, `oracle@2016`, `Password!@#$`, `Abc12345`, `1234`, `123`, `admin17`, `admin$11`）を繰り返し試行し、認証情報を特定しています。
2.  **永続化 (Persistence)**:
    *   ログインに成功後、`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~` コマンドにより、攻撃者のSSH公開鍵（コメント `mdrfckr`）を `~/.ssh/authorized_keys` に追加し、パスワードなしでの再アクセス経路を確立しようとしています。
    *   `echo "root:UMeEWoiKxlZm"|chpasswd|bash` コマンドにより、`root` ユーザーのパスワードを変更しようとしています。
3.  **偵察 (Discovery)**: 以下のコマンド群により、システムの構成や状態に関する情報を広範に収集しています。
    *   `cat /proc/cpuinfo | grep name | wc -l`, `cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'`, `lscpu | grep Model`: CPU情報
    *   `free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'`: メモリ情報
    *   `which ls`, `ls -lh $(which ls)`: `ls`コマンドのパスと権限
    *   `crontab -l`: cronジョブのリスト
    *   `w`: ログインユーザーとシステム負荷
    *   `uname -m`, `uname`, `uname -a`: OSおよびカーネル情報
    *   `whoami`: 現在のユーザー名
    *   `df -h | head -n 2 | awk 'FNR == 2 {print $2;}'`: ディスク使用量
4.  **防御回避 (Defense Evasion)**: `rm -rf /tmp/secure.sh; rm -rf /tmp/auth.sh; pkill -9 secure.sh; pkill -9 auth.sh; echo > /etc/hosts.deny; pkill -9 sleep;` コマンドにより、一時ファイルの削除、特定のプロセスの停止、`/etc/hosts.deny` のクリアを試み、既存のセキュリティ対策や他のマルウェアの活動を妨害しようとしています。
5.  **特権操作**: `chattr -ia .ssh; lockr -ia .ssh` を試行していますが、これはハニーポット環境では失敗しています。おそらく `authorized_keys` ファイルの保護属性を操作しようとしたものと推測されます。

**【使用ツール】**

*   標準的なSSHクライアント
*   自動化されたブルートフォーススクリプトやボットネットクライアント (複数のログイン試行と定型コマンド実行から推測)
*   Linux/Unix標準コマンド群 (`cd`, `rm`, `mkdir`, `echo`, `chmod`, `cat`, `grep`, `wc`, `head`, `awk`, `free`, `which`, `ls`, `crontab`, `w`, `uname`, `whoami`, `lscpu`, `df`, `chpasswd`, `pkill`, `chattr`, `lockr`)

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

*   **認証情報の侵害**: 攻撃者は `root` ユーザーの認証情報（`root:admin17` および `root:admin$11`）を複数回特定し、ターゲットシステム（ハニーポット）へのログインに成功しています。これは現実のシステムであれば、最も重要な特権アカウントの侵害であり、システムの完全な制御を許すことになります。
*   **永続化とシステム乗っ取りの試み**: SSH公開鍵の設置と `root` パスワードの変更試行は、システムへの永続的なアクセスと完全な支配を確立しようとする明確な意図を示しています。
*   **広範な偵察活動**: ログイン後の多岐にわたるシステム情報収集は、攻撃者がシステムの環境を理解し、次の攻撃フェーズ（マルウェアの展開、データ窃取、横展開など）のための足がかりを探していることを強く示唆します。
*   **防御回避の試み**: `/etc/hosts.deny` のクリアやプロセスの停止は、セキュリティ対策を無効化し、攻撃の痕跡を隠蔽しようとする悪意ある行動です。
*   **自動化された攻撃**: 攻撃が長期間にわたり、多様なユーザー名とパスワードを試行し、ログイン後も複数の定型コマンドを続けて実行していることから、これは手動によるものではなく、自動化されたスクリプトやボットネットの一部である可能性が高いです。これにより、今後も同様の攻撃が継続または他のシステムにも展開されるリスクがあります。

### 4. 推奨アクション

このログはハニーポットからのものですが、現実のシステムであれば重大なセキュリティインシデントに該当します。以下の推奨アクションは、当社の実環境における同様の攻撃に対する予防策および対応策として実施を推奨します。

1.  **攻撃元IPアドレスの即時ブロック**:
    *   ファイアウォール、IDS/IPS、または他のネットワークセキュリティデバイスにて、攻撃元IPアドレス `14.103.63.16` からの通信をブロックします。
2.  **SSHサーバーのセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能な限り、公開鍵認証のみを許可する設定に変更します。
    *   **強固なパスワードポリシーの徹底**: すべてのユーザーアカウントに対し、複雑性、長さ、有効期限を含む強固なパスワードポリシーを強制します。ブルートフォースで成功した `admin17` や `admin$11` のような単純なパスワードは厳禁です。
    *   **rootログインの禁止**: SSH経由での `root` 直接ログインを禁止し、一般ユーザーでログイン後、`sudo` を利用する運用を徹底します。
    *   **アカウントロックアウト機能の導入**: 複数回のログイン失敗 (例: 3〜5回) で、該当IPアドレスまたはアカウントを一時的または永続的にロックアウトする仕組み (例: `fail2ban`) を導入します。
    *   **SSHポートの変更**: 22番ポート以外のカスタムポートを使用することも検討します (ただし、これは根本的な解決策ではなく、スキャン回避策の一つです)。
3.  **アカウントおよび認証情報の監査**:
    *   全システムで、攻撃者が試行したユーザー名 (例: `ubuntu`, `test`, `oracle`, `admin`, `ftpadmin`, `user-backup`, `root`) が存在するか確認し、もし存在する場合はパスワードが強固であること、および不要なアカウントは削除されていることを確認します。
    *   ログに示された成功パスワード (`admin17`, `admin$11`) と一致するアカウントが存在しないか緊急で確認し、存在する場合は即座にパスワードを変更します。
4.  **SSH公開鍵認証の緊急確認**:
    *   全てのLinux/Unixサーバーにおいて、全ユーザーの `~/.ssh/authorized_keys` ファイルを監査し、不審なSSH公開鍵（特に `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が追加されていないか確認します。発見された場合は、直ちに該当鍵を削除し、システム侵害の有無を詳細に調査します。
5.  **ログ監視とアラートの強化**:
    *   SSH認証ログ (`/var/log/auth.log` など) の監視を強化し、異常なログイン試行、ログイン成功、不審なコマンド実行に対するリアルタイムアラートを設定します。
    *   SIEM (Security Information and Event Management) システムへのログ連携を確実にし、分析と可視化を強化します。
6.  **脆弱性管理**:
    *   定期的にシステム脆弱性スキャンを実施し、既知の脆弱性や設定不備がないか確認・修正します。
7.  **インシデントレスポンス計画の見直し**:
    *   このような侵害が発生した場合のインシデントレスポンス計画が、最新の脅威に対応できるよう適切に機能するかを確認し、必要に応じて更新します。特に、侵害後のシステム復旧手順とフォレンジック調査の実施体制を確認します。

---
以上