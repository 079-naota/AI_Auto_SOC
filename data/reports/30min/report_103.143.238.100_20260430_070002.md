# SOC自動分析レポート: 103.143.238.100

**生成日時:** 2026-04-30 07:00:02

---

## SOC分析レポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `103.143.238.100` から、SSHサービスに対するブルートフォース攻撃が繰り返し行われました。攻撃者は複数の簡易なパスワード (`admin1234`, `3245gs5662d34`, `admin123#!`, `admin_!@#`, `server01`) を使用して `root` ユーザーとして合計4回ログインに成功しています。

ログイン成功後、攻撃者は以下の行動を繰り返し実行しています。
1.  ホームディレクトリ内の `.ssh` ディレクトリの属性を変更（`chattr -ia .ssh; lockr -ia .ssh`）し、変更可能な状態にする。`lockr` は誤記または未知のコマンドの可能性があります。
2.  既存の `.ssh` ディレクトリを削除し、再作成。
3.  `~/.ssh/authorized_keys` ファイルに攻撃者自身のSSH公開鍵を追加し、永続的なアクセス経路を確立。
4.  特定のセカンドペイロード（SHA256ハッシュ: `a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2`）を複数回ダウンロードしようとしている。

これらの行動から、攻撃の主な目的は、**脆弱なSSHパスワードを持つシステムを侵害し、永続的なアクセス手段（バックドア）を確立した上で、マルウェア（セカンドペイロード）を導入してシステムを乗っ取り、その計算資源やネットワーク資源を悪用すること**であると推測されます。

### 2. 推測される手法・使用ツール

*   **初期侵入**: SSHに対する辞書攻撃またはブルートフォース攻撃。`root` ユーザーと一般的なパスワードリストを組み合わせて自動化されたツールが使用された可能性が高いです。
*   **永続化**:
    *   `~/.ssh/authorized_keys` ファイルへの攻撃者自身のSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) の追加。これにより、パスワード認証なしでSSH接続が可能になります。
    *   `chattr -ia .ssh` コマンドは、通常、ファイルやディレクトリの不変属性（`i`）や追記のみ属性（`a`）を無効にし、改ざん防止機能を解除する目的で使用されます。これにより、`authorized_keys` の変更や削除が可能になります。
*   **セカンダリペイロードの展開**: ログイン後、継続的に特定のマルウェアファイルをダウンロードしようとしています。これは、システムの完全な制御を奪い、悪用するためのダウンローダーまたはマルウェア本体である可能性が高いです。

**ファイルダウンロード検知（セカンドペイロード）の意図の推測**:
ダウンロードされたペイロード（ハッシュ: `a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2`）の取得元URLは不明ですが、攻撃者の行動履歴から、このペイロードは侵害されたシステムを悪用するためのマルウェアであると強く推測されます。
一般的なSSHブルートフォース攻撃の後に続くペイロードの目的としては、以下のものが考えられます。

*   **仮想通貨マイニングスクリプト/バイナリ**: 侵害されたシステムのCPUリソースを不正に利用し、仮想通貨をマイニングする目的。これにより、システムのパフォーマンス低下や電力消費増大を引き起こします。
*   **DDoSボットネットクライアント**: システムをDDoS攻撃のボットとして利用し、他の標的への攻撃に参加させる目的。これにより、システムのネットワーク帯域が不正に消費されます。
*   **バックドア/コマンド＆コントロール（C2）クライアント**: さらなるコマンドを受け取り、他のシステムへの攻撃の中継点としたり、機密情報を窃取したりする目的。

これらのペイロードは、攻撃者がシステムの永続的な制御を確立した後で、そのリソースを最大限に悪用するために導入されます。

### 3. 脅威レベルとその理由

*   **脅威レベル**: **高 (High)**
*   **理由**:
    *   **複数回の侵入成功**: 攻撃者が `root` ユーザーとしてシステムに複数回ログインを成功させており、ハニーポットが実システムであった場合、完全に制御を奪われている状態です。
    *   **永続的なアクセス確立**: SSH公開鍵を設置することで、攻撃者はパスワード認証なしでいつでもシステムに再侵入できるバックドアを構築しています。これにより、一度隔離されても容易に再侵入されるリスクがあります。
    *   **マルウェア導入の試み**: システムの資源を悪用するためのセカンドペイロードのダウンロードが繰り返し試みられています。これが実行されていれば、システムは仮想通貨マイニングやDDoS攻撃の踏み台など、不正な活動に悪用される可能性があります。
    *   **広範な影響の可能性**: 侵害されたシステムがボットネットの一部になった場合、組織のネットワークリソースの悪用だけでなく、外部への攻撃元となることで組織の評判や信頼性にも悪影響を及ぼす可能性があります。

