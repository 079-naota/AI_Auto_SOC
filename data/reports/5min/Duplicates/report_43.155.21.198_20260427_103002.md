# SOC自動分析レポート: 43.155.21.198

**生成日時:** 2026-04-27 10:34:13

---

8. The user successfully authenticated with the credentials. This means the attacker has gained access to the system through legitimate means (as seen by the Cowrie honeypot).

**Phase 3: Backdoor Establishment and Persistence**
*   [2026-04-27T03:33:27.731364Z] cowrie.command.input - 入力コマンド: cd ~; chattr -ia .ssh; lockr -ia .ssh
    *   The attacker attempts to change attributes of the `.ssh` directory. `chattr -ia` aims to remove immutable and append-only attributes, which would prevent deletion or modification of files. `lockr` is not a standard Linux command and likely failed. This action suggests an attempt to overcome potential file protections before modifying SSH configurations.
*   [2026-04-27T03:33:28.004251Z] cowrie.command.input - 入力コマンド: cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~
    *   This is the critical persistence command:
        1.  `rm -rf .ssh`: Deletes any existing `.ssh` directory and its contents.
        2.  `mkdir .ssh`: Creates a new, empty `.ssh` directory.
        3.  `echo "..." >>.ssh/authorized_keys`: Appends the attacker's public SSH key (commented as "mdrfckr") to the `authorized_keys` file. This establishes a backdoor, allowing the attacker to log in without a password using their private key.
        4.  `chmod -R go= ~/.ssh`: Sets restrictive permissions on the `.ssh` directory, removing group and others' read/write/execute permissions. This is a common practice to make SSH keys work correctly and also serves to hide the backdoor by making the directory less conspicuous.

