# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 23:16:48

---

## 攻撃ログ分析レポート

**分析対象ログ**: Cowrieハニーポットログ
**攻撃元IP**: 185.216.119.134
**分析期間**: 2026-04-25T04:15:39Z から 2026-04-25T04:47:34Z まで

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `185.216.119.134` から、SSHサービスに対して継続的なブルートフォース（またはパスワードスプレー）攻撃が確認されました。攻撃者は、`zabbix`, `john`, `satya`, `admin`, `test`, `test1`, `user` といった様々な一般的なユーザー名に加え、特に `root` ユーザーに対して多数のパスワードを試行しています。

この攻撃の最も重要な点は、**`root` ユーザーでのログインに複数回成功している点**です。ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確立しようと、以下のコマンドを実行しています。

`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

このコマンドは、`root`ユーザーのホームディレクトリにある`.ssh`ディレクトリを一度削除し、新たに作成し直した上で、特定のSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を `authorized_keys` ファイルに追加しようとするものです。これにより、攻撃者はパスワードなしで該当システムにSSH接続できるようになり、バックドアを確立することを目的としています。

### 2. 推測される手法・使用ツール

*   **ブルートフォース/パスワードスプレー攻撃**: ログには多数の異なるユーザー名とパスワードの組み合わせが短時間で試行されており、自動化されたスクリプトやツール（例: Hydra, NmapのNSEスクリプトなど）が用いられたブルートフォース攻撃であると推測されます。
*   **SSH公開鍵認証バックドアの設置**: ログイン成功後に実行されたコマンドは、永続的なアクセスを確保するための典型的な手法です。攻撃者はSSH公開鍵認証を利用して、パスワードに依存しないアクセス経路を確保しようとしています。この種の活動は、感染後のマルウェアやスクリプトの一部として自動的に実行されることが多いです。
*   **不明なコマンドの使用**: `chattr -ia .ssh; lockr -ia .ssh` の中の `lockr` コマンドは標準的なLinuxコマンドではなく、タイポであるか、特定のマルウェアや攻撃ツールが提供する独自の機能である可能性があります。ハニーポットの特性上、これらのコマンドは `cowrie.command.failed` と記録されています。
*   **SSHクライアント**: 攻撃は標準的なSSHプロトコルを通じて行われており、専用のSSHクライアントまたはそれをラップするスクリプトが使用されています。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
*   **root権限の奪取試行**: 攻撃者はシステムの最高権限である `root` ユーザーとして、合計6回ログインに成功しています（ハニーポット上での成功）。これは、もしこの攻撃が実システムに対して行われていれば、システムの完全な制御を奪われる可能性があったことを意味します。
*   **永続化の試み**: ログイン成功後に不正なSSH公開鍵を設置しようとしていることは、一度侵入に成功すれば、パスワードが変更されても攻撃者がシステムにアクセスし続けることを可能にするため、非常に危険です。これにより、恒久的なバックドアが形成されるリスクがあります。
*   **一般的なパスワードの悪用**: 攻撃で成功したパスワード（例: `123.com.`, `3245gs5662d34`, `nPSpP4PBW0`, `Aa112211.`, `123Qwe!@#`, `Admin12!@#`）には、一般的に利用されやすいパターンや、辞書攻撃でヒットしやすいものが含まれています。これは多くのシステムで存在する脆弱性を狙った広範な攻撃であることを示唆しています。
*   **広範な攻撃範囲**: 複数の異なるユーザー名やパスワードを試行しており、組織内の他のSSHサービスに対しても同様の攻撃が行われる可能性があります。
*   **ハニーポットでの検知**: 今回のログはCowrieハニーポットで記録されたため、実際のシステムへの被害は発生していませんが、このログは攻撃者が積極的に脆弱なSSHサーバーを探し、侵入を試みている明確な証拠となります。実環境で同様の脆弱性（弱いパスワード、SSHのインターネット公開など）が存在する場合、深刻なインシデントに発展する可能性が非常に高いです。

### 4. 推奨アクション

1.  **攻撃元IPのブロック**:
    *   攻撃元IPアドレス `185.216.119.134` をファイアウォール、IDS/IPS、またはWAFで即座にブロックし、今後のアクセスを遮断してください。
2.  **SSHパスワードの強化と変更**:
    *   システム内の全てのSSHユーザー（特に `root` ユーザー）のパスワードを、複雑で推測されにくいものに強制的に変更してください。
    *   パスワードポリシーを見直し、定期的なパスワード変更や、十分な複雑性を求める要件を導入してください。
3.  **SSH鍵認証の強化と監査**:
    *   `root` ユーザーでのSSHパスワード認証を無効化し、鍵認証のみに制限してください。
    *   システム上の全ての `~/.ssh/authorized_keys` ファイルの内容を監査し、不審な公開鍵が登録されていないか確認し、発見した場合は直ちに削除してください。特に、ログに記載されている攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が含まれていないかを確認してください。
    *   可能であれば、SSH接続に多要素認証 (MFA) を導入し、セキュリティを強化してください。
4.  **SSH公開設定の見直し**:
    *   インターネットに公開されているSSHサービスを精査し、不必要に公開されているものは停止するか、VPNやジャンプサーバーなどのより安全な経路経由でのアクセスに限定してください。
    *   SSHポートを標準の22番から変更する（セキュリティの強化としては限定的ですが、自動化されたスキャンからのヒットを減らせます）。
5.  **認証ログ監視の強化**:
    *   SSHログイン試行ログ（`/var/log/auth.log` など）を継続的に監視し、不審なログイン試行（特に短時間での多数のログイン失敗）をリアルタイムで検知できるSIEM (Security Information and Event Management) システムや集中ログ管理システムを導入・強化してください。
    *   `fail2ban` などのツールを導入し、ログイン失敗回数が多いIPアドレスを自動的に一時ブロックする設定を適用してください。
6.  **システムの脆弱性スキャン**:
    *   組織内の全システムに対し、定期的な脆弱性スキャンを実施し、SSHサービス以外の潜在的な脆弱性も特定・修正してください。
7.  **脅威情報の共有**:
    *   この攻撃元IPアドレス、試行されたユーザー名/パスワード、不正なSSH鍵情報（mdrfckr）を社内のセキュリティチームや関連するセキュリティコミュニティと共有し、他のシステムへの影響がないか確認するとともに、情報連携を強化してください。
8.  **ハニーポットログの継続的な分析**:
    *   Cowrieハニーポットのログを継続的に分析し、新たな攻撃手法や攻撃元を早期に特定できるよう努めてください。