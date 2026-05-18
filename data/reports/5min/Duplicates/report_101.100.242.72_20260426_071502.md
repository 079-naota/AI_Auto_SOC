# SOC自動分析レポート: 101.100.242.72

**生成日時:** 2026-04-26 07:18:20

---

## SOC分析レポート

**件名: 攻撃ログ分析報告書 - SSHブルートフォースおよび永続化の試み**

**日付:** 2026年04月26日
**報告者:** SOCアナリスト

### 1. 攻撃の概要と目的

攻撃元IP `101.100.242.72` から、当社のハニーポット（Cowrie）に対し、継続的なSSHブルートフォース攻撃が確認されました。攻撃者は複数の一般的なユーザー名（例: frappe, deployer, ubuntu, admin, tester, test, oracle, user, zhaoxj）と辞書攻撃的なパスワードリストを試行しています。

特に注目すべきは、`root` ユーザーでのログイン成功が複数回記録されており、成功するたびに以下の共通した行動パターンが確認されました。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh` コマンドで、`.ssh` ディレクトリの属性変更を試みる。(`lockr` は存在しないコマンドとして失敗)
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~` コマンドで、`.ssh` ディレクトリを削除・再作成し、特定のSSH公開鍵を `authorized_keys` ファイルに書き込み、パーミッションを設定している。

攻撃の目的は、SSHの脆弱な認証情報を悪用してシステムに初期アクセスを確立し、その後、公開鍵認証によるバックドア（永続化メカニズム）を設置することで、将来的にパスワードなしでシステムへのアクセスを維持することであると推測されます。これは、システムの完全な乗っ取り、ボットネットへの組み込み、またはさらなる攻撃の足がかりとすることを意図していると考えられます。

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **ブルートフォース攻撃 / 辞書攻撃:** ターゲットシステムに対するSSH認証情報の網羅的な試行。特に `root` ユーザーに焦点を当てている。
    *   **永続化 (Persistence):** ログイン成功後、速やかに `~/.ssh/authorized_keys` ファイルに攻撃者自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を追加することで、永続的なアクセス経路を確保しようとしています。鍵のコメント「mdrfckr」は攻撃者の特徴的なサインである可能性があります。
    *   **防御回避 (Defense Evasion):** `chattr -ia .ssh` コマンドは、ファイルやディレクトリの不変属性を解除しようとする試みであり、システム管理者による防御措置を回避する意図が見られます。
*   **使用ツール:**
    *   ログのパターン（連続的なログイン試行、成功後の定型的なコマンド実行）から、SSHクライアント機能とブルートフォース機能を兼ね備えた自動化された攻撃ツール（例: `Hydra` や `Medusa` のようなパスワードクラッカー、またはカスタムスクリプト）が使用されている可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

*   **ログイン成功の頻発:** ハニーポット上とはいえ、`root` ユーザーでのログイン成功が複数回（計5回）記録されており、もしこれが実システムであれば、攻撃者はシステムの最高権限を何度も奪取していることになります。
*   **永続化の試み:** ログイン成功直後に、攻撃者は公開鍵を設置してバックドアを確保しようとしています。これは単なる一時的な侵入ではなく、長期的なシステム乗っ取りを意図している明確な証拠です。
*   **権限の高いユーザー（root）の標的:** 攻撃者はシステム上で最も強力な権限を持つ `root` ユーザーを狙っており、成功した場合はシステム全体に甚大な影響を及ぼす可能性があります。
*   **自動化された攻撃:** 攻撃は自動化されており、継続的かつ広範囲な環境に対して同様の攻撃を展開している可能性があり、類似の脆弱性を持つ他のシステムも標的となるリスクがあります。

### 4. 推奨アクション

この攻撃はハニーポットに対するものでしたが、もし実システムであった場合、深刻な侵害が発生していた状況です。以下の即時対応と長期的な対策を実施することを強く推奨します。

#### 4.1. 即時対応（Immediate Action）

1.  **攻撃元IPのブロック:** 攻撃元IP `101.100.242.72` からのSSH接続を、ファイアウォールやIDS/IPSで即座にブロックリストに追加してください。
2.  **侵害された認証情報の確認と変更:**
    *   ログに記録されたログイン成功パスワード（`qwer1234QWER!@#$`, `3245gs5662d34`, `Ni123456`, `ubuntu@123`, `Password.123`, `a12348765`）が、当社の他のシステムで実際に使用されていないか確認してください。
    *   もし使用されている場合は、該当するアカウントのパスワードを直ちに、かつ十分に複雑なものに変更してください。
3.  **公開鍵認証設定の監査とクリーンアップ:**
    *   全てのシステム（特にSSH公開ポートを持つサーバー）において、全ユーザーの `~/.ssh/authorized_keys` ファイルの内容を監査し、不審な公開鍵がないか確認してください。
    *   特にログに記録された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が存在する場合は、速やかに削除してください。
4.  **システム監査の実施:** 侵害の兆候が見られる可能性のある全てのシステムについて、ログイン履歴、コマンド実行履歴、ファイル変更履歴などを詳細に確認し、他の不審な活動（マルウェアのインストール、外部への通信、データ窃取の痕跡など）がないか調査してください。

#### 4.2. 長期的な対策（Long-term Measures）

1.  **SSH設定の強化:**
    *   **パスワード認証の無効化:** 可能であれば、SSHパスワード認証を無効にし、公開鍵認証のみに限定してください。
    *   **rootユーザーの直接ログイン禁止:** `PermitRootLogin no` を設定し、`root` ユーザーでの直接ログインを禁止し、必要に応じて `sudo` を使用する運用に切り替えてください。
    *   **SSHポートの変更:** 標準の22番ポートから別のポートに変更することを検討してください（セキュリティバイオブスキュリティに過ぎませんが、自動化された攻撃の頻度を減少させる効果があります）。
    *   **許可ユーザーの制限:** `AllowUsers` ディレクティブを使用して、SSH接続を許可するユーザーを明示的に指定し、最小限に制限してください。
    *   **認証試行回数の制限:** `/etc/ssh/sshd_config` に `MaxAuthTries` (例: 3〜6回) を設定し、ログイン試行回数を制限してください。
2.  **多要素認証（MFA）の導入:** SSH接続に多要素認証を必須とすることで、認証情報の漏洩や推測による不正アクセスを防ぎます。
3.  **侵入検知/防御システムの導入:** `fail2ban` のようなツールを導入し、一定回数以上のログイン失敗があったIPアドレスを自動的にブロックするように設定してください。
4.  **強力なパスワードポリシーの強制:** 全てのシステムユーザーに対して、複雑でユニークなパスワードの使用を強制するポリシーを導入し、定期的な変更を促してください。
5.  **セキュリティパッチの適用:** OSおよびSSHサーバーソフトウェア（OpenSSHなど）を常に最新の状態に保ち、既知の脆弱性への対策を徹底してください。
6.  **定期的なログ監視の強化:** SIEM (Security Information and Event Management) などのツールを活用し、SSHログインの失敗、異常なログイン元、特権コマンドの実行、ファイル属性変更などを継続的に監視し、アラートを発報する体制を強化してください。
7.  **公開鍵の厳格な管理:** 不要になった公開鍵は速やかに削除し、定期的に `authorized_keys` ファイルの内容を確認するプロセスを確立してください。