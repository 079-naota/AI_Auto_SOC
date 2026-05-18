# SOC自動分析レポート: 43.155.21.198

**生成日時:** 2026-04-27 11:10:40

---

## SOCアナリストレポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `43.155.21.198` から、複数のSSHログイン試行とシステム侵害を目的とした攻撃が観測されました。
攻撃は、辞書攻撃またはブルートフォース攻撃によりSSH認証情報を特定し、rootユーザーとしてシステムに不正アクセスを試みるものでした。
ログイン成功後、攻撃者は自身のSSH公開鍵をターゲットシステムの `authorized_keys` ファイルに追加することで、永続的なバックドアを設置しようとしました。
さらに、同一のハッシュ値を持つ不明なファイルを複数回ダウンロードしようとしており、これは初期アクセス確立後にシステムの悪用を深めるための追加マルウェア（ペイロード）の展開を意図していると推測されます。

### 2. 推測される手法・使用ツール

1.  **認証情報の総当たり攻撃 (Credential Stuffing / Brute-force Attack)**:
    *   多数の異なるユーザー名およびパスワードの組み合わせ（例: `rootwww:1234qwer`, `345gs5662d34:345gs5662d34`）を用いてSSHログインを試行していることから、自動化されたブルートフォースツールや辞書攻撃ツールが使用された可能性が高いです。
    *   最終的に `root` ユーザーに対して複数のパスワード（例: `6yhnji90-`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`）でログインに成功しています。

2.  **永続化のためのバックドア設置**:
    *   ログイン成功後、攻撃者は `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~` というコマンドを実行しています。
    *   これは、既存の`.ssh`ディレクトリを削除し、再作成した上で、自身のSSH公開鍵（コメント `mdrfckr`）を `~/.ssh/authorized_keys` に追加することで、パスワードなしで将来的にSSH接続ができるようにするバックドアの設置を目的としています。
    *   `chattr -ia .ssh` コマンドも試行されており、`.ssh` ディレクトリの属性を変更し、ファイル操作の制限を解除しようとしたと考えられますが、このコマンドは失敗しています。

3.  **追加ペイロードの展開**:
    *   SSHキーの設置と並行して、またはその直後に、同じSHA256ハッシュ値 `a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2` を持つファイルが複数回ダウンロードされています（取得元URLは不明）。
    *   この行動は、初期アクセス確立後にシステムの悪用を深めるための、追加マルウェアのデプロイを意図していると強く推測されます。
    *   **ペイロードの意図**: SSHアクセスを確立し、永続化のためのバックドアを設置した後にダウンロードされるファイルは、通常、システムのリソースを悪用するためのツールであることが多いです。具体的なペイロードの種類としては、以下が考えられます。
        *   **ボットネットのダウンローダー/クライアント**: 感染したシステムをボットネットの一部とし、DDoS攻撃や他のサイバー犯罪活動に利用するためのエージェントをダウンロード・実行します。
        *   **暗号通貨マイニングスクリプト**: システムのCPUやGPUリソースを不正に利用し、Moneroなどの暗号通貨を採掘させるためのスクリプトやバイナリ。
        *   **追加のバックドア/RAT (Remote Access Trojan)**: より高度な制御を可能にするためのマルウェア。
        *   **情報窃取ツール**: システム情報、認証情報などを収集し、攻撃者に送信するツール。
        *   **ランサムウェア**: ファイルを暗号化し、身代金を要求するマルウェア。
    *   今回の行動履歴からは、特にシステムリソースを直接悪用する暗号通貨マイナーや、さらなる攻撃の足がかりとなるボットネットのエージェントである可能性が高いと判断されます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**
*   **root権限での不正アクセス:** 攻撃者はSSH経由で `root` ユーザーとしてログインすることに成功しており、システムの完全な制御権を取得した状態にあります。
*   **永続化の試み:** 自身のSSH公開鍵を `authorized_keys` に追加することで、パスワードが変更された後もアクセスを維持できる永続的なバックドアを設置しようとしています。これは長期的なシステム侵害を企図するものです。
*   **追加マルウェアの展開:** 不明なファイル（ハッシュ値 `a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2`）のダウンロードを試みていることから、単なるアクセスにとどまらず、システムの機能を悪用したり、他の攻撃の踏み台にしたりする可能性が高いです。
*   このハニーポットが本番環境であった場合、機密情報の窃取、データ破壊、他のシステムへの水平展開、サービス妨害、リソースの不正利用（例: 暗号通貨マイニング）など、甚大な被害が発生する危険性があります。

### 4. 抽出されたIoC (Indicators of Compromise)

*   **攻撃元IPアドレス:** `43.155.21.198`
*   **不正アクセスに成功した認証情報:**
    *   ユーザー名: `root`, パスワード: `6yhnji90-`
    *   ユーザー名: `root`, パスワード: `3245gs5662d34`
    *   ユーザー名: `root`, パスワード: `Pan5202614`
    *   ユーザー名: `root`, パスワード: `zhaojia`
    *   ユーザー名: `root`, パスワード: `P@$$w0rd12`
    *   ユーザー名: `root`, パスワード: `Login!@456`
    *   ユーザー名: `root`, パスワード: `mail@1234`
*   **不正に追加されたSSH公開鍵 (authorized_keys内に埋め込まれた鍵):**
    ```
    ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr
    ```
*   **ダウンロードされたファイルのハッシュ値 (SHA256):** `a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2`
*   **不正なコマンド文字列:**
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

### 5. 推奨アクション

1.  **緊急対応 (Immediate Actions):**
    *   **攻撃元IPのブロック:** ファイアウォールやIPS/IDSにて攻撃元IP `43.155.21.198` からの通信をブロックします。
    *   **認証情報の変更:** ログに記載されているすべての成功したユーザー名（特に `root`）と関連するパスワードを直ちに、かつ安全性の高いものに変更します。
    *   **SSH公開鍵認証の確認と不正な鍵の削除:** すべてのユーザーの `~/.ssh/authorized_keys` ファイルの内容を確認し、上記のIoCで示された攻撃者の公開鍵が存在しないことを確認します。もし存在する場合は、直ちに削除します。
    *   **マルウェアスキャンと検出されたファイルの隔離・削除:** システム全体を最新のマルウェア対策ソフトウェアでスキャンし、`a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2` のハッシュ値を持つファイルやその他の異常なファイルが検出された場合は、隔離または削除します。
    *   **システムフォレンジック調査:** ログに見られる行動がハニーポット上のものであるとしても、同様の攻撃が本番環境で発生した場合を想定し、システムイメージの取得、メモリダンプ、ログの網羅的な収集と分析を実施し、実際の侵害範囲と影響を特定します。

2.  **再発防止策 (Preventive Measures):**
    *   **SSH設定の強化:**
        *   パスワード認証を無効化し、公開鍵認証のみを許可します。
        *   `root` ユーザーのSSHログインを禁止します (`PermitRootLogin no`)。
        *   SSHポートを標準の22番以外に変更します。
        *   ログイン試行回数制限を設定します (`MaxAuthTries` など)。
        *   `sshd_config` にて`AllowUsers` や `DenyUsers` を適切に設定し、SSHアクセス可能なユーザーを制限します。
    *   **多要素認証 (MFA) の導入:** SSH接続にMFAを必須とします。
    *   **強固なパスワードポリシーの徹底:** すべてのシステムアカウントに対して、複雑で長いパスワードの使用を義務付け、定期的な変更を促します。
    *   **定期的な脆弱性診断とパッチ適用:** OSおよびアプリケーションの脆弱性を定期的に診断し、最新のセキュリティパッチを適用します。
    *   **ログ監視の強化:** SSHログインログ、認証ログ、コマンド実行ログなどを詳細に監視し、異常なアクセスパターンやコマンド実行を早期に検知できる体制を強化します。SIEMシステムなどへのログ連携を検討します。
    *   **セキュリティ教育:** 従業員に対するセキュリティ意識向上トレーニングを実施し、フィッシングやソーシャルエンジニアリングに対する防御力を高めます。