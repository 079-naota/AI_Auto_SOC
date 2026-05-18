# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 13:57:35

---

## SOCアナリストレポート

### 攻撃ログ分析レポート

**報告日時**: 2026-04-26T02:00:00Z
**攻撃元IP**: 182.70.243.207
**監視対象**: SSHハニーポット（Cowrie）

---

### 1. 攻撃の概要と目的

攻撃者はIPアドレス `182.70.243.207` から、約17分間（2026-04-26T01:17:32Zから01:34:44Z）にわたり、SSHサービスに対する組織的な攻撃を実施しました。この攻撃は、主にSSHブルートフォース攻撃と、それに続くシステムへの永続的なアクセス経路の確立（バックドア設置）を目的としています。

具体的には、最初に一般的なユーザー名（`steam`など）でログインを試行した後、集中的に`root`アカウントを標的としたブルートフォース攻撃を行っています。ハニーポットが複数の`root`アカウントに対するパスワード認証に成功したと記録した後、攻撃者は`~/.ssh/authorized_keys`ファイルに自身の公開鍵を登録しようと試み、パスワードなしでの再アクセスを企図しました。公開鍵設置後には、その鍵が有効であることを確認するようなログイン試行も繰り返し観測されています。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSH ブルートフォース攻撃/パスワードスプレー攻撃**: 辞書攻撃やパスワードリスト攻撃によって、`root`ユーザーを含む複数の一般的なユーザー名や推測しやすいユーザー名（`steam`, `tunnel`, `cloud`, `gitlab`）に対して、様々なパスワードを試行しています。
    *   **永続化 (Persistence)**: ログイン成功後、攻撃者は以下のコマンドを実行し、将来にわたるシステムへの不正なアクセス経路を確立しようとしました。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
            *   このコマンドは、既存のSSH公開鍵を削除し、攻撃者自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を`~/.ssh/authorized_keys`に追加することで、バックドアを設置するものです。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`というコマンドも試行されていますが、Cowrieのログでは失敗していることが示されており、標準的なLinuxコマンドではないか、意図したオプションではないため実行に失敗している可能性が高いです。意図としては`.ssh`ディレクトリの属性変更やロック解除を試みたものと推測されます。
*   **使用ツール**:
    *   短時間での多数のログイン試行と、ログイン後の定型的なコマンド実行パターンから、`Hydra`や`Medusa`といった自動化されたブルートフォースツール、または攻撃者が作成したカスタムスクリプトが使用されている可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
*   **明確な悪意ある意図**: 攻撃は単なる偵察や偶発的なものではなく、`root`権限の奪取と永続的なバックドアの確立という明確な目的を持って実行されています。これは、もし実際のシステムで成功していた場合、深刻なシステム侵害に繋がる行為です。
*   **`root`アカウントへの集中攻撃**: 最高の権限を持つ`root`アカウントを直接狙っており、その認証情報を複数回突破したとログは示しています。これにより、システムが完全に制御される危険性があります。
*   **永続化の試み**: 公開鍵の設置は、攻撃者が一度侵入した後も、パスワード変更などの対策によってアクセスが遮断されることなく、継続的にシステムにアクセスしようとする意図を示しています。これは検出を困難にし、長期的なリスクをもたらします。
*   **自動化された攻撃**: 攻撃が自動化されているため、システムが脆弱な場合、迅速に悪用される可能性があります。

### 4. 推奨アクション

1.  **攻撃元IPアドレスの即時ブロック**:
    *   ファイアウォール、IDS/IPS、またはルーターのACLに `182.70.243.207` を追加し、すべての通信をブロックします。
2.  **SSHパスワードポリシーの強化**:
    *   システム内のすべてのユーザーアカウント、特に`root`アカウントや管理者権限を持つアカウントについて、複雑で長いパスワードの使用を義務付けます。
    *   定期的なパスワード変更を強制します。
3.  **SSHサービス設定の最適化**:
    *   `PermitRootLogin no` を設定し、`root`ユーザーによるSSH直接ログインを禁止します。一般ユーザーでログイン後、`sudo`を使用して特権操作を行うようにします。
    *   可能であれば、パスワード認証を無効化し、証明書ベースの認証（公開鍵認証）と多要素認証（MFA）の組み合わせを必須とします。
    *   SSHサービスがデフォルトポート (22/TCP) 以外で稼働しているか確認し、必要に応じて変更を検討します。
4.  **侵入検知・防止システムの強化**:
    *   `Fail2Ban`のようなツールを導入または設定強化し、一定回数以上のSSHログイン失敗があったIPアドレスを自動的にブロックするようにします。
    *   IDS/IPSのシグネチャを更新し、SSHブルートフォース攻撃や不審なコマンド実行（特に`.ssh`ディレクトリへの変更）を検知・防御できるようにします。
5.  **既知の悪意ある公開鍵の監視**:
    *   今回の攻撃で使用された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) がシステム内の`authorized_keys`ファイルに存在しないことを定期的にスキャン・確認する仕組みを導入します。
6.  **ログ監視とアラートの強化**:
    *   SSHログイン成功イベント、特に`root`アカウントへのログイン成功時には、セキュリティチームに即座にアラートが通知されるようにログ監視システムを設定します。
    *   `/var/log/auth.log` (または同等の認証ログ) の不正アクセス試行、特に繰り返されるログイン失敗を監視し、異常なパターンを検知します。
    *   `.ssh`ディレクトリへの変更や、`authorized_keys`ファイルへの書き込み試行を監視する監査ルールを設定します。

本レポートはハニーポットのログに基づいています。実際のプロダクション環境では、上記の推奨事項を速やかに実施し、同様の攻撃からシステムを保護することが不可欠です。