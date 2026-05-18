# SOC自動分析レポート: 132.145.213.106

**生成日時:** 2026-05-01 08:56:40

---

## SOCアナリストレポート

### 攻撃ログ分析レポート

**報告日時**: 2026-05-01 (分析時点)
**攻撃元IPアドレス**: 132.145.213.106
**対象システム**: SSHサービス (Cowrieハニーポットによる観測)

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `132.145.213.106` から、SSHサービスに対して一連の不正アクセス試行が観測されました。これは約23分間にわたり行われ、複数のユーザー名とパスワードの組み合わせを試行する、典型的なブルートフォース攻撃/辞書攻撃のパターンを示しています。

攻撃の主な目的は以下の2点と推測されます。

1.  **システムへの不正ログイン**: SSH認証情報を突破し、対象システムに管理者権限（root）を含む不正なアクセスを確立すること。
2.  **永続的なアクセス経路の確立**: ログイン成功後、自身のSSH公開鍵をターゲットシステムの `authorized_keys` に追加することで、パスワードなしでいつでも再接続できるバックドアを設置し、永続的なアクセス経路を確保すること。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース攻撃 / 辞書攻撃**: ログには、`user`, `deployer`, `test`, `student`, `newuser`, `debian`, `odoo`, `testuser`, `teamspeak3`, `kafka`, `ubuntu`, `ftpuser`, `admin_user`, `minecraft` など、多数の一般的なユーザー名やデフォルトユーザー名、およびそれに紐づく様々なパスワードを試行している記録があります。これは自動化されたスクリプトやツールによる試行であると強く示唆されます。
    *   **バックドアの設置**: ログイン成功後には、`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~` というコマンドが繰り返し実行されています。これは、攻撃者自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を追加し、以後パスワードなしでログインできるようにするためのものです。

*   **使用ツール**:
    *   SSHクライアント (バージョン情報はログに記載なし)
    *   ブルートフォース/辞書攻撃を実行するための自動化スクリプトまたはツール (例: Hydra, Nmapのssh-bruteスクリプトなど)
    *   標準的なシェルコマンド (`cd`, `rm`, `mkdir`, `echo`, `chmod`)

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:

*   **広範囲なブルートフォース攻撃**: 多数のユーザー名とパスワードの組み合わせを短い期間に集中的に試行していることから、組織のシステムに対して自動化された大規模な攻撃が仕掛けられている可能性が高いです。
*   **管理者権限でのログイン成功**: ログには`root`ユーザーとして複数回ログインに成功したと記録されており、これは攻撃者側が管理者権限でのアクセスを得たものと認識していることを意味します。（ただし、今回はハニーポットへのアクセスであり、実際のシステムへの侵入ではありません。）
*   **永続化の試み**: ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確保するため、自身の公開鍵を `authorized_keys` に追加しようとしました。これは、もし実際のシステムで成功していれば、攻撃者がいつでも任意のタイミングでシステムに再侵入できる状態になっていたことを示します。
*   **試行された認証情報の危険性**: 試行されたパスワードの中には、`oracle7`, `admin3344`, `admin@123$%^` など、推測されやすい、または一般的なデフォルトパスワードによく似たものが含まれています。これらの情報が実際の環境で利用されている場合、深刻な脆弱性となり得ます。

以上の理由から、この攻撃は非常に危険であり、もしハニーポットでなければ、対象システムは完全に攻撃者に掌握されていた可能性が高いと判断します。

### 4. 推奨アクション

以下の対策を早急に実施し、セキュリティ体制を強化することを強く推奨します。

1.  **攻撃元IPアドレスのブロック**:
    *   攻撃元IPアドレス `132.145.213.106` を企業のファイアウォール、IDS/IPS、またはWAFで恒久的にブロックし、今後のアクセスを完全に遮断してください。
2.  **SSHブルートフォース対策の強化**:
    *   **IPアドレス制限**: SSHサービスへのアクセスを、信頼できる特定のIPアドレス範囲に限定するようファイアウォールルールを見直してください。
    *   **Fail2Banなどの導入**: 認証失敗回数に基づいて一定期間IPアドレスをブロックするツール（例: Fail2Ban）を導入し、設定を最適化してください。
    *   **パスワード認証の無効化**: 可能であれば、SSHパスワード認証を無効化し、より安全な公開鍵認証のみを許可する設定に変更してください。
    *   **多要素認証 (MFA) の導入**: SSHログインに多要素認証を導入し、セキュリティレベルを向上させてください。
    *   **ポート変更**: SSHサービスのデフォルトポート（22/TCP）を一般的なポートではないものに変更することも検討してください（ただし、これは攻撃を完全に防ぐものではなく、あくまでノイズを減らす効果にとどまります）。
3.  **アカウントの棚卸しとパスワードポリシーの強化**:
    *   ログに記録されたログイン試行情報（成功したパスワード `oracle7`, `3245gs5662d34`, `admin3344`, `admin@123$%^` および失敗したパスワード群）をレビューし、これらの組み合わせが自社のシステムで実際に使用されていないかを確認してください。もし使用されている場合は、即座に該当アカウントのパスワードを変更してください。
    *   全てのシステムアカウントに対して、最低文字数、複雑性（大文字、小文字、数字、記号の組み合わせ）、定期的なパスワード変更を義務付ける強力なパスワードポリシーを適用・強化してください。
    *   `root`アカウントへの直接ログインを禁止する設定（`PermitRootLogin no`）が適用されていることを確認してください。
    *   長期間利用されていない、または不要なアカウントは速やかに削除してください。
4.  **既存システムに対する侵害調査**:
    *   ハニーポットのログは実際のシステムが侵害されたことを直接示すものではありませんが、攻撃者が試行した認証情報や手法は、実際のシステムが標的となる可能性を示唆しています。企業内の全てのSSH公開サーバーに対して、今回のログで使われた認証情報でログインできないか、また不正なSSH公開鍵が設置されていないか（特に`/root/.ssh/authorized_keys`などの標準的な場所）を緊急で監査してください。
    *   特に、試行された公開鍵 `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` が不正に追加されていないかを確認してください。
5.  **セキュリティ監視の強化**:
    *   SSHログインログ（`auth.log`など）の監視を強化し、異常なログイン試行や成功がないか継続的にチェックしてください。
    *   SIEM（Security Information and Event Management）システムを活用し、これらのログを相関分析することで、より迅速に脅威を検知できるようにしてください。

---