### 4. 抽出されたIoC（Indicators of Compromise）

*   **攻撃元IPアドレス**: `103.143.238.100`
*   **不正に利用されたユーザー名**: `root`
*   **不正に利用されたパスワード**: `admin1234`, `3245gs5662d34`, `admin123#!`, `admin_!@#`, `server01`
*   **攻撃者が設置したSSH公開鍵**:
    *   `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`
    *   コメント: `mdrfckr`
*   **ダウンロードされたセカンドペイロードのSHA256ハッシュ**: `a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2`
*   **攻撃者が実行したコマンド**:
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

### 5. 推奨アクション

1.  **即時対応（検知時）**:
    *   **攻撃元IPのブロック**: ファイアウォールやIPS/IDSにて、攻撃元IPアドレス `103.143.238.100` からのすべての通信を即座にブロックする。
    *   **侵害されたシステムの特定と隔離**: もしこれがハニーポットではなく実システムであった場合、当該システムをネットワークから直ちに隔離し、さらなる被害拡大を阻止する。
    *   **パスワードのリセット**: 影響を受けた可能性のあるすべてのシステムで、`root` ユーザーを含むすべてのシステムアカウントのパスワードを、複雑で強力なものに強制的にリセットする。上記IoCに含まれるパスワードは、他のシステムでも使用されていないか確認する。
    *   **不正なSSH公開鍵の削除**: 侵害されたシステム上の `~/.ssh/authorized_keys` ファイル（および他のユーザーの類似ファイル）を検査し、上記の攻撃者による公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を含む不正なエントリを削除する。
    *   **マルウェア分析**: ダウンロードされたセカンドペイロードのハッシュ値 `a8460f446be540410004b1a8db4083773fa46f7fe76fa84219c93daa1669f8f2` を基に、サンドボックス環境で詳細なマルウェア分析を実施し、その機能と影響を特定する。
    *   **フォレンジック調査**: 侵害の深さ、影響範囲、攻撃者の他の活動を特定するため、詳細なフォレンジック調査を実施する。

2.  **予防策・再発防止策**:
    *   **SSH設定の強化**:
        *   `PermitRootLogin no` を設定し、`root` ユーザーのSSH直接ログインを禁止する。
        *   パスワード認証を無効にし、公開鍵認証のみを許可する (`PasswordAuthentication no`)。
        *   鍵認証を利用する場合は、強固なパスフレーズを持つ鍵の使用を義務付け、適切なファイルパーミッション (例: `~/.ssh` は 700, `authorized_keys` は 600) を徹底する。
        *   可能な場合は多要素認証 (MFA) をSSHログインに導入する。
        *   SSHサービスを標準の22番ポートから変更し、一般的なスキャンから隠蔽する (セキュリティバイオクソリティではあるが、ノイズは減る)。
    *   **強力なパスワードポリシーの徹底**: すべてのシステムアカウントに対し、複雑なパスワード（大文字、小文字、数字、記号を含む長い文字列）を義務付け、定期的な変更を促す。パスワード管理ツールや集中認証システムの導入を検討する。
    *   **自動防御システムの導入**: Fail2banなどのツールを導入し、不正なログイン試行を検知・ブロックする。
    *   **システムの定期的な更新とパッチ適用**: OSおよびすべてのソフトウェアを最新の状態に保ち、既知の脆弱性を悪用されるリスクを低減する。
    *   **セキュリティ監視の強化**: SIEM (Security Information and Event Management) や EDR (Endpoint Detection and Response) ソリューションを導入し、SSHログイン、ファイルシステム変更、プロセスの起動、ネットワーク通信など、システム上の異常な活動をリアルタイムで監視・検知する体制を構築する。
    *   **不要なサービスの停止**: 外部に公開する必要のないサービスは停止し、アタックサーフェスを最小化する。
    *   **従業員のセキュリティ意識向上**: 定期的なセキュリティトレーニングを実施し、フィッシング、パスワード管理、不審な活動の報告などに関する従業員の意識を高める。