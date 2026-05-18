# SOC自動分析レポート: 190.244.39.232

**生成日時:** 2026-04-26 11:43:55

---

## SOCアナリストレポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `190.244.39.232` から、本システム（Cowrieハニーポット）のSSHサービスに対し、複数のユーザー名とパスワードを試行するブルートフォース/辞書攻撃が継続的に観測されました。
攻撃は特に `root` ユーザーに対する執拗な試行が特徴で、複数回の成功ログインが確認されています。

この攻撃の主な目的は以下の通りと推測されます。

1.  **システムへの不正アクセスと完全な制御権の奪取**: `root` ユーザーでのログイン成功を通じて、システムの最高権限を掌握すること。
2.  **永続的なアクセス経路の確立**: ログイン成功後、自身のSSH公開鍵を `root` ユーザーの `~/.ssh/authorized_keys` に追加することで、パスワード認証を回避し、将来にわたって継続的にシステムへアクセス可能なバックドアを確立すること。
3.  **さらなる攻撃の足がかり**: 確立されたアクセスを用いて、マルウェアの展開、データの窃取、他のシステムへの横展開、またはボットネットへの参加など、より広範な悪意ある活動を行うための基盤とすること。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース/辞書攻撃 (Credential Stuffing)**: `odoo`, `root`, `345gs5662d34`, `user0`, `shiv`, `oracle`, `ovpn`, `windows` など、様々なユーザー名と複数の一般的なパスワード (`odoo2026!`, `135792468`, `abcdefgh`, `Aa112211.`, `Gp123456`, `nPSpP4PBW0`, `3245gs5662d34`, `123456`, `shiv123`, `oracle09!`, `ovpn`, `password`) を短時間で繰り返し試行しています。これは自動化された辞書攻撃の典型的な挙動です。
    *   **永続化 (Persistence)**: `root` ユーザーとしてログインに成功した後、`cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~` というコマンドを実行し、攻撃者のSSH公開鍵（コメント `mdrfckr`）を `authorized_keys` ファイルに追加しようとしています。これは、システムへの将来的なアクセスを確保するための典型的な永続化手法です。
    *   **痕跡改ざん/隠蔽の試み**: `cd ~; chattr -ia .ssh; lockr -ia .ssh` というコマンドも試行されています。`chattr -ia .ssh` はファイルシステム属性を変更し、`authorized_keys` などの重要ファイルが変更・削除されないように保護する不変属性 (`i`) や追加のみ属性 (`a`) を解除しようとするもので、自身の活動の痕跡を隠蔽したり、永続化メカニズムを保護する意図が考えられます（`lockr` コマンドは一般的なLinuxコマンドではなく、ハニーポット上で失敗しています）。

*   **使用ツール**:
    *   **自動化スクリプト/ボットネット**: 複数の異なる認証情報を短時間に試行し、ログイン成功後に定型的なコマンドを繰り返し実行していることから、手動操作ではなく、自動化されたSSHブルートフォースツール（例: Hydra, Medusa, Nmap NSEスクリプトなど）や、ボットネットの一部として活動している可能性が高いです。
    *   **標準SSHクライアント**: 接続には標準的なSSHクライアントが使用されています。

### 3. 脅威レベルとその理由

*   **脅威レベル**: **高 (High)**

*   **理由**:
    1.  **root権限奪取の成功**: 本ログはハニーポットのものであるため実際のシステム侵害には至っていませんが、もしこれが本番環境のシステムに対して行われていた場合、攻撃者は `root` ユーザーのパスワードを複数回突破しており、システムに対する完全な制御権 (`root` 権限) を完全に奪取したことになります。これは最も深刻なシステム侵害の一つです。
    2.  **永続的なバックドアの確立試行**: 攻撃者はログイン後、自身のSSH公開鍵を `authorized_keys` に追加することで、パスワードなしでシステムに再アクセスできる永続的なバックドアの確立を試みています。これにより、パスワードの変更や他の対策を講じても、攻撃者はいつでもシステムに戻ってこられる状態になります。
    3.  **自動化された攻撃の継続性**: 攻撃が自動化されており、異なる認証情報を執拗に試行していることから、この攻撃元が脆弱なSSHサービスを持つ広範なターゲットをスキャンしていると推測されます。組織内の他のシステムも同様の攻撃を受けるリスクが高いことを示唆しています。
    4.  **潜在的な二次攻撃の危険性**: root権限でのアクセスと永続化の確立は、その後のマルウェア感染、データ窃取、システム破壊、リソースの悪用（例：暗号通貨マイニング、DDoS攻撃の踏み台化）など、より深刻な二次攻撃への足がかりとなります。

