# SOC自動分析レポート: 103.117.56.152

**生成日時:** 2026-04-26 23:56:31

---

## SOCアナリストレポート

**報告日時:** 2026-04-26T07:36:31Z (ログ最終時刻に基づく)
**分析対象IP:** 103.117.56.152

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `103.117.56.152` から、当社のSSHサービスに対する不正アクセス試行が複数回確認されました。これは、主に辞書攻撃やブルートフォース攻撃を介して行われ、最終的に `root` ユーザーの認証情報が侵害され、ログインに成功しています。

ログイン成功後、攻撃者はシステムに永続的なアクセス経路を確立するため、自身のSSH公開鍵をターゲットの `.ssh/authorized_keys` ファイルに追加しようと試みています。これにより、以降はパスワードなしでシステムにアクセスできるバックドアを設置し、将来的な不正アクセスを容易にすることが目的と考えられます。

### 2. 推測される手法・使用ツール

*   **初期アクセス手法:**
    *   **ブルートフォース攻撃 / 辞書攻撃 (Brute-force / Dictionary Attack):** `testuser`, `bot`, `postgres`, `user1`, `steam`, `ubuntu`, `wang`, `oracle` といった一般的に使用されるユーザー名や、不明な文字列 (`345gs5662d34`) を用いて、多数のパスワードを繰り返し試行しています。特に `root` ユーザーへのログインを執拗に試みており、異なるパスワードで複数回ログインに成功しています。
*   **永続化手法 (Persistence):**
    *   ログイン成功後、攻撃者は以下のコマンドを順番に実行しています。
        1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリのファイル属性（不変属性や追加のみ属性など）を解除しようとしています。これは、ディレクトリ内のファイルを変更するための準備と考えられます。（`lockr` は標準的なコマンドではありませんが、`chattr` と同様の意図、またはタイプミスと推測されます。）
        2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`:
            *   既存の `.ssh` ディレクトリを削除し、再作成。
            *   攻撃者のSSH公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を `.ssh/authorized_keys` ファイルに追加。
            *   `.ssh` ディレクトリのパーミッションを設定し、所有者以外のアクセスを制限しています。

*   **使用ツール:**
    *   **SSHクライアント:** 不正なログイン試行とコマンド実行のために使用。これはHydraやMedusaなどのSSHブルートフォースツール、あるいはカスタムスクリプトの一部である可能性があります。
    *   **標準Linuxコマンド:** `cd`, `rm`, `mkdir`, `echo`, `chmod`, `chattr` などの一般的なシェルコマンド。

攻撃は一定の時間間隔で繰り返し行われており、異なるパスワードで複数回 `root` ログインに成功していることから、自動化された攻撃スクリプトやボットネットの一部である可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **最高権限の侵害:** `root` ユーザーの認証情報が侵害され、ログインに成功しているため、システムに対する完全な制御権が奪われた可能性があります。これは最も深刻なシステム侵害の一つです。
2.  **永続的なアクセス経路の確立:** 攻撃者が `authorized_keys` に自身の公開鍵を登録しようとしていることは、将来的にパスワードなしでシステムに再アクセスするためのバックドアを設置する意図を示しています。これにより、一度排除しても再侵入されるリスクが高まります。
3.  **自動化された攻撃:** 攻撃が繰り返し行われ、定型的なコマンドが実行されていることから、自動化された攻撃ボットによるものである可能性が高く、同様の攻撃が他のシステムにも展開されているか、または今後も継続される可能性があります。
4.  **潜在的な二次被害:** 攻撃者がシステムにアクセスした場合、機密情報の窃取、追加のマルウェア（ランサムウェア、マイニングマルウェアなど）のインストール、システムの破壊、他の内部システムへの横展開、外部への攻撃踏み台としての利用など、甚大な被害に繋がる可能性があります。

### 4. 推奨アクション

**緊急対応 (Immediate Actions):**

1.  **攻撃元IPのブロック:** 攻撃元IPアドレス `103.117.56.152` からのすべての通信（特にSSHポート22番）をファイアウォールまたはセキュリティグループで即座にブロックしてください。
2.  **認証情報の変更:** ログインに成功した `root` ユーザーのパスワードを、直ちに非常に複雑で推測困難なものに変更してください。
3.  **バックドアの確認と削除:**
    *   `root` ユーザーのホームディレクトリ (`/root/.ssh/authorized_keys`) を確認し、不正なSSH公開鍵（上記ログに記載された`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`を含む）が登録されていないか確認し、存在する場合は直ちに削除してください。
    *   `.ssh` ディレクトリとその内容のパーミッションが正しく設定されているか（通常は`drwx------`、`authorized_keys`は`rw-------`）確認し、不正な変更がないか検証してください。
    *   `chattr` コマンドが使用された可能性を考慮し、`.ssh` ディレクトリやその他重要なシステムファイルに不変属性などの特殊な属性が付与されていないか確認してください（`lsattr -aR ~/.ssh`など）。
4.  **侵害範囲の特定 (Forensic Investigation):**
    *   システムが完全に侵害された可能性を前提に、詳細なフォレンジック調査を開始し、不正な活動の全容を把握してください。
    *   不審なプロセス、設定変更、ファイル、ネットワーク接続がないか、システムログ、アプリケーションログ、SSHログなどを詳細に確認してください。
    *   rootkitなどのマルウェアがインストールされていないかスキャンしてください。
5.  **影響範囲の確認:** 当該システムが他のシステムと連携している場合、横展開の可能性も考慮し、関連システムへの影響がないか確認してください。

**予防的対応 (Preventative Measures):**

1.  **SSHアクセス制限の強化:**
    *   SSHサービスへのアクセスを、特定の信頼されたIPアドレスまたはVPN経由のみに制限してください。
    *   可能な限り、SSHのパスワード認証を無効化し、堅牢な公開鍵認証のみを許可する運用に切り替えてください。
    *   多要素認証 (MFA) の導入を検討してください。
    *   `root` ユーザーによるSSH直接ログインを禁止し、一般ユーザーでログイン後に `sudo` を使用する運用を徹底してください。
    *   SSHポートを標準の22番から変更する（あくまで追加的な対策であり、根本的なセキュリティ強化ではありません）。
2.  **パスワードポリシーの強化:** すべてのシステムユーザーに対して、複雑で定期的に変更されるパスワードポリシーを強制してください。
3.  **ブルートフォース対策:** Fail2Banなどのツールを導入し、不正なログイン試行を自動的に検出し、一定回数失敗したIPアドレスを一時的または恒久的にブロックする仕組みを導入してください。
4.  **監視とアラートの強化:**
    *   SIEM (Security Information and Event Management) システムやIDS/IPS (Intrusion Detection/Prevention System) を導入・強化し、SSHへの異常なログイン試行やログイン成功、重要なファイル（`.ssh/authorized_keys`など）への変更、不審なコマンド実行などをリアルタイムで監視し、アラートを発する体制を構築してください。
    *   脅威インテリジェンスを活用し、攻撃元IPアドレスをブロックリストに追加し、今後の監視に役立ててください。
5.  **定期的な監査:** SSH設定、ユーザーアカウント、およびシステムログの定期的なセキュリティ監査を実施してください。
6.  **システムのパッチ適用:** OSおよびすべてのソフトウェアを最新の状態に保ち、既知の脆弱性を悪用されるリスクを低減してください。

---
**免責事項:** このレポートは提供されたログデータに基づいて作成されたものです。実際のシステムの状態は、詳細な調査によってのみ確認できます。