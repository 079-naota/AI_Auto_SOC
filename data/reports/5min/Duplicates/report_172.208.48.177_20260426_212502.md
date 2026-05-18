# SOC自動分析レポート: 172.208.48.177

**生成日時:** 2026-04-26 21:28:24

---

## SOCアナリスト レポート

### 1. 攻撃の概要と目的

このログは、攻撃元IPアドレス `172.208.48.177` からのSSHサービスに対する広範なブルートフォース/辞書攻撃を示しています。攻撃者は、主に `root` ユーザーを含む複数のユーザー名と、様々なパスワードの組み合わせを繰り返し試行しています。

攻撃の主な目的は以下の2点と推測されます。

1.  **SSH認証情報の窃取**: 脆弱なユーザー名とパスワードの組み合わせを特定し、SSHアクセス権を獲得すること。特にシステムに対する最高権限を持つ `root` アカウントの奪取を狙っています。
2.  **永続化 (Persistence) の確立**: ログイン成功後、攻撃者自身の公開鍵を標的システムの `~/.ssh/authorized_keys` ファイルに追加することで、パスワード認証なしで永続的にSSHアクセスを可能にするバックドアを設置しようとしています。これにより、たとえパスワードが変更されたとしても、攻撃者は継続してシステムにアクセスできる状態を作り出すことを意図しています。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSH ブルートフォース/辞書攻撃**: ログには、`nagios`, `root`, `seekcy`, `rich`, `testuser`, `user`, `nexus`, `ftpuser`, `postgres`, `cisco` といった多様なユーザー名に対し、複数の異なるパスワードを試行した痕跡があります。特に `root` ユーザーに対しては、`qwe123...`, `3245gs5662d34`, `Abcd1234!@#$`, `aa888888`, `b123456`, `Root1234$` といった複数のパスワードでログインに成功しており、これは自動化された辞書攻撃またはパスワードスプレー攻撃の典型的なパターンです。
    *   **永続化の試み**: ログイン成功後、攻撃者は以下のコマンドを実行しています。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリのimmutable (変更不可) 属性を解除し、`lockr` コマンドでロックを試みることで、後続の操作が妨げられないようにする意図が伺えます。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: 既存の `.ssh` ディレクトリを削除し、再作成した上で、攻撃者自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を追加し、適切なパーミッションを設定しています。これは永続的なアクセス経路を確立するための明確な行為です。
*   **使用ツール**: Cowrieハニーポットのログであるため、具体的な攻撃ツール名は特定できませんが、このような一連のブルートフォース攻撃とコマンド実行は、`Hydra`、`Medusa`、またはカスタムスクリプトと`sshpass`などのツールを組み合わせて自動化されている可能性が高いです。公開鍵内のコメント `mdrfckr` は、攻撃グループやキャンペーンの識別子である可能性があります。

### 3. 脅威レベルとその理由

*   **脅威レベル**: **高 (High)**
*   **理由**:
    *   **Root権限の複数回奪取**: ログには `root` ユーザーでのログイン成功が複数回記録されています。これは、もし実際のシステムであれば、攻撃者が最高権限である `root` 権限を完全に掌握したことを意味し、システムへの完全な制御を可能にします。
    *   **明確な永続化の試み**: 攻撃者はログイン後、自身の公開鍵を `authorized_keys` に追加することで、バックドアを設置し、今後のアクセスを容易にしようとしています。これは単なる一時的な侵入ではなく、長期的なアクセスを計画していることを示唆しており、非常に悪質です。
    *   **広範な攻撃活動**: 単一のIPアドレスから大量のログイン試行が行われており、脆弱なSSHサービスを持つシステムをターゲットにした一般的なスキャンおよび攻撃活動の一部であると考えられます。これは、標的型攻撃というよりは、感染したボットネットの一部、あるいは脆弱なサーバーを探し回る自動化されたマルウェアによって行われている可能性も示唆しています。
    *   **潜在的な影響の甚大さ**: もしこの事象が実際の運用環境で発生していた場合、攻撃者は機密データの窃取、システムの改ざん、マルウェアの埋め込み、他のシステムへの踏み台利用、さらにはランサムウェア展開など、甚大な損害を引き起こす可能性があります。

