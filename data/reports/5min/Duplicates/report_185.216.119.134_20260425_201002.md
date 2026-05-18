# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 20:12:11

---

## SOC分析レポート

**インシデント概要：SSHサービスへのブルートフォース攻撃と不正な永続化の試み**

### 1. 攻撃の概要と目的

攻撃元IPアドレス `185.216.119.134` から、当方ハニーポットのSSHサービスに対して広範なブルートフォース攻撃が実施されました。攻撃は複数回のログイン試行を経て、最終的に `root` ユーザーでのログインに成功しています。

ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確立するため、自身のSSH公開鍵を `root` ユーザーの `~/.ssh/authorized_keys` に追加しようとしました。この行動は、一度パスワード認証で侵入に成功した後、より堅牢な公開鍵認証を用いて将来的なアクセスを確保する目的があると考えられます。

**攻撃のタイムライン:**
*   **04:15:39 - 04:37:24**: `zabbix`, `john`, `satya` といったユーザー名に対するログイン試行失敗。
*   **04:38:28**: `root` ユーザー、パスワード `123.com.` で**ログイン成功**。直後に`~/.ssh/authorized_keys`への公開鍵追加コマンド実行。
*   **04:38:30**: `root` ユーザー、パスワード `3245gs5662d34` でログイン成功。
*   **04:39:29**: `admin` ユーザーに対するログイン試行失敗。
*   **04:40:29**: `root` ユーザー、パスワード `nPSpP4PBW0` で**ログイン成功**。直後に再度`~/.ssh/authorized_keys`への公開鍵追加コマンド実行。
*   **04:40:32**: `root` ユーザー、パスワード `3245gs5662d34` でログイン成功。
*   **04:41:29**: `root` ユーザー、パスワード `Aa112211.` で**ログイン成功**。直後に再度`~/.ssh/authorized_keys`への公開鍵追加コマンド実行。
*   **04:41:32**: `root` ユーザー、パスワード `3245gs5662d34` でログイン成功。
*   **04:42:31**: `root` ユーザー、パスワード `123Qwe!@#` で**ログイン成功**。直後に再度`~/.ssh/authorized_keys`への公開鍵追加コマンド実行。
*   **04:42:33**: `root` ユーザー、パスワード `3245gs5662d34` でログイン成功。
*   **04:43:31 - 04:46:30**: `test`, `test1`, `user` といったユーザー名に対するログイン試行失敗。
*   **04:47:32**: `root` ユーザー、パスワード `Admin12!@#` で**ログイン成功**。直後に再度`~/.ssh/authorized_keys`への公開鍵追加コマンド実行。

### 2. 推測される手法・使用ツール

*   **攻撃手法**:
    *   **ブルートフォースアタック / パスワードスプレー**: 攻撃者は複数の一般的なユーザー名（`zabbix`, `john`, `satya`, `admin`, `test`, `user`）や、特権アカウントである `root` に対して、辞書攻撃や総当たり攻撃と推測される多様なパスワードを試行しています。短時間での連続したログイン試行から、自動化されたツールが使用されている可能性が高いです。
    *   **永続化 (Persistence)**: ログイン成功後、攻撃者は以下のコマンドを実行し、自身の公開鍵をサーバーに登録することで、将来的にパスワードなしでSSHアクセスを確立しようとしました。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh` （属性変更やロックを試行）
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
            *   このコマンドは、既存の `.ssh` ディレクトリを削除し、再作成した上で、特定の公開鍵 `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` を `authorized_keys` に追加し、適切なパーミッション (`chmod -R go= ~/.ssh`) を設定するものです。

*   **使用ツール**:
    *   SSHクライアント。
    *   ブルートフォース攻撃を自動化するスクリプトまたはツール（例: Hydra, NmapのSSH関連スクリプト）。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **特権アカウント（`root`）のログイン成功**: 攻撃者はシステム上で最も高い権限を持つ `root` アカウントへのログインに複数回成功しています。これにより、攻撃が実環境で発生した場合、システムに対する完全な制御権が奪取されることになります。
2.  **永続的アクセスの試み**: 攻撃者はログイン成功後、速やかに自身のSSH公開鍵を登録することで、将来的にパスワードを知らなくてもシステムにアクセスできる永続的なバックドアを設置しようとしました。これは、一度侵入が発覚してパスワードが変更されても、攻撃者がアクセスを維持するための典型的な手法です。
3.  **自動化された攻撃の可能性**: 攻撃行動は短時間で連続して行われ、ログイン試行から公開鍵設置までの一連のプロセスが繰り返されていることから、自動化されたスクリプトやボットによって実行されている可能性が高いです。このような自動化された攻撃は、他の脆弱なシステムに対しても同時に進行している可能性があります。
4.  **広範な影響**: `root`権限が奪取された場合、攻撃者はデータの窃取、システム設定の改ざん、マルウェアの展開、他のシステムへの攻撃拠点としての利用（踏み台）、さらにはシステムの完全な破壊など、あらゆる悪意のある活動を実行することが可能になります。

### 4. 推奨アクション

このログはハニーポットの記録ですが、実際のシステムで同様の攻撃が発生した場合を想定し、以下の緊急および中期・長期対策を推奨します。

**A. 緊急対応（Immediate Actions）:**

1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `185.216.119.134` をファイアウォール、またはIPS/IDSで即座にブロックし、アクセスを遮断してください。
2.  **SSHパスワード認証の無効化と多要素認証の導入**:
    *   `PermitRootLogin no` を設定し、`root`アカウントでのSSH直接ログインを禁止してください。
    *   パスワード認証を完全に無効化し、公開鍵認証のみを許可するように設定 (`PasswordAuthentication no`)。
    *   可能な限り、SSHログインに多要素認証（MFA）を導入してください。
3.  **不正なSSH公開鍵の確認と削除**:
    *   全てのユーザー、特に`root`アカウントの `~/.ssh/authorized_keys` ファイルを緊急で確認してください。
    *   以下の公開鍵、または不明な公開鍵が登録されている場合、直ちに削除してください。
        `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`
    *   `.ssh`ディレクトリとその中身のファイルパーミッションが適切であるか確認してください。
4.  **全ユーザーパスワードのリセットとポリシー強化**:
    *   全てのシステムユーザーアカウントのパスワードを強制的にリセットし、強力なパスワードポリシー（大文字・小文字・数字・記号を含む12文字以上など）を適用してください。

**B. 中期・長期対策（Mid- to Long-Term Actions）:**

1.  **侵入検知・防止システム (IDS/IPS) の導入・強化**: ブルートフォースアタックを検知し、自動的に遮断するFail2Banなどのツールを導入または設定強化してください。
2.  **SSHポートの変更**: デフォルトの22番ポートから別のポート番号に変更することで、自動化されたスキャンからの露出を減らしてください。
3.  **ログ監視の強化**: SSHログインログ（成功・失敗両方）、特に`root`ユーザーや特権ユーザーのログイン試行、および`~/.ssh/authorized_keys`への変更に関するログをリアルタイムで監視する体制を構築してください。SIEMツールとの連携も検討してください。
4.  **システム監査と脆弱性診断**: 定期的にシステムの脆弱性診断を実施し、潜在的なセキュリティホールを特定・修正してください。
5.  **セキュリティ意識向上トレーニング**: 従業員に対し、安全なパスワードの利用やフィッシング攻撃への注意喚起など、セキュリティ意識向上トレーニングを定期的に実施してください。

上記対策を速やかに実行し、セキュリティリスクを最小限に抑えることを強く推奨します。