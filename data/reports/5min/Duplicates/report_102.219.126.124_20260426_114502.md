# SOC自動分析レポート: 102.219.126.124

**生成日時:** 2026-04-26 11:46:05

---

## 攻撃分析レポート

### 1. 攻撃の概要と目的

攻撃元IP `102.219.126.124` から、SSHサービスを標的としたブルートフォース/辞書攻撃が確認されました。攻撃者は複数のユーザー名とパスワードの組み合わせを試行し、特に `root` ユーザーに対して集中的に攻撃を行っています。

攻撃は以下の段階で進行しました：
1.  **初期偵察/ブルートフォース試行:** `drcom` などのユーザー名でログインを試行し失敗。
2.  **ログイン成功と不正アクセスの確立:** 約15分後、`root` ユーザーとして複数の異なるパスワード (`1qaz@WSX3edc$RFV!@`, `ali123456`, `Root8`, `Aa112211.`, `Config123`, `Aa123321` など) でログインに成功しています。
3.  **永続化の試行:** ログイン成功後、攻撃者は即座に以下のコマンドを実行し、自身のSSH公開鍵をターゲットシステムの `~/.ssh/authorized_keys` に埋め込むことで、パスワードなしでの再ログイン経路を確立しようとしました。
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh` (ファイルの属性変更を試行)
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
攻撃の主な目的は、ターゲットシステムへの永続的なアクセス経路を確立し、将来的な偵察、データ窃取、マルウェア展開、または他のシステムへの足がかりとしての利用を可能にすることであると推測されます。

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **ブルートフォース攻撃 / 辞書攻撃:** SSHの認証情報を無差別または辞書ベースで試行し、有効なクレデンシャルを発見しようとした。
    *   **永続化 (Persistence):** `authorized_keys`ファイルに自身の公開鍵を登録することで、パスワードなしでシステムに再アクセスできるバックドアを設置しようとした。
    *   **防衛回避 (Defense Evasion):** `chattr`コマンド（および不明な`lockr`コマンド）を使用し、`.ssh`ディレクトリのimmutable属性を無効化しようとした形跡から、既存のセキュリティ設定を迂回し、永続化を強固にしようとした可能性がある。
*   **使用ツール:**
    *   SSHクライアント機能を持つ自動化されたブルートフォースツールまたはスクリプト（例: Hydra, Medusa, またはカスタムスクリプト）。
    *   特定の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) は、特定の攻撃グループやマルウェアキャンペーンに関連付けられる可能性があります。鍵のコメント「mdrfckr」も特徴的です。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**
*   **ログイン成功:** `root`ユーザーとして複数回ログインに成功しており、これは実際のシステムであれば最高レベルの権限が奪取されたことを意味します。ハニーポットのログであっても、攻撃者の意図と能力を示すものです。
*   **永続化の試行:** 攻撃者が永続的なアクセス経路を確立しようとしたことは、後続のより深刻な攻撃（データ窃取、マルウェア展開、システム破壊など）の前段階であり、非常に危険です。
*   **Root権限の悪用:** `root`ユーザーとしてアクセスを試みていることから、成功すればシステム全体に対する完全な制御を得ることを意図しており、被害の範囲が広範に及ぶ可能性があります。
*   **自動化された攻撃:** ログイン成功から永続化のコマンド実行までの一連の動作が迅速かつ定型的であることから、自動化されたツールやスクリプトが使用されている可能性が高く、広範囲のシステムが標的となっている可能性があります。
*   **複数の成功パスワード:** 複数の異なる`root`パスワードでログイン成功している事実は、もしこれが実際のシステムであれば、非常に脆弱なパスワード管理を示唆します。

### 4. 推奨アクション

#### 緊急対応 (Immediate Actions):

1.  **攻撃元IPのブロック:** ファイアウォール、WAF、IDS/IPSなどのセキュリティデバイスで、攻撃元IPアドレス `102.219.126.124` からの全ての通信を即座にブロックしてください。
2.  **SSHサービスログの緊急監査:** 公開されている全てのSSHサービスを持つシステムについて、過去の認証ログを緊急で確認し、以下の情報を調査してください。
    *   `102.219.126.124` からの接続履歴。
    *   ログに記録された成功パスワード (`1qaz@WSX3edc$RFV!@`, `ali123456`, `Root8`, `Aa112211.`, `Config123`, `Aa123321`, `3245gs5662d34` など) を使用したログイン成功がないか。
    *   `root`ユーザーへの不正ログイン試行や成功がないか。
3.  **侵害の有無の確認と対応:**
    *   もし上記のパスワードのいずれかが実際のシステムで使われていた場合、または`root`ログインが成功していた場合は、直ちに該当アカウントのパスワードを変更してください。
    *   `~/.ssh/authorized_keys`ファイルに、攻撃者が埋め込もうとした公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が存在しないか確認し、存在する場合は即座に削除してください。
    *   疑わしいシステムは隔離し、専門家による詳細なフォレンジック調査を実施して、他のバックドアやマルウェアの有無、データ窃取の痕跡などを確認してください。

#### 恒久的な対策 (Long-Term Mitigation):

1.  **SSHセキュリティの強化:**
    *   **パスワード認証の無効化:** 可能であれば、パスワード認証を完全に無効にし、公開鍵認証のみを許可するように設定してください。
    *   **Rootログインの禁止:** `PermitRootLogin no` を設定し、`root`ユーザーの直接ログインを禁止してください。必要な場合は、一般ユーザーでログイン後、`sudo` を利用するようにしてください。
    *   **強固なパスワードポリシーの徹底:** 全てのシステムユーザーに対して、複雑性、長さ、有効期限などを含む厳格なパスワードポリシーを導入し、定期的な変更を強制してください。
    *   **多要素認証 (MFA) の導入:** SSHアクセスに対して多要素認証を導入し、セキュリティを強化してください。
    *   **ポート変更:** SSHの標準ポート22番を非標準ポートに変更することで、自動化された広範なスキャンからの露呈を減らすことができます（セキュリティバイオブスキュリティですが、初期的な保護には有効です）。
2.  **ブルートフォース対策:**
    *   `Fail2ban` などの侵入検知/防御システムを導入し、不正なログイン試行を自動で検知・ブロックする仕組みを構築してください。
3.  **システムの監査と監視の強化:**
    *   定期的にユーザーアカウント、認証情報（特に`authorized_keys`）、およびシステムログの監査を実施してください。
    *   SIEM（Security Information and Event Management）ソリューションを導入し、SSHログイン試行、成功、コマンド実行などのログを一元的に収集・監視し、異常を早期に検知できる体制を構築してください。
4.  **脅威インテリジェンスの活用:** 攻撃元のIPアドレスや埋め込まれた公開鍵情報を脅威インテリジェンスプラットフォームに登録し、関連する脅威情報を継続的に収集・分析してください。
5.  **セキュリティ意識向上トレーニング:** システム管理者およびユーザーに対して、SSHの安全な利用方法、強固なパスワードの重要性、不審な活動の報告方法などについて定期的なトレーニングを実施してください。