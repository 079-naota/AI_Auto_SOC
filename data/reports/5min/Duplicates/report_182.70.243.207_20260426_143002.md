# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 14:32:44

---

## SOC分析レポート

### 1. 攻撃の概要と目的

*   **攻撃元IPアドレス**: 182.70.243.207
*   **攻撃日時**: 2026年04月26日 01:17:32Z から 01:34:44Z にかけて継続的に観測
*   **対象プロトコル**: SSH (Secure Shell)
*   **攻撃の概要**:
    攻撃元IPアドレス 182.70.243.207 から、複数回にわたるSSHブルートフォース攻撃が試行されました。最初のログイン試行は失敗しましたが、その後、異なるパスワードを使用して`root`ユーザーでのログインに複数回成功しています。ログイン成功後、攻撃者はシステムへの永続的なアクセスを確立するために、自身のSSH公開鍵を`.ssh/authorized_keys`ファイルに追加しようとしました。この活動は自動化された攻撃スクリプトによって実行されている可能性が高いです。

*   **攻撃の目的**:
    1.  **不正なリモートアクセス**: SSHブルートフォース攻撃により、対象システムへの不正なリモートアクセス権限を獲得する。
    2.  **永続化 (Persistence)**: ログイン成功後、公開鍵認証によるバックドアを設置することで、パスワード変更などの対策後もシステムへのアクセスを維持する経路を確保する。
    3.  **さらなる悪意のある活動の準備**: 確立されたアクセスを利用して、情報窃取、マルウェアの展開、他のシステムへの横展開、システムの破壊など、様々な悪意のある活動の足場を築く。

### 2. 推測される手法・使用ツール

*   **ブルートフォース攻撃**:
    *   `steam`, `root`, `tunnel`, `cloud`, `gitlab`, `345gs5662d34` など複数のユーザー名と、多種多様なパスワード (`steamsteamsteam`, `QAZwsx`, `123456`, `123`, `gitlab@2025`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#`, `3245gs5662d34`) を短時間のうちに継続的に試行しています。これは、HydraやMedusaといった自動化されたブルートフォースツール、またはカスタムスクリプトが使用されていることを強く示唆しています。
*   **永続化メカニズム (バックドア設置)**:
    *   ログイン成功後、以下のコマンドが実行されています。
        `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
    *   このコマンドは、既存の`.ssh`ディレクトリを削除し、再作成した上で、攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を`authorized_keys`に追加するものです。これにより、攻撃者はパスワードなしでSSH公開鍵認証を通じて再接続できるようになり、永続的なアクセスが確保されます。公開鍵のコメント `mdrfckr` は攻撃者の識別子の一つとなり得ます。
*   **ファイル属性変更試行**:
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh` というコマンドがログイン後に複数回実行されています。`chattr -ia .ssh`はLinuxのファイルシステム拡張属性（immutable attribute, append-only attributeなど）を解除しようとするもので、`.ssh`ディレクトリの内容を改変可能にすることを目的としています。`lockr`は一般的なLinuxコマンドではないため`failed`となっていますが、これも同様にファイル属性のロック解除を試みたものと推測されます。

### 3. 脅威レベルとその理由

*   **脅威レベル: 重大 (Critical)**

*   **理由**:
    *   **不正ログインの成功**: 提供されたログでは、攻撃者が`root`ユーザーとして複数回ログインに成功しています。これが実際のシステムであった場合、攻撃者はシステムの最高権限である`root`権限を掌握したことになり、システム上のあらゆる操作（設定変更、データアクセス、マルウェア導入、アカウント作成など）が可能となります。
    *   **永続的なアクセス経路の確立試行**: ログイン成功後、攻撃者は自身のSSH公開鍵をターゲットシステムの`authorized_keys`に追加しようとしました。これは、例えパスワードが変更されたとしても、攻撃者が秘密鍵を持っていればいつでもシステムに再侵入できるバックドアを設置する試みであり、長期的なリスクをもたらします。
    *   **ブルートフォース攻撃の継続性**: 継続的なブルートフォース攻撃は、辞書攻撃や既知の脆弱なパスワードリストを用いた自動化された攻撃であり、広く一般的なインターネットからの攻撃を示唆しています。
    *   **潜在的な影響の甚大さ**: 攻撃者が`root`権限でシステムにアクセスし、永続化に成功した場合、データの窃取、システムの破壊、他の内部システムへの横展開、サービス停止、ランサムウェア感染など、組織にとって壊滅的な被害が発生する可能性が非常に高いです。

### 4. 推奨アクション

#### 緊急対応 (Immediate Actions):

1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `182.70.243.207` からのSSH接続を、ファイアウォール、IDS/IPS、またはセキュリティグループで即座にブロックしてください。
2.  **SSHサービスの設定強化**:
    *   **パスワード認証の無効化**: SSHデーモン (`sshd_config`) において `PasswordAuthentication no` を設定し、公開鍵認証のみに限定してください。
    *   **rootユーザーのSSH直接ログイン禁止**: `PermitRootLogin no` を設定し、`root`ユーザーによる直接ログインを禁止し、必要に応じて一般ユーザーでログイン後`su`または`sudo`を使用するように強制してください。
    *   **強力なパスワードへのリセット**: ログに記録されたログイン成功パスワード（`QAZwsx`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#`, `3245gs5662d34`）が実際に使用されているアカウント（特に`root`）について、直ちに強力で固有なパスワードにリセットしてください。
    *   **多要素認証 (MFA) の導入**: 可能な限りSSHログインにMFAを導入し、認証の強度を高めてください。
    *   **Fail2Banなどの導入**: ブルートフォース攻撃を自動的に検知・ブロックするツール（Fail2Banなど）を導入し、不正なログイン試行を抑制してください。
3.  **SSH公開鍵のレビューと削除**:
    *   全てのユーザー（特に`root`）の`~/.ssh/authorized_keys`ファイルを緊急に確認し、ログに記載された攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) や、その他の不審な公開鍵が存在しないことを確認し、発見された場合は直ちに削除してください。

