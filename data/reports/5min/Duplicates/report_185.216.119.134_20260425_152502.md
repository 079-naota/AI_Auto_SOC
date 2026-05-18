# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 15:26:45

---

## SOC分析レポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `185.216.119.134` から、2026年4月25日04:15Zから04:47Zにかけて、本システム（Cowrieハニーポット）に対する集中的なSSHブルートフォース攻撃が観測されました。

この攻撃は、様々なユーザー名とパスワードの組み合わせを試行することで、システムへの不正アクセスを試みるものでした。特に、`root` ユーザーに対するログイン試行が複数回成功しており、攻撃者はシステムの最高権限を取得したことを想定し、永続的なアクセス経路を確立しようとしていました。

具体的には、ログイン成功後には以下のコマンド実行が試みられました。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

最初のコマンドは `.ssh` ディレクトリの属性を変更し、ファイルの削除や変更を困難にすることで、バックドアの永続性を高めようとしたものと推測されますが、Cowrie環境では失敗しています。
二番目のコマンドは、攻撃者のSSH公開鍵を `~/.ssh/authorized_keys` に追加し、これによりパスワードなしで将来的にシステムにSSH接続できるバックドアを確立しようとする明確な目的があります。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSH ブルートフォース攻撃 / パスワードスプレー攻撃**: `zabbix`, `john`, `satya`, `admin`, `test`, `user` といった一般的なユーザー名や、特に `root` ユーザーに対して、複数の推測しやすい、または既知の脆弱なパスワードを試行しています。
    *   **バックドアの確立**: ログイン成功後、攻撃者のSSH公開鍵を `authorized_keys` ファイルに書き込むことで、パスワード認証を回避し、永続的なアクセス経路を確保しようとしています。
    *   **永続化の試み**: `chattr` や `lockr` コマンドを使用して、追加したSSH鍵の削除や改変を防ごうとしています。
*   **使用ツール**:
    *   SSH接続とブルートフォース攻撃を実行するための自動化ツール（例: Hydra, Nmapの`ssh-brute`スクリプトなど）が使用された可能性が高いです。
    *   公開鍵の追加には、通常のシェルコマンドが使用されています。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:

*   **`root` ユーザーでのログイン成功**: ログはCowrieハニーポットのものですが、攻撃者は複数回にわたって `root` ユーザーでのログインに成功しています。これが本番環境であった場合、攻撃者はシステムに対する最高権限を完全に掌握したことになります。
*   **永続化メカニズムの確立試行**: ログイン成功後に、`~/.ssh/authorized_keys` に攻撃者のSSH公開鍵を追加しようとしています。これは、一旦アクセスを確立した後に、パスワード変更などの防御策が講じられても、継続的にシステムにアクセスするための永続的なバックドアを設置する非常に危険な行為です。
*   **組織的な攻撃の可能性**: 試行されたユーザー名やパスワードのパターンから、一般的な辞書攻撃やパスワードスプレー攻撃の一環である可能性が高いです。また、特定の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を利用していることから、特定の攻撃グループまたはボットネットによる広範なスキャン活動である可能性があります。
*   **コマンド実行の試み**: システム上で特定のコマンドを実行し、環境の改変を試みていることから、単なる偵察ではなく、明確な目的を持った攻撃であると判断されます。

### 4. 推奨アクション

この攻撃はハニーポットで観測されたものですが、本番環境で同様の攻撃が発生した場合を想定し、以下の緊急および長期的な対策を推奨します。

#### 緊急対応 (Immediate Actions):

1.  **攻撃元IPアドレスのブロック**:
    *   攻撃元IPアドレス `185.216.119.134` を、ファイアウォール、IPS/IDS、またはネットワークACLで即座にブロックし、これ以上のアクセスを防止します。
2.  **ログイン成功アカウントの確認とパスワード変更**:
    *   ログに記録された `root` ユーザーでログインに成功したパスワード (`123.com.`, `nPSpP4PBW0`, `Aa112211.`, `123Qwe!@#`, `Admin12!@#`) が、**実際のシステムで現在も使用されていないか緊急に確認**してください。
    *   もし使用されている場合は、**即座に当該アカウントのパスワードを強力なものに変更**してください。
    *   これ以外の試行されたユーザー名（`zabbix`, `john`, `satya`, `345gs5662d34`, `admin`, `test`, `test1`, `user`）についても、当該アカウントが存在しないか、パスワードが脆弱でないかを確認し、必要に応じて変更または削除を検討してください。
3.  **SSH設定の監査と不正な鍵の削除**:
    *   **本番環境の全サーバー**において、`root` ユーザーおよび他の特権ユーザーの `~/.ssh/authorized_keys` ファイルの内容を監査し、ログに示された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が含まれていないか確認してください。
    *   もし不正な鍵が発見された場合、**即座に当該鍵を削除**し、`~/.ssh` ディレクトリおよび `authorized_keys` ファイルの権限が適切であるか（例: `.ssh` は700、`authorized_keys` は600）を確認してください。
4.  **侵害調査 (Forensic Investigation)**:
    *   もし本番環境で同様のログイン成功が確認された場合、攻撃者がシステムにアクセスした証拠となります。影響を受けたシステムの詳細なフォレンジック調査を実施し、以下の点を確認してください。
        *   他のバックドアやマルウェアが設置されていないか。
        *   データが改ざん、窃取されていないか。
        *   他のシステムへの横展開が行われていないか。
        *   アクセスログ（SSH, Web, その他のサービス）を詳細に分析し、不審な活動がないか確認してください。

#### 長期的な対策 (Long-term Measures):

1.  **SSHのセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能であれば、SSHパスワード認証を無効にし、公開鍵認証のみを許可するように設定します。
    *   **`root` ユーザーのSSHログイン禁止**: `PermitRootLogin no` を設定し、`root` ユーザーでのSSH直接ログインを禁止します。特権作業は一般ユーザーでログイン後、`sudo` を使用して行います。
    *   **SSHポートの変更**: 標準ポート22番から別のポートに変更し、自動化されたスキャンからの露出を減らします。
    *   **Fail2Banなどの導入**: 複数回のログイン失敗があった場合に、自動的にIPアドレスをブロックするツール（Fail2Banなど）を導入します。
    *   **多要素認証 (MFA) の導入**: SSHログインにMFAを導入し、セキュリティを強化します。
    *   **強固なパスワードポリシーの適用**: 全ユーザーに対して、複雑で定期的に変更されるパスワードポリシーを強制します。
2.  **ログ監視の強化**:
    *   SSHのログイン成功・失敗ログをリアルタイムで監視し、SIEM（Security Information and Event Management）システムなどへ集約・連携させ、異常なログイン試行や成功を早期に検知できるアラート体制を構築します。
    *   ハニーポット（Cowrieなど）からのログもSIEMに集約し、攻撃手法のトレンド分析や脅威インテリジェンスとして活用します。
3.  **脆弱性管理とパッチ適用**:
    *   システムやアプリケーションの既知の脆弱性を定期的にスキャンし、最新のセキュリティパッチを迅速に適用するプロセスを確立します。
4.  **脅威インテリジェンスの活用**:
    *   攻撃元IPアドレス (`185.216.119.134`) を脅威インテリジェンスデータベースで調査し、既知の悪性IPアドレスリストに追加することを検討します。

以上の対策を講じることで、今後の類似攻撃に対する防御能力を向上させ、システムのセキュリティ体制を強化することができます。