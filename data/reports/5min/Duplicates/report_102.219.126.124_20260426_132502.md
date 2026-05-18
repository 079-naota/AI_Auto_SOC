# SOC自動分析レポート: 102.219.126.124

**生成日時:** 2026-04-26 13:26:44

---

## SOC分析レポート

**件名: SSHサービスに対するブルートフォース攻撃およびバックドア設置試行に関する分析レポート**

### 1. 攻撃の概要と目的

攻撃元IPアドレス `102.219.126.124` から、SSHサービスに対して継続的な認証試行（ブルートフォース/辞書攻撃）が行われました。複数の異なるパスワードを用いて `root` ユーザーでのログインに成功した後、永続的なアクセス経路を確立するために攻撃者のSSH公開鍵をターゲットシステムの `~/.ssh/authorized_keys` ファイルに書き込む試行が確認されました。

**攻撃の主な目的:**
*   特権ユーザー（root）の認証情報を特定し、システムへの不正アクセスを確立する。
*   認証突破後、SSH公開鍵認証による永続的なバックドアを設置し、将来的にパスワードなしでシステムに再接続できるようにする。

### 2. 推測される手法・使用ツール

*   **ブルートフォース/辞書攻撃:** 攻撃者は `drcom` や `ubuntu`、`user` といった一般的なユーザー名、そして特に `root` ユーザーに対して、複数のパスワード（例: `1qaz@WSX3edc$RFV!@`, `ali123456`, `Root8`, `Aa112211.`, `Config123`, `Aa123321` など）を試行しています。このことから、自動化された辞書攻撃やブルートフォース攻撃ツールが使用されていると考えられます。
*   **自動化された攻撃スクリプト/ボット:** 連続的なログイン試行、ログイン成功後の定型的なコマンド実行（`chattr` 属性変更試行、`.ssh` ディレクトリの再作成と `authorized_keys` への公開鍵追加、`chmod` による権限設定）、およびその後の特定ユーザー (`345gs5662d34`) での再接続試行の繰り返しから、攻撃は手動ではなく、自動化されたスクリプトやボットによって実行されている可能性が高いです。
*   **永続化メカニズム（SSH公開鍵バックドア）:** ログイン成功後、攻撃者は以下のコマンドを実行し、自身の公開鍵を `~/.ssh/authorized_keys` に追加して永続的なアクセス経路を確保しようとしました。
    ```bash
    cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~
    ```
    この公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）は、セキュリティコミュニティで広く知られている、Miraiボットネットなどのマルウェアや他の自動化された攻撃ツールで利用される不正なSSH公開鍵です。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**
*   **認証突破の成功:** 攻撃者はSSHサービスに対するブルートフォース攻撃により、特権ユーザーである `root` の認証情報を複数回特定することに成功しています。これは、もし本番環境であれば、システムへの完全なアクセス権を奪取されたことを意味します。
*   **永続化の試行:** ログイン後、攻撃者は自身のSSH公開鍵を `authorized_keys` に追加することで、パスワードなしで永続的にアクセスできるバックドアを設置しようとしました。この手法は、システムへの持続的な侵害を可能にし、検出を困難にします。
*   **既知の悪性公開鍵の使用:** 使用された公開鍵がMiraiボットネットに関連する既知の不正な鍵であることから、攻撃者は広範なボットネット活動の一部である可能性があり、ターゲットシステムをマルウェア感染やさらなる攻撃の踏み台にしようとしていたことが推測されます。
*   **広範囲な影響の可能性:** もしこの攻撃がハニーポットではなく実際のサーバーに対して行われていた場合、システムは完全に侵害され、データの窃取、マルウェアの展開、サービス停止、他のシステムへの攻撃の踏み台化など、深刻な被害が発生していたでしょう。

### 4. 推奨アクション

このログはハニーポットのものですが、実際のシステムで同様の攻撃を防御し、被害を防ぐために以下の対応を強く推奨します。

1.  **攻撃元IPアドレスのブロック:**
    *   攻撃元IPアドレス `102.219.126.124` からの接続をファイアウォール、IDS/IPS、またはエッジルーターで直ちにブロックしてください。ただし、攻撃者は常にIPアドレスを変更する可能性があるため、これは一時的な対策に過ぎません。
2.  **SSHセキュリティ設定の強化:**
    *   **rootログインの無効化:** SSHによる `root` ユーザーの直接ログインを無効にし、一般ユーザーでログイン後、`sudo` を利用して特権操作を行う運用を徹底してください。
    *   **パスワード認証の制限と鍵認証の必須化:** 可能な限りパスワード認証を無効化し、堅牢なSSH鍵認証のみを許可する設定にしてください。
    *   **強力なパスワードポリシーの適用:** パスワード認証を許可する場合、辞書攻撃やブルートフォース攻撃に耐えうる複雑性、長さ、有効期限を持つパスワードポリシーを適用してください。
    *   **SSHポートの変更:** 標準ポート（22番）から非標準ポートに変更することを検討してください。これにより、自動化された広範囲なスキャンからのヒット率を下げることができます。
    *   **`authorized_keys` ファイルの権限と内容の定期的な確認:** 不正なSSH公開鍵が追加されていないか、定期的に確認する仕組みを導入してください。
3.  **既存システムでのアカウント棚卸しとパスワード変更:**
    *   もしハニーポットのログイン成功パスワードが、他のシステムで利用されている場合は、直ちに該当する全てのアカウントのパスワードを変更してください。
    *   システム内の全てのアカウントについて、不要なアカウントの削除、パスワードの強度確認、多要素認証（MFA）の導入を検討してください。
4.  **脅威インテリジェンスの活用と監視強化:**
    *   今回検出された不正なSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を既知の悪性インジケーターとして登録し、SIEMやIDS/IPSで監視・検出ができるように設定してください。
    *   SSHログインログをSIEM等の集中ログ管理システムに集約し、ブルートフォース試行、異常なログインパターン、不明なIPアドレスからの接続、特権ユーザーの不審なアクティビティをリアルタイムで検知・アラートする仕組みを導入してください。
5.  **定期的なセキュリティ監査と脆弱性診断:**
    *   SSHサービスを含む、公開されているシステムに対して定期的な脆弱性診断とペネトレーションテストを実施し、潜在的な脆弱性を特定し修正してください。

以上