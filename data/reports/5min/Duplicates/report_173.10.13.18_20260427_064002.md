# SOC自動分析レポート: 173.10.13.18

**生成日時:** 2026-04-27 06:41:37

---

## SOCアナリストレポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `173.10.13.18` から、SSHサービスに対して継続的な攻撃が検知されました。
この攻撃は、まずSSHパスワード認証に対するブルートフォース/辞書攻撃を通じてシステムの認証情報を窃取し、ログインに成功した後に、永続的なアクセスを可能にするバックドア（SSH公開鍵）を設置することを目的としています。

**主要な攻撃フロー:**
1.  **初期偵察・認証情報窃取**: 複数のユーザー名とパスワードの組み合わせ（`dev:!dev`, `trans:trans`など）でSSHログインを試行。最終的に `root` ユーザーに対して、複数のパスワード（例: `123456Aa`, `Aa000000`, `Sp0rt`, `123456789a@`, `qaz123!@#`, `Aa12488261`, `3245gs5662d34`）でログインに成功しています。
2.  **永続化（Persistence）**: `root` ユーザーとしてログイン成功後、攻撃者は以下のコマンドを実行しています。
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリの不変属性（immutable attribute）を解除し、変更可能にしようと試みています。`lockr` コマンドは標準的ではありません。
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: 既存の `.ssh` ディレクトリを削除・再作成し、攻撃者自身のSSH公開鍵（コメント: `mdrfckr`）を `authorized_keys` ファイルに書き込むことで、パスワードなしで再ログインできるバックドアを確立しようとしています。
3.  **アクセス確認**: 鍵設置後、攻撃者は複数回にわたり `345gs5662d34` というユーザー名でのログインを試み、失敗しています。これは、設置したSSH鍵を使用した接続テストであった可能性が高いです。その後、`root:3245gs5662d34` でのログイン成功も複数回確認されています。

これらの攻撃は一貫して繰り返されており、自動化された攻撃ツールによるものと推測されます。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSHブルートフォース/辞書攻撃**: 大量の認証情報試行から、`root` アカウントに対するパスワードの総当たりまたは辞書攻撃が行われたと判断されます。
    *   **永続化メカニズムの確立**: 成功したSSHセッションを利用して、攻撃者自身のSSH公開鍵をシステムに設置することで、将来的なアクセス経路を確保しようとしています。
*   **使用ツール**:
    *   **自動化されたSSHクライアント**: 連続的な接続とコマンド実行パターンから、何らかの自動化されたスクリプトまたはツール（例: Hydra、Medusaなどのブルートフォースツール、またはカスタムスクリプト）が使用されている可能性が高いです。
    *   **一般的なLinuxコマンド**: `cd`, `rm`, `mkdir`, `echo`, `chmod`, `chattr` といった標準的なシェルコマンドが使用されています。`lockr` というコマンドは一般的ではなく、ハニーポット環境でのエミュレーションまたは攻撃者の誤った期待を示す可能性があります。
    *   **SSH公開鍵**: 攻撃者は自身のSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を利用して、バックドアを設置しようとしています。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**
1.  **最高権限でのログイン成功**: 攻撃者は `root` ユーザーとしてシステムへのログインに複数回成功しています。`root` 権限はシステム上の最高権限であり、実システムであれば攻撃者による完全な制御（データの窃取、改ざん、システムの破壊、他のシステムへの横展開など）が可能になります。
2.  **永続的なアクセス経路の確立**: ログイン成功後、攻撃者はSSH公開鍵を設置することで、パスワード認証を経ずに長期的なアクセスを確保しようとしています。これは、システムの掌握と継続的な悪用を目的とした典型的な永続化戦略であり、一度侵入が許されると検出・排除が困難になるため、非常に深刻な脅威となります。
3.  **攻撃の自動化と継続性**: 複数の異なるパスワードで `root` ログインに成功し、同様のバックドア設置コマンドを短時間で複数回繰り返していることから、この攻撃は自動化されており、組織的な攻撃や大規模なボットネットの一部である可能性が高いです。これは単発の攻撃ではなく、継続的な脅威に晒されていることを示唆します。
4.  **攻撃者の悪意**: 公開鍵のコメントに「mdrfckr」という攻撃的な文字列が含まれていることから、攻撃者の明確な悪意と意図的な侵害の目的が読み取れます。

### 4. 推奨アクション

このログはハニーポット (Cowrie) のものであるため、実際のシステム侵害は発生していませんが、実システムが同様の攻撃を受けた場合の対応として以下の行動を強く推奨します。

1.  **攻撃元IPの即時ブロック**:
    *   攻撃元IPアドレス `173.10.13.18` を社内のファイアウォール、IDS/IPS、または各サーバのホストベースファイアウォール（iptables/firewalld）でブロックし、今後の攻撃を遮断します。
2.  **SSH認証情報の緊急見直しと強化**:
    *   **パスワード変更**: SSHアクセスを持つ全てのシステムにおいて、`root` ユーザーを含む全てのアカウントのパスワードを直ちに、かつ強力なものに変更します。特にログに記録されたパスワードが他のシステムで使い回されていないか確認し、使用されている場合は即座に変更します。
    *   **root直接ログインの無効化**: SSHサービス設定（`/etc/ssh/sshd_config`）において `PermitRootLogin no` を設定し、`root` ユーザーの直接SSHログインを無効化します。必要な場合は、一般ユーザーでログイン後に `su` または `sudo` を使用する運用に切り替えます。
    *   **SSH鍵認証への移行**: パスワード認証を完全に無効化し、強力なSSH鍵認証への移行を検討します。鍵の生成、配布、管理プロセスを厳格化し、定期的な鍵のローテーションを実施します。
    *   **ブルートフォース対策**: Fail2ban、sshd_configの `MaxAuthAttempts` 設定、SSHサービスへのレートリミット設定などを導入し、総当たり攻撃への耐性を強化します。
3.  **不審なSSH公開鍵の確認と削除**:
    *   全てのLinux/Unixサーバ（特に公開SSHサービスを提供しているサーバ）において、`root` ユーザーおよび他の特権ユーザーの `~/.ssh/authorized_keys` ファイルを緊急で監査し、ログに記録された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が存在しないか確認します。存在する場合は、即座に削除し、システムへの再侵入経路を断ちます。
    *   同時に、`~/.ssh` ディレクトリのパーミッションが適切であるか (`chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/authorized_keys`) も確認します。
4.  **システムログのフォレンジック調査**:
    *   対象システムにおけるSSH認証ログ（`/var/log/auth.log` や `journalctl` など）や、プロセス実行ログ、ネットワーク接続ログなどを詳細に調査し、攻撃者が他にどのような活動を行ったか、追加のマルウェアがダウンロードされていないか、他のシステムへの横展開が試みられていないかを確認します。
5.  **セキュリティ監視の強化**:
    *   SSHログインの失敗および成功イベント、`root` ユーザーによる不審なコマンド実行、`.ssh` ディレクトリへの変更などを検知するアラート設定をSIEM（Security Information and Event Management）などのセキュリティ監視システムで強化します。
    *   異常なアクセスパターン（例: 通常と異なる時間帯からのログイン、短時間での多発的なログイン失敗など）を早期に発見できる体制を構築します。
6.  **インシデントレスポンス計画の確認と訓練**:
    *   今回の事案を受けて、組織のインシデントレスポンス計画が現状の脅威に対応できるかを確認し、必要に応じて更新します。関連部署との連携体制や責任範囲を明確化し、定期的な訓練を実施します。