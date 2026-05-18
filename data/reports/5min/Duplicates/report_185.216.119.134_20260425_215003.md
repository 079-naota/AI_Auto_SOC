# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 21:52:29

---

## SOC分析レポート

### 1. 攻撃の概要と目的

攻撃元IP `185.216.119.134` から、システムに対するSSH接続の試行が多数確認されました。これはブルートフォース（総当たり）攻撃または辞書攻撃と判断されます。攻撃者はrootアカウントを含む複数のユーザーアカウントに対して、様々なパスワードの組み合わせを試みています。

最終的な攻撃の目的は、システムへの不正なrootアクセス権の取得、および永続的なバックドア（SSH公開鍵）の設置による持続的なアクセス経路の確立であると推測されます。

このログはハニーポット (Cowrie) 上で観測されたものであり、実際のシステム侵害は発生していませんが、攻撃者がログインに成功したと認識し、さらに踏み込んだ攻撃行動を試みていることが明らかになっています。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース/辞書攻撃**: SSHサービスに対して、事前に用意されたユーザー名とパスワードのリストを使用して、ログイン試行を繰り返す手法です。ログには`zabbix`, `john`, `satya`, `admin`, `test`, `user`といった一般的なユーザー名や、`root`ユーザーに対する試行が多数含まれており、パスワードも推測されやすいものから複雑なものまで広範囲にわたっています。
    *   **永続的なアクセス確立**: ログイン成功後、攻撃者は`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`というコマンドを実行し、自身の公開鍵を`authorized_keys`ファイルに追加しようとしています。これにより、パスワード認証を必要とせず、SSH鍵認証による再接続が可能になります。
    *   **痕跡隠蔽/防御妨害**: 一部のログイン成功後には、`cd ~; chattr -ia .ssh; lockr -ia .ssh`というコマンドも試行されています。これは`.ssh`ディレクトリに対する不変属性（immutable attribute）の解除やロックを試み、その後の操作（`authorized_keys`の変更など）を容易にし、あるいは防御側による改ざん検出を妨害する意図があった可能性があります。ただし、`cowrie.command.failed`となっているため、ハニーポット環境ではこれらのコマンドは実行されなかったか、または期待通りに機能しなかったと考えられます。

*   **使用ツール**:
    *   ログのパターンから、Hydra、Medusa、NmapのSSHブルートフォーススクリプト、または攻撃者が自作した自動化スクリプトなど、ブルートフォース攻撃を自動化するツールが使用されている可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **root権限奪取の試み**: 攻撃者は最も機密性の高いrootユーザーアカウントに焦点を当て、ログイン試行を繰り返しています。ハニーポット上では複数回rootでのログインが成功しており、これは攻撃者の試みが成功する可能性が高いことを示唆します。
2.  **永続的なアクセス確立の試み**: ログイン成功後に不正なSSH公開鍵を設置しようとしている行動は、単なる情報収集や一時的な侵入にとどまらず、システムへの永続的なアクセス経路を確保し、長期的な制御を確立しようとする明確な意図を示しています。これは実際のシステムであれば深刻な侵害につながります。
3.  **自動化された攻撃**: 短期間に多数の異なるクレデンシャルでのログイン試行と、ログイン成功後の自動的なコマンド実行から、この攻撃が手動ではなく自動化されたツールやスクリプトによって実行されていることが推測されます。このような自動化された攻撃は、多数の標的に対して効率的に行われるため、広範な脅威となります。
4.  **不審な公開鍵**: 注入されようとしている公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）は、攻撃者が特定のマルウェアキャンペーンやボットネットの一部として使用している可能性があります。

### 4. 推奨アクション

1.  **攻撃元IPのブロック**:
    *   直ちに攻撃元IPアドレス `185.216.119.134` をファイアウォールやWAF等でブロックリストに追加し、さらなるアクセスを拒否してください。
2.  **SSHセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能であれば、SSHパスワード認証を無効にし、公開鍵認証のみに限定してください。
    *   **強力なパスワードポリシーの適用**: 全てのユーザーアカウント、特に特権アカウントに対し、複雑で推測されにくいパスワードの使用を義務付け、定期的な変更を推奨してください。
    *   **多要素認証 (MFA) の導入**: SSHログインに多要素認証を導入し、セキュリティを大幅に向上させてください。
    *   **レートリミットと不正ログイン対策ツールの導入**: `Fail2Ban` などのツールを導入し、一定回数のログイン失敗があったIPアドレスを自動的にブロックする設定を行ってください。
    *   **SSHポートの変更 (緩和策)**: 標準のSSHポート22番から別の高ポート番号に変更することで、自動化されたスキャンからの攻撃機会を減らすことができます（ただし、これは検出回避のためのものであり、本質的な防御策ではありません）。
    *   **rootログインの制限**: SSH経由でのroot直接ログインを禁止し、一般ユーザーでログイン後に`sudo`コマンドを使用する運用に切り替えてください。
3.  **システム監査とログ監視の強化**:
    *   提供された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が自社のシステム上の`authorized_keys`ファイルに存在しないか、緊急で確認してください。もし存在した場合は、直ちに削除し、該当するシステムの完全なフォレンジック調査を実施してください。
    *   SSHログインログ、認証ログ、コマンド実行ログなどの監視を強化し、異常なログイン試行や特権コマンドの実行を迅速に検知できる体制を構築してください。
4.  **ユーザーアカウントの棚卸し**:
    *   ログに登場する`zabbix`, `john`, `satya`, `admin`, `test`, `user`といったアカウント名が、現在使用されていない古いアカウントやデフォルトアカウントとして存在していないか確認し、不要なアカウントは削除または無効化してください。

---