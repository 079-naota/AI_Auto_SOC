# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 19:12:07

---

## セキュリティインシデント分析レポート

**報告日時:** 2026-04-25T04:50:00Z
**攻撃元IP:** 185.216.119.134
**対象システム:** SSHハニーポット (Cowrie)

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `185.216.119.134` から、SSHハニーポットに対し、継続的なブルートフォース攻撃および辞書攻撃が実行されました。この攻撃は、複数の異なるユーザー名とパスワードの組み合わせを試行し、特に管理者権限である `root` ユーザーに対するログインを狙っています。

攻撃の主要な目的は、SSHサービスを介してシステムの管理者権限（`root`）を取得し、その後、システムへの永続的なアクセス経路を確立することにあると推測されます。具体的には、ログイン成功後、攻撃者は自身のSSH公開鍵をターゲットシステムの `root` ユーザーの `~/.ssh/authorized_keys` ファイルに追加することで、パスワードなしでの再ログインを可能にするバックドアを設置しようと試みました。これにより、認証情報を再利用することなく、いつでもシステムにアクセスできる状態を作り出すことを目指しています。

---

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **ブルートフォース攻撃 / 辞書攻撃:** 短時間で大量のユーザー名とパスワードの組み合わせ（例: `zabbix:test`, `john:1234567890`, `root:123.com.`, `root:nPSpP4PBW0` など）を試行しており、これは自動化されたブルートフォースツールや辞書攻撃ツールによる典型的な挙動です。
    *   **永続化 (Persistence):** `root` ユーザーとしてログイン成功後、`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~` というコマンドを実行し、自らのSSH公開鍵を `authorized_keys` ファイルに追加しようとしました。これは、システムへの恒久的なアクセス権を確立するための一般的な「永続化」の手法です。
    *   **防御回避 (Defense Evasion):** `cd ~; chattr -ia .ssh; lockr -ia .ssh` というコマンドを複数回試行していますが、ハニーポット上では失敗しています。これらのコマンドは、通常、ファイル属性を変更して `authorized_keys` ファイルの変更や削除を困難にし、設置したバックドアを保護するための防御回避の試みであると推測されます。

*   **使用ツール:**
    *   **自動化されたSSHクライアント / ブルートフォースツール:** ログのタイムスタンプを見ると、ログイン試行からコマンド実行までが非常に迅速であり、手動操作ではなく、`hydra`, `medusa`, `ncrack` などのSSHログイン試行を自動化するツールやカスタムスクリプトが使用されている可能性が高いです。
    *   **SSH鍵:** 攻撃者が `authorized_keys` に追加しようとした公開鍵は `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` であり、コメント `mdrfckr` は特定のボットネットやマルウェアキャンペーンで用いられる特徴的な文字列である可能性があります。

---

### 3. 脅威レベルとその理由

*   **脅威レベル:** **高 (High)**

*   **理由:**
    1.  **管理者権限 (root) でのログイン成功試行:** 本ログはハニーポットのものであるため実際のシステム侵害には至っていませんが、もしこれが本番環境のシステムであれば、攻撃者はシステムの最高権限である `root` でのログインに複数回成功しています。これは、システム全体の制御を奪われる深刻なリスクを意味します。
    2.  **永続的なアクセス経路の確立試行:** 攻撃者はSSH公開鍵を `authorized_keys` に追加することで、パスワードなしでのアクセスを可能にするバックドアを設置しようとしました。これにより、長期的なシステムへのアクセスが可能となり、検知と対処が非常に困難になります。
    3.  **自動化された広範な攻撃:** ログイン試行の速度と多様なパスワード、一貫したコマンド実行パターンから、自動化された攻撃ツール（ボットネットの一部である可能性を含む）が使用されていることが強く示唆されます。このような攻撃は、さらなる脆弱性悪用やマルウェア配布の前段階となることが一般的です。
    4.  **防御回避の試み:** `chattr` コマンドによるファイル属性変更の試みは、攻撃者が設置したバックドアを隠蔽し、除去を困難にしようとする明確な意図を示しており、悪質性が高いと評価されます。

---

### 4. 推奨アクション

1.  **攻撃元IPアドレスの即時ブロック:**
    *   ファイアウォール、IDS/IPS、またはルーターのACL等で、攻撃元IPアドレス `185.216.119.134` からのすべての通信を直ちにブロックしてください。必要に応じて、当該IPアドレスが所属するCIDR範囲やAS（自律システム）からのトラフィックもブロック対象に含めることを検討してください。

2.  **SSHサービスのセキュリティ強化:**
    *   **`root` ユーザーのSSHログイン禁止:** すべてのシステムにおいて、`root` ユーザーによるSSHパスワードログインを無効化してください。
    *   **パスワード認証の制限:** 可能であれば、パスワード認証を無効化し、SSH鍵認証のみに限定してください。
    *   **強力なパスワードポリシーの適用:** すべてのユーザーに対して、複雑性、長さ、有効期限に関する強力なパスワードポリシーを強制し、定期的なパスワード変更を推奨してください。
    *   **多要素認証 (MFA) の導入:** SSH接続に多要素認証を導入し、セキュリティレベルを向上させてください。
    *   **アクセス元IPアドレスの制限:** SSH接続を許可するIPアドレスを、信頼できるネットワークからのものに限定するホワイトリスト方式を導入してください。
    *   **SSHポートの変更:** 標準ポート (22) 以外のポートを使用することも検討してください（ただし、これは検出を遅らせる効果はあるものの、根本的な解決策ではありません）。

3.  **SSH鍵認証設定の緊急監査とクリーンアップ:**
    *   すべてのLinux/Unix系システムにおいて、特に `root` ユーザーの `~/.ssh/authorized_keys` ファイルの内容を緊急で精査し、不正な公開鍵が追加されていないかを確認してください。
    *   本ログに示された攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が見つかった場合、直ちに削除し、関連するログ（認証ログ、コマンド履歴など）を詳細に調査して侵害の範囲を特定してください。
    *   `chattr` コマンドによって重要なファイルやディレクトリの属性が不正に変更されていないか (`lsattr -aR ~/.ssh` などで確認) を確認してください。

4.  **ログ監視の強化とアラート設定:**
    *   SSHログイン試行（成功・失敗問わず）、特に `root` ユーザーへのログイン試行、`authorized_keys` ファイルへの変更、および重要なシステムコマンドの実行（`rm`, `mkdir`, `echo`, `chattr` など）に関するログ監視を強化してください。
    *   これらのイベントに対して、リアルタイムのアラートを生成するようにSIEM (Security Information and Event Management) やログ管理システムを設定してください。

5.  **脅威インテリジェンスの活用:**
    *   攻撃元IPアドレス `185.216.119.134` と、攻撃者が追加しようとしたSSH公開鍵のハッシュ値、および公開鍵のコメント `mdrfckr` を脅威インテリジェンスプラットフォーム（VirusTotal, Shodan, AbuseIPDBなど）で検索し、既知の脅威アクターやボットネット、マルウェアキャンペーンに関連するかどうかを確認してください。これにより、攻撃の背景にある脅威グループや手法に関する追加情報を得られる可能性があります。

6.  **インシデントレスポンスプランの見直し:**
    *   このような管理者権限を狙ったブルートフォース攻撃に対するインシデントレスポンスプランが適切であるかを見直し、定期的な訓練を通じてチームの対応能力を向上させてください。