### 4. 推奨アクション

**緊急対応 (Immediate Actions)**:

1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `190.244.39.232` からのすべての通信を、境界ファイアウォールまたはIPS/IDSにて即座にブロックしてください。
2.  **既存SSH公開鍵のレビューと削除**: すべてのSSHサーバーにおいて、`root` ユーザーおよび他の特権ユーザーの `~/.ssh/authorized_keys` ファイルを徹底的にレビューし、不審な公開鍵（特にログに示されたコメント `mdrfckr` の公開鍵 `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` など）が登録されていないか確認し、発見された場合は直ちに削除してください。
3.  **パスワードの強制変更**: 本ログに記録されたログイン成功パスワード (`135792468`, `abcdefgh`, `Aa112211.`, `Gp123456`, `nPSpP4PBW0`, `3245gs5662d34`) が、組織内の他のシステムやサービスで使い回されていないか緊急で確認し、該当するアカウントのパスワードはすべて直ちに強力なものへ強制変更してください。
4.  **侵害調査 (Compromise Assessment)**: もしこの攻撃が本番環境のシステムで発生していた場合、当該システムが完全に侵害されている可能性が高いです。専門家による包括的な侵害調査（マルウェアの有無、データ窃取の痕跡、設定変更、新たなユーザーアカウントの有無など）を直ちに開始してください。

**予防的措置 (Preventive Measures)**:

1.  **SSH設定の厳格化**:
    *   **パスワード認証の無効化**: SSHサービスでは、可能な限りパスワード認証を無効化し、より安全な鍵認証のみを許可する設定 (`PasswordAuthentication no`) に変更してください。
    *   **rootログインの禁止**: `PermitRootLogin no` を設定し、`root` ユーザーの直接ログインを禁止してください。必要に応じて、一般ユーザーでログイン後、`sudo` を利用する運用に切り替えてください。
    *   **SSHポートの変更**: 標準の22番ポートから別の高位ポートに変更することを検討してください（セキュリティバイオブスキュリティですが、自動化されたスキャンからの露出を減らせます）。
    *   **Fail2Banなどの導入**: 複数回のログイン失敗を検知し、一時的に攻撃元IPをブロックするFail2Banなどのツールを導入・設定してください。
    *   **不要なアカウントの削除/無効化**: 使用されていないSSHアカウントはすべて削除または無効化してください。
2.  **強力なパスワードポリシーの適用**: 組織全体で、複雑性、長さ、定期的な変更を義務付ける強力なパスワードポリシーを徹底してください。可能であれば、多要素認証 (MFA) の導入を検討してください。
3.  **システムおよびアプリケーションのパッチ管理**: OS、SSHサービス、およびその他のシステムコンポーネントの脆弱性スキャンを定期的に実施し、常に最新のセキュリティパッチを適用してください。
4.  **ログ監視の強化**: SSHログインログを含むすべての重要なセキュリティログをSIEM（Security Information and Event Management）などの集中ログ管理システムに集約し、不審なログイン試行、成功、および特権コマンド実行に対するリアルタイムのアラートを設定・監視を強化してください。
5.  **インシデントレスポンス計画の見直しと訓練**: 今回のような攻撃に対する組織のインシデントレスポンス計画を定期的に見直し、シミュレーション訓練を実施することで、有事の際の対応能力を向上させてください。
6.  **脅威インテリジェンスの活用**: ログに記載されたSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) や攻撃元IPを脅威インテリジェンスプラットフォームで検索し、関連する他の攻撃情報やIoC（Indicators of Compromise）を収集・分析してください。