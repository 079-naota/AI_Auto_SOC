# SOC自動分析レポート: 103.117.56.152

**生成日時:** 2026-04-26 20:21:16

---

## 攻撃ログ分析レポート

### 1. 攻撃の概要と目的

攻撃元IP `103.117.56.152` は、複数の異なるユーザー名とパスワードを試行するSSHブルートフォース攻撃を繰り返し実施しました。この攻撃は、まず一般的なユーザー名（`testuser`, `bot`, `postgres`, `user1`, `steam`, `ubuntu`, `wang`, `oracle`など）と辞書的なパスワードを組み合わせて認証を試みました。

最終的に、`root` ユーザーに対して複数のパスワード（`Aa@12345`, `odoo123`, `nPSpP4PBW0`, `xxZZ1234`, `Aa112211.`）でログインに成功したことが記録されています（これはハニーポットの挙動を指します）。ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確立することを目的とし、以下の不正なコマンドを実行しました。

- `cd ~; chattr -ia .ssh; lockr -ia .ssh`：`.ssh`ディレクトリの属性を変更し、内容の変更を可能にしようとしました（`lockr`は標準コマンドではないため失敗）。
- `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`：このコマンドは、既存の`.ssh`ディレクトリを削除し、再作成した上で、攻撃者の公開鍵（コメント部分が`mdrfckr`）を`authorized_keys`ファイルに追加し、適切なパーミッションを設定するものです。これにより、攻撃者は今後パスワードなしでSSHアクセスを確立できるバックドアを設置しようとしました。

公開鍵の設置後には、その鍵を利用したアクセスが試行され（`345gs5662d34`ユーザーでのログイン失敗、その後の`root`ユーザーでのログイン成功は公開鍵認証によるものと推測）、アクセスの確立を確認していると見られます。

### 2. 推測される手法・使用ツール

-   **手法:**
    -   **SSHブルートフォース攻撃 / パスワードスプレー攻撃:** 大量のユーザー名とパスワードの組み合わせを自動的に試行することで、脆弱な認証情報を特定しようとしました。
    -   **永続化メカニズムの確立:** ログイン成功後、SSHの公開鍵認証を悪用し、自身の公開鍵を`~/.ssh/authorized_keys`に設置することで、パスワード認証を迂回して将来的にいつでもアクセスできるバックドアを作成しようとしました。これは、侵害後の足場固めとして一般的な手法です。
-   **使用ツール:**
    -   **自動化されたSSHクライアントまたはスクリプト:** 連続するログイン試行と定型的なコマンド実行パターンから、HydraやNmapのNSEスクリプトのような自動化されたブルートフォースツールや、それを組み込んだシェルスクリプトが使用されている可能性が高いです。
    -   **マルウェアに関連する公開鍵:** `authorized_keys`に追加された公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）は、MiraiボットネットなどのIoTマルウェアキャンペーンでよく見られるものであり、この攻撃が広範なボットネット活動の一部である可能性を強く示唆しています。

### 3. 脅威レベルとその理由

-   **脅威レベル: 高 (High)**
-   **理由:**
    1.  **実質的なシステム侵害（ハニーポット上）:** ログ上では `root` ユーザーでのログインに複数回成功しており、実際のシステムであれば完全な侵害を意味します。これは攻撃の成功度合いが非常に高いことを示します。
    2.  **永続化のためのバックドア設置試行:** ログイン成功後に、攻撃者の公開鍵を`authorized_keys`に追加しようとするコマンドが実行されていることは、単なる一時的なアクセスではなく、恒久的なシステムへのアクセス経路を確立しようとしている明確な意図を示しています。これにより、パスワードが変更された後でも、攻撃者は鍵情報があればシステムに再アクセスすることが可能になります。
    3.  **既知の悪意ある公開鍵の使用:** 使用された公開鍵は、過去にMiraiなどのボットネットで利用されたものと一致しており、この攻撃が自動化された大規模なボットネットの一部である可能性が高いです。これは、システムが乗っ取られた場合、DDoS攻撃の踏み台や暗号通貨マイニング、さらなるマルウェア拡散などに悪用される危険性があることを意味します。
    4.  **広範囲なブルートフォース試行:** 特定のターゲットに絞った攻撃ではなく、一般的なユーザー名とパスワードを多数試行していることから、インターネットに公開されたSSHサービスを持つ脆弱なサーバーを無差別に探索する活動の一環と見られます。

### 4. 推奨アクション

このログはハニーポット上のものであるため、実際のシステムへの直接的な被害は発生していませんが、同様の攻撃が実環境に仕掛けられた場合の対策として以下の行動を推奨します。

1.  **攻撃元IPアドレスのブロック:**
    *   ファイアウォール、IDS/IPS、またはACL（アクセス制御リスト）にて、攻撃元IPアドレス `103.117.56.152` からのすべての通信をブロックリストに追加し、今後の接続を拒否してください。
2.  **SSH認証の強化:**
    *   **パスワード認証の無効化:** 可能な限り、SSH接続でのパスワード認証を無効にし、公開鍵認証のみを許可する設定（`PasswordAuthentication no`）を適用します。
    *   **Rootログインの禁止:** `root`ユーザーの直接ログインを禁止する設定（`PermitRootLogin no`）を適用し、必要であれば一般ユーザーでログイン後、`su`または`sudo`を使用するように徹底します。
    *   **強力なパスワードポリシー:** パスワード認証を継続する場合でも、すべてのユーザーに対して、複雑性、長さ、有効期限、履歴制限などを含む強力なパスワードポリシーを強制します。
    *   **多要素認証 (MFA) の導入:** SSHログインに多要素認証（例: TOTP、FIDO2デバイス）を導入し、認証情報の漏洩があった場合のセキュリティリスクを軽減します。
3.  **公開鍵管理の徹底:**
    *   **`authorized_keys`の監査:** すべてのシステムユーザーの`~/.ssh/authorized_keys`ファイルを定期的に監査し、不正な公開鍵（特に今回の攻撃で確認された鍵`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないことを確認し、不正なものがあれば即座に削除します。
    *   **パーミッションの厳格化:** `.ssh`ディレクトリおよび`authorized_keys`ファイルのパーミッションを厳格に設定（例: `.ssh`は`700`、`authorized_keys`は`600`）し、不適切な書き込み権限を防ぎます。
4.  **監視とアラートの強化:**
    *   SSHログインログ（認証成功・失敗両方）をSIEMや中央ログ管理システムに集約し、異常なログイン試行パターン（短時間での多数のログイン失敗、普段と異なるIPからのログイン、未知の公開鍵によるログイン成功など）を検知した場合に、即座にアラートを発するように設定します。
    *   `chattr`コマンドなどのファイル属性変更コマンドの実行を監視します。
5.  **システムセキュリティの最適化:**
    *   SSHサービスのデフォルトポート22番から別の高位ポートへの変更を検討します（これはセキュリティの絶対的な解決策ではないが、自動スキャンノイズの低減に役立ちます）。
    *   OSおよびSSHサーバーソフトウェアを常に最新のバージョンに保ち、既知の脆弱性への対策を行います。
    *   不要なサービスやポートはすべて閉じ、攻撃対象領域を最小化します。
6.  **インシデントレスポンス計画の確認:**
    *   万が一、システムが侵害された場合のインシデントレスポンス計画（封じ込め、根絶、復旧の手順）を定期的に確認し、必要に応じて更新します。