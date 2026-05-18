# SOC自動分析レポート: 172.208.48.177

**生成日時:** 2026-04-26 20:47:44

---

SOCアナリストとして、提供されたログを分析し、以下のレポートを作成しました。

---

### **SOC分析レポート**

**レポートID:** SOC-20260426-001
**分析日時:** 2026-04-26T11:17:00Z
**攻撃元IP:** 172.208.48.177
**対象サービス:** SSH (ポート22)

---

#### **1. 攻撃の概要と目的**

攻撃元IPアドレス `172.208.48.177` から、ターゲットシステム（Cowrieハニーポット）に対して、SSHサービスへの不正アクセスを試みる継続的な攻撃が観測されました。
攻撃は、SSHパスワードの総当たり攻撃（ブルートフォースアタックまたはパスワードスプレーアタック）によって開始されました。特筆すべきは、複数の異なるパスワードを使用して`root`ユーザーでのログインに複数回成功している点です。
ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確立するため、`.ssh/authorized_keys` ファイルに自身のSSH公開鍵を追加しようとしています。これは、将来的にパスワード認証なしでシステムにアクセスできるバックドアを設置し、システムの完全な制御を奪取することを目的としていると推測されます。

---

#### **2. 推測される手法・使用ツール**

*   **初期アクセス（ブルートフォース/パスワードスプレー）:**
    *   攻撃者は、`nagios`, `seekcy`, `rich`, `testuser`, `user`, `nexus`, `ftpuser`, `postgres`, `cisco`などの一般的なユーザー名や、無作為な文字列 (`345gs5662d34`) を試すとともに、`root`ユーザーに対して特に執拗に多数のパスワード (`qwe123...`, `3245gs5662d34`, `Abcd1234!@#$`, `aa888888`, `b123456`, `Root1234$`) を試行しています。
    *   短時間で多様な組み合わせを試み、ログイン成功後の行動が定型化されていることから、自動化されたスクリプトまたは専用のブルートフォースツール（例: Hydra, Nmap, Medusaなど）が使用されている可能性が高いです。

*   **永続化:**
    *   ログイン成功後、攻撃者は以下のコマンドを実行し、自身のSSH公開鍵を`root`ユーザーの`authorized_keys`ファイルに書き込もうと試みています。
        ```bash
        cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~
        ```
    *   また、その前に`chattr -ia .ssh; lockr -ia .ssh`というコマンドも試みていますが、Cowrieの環境では失敗しています。これは、`.ssh`ディレクトリの属性（immutable/append-onlyなど）を解除しようとする試みであり、ファイル操作の妨げとなる保護機構を無力化する意図があったと見られます。
    *   この手法は、システムへの永続的なバックドアを確立するための一般的な方法です。

*   **特定のSSH公開鍵:**
    *   使用されているSSH公開鍵 `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` は、既知の悪意ある活動に関連付けられている可能性があります。このキーの指紋やコメント (`mdrfckr`) は、マルウェアキャンペーンやボットネット活動でよく見られるものです。

---

#### **3. 脅威レベルとその理由**

**脅威レベル: 高 (High)**

**理由:**

*   **複数回のrootログイン成功:** 攻撃者が`root`アカウントで複数の異なるパスワードによりログインに成功している点は非常に深刻です。実際のシステムであれば、これにより攻撃者はシステムに対する完全な制御権を獲得し、任意の操作が可能となります。
*   **永続化の明確な意図:** ログイン成功後、攻撃者が一貫して`.ssh/authorized_keys`に自身の公開鍵を追加しようとしていることから、システムへの永続的なアクセス経路を確立する明確な意図が読み取れます。これにより、パスワードが変更されたとしても攻撃者はアクセスを維持できます。
*   **自動化された攻撃:** 短時間での複数回の試行と定型化されたコマンド実行は、攻撃が自動化されたツールによって行われていることを示唆します。このような攻撃は、発見されにくい形で広範囲にわたるシステムを標的とする可能性があり、深刻な被害につながりやすいです。
*   **権限昇格への直接的な試み:** 攻撃対象が最初からシステム最高権限を持つ`root`ユーザーであるため、成功した場合のインシデントの影響範囲は最大となります。
*   **特定のSSHキーの利用:** 使用されているSSH公開鍵は、既知の悪意ある活動やマルウェアに関連付けられている可能性があり、単一の攻撃者によるものではなく、より大規模な攻撃キャンペーンの一部である可能性も考慮されます。

---

#### **4. 推奨アクション**

以下の緊急対策と恒久対策を実施することを強く推奨します。

**緊急対策 (即時実施):**

1.  **攻撃元IPのブロック:** 攻撃元IPアドレス `172.208.48.177` からのすべての通信を、境界ファイアウォールやWAF等で即座にブロックリストに追加してください。
2.  **SSH公開鍵の確認と削除:** ログに記載されたSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が、本番環境のいずれかのシステム上の`.ssh/authorized_keys`ファイルに追加されていないか緊急で確認し、存在する場合は直ちに削除してください。
3.  **パスワードの緊急変更:** ログに記録されたログイン成功パスワード (`qwe123...`, `3245gs5662d34`, `Abcd1234!@#$`, `aa888888`, `b123456`, `Root1234$`) が実際のシステムで使われている場合、関連するすべてのアカウント（特に`root`アカウント）のパスワードを直ちに変更し、非常に強力なものに設定してください。

**恒久対策 (優先的に実施):**

1.  **SSH設定の強化:**
    *   **パスワード認証の無効化:** 可能であれば、SSHパスワード認証を完全に無効にし、SSH鍵認証のみを許可する設定に変更してください。
    *   **`PermitRootLogin no` の設定:** `sshd_config`ファイルで`PermitRootLogin no`を設定し、`root`ユーザーの直接ログインを禁止してください。必要であれば、一般ユーザーでログイン後に`sudo`を使用するようにしてください。
    *   **Rate Limiting/Account Lockout:** 連続したSSHログイン失敗に対して、一時的なIPブロックやアカウントロックアウトを行う仕組みを導入してください（例: Fail2Ban）。
    *   **SSHポートの変更:** 標準のSSHポート22番を非標準のポートに変更することも、自動化されたスキャンからのヒット数を減らす上で有効です（ただし、これはセキュリティバイアオブスキュリティであり、根本的な対策ではありません）。
    *   **多要素認証 (MFA/2FA) の導入:** 可能であれば、SSHアクセスに対して多要素認証を導入し、セキュリティを強化してください。
2.  **アカウントとパスワードポリシーの棚卸し:**
    *   システム上のすべてのアカウントを棚卸しし、不要なアカウントを削除してください。
    *   すべてのユーザーに対して、複雑性、長さ、定期的な変更を強制する強力なパスワードポリシーを適用してください。
3.  **侵入検知/防御システム (IDS/IPS) の強化:**
    *   SSHブルートフォースアタックを検知し、自動的にブロックできるIDS/IPSルールを導入または強化してください。
4.  **ログの継続的な監視とアラート設定:**
    *   実際のSSHログ（`/var/log/auth.log`など）を含むすべての認証ログをSIEMシステムなどに集約し、不審なログイン試行、特に`root`ユーザーへのログイン成功や、`authorized_keys`ファイルへの変更試行に対して即座にアラートが発報されるように設定してください。
5.  **セキュリティ教育:**
    *   管理者およびユーザーに対し、強力なパスワードの重要性、不審なアクティビティへの警戒、セキュリティベストプラクティスに関する定期的な教育を実施してください。

---