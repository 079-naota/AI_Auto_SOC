# SOC自動分析レポート: 103.132.243.250

**生成日時:** 2026-04-26 15:03:38

---

## SOCレポート：SSHブルートフォース攻撃および永続化の試み

### 1. 攻撃の概要と目的

本レポートは、攻撃元IPアドレス `103.132.243.250` からSSHサービスに対する一連の攻撃を分析したものです。ログはCowrieハニーポットにより記録されました。

攻撃者はまず、`oracle`、`mani`、`ftpuser` などの一般的なユーザー名や、`oracle09!`、`mani`、`test123` といった推測されやすいパスワードを用いたブルートフォース攻撃を開始しました。その後、`root` ユーザーに対するブルートフォース攻撃に切り替え、複数のパスワード（`135792468`、`abcdefgh`、`qazwsxedc123`、`P@ssw0rd6`、`Admin88888888`、`Gp123456`など）でログインに成功しました。

ログイン成功後、攻撃者は `chattr` コマンドで `.ssh` ディレクトリの属性変更を試みた後、以下のコマンドを実行し、自身のSSH公開鍵を `~/.ssh/authorized_keys` ファイルに追加して永続的なアクセス経路を確立しようとしました。

`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

この一連の行動の主な目的は、認証情報を窃取し、特権アカウントでの不正ログインを成功させた上で、SSH鍵認証によるバックドアを仕掛けることで、検出後も継続的にシステムへアクセスできる状態を維持することです。

### 2. 推測される手法・使用ツール

*   **ブルートフォース/辞書攻撃:** 複数のユーザー名とパスワードの組み合わせを短時間に大量に試行していることから、自動化されたブルートフォース攻撃または辞書攻撃ツールが使用されていると推測されます。
*   **永続化メカニズム:** ログイン成功後、`~/.ssh/authorized_keys` に攻撃者の公開鍵を追加する手法は、SSHサービスを持つシステムへの不正アクセスにおける典型的な永続化手法です。これにより、攻撃者はパスワードを知らなくても、自身の秘密鍵を使ってシステムへ再ログインが可能になります。
*   **自動化された攻撃スクリプト/ボット:** ログイン成功時に決まったコマンド（`chattr`の試行と公開鍵の配置）を繰り返し実行していることから、攻撃者は手動ではなく、あらかじめ用意されたスクリプトやボットネットの一部として活動している可能性が高いです。`chattr`コマンドが一部失敗しているのは、攻撃ツールが対象環境（ハニーポット）のコマンドセットを完全に認識していないためと考えられます。
*   **SSH公開鍵:** `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` この公開鍵は、攻撃者が将来的なアクセスに利用する認証情報であり、コメントの `mdrfckr` は攻撃者の識別子やキャンペーン名である可能性があります。

### 3. 脅威レベルとその理由

**脅威レベル：高 (High)**

**理由:**
1.  **rootアカウントへのログイン成功:** 攻撃者がシステム内で最も高い権限を持つ `root` アカウントの認証情報（パスワード）を特定できたことは、極めて深刻な脅威です。これにより、システムに対する完全な制御権を獲得するリスクがありました。
2.  **永続的なアクセス経路の確立試み:** ログイン成功後、速やかにSSH公開鍵を `authorized_keys` に配置し、パスワード認証なしでアクセスできるバックドアを確立しようとしました。これは、単一の侵入で終わらず、将来的な継続的アクセスを目的としていることを示しています。
3.  **自動化された広範な攻撃の可能性:** 攻撃パターンから、これは特定のターゲットを狙ったものではなく、インターネット上の脆弱なSSHサーバーを探索する自動化された広範なスキャン活動の一部である可能性が高いです。本件で観測された攻撃元IPアドレスが他の組織資産や業界で同様の攻撃を行っている可能性があります。
4.  **複数の異なるパスワードでの成功:** 攻撃ツールが複数の脆弱な `root` パスワードを発見したことは、辞書攻撃の有効性を示唆しており、他のシステムに対しても同様のリスクがあることを意味します。

### 4. 推奨アクション

この攻撃はハニーポットで観測されたものですが、もし実環境で発生したと仮定した場合、以下の緊急対応と予防策を推奨します。

#### 緊急対応 (Immediate Actions)

1.  **攻撃元IPアドレスのブロック:** 攻撃元IPアドレス `103.132.243.250` からのSSH接続を、ファイアウォールやIDS/IPSで即座にブロックします。
2.  **パスワードのリセット:** 攻撃者がログインに成功した `root` アカウントで使用されていたパスワード（`135792468`、`abcdefgh`、`qazwsxedc123`、`P@ssw0rd6`、`Admin88888888`、`Gp123456`、`3245gs5662d34` など）が他のシステムやアカウントで使われていないか確認し、使用されている場合は直ちに強力なパスワードにリセットします。
3.  **不正なSSH公開鍵の削除:** すべてのシステムで、各ユーザーの `~/.ssh/authorized_keys` ファイルを確認し、攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、存在する場合は削除します。
4.  **システムへの侵入調査:** 不審なファイル、プロセス、ネットワーク接続がないか、システム全体のマルウェアスキャンおよびフォレンジック調査を実施します。

#### 予防策 (Preventive Measures)

1.  **SSHセキュリティ強化:**
    *   **パスワードポリシーの強化:** すべてのユーザー（特に `root`）に対し、複雑で推測されにくいパスワードを強制します。定期的なパスワード変更も検討します。
    *   **root直接ログインの禁止:** `sshd_config` で `PermitRootLogin no` を設定し、`root` ユーザーの直接ログインを禁止し、`sudo` を経由したアクセスに限定します。
    *   **鍵認証の強制:** 可能であれば、パスワード認証を無効にし、SSH鍵認証のみを許可します。
    *   **多要素認証 (MFA) の導入:** SSH接続にMFAを導入し、セキュリティを強化します。
    *   **ポート変更:** SSHのデフォルトポート (22番) を変更し、一般的なスキャンからの可視性を低減します。
    *   **Fail2banなどの導入:** ブルートフォース攻撃を自動的に検知・遮断するツール (例: Fail2ban) を導入します。
    *   **アクセス元IP制限:** SSHアクセスを信頼できるIPアドレス範囲に制限します。
2.  **アカウント管理:**
    *   未使用アカウントの削除、または無効化。
    *   デフォルトアカウントのユーザー名変更を検討します。
3.  **ログ監視の強化:**
    *   SSHログインログ（成功・失敗両方）の監視を強化し、不審なログイン試行や成功を早期に検知できる体制を確立します。
    *   `authorized_keys` ファイルなど、システム設定ファイルに対する不正な変更を検知するファイル整合性監視 (FIM) ツールを導入します。
4.  **脅威インテリジェンスの活用:**
    *   今回の攻撃で使用されたSSH公開鍵 (`mdrfckr`) や攻撃元IPアドレスを脅威インテリジェンスプラットフォームに登録・照会し、既知の攻撃キャンペーンやTTPsとの関連性を継続的に調査します。
5.  **定期的な脆弱性診断とパッチ適用:**
    *   システムやアプリケーションの脆弱性診断を定期的に実施し、発見された脆弱性には速やかにパッチを適用します。