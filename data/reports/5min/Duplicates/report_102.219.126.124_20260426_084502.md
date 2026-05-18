# SOC自動分析レポート: 102.219.126.124

**生成日時:** 2026-04-26 08:46:06

---

## SOC分析レポート

**日付:** 2026年04月26日
**作成者:** 優秀なSOCアナリスト
**攻撃元IP:** 102.219.126.124

---

### 1. 攻撃の概要と目的

このログは、SSHハニーポット「Cowrie」によって収集された、攻撃元IPアドレス `102.219.126.124` からの悪意のあるSSH接続試行の記録です。

攻撃者は、約1時間20分の間に複数回にわたりSSHサービスへのログインを試みています。最初のログイン試行は失敗しましたが、その後、様々なパスワードを用いて `root` ユーザーでのログインに複数回成功しています。ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確立するため、以下の不正なコマンドを繰り返し実行しようとしています。

1.  `~/.ssh` ディレクトリの属性変更（`chattr -ia .ssh`）を試み、その保護を解除しようとしています。
2.  `~/.ssh` ディレクトリを削除し、再作成しています（`rm -rf .ssh && mkdir .ssh`）。
3.  自身のSSH公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を `~/.ssh/authorized_keys` ファイルに追加しています。これにより、パスワード認証を必要とせずに、攻撃者がいつでもSSH接続できるバックドアが設置されます。
4.  `~/.ssh` ディレクトリのパーミッションを変更し、他のユーザーからのアクセスを制限することで、バックドアの隠蔽を図っています。

攻撃の主な目的は、SSHサービスへの不正ログインを通じて、システムへの永続的なアクセス権（バックドア）を確立することにあると判断されます。

### 2. 推測される手法・使用ツール

*   **攻撃手法:**
    *   **ブルートフォース攻撃 / パスワードスプレー攻撃:** 攻撃者は `drcom`, `ubuntu`, `user` といった一般的なユーザー名や、`root` ユーザーに対して、複数の強力なパスワード（例: `1qaz@WSX3edc$RFV!@`, `ali123456`, `Root8`, `Aa112211.`, `Config123`, `Aa123321` など）を試行しています。これは、自動化されたパスワード推測攻撃である可能性が高いです。
    *   **永続化 (Persistence):** ログイン成功後、`authorized_keys` ファイルに自身の公開鍵を追加することで、システムへの永続的なアクセス経路を確立しようとしています。これは、パスワードが変更された後もアクセスを維持するための典型的な手法です。
    *   **特権昇格の試み (rootアカウントの利用):** 攻撃は主に `root` ユーザーを標的にしており、最高権限でのシステム制御を試みています。
*   **使用ツール:**
    *   SSHブルートフォース攻撃を自動化するツールやスクリプトが使用されていると推測されます。ログイン成功後に一連のコマンドを自動的に実行していることから、シェルスクリプトやPythonなどのスクリプト言語で作成されたツール、または既成のボットネットクライアントの一部である可能性が高いです。
    *   `chattr` コマンドの使用は、ファイル属性の操作によって、より高度な永続化や痕跡隠蔽を図る意図を示唆しています。ただし、`lockr` コマンドは一般的なLinuxシステムには存在しないため、攻撃者が誤ったコマンドを含んでいるか、特定の環境を想定したスクリプトを使用している可能性があります。
    *   公開鍵: `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` この公開鍵のコメント「mdrfckr」は攻撃者グループの特定の識別子や、不特定多数に利用される一般的な攻撃テンプレートの一部である可能性があります。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

*   **ログイン成功の頻度:** 攻撃者は `root` ユーザーとしてハニーポットへのログインに複数回成功しています。これは、もし実際のシステムであれば、重大なセキュリティ侵害につながる非常に危険な状況です。
*   **永続化の試み:** ログイン成功後、攻撃者は即座に `authorized_keys` ファイルに自身の公開鍵を追加しようとしています。これは、システムへの永続的なバックドアを設置し、長期的な支配を目的とした明確な意図があることを示しています。永続的なアクセスは、さらなる攻撃（データ窃盗、マルウェア展開、C2通信確立など）の足がかりとなります。
*   **特権アカウント（root）の標的:** 最も権限の高い `root` アカウントが継続的に標的とされており、攻撃成功時の影響が最大化されることを意図しています。
*   **自動化された攻撃:** 複数の異なるパスワードを短期間に試行し、成功後に定型的なコマンドを実行していることから、自動化された攻撃ツールやボットネットの一部であると推測されます。このような攻撃は、継続的かつ広範囲にわたる可能性があります。

