# SOC自動分析レポート: 101.100.242.72

**生成日時:** 2026-04-26 06:58:03

---

## SOC分析レポート

### 1. 攻撃の概要と目的

攻撃元IP `101.100.242.72` から、当社のSSHサービスに対して継続的なブルートフォース攻撃が試行されました。複数のユーザー名とパスワードの組み合わせが試された結果、特に`root`ユーザーにおいて複数回のログイン成功が確認されています。

ログイン成功後、攻撃者は以下の目的で一連のコマンドを実行しようとしています。

1.  **永続的なアクセス経路の確立:** `.ssh/authorized_keys`ファイルに自身の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を書き込むことで、パスワード認証なしで将来的に再アクセスできるバックドアを設置しようとしています。
2.  **既存のセキュリティ対策の無効化:** `chattr -ia .ssh; lockr -ia .ssh`といったコマンドを試行しており、`.ssh`ディレクトリに対する不変属性（`i`属性）を解除するなど、システム管理者によって設定されたファイル保護属性を無効化しようとする意図が伺えます。（`lockr`は不明なコマンドのため実行に失敗しています）。

これらの行動は、標的システムに対する完全な制御の奪取、情報の窃取、あるいは他の攻撃活動の足がかりとすることを目的としていると強く推測されます。

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **SSHブルートフォース/辞書攻撃:** ログには、`frappe`, `deployer`, `ubuntu`, `admin`, `tester`, `test`, `oracle`, `user`, `zhaoxj`などの一般的なユーザー名や、`root`ユーザーに対して、多数の異なるパスワードを試行している記録があります。これは自動化されたブルートフォース攻撃または辞書攻撃の典型的なパターンです。
    *   **永続化 (Persistence):** ログイン成功後、`.ssh/authorized_keys`ファイルを操作して、自身が生成したSSH公開鍵を登録しようとしています。これにより、パスワード認証なしで、いつでもターゲットシステムにアクセスできる状態を作り出そうとしています。
*   **使用ツール:**
    *   **ブルートフォースツール:** 複数のユーザー名とパスワードを高速かつ反復的に試行していることから、Hydra、Medusa、Nmapの`ssh-brute`スクリプトなどの自動化されたツールが使用されている可能性が高いです。
    *   **自動化されたシェルスクリプト:** ログイン後のコマンド入力が非常に定型的かつ迅速に行われていることから、攻撃者が事前に準備したシェルスクリプトを自動実行していると推測されます。

### 3. 脅威レベルとその理由

**脅威レベル: Critical (高)**

**理由:**

*   **複数回の`root`ログイン成功:** ログには`root`ユーザーで合計5回のログイン成功が記録されており、これはシステムに対する最大の権限を奪取されかけたことを意味します。ハニーポット環境でなければ、深刻な侵害に至っていたでしょう。
*   **恒久的なバックドアの設置試行:** 攻撃者がログイン後に`authorized_keys`を操作し、自身のSSH公開鍵を登録しようとしたことは、一度の侵害で終わらず、将来にわたって継続的にシステムへのアクセスを維持しようとする明確な意図を示しています。
*   **攻撃の継続性と執拗さ:** 攻撃者は複数のセッションにわたり、様々なユーザー名とパスワードを試し、ログイン成功後も繰り返し不正な公開鍵の設置を試みています。これは、単発の攻撃ではなく、ターゲットシステムへの侵入に強い意欲を持つ攻撃者によるものと判断できます。
*   **不明なコマンドの試行:** `lockr`というコマンドはCowrieハニーポットでは`command.failed`と記録されており、これは攻撃者が独自の、または一般的ではないツール/スクリプトを持ち込もうとしている可能性を示唆しています。

### 4. 推奨アクション

#### 緊急対応 (Immediate Actions):

1.  **攻撃元IPのブロック:** 攻撃元IPアドレス `101.100.242.72` からのすべてのネットワークアクセスを、ファイアウォール、IPS/IDS、またはセキュリティグループで即座にブロックしてください。
2.  **パスワードの緊急変更と監査:** ログに記録されたログイン成功パスワード（`qwer1234QWER!@#$`, `Ni123456`, `ubuntu@123`, `Password.123`, `a12348765`, `3245gs5662d34`）が実稼働環境のどのユーザー（特に`root`）で使用されていないかを確認し、もし使用されている場合は、直ちに複雑なものに変更してください。また、これらのパスワードが他のシステムで使い回されていないか、広範な監査を実施してください。
3.  **SSH公開鍵の監査:** すべてのシステムにおいて、`.ssh/authorized_keys`ファイルの内容を精査し、不正な公開鍵（特にログ内の`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が登録されていないか確認し、発見した場合は削除してください。
4.  **関連ログの確認:** 実際のSSHサーバーの認証ログ (`/var/log/auth.log`など) や他のシステムログを詳細に確認し、このIPアドレスからのアクセスや不審な活動が他にないか調査してください。

#### 長期的な対策 (Long-term Measures):

1.  **ブルートフォース対策ツールの導入:** Fail2Banなどのツールを導入し、SSH認証失敗回数に基づいたIPアドレスの自動ブロックを設定してください。
2.  **SSHアクセスの制限:**
    *   SSHのデフォルトポート (22番) を変更し、一般的なスキャンからの検出を困難にしてください。
    *   ファイアウォールルールを強化し、SSHサービスへのアクセスを特定の信頼できるIPアドレス範囲またはVPN経由に限定してください。
3.  **認証方法の強化:**
    *   SSHパスワード認証を無効化し、公開鍵認証のみに限定してください。公開鍵には強固なパスフレーズを設定することを必須としてください。
    *   可能であれば、多要素認証 (MFA) をSSHアクセスに導入してください。
4.  **`root`ログインの禁止:** SSH経由での`root`ユーザーによる直接ログインを禁止し、一般ユーザーでログイン後に`sudo`を使用する運用を徹底してください。
5.  **パスワードポリシーの強化:** すべてのユーザーアカウントに対して、複雑さ、長さ、変更頻度に関する厳格なパスワードポリシーを適用してください。
6.  **システムの最新化:** オペレーティングシステムおよびインストールされているすべてのソフトウェアパッケージを定期的に更新し、既知の脆弱性への対策を講じてください。
7.  **脅威インテリジェンスの活用:** ログから抽出された不正な公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb6Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を脅威インテリジェンス情報として登録し、他の環境での出現がないか監視してください。