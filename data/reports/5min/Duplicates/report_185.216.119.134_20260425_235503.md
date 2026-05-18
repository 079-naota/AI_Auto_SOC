# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 23:57:18

---

## 攻撃ログ分析レポート

### 1. 攻撃の概要と目的

このログは、攻撃元IPアドレス `185.216.119.134` からのSSHサービスに対するブルートフォース攻撃を示しています。攻撃は2026年4月25日04:15:39Zから04:47:34Zにかけて行われました。

攻撃者は様々なユーザー名とパスワードの組み合わせを試行しており、特に `root` ユーザーに対して複数のパスワードでログイン成功を記録しています。ログイン成功後、攻撃者はシステムに永続的なアクセス経路を確立するために、以下の行動を試みています。

*   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh`ディレクトリのファイル属性を変更し、権限を操作しようとする試み。
*   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: `.ssh`ディレクトリを削除・再作成し、指定されたSSH公開鍵を `authorized_keys` ファイルに追加することで、パスワードなしでのアクセス（バックドア）を確立しようとする試み。

攻撃の主な目的は、SSHを介してシステムに不正侵入し、永続的なアクセス経路を確保することであると推測されます。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSHブルートフォース攻撃 / パスワードスプレー攻撃**: `zabbix`, `john`, `satya`, `admin`, `test`, `user`, `root` など複数のユーザー名に対して、既知の脆弱なパスワードリストや辞書に基づいたパスワードを試行しています。特に `root` ユーザーに対しては何度も異なるパスワードを試みています。
    *   **認証情報の永続化 (Persistence)**: ログインに成功した後、攻撃者は自身が管理するSSH公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を `root` ユーザーの `~/.ssh/authorized_keys` に追加しようとしました。これにより、将来的にパスワードを知らなくても、この公開鍵に対応する秘密鍵を持つ攻撃者がアクセスできるようになります。
    *   **隠蔽工作の試み**: `chattr -ia .ssh; lockr -ia .ssh` コマンドは、`authorized_keys`ファイルの属性を変更し、削除や変更を困難にすることで、バックドアの存在を隠蔽または保護しようとする意図があった可能性があります。

*   **使用ツール**:
    *   攻撃の時間間隔や多数の試行から、標準的なSSHクライアントと連携する自動化されたスクリプト、またはボットネットの一部として動作するマルウェアが使用されている可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
1.  **ログイン成功の頻発**: `root` ユーザーで複数回ログインに成功している記録があります（ハニーポット上での成功）。これは、一般的なパスワードや辞書攻撃で簡単に推測されうるパスワードが使用されている可能性を示唆しており、もし本番環境でこれらのパスワードが使用されている場合、実際のシステムが深刻な危険に晒されます。
    *   成功した `root` パスワード: `123.com.`, `nPSpP4PBW0`, `3245gs5662d34`, `Aa112211.`, `123Qwe!@#`, `Admin12!@#`
2.  **永続化の試み**: ログイン後、攻撃者は自身の公開鍵を `authorized_keys` に追加しようとしました。これは、単なる情報窃取だけでなく、システムの制御を奪取し、永続的なバックドアを確立しようとする明確な意図を示しています。
3.  **root権限での活動**: 攻撃者が `root` ユーザーとしてコマンド実行を試みているため、もし本番環境でログインが成功していれば、システム全体が完全に侵害されるリスクがあります。
4.  **自動化された攻撃**: 短時間で多数の試行と複雑なコマンド実行を繰り返していることから、これは手動ではなく自動化されたボットによる攻撃である可能性が高く、他のシステムにも同様の攻撃を仕掛けている可能性があります。

### 4. 推奨アクション

#### 4.1. 緊急対応 (Immediate Actions)

1.  **攻撃元IPのブロック**:
    *   攻撃元IPアドレス `185.216.119.134` をファイアウォールやIPS/IDSにてブロックリストに追加し、今後のアクセスを遮断してください。
2.  **認証情報の変更と確認**:
    *   ログに記録された `root` ユーザーおよび成功したパスワード（`123.com.`, `nPSpP4PBW0`, `3245gs5662d34`, `Aa112211.`, `123Qwe!@#`, `Admin12!@#`）が、もし本番環境のどのシステムでも使用されている場合、**直ちにこれらのパスワードを複雑なものに変更してください。**
    *   攻撃ログに現れた他のユーザー名とパスワードの組み合わせ（例: `zabbix:test`, `john:1234567890`, `satya:satya123`, `admin:admin0` など）が、本番環境のシステムで使用されていないか確認し、使用されている場合は変更を検討してください。
3.  **不正なSSH公開鍵の確認と削除**:
    *   全てのSSHサーバー（特に `root` ユーザー）の `~/.ssh/authorized_keys` ファイルをレビューし、ログに記録された以下の公開鍵が存在しないか確認してください。
        `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`
    *   もし発見された場合、直ちに当該公開鍵のエントリを削除し、ファイルのパーミッションを適切に設定し直してください（例: `chmod 600 ~/.ssh/authorized_keys`）。
4.  **侵害有無の確認**:
    *   ログインが成功したとされるシステムにおいて、不審なプロセス、ファイル、ネットワーク接続がないか、また監査ログに不審な活動が記録されていないか、詳細な調査を実施してください。

#### 4.2. 長期的な対策 (Long-term Measures)

1.  **SSHセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能な限り、SSHパスワード認証を無効にし、公開鍵認証のみに限定してください。
    *   **rootログインの禁止**: `PermitRootLogin no` を設定し、`root` ユーザーがSSHで直接ログインできないように設定してください。管理者権限が必要な場合は、一般ユーザーでログイン後、`sudo` を使用することを義務付けてください。
    *   **強力なパスワードポリシー**: 全てのユーザーに対して、十分に長く複雑なパスワードを強制するポリシーを導入してください。
    *   **多要素認証 (MFA)**: 重要なシステムへのSSHアクセスには、多要素認証を導入することを強く推奨します。
    *   **Fail2banなどの導入**: 短時間での複数回ログイン失敗を検知し、自動的に攻撃元IPアドレスをブロックするツール（例: Fail2ban）を導入してください。
    *   **SSHポートの変更**: 標準の22番ポートではなく、使用頻度の低い高位ポートに変更することで、自動化されたスキャンからのノイズを減らすことができます（根本的なセキュリティ対策ではない点に留意）。
2.  **監視強化**:
    *   SSHログイン試行（成功・失敗）、`authorized_keys`ファイルへの変更、不審なコマンド実行、ファイルダウンロードなどのイベントに対して、SIEMやログ監視システムでアラートを設定し、異常を早期に検知できる体制を構築してください。
    *   ハニーポット（Cowrieなど）のログをSIEMに統合し、攻撃トレンドや新しい攻撃手法の情報を継続的に収集・分析してください。
3.  **システムとソフトウェアの定期的な更新**:
    *   OS、SSHサーバ、その他のシステムコンポーネメントを常に最新の状態に保ち、既知の脆弱性を悪用した攻撃を防いでください。
4.  **セキュリティ意識向上トレーニング**:
    *   従業員に対し、フィッシング、ソーシャルエンジニアリング、パスワードの適切な管理方法など、セキュリティに関する定期的なトレーニングを実施してください。

以上の推奨アクションを実施し、システムのセキュリティ体制を強化してください。