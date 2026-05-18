# SOC自動分析レポート: 154.83.12.193

**生成日時:** 2026-04-26 01:16:10

---

## SOCアナリストレポート

**攻撃元IP**: 154.83.12.193
**分析日時**: 2026-04-26

### 1. 攻撃の概要と目的

攻撃元IPアドレス `154.83.12.193` から、SSHサービスに対して継続的な不正アクセスが試行されています。ログからは、複数の異なるユーザー名とパスワードを組み合わせたブルートフォース攻撃、またはパスワードスプレー攻撃が行われていることが確認できます。

特に注目すべきは、攻撃者が複数回にわたり `root` ユーザーのパスワードを突破し、SSHログインに成功している点です。ログイン成功後、攻撃者は以下の定型的なコマンドをほぼ同時に実行しています。

`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

このコマンドは、`~/.ssh`ディレクトリを再作成し、攻撃者自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を`authorized_keys`ファイルに書き込むことで、SSHキー認証によるバックドアを設置し、永続的なアクセス経路を確保することを目的としています。

### 2. 推測される手法・使用ツール

*   **攻撃手法**:
    *   **SSH ブルートフォース/パスワードスプレー攻撃**: `ubuntu`, `root`, `test`, `sftptest`などの一般的なユーザー名や推測されやすいユーザー名に対して、複数のパスワードを繰り返し試行しています。これは自動化された辞書攻撃またはパスワードスプレー攻撃の特徴です。
    *   **永続化 (Persistence)**: ログイン成功後に、攻撃者自身のSSH公開鍵を`~/.ssh/authorized_keys`に書き込むことで、パスワードなしで将来的にシステムへ再アクセスできるバックドアを設置しようとしています。これは典型的な永続化の手法です。
    *   **特権昇格 (Privilege Escalation)**: 直接的な特権昇格コマンドは見られませんが、`root`ユーザーとしてログインに成功しているため、その後の行動は最高権限で行われることを意味します。
*   **使用ツール**:
    *   一連のログイン試行とログイン成功後のコマンド実行は、非常に短時間で自動的に行われていることから、SSHのクレデンシャルクラッキングとペイロード（公開鍵の設置）実行を自動化するツールが使用されている可能性が高いです。具体的なツール名としては、`Hydra`や`Medusa`、または攻撃者が作成したカスタムスクリプトなどが考えられます。
    *   最初に実行された`chattr -ia .ssh; lockr -ia .ssh`コマンドは失敗していますが、これは`.ssh`ディレクトリのファイル属性（immutable属性など）を解除し、書き込みを可能にしようとしたものと推測されます。

### 3. 脅威レベルとその理由

*   **脅威レベル: 高 (High)**

*   **理由**:
    1.  **`root`権限の奪取**: 攻撃者は複数回にわたってシステム上の最高権限を持つ`root`ユーザーの認証情報を突破し、ログインに成功しています。これは、対象システムに対する完全な制御権を奪取する可能性を意味し、最も深刻な脅威の一つです。
    2.  **永続化メカニズムの確立**: ログイン成功後、攻撃者はバックドアとしてSSH公開鍵を設置しようとしています。これにより、パスワードが変更されたとしても、攻撃者は秘密鍵を用いてシステムへのアクセスを維持できるリスクがあります。
    3.  **自動化された攻撃の継続性**: 攻撃が自動化されているため、特定のターゲットに限定されず、広範なインターネットスキャンの一部として標的とされた可能性が高いです。これは、今後も同様の攻撃が継続されるか、他のシステムも標的となる可能性があることを示唆しています。
    4.  **明確な悪意**: 設置しようとした公開鍵のコメントに「mdrfckr」という侮蔑的な文字列が含まれており、攻撃者の明確な悪意が示されています。

このログはハニーポット (Cowrie) のものであるため、実際のシステム侵害は発生していませんが、もしこれが実運用環境で発生していた場合、システムは完全に侵害され、データ漏洩、システム破壊、マルウェア感染、他のシステムへの攻撃基盤としての悪用など、極めて甚大な被害につながる可能性がありました。

### 4. 推奨アクション

このログはハニーポットで観測されたものですが、実システムで同様の事象が発生した場合を想定し、以下の緊急対応と予防的対策を直ちに実施してください。

1.  **緊急対応 (Immediate Actions)**:
    *   **攻撃元IP (154.83.12.193) のブロック**: ファイアウォールまたはIDS/IPSにて、当該IPアドレスからのSSH (ポート22) 接続を即座にブロックしてください。
    *   **`root`パスワードの即時変更**: ログに確認された`root`ユーザーのパスワード（`nPSpP4PBW0`, `zj@123456`, `QWERqwer1234`, `Root2024!`, `Aa112211.`）を含む、全ての`root`アカウントおよび管理者権限を持つアカウントのパスワードを、複雑で推測されにくいものに直ちに変更してください。
    *   **不正なSSH公開鍵の確認と削除**: 全てのSSHサーバーにおいて、`~/.ssh/authorized_keys`ファイルの内容を確認し、攻撃者が設置しようとした公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、発見された場合は直ちに削除してください。
    *   **`.ssh`ディレクトリのパーミッション確認**: `~/.ssh`ディレクトリおよび`authorized_keys`ファイルのパーミッションが適切に設定されているか確認し、必要に応じて修正してください（例: `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/authorized_keys`）。
    *   **システム侵害の有無の詳細調査**: 不正なログインが成功した可能性があるため、対象システムの詳細なフォレンジック調査を実施し、攻撃者が他のマルウェアを設置していないか、システム設定を変更していないか、データが窃取されていないかなどを確認してください。
    *   **SSHサービスの設定強化**:
        *   `sshd_config`ファイルにて `PermitRootLogin no` を設定し、`root`ユーザーによる直接SSHログインを禁止してください。
        *   可能であれば、`PasswordAuthentication no` を設定し、パスワード認証を無効化して公開鍵認証のみに切り替えることを強く推奨します。

2.  **予防的対策 (Preventative Measures)**:
    *   **多要素認証 (MFA) の導入**: SSHログインに多要素認証を導入し、認証セキュリティを強化してください。
    *   **ブルートフォース対策ツールの導入**: `fail2ban`などのツールを導入し、連続したログイン失敗を検出し、一時的にIPアドレスをブロックするなどの対策を講じてください。
    *   **SSHポートの変更**: 標準のSSHポート22番を別の高位ポートに変更することを検討してください。これにより、一般的なスキャンからの検出リスクを低減できます。
    *   **厳格なパスワードポリシーの適用**: 強固で推測されにくいパスワードの使用を強制し、定期的なパスワード変更をユーザーに義務付けるポリシーを適用してください。
    *   **ログ監視体制の強化**: SSH認証ログ (`/var/log/auth.log` など) を含め、システムのセキュリティログを継続的に監視し、異常なアクセスや挙動を早期に検出できる体制を強化してください。
    *   **セキュリティパッチの適用**: 使用しているOSやソフトウェアに最新のセキュリティパッチが適用されていることを定期的に確認し、適用してください。