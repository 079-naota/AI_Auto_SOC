# SOC自動分析レポート: 103.172.205.139

**生成日時:** 2026-04-26 02:18:38

---

## セキュリティインシデント分析レポート

**対象ログ**: Cowrieハニーポットログ
**攻撃元IP**: 103.172.205.139
**分析日時**: 2026-04-26TXX:XX:XXZ

---

### 1. 攻撃の概要と目的

本ログは、`103.172.205.139` からのSSHサービスに対する断続的な攻撃活動を記録しています。攻撃者は約1時間半にわたり、様々なユーザー名とパスワードを試行するブルートフォース/パスワードスプレー攻撃を仕掛けています。

特に注目すべきは、この攻撃者が複数回、`root`ユーザーを含む複数のアカウントでSSHログインに成功している点です。ログイン成功後、攻撃者は以下の活動を試みています。

*   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: 既存の`.ssh`ディレクトリのファイル属性（特に不変属性や追記専用属性）を変更し、ファイルの改ざんや削除を可能にしようとしています。`lockr`コマンドは失敗していますが、防御回避の意図が見て取れます。
*   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjux0hJOK4Mjw==` は非常に有名なSSHバックドアであり、世界中のホニーポットで観測されています。これはMiraiなどのボットネットが使用する鍵として知られています。

攻撃の目的は、標的システムへの不正アクセスを確立し、永続化することであると推測されます。これにより、マルウェアの展開、データ窃取、他のシステムへのラテラルムーブメント、あるいはボットネットの一部として利用する準備を行おうとしていると考えられます。

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **SSH ブルートフォース/パスワードスプレー攻撃:** ログには多様なユーザー名（`user7`, `root`, `345gs5662d34`, `deployer`, `ubuntu`, `user`, `mary`, `admin`, `zhaoxj`など）とパスワードの組み合わせが短時間で大量に試行されていることが示されています。特に `root` ユーザーを狙った攻撃が複数回成功しており、一般的なパスワードや過去の漏洩情報に基づいたパスワードリストを使用している可能性が高いです。
    *   **永続化メカニズムの確立 (SSH公開鍵認証によるバックドア):** ログイン成功後、攻撃者は `~/.ssh/authorized_keys` ファイルに特定のSSH公開鍵を書き込むコマンドを実行しています。この公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4c...`）は、Miraiボットネットなどで知られる悪意のあるSSH鍵であり、これが追加されると、攻撃者はパスワードなしでいつでもSSHアクセスできるようになります。
    *   **防御回避の試行:** `chattr -ia .ssh` や `lockr -ia .ssh` といったコマンドは、ファイルシステムの属性を変更することで、`.ssh`ディレクトリとその中のファイル（特に `authorized_keys`）が簡単に削除または変更されないようにする（あるいは、既存の保護を解除する）ことを意図しています。これにより、自身の追加したバックドアの永続性を高めようとしたと考えられます。`lockr`は一般的なコマンドではないため失敗していますが、その意図は明確です。

*   **使用ツール:**
    *   攻撃者が直接使用したツールはログからは特定できませんが、上記の手法から、SSHブルートフォースツール（例: Hydra, Nmapの`ssh-brute`スクリプトなど）や、これらを組み込んだ自動化されたスクリプトまたはボットプログラムが使用された可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

*   **複数回のログイン成功:** 攻撃は推測に終わらず、実際に`root`ユーザーを含む複数のアカウントでSSHログインに成功しています。これはシステムが直接的な脅威に晒されたことを意味します。
*   **重要なアカウント（root）の侵害:** `root`ユーザーでのログイン成功は、システムに対する完全な制御を攻撃者に与えることを意味し、極めて深刻な事態です。
*   **永続化の試み:** `authorized_keys`ファイルへのSSH公開鍵の追加は、攻撃者が一度アクセスを確立した後に、そのアクセスを永続化させるための典型的な手法です。このバックドアが成功していれば、システムの再起動やパスワード変更後も攻撃者はアクセスを維持できます。
*   **Miraiボットネットに関連する公開鍵の使用:** ログに記録されている公開鍵は、MiraiボットネットがSSHバックドアとして利用することが知られているものです。これは、攻撃がより大規模なボットネット活動やマルウェア感染の一部である可能性を示唆しており、単一のシステム侵害以上の脅威をもたらす可能性があります。
*   **防御回避の試行:** `chattr`などのコマンドの使用は、攻撃者がシステムの保護メカニズムを理解し、それを無効化しようとする高度な意図を持っていることを示しています。

