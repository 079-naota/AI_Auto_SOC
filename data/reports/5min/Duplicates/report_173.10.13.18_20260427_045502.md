# SOC自動分析レポート: 173.10.13.18

**生成日時:** 2026-04-27 04:56:18

---

## SOCアナリストレポート

### 1. 攻撃の概要と目的

このレポートは、攻撃元IPアドレス `173.10.13.18` から観測されたSSHサービスに対する一連の攻撃を分析したものです。ハニーポット (Cowrie) のログに基づくと、攻撃者は複数のパスワードを試行してシステムへの認証突破を試み、成功したと記録された後、永続的なアクセス経路を確立しようとしています。

*   **攻撃元IPアドレス:** 173.10.13.18
*   **攻撃日時:** 2026-04-27T03:16:46Z から 2026-04-27T03:31:36Z にかけて
*   **攻撃対象サービス:** SSH (Secure Shell)
*   **攻撃手法の概要:**
    1.  複数のユーザー名（`dev`, `trans`, `root`）とパスワードの組み合わせを試行するブルートフォース/辞書攻撃。
    2.  ハニーポット上での `root` ユーザーとしての認証成功（複数回）。
    3.  認証成功後、`root` ユーザーのホームディレクトリ (`~`) にある `.ssh` ディレクトリを操作し、攻撃者の公開鍵を `authorized_keys` ファイルに追加することで、パスワードなしでの再アクセスを可能にするバックドアを設置しようとする。
*   **攻撃の目的:**
    *   システムへの不正アクセスと権限昇格（`root` 権限の奪取）。
    *   SSH公開鍵認証を利用した永続的なアクセス経路の確立（バックドアの設置）。
    *   これにより、将来的にシステムを自由に操作・悪用するための足がかりを築くこと。

### 2. 推測される手法・使用ツール

*   **認証突破:**
    *   **手法:** SSHのブルートフォース攻撃または辞書攻撃。攻撃者は「dev」「trans」「root」といった一般的なユーザー名と、「!dev」「trans」「123456Aa」「Aa000000」「Sp0rt」「123456789a@」「qaz123!@#」「Aa12488261」などの推測されやすい、あるいは一般的なパスワードリストを用いて試行を繰り返しています。
    *   **ツールの推測:** 複数のログイン試行が短時間で繰り返され、その後の一連のコマンド実行も自動化されていることから、`Hydra`や`Medusa`のようなブルートフォースツール、またはカスタムスクリプトが使用されている可能性が高いです。
*   **永続的アクセス確立（バックドア設置）:**
    *   **手法:** ログイン成功後、以下のコマンドを実行し、自身のSSH公開鍵をターゲットシステムの`root`ユーザーの`authorized_keys`ファイルに追加しようとしています。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
    *   **補足:** `chattr -ia .ssh` は、`.ssh`ディレクトリのimmutable属性（不変属性）を解除しようとする意図があります。`lockr -ia .ssh` は一般的なLinuxコマンドではなく、ログでは`command.failed`と記録されているため、誤記か、特定のマルウェアやツールが使用する独自のコマンドである可能性がありますが、主要な意図は`authorized_keys`の改変にあると考えられます。
    *   **使用された公開鍵:** `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`

### 3. 脅威レベルとその理由

*   **脅威レベル: 高 (High)**
*   **理由:**
    *   **認証突破の成功:** ハニーポット上であるとはいえ、攻撃者は `root` ユーザーとして複数回ログインに成功しており、これは現実のシステムでも脆弱なパスワードが使用されていれば、容易に認証を突破される可能性があることを示しています。
    *   **永続的アクセスの意図:** ログイン後にSSH公開鍵を植え付ける試みは、システムへの永続的なバックドアを設置する明確な意図を示しています。公開鍵認証によるアクセスは、パスワード認証ログが残らないため、後の検出が困難になる可能性があります。
    *   **Root権限の標的:** 攻撃者がシステム内で最も高い権限を持つ `root` ユーザーを標的にしていることから、システム全体を掌握し、広範な悪意ある活動（データ窃取、マルウェア配布、他のシステムへの攻撃拠点化など）を行う可能性が非常に高いです。
    *   **自動化された攻撃:** 攻撃は複数の異なるパスワードを短時間で試行し、ログイン後の手順も自動化されているため、特定のターゲットに限定されない広範なスキャンと攻撃の一部であると考えられます。これは、今後も継続的な攻撃や、他のシステムへの横展開が行われる可能性を示唆しています。

### 4. 推奨アクション

この攻撃はハニーポットで観測されたものですが、実際のシステムで同様の攻撃が成功した場合に備え、以下の対策を推奨します。

*   **即時対応:**
    *   **攻撃元IPアドレスのブロック:** ファイアウォールやIPS/IDSにて、攻撃元IPアドレス `173.10.13.18` からのすべての通信を即座にブロックしてください。
    *   **SSHログの緊急確認:** 実際の運用中のSSHサーバーについて、この攻撃元IPアドレスからのアクセスログを直ちに確認し、ログイン試行（特に`root`ユーザー）や認証成功がないか、不審なコマンド実行がないか調査してください。
    *   **システム脆弱性スキャン:** 万が一、システムが侵害された可能性がある場合、全体的な脆弱性スキャンおよびマルウェアスキャンを実施してください。
*   **SSHセキュリティの強化:**
    *   **パスワード認証の無効化:** 可能であれば、SSHパスワード認証を無効にし、公開鍵認証のみを許可するように設定を変更してください。
    *   **`root`ユーザーの直接ログイン禁止:** `PermitRootLogin no` を設定し、`root`ユーザーの直接SSHログインを禁止してください。管理者権限での作業が必要な場合は、一般ユーザーでログイン後、`su`または`sudo`を使用するようにしてください。
    *   **強力なパスワードポリシーの徹底:** すべてのシステムユーザー（特に管理者アカウント）に対して、複雑で長いパスワードの使用を義務付け、定期的な変更を推奨してください。
    *   **SSHポートの変更:** 標準の22番ポートではなく、使用されていない高ポート番号に変更することで、自動化されたスキャン攻撃の対象となる頻度を減少させることができます。
    *   **レート制限の導入:** Fail2banなどのツールを導入し、短時間での複数回ログイン失敗を検知・ブロックする仕組みを導入してください。
*   **ログ監視とアラート体制の強化:**
    *   SSHのログイン成功/失敗、特に`root`ユーザーや管理者権限ユーザーのログイン試行、及び成功に対するアラートを強化してください。
    *   `authorized_keys`ファイルなど、SSH設定ファイルへの不審な変更を監視し、アラートを発する仕組みを導入してください。
    *   ログイン後の不審なコマンド実行（特にファイル操作やネットワーク通信関連）を検知できるようなルールを追加してください。
*   **情報共有:**
    *   攻撃元IPアドレス `173.10.13.18` および攻撃者が使用しようとした公開鍵情報（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を社内および関係する外部の脅威情報プラットフォーム（ISAC/CSIRTなど）と共有し、他の組織への注意喚起と情報収集に役立ててください。