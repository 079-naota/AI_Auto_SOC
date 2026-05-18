# SOC自動分析レポート: 172.208.48.177

**生成日時:** 2026-04-26 19:27:36

---

## SOC分析レポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `172.208.48.177` から、ターゲットシステム（Cowrieハニーポット）のSSHサービスに対する継続的なブルートフォース攻撃が確認されました。この攻撃は、様々なユーザー名とパスワードの組み合わせを試行して不正なログインを試みるものでした。

ログによると、攻撃者は複数の異なるパスワードを用いて `root` ユーザーでのログインに複数回成功しています。ログイン成功後、攻撃者は以下の定型的な一連のコマンドを実行しました。

1.  `chattr -ia .ssh; lockr -ia .ssh`: 既存の `.ssh` ディレクトリの属性を変更し、保護を解除しようと試みています（`lockr` コマンドはハニーポット上で失敗）。
2.  `rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: 既存の `.ssh` ディレクトリを削除し、新規作成した上で、攻撃者自身の公開鍵 (`mdrfckr` というコメント付き) を `authorized_keys` に追加しようとしました。これにより、パスワードなしで永続的にSSHログインできるバックドアを設置する意図があったと判断されます。

この攻撃の目的は、脆弱な認証情報を悪用してシステムへの初期アクセスを確立し、さらに公開鍵ベースの永続的なバックドアを設置することで、将来的な不正アクセス経路を確保することにあると推測されます。

### 2. 推測される手法・使用ツール

*   **SSH ブルートフォース攻撃:**
    *   攻撃者は、`nagios`, `seekcy`, `rich`, `testuser`, `user`, `nexus`, `ftpuser`, `postgres`, `cisco` といった様々なユーザー名と、それに対応する（あるいは一般的な）パスワードを組み合わせて試行しています。
    *   特に `root` ユーザーに対しては、`qwe123...`, `3245gs5662d34`, `Abcd1234!@#$`, `aa888888`, `b123456`, `Root1234$` など、異なる強力なパスワードが複数回試行され、ログインに成功しています。これは、攻撃者が複数のパスワードリストを使用しているか、高度なブルートフォースツールを利用している可能性を示唆します。
*   **永続化 (Persistence) 手法:**
    *   ログイン成功後、SSHの公開鍵認証メカニズムを悪用して、攻撃者自身の公開鍵を `~/.ssh/authorized_keys` に追加しようとしました。これにより、パスワードを知らなくても当該システムにSSH接続できるようになり、永続的なアクセス経路が確立されます。
*   **使用ツール:**
    *   一連の継続的なブルートフォース試行と、ログイン後の定型的なコマンド実行パターンから、この攻撃は手動ではなく、自動化されたスクリプトまたはマルウェア（ボットネット）によって行われている可能性が極めて高いです。
    *   SSHブルートフォースには `Hydra`, `Medusa`, `Nmap` のスクリプトなどが一般的に利用されます。
    *   公開鍵のコメントが `mdrfckr` であること、および毎回同じ鍵を挿入しようとすることから、特定のマルウェアキャンペーンや攻撃グループに関連する活動であると推測されます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

*   **ログイン成功の頻度と影響度:** ハニーポット上であるとはいえ、攻撃者が `root` ユーザーとして複数回ログインに成功しているという事実は、実際のシステムにおいて脆弱なパスワードが存在する場合、容易に最高権限が奪取される危険性があることを示しています。
*   **永続化メカニズムの確立意図:** 攻撃者がログイン後、一貫して公開鍵を介したバックドアの設置を試みていることは、単なる偵察ではなく、システムへの長期的なアクセスと制御を目的としていることを示します。このようなバックドアが設置された場合、パスワードが変更されても攻撃者はシステムへのアクセスを維持できます。
*   **自動化された攻撃の性質:** 継続的かつ定型的な攻撃パターンは、広範囲の標的を狙う自動化されたボットネットの一部である可能性を示唆しており、他のシステムへの類似の攻撃も懸念されます。
*   **潜在的な二次攻撃の可能性:** 不正アクセスが成功した場合、その後の活動として、機密データの窃取、他のシステムへの横展開、マルウェアの配布、ランサムウェア攻撃などが実行される可能性があります。

### 4. 推奨アクション

1.  **攻撃元IPアドレスのブロック:**
    *   ファイアウォール、IDS/IPS、またはWAFにて、攻撃元IPアドレス `172.208.48.177` からのすべての通信をブロックリストに追加してください。
2.  **SSH認証の強化:**
    *   **パスワードポリシーの強化:** 推測されやすいパスワードや、今回のログに記録されたパスワード（`qwe123...`, `Abcd1234!@#$`, `aa888888`, `b123456`, `Root1234$`, `3245gs5662d34` など）を禁止するよう、より複雑で長いパスワードの使用を強制するポリシーを導入してください。
    *   **公開鍵認証の強制:** 可能であれば、パスワード認証を完全に無効にし、公開鍵認証のみを許可するようにSSH設定を変更してください。これはブルートフォース攻撃に対する最も効果的な対策の一つです。
    *   **多要素認証 (MFA) の導入:** SSHログインに対してMFAを導入し、認証セキュリティをさらに強化することを検討してください。
3.  **SSH設定の監査と強化:**
    *   `PermitRootLogin no` を設定し、`root` ユーザーによる直接のSSHログインを禁止してください。特権操作は一般ユーザーでログイン後、`sudo` を介して実行するように運用を徹底してください。
    *   SSHサービスがデフォルトのポート22番を使用している場合、ポート番号を変更することを検討してください（ただし、これは対策の一部であり、本質的な防御ではありません）。
    *   `AllowUsers` または `AllowGroups` ディレクティブを使用して、SSHアクセスを許可するユーザーやグループを厳密に制限してください。
4.  **既存システムに対する緊急脆弱性診断:**
    *   本ログでログインに成功したと記録されているパスワード（`qwe123...`, `3245gs5662d34`, `Abcd1234!@#$`, `aa888888`, `b123456`, `Root1234$`）が、組織内の実際のシステムで現在も使用されていないか緊急で確認し、もし存在する場合は直ちにこれらを含むすべての脆弱なパスワードを変更してください。
    *   `~/.ssh/authorized_keys` ファイルの内容を監査し、不正な公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が追加されていないか確認してください。
5.  **監視体制の強化:**
    *   SSHログインログ（`auth.log`など）およびCowrieログに対する監視ルールを強化し、ブルートフォース攻撃や異常なログイン後の活動を早期に検知できる体制を構築してください。
    *   SIEM (Security Information and Event Management) システムを導入している場合は、これらのログを連携させ、相関分析を通じてより高度な脅威検知を目指してください。
6.  **IOC (Indicator of Compromise) の共有:**
    *   攻撃元IPアドレス `172.208.48.177` および攻撃者が追加しようとした公開鍵情報 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を、関連するセキュリティ情報共有プラットフォームや組織内関係者と共有し、他システムでの防御に役立ててください。