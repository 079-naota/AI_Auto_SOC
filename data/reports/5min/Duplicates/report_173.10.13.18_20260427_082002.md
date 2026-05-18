# SOC自動分析レポート: 173.10.13.18

**生成日時:** 2026-04-27 08:21:44

---

優秀なSOCアナリストとして、提示された攻撃ログを分析し、以下のレポートを作成します。

---

### セキュリティインシデント分析レポート

**報告日時**: 2026-04-27TXX:XX:XXZ (分析完了時点)
**攻撃元IPアドレス**: 173.10.13.18
**ターゲット**: Cowrieハニーポット（SSHサービス）

---

#### 1. 攻撃の概要と目的

攻撃元IPアドレス `173.10.13.18` から、SSHサービスに対して執拗なブルートフォース攻撃が行われ、複数回 `root` ユーザーでのログインに成功しています。ログイン成功後、攻撃者は永続的なアクセスを確立するために、自身のSSH公開鍵を `authorized_keys` ファイルに登録しようと試みています。

この攻撃の主な目的は、標的システムへの不正アクセスを確立し、将来的にパスワードなしで再アクセスできるバックドアを仕込むことにあると推測されます。

---

#### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース攻撃（Brute-force Attack）**: 攻撃者はSSHサービスに対して、辞書に含まれる可能性のある複数のパスワード（例: `dev`, `trans`, `123456Aa`, `Aa000000`, `Sp0rt`, `123456789a@`, `qaz123!@#`, `Aa12488261`など）を `root` ユーザー名で繰り返し試行しています。
    *   **永続化（Persistence）**: ログインに成功した後、攻撃者はシステムへの永続的なアクセス経路を確立しようとしています。具体的には、以下のコマンドを実行し、自身のSSH公開鍵を `~/.ssh/authorized_keys` ファイルに追加することで、パスワード認証を必要としない鍵認証でのログインを可能にしようとしています。
        ```bash
        cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~
        ```
    *   **防御回避（Defense Evasion）**: `cd ~; chattr -ia .ssh; lockr -ia .ssh` のコマンド入力から、攻撃者は `.ssh` ディレクトリの属性変更（immutable属性解除など）を試み、その後の公開鍵登録を確実に実行しようとしている可能性があります。（`lockr`コマンドは一般的に存在しないため、タイプミスか特定の環境に依存するコマンドの試行と見られます。）

*   **使用ツール**:
    *   上記のブルートフォース攻撃とコマンド実行パターンから、Hydra、Medusa、NmapのSSHスクリプト、またはカスタムスクリプトなど、自動化された攻撃ツールが使用されている可能性が高いです。
    *   公開鍵のコメントが `mdrfckr` となっていることから、特定のボットネット（例: Miraiの亜種など）の一部である可能性も考慮されます。

---

#### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
1.  **認証突破の成功**: 攻撃者は `root` ユーザーとしてターゲットシステムへのログインに複数回成功しています。これは実環境であれば、システムの完全な乗っ取りにつながる非常に深刻な事態です。
2.  **永続化の試み**: ログイン成功後、攻撃者はバックドアとして機能するSSH公開鍵の登録を試みています。これにより、一度アクセスを確立すれば、パスワード変更などの対策が取られても、登録した公開鍵で継続的にアクセスされるリスクが発生します。
3.  **攻撃の自動化**: 攻撃元IPからの連続的なログイン試行と、ログイン成功後の定型的なコマンド実行から、この攻撃が自動化されたスクリプトやボットによって行われている可能性が高いと判断されます。これは、広範囲のシステムを標的とした無差別攻撃の一部である可能性を示唆しており、他のシステムも同様の脆弱性に晒されている可能性があります。

ハニーポットであるため実際のシステムへの被害は発生していませんが、このログは実環境で発生した場合の重大なインシデントを示唆しています。

---

#### 4. 推奨アクション

**緊急対応（Immediate Actions）**:

1.  **攻撃元IPアドレスのブロック**: 攻撃元IPアドレス `173.10.13.18` を、ファイアウォール、IDS/IPS、またはWAFで直ちにブロックリストに追加し、今後の接続を拒否します。
2.  **SSHパスワードの強制変更**: もし類似のパスワード（`123456Aa`, `Aa000000`, `Sp0rt`, `123456789a@`, `qaz123!@#`, `Aa12488261`など）が本番環境の `root` アカウントや他の特権アカウントで使用されている場合、直ちに複雑なものに変更するよう全ユーザーに促します。
3.  **SSH公開鍵の監査**: 全てのSSHサーバーにおいて、`root` ユーザーおよび他の特権ユーザーの `~/.ssh/authorized_keys` ファイルを監査し、不正な公開鍵（特に公開鍵 `mdrfckr`）が存在しないことを確認し、もし発見された場合は直ちに削除します。

**事後対応と予防策（Post-Incident & Preventive Measures）**:

1.  **SSH設定の強化**:
    *   `PermitRootLogin no`: SSH経由での `root` ユーザーの直接ログインを禁止します。sudoを使用してアクセスするようにします。
    *   `PasswordAuthentication no`: パスワード認証を無効化し、鍵認証のみに限定します。
    *   より強力なパスワードポリシーの徹底、多要素認証（MFA）の導入を検討します。
    *   SSHポートを標準の22番以外に変更する「ポートノッキング」や「ポートステルス」も検討しますが、根本的な対策ではありません。
2.  **ログ監視の強化**: SSHログイン失敗ログや、認証成功後の異常なコマンド実行に対するアラート設定を強化します。
3.  **脅威インテリジェンスの活用**: 攻撃に使用されたIPアドレス (`173.10.13.18`) およびSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を社内の脅威インテリジェンスデータベースに登録し、他システムでの検知に活用します。
4.  **ハニーポットの活用**: Cowrieのようなハニーポットをデプロイし続けることで、新たな攻撃手法や攻撃者の活動パターンを継続的に監視・分析し、防御策にフィードバックします。

---