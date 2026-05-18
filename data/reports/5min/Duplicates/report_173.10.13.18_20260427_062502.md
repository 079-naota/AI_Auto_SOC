# SOC自動分析レポート: 173.10.13.18

**生成日時:** 2026-04-27 06:26:13

---

## 攻撃ログ分析レポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `173.10.13.18` から、本システム (Cowrieハニーポット) のSSHサービスに対して、執拗なブルートフォース攻撃と、それに続く永続化のためのバックドア設置の試みが行われました。

攻撃者はまず、`dev` や `trans` といった一般的なユーザー名でログインを試み、その後 `root` ユーザーに対する多数のパスワードを試行しました。複数の異なるパスワード (`123456Aa`, `Aa000000`, `Sp0rt`, `123456789a@`, `qaz123!@#`, `Aa12488261`, `3245gs5662d34`) で `root` ユーザーとしてログインに成功しています。

ログイン成功後、攻撃者は以下の目的のために一連のコマンドを実行しました。
*   **目的1: 永続的なアクセス経路の確立**
    *   `root` ユーザーとしてログイン後、`.ssh` ディレクトリ内の既存の `authorized_keys` ファイルを削除または上書きし、自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を追加することで、パスワードなしで将来的にSSH接続できるバックドアを設置しようとしました。

### 2. 推測される手法・使用ツール

*   **SSHブルートフォース攻撃:**
    *   攻撃者は自動化されたツールやスクリプトを使用して、広範なユーザー名とパスワードの組み合わせを試行しました。特に `root` ユーザーへの辞書攻撃や既知の脆弱なパスワードリストを用いた試行が見られます。
*   **永続化メカニズム（SSHキーベースのバックドア）:**
    *   ログイン成功後、攻撃者は以下のコマンドを実行し、自身の公開鍵を `root` ユーザーの `authorized_keys` に追加してSSHキー認証による永続的なアクセスを確保しようとしました。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリの属性を変更し、書き込み可能にしようとしています。`lockr` は標準的なコマンドではありませんが、`chattr` と同様の目的（ファイル保護の解除）を意図していると推測されます。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: これは、既存の`.ssh`ディレクトリを削除し、新しいディレクトリを作成した上で、攻撃者の公開鍵を`authorized_keys`に書き込み、適切なパーミッションを設定する一連の典型的なバックドア設置コマンドです。
*   **自動化された攻撃スクリプト/ボットネット:**
    *   攻撃が短時間で繰り返され、一連のログイン試行とコマンド実行が自動的に行われていることから、攻撃者は自動化されたスクリプトまたはボットネットの一部を使用している可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

*   **ルート権限の奪取を試行:** 攻撃者はシステムの最高権限である `root` ユーザーのパスワードを特定し、ログインに成功しています。これにより、もし実システムであれば、攻撃者はシステムの完全な制御権を掌握したことになります。
*   **永続化メカニズムの確立試行:** ログイン成功後、SSH公開鍵ベースのバックドアを設置しようとしており、これによりパスワードが変更されたとしてもシステムへのアクセスを維持する計画であったことが示唆されます。これは、攻撃者が長期的なアクセスを目的としていることを明確に示しており、極めて危険です。
*   **広範なブルートフォース攻撃:** 攻撃者は様々なパスワードを試行しており、これはインターネットに公開されたSSHサービス全般に対する広範なスキャンと攻撃の一部であると考えられます。
*   **自動化された攻撃:** 人手によるものではなく、自動化されたスクリプトによる攻撃であり、継続的かつ効率的に脆弱なシステムを探し出し、侵入を試みる特性があります。

### 4. 推奨アクション

**緊急対応:**

1.  **攻撃元IPのブロック:** 攻撃元IPアドレス `173.10.13.18` からのすべての通信を、ファイアウォールまたはIPS/IDSで即座にブロックしてください。
2.  **SSHサービスの認証強化:**
    *   **パスワード認証の無効化:** 可能であれば、SSHサービスにおいてパスワード認証を完全に無効にし、公開鍵認証のみを許可するように設定してください。
    *   **`root` ユーザーのログイン無効化:** `sshd_config` に `PermitRootLogin no` を設定し、`root` ユーザーの直接ログインを禁止してください。
    *   **強力なパスワードポリシーの適用:** すべてのシステムユーザーに対して、複雑でユニークなパスワードの使用を強制してください。
3.  **既存システムへの影響評価:** Cowrieハニーポットのログであるため直接的な被害はありませんが、この攻撃と同じ手法が他の本番環境のシステムに対して行われていないか、SSHログ (auth.log等) を確認し、同様のログイン成功や不審なコマンド実行がないか確認してください。
4.  **`authorized_keys`の監査:** 全てのユーザー（特に`root`）の`.ssh/authorized_keys`ファイルに、身元不明な公開鍵が登録されていないか確認し、不審なものがあれば削除してください。本ログに記載されている公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が存在しないか特に注意してください。

**予防策:**

1.  **多要素認証 (MFA) の導入:** SSHを含む重要なサービスへのログインにMFAを導入し、認証の強度を高めてください。
2.  **侵入検知/防御システム (IDS/IPS) の導入と強化:** SSHブルートフォース攻撃を自動的に検知・ブロックできるような設定を導入・強化してください (`fail2ban`等のツールも有効です)。
3.  **SSHポートの変更:** デフォルトの22番ポートから別のポートに変更することも、自動化されたスキャンによる攻撃の機会を減らす効果があります（セキュリティバイオブスキュリティ）。
4.  **定期的なセキュリティ監査と脆弱性診断:** システムの脆弱性を定期的にスキャンし、最新のパッチを適用してください。
5.  **ログ監視の強化:** SIEM (Security Information and Event Management) システムなどを活用し、SSHのログイン試行、成功、失敗、不審なコマンド実行などのログを継続的に監視し、異常を早期に検知できる体制を構築してください。