### 4. 推奨アクション

このログはハニーポットのものであるため実際のシステム侵害は発生していませんが、実際のシステムであれば取るべき対策と、ハニーポットから得られたインテリジェンスを活用した予防策を以下に示します。

#### 緊急対応 (もし実際のシステムが攻撃された場合):

1.  **攻撃元IPアドレスのブロック:** 攻撃元IPアドレス `102.219.126.124` をファイアウォールまたはIPS/IDSで即座にブロックし、さらなるアクセスを遮断します。
2.  **侵害検知の確認:** ログに記録されたすべての成功したユーザー名とパスワードの組み合わせ（`root:1qaz@WSX3edc$RFV!@`, `root:ali123456`, `root:Root8`, `root:Aa112211.`, `root:Config123`, `root:Aa123321`, `root:3245gs5662d34` など）が、組織内のシステムで実際に使用されていないか緊急で確認します。もし使用されている場合は、以下の対応を行います。
    *   該当アカウントのパスワードを直ちにリセットします。
    *   該当システムについて、侵害の痕跡（不正なファイル、不審なプロセス、ネットワーク接続など）がないか、フォレンジック調査を実施します。
    *   `~/.ssh/authorized_keys` ファイルに、攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が追加されていないか確認し、発見された場合は削除します。
3.  **広範囲な確認:** ネットワーク内の他のSSHサーバーが同様の攻撃を受けていないか、関連するログインログやシステムログを包括的に確認します。

#### 予防策と長期的なセキュリティ強化:

1.  **SSHセキュリティ強化:**
    *   **Rootログインの無効化:** SSHサーバー設定（`/etc/ssh/sshd_config`）で `PermitRootLogin no` を設定し、`root` ユーザーでの直接ログインを禁止します。
    *   **パスワード認証の無効化（可能であれば）:** 厳格な公開鍵認証のみを許可し、パスワード認証を無効化します（`PasswordAuthentication no`）。
    *   **多要素認証 (MFA) の導入:** 可能であれば、SSHアクセスにMFAを導入し、セキュリティを強化します。
    *   **鍵認証の厳格化:** 公開鍵認証を使用する場合、鍵ファイルのパーミッションが適切であること（`authorized_keys` は`600`、`.ssh` ディレクトリは`700`）を確認し、`StrictModes yes` を有効にします。
2.  **アクセス制限:**
    *   SSHポート（デフォルトは22/TCP）へのアクセスを、信頼できるIPアドレス範囲に限定する（IPホワイトリスト方式）。
    *   可能な限り、SSHポートをデフォルトの22番から変更する（ポートノッキングなどの追加対策も検討）。
3.  **アカウントとパスワードポリシー:**
    *   すべてのシステムユーザーに対し、強力で複雑なパスワードの使用を義務付け、定期的なパスワード変更を強制します。
    *   アカウントのロックアウトポリシーを適切に設定し、ブルートフォース攻撃に対する耐性を高めます。
    *   不要なユーザーアカウントを削除し、サービスアカウントなどの最低限の権限を持つユーザーのみを使用します。
4.  **ログ監視と検知:**
    *   SSH認証ログを含むすべてのシステムログをSIEMなどの集中ログ管理システムに統合し、リアルタイムでの監視、異常検知、アラート生成を可能にします。
    *   Fail2banや類似のツールを導入し、不正なログイン試行を自動的に検知・ブロックするメカニズムを構築します。特にSSHに対するブルートフォース攻撃に有効です。
    *   `authorized_keys` ファイルの変更を監視し、不正な変更があればアラートを発する設定を導入します。
5.  **脅威インテリジェンスの活用:**
    *   本レポートで特定された攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を脅威インテリジェンスデータベースで検索し、既知の攻撃グループやマルウェア、ボットネットに関連付けられていないか調査を継続します。