#### フォレンジック調査 (Forensic Investigation):

1.  **影響範囲の特定**:
    *   システムログ (`/var/log/auth.log`, `/var/log/secure`など) やSSHデーモンのログを詳細に調査し、攻撃元IPからの他のログイン試行や成功、不正なコマンド実行の痕跡がないか確認してください。
    *   不審なプロセス、ネットワーク接続、ファイル改変、新規作成されたユーザーアカウントの有無などを調査し、システムへのさらなる侵害がないかを確認してください。
2.  **他のシステムへの影響確認**: ネットワーク内の他のシステム（特にSSH公開鍵認証を使用しているシステム）に対しても、同様の侵害がないか、または攻撃の横展開が行われていないかを確認してください。

#### 長期的な対策 (Long-term Measures):

1.  **定期的な脆弱性診断とペネトレーションテスト**: システムのセキュリティホールを特定し、修正するために定期的な診断とテストを実施してください。
2.  **セキュリティ意識向上トレーニング**: 従業員に対し、強力なパスワードの使用、フィッシング攻撃への警戒、不審な活動の報告など、セキュリティ意識向上トレーニングを継続的に実施してください。
3.  **ログ監視体制の強化**: ログ収集・分析システム (SIEM: Security Information and Event Management) を導入し、SSHログイン試行、異常なコマンド実行、ファイル改変などをリアルタイムで監視・アラートを生成する体制を構築してください。
4.  **システムのパッチ適用**: OSやSSHサーバーソフトウェアを含む全てのシステムコンポーネントを最新の状態に保ち、既知の脆弱性を悪用されないように定期的にパッチを適用してください。
5.  **アクセス制御の最小権限の原則**: 各ユーザーやサービスが必要最小限の権限のみを持つように、アクセス制御を見直し、不要なアカウントは削除してください。
6.  **ネットワークセグメンテーション**: SSHポートへのアクセスを信頼できるIPアドレス範囲に限定し、インターネットからの直接アクセスを避けるためのネットワークセグメンテーションを検討してください。

このレポートは提供されたログに基づいています。実際のシステムでは、より広範な影響や追加の侵害がある可能性があります。上記の推奨事項を速やかに実行し、セキュリティ態勢を強化することが極めて重要です。