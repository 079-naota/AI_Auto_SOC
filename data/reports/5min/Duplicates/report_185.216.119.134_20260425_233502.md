# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 23:37:46

---

## SOCアナリスト レポート

### 1. 攻撃の概要と目的

攻撃元IP `185.216.119.134` から、当社のSSHサービスに対して継続的なブルートフォース攻撃が試行されました。この攻撃者は、複数のユーザー名とパスワードの組み合わせを試行し、最終的に`root`アカウントを含むいくつかのユーザーでログインに成功しています。ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確立するため、SSH公開鍵認証によるバックドア（`~/.ssh/authorized_keys`への公開鍵追加）を設置しようとしました。

この攻撃の主な目的は、当社のシステムへの不正アクセスと、その後の継続的なアクセス権の維持であると推測されます。

### 2. 推測される手法・使用ツール

*   **攻撃手法:**
    *   **ブルートフォース/辞書攻撃:** ログには`zabbix`, `john`, `satya`, `admin`, `test`, `test1`, `user`などの一般的なユーザー名や、推測しやすいパスワードを含む多数のログイン試行が記録されています。これは、自動化されたツールによる大規模なブルートフォース攻撃、または辞書攻撃が実行されたことを強く示唆しています。
    *   **権限昇格 (未遂):** 複数の試行で`root`アカウントへのログインに成功しています。`root`はシステム最高の権限を持つアカウントであり、これにアクセスすることは攻撃者にとって最も重要な目標の一つです。
    *   **永続化 (Persistence):** ログイン成功後、攻撃者は以下のコマンドを実行しようとしました。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh`ディレクトリのファイル属性を変更し、削除や変更に対する保護を無効化しようとしています。これは、`authorized_keys`ファイルの改ざんを容易にするための準備と考えられます。 Cowrieログでは`cowrie.command.failed`となっているため、これらのコマンドは実行されなかったか、ハニーポットがエミュレートできなかったと考えられます。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: これは、`~/.ssh`ディレクトリを再作成し、攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を`authorized_keys`に追加するものです。これにより、攻撃者はパスワードなしでSSHアクセスを維持しようとしました。
*   **使用ツール:**
    *   **ブルートフォースツール:** 大量のログイン試行を短時間で行っていることから、Hydra, Medusa, NmapのNSEスクリプト、またはカスタムスクリプトなどの自動化されたSSHブルートフォースツールが使用された可能性が高いです。
    *   **SSHクライアント:** SSHプロトコルに対応した標準的なクライアント（OpenSSHなど）が使用されていると推測されます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **最高権限アカウントへの不正アクセス成功:** 攻撃者が`root`アカウントで複数回ログインに成功している点は、実システムであればシステム全体が完全に侵害されたことを意味し、極めて深刻な事態です。
2.  **永続的なアクセス経路の確立試行:** ログイン後に`authorized_keys`への公開鍵追加を試みていることから、一時的なアクセスではなく、検知されずに継続的にシステムを制御しようとする明確な意図が読み取れます。これにより、パスワードが変更されても攻撃者はアクセスを維持できます。
3.  **広範な影響の可能性:** この攻撃は、インターネットに公開された脆弱なSSHサーバーを狙う自動化されたスキャン活動の一部である可能性が高く、同様の手法が他のシステムにも適用されるリスクがあります。
4.  **コマンド実行によるシステム改変の意図:** `chattr`コマンドや`authorized_keys`の変更など、システムの設定を改変し、防御機構を弱め、自身のアクセスを永続化しようとする明確な挙動が確認されています。

このログはハニーポット（Cowrie）のものであるため、実際のシステムが直接的な被害を受けたわけではありませんが、もし実環境であれば重大なセキュリティ侵害につながる非常に危険な攻撃パターンです。

### 4. 推奨アクション

以下の緊急対応と予防策を速やかに実施することを推奨します。

#### 緊急対応 (Immediate Actions):

1.  **攻撃元IPのブロック:** 攻撃元IPアドレス `185.216.119.134` を、ファイアウォール、IDS/IPS、またはWAFなどのセキュリティ機器で直ちにブロックリストに追加し、アクセスを遮断します。
2.  **全SSHパスワードの変更:** ログインに成功した`root`アカウントを含む、全てのシステムユーザーのSSHパスワードを、予測困難な強力なものに直ちに変更します。
3.  **SSH公開鍵の確認と削除:**
    *   全てのユーザー（特に`root`）のホームディレクトリ配下の`~/.ssh/authorized_keys`ファイルの内容を確認します。
    *   ログに記載されている攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、存在する場合は直ちに削除します。
    *   不審な公開鍵や、認識のないSSHキーがないかも併せて確認し、削除します。
4.  **侵害調査 (Forensic Investigation):**
    *   システム全体で不審なファイル、プロセス、cronジョブ、ネットワーク接続、権限昇格の痕跡などがないか、詳細なフォレンジック調査を実施し、二次感染やさらなるバックドアが存在しないかを確認します。
    *   特に、攻撃者が侵入後に他のツールをダウンロードしたり、ユーザーを追加したりしていないかを確認します。
5.  **ログの継続監視:** SSH認証ログ（`/var/log/auth.log`など）やシステムログを継続的に監視し、今後不審なSSH接続や活動がないか注意深く確認します。

#### 予防策 (Proactive Measures):

1.  **SSH公開鍵認証の強制:** パスワード認証を無効化し、公開鍵認証のみを許可するようにSSHサーバー設定（`/etc/ssh/sshd_config`）を変更します。これは最も効果的な対策の一つです。
    *   `PasswordAuthentication no`
    *   `ChallengeResponseAuthentication no`
2.  **rootログインの禁止:** `PermitRootLogin no` を設定し、`root`ユーザーでの直接ログインを禁止します。必要な場合は一般ユーザーでログイン後、`sudo`を利用するように徹底します。
3.  **Fail2Banなどの導入:** ブルートフォース攻撃を自動的に検知し、攻撃元IPアドレスを一時的または永続的にブロックするツール（例: Fail2Ban, CrowdSecなど）を導入します。
4.  **多要素認証 (MFA) の導入:** 可能であれば、SSH接続に多要素認証を導入し、セキュリティを強化します。
5.  **強力なパスワードポリシーの徹底:** 全てのユーザーに対して、十分な長さと複雑さを持つパスワード（大文字、小文字、数字、記号を組み合わせた12文字以上）の使用を義務付け、定期的な変更を推奨します。
6.  **不要なアカウントの削除/無効化:** 使用されていないアカウントは削除または無効化し、攻撃対象を減らします。
7.  **システムおよびソフトウェアのアップデート:** OSやSSHサーバーソフトウェアを含む全てのアプリケーションを最新の状態に保ち、既知の脆弱性を解消します。
8.  **SSHポートの変更:** 標準の22番ポートから、一般的でない別のポート番号に変更することを検討します（これは攻撃を遅延させる効果はありますが、根本的な解決策ではありません）。
9.  **アクセス制限:** ファイアウォールで、信頼できるIPアドレス範囲からのみSSHポートへのアクセスを許可するように制限します。外部からのアクセスが必要な場合は、VPNなどのセキュアな経路を介して接続することを義務付けます。