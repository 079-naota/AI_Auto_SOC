# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 15:47:18

---

SOCアナリストとして、提供された攻撃ログを分析し、以下のレポートを作成しました。

---

### **攻撃分析レポート**

**報告日時:** 2026-04-26T01:35:00Z (分析日時)
**攻撃元IPアドレス:** 182.70.243.207

---

#### **1. 攻撃の概要と目的**

攻撃元IPアドレス 182.70.243.207から、システムに対する継続的なSSHブルートフォース/辞書攻撃が観測されました。攻撃者は`steam`, `tunnel`, `cloud`, `gitlab`, `345gs5662d34`といった複数のユーザー名と、様々なパスワードの組み合わせを試行しました。

特に悪質な点として、`root`ユーザーに対する複数のパスワードが突破され、ログインに成功していることが確認されました。ログイン成功後、攻撃者は即座に以下のコマンドを実行することで、システムへの永続的なアクセス経路を確立しようと試みました。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

これは、`root`ユーザーの`.ssh/authorized_keys`ファイルに攻撃者の公開鍵を追加し、パスワードなしでSSHログインできるバックドアを設置する明確な試みです。これらの永続化の試みは、最初のログイン成功（01:26:29Z）以降、合計6回にわたって繰り返されました。

攻撃の目的は、SSH経由での初期アクセスを獲得し、`root`権限でバックドアを設置することで、対象システムへの永続的な制御権を確立することであると推測されます。

---

#### **2. 推測される手法・使用ツール**

*   **SSH ブルートフォース/辞書攻撃**: 短時間のうちに多数の異なるユーザー名とパスワードの組み合わせを試行していることから、自動化された攻撃ツール（例: Hydra, NmapのNSEスクリプトなど）が使用されている可能性が高いです。ログからは、`steam`, `root`, `345gs5662d34`, `tunnel`, `cloud`, `gitlab`などのユーザー名が標的にされています。
*   **バックドア設置（公開鍵認証）**: ログイン成功後に実行されたコマンドは、`rm -rf .ssh && mkdir .ssh && echo "..." >> .ssh/authorized_keys && chmod -R go= ~/.ssh`という典型的なSSH公開鍵バックドアの設置手順です。攻撃者はこの公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を用いて、パスワードなしで再ログインを試みるでしょう。
*   **ファイル属性操作の試み**: `chattr -ia .ssh; lockr -ia .ssh`というコマンドも実行されていますが、`cowrie.command.failed`と記録されていることから、これらのコマンドはハニーポット環境では機能しなかったか、または存在しないコマンド（特に`lockr`）が指定された可能性があります。しかし、これは攻撃者が`.ssh`ディレクトリへの防御機構（例：不変属性）を解除しようとする意図があったことを示唆しています。

---

#### **3. 脅威レベルとその理由**

**脅威レベル: 高 (High)**

**理由:**

*   **`root`権限でのログイン成功**: 攻撃者はシステムで最も高い権限を持つ`root`ユーザーとして複数回ログインに成功しています。これは、もし実環境であればシステム全体の乗っ取りにつながる非常に深刻な状況です。
*   **永続化の試み**: 攻撃者はログイン成功後、速やかにSSH公開鍵バックドアを設置しようと試みました。これは、一時的なアクセスに留まらず、システムの永続的な制御を目的としていることを示しており、非常に高い悪意を持った攻撃です。
*   **継続的な攻撃と執着**: 約1時間にわたり、断続的にSSHログイン試行とバックドア設置の試みを繰り返しています。これは、自動化された攻撃スクリプトが稼働しているだけでなく、標的システムへの侵入に強い執着があることを示唆しています。
*   **広範なユーザー名/パスワード試行**: 一般的なユーザー名（`steam`, `cloud`, `gitlab`など）からランダムな文字列（`345gs5662d34`）まで、幅広い認証情報を試しており、より巧妙な攻撃キャンペーンの一部である可能性も考えられます。

---

#### **4. 推奨アクション**

この攻撃はハニーポットで観測されたものですが、実環境で同様の事象が発生した場合に備え、以下の対策を直ちに実施することを強く推奨します。

1.  **SSHパスワード認証の無効化**:
    *   可能な限り、SSHのパスワード認証を無効化し、公開鍵認証のみを許可するように設定を変更してください（`sshd_config`で`PasswordAuthentication no`を設定）。これにより、ブルートフォース攻撃によるログイン試行を根本的に防ぐことができます。
2.  **SSHパスワードの複雑化と定期的な変更**:
    *   もしパスワード認証を継続する必要がある場合、全てのSSHユーザー（特に`root`）のパスワードを、上記のログで成功したパスワード（例: `QAZwsx`, `Root1234567@@`, `3245gs5662d34`など）とは異なる、非常に複雑なものに変更し、定期的な更新を義務付けてください。
3.  **SSHサービスのセキュリティ強化**:
    *   **rootログインの制限**: `sshd_config`で`PermitRootLogin no`を設定し、`root`ユーザーの直接ログインを禁止してください。特権操作は一般ユーザーでログイン後、`sudo`コマンドを使用することを徹底してください。
    *   **ポート変更**: SSHサービスを標準の22番ポート以外のポートで稼働させることを検討してください（スキャンによる検出を困難にする効果があります）。
    *   **Rate Limitingの導入**: `fail2ban`などのツールを導入し、SSHのログイン試行回数に制限を設け、規定回数以上の失敗があったIPアドレスを一時的または永続的にブロックするように設定してください。
    *   **AllowUsers/DenyUsers**: `sshd_config`でSSHへのアクセスを許可するユーザーを明示的に指定し、不要なユーザーからのアクセスを制限してください。
4.  **侵入検知システム (IDS/IPS) の強化**:
    *   SSHブルートフォース攻撃のパターンを検知し、自動的に遮断できるようなIDS/IPSルールを導入・更新してください。
5.  **ログ監視の強化とアラート設定**:
    *   SSHログインの成功/失敗、特に`root`ユーザーや特権ユーザーのログイン試行、および`.ssh`ディレクトリへの変更に関するログをリアルタイムで監視し、異常を検知した際には直ちにアラートが発せられる体制を構築してください。
6.  **脅威インテリジェンスの活用とIPアドレスのブロック**:
    *   攻撃元IPアドレス 182.70.243.207を脅威インテリジェンスフィードで調査し、既知の悪性IPアドレスリストに追加してください。ファイアウォールでこのIPアドレスからのアクセスを全て遮断することを強く推奨します。
7.  **公開鍵認証設定の監査**:
    *   全てのサーバー上の`.ssh/authorized_keys`ファイルの内容を監査し、不正な公開鍵が追加されていないか確認してください。特にログに記録された公開鍵(`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`)が存在しないか確認し、もし存在すれば直ちに削除してください。また、`.ssh`ディレクトリとその中身のファイル権限が適切に設定されていることを確認してください（例: `~/.ssh`は700、`~/.ssh/authorized_keys`は600）。

---