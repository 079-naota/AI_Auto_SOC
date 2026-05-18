# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 13:46:53

---

## SOCアナリストによる攻撃レポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `185.216.119.134` から、当社のSSHサービスに対して断続的なブルートフォース攻撃が確認されました。この攻撃の主な目的は、SSH認証情報を窃取し、システムへの不正アクセスを確立することです。

ログからは以下の主要な行動が特定されました。

*   **ブルートフォース攻撃**: `zabbix`, `john`, `satya`, `admin`, `test`, `test1`, `user` といった一般的なユーザー名、および `root` ユーザーに対して、複数のパスワードを試行しています。
*   **認証情報の窃取と不正アクセス**: 複数回にわたり `root` ユーザーでのログインに成功しています。（例: `root:123.com.`, `root:nPSpP4PBW0`, `root:Aa112211.`, `root:123Qwe!@#`, `root:Admin12!@#` など）
*   **持続化（Persistence）の試み**: ログイン成功後、攻撃者は `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~` というコマンドを実行し、自身のSSH公開鍵を `~/.ssh/authorized_keys` ファイルに追加しようとしています。これは、バックドアを設置し、パスワード認証が変更されても永続的なアクセス経路を確保するための行動です。
*   **防御回避の試み**: `cd ~; chattr -ia .ssh; lockr -ia .ssh` というコマンドも実行しようとしていますが、これは `chattr` コマンドで `.ssh` ディレクトリの属性を変更し、保護を試みるものと推測されます（ログ上では `cowrie.command.failed` と記録されており、ハニーポット環境では失敗しています）。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSHブルートフォース/辞書攻撃**: 大量の認証情報を試行していることから、自動化されたパスワード推測攻撃が実施されています。
    *   **持続化（Persistence）**: 認証成功後、SSH公開鍵を利用してバックドアを設置し、今後のアクセスを容易にしようとする試みです。
    *   **ファイル属性操作による防御回避**: `chattr` コマンドの使用は、`.ssh` ディレクトリの属性を操作し、その内容の変更や削除を防ぐことで、バックドアの永続性を高めようとする意図が考えられます。
*   **使用ツール**:
    *   **自動化された攻撃スクリプト/ツール**: 短期間に多数のログイン試行と認証成功後のコマンド実行が行われていることから、特定のSSHブルートフォースツールやマルウェアの一部として組み込まれたスクリプトが使用されている可能性が高いです。
    *   **特徴的なSSH公開鍵**: `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` という公開鍵は、コメント部分 (`mdrfckr`) も含めて特定のマルウェアキャンペーンやボットネットに関連する特徴である可能性があります。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:

*   **`root` ユーザーでの認証成功**: 攻撃者はシステム上で最も高い権限を持つ `root` ユーザーでのログインに複数回成功しています。これは、システムが完全に侵害される危険性が極めて高い状態であることを意味します。
*   **持続化メカニズムの確立**: ログイン成功後、攻撃者は `authorized_keys` に自身の公開鍵を追加しようとしており、永続的なアクセス経路の確立を意図しています。これにより、パスワードが変更されても、攻撃者がバックドアを通じて再度侵入する可能性が高まります。
*   **活発で継続的な攻撃**: 同じ攻撃元IPから、短時間に複数回のログイン試行と認証成功後の悪意あるコマンド実行が繰り返されており、攻撃者が明確な目的を持って積極的に活動していることを示しています。
*   **潜在的な二次被害**: 認証に成功し、システムが完全に侵害された場合、攻撃者はシステムのリソースを悪用して他のシステムへの攻撃、データ窃取、マルウェアの展開など、さらなる被害を引き起こす可能性があります。

### 4. 推奨アクション

**緊急対応（即時実施）**:

1.  **攻撃元IPアドレスのブロック**: ファイアウォール、IDS/IPS、またはSSHデーモンの設定 (`/etc/hosts.deny`など) を利用して、攻撃元IPアドレス `185.216.119.134` からの全ての通信を直ちにブロックしてください。
2.  **侵害された可能性のあるアカウントのパスワード変更**: ログに記録されている認証成功した全ての `root` ユーザーアカウント（および試行された他のユーザー名 `zabbix`, `john`, `satya`, `admin`, `test`, `test1`, `user`, `345gs5662d34` など）について、直ちに複雑で推測困難なパスワードに変更してください。
3.  **SSH `authorized_keys` ファイルの確認と削除**: 侵害された可能性のある全てのユーザーのホームディレクトリ (`/root/.ssh/authorized_keys` など) を確認し、攻撃者によって追加された公開鍵（特に `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を削除してください。また、全ての `~/.ssh` ディレクトリのパーミッションが適切 (`700` など) であることを確認してください。
4.  **システム侵害の有無の徹底的な確認**: ログイン成功後に他の不審な活動（マルウェアのダウンロードと実行、設定ファイルの改ざん、新たなユーザーアカウントの作成、外部への不審な通信、Webシェルなどの設置）がないか、システムログ（`auth.log`, `syslog`, `audit log`など）、ネットワーク接続ログ、プロセスの監視などを実施し、詳細なフォレンジック分析を行ってください。

**長期的な対策**:

1.  **SSH認証の強化**:
    *   パスワード認証を無効化し、公開鍵認証のみを許可することを強く推奨します。
    *   公開鍵認証を使用する場合でも、鍵ファイルのパーミッション管理を厳格化し、パスフレーズを設定してください。
    *   可能であれば、二要素認証（MFA）を導入し、セキュリティを強化してください。
2.  **ブルートフォース対策の導入**:
    *   Fail2banなどのツールを導入し、一定回数のログイン失敗があったIPアドレスを自動的にブロックする設定を行ってください。
    *   SSHサービスへのアクセスを、特定の信頼できるIPアドレス範囲からのみに制限する（ホワイトリスト方式）。
    *   SSHデーモンの標準ポート (22番) を変更することも、自動化されたスキャン攻撃への対策として有効です（ただし、これはセキュリティバイオブスケーラントであり、本質的な対策ではありません）。
3.  **パスワードポリシーの強化**: 全てのシステムユーザーに対して、文字数、複雑性、履歴制限などを含む強固なパスワードポリシーを強制し、定期的なパスワード変更を義務付けてください。デフォルトパスワードや辞書攻撃で推測されやすいパスワードの使用を禁止してください。
4.  **不要なユーザーアカウントの削除**: 攻撃ログに試行されたユーザー名の中で、現在使用されていない、または不要なアカウントが存在する場合は、セキュリティリスクを減らすために削除してください。
5.  **ログ監視の強化とSIEM連携**: SSHログインログを含む全てのシステムログを継続的に監視し、異常なログイン試行や認証成功、不審なコマンド実行を早期に検知できる体制を構築してください。可能であれば、SIEM (Security Information and Event Management) システムを導入し、ログの集中管理と相関分析を行ってください。
6.  **定期的な脆弱性スキャンとパッチ適用**: 定期的にシステムに対する脆弱性スキャンを実施し、発見された脆弱性には速やかにパッチを適用してください。
7.  **従業員のセキュリティ意識向上**: 従業員に対し、安全なパスワードの利用、不審なメールやアクティビティへの注意喚起など、セキュリティ意識向上トレーニングを継続的に実施してください。