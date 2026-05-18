# SOC自動分析レポート: 101.100.242.72

**生成日時:** 2026-04-26 06:18:09

---

## SOC分析レポート

**報告日時**: 2026-04-26 (ログ分析に基づき仮定)
**報告者**: [あなたの名前/SOCアナリスト]
**事象**: SSHサービスへのブルートフォース攻撃と認証成功後の活動

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `101.100.242.72` から、当社のSSHサービス（ハニーポットであるCowrieで監視）に対し、断続的なブルートフォース攻撃が確認されました。この攻撃では、様々なユーザー名とパスワードの組み合わせが試行されています。

**攻撃の主要な目的は以下の通りと推測されます。**

1.  **SSHサービスへの不正アクセス**: 大量のユーザー名・パスワードを試行し、正規の認証情報を特定すること。
2.  **永続的なアクセス経路（バックドア）の確立**: 認証成功後、攻撃者は自身の公開鍵を `~/.ssh/authorized_keys` ファイルに書き込むことで、パスワードなしで再ログイン可能なバックドアを設置し、システムの永続的な制御権を確保しようとしています。

この攻撃は、ターゲットシステムに対する完全な制御権奪取を狙った初期段階の活動であり、成功した場合、他のマルウェアの展開やデータ窃取などの後続攻撃に繋がる可能性があります。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース攻撃（Brute-force attack）**: 標準的なSSHクライアントと、辞書攻撃や既知の脆弱なパスワードリストを用いた自動化されたログイン試行が行われています。特に `root` ユーザーに対する重点的な試行が確認されています。
    *   **バックドアの設置**: 認証成功後、攻撃者は以下のコマンドを実行し、自身の公開鍵を `~/.ssh/authorized_keys` に追加しようとしています。
        ```bash
        cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~
        ```
        この公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）は、攻撃者のIDを特定する手がかりとなり得ます。
    *   **痕跡の操作**: `chattr` コマンドで属性を変更しようとしたり、`chmod` でパーミッションを設定したりしており、バックドアの安定化と他のユーザーによる改変防止、あるいは発見されにくくする意図がうかがえます。
*   **使用ツール**:
    *   **自動化されたブルートフォースツール**: 大量のログイン試行と複数のユーザー名/パスワードの組み合わせを短い間隔で試行していることから、Hydra, Medusa, Nmapのスクリプト（`ssh-brute`など）、またはカスタムスクリプトのような自動化ツールが使用されている可能性が高いです。

### 3. 脅威レベルとその理由

*   **脅威レベル**: **高 (High)**
*   **理由**:
    1.  **root権限での認証成功**: ログには `root` ユーザーとして、以下の複数のパスワードでログイン成功が記録されています。
        *   `root` / `qwer1234QWER!@#$`
        *   `root` / `3245gs5662d34`
        *   `root` / `Ni123456`
        *   `root` / `ubuntu@123`
        *   `root` / `Password.123`
        *   `root` / `a12348765`
        `root`はシステム上の最高特権を持つユーザーであり、そのアカウントが乗っ取られると、システムに対する完全な制御権が攻撃者に渡ることを意味します。
    2.  **永続性メカニズムの確立**: 認証成功後に、`authorized_keys`に攻撃者の公開鍵を追加するコマンドが実行されており、これはシステムへの永続的なアクセス経路を確保しようとする明確な意図を示します。パスワードが変更されても、攻撃者はキーペア認証で再アクセスすることが可能になります。
    3.  **広範なブルートフォース試行**: `frappe`, `deployer`, `ubuntu`, `admin`, `tester`, `test`, `oracle`, `user`, `zhaoxj`, `345gs5662d34`など、様々なユーザー名とパスワードの組み合わせが試されており、広範なアカウントの脆弱性を探索していることが示唆されます。

### 4. 推奨アクション

この攻撃がハニーポットに対するものであったとしても、同様の攻撃が実環境でも行われる可能性があるため、以下の対策を推奨します。

1.  **攻撃元IPアドレスのブロック**:
    *   ファイアウォールやIDS/IPSにおいて、攻撃元IPアドレス `101.100.242.72` からのすべての通信を直ちにブロックリストに追加し、アクセスを遮断します。
2.  **SSHサービスへのセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能な限り、SSHのパスワード認証を無効化し、公開鍵認証のみを許可する設定に変更します。
    *   **強固なパスワードポリシーの適用**: 全ユーザーに対し、複雑性、長さ、定期的な変更を強制する強固なパスワードポリシーを適用します。特に `root` ユーザーのパスワードは極めて強力なものに設定すべきです。
    *   **多要素認証（MFA）の導入**: SSHログインに多要素認証を導入し、認証のセキュリティレベルを向上させます。
    *   **デフォルトポートの変更**: SSHのデフォルトポート（22番）を非標準のポートに変更し、自動化されたスキャン攻撃からの露出を減らします（これは一時的な対策であり、根本的な解決策ではありません）。
    *   **アクセス元IPアドレス制限**: 信頼できる特定のIPアドレス範囲からのみSSH接続を許可するよう、ファイアウォールルールを設定します。
    *   **レートリミットの設定**: 連続したログイン失敗を検知した場合、一時的に接続を制限またはブロックする設定（例: `fail2ban`の導入）を行います。
3.  **システム侵害の確認（実システムへの影響評価）**:
    *   この攻撃ログが実システムのものであった場合、以下の緊急対応が必要です。
        *   **不正な認証情報の確認**: ログに記載された認証成功パスワード（`qwer1234QWER!@#$`, `3245gs5662d34`, `Ni123456`, `ubuntu@123`, `Password.123`, `a12348765` など）が、他のシステムやサービスで再利用されていないか、緊急で監査・確認し、該当する場合は直ちにパスワードをリセットします。
        *   **`authorized_keys`ファイルの監査とクリーンアップ**: 全ユーザー、特に `root` および特権ユーザーの `~/.ssh/authorized_keys` ファイルを精査し、不正な公開鍵（特にログに記載された `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` の鍵）が追加されていないか確認し、発見した場合は削除します。
        *   **システムの整合性チェック**: 侵害された可能性のあるシステムについて、バックドア、不正なプロセス、設定変更、追加されたファイルがないか、システム全体の整合性チェックを実施します。
        *   **ログの深掘り**: システムログ、認証ログ、アプリケーションログなど、他の関連ログを詳細に分析し、攻撃者がSSHログイン成功後に他の活動（データ窃取、横展開など）を行っていないか確認します。
4.  **ハニーポット監視の継続**:
    *   Cowrieハニーポットは、このような攻撃活動を効果的に捕捉する優れたツールであることが再確認されました。引き続き監視を継続し、攻撃者の動向、使用されるクレデンシャル、新たな攻撃手法やペイロードを収集・分析します。収集された情報は、実システムのセキュリティ強化に役立てます。