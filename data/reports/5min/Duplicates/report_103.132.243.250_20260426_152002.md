# SOC自動分析レポート: 103.132.243.250

**生成日時:** 2026-04-26 15:23:38

---

## SOCアナリスト レポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `103.132.243.250` から、対象システムへのSSHブルートフォース攻撃が確認されました。攻撃は複数回にわたり、異なるユーザー名とパスワードの組み合わせを試行しています。特に `root` ユーザーに対するブルートフォース攻撃が成功しており、その後、攻撃者はシステムへの永続的なアクセスを確立するために、自身がコントロールするSSH公開鍵をターゲットシステムの `root` ユーザーの `authorized_keys` ファイルに追加しようとしました。

攻撃の主な目的は、SSH認証情報を窃取し、システムへの不正アクセスを確立すること、および、そのアクセスを永続化させるためのバックドア（SSHキーベース認証）を設置することであると推測されます。

### 2. 推測される手法・使用ツール

*   **SSHブルートフォース攻撃 / 辞書攻撃:**
    *   ログには `oracle:oracle09!`, `mani:mani`, `root:135792468`, `root:abcdefgh`, `root:qazwsxedc123`, `ftpuser:test123`, `root:P@ssw0rd6`, `root:Admin88888888`, `root:Gp123456` など、広範なユーザー名とパスワードの組み合わせが短時間で試行されています。これは、自動化されたツールによるSSHブルートフォース攻撃または辞書攻撃の典型的なパターンです。
    *   特に `root` ユーザーに対して多数の試行と成功が見られます。
*   **永続化 (Persistence) 手法:**
    *   ログイン成功後、攻撃者は以下のコマンドを実行しています。
        ```bash
        cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~
        ```
    *   このコマンドは、既存の `.ssh` ディレクトリを削除し、新しいディレクトリを作成した後、攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を `authorized_keys` ファイルに追加し、パーミッションを適切に設定するものです。これにより、攻撃者は今後パスワードを知らなくても、この公開鍵に対応する秘密鍵を用いてSSH接続が可能になります。これは典型的な永続化の手法です。
*   **防御回避の試み:**
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh` というコマンドも試行されています（ハニーポット環境では `command.failed` となっています）。これは、`.ssh` ディレクトリに対する不変属性（`chattr +i`）やその他のロックを解除し、`authorized_keys` ファイルの改変を可能にしようとする試みと推測されます。
*   **使用ツール:** ログから具体的なツール名を特定することはできませんが、SSHブルートフォース攻撃とログイン後の自動コマンド実行を組み合わせたスクリプトや、Hydra, Medusa, Nmap Scripting Engine (NSE) など、SSH関連の攻撃に特化した自動化ツールが使用された可能性が高いです。

### 3. 脅威レベルとその理由

*   **脅威レベル: 高 (High)**
*   **理由:**
    1.  **複数のログイン成功:** 攻撃者は `root` ユーザーを含む複数のアカウントでSSHログインに成功しています。これは、もし本番環境であれば、すでにシステムが侵害された状態であることを示します。
    2.  **永続化の試み:** ログイン成功後、攻撃者は自身がコントロールするSSH公開鍵をシステムに追加することで、恒久的なバックドアを設置しようとしています。これにより、パスワードが変更された後でも、攻撃者はSSHキーベース認証で再アクセスすることが可能となります。
    3.  **自動化された広範な攻撃:** 辞書攻撃的な試行から、攻撃が自動化されたプロセスによって行われていることが伺えます。このような攻撃は、継続的に繰り返される可能性があり、他のシステムへも同様の手口で攻撃を仕掛けている可能性があります。
    4.  **高い影響度:** `root` 権限でのアクセスが確立された場合、攻撃者はシステムの完全な制御を奪い、マルウェアのインストール、データ窃取、システムの破壊、他の内部システムへの横展開など、極めて重大な影響を与える活動を行うことができます。

### 4. 推奨アクション

1.  **即時対応 (インシデントレスポンス):**
    *   **攻撃元IPのブロック:** 攻撃元IPアドレス `103.132.243.250` からのSSH接続を、組織のファイアウォール、IDS/IPS、または各ホストのファイアウォール（iptablesなど）で即座にブロックしてください。
    *   **対象システムの緊急調査と修復 (本番環境の場合):**
        *   **アカウントパスワードのリセット:** ログでログインに成功した `root` ユーザーを含む、全てのSSHアクセス可能なアカウントのパスワードを直ちに、かつ強力なものに変更してください。
        *   **SSH `authorized_keys` の確認と削除:** `root` ユーザーのホームディレクトリ（`/root/.ssh/`）および他のシステムユーザーのホームディレクトリ内にある `.ssh/authorized_keys` ファイルを確認し、身に覚えのないSSH公開鍵（特にログに記載された `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、存在する場合は削除してください。
        *   **システムログのフォレンジック調査:** `/var/log/auth.log` や `/var/log/secure` などの認証ログ、その他システムログを詳細に確認し、攻撃者がログイン後にどのような追加行動（ファイル改変、マルウェアダウンロード、データ窃取、他システムへの接続試行など）を行ったかを調査してください。
        *   **システム整合性の確認:** Rootkit検出ツールやファイル整合性監視ツール（Tripwire, AIDEなど）を用いて、システムの改ざんがないか確認してください。アンチウイルス/マルウェアスキャンも実施してください。
        *   **ネットワーク監視の強化:** 対象システムからの不審な通信（外部への接続、異常なデータ転送など）がないか、ネットワークトラフィックを監視してください。
    *   **脅威インテリジェンスの活用 (ハニーポットの場合):**
        *   ログに記録された攻撃元IPアドレス、試行されたユーザー名とパスワード、および攻撃者が追加しようとしたSSH公開鍵の情報を、組織内の脅威インテリジェンスデータベースに登録し、SIEMやIDS/IPSルールに組み込むことで、将来の攻撃検知能力を向上させてください。

2.  **予防策 (セキュリティ強化):**
    *   **多要素認証 (MFA) の導入:** SSH接続に多要素認証を必須とすることで、パスワードが窃取された場合でも不正ログインを防ぐことができます。
    *   **強力なパスワードポリシーの適用:** 最小文字数、複雑性要件（大文字、小文字、数字、記号の組み合わせ）、定期的な変更などを義務付ける強力なパスワードポリシーをシステム全体で適用してください。
    *   **`root` ユーザーの直接ログイン禁止:** `/etc/ssh/sshd_config` ファイルで `PermitRootLogin no` を設定し、`root` ユーザーによる直接SSHログインを禁止してください。特権操作が必要な場合は、一般ユーザーでログイン後、`sudo` コマンドを使用させるようにしてください。
    *   **不要なアカウントの削除/無効化:** `oracle`, `mani`, `ftpuser` など、現在使用されていないシステムアカウントは削除するか、SSHログインを無効化してください。
    *   **ログイン試行回数制限の導入:** `Fail2ban` などのツールを導入し、SSHへのログイン試行失敗が一定回数を超えたIPアドレスを一時的または永続的にブロックする設定を行ってください。
    *   **SSHキーベース認証の厳格な運用:** パスワード認証を完全に無効化し、SSHキーベース認証のみを許可することを検討してください。その際、秘密鍵の厳重な管理と、`authorized_keys` ファイルのパーミッション設定（`chmod 600 ~/.ssh/authorized_keys`）が適切であることを確認してください。
    *   **定期的なセキュリティ監査:** システムの脆弱性スキャン、設定レビュー、ログ分析を定期的に実施し、潜在的なセキュリティリスクを早期に発見・対処する体制を強化してください。