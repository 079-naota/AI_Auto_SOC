# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 08:31:51

---

## SOCアナリストレポート

### 攻撃ログ分析レポート

**日付**: 2026年04月26日
**分析者**: 優秀なSOCアナリスト
**対象ログ**: Cowrie Honeypotログ

---

### 1. 攻撃の概要と目的

攻撃元IP `182.70.243.207` から、SSHサービスを標的とした複数回の認証試行およびログイン後の不正な活動が検出されました。

攻撃者は主に以下の目的を達成しようとしています。

1.  **初期アクセス (Initial Access)**: SSHサービスに対するブルートフォース（辞書攻撃）により、有効な認証情報（特に `root` ユーザーのパスワード）を入手すること。
2.  **永続化 (Persistence)**: ログイン成功後、対象システムの `root` ユーザーの `.ssh/authorized_keys` ファイルに自身の公開鍵を登録することで、パスワードなしで将来的にアクセスできるバックドアを設置すること。これにより、認証情報を失っても継続的にシステムにアクセス可能となる永続的な経路を確保しようとしています。

この攻撃は、ターゲットシステムへの不正侵入と、その後の長期的な制御を確立することを明確に意図しています。

### 2. 推測される手法・使用ツール

この攻撃は、自動化されたツールまたはスクリプトによって実行されている可能性が高いです。

*   **ブルートフォース/辞書攻撃**:
    *   複数のユーザー名（`steam`, `tunnel`, `cloud`, `gitlab`, `root`）とパスワードの組み合わせを短い間隔で大量に試行しています。
    *   特に `root` ユーザーに対して、`QAZwsx`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#` などの様々なパスワードを試行し、複数回成功させています。
    *   これらのパスワードは、一般的によく使われる弱いパスワードや、辞書攻撃で用いられるリストに含まれる可能性のあるものです。

*   **永続化の試み（バックドア設置）**:
    *   `root` ユーザーでのログイン成功後、以下のコマンド群を繰り返し実行しています。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリの属性（immutable/append-onlyなど）を解除しようとする試みです。`lockr` コマンドは一般的なLinuxシステムには存在しないため、Honeypotでは失敗しています。これは、`.ssh` ディレクトリへの書き込みを阻害する保護メカニズムを無効化しようとしていることを示します。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`:
            *   既存の `.ssh` ディレクトリを削除し、再作成。
            *   自身の公開鍵 `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` を `~/.ssh/authorized_keys` に追記。この公開鍵のコメントは `mdrfckr` となっており、攻撃者の悪意を示すものです。
            *   `.ssh` ディレクトリのパーミッションを適切に設定し、公開鍵認証が機能するようにしています。

*   **再接続試行**: 公開鍵の設置後、攻撃者はすぐさま追加した公開鍵でのSSH接続を試みていると推測されますが、Honeypotであるためパスワード認証の失敗または別のパスワード認証の成功として記録されているようです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:

*   **root権限の奪取試行**: Honeypot上ではありますが、攻撃者が `root` ユーザーとしてログインに成功している点が最も深刻です。実際のシステムでこれが成功した場合、システム全体が完全に制御され、データの窃取、破壊、マルウェアの配布、他のシステムへの足がかりなどに利用される可能性があります。
*   **永続化の明確な意図**: ログイン成功後に公開鍵を `authorized_keys` に追加しようとする行動は、システムへの継続的なアクセス経路を確保するための明確な試みであり、非常に悪質です。これは、単なる情報収集目的ではなく、長期的な侵入を計画していることを示唆します。
*   **自動化された攻撃**: 試行の頻度とパターンから、この攻撃が自動化されたスクリプトやボットネットの一部である可能性が高いです。これは、特定のターゲットを狙ったものではなく、インターネット上の脆弱なSSHサーバーを無差別にスキャンし、攻撃していることを意味します。
*   **公開鍵の存在**: 使用された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) は、特定の攻撃キャンペーンやマルウェアに関連付けられている可能性があります。コメント `mdrfckr` も攻撃者の意図を示す可能性があります。

### 4. 推奨アクション

この攻撃ログはHoneypotからのものであるため、直接的なシステム侵害は発生していませんが、実際のシステムであれば重大なセキュリティインシデントに発展していた可能性があります。以下の推奨アクションを実施し、セキュリティ体制を強化してください。

1.  **攻撃元IPのブロック**:
    *   攻撃元IPアドレス `182.70.243.207` からのすべての通信を、ファイアウォールやIPS/IDSで即座にブロックリストに追加してください。

2.  **SSHサーバーのセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能であれば、SSHパスワード認証を無効にし、公開鍵認証のみに限定してください。これにより、ブルートフォース攻撃のリスクを大幅に低減できます。
    *   **`root` ユーザーの直接ログイン禁止**: `PermitRootLogin no` をSSH設定 (`/etc/ssh/sshd_config`) に追加し、`root` ユーザーがSSHで直接ログインできないように設定してください。`root` 権限が必要な場合は、一般ユーザーでログイン後に `su` または `sudo` を使用することを義務付けてください。
    *   **強力なパスワードポリシーの強制**: ユーザーが推測されにくい、複雑なパスワードを設定するよう強制するポリシーを導入し、定期的なパスワード変更を促してください。
    *   **非標準ポートの使用**: SSHポートを標準の22番以外（例: 2222番など）に変更することで、自動化された広範囲なスキャンからのヒット率を下げることができます。ただし、これは主要な防御策ではなく、補助的な対策と認識してください。
    *   **多要素認証 (MFA) の導入**: 可能であれば、SSHログインにMFAを導入し、セキュリティを強化してください。

3.  **侵入検知・防御システムの強化**:
    *   **ブルートフォース対策**: Fail2Banなどのツールを導入し、一定回数以上のログイン失敗を検出した場合に、自動的に攻撃元IPをブロックするように設定してください。
    *   **IDS/IPSの監視強化**: SSHに対する異常なアクセスパターン（短時間での大量ログイン試行、特定のユーザー名への集中攻撃など）を検知・警告できるよう、IDS/IPSのルールを見直してください。
    *   **ファイル整合性監視 (FIM)**: `/root/.ssh/authorized_keys` や `/etc/ssh/sshd_config` など、SSHに関連する重要な設定ファイルや認証ファイルの変更を監視し、不正な変更があれば即座にアラートを発生させる仕組みを導入してください。

4.  **ログ監視とインシデント対応の見直し**:
    *   **リアルタイム監視**: すべてのSSHサーバーの認証ログ (`/var/log/auth.log` または `/var/log/secure`) をリアルタイムで監視し、異常なログイン試行や成功を迅速に検知できる体制を構築してください。
    *   **脅威インテリジェンスの活用**: ログに記録された攻撃元IPアドレスや、`authorized_keys` に挿入されようとした公開鍵の情報が、既知の脅威アクターやマルウェアに関連付けられていないか、脅威インテリジェンスプラットフォームで照合してください。
    *   **インシデントレスポンス計画の更新**: 今回のログで示された攻撃手法（ブルートフォースとバックドア設置）を想定し、既存のインシデントレスポンス計画に抜けがないか確認・更新してください。特に、`root` ユーザーの侵害が疑われる場合の対応フローを明確にしてください。

5.  **定期的な脆弱性診断**:
    *   システム全体の脆弱性スキャンを定期的に実施し、潜在的な弱点を特定・修正してください。

このレポートが、今後のセキュリティ対策の一助となることを期待します。