### 4. 推奨アクション

この攻撃を受けて、以下の緊急対応と予防措置を強く推奨します。

#### 緊急対応 (Immediate Actions):

1.  **攻撃元IPアドレスのブロック**:
    *   `172.208.48.177` からのすべてのネットワーク接続（特にSSHポート22番）をファイアウォール、IDS/IPS、またはルーターで即座にブロックしてください。
2.  **公開鍵の無効化と削除**:
    *   システム上のすべてのユーザー（特に `root` ユーザー）の `~/.ssh/authorized_keys` ファイルを確認し、ログに記録されている攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、存在する場合は直ちに削除してください。
3.  **漏洩パスワードのリセット**:
    *   ログに記録されたログイン成功時の `root` パスワード (`qwe123...`, `3245gs5662d34`, `Abcd1234!@#$`, `aa888888`, `b123456`, `Root1234$`) は漏洩している可能性が高いです。これらのパスワードを使用している可能性のあるすべてのシステム、サービス、およびユーザーアカウントのパスワードを直ちに、かつ強力なパスワードに変更してください。特に `root` アカウントのパスワードは最優先で変更します。
4.  **システム侵害の確認**:
    *   このログはハニーポットのものですが、もし実システムであった場合、以下の侵害確認が必要です。
        *   不審なプロセスやサービスが稼働していないか。
        *   不正なファイルやスクリプト（特に `/tmp`, `/var/tmp`, `/dev/shm` など）が作成されていないか。
        *   他のバックドアやrootkitがインストールされていないか、整合性チェックツール（`aide`, `rkhunter`, `chkrootkit`など）で確認。
        *   不審なネットワーク接続（特に外部への接続）がないか。
        *   システムログ（`auth.log`, `syslog`など）に他の不審な活動が記録されていないか確認。

#### 予防措置 (Preventive Measures):

1.  **SSH認証の強化**:
    *   **パスワード認証の無効化**: 可能な限りパスワード認証を無効にし、安全な公開鍵認証のみを使用するよう設定してください (`PasswordAuthentication no` in `sshd_config`)。
    *   **Rootログインの禁止**: `root` ユーザーのSSH直接ログインを禁止してください (`PermitRootLogin no` in `sshd_config`)。一般ユーザーでログイン後、`sudo` を利用して権限昇格を行う運用を徹底します。
    *   **強力なパスワードポリシーの適用**: パスワード認証を使用する場合、長さ、複雑性、有効期限などを含む強力なパスワードポリシーを強制し、定期的な変更を義務付けてください。
2.  **多要素認証 (MFA) の導入**:
    *   SSHログインにMFAを導入し、認証セキュリティを大幅に向上させてください。
3.  **不正ログイン検知システムの導入・強化**:
    *   `Fail2Ban` などのツールを導入し、連続したSSHログイン試行失敗を検知した場合、自動的に攻撃元IPアドレスをブロックする仕組みを構築してください。
4.  **ログ監視とアラートの強化**:
    *   SSHログインログや認証ログをリアルタイムで監視し、異常なログイン試行や成功、不審なコマンド実行を検知した際に即座にアラートが発報される体制を確立してください。SIEMなどのログ管理システムへの統合を検討します。
5.  **デフォルトポートの変更またはアクセス制限**:
    *   SSHのデフォルトポート (22番) を変更するか、特定の信頼できるIPアドレス範囲からのアクセスのみを許可するようファイアウォールを設定することで、攻撃対象の露出を減らしてください。VPN経由でのSSHアクセスも有効な手段です。
6.  **定期的なセキュリティパッチ適用**:
    *   OSおよびSSHサービスに関連するソフトウェアのセキュリティパッチを定期的に適用し、既知の脆弱性を悪用されるリスクを低減してください。

このレポートは、提供されたCowrieハニーポットのログに基づいています。実際のシステムでは、攻撃の痕跡がさらに広範囲に及ぶ可能性があるため、詳細なフォレンジック調査と包括的なセキュリティ対策の実施を強く推奨します。