# SOC自動分析レポート: 122.177.246.97

**生成日時:** 2026-04-25 17:36:35

---

## 攻撃ログ分析レポート

### 1. 攻撃の概要と目的

提供されたログは、攻撃元IPアドレス `122.177.246.97` からのSSHサービスに対する不正アクセス試行および侵入後の活動を示しています。攻撃者は複数のユーザー名とパスワードの組み合わせを用いてブルートフォース/パスワードスプレー攻撃を仕掛け、特に`root`ユーザーでのログインに複数回成功しています。

ログイン成功後、攻撃者は以下の目的で一連のコマンドを実行しています。
*   既存のSSH認証情報を削除し、攻撃者自身の公開鍵を追加することで、永続的なアクセス経路（バックドア）を確立する。
*   ファイルシステム属性を変更することで、認証情報ファイルの保護を解除し、変更を容易にする（ただし、`lockr`コマンドは失敗）。

この攻撃は、ターゲットシステムのSSHサービスを悪用し、`root`権限を奪取してシステムの制御権を確立することを目的としています。

### 2. 推測される手法・使用ツール

*   **認証情報推測攻撃 (Credential Stuffing / Brute-force / Password Spraying):** ログからは、`deployer`, `deploy`, `vnc`, `345gs5662d34`, `root`といった様々なユーザー名と、多数のパスワード (`12344321`, `ccQQ123`, `frappe22`, `test123`, `3245gs5662d34`, `AAaa112233`, `Master2025`) を試行していることが確認できます。特に`root`ユーザーに対しては異なる複数のパスワードでログイン成功しており、これは自動化されたスクリプトやツールを用いた辞書攻撃やパスワードスプレー攻撃である可能性が高いです。
*   **永続化メカニズムの確立:** ログイン成功後、攻撃者は以下のコマンドを実行しています。
    `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
    このコマンドは、既存の`.ssh`ディレクトリを削除し、新たなディレクトリを作成した上で、攻撃者自身の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を`authorized_keys`ファイルに書き込むことで、パスワードなしでSSHログインを可能にするバックドアを設置しようとしています。
*   **使用ツール:** 標準的なSSHクライアントおよびシェルコマンド (`cd`, `rm`, `mkdir`, `echo`, `chmod`, `chattr`) が使用されています。パスワード推測攻撃にはHydraやMedusaのような自動化ツールが利用された可能性があります。`lockr`コマンドは標準的なものではないため、カスタムスクリプトの一部であるか、Typoである可能性があります（ログではコマンド失敗と記録されています）。

### 3. 脅威レベルとその理由

**脅威レベル: Critical (非常に高い)**

**理由:**
1.  **最高権限アカウント (`root`) の認証突破:** ログから、攻撃者が`root`アカウントでパスワード認証を複数回成功させていることが確認されます。`root`権限の奪取は、システムに対する完全な制御権を意味し、データ窃取、破壊、改ざん、マルウェアの展開、他のシステムへの踏み台利用など、あらゆる深刻な被害に繋がる可能性があります。
2.  **永続的なアクセス経路の確立試行:** 攻撃者は、自身のSSH公開鍵を`authorized_keys`ファイルに追加することで、システムへのパスワードなしのアクセスを確立しようとしています。これは、初期の認証情報が変更されたとしても、攻撃者がアクセスを維持できるという点で、非常に危険なバックドアとなります。
3.  **執拗な攻撃の継続:** 短期間に複数の異なるパスワードで`root`アクセスに成功し、その都度同様のバックドア設置コマンドを繰り返していることから、攻撃者の執拗な意図と、複数の脆弱なアカウント情報（または推測されやすいパスワード）が存在する可能性が示唆されます。
4.  **Honeypotでの検知:** 本ログはHoneypotであるCowrieによって記録されたものですが、これは実際のシステムに対して同様の攻撃が行われた場合、認証突破とバックドアの設置が成功し、極めて重大なインシデントに発展していた可能性が高いことを意味します。Honeypotが捕捉した脅威であるため実システムへの直接的な被害は発生していませんが、この攻撃パターンは極めて悪質であり、本物のシステムへの脅威として最大限の注意を払う必要があります。

### 4. 推奨アクション

**緊急対応 (Immediate Actions):**

1.  **攻撃元IPアドレスのブロック:** 攻撃元IPアドレス `122.177.246.97` をネットワーク境界（ファイアウォール、IPS/IDSなど）で直ちにブロックし、今後のアクセスを遮断してください。
2.  **rootアカウントのパスワードリセット:** ログに記録されている`root`アカウントで成功した全てのパスワード (`ccQQ123`, `3245gs5662d34`, `AAaa112233`, `Master2025`) は脆弱であるか、既に漏洩している可能性が高いです。直ちに、全ての`root`アカウントおよび同様に脆弱なパスワードを使用している可能性のある全てのアカウントのパスワードを、複雑かつ推測困難なものにリセットしてください。
3.  **SSH `authorized_keys`ファイルの検査とクリーンアップ:** 全てのユーザー（特に`root`）の`~/.ssh/authorized_keys`ファイルを検査し、ログに記載された攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないことを確認してください。もし存在した場合は、直ちに該当する行を削除し、ファイルのパーミッションを適切に設定（通常は`600`）してください。
4.  **システムログの精査:** 過去のSSH認証ログ、システムログ、アプリケーションログなどを遡って精査し、他に不審なログイン試行、成功したログイン、または不正な活動がないか確認してください。
5.  **脆弱性スキャンとマルウェアチェック:** 念のため、システムに対して脆弱性スキャンを実施し、既知の脆弱性が悪用されていないか確認してください。また、マルウェアスキャンを実施し、バックドアや追加の悪意のあるコンポーネントがインストールされていないか確認してください。

**長期的な対策 (Long-term Actions):**

1.  **SSH認証の強化:**
    *   **パスワード認証の無効化:** 可能であれば、パスワード認証を無効化し、SSH鍵認証のみを許可してください。
    *   **`root`ユーザーのSSHログイン禁止:** `root`ユーザーが直接SSHログインすることを禁止し、一般ユーザーでログイン後、`sudo`を利用して特権操作を行うように設定してください。
    *   **多要素認証 (MFA) の導入:** SSHログインにMFAを導入し、セキュリティを強化してください。
2.  **アカウントとパスワードポリシーの強化:**
    *   推測困難で強力なパスワードポリシーを強制し、定期的なパスワード変更を推奨または義務付けてください。
    *   全てのシステムアカウントを監査し、不要なアカウントは削除または無効化してください。
3.  **SSHサービスの公開範囲の制限:**
    *   SSHポート (通常22番) がインターネットに公開されている必要がない場合は、VPN経由でのアクセスに限定するか、信頼できる特定のIPアドレス範囲からのアクセスのみを許可するようにファイアウォールルールを厳格化してください。
    *   SSHサービスのデフォルトポート番号を変更することも、既知の攻撃からの可視性を下げるために有効です。
4.  **システム監視の強化:**
    *   SSHログインの失敗回数が多いIPアドレスを自動的にブロックするツール (例: Fail2Ban) を導入または設定を強化してください。
    *   SSHログイン、特に`root`アカウントへのログイン成功を即座にアラートするルールをSIEM/ログ管理システムに設定してください。
    *   `authorized_keys`ファイルなど、重要な設定ファイルへの変更を監視する設定を追加してください。
5.  **従業員へのセキュリティ意識向上教育:** 強力なパスワードの重要性、不審な活動の報告方法などについて、定期的に従業員にセキュリティ教育を実施してください。