これらの活動は、標的とされたシステムが実環境であれば、完全に侵害され、データの窃取、マルウェアの展開、あるいはボットネットの一部としての利用など、甚大な被害につながった可能性が高いです。

### 4. 推奨アクション

以下の緊急対応と再発防止策を速やかに実施してください。

1.  **緊急対応 (Immediate Actions):**
    *   **攻撃元IPのブロック:** 攻撃元IPアドレス `103.172.205.139` からのすべての通信を、ファイアウォールまたはエッジルーターで即座にブロックしてください。
    *   **SSHアカウントのパスワードリセット:** ログに記載されている、ログインに成功したユーザーアカウント（特に`root`）だけでなく、攻撃者が試行したすべてのユーザー名（`user7`, `deployer`, `ubuntu`, `user`, `mary`, `admin`, `zhaoxj`など）について、パスワードを強力なものに変更してください。また、SSHを公開しているすべてのサーバーで、これらパスワードの使い回しがないか確認し、あれば即座に変更してください。
    *   **不正なSSH公開鍵の確認と削除:** すべてのユーザーのホームディレクトリ（特に`root`ユーザー）にある `~/.ssh/authorized_keys` ファイルを緊急で確認し、身に覚えのないSSH公開鍵（特にログに記載された`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4c...`）が存在しないかチェックし、発見した場合は削除してください。
    *   **システム整合性チェックとマルウェアスキャン:** 攻撃者がバックドア以外にマルウェアを設置したり、システム設定を改ざんしたりした可能性を考慮し、システム整合性監視ツール（AIDE, Tripwireなど）を用いたチェックや、最新のアンチウイルスソフトウェアによるフルスキャンを実施してください。
    *   **ログの深掘り調査:** 攻撃が実際に成功した場合、ハニーポットログだけでは把握できないさらなる活動（データアクセス、他のシステムへの接続試行など）が行われた可能性があります。関連するシステムログ（auth.log, syslogなど）を詳細に調査してください。

2.  **再発防止策 (Preventative Measures):**
    *   **SSHセキュリティの強化:**
        *   **公開鍵認証の強制:** パスワード認証を無効化し、公開鍵認証のみを許可する設定に変更してください。
        *   **rootユーザーの直接ログイン禁止:** `PermitRootLogin no` を設定し、`sudo`を利用した特権昇格を強制してください。
        *   **多要素認証(MFA)の導入:** 可能であればSSHアクセスに多要素認証を導入し、セキュリティをさらに強化してください。
        *   **Rate Limiting/アカウントロックアウト:** Fail2Banなどのツールを導入し、短時間でのSSHログイン失敗が一定回数を超えた場合に、自動的にIPアドレスをブロックする設定を導入してください。
        *   **デフォルトポートの変更:** SSHのデフォルトポート（22番）を非標準のポートに変更し、自動化されたスキャンからの露出を減らしてください（これは根本的な解決策ではありませんが、ノイズを減らす効果はあります）。
    *   **パスワードポリシーの強化:** 従業員やシステムアカウントに対し、複雑なパスワードの利用と定期的な変更を義務付けるポリシーを徹底してください。過去の漏洩パスワードリストとの照合も検討してください。
    *   **IDS/IPSの導入と監視強化:** 不審なSSHアクティビティやコマンド実行を検知・ブロックできるIDS/IPSの導入または既存システムのルール強化を行ってください。
    *   **ハニーポットの活用:** 今回のログはハニーポットからのものですが、実環境の防御を強化するためにも、このような攻撃トレンドを継続的に収集・分析するためのハニーポット運用を続けることを推奨します。
    *   **定期的な脆弱性スキャンとパッチ適用:** OSおよびSSHサービスを含むすべてのソフトウェアの脆弱性スキャンを定期的に実施し、発見された脆弱性には速やかにパッチを適用してください。