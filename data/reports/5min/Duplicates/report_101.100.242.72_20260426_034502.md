# SOC自動分析レポート: 101.100.242.72

**生成日時:** 2026-04-26 03:47:00

---

## 攻撃ログ分析レポート

### 1. 攻撃の概要と目的
攻撃元IP `101.100.242.72` から、SSHサービスに対する継続的なブルートフォース攻撃が確認されました。この攻撃者は、様々なユーザー名とパスワードの組み合わせを試行し、最終的に `root` ユーザーの複数のパスワードを特定してログインに成功しています。

ログイン成功後、攻撃者は以下の目的で一連のコマンドを実行しています。
*   **永続化 (Persistence)**: 自身のSSH公開鍵をターゲットシステムの `root` ユーザーの `~/.ssh/authorized_keys` ファイルに追加することで、パスワードなしでの再ログインを可能にする永続的なバックドアを設置しようとしています。これにより、将来的に容易かつステルスにシステムへアクセスできる状態を確立することを目的としています。
*   **権限維持**: `root` ユーザーの権限を維持し、システムに対する完全な制御を確保しようとしています。

### 2. 推測される手法・使用ツール
*   **SSHブルートフォース攻撃**:
    *   攻撃者は `frappe`, `deployer`, `ubuntu`, `admin`, `tester`, `test`, `oracle`, `user`, `zhaoxj` といった一般的なユーザー名、および `root` ユーザーに対して、複数の辞書的なパスワード（例: `frappeuser`, `password123`, `default`, `Admin05`, `tester1`, `Password`, `oracle20`, `user15!`, `zhaoxj`）を試行しています。
    *   特に `root` ユーザーに対しては、`qwer1234QWER!@#$`, `Ni123456`, `ubuntu@123`, `Password.123`, `a12348765`, `3245gs5662d34` など、複数の異なるパスワードでのログイン成功が確認されており、広範なパスワードリストを使用していることが示唆されます。
    *   ログイン試行が短時間で繰り返されていることから、HydraやMedusaなどの自動化されたパスワードクラッキングツール、あるいはカスタムスクリプトが使用されている可能性が高いです。
*   **永続化メカニズムの設置**:
    *   ログイン成功後、攻撃者は以下のコマンドを実行しています。
        ```bash
        cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~
        ```
        このコマンドは、既存の `.ssh` ディレクトリを削除し、新たに作成したディレクトリに攻撃者の公開鍵（コメント `mdrfckr` を含む）を `authorized_keys` として登録し、適切なパーミッションを設定するものです。
    *   最初に `cd ~; chattr -ia .ssh; lockr -ia .ssh` というコマンドも試行されていますが、これはハニーポット環境では失敗しています。`chattr -ia .ssh` はファイル属性を変更し、`.ssh` ディレクトリが変更・削除されないようにする保護を解除する意図があったと考えられます。`lockr` は一般的なLinuxコマンドではないため、攻撃者独自のツールの一部であるか、誤記の可能性があります。

### 3. 脅威レベルとその理由
*   **脅威レベル: 高 (High)**
*   **理由**:
    *   **複数回のRootユーザーログイン成功**: 本ログはCowrieハニーポットのものであるため、実際のシステムへの被害は発生していませんが、攻撃者が `root` ユーザーの有効なパスワードを複数種類特定し、ログインに成功しているという事実は極めて深刻です。もしこれが実環境であれば、攻撃者はシステムに対する完全な制御を獲得したことになります。
    *   **永続化の試み**: ログイン成功後、速やかにSSH公開鍵認証によるバックドアの設置を試みていることから、攻撃者は単なる一時的な侵入ではなく、長期的なアクセス経路の確保を目的としていることが明確です。これにより、データ窃取、マルウェア展開、C2通信など、さらなる悪意のある活動の準備が整えられます。
    *   **特権アカウントへの集中攻撃**: 攻撃者が `root` アカウントに焦点を当ててブルートフォース攻撃を行っている点は、最大の権限獲得を目指していることを示しています。
    *   **自動化された攻撃**: 広範なパスワードリストと自動化されたツールによる攻撃は、特定のターゲットを狙う標的型攻撃というより、インターネット全体をスキャンし、脆弱なシステムや弱いパスワードを持つシステムを無差別に探索する広範な攻撃の一部である可能性が高いです。

### 4. 推奨アクション
**緊急対応 (Immediate Actions):**
1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `101.100.242.72` を、ファイアウォールやIDS/IPSで直ちにブロックし、今後のアクセスを遮断します。
2.  **パスワードの緊急変更**: ログに記録された `root` ユーザーのパスワード（`qwer1234QWER!@#$`, `Ni123456`, `ubuntu@123`, `Password.123`, `a12348765`, `3245gs5662d34`）が**実際のシステムで使用されていないことを確認**し、もし使用されている場合は、関係する全てのシステムで直ちに**強力でユニークなパスワードに変更**します。他のユーザーアカウントのパスワードも網羅的にレビューし、不審なものがあれば変更します。
3.  **SSH公開鍵のレビュー**: 全てのサーバーの `root` ユーザーおよび他の特権ユーザーの `~/.ssh/authorized_keys` ファイルの内容をレビューし、不正なSSH公開鍵（特にログ内の `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないことを確認します。不正な鍵が発見された場合は直ちに削除します。
4.  **侵害調査の実施**: ログから確認されたパスワードが使用されていた可能性のあるシステムに対して、徹底的な侵害調査（Compromise Assessment）を実施します。不審なプロセス、ファイル、ネットワーク接続、特権昇格の痕跡、その他のバックドアの有無を確認します。

**長期対策 (Long-term Measures):**
1.  **SSH公開鍵認証の強制**: パスワード認証を無効化し、SSH公開鍵認証のみを許可するようにSSH設定 (`/etc/ssh/sshd_config` の `PasswordAuthentication no` と `PermitRootLogin prohibit-password` または `no`) を変更します。
2.  **多要素認証 (MFA) の導入**: 可能な限りSSHログインにMFAを導入し、認証セキュリティを強化します。
3.  **SSHログインの制限**: `root` ユーザーでの直接SSHログインを禁止し、一般ユーザーでログイン後、`sudo` を利用するように運用を改善します。
4.  **レートリミットおよびIPブロックの自動化**: ログイン失敗回数に応じてIPアドレスを一時的または永続的にブロックするFail2BanやCrowdSecなどのツールを導入し、ブルートフォース攻撃を自動的に軽減します。
5.  **強力なパスワードポリシーの適用**: 組織全体で、長さ、複雑性、定期的な変更を強制する強力なパスワードポリシーを適用します。
6.  **システムのパッチ適用と更新**: 全てのシステムを最新の状態に保ち、既知の脆弱性を悪用されるリスクを低減します。
7.  **監視の強化**: SSHログインログを常に監視し、不審なログイン試行や成功、特権操作がないか、SIEM (Security Information and Event Management) システム等と連携してリアルタイムでアラートを生成できる体制を構築します。
8.  **ポートスキャン対策**: ファイアウォールで不必要なポートを閉鎖し、外部からのSSHアクセスは必要最小限に留める、またはVPN経由に限定することを検討します。