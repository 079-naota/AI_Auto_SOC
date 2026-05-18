# SOC自動分析レポート: 103.172.205.139

**生成日時:** 2026-04-26 02:27:29

---

## SOCアナリストレポート

**日時:** 2026-04-26 01:45:00 UTC (レポート作成時点)
**分析対象ログ期間:** 2026-04-26T01:13:56Z - 2026-04-26T01:44:00Z
**攻撃元IPアドレス:** 103.172.205.139
**対象サービス:** SSH (ポート22)
**ログソース:** Cowrie (SSHハニーポット)

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス 103.172.205.139 から、SSHサービスに対する継続的なブルートフォース/辞書攻撃が確認されました。この攻撃者は、複数のユーザー名と推測されやすいパスワードの組み合わせを繰り返し試行し、最終的に `root` ユーザーでのログインに複数回成功しています。

ログイン成功後、攻撃者は自身のSSH公開鍵をターゲットシステムの `root` ユーザーの `~/.ssh/authorized_keys` ファイルに追加することで、永続的なアクセス経路を確立しようとしています。これは、今後のパスワードなしでの再侵入を可能にし、システムへのバックドアを設置する明確な意図を示しています。

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **SSH ブルートフォース/辞書攻撃:** ログには `user7`, `deployer`, `frappe`, `ubuntu`, `user`, `mary`, `admin`, `zhaoxj`, `345gs5662d34`, そして特権ユーザーである `root` など、複数のユーザー名に対するログイン試行が記録されています。パスワードも `1234`, `password123`, `default` といった推測されやすいものや、`abcd1234.`, `3245gs5662d34`, `Password.123`, `MoeClub.org`, `a12348765`, `abc@123456` といったやや複雑なものが含まれており、広範なパスワードリストを用いた辞書攻撃が行われた可能性が高いです。
    *   **永続化メカニズムの確立:** `root` ユーザーでのログイン成功後、攻撃者は以下のコマンドを実行しようとしました。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: 既存の `.ssh` ディレクトリに設定されている可能性のある不変属性（immutable attribute）を解除し、変更を可能にしようとしています（ハニーポットのログでは `command.failed` となっていますが、これはハニーポットがこのコマンドをエミュレートできなかったためであり、攻撃者の意図としては既存の保護を無効化しようとしたものと推測されます）。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOKrvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`:
            1.  既存の `.ssh` ディレクトリを削除。
            2.  新しい `.ssh` ディレクトリを作成。
            3.  攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOKrvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を `~/.ssh/authorized_keys` に追加。
            4.  `.ssh` ディレクトリのパーミッションを適切に設定し、他のユーザーからの読み書き実行を制限。
            この一連のコマンドは、SSH鍵認証による再侵入経路を確保するための典型的な手口です。
*   **使用ツール:**
    *   SSHクライアント: 基本的なSSH接続のため。
    *   ブルートフォース/辞書攻撃ツール: 複数の認証情報を自動的かつ高速に試行するために、`hydra`、`medusa`、またはカスタムスクリプトなどのツールが使用された可能性があります。
    *   SSH鍵生成ツール: 攻撃者の公開鍵は、`ssh-keygen`などの標準的なツールで生成されたものと推測されます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **特権アカウントへのログイン成功:** 攻撃者は `root` ユーザーとしてログインに複数回成功しています。これは、もしこれが実システムであれば、攻撃者がシステムに対する完全な制御権を取得したことを意味します。
2.  **永続化の試み:** ログイン成功後、攻撃者は自身のSSH公開鍵を `authorized_keys` に追加しようと試みています。これにより、パスワードが変更された後でも、攻撃者がSSH鍵認証を使用してシステムに再接続できる永続的なバックドアが設置されることになります。
3.  **明確な悪意ある意図:** 単なる脆弱性スキャンやランダムなログイン試行に留まらず、ログイン後に具体的な悪意あるコマンド（永続化のための鍵埋め込み）を実行しようとしていることから、システムへの深刻な侵害意図が明確です。
4.  **広範囲なパスワード試行:** 一般的なユーザー名と弱いパスワードだけでなく、`root`ユーザーに対しても多様なパスワードを試行しており、組織内で使用されている可能性のあるパスワードパターンを特定しようとしている可能性があります。

### 4. 推奨アクション

**A. 緊急対応 (Immediate Actions):**

1.  **攻撃元IPのブロック:** 攻撃元IPアドレス `103.172.205.139` からのすべてのネットワーク通信（特にSSHポート22への接続）をファイアウォールまたはIPSで即座にブロックしてください。
2.  **認証情報のリセット:** ログでログイン成功が確認されたすべてのユーザーアカウント（特に`root`）について、直ちにパスワードを非常に複雑で推測されにくいものに変更してください。また、他の推測されやすいパスワード (`1234`, `password123`, `default`など) も実環境で使用されていないか確認し、使用されている場合は即座に変更してください。
3.  **不正なSSH鍵の確認と削除:** すべてのユーザー（特に`root`）のホームディレクトリ内の `.ssh/authorized_keys` ファイルを緊急で確認し、ログに記載された攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOKrvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が存在しないことを確認してください。もし存在する場合は、直ちにそのエントリを削除してください。
4.  **SSH設定の強化:**
    *   `root`ユーザーでの直接SSHログインを無効化 (`PermitRootLogin no`) し、一般ユーザーでログイン後に`sudo`を使用する運用に切り替えてください。
    *   パスワード認証を無効化し、鍵認証のみを許可する (`PasswordAuthentication no`, `ChallengeResponseAuthentication no`) 設定に切り替えてください。

**B. フォレンジック調査 (Forensic Investigation):**

1.  **詳細なログ分析:**
    *   認証ログ (`/var/log/auth.log` など) を詳細に確認し、攻撃が実際に成功したか、他の不正ログインや操作がないか確認してください。
    *   シェル履歴 (`~/.bash_history` など) やシステムログを確認し、攻撃者がログイン後に他のコマンドを実行していないか調査してください。
2.  **マルウェアスキャン:** サーバー全体を包括的なマルウェアスキャンツールでスキャンし、不正なファイルやマルウェアが設置されていないか確認してください。
3.  **システム変更の検出:** 不正なユーザーアカウントの追加、バックドアプログラムのインストール、設定ファイルの改竄など、システムに異常な変更がないか確認してください。
4.  **ネットワークトラフィックの分析:** 攻撃期間中のネットワークトラフィックログ（もしあれば）を分析し、外部への不審な通信（データ流出、C2通信など）がないか確認してください。

**C. 予防的措置 (Preventive Measures):**

1.  **SSH総当たり攻撃対策の導入/強化:**
    *   Fail2BanやOSSECなどの侵入検知/防御システムを導入し、SSHへの総当たり攻撃を自動的に検知・ブロックするよう設定してください。
    *   SSH接続へのレートリミットを設定し、短時間での試行回数を制限してください。
2.  **多要素認証 (MFA) の導入:** 可能であれば、SSHログインにMFAを導入し、セキュリティを強化してください。
3.  **SSHポートの変更:** 標準のSSHポート (22) 以外のポートを使用することで、一般的なポートスキャンからの攻撃対象となる頻度を減らすことができます（これはセキュリティの向上策の一つであり、絶対的な対策ではありません）。
4.  **定期的な監査と脆弱性診断:** 定期的にサーバーのセキュリティ監査、脆弱性診断を実施し、潜在的なリスクを早期に発見・対処してください。
5.  **セキュリティ意識向上トレーニング:** 従業員に対し、安全なパスワードの使用、不審な活動の報告など、セキュリティ意識向上のためのトレーニングを実施してください。

---

このレポートは、提供されたログに基づいています。実際のシステムにおける影響範囲は、詳細なフォレンジック調査によってのみ正確に判断できます。上記の推奨アクションを速やかに実行し、セキュリティ侵害の拡大を防ぐことが最優先事項です。