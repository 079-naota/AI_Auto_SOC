# SOC自動分析レポート: 210.79.191.205

**生成日時:** 2026-04-26 17:23:56

---

## SOC分析レポート

### 攻撃概要

*   **報告日**: 2026年04月26日
*   **攻撃元IP**: 210.79.191.205
*   **観測されたシステム**: SSHハニーポット (Cowrie)
*   **攻撃の種類**: SSHブルートフォース/辞書攻撃、それに続く認証情報の永続化試行

本ログはSSHハニーポットであるCowrieによって記録されたものであり、実際のシステムへの直接的な侵害は発生していませんが、攻撃者の意図と手法を明確に示しています。攻撃者は、SSHサービスへの不正なアクセスを試み、複数のパスワードを試行してログインに成功したと認識した後、自身のSSH公開鍵をターゲットシステムの `authorized_keys` ファイルに追加することで、永続的なアクセス経路を確立しようとしています。

### 1. 攻撃の概要と目的

攻撃元IP `210.79.191.205` から、SSHサービスに対して執拗なログイン試行が行われています。ログによれば、攻撃者は `root` ユーザーに対して複数のパスワード（例: `100202500`, `ghost123`, `Qazwsx12345678..`, `123456-qwe`, `123Qwert`, `changeme1`）でログインに成功したと認識しています。

ログイン成功後、攻撃者は以下のコマンドを複数回にわたり実行しています。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリの属性を変更し、書き込みを可能にしようとしています。`chattr -ia` は不可変属性や追加のみ属性を削除する意図と推測されます。`lockr` は不明なコマンドですが、ファイルシステム操作を試みていることが伺えます。
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`:
    *   既存の `.ssh` ディレクトリを削除し、再作成します。
    *   特定のSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を `~/.ssh/authorized_keys` ファイルに書き込みます。この公開鍵は、攻撃者がパスワードなしでSSHアクセスを継続するためのバックドアとして機能します。
    *   `.ssh` ディレクトリとファイルのパーミッションを `chmod -R go=` で設定し、SSHのセキュリティ要件に合致させようとしています。

攻撃の主な目的は、SSH経由で不正にシステムに侵入し、その後の永続的なアクセス経路（バックドア）を確立することにあると推測されます。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース/辞書攻撃**: `root`、`git`、`ubuntu` といった一般的なユーザー名に対し、辞書攻撃でよく用いられるような複数のパスワードを試行しています。特に `root` ユーザーに対する試行と成功認識が顕著です。
    *   **認証情報の永続化**: ログイン成功後、速やかにSSH公開鍵を `authorized_keys` ファイルに追加しようとする明確な意図が見られます。これは、一度侵入に成功すれば、パスワードが変更されても攻撃者がアクセスを継続するための常套手段です。
*   **使用ツール**:
    *   **自動化ツール**: 複数回のログイン試行と、それに続く一連のコマンド実行が非常に短時間でかつ定型的に行われていることから、Hydra、Medusa、NmapのNSEスクリプト、またはカスタムスクリプトのような自動化されたSSHブルートフォースツールが使用されている可能性が高いです。ログイン成功後のコマンドシーケンスが複数回全く同じであることから、ペイロード実行機能を持つツールと推測されます。

### 3. 脅威レベルとその理由

*   **脅威レベル**: **高 (High)**

*   **理由**:
    *   **rootログインの成功認識**: ログ上では `root` ユーザーでのログインが複数回成功したと認識されており、これはハニーポットの挙動ですが、もしこれが実際のシステムであれば、攻撃者はシステムの最高権限を掌握したことになります。
    *   **永続化の明確な試み**: 攻撃者はログイン後、自身のSSH公開鍵を `authorized_keys` に追加しようと明確に試みています。これは、一度侵入が成功すれば、検出されにくい永続的なバックドアを設置し、パスワード変更後もアクセスを継続する目的があるため、非常に悪質性が高いです。
    *   **自動化された攻撃**: 人手によるものとは異なり、自動化されたツールによる攻撃は、より広範な標的を効率的に狙い、多くのシステムに被害をもたらす可能性を秘めています。これは特定の標的への執着よりも、脆弱なシステムを探索するボットネットの一部である可能性を示唆します。
    *   **一般的なパスワードの悪用**: ログインに成功したと認識されたパスワードは、辞書攻撃でよく使われる類のものであり、多くのシステムがこの種の攻撃に対して脆弱である可能性を示しています。

### 4. 推奨アクション

1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `210.79.191.205` からのアクセスを、ファイアウォールやIDS/IPSで即座にブロックリストに追加し、今後の通信を遮断してください。
2.  **SSH認証の強化**:
    *   **パスワード認証の無効化**: 可能な限りSSHのパスワード認証を無効にし、より安全な公開鍵認証のみを許可してください。
    *   **多要素認証 (MFA) の導入**: SSHログインに多要素認証を導入し、認証プロセスを強化してください。
    *   **複雑なパスワードポリシー**: パスワード認証を使用する場合は、推測されにくい複雑なパスワードを強制し、定期的な変更を促すポリシーを徹底してください。
    *   **rootログインの禁止**: SSH経由での `root` ユーザーによる直接ログインを禁止し、一般ユーザーでログイン後に `sudo` や `su -` を利用するように設定してください。
3.  **ログイン試行のレートリミット/ロックアウト**: SSHサービスに対し、`fail2ban` のようなツールを導入し、連続したログイン失敗を検知した場合に、一定期間アクセスを自動的にブロックする設定を適用してください。
4.  **SSH鍵管理の厳格化**:
    *   `~/.ssh` ディレクトリおよび `authorized_keys` ファイルのパーミッション設定が適切であるか（通常はオーナーのみ書き込み可）を確認してください。
    *   不審な公開鍵が登録されていないか、既存のシステム上の `authorized_keys` ファイルを定期的に監査してください。ログに記録された攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) がシステムに存在しないことを確認し、もしあれば即座に削除してください。
5.  **ログ監視の強化**: SSH認証ログ、システムログ、およびその他関連するセキュリティログを継続的に監視し、不審なログイン試行、ログイン成功、異常なファイル操作（特に `~/.ssh` ディレクトリ関連）がないかを確認するアラートを設定してください。
6.  **脆弱性スキャンの実施**: 定期的にシステムに対する脆弱性スキャンを実施し、SSHサービス設定の不備や、脆弱な認証情報（デフォルトパスワードや推測されやすいパスワード）がないかを確認してください。
7.  **脅威インテリジェンスとの照合**: ログに記録された攻撃元IPアドレスやSSH公開鍵を脅威インテリジェンスフィードと照合し、既知の攻撃キャンペーンやマルウェアに関連しているか調査してください。