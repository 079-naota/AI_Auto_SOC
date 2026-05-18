# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 17:27:45

---

## SOCアナリストによる攻撃ログ分析レポート

### 1. 攻撃の概要と目的

提供されたCowrieハニーポットのログを分析した結果、攻撃元IP `182.70.243.207` から複数回にわたるSSHサービスへのブルートフォース/辞書攻撃が確認されました。攻撃者は主に`root`ユーザーを標的とし、様々なパスワードの組み合わせを試行しています。

この攻撃の主な目的は、SSHサービスへの不正なアクセスを確立し、さらにシステムに攻撃者自身の公開鍵を`authorized_keys`ファイルに追加することで、パスワード認証なしで永続的なバックドアアクセスを確立しようとすることであると推測されます。一度アクセスに成功すると、攻撃者は`~/.ssh`ディレクトリを操作し、自身のSSH公開鍵を設置することで、今後のアクセスを容易にしようと試みています。

### 2. 推測される手法・使用ツール

*   **ブルートフォース/辞書攻撃**:
    *   攻撃者は`steam`、`root`、`tunnel`、`cloud`、`gitlab`といったユーザー名と、多種多様なパスワード（例: `steamsteamsteam`, `QAZwsx`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#`）を繰り返し試行しています。
    *   また、`345gs5662d34`という特徴的なユーザー名とパスワードの組み合わせも頻繁に試行されています。これは、ボットネットなどで一般的に使用されるデフォルト認証情報、または特定のマルウェアが試行する認証情報の一部である可能性があります。
*   **永続化のためのバックドア設置**:
    *   ログイン成功後、攻撃者は以下のコマンドを自動的に実行しようとしています。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh`ディレクトリのファイル属性（不変属性や追記属性）を解除し、内容の変更を可能にしようとしています。`lockr`コマンドは標準的なLinuxコマンドではないため、実行に失敗しています。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`:
            *   既存の`.ssh`ディレクトリを削除し、再作成。
            *   攻撃者のSSH公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を`.ssh/authorized_keys`に追加。
            *   `.ssh`ディレクトリのパーミッションを適切に設定し、鍵認証でのアクセス準備を整えています。
*   **自動化ツール/スクリプト**:
    *   一連のログイン試行と、ログイン成功後のコマンド実行は、間隔が短く、同じパターンで繰り返されていることから、自動化されたスクリプトやツールによって実行されていると判断されます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
1.  **侵入の成功と永続化の試み**: 攻撃者は複数回にわたって`root`ユーザーでのログインに成功しており、これはシステムの最高権限を奪取したことを意味します。ログイン成功後、速やかにSSH公開鍵を設置して永続的なアクセス経路を確立しようとしているため、その意図は明確なシステム制御の奪取と継続的なアクセスです。
2.  **広範なブルートフォース攻撃**: 特定のユーザー名だけでなく、一般的なユーザー名と様々なパスワードの組み合わせを網羅的に試行していることから、攻撃者は自動化されたツールを用いて脆弱なSSHサービスを持つシステムを広く探索していると考えられます。
3.  **特徴的な認証情報の利用**: `345gs5662d34`のような特定のランダムな文字列のユーザー名とパスワードを繰り返し試行していることは、特定のマルウェアやボットネットの活動パターンに合致する可能性があります。
4.  **活動の継続性**: 比較的短時間のうちに何度もログイン試行と不正な鍵の設置を繰り返しており、攻撃活動が継続的かつ自動的であると判断できます。

ハニーポットのログであるため、実際にシステムが侵害されたわけではありませんが、この種の攻撃が本番環境で成功した場合、データ漏洩、システム破壊、ランサムウェア感染、さらにはボットネットの一部として悪用されるなど、深刻な被害につながる可能性が極めて高いです。

### 4. 推奨アクション

この攻撃を受けて、以下の推奨アクションを速やかに実施することを強く推奨します。

1.  **攻撃元IPアドレスのブロック**:
    *   攻撃元IPアドレス `182.70.243.207` を組織のファイアウォール、IDS/IPS、またはエッジルーターで即座にブロックし、今後のアクセスを遮断してください。
2.  **SSHセキュリティの強化**:
    *   **パスワード認証の無効化**: 可能な限りSSHのパスワード認証を無効化し、公開鍵認証のみを許可するように設定してください。
    *   **`root`ユーザーの直接ログイン禁止**: `PermitRootLogin no`をSSH設定（`/etc/ssh/sshd_config`）に記述し、`root`ユーザーでの直接ログインを禁止してください。必要に応じて、一般ユーザーでログイン後、`sudo`を使用して権限昇格を行わせる運用に切り替えてください。
    *   **強固なパスワードポリシーの適用**: 辞書攻撃やブルートフォース攻撃に耐えうる、十分な長さと複雑さを持つパスワードの使用を全ユーザーに義務付けてください。
    *   **SSHポートの変更**: 標準の22番ポートではなく、より高いポート番号に変更することを検討してください。これは、自動化されたスキャンからの露出を減らすのに役立ちます（ただし、決定的な対策ではありません）。
    *   **侵入検知/防御システム (Fail2banなど) の導入/設定強化**: ログイン失敗回数に応じて攻撃元IPアドレスを自動的にブロックするツール（Fail2banなど）を導入または設定を強化し、総当たり攻撃への耐性を高めてください。
3.  **認証ログの監視とアラート体制の強化**:
    *   SSHログインの成功および失敗のログ（`auth.log`など）を継続的に監視し、異常なログイン試行パターン（例: 短時間での大量のログイン失敗、未知のユーザー名での試行、`root`ユーザーへの頻繁な試行）を速やかに検知できるアラートシステムを導入または強化してください。
    *   `authorized_keys`ファイルへの変更を監視するファイル整合性監視ツール（FIM）を導入し、不正な鍵の設置を即座に検知できるようにしてください。
4.  **使用された公開鍵のブラックリスト登録**:
    *   今回の攻撃で使用されたSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を、セキュリティデバイスやSSHサーバーの設定でブロック対象として登録することを検討してください。
5.  **ハニーポットの運用見直し**:
    *   Cowrieハニーポットがこのような攻撃を検知した際、より迅速かつ詳細なアラートを発報するよう設定を見直してください。例えば、ログイン成功後のコマンド実行やファイル操作があった場合に、すぐにセキュリティチームに通知されるようにするべきです。
    *   ハニーポットが検知した攻撃手法や使用された認証情報などのインテリジェンスを、実際の防御システムにフィードバックするプロセスを確立してください。