**Phase 4: Repeated Login Attempts and Backdoor Re-establishment**
*   The attacker continues to make SSH connections using various credentials, some failing (`345gs5662d34`) and many succeeding for the `root` user with different passwords (`3245gs5662d34`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`).
*   In each successful `root` login session, the attacker consistently attempts to re-execute the same set of commands as in Phase 3:
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "..." >>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
    *   The consistent re-application of the same SSH key-based backdoor suggests robust automation and an intent to ensure their persistence even if other access methods (e.g., specific passwords) change or fail, or if the `authorized_keys` file is modified by other means.

### 1. 攻撃の概要と目的

*   **攻撃元IPアドレス**: 43.155.21.198
*   **攻撃の種類**: SSHブルートフォース攻撃と、それに続く永続的なアクセス経路（バックドア）の設置
*   **タイムライン**: 2026年4月27日03時31分15秒から約8分間にわたり、断続的に攻撃が実施されました。
*   **概要**:
    攻撃者は、複数のユーザー名（例: `rootwww`, `345gs5662d34`）や、さまざまなパスワード（例: `1234qwer`, `6yhnji90-`, `3245gs5662d34`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`）を繰り返し試行し、SSHサービスへのブルートフォース攻撃を実行しました。ハニーポットの挙動により、攻撃者は複数のパスワードで`root`ユーザーとしてログインに成功しています。

    ログイン成功後、攻撃者は自身の公開鍵をターゲットシステムの`~/.ssh/authorized_keys`ファイルに追加することで、パスワードなしでのSSHアクセスを可能にする永続的なバックドアを確立しようとしました。このプロセスには、既存の`.ssh`ディレクトリの削除、新規作成、公開鍵の追加、および適切なファイルパーミッションの設定が含まれています。これらのコマンドは、ログインが成功するたびに繰り返し実行されており、攻撃の自動化と持続性の確保への強い意図が示唆されます。

*   **攻撃の目的**:
    ターゲットシステムへのSSH不正アクセス権を獲得し、さらに自身のSSH公開鍵を登録することで、永続的かつパスワード認証に依存しないアクセス経路を確立することを目指しています。これにより、将来にわたるシステムへの無許可アクセスを維持し、さらなる悪意のある活動（データ窃取、マルウェア展開、他のシステムへの攻撃拠点化など）のための足がかりを築くことを目的としていると考えられます。

### 2. 推測される手法・使用ツール

*   **認証突破手法**:
    *   **SSHブルートフォース攻撃**: 辞書攻撃や総当たり攻撃の手法を用いて、多様なユーザー名とパスワードの組み合わせを自動的に試行し、SSH認証を突破しようとしています。特に、特権ユーザーである`root`アカウントが主な標的となっています。
*   **永続化手法**:
    *   **SSH公開鍵認証バックドア**: ログインに成功した後、`~/.ssh/authorized_keys`に攻撃者の公開鍵を追加する一般的な手法を使用しています。これにより、攻撃者は自身の秘密鍵を用いて、パスワード認証を経ずにシステムにアクセスできるようになります。これは、非常に効果的で検出が難しい永続化メカニズムです。
*   **使用ツール（推測）**:
    *   **自動化されたSSHブルートフォースツール**: 短時間で多数のログイン試行が行われていることから、`Hydra`、`Medusa`、`Nmap`の`ssh-brute`スクリプトなどの自動化されたブルートフォースツールが使用されている可能性が高いです。
    *   **シェルスクリプトまたはマルウェア**: ログイン成功後のコマンド実行が非常に高速かつ一貫していることから、事前に用意されたシェルスクリプト、またはSSHアクセスを試みて永続化を図るマルウェア（例: Miraiボットネットの一部、XMRigマイナーなどが感染時に実施する活動）によって行われていると推測されます。特に、`chattr`コマンドの使用試行や、一連の`.ssh`ディレクトリ操作は、このような自動化された攻撃の典型的な挙動です。

### 3. 脅威レベルとその理由

*   **脅威レベル**: **高 (High)**

*   **理由**:
    1.  **root権限の奪取を目指している**: 攻撃は最も特権の高い`root`ユーザーアカウントを狙っており、成功した場合、システムへの完全な制御権が攻撃者に渡ります。これは、システムの完全な侵害に直結する非常に重大な事態です。
    2.  **永続的なアクセス経路の確立**: 攻撃者が自身の公開鍵を`authorized_keys`ファイルに登録しようとする行為は、システムが再起動されたり、パスワードが変更されたりしても、攻撃者が常にSSH経由でアクセスできる永続的なバックドアを設置する試みです。これにより、攻撃者は長期的にシステムを支配することが可能になります。
    3.  **自動化された攻撃**: ブルートフォース試行からバックドア設置までの一連の活動が短時間で繰り返されており、攻撃が自動化されていることが強く示唆されます。これは、特定の標的を狙った攻撃というよりは、インターネット上で脆弱なサーバーを無差別にスキャンし、感染を広げようとする広範な攻撃活動の一環である可能性が高いです。このような攻撃は、一旦成功すると瞬く間に被害が拡大する恐れがあります。
    4.  **潜在的な影響の深刻さ**: もしこれが実稼働環境であれば、攻撃者は機密情報の窃取、システム構成の改ざん、データの破壊、ウェブサイトの改ざん、ランサムウェアの展開、他のシステムへの攻撃基盤としての悪用など、壊滅的な被害をもたらす可能性があります。

### 4. 推奨アクション

1.  **攻撃元IPアドレスの緊急ブロック**:
    *   直ちにファイアウォール、IDS/IPS、またはWAFなどのセキュリティ機器で、攻撃元IPアドレス `43.155.21.198` からの全てのインバウンド接続をブロックしてください。
2.  **SSHサービスセキュリティの強化**:
    *   **パスワード認証の無効化**: 可能な限り、SSHサービスでのパスワード認証を無効にし、公開鍵認証のみを許可するように設定を変更してください。
    *   **`root`ログインの禁止**: `/etc/ssh/sshd_config`ファイルで`PermitRootLogin no`を設定し、rootユーザーによる直接のSSHログインを禁止してください。必要に応じて、一般ユーザーでログイン後、`sudo`や`su`コマンドを使用して特権昇格を行う運用を徹底してください。
    *   **SSHポートの変更**: デフォルトのSSHポート (22番) を使用している場合、よく知られていない別のポートに変更することで、一般的なブルートフォース攻撃の対象になるリスクを軽減できます。
    *   **認証試行回数の制限と自動ブロック**: `Fail2Ban`などのツールを導入し、一定回数以上のSSH認証失敗があったIPアドレスを一時的または永続的に自動でブロックする仕組みを構築してください。
    *   **二要素認証 (MFA) の導入**: SSHログインに二要素認証を導入し、認証プロセスを多層化することでセキュリティを大幅に強化してください。
3.  **既存システムに対する緊急監査**:
    *   **`~/.ssh/authorized_keys`ファイルの確認**: ネットワーク内の全てのLinux/Unix系サーバーにおいて、全ユーザーのホームディレクトリ下の`~/.ssh/authorized_keys`ファイルの内容を緊急で確認してください。今回検出された公開鍵（`ssh-rsa AAAAB3NzaC1yc2E... mdrfckr`）と一致するものが登録されていないか、厳重にチェックし、もし発見された場合は即座に削除してください。
    *   **不審なユーザーアカウントの確認**: システム