# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 19:46:45

---

## SOCレポート：SSHブルートフォースおよび認証情報窃取・永続化の試み

### 1. 攻撃の概要と目的

攻撃元IPアドレス `185.216.119.134` から、システムへのSSHサービスに対するブルートフォース攻撃が確認されました。この攻撃は複数のユーザー名とパスワードの組み合わせを試行し、最終的に`root`ユーザーとして複数回認証に成功しています。認証成功後、攻撃者は自身のSSH公開鍵をターゲットシステムの`.ssh/authorized_keys`に追加することで、将来的なアクセス経路（バックドア）を確立し、システムの永続的な制御を試みています。

このログはハニーポット (Cowrie) 上で記録されたものであり、実際のシステムへの直接的な侵害はシミュレートされていますが、攻撃者の目的はシステムの管理者権限の奪取と、永続的なアクセス経路の確保であると推測されます。

### 2. 推測される手法・使用ツール

*   **SSHブルートフォース/パスワードスプレー攻撃**: ログには`zabbix`, `john`, `satya`, `admin`, `test`, `test1`, `user`といった複数の一般的なユーザー名や、`root`ユーザーに対する複数の異なるパスワード試行が記録されています。これは、辞書攻撃やパスワードスプレー攻撃といったブルートフォース手法が用いられていることを示唆しています。
*   **自動化されたスクリプト/ツール**: 短時間で多数のログイン試行と、認証成功後の定型的なコマンド実行（SSH公開鍵の追加）が行われていることから、手動操作ではなく、HydraやMedusaのようなSSHブルートフォースツール、あるいはNmapのNSEスクリプト、専用のボットネットスクリプトなど、自動化されたツールが使用されている可能性が高いです。
*   **認証情報の窃取・永続化**: 認証成功後、攻撃者は以下のコマンドを試行しています。
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh` （`chattr`/`lockr`コマンドの誤記または存在しないコマンドのため失敗）
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
    このコマンドは、既存の`.ssh`ディレクトリを削除し、新たに作成した`.ssh/authorized_keys`ファイルに特定の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を書き込み、パーミッションを設定することで、攻撃者がパスワードなしでSSHアクセスできるバックドアを設置しようとするものです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**
*   **管理者権限 (root) の奪取**: ログには、攻撃者が`root`ユーザーとして複数回認証に成功している記録があります。実システムであれば、`root`権限の奪取はシステム全体が完全に侵害されることを意味し、最も深刻な脅威の一つです。
*   **永続化の試み**: 認証成功後、攻撃者はSSH公開鍵を`.ssh/authorized_keys`に追加することで、永続的なアクセス経路を確立しようとしています。これにより、パスワードが変更されたとしても、攻撃者は秘密鍵を持つことでシステムに再アクセスできるようになります。
*   **広範な攻撃活動**: 複数のユーザー名とパスワードを短時間で試行していることから、これは標的型攻撃というよりは、インターネット上でSSHサービスを公開しているシステムを無差別にスキャンし、脆弱な認証情報を悪用しようとするボットネット活動の一部である可能性が高いです。
*   **潜在的な影響の甚大さ**: この攻撃が実システムに対して成功した場合、データの窃取、システム破壊、マルウェアの配布、他のシステムへの攻撃拠点としての悪用など、壊滅的な被害につながる可能性があります。

### 4. 推奨アクション

**緊急対応 (Immediate Actions):**

1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `185.216.119.134` からのSSH接続を、ファイアウォールやIPS/IDSで即座にブロックしてください。
2.  **SSH認証ログの精査**: 実際のSSHサーバの認証ログ（例: `/var/log/auth.log`や`journalctl`など）を詳細に確認し、同様の不正なログイン試行や認証成功がないか確認してください。特に`root`ユーザーに対する試行に注意してください。
3.  **パスワードの緊急変更**: ログに記録された、認証成功した全てのユーザー（特に`root`）のパスワードを直ちに変更してください。他のシステムで同じパスワードを使い回している場合は、それらのパスワードも変更してください。
4.  **不正なSSH公開鍵の確認・削除**: 認証成功したユーザー（特に`root`）のホームディレクトリ配下の`.ssh/authorized_keys`ファイルを確認し、ログに記録された公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、存在する場合は直ちに削除してください。
5.  **システム侵害の調査**: 認証成功が確認されたシステムについて、追加の侵害兆候（不審なプロセス、未知のファイル、不正なネットワーク通信、設定変更など）がないか、フォレンジック調査を実施してください。

**予防的対策 (Preventative Measures):**

1.  **SSH設定の強化**:
    *   **ポート変更**: SSHサービスを標準のポート22以外（例: 2222番など）に変更してください。
    *   **パスワード認証の無効化**: 可能な限り、パスワード認証を無効化し、強力な公開鍵認証のみを許可してください。
    *   **`root`ログインの無効化**: SSH経由での`root`ユーザーの直接ログインを禁止し、必要であれば一般ユーザーでログイン後、`sudo`コマンドを使用するように設定してください。
    *   **最大認証試行回数の制限**: `sshd_config`で`MaxAuthTries`を低く設定し、短時間での試行回数を制限してください。
2.  **多要素認証 (MFA) の導入**: SSHログインにMFAを導入し、認証セキュリティを強化してください。
3.  **ブルートフォース対策ツールの導入**: Fail2banなどのツールを導入し、不正なログイン試行を自動的に検知・ブロックする仕組みを構築してください。
4.  **強力なパスワードポリシーの徹底**: 全てのユーザーに対し、複雑で推測されにくいパスワードの使用を義務付け、定期的な変更を推奨してください。
5.  **脆弱性管理とパッチ適用**: システムおよびSSHデーモンの脆弱性スキャンを定期的に実施し、常に最新のセキュリティパッチを適用してください。
6.  **監視とアラートの強化**: SIEM (Security Information and Event Management) やログ管理システムを導入し、SSHログインログのリアルタイム監視と、不正ログイン試行や認証成功に対するアラート機能を強化してください。
7.  **ハニーポットの継続的な監視**: Cowrieハニーポットのログを継続的に監視し、新たな攻撃パターンや攻撃元のIPアドレスを特定し、セキュリティ対策に活用してください。