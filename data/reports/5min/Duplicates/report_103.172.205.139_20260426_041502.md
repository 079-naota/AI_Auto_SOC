# SOC自動分析レポート: 103.172.205.139

**生成日時:** 2026-04-26 04:18:41

---

## SOC分析レポート

### 1. 攻撃の概要と目的

このログは、攻撃元IPアドレス `103.172.205.139` からのSSHサービスに対する継続的な攻撃を示しています。
攻撃は主に以下のフェーズで構成されています。

1.  **偵察と認証情報の窃取**: 複数の一般的なユーザー名（`user7`, `deployer`, `frappe`, `ubuntu`, `user`, `mary`, `admin`, `zhaoxj`など）と、それに続く辞書攻撃・パスワードリスト攻撃と推測される多様なパスワードを試行しています。
2.  **特権アカウントへの不正ログイン**: 複数回にわたり、`root`ユーザーとして異なるパスワード（`abcd1234.`, `Password.123`, `MoeClub.org`, `a12348765`, `abc@123456`）でのログインに成功しています。これは非常に重大なセキュリティ侵害です。
3.  **永続性の確保（バックドア設置）**: ログイン成功後、攻撃者は自身のSSH公開鍵を `~/.ssh/authorized_keys` に追加しようとするコマンド（`rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK4rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys`）を実行しています。これにより、パスワード認証なしで永続的にシステムへアクセスできるバックドアを設置しようとしています。また、事前に `chattr -ia .ssh` や `lockr -ia .ssh` といったコマンドで `.ssh` ディレクトリの属性を変更し、鍵の設置を確実にしようとしています。

攻撃の最終的な目的は、システムへの不正かつ永続的なアクセス権を確立し、完全な制御を奪うことであると推測されます。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSHブルートフォース/パスワードリスト攻撃**: 多くの異なるユーザー名とパスワードの組み合わせを短時間で試行していることから、自動化されたツールを用いた攻撃である可能性が高いです。攻撃者は、漏洩した認証情報リストや一般的なパスワード辞書を使用していると考えられます。
    *   **永続化メカニズム**: SSH `authorized_keys` を悪用して公開鍵認証によるバックドアを設置しようとしています。これは、一旦システムに侵入した後、将来的に再侵入するための一般的な手法です。
    *   **ファイル属性操作**: `chattr -ia .ssh` や `lockr -ia .ssh` は、SSH鍵ファイルの操作を妨げる可能性のある特殊なファイル属性を解除しようとする試みです。
*   **使用ツール**:
    *   **SSHブルートフォースツール**: `Hydra` や `Medusa`、カスタムスクリプトなど、SSHに対する辞書攻撃やパスワードリスト攻撃を自動化するツールが使用されていると推測されます。
    *   **SSHクライアント**: ログイン成功後のコマンド実行には、標準的なSSHクライアント、またはシェルスクリプトやPythonスクリプトなどの自動化スクリプトが使用されていると考えられます。
    *   **公開鍵**: ログに残された `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK4rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` は、攻撃者固有のバックドア用公開鍵です。コメントが `mdrfckr` であることから、悪意のある意図が明確です。

### 3. 脅威レベルとその理由

**脅威レベル: 非常に高い (Critical)**

**理由**:

*   **特権アカウントへのログイン成功**: `root`アカウントへのログインが複数回成功しており、もしこのシステムが実運用環境であれば、システム全体が完全に侵害された状態となります。
*   **永続化の試み**: 攻撃者がバックドア（SSH公開鍵）を設置しようとしていることは、一度の侵害で終わらず、将来にわたってシステムへのアクセスを維持し、より広範な悪意ある活動（データ窃取、マルウェア展開、DDoSボットへの組み込みなど）を行う意図があることを強く示唆します。
*   **継続的な攻撃**: 攻撃は一度きりではなく、異なるパスワードやログイン試行を繰り返して継続的に行われています。これは、攻撃者が執拗にシステムの完全な支配を目指していることを示します。

このログはハニーポットで捕捉されたものですが、実際のシステムであれば壊滅的な影響を及ぼす可能性があります。

### 4. 推奨アクション

この攻撃を受けて、以下の推奨アクションを講じる必要があります。

**緊急対応（Critical Actions）**:

1.  **攻撃元IPのブロック**: 直ちに攻撃元IPアドレス `103.172.205.139` をファイアウォール、IDS/IPSなどでブロックし、さらなるアクセスを遮断します。
2.  **SSH認証情報の変更**: ログに記録された `root` ユーザーの成功パスワード（`abcd1234.`, `Password.123`, `MoeClub.org`, `a12348765`, `abc@123456`）が実システムで使用されていないか緊急確認し、もし使用されている場合は、全てのシステムで直ちに強固でユニークなパスワードに変更してください。
3.  **SSH設定の強化**:
    *   **rootログインの無効化**: SSH経由での `root` ユーザーの直接ログインを無効化し、一般ユーザーでログイン後に `sudo` を使用する運用に切り替えてください。 (`PermitRootLogin no` を設定)
    *   **パスワード認証の無効化**: SSHのパスワード認証を無効化し、鍵認証のみに限定してください。 (`PasswordAuthentication no` を設定)
    *   **鍵認証の確認**: 全てのユーザーの `~/.ssh/authorized_keys` ファイルを徹底的にレビューし、ログに記載された攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK4rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を含む未知の公開鍵がないか確認し、発見した場合は直ちに削除してください。また、`~/.ssh` ディレクトリと `authorized_keys` ファイルの適切なパーミッション設定（`chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/authorized_keys`）を強制してください。
4.  **多要素認証 (MFA) の導入**: 公開されているSSHサービスには、可能であれば多要素認証を導入し、セキュリティを強化してください。
5.  **ログ監査の強化**: 不審なログイン試行や特権コマンドの実行を検知するためのログ監視ルールを強化し、アラート体制を整備してください。

**長期的な対応（Long-Term Measures）**:

1.  **脆弱性管理**: OSおよびミドルウェアの定期的なセキュリティパッチ適用を徹底し、既知の脆弱性を排除してください。
2.  **ネットワークセグメンテーション**: SSHサービスへのアクセスを信頼できるIPアドレス範囲に限定し、必要に応じてVPNなどのセキュアな経路を介してのみアクセスを許可するよう見直してください。
3.  **HIDS/EDRの導入**: ホストベースの侵入検知システム（HIDS）やエンドポイント検出応答（EDR）ソリューションを導入し、不審なファイル変更やプロセス実行をリアルタイムで検知・対応できる体制を構築してください。
4.  **インシデントレスポンス計画の見直し**: 今回の攻撃パターン（ブルートフォースからのバックドア設置）を考慮に入れ、インシデントレスポンス計画を定期的に見直し、訓練を実施してください。
5.  **セキュリティ教育**: 強固なパスワードポリシーの徹底、不審なアクティビティ報告など、従業員のセキュリティ意識向上教育を継続的に実施してください。