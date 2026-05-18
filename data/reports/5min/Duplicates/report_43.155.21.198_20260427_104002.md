# SOC自動分析レポート: 43.155.21.198

**生成日時:** 2026-04-27 10:40:56

---

優秀なSOCアナリストとして、提供された攻撃ログを詳細に分析し、以下のレポートを作成しました。

---

### セキュリティインシデント分析レポート

**報告日時**: 2026-04-27T04:00:00Z (推定)
**攻撃元IPアドレス**: 43.155.21.198
**ターゲット**: SSHサービス (Cowrieハニーポット)

#### 1. 攻撃の概要と目的

攻撃元IPアドレス `43.155.21.198` から、短時間で複数回にわたるSSHログイン試行が行われました。これは、主に `root` ユーザーを標的としたブルートフォース攻撃または辞書攻撃であると判断されます。

攻撃者の主要な目的は、システムの初期アクセスを確立し、その後、自身のSSH公開鍵をターゲットサーバーの `~/.ssh/authorized_keys` ファイルに書き込むことで、永続的なアクセス経路（バックドア）を確立することです。これにより、将来的にパスワードなしでシステムにアクセスできるようになり、さらなる攻撃活動（例: マルウェアの展開、データ窃取、ボットネットへの組み込み、他のシステムへの横展開など）の足がかりを築くことを意図していると考えられます。

ログはCowrieハニーポットのものであるため、実際のシステムへの侵害は発生していませんが、このログは攻撃者が実際に成功した場合に何を行うかを示す明確な証拠となります。

#### 2. 推測される手法・使用ツール

*   **初期アクセス (Initial Access)**:
    *   **ブルートフォース/辞書攻撃**: ログには `rootwww`, `1234qwer`, `345gs5662d34`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`, `3245gs5662d34` など、様々なユーザー名とパスワードの組み合わせが試行されています。これは、自動化されたツールによる一般的なクレデンシャルスタッフィングまたはブルートフォース攻撃の典型的な挙動です。特に `root` ユーザーへの集中攻撃が見られます。
*   **永続化 (Persistence)**:
    *   ログイン成功後（ハニーポット上での成功）、攻撃者は以下のコマンド群を実行しようとしています。
        1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `chattr -ia .ssh` は、`.ssh` ディレクトリに設定されている不変属性（immutable attribute: `i`）や追記専用属性（append-only attribute: `a`）を解除しようとするものです。これにより、ファイルの変更や削除を可能にしようとしています。`lockr` は一般的なLinuxコマンドではなく、ここでは失敗していますが、何らかの特定の防御メカニズムの無効化を試みた可能性があります。
        2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: このコマンドは、既存の `.ssh` ディレクトリを削除して新しく作成し、自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を `authorized_keys` ファイルに書き込み、さらに適切なパーミッション (`chmod -R go= ~/.ssh`) を設定して、SSH鍵認証によるアクセスを可能にしようとするものです。この公開鍵は、コメント部分に「mdrfckr」と記載されており、攻撃者グループの識別子である可能性があります。
*   **使用ツール**: 複数のログイン試行と定型的なコマンド実行のパターンから、Hydra、Medusa、Nmapの`ssh-brute`スクリプトなどの自動化されたブルートフォースツール、およびログイン後のアクションを自動実行するカスタムシェルスクリプトが使用されている可能性が高いです。

#### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

*   **最高権限アカウントの標的化**: 攻撃者が `root` ユーザーを執拗に狙っており、もし成功すればシステムへの完全な制御を奪われるリスクがあります。
*   **永続化の試み**: 単なる一時的なアクセスではなく、SSH鍵による永続的なバックドアの設置を目的としているため、非常に悪質な意図が感じられます。これにより、一度侵害に成功すれば、パスワードが変更されても攻撃者はシステムにアクセスし続けることが可能になります。
*   **自動化された攻撃**: 攻撃が自動化されていることから、特定の組織を狙ったものではなく、インターネット上に公開されている脆弱なSSHサーバーを大規模にスキャンし、侵害しようとする広範なキャンペーンの一部である可能性が高いです。
*   **複数のパスワードの試行成功**: ハニーポット上で複数の異なるパスワード (`6yhnji90-`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`, `3245gs5662d34`) でログインに成功している記録があり、もし実際のシステムであれば、これらのパスワードが使用されている場合に侵害されていたことを意味します。

#### 4. 推奨アクション

1.  **攻撃元IPアドレスの即時ブロック**:
    *   ファイアウォール、IDS/IPS、およびクラウドセキュリティグループ（AWS Security Groups, Azure Network Security Groupsなど）にて、攻撃元IPアドレス `43.155.21.198` からのSSH (TCPポート22) への全てのアクセスを直ちにブロックしてください。
2.  **SSH認証の強化**:
    *   **公開鍵認証への移行**: 可能な限りSSHパスワード認証を無効化し、より安全な公開鍵認証のみを許可するようにSSHサーバーを設定してください。
    *   **rootログインの無効化**: `/etc/ssh/sshd_config` で `PermitRootLogin no` を設定し、SSH経由での `root` ユーザーの直接ログインを禁止してください。特権が必要な場合は、一般ユーザーでログイン後に `sudo` を使用する運用を徹底してください。
    *   **多要素認証 (MFA) の導入**: ユーザー認証層にMFAを導入することで、認証情報が漏洩した場合でも不正ログインを阻止できます。
    *   **authorized_keysの厳格な管理**:
        *   `~/.ssh` ディレクトリのパーミッションが `700`、`~/.ssh/authorized_keys` ファイルのパーミッションが `600` であることを確認し、他のユーザーが読み書きできないようにしてください。
        *   全ての `authorized_keys` ファイルを定期的に監査し、認識できない公開鍵（特に今回の攻撃で使用された `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が含まれていないか確認してください。
3.  **パスワードポリシーの強化とリセット**:
    *   ログに記録されている攻撃者が試行し「成功」したパスワード（`6yhnji90-`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`, `3245gs5662d34`）が、実際のシステムで現在使用されていないことを確認してください。もし使用されている場合は、直ちに該当ユーザーのパスワードをより複雑で推測しにくいものにリセットしてください。
    *   強力なパスワードポリシー（文字数、文字種混合、定期的な変更など）を強制してください。
4.  **既存システムに対する侵害の痕跡調査**:
    *   全ての公開SSHサーバーにおいて、今回の攻撃パターンと同様のログイン試行失敗ログ、および不審なログイン成功ログがないか、過去のログを遡って徹底的に調査してください。
    *   `~/.ssh/authorized_keys` やその他のシステムファイルに、攻撃者の公開鍵（上記）やその他の不審な変更がないか、全てのユーザーアカウントに対して監査を行ってください。
5.  **IDS/IPSおよびSIEMルールの強化**:
    *   短時間での複数回ログイン失敗を検知し、自動的に送信元IPをブロックするIDS/IPSルール（例: Fail2Banなど）を設定してください。
    *   SSHログインの異常な挙動（例: 未知のIPからのログイン、rootユーザーへの不審なログイン試行、認証後の不審なコマンド実行）を検知するSIEMルールを構築・強化してください。
6.  **脅威インテリジェンスの共有**:
    *   攻撃元IPアドレス `43.155.21.198` と攻撃者が使用したSSH公開鍵の情報を、関連する脅威インテリジェンスプラットフォームやセキュリティコミュニティと共有し、他の組織の防御に役立ててください。

---