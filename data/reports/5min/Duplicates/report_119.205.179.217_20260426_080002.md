# SOC自動分析レポート: 119.205.179.217

**生成日時:** 2026-04-26 08:02:33

---

## SOC分析レポート

### 1. 攻撃の概要と目的

攻撃元IPアドレス `119.205.179.217` から、ターゲットシステム（ハニーポット）に対するSSHブルートフォース攻撃が複数回観測されました。攻撃者は、様々なユーザー名とパスワードの組み合わせを試行しており、特に `root` ユーザーへのログインを執拗に試みています。

ログインに成功した後、攻撃者はシステムへの永続的なアクセス経路を確立することを目的としています。具体的には、攻撃者自身のSSH公開鍵をターゲットシステムの `~/.ssh/authorized_keys` ファイルに書き込むことで、パスワードなしで将来的に再ログインできるバックドアを設置しようとしました。

### 2. 推測される手法・使用ツール

*   **初期アクセス (Initial Access) - ブルートフォース/パスワードスプレー攻撃**:
    *   短期間に多様なユーザー名（例: `kamil`, `an`, `ubuntu`, `bitrix`, `b`, `testadmin`, `user`）とパスワードの組み合わせを試行しています。特に `root` ユーザーに対しては、`qazwsxedc123456`, `Aa112211.`, `dlgwbn`, `3edc4rfv#`, `Qazwsx999!`, `3245gs5662d34` など複数のパスワードでログインに成功しています。これは、自動化されたブルートフォースツール（Hydra、NmapのSSHスクリプト、Metasploitなど）またはカスタムスクリプトが使用されていることを強く示唆しています。
*   **永続化 (Persistence) - SSH公開鍵の追加**:
    *   ログイン成功後、以下のコマンドを実行し、攻撃者の公開鍵を `~/.ssh/authorized_keys` に追加しようとしました。
        `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPC5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
    *   公開鍵のコメント `mdrfckr` は、攻撃者の識別や所属グループに関する手掛かりとなる可能性があります。
*   **防御回避 (Defense Evasion) - ファイル属性の変更試行**:
    *   上記の鍵追加コマンドの前に、`cd ~; chattr -ia .ssh; lockr -ia .ssh` というコマンドも試行しています。
        *   `chattr -ia .ssh`: Linuxの拡張属性 `immutable` (`i`) や `append-only` (`a`) を解除しようとしています。これは、`authorized_keys` ファイルが変更されないように保護されている場合に、その防御機構を無効化する意図があると考えられます。
        *   `lockr -ia .ssh`: `lockr` は標準的なLinuxコマンドではないため、ハニーポットが認識しないコマンドであるか、または攻撃者が使用する特定のツール/スクリプトの一部である可能性があります。いずれにしても、ファイルへの変更を妨げる機構を無効化しようとする試みの一環と推測されます。

### 3. 脅威レベルとその理由

*   **脅威レベル: 高 (High)**

*   **理由**:
    *   **積極的なブルートフォース攻撃**: 不特定多数の認証情報を試行し、正規の認証を突破しようとする明確な意図が見られます。
    *   **rootアカウントへの集中**: 攻撃者がシステムに対して最も高い権限である `root` ユーザーの奪取を狙っていることは、成功した場合の被害が甚大になる可能性を示唆します。
    *   **永続化メカニズムの確立**: ログイン成功後の行動が、攻撃者のSSH公開鍵を設置することであるため、一時的な侵入ではなく、長期的なアクセス経路（バックドア）を確保しようとする明確な意図があります。これにより、システムへの継続的な侵入、さらなる内部活動、情報窃取、他のシステムへの横展開などが可能になります。
    *   **複数のrootパスワードでのログイン成功**: 実際の環境であれば、複数のrootアカウントまたはそれに準ずるアカウントが侵害されたことを意味し、複数の脆弱なパスワードが存在する可能性が高いことを示しています。

### 4. 推奨アクション

*   **即時対応 (Immediate Actions)**
    1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `119.205.179.217` をファイアウォール、IDS/IPS、WAFなどで速やかにブロックリストに追加し、今後の攻撃を阻止します。
    2.  **侵害された認証情報の確認とリセット**: ログに記録されたすべてのログイン成功したユーザー名とパスワードの組み合わせ（特に `root` ユーザーの複数のパスワード）が、組織内の他のシステムで使用されていないか緊急で確認し、該当する場合はパスワードを即座にリセットします。
    3.  **不正なSSH公開鍵の監査と削除**: 組織内の全SSHサーバにおいて、提供された攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が `~/.ssh/authorized_keys` ファイルに存在しないか監査し、存在する場合は直ちに削除します。
    4.  **フォレンジック調査**: 実際に侵害が発生している可能性を考慮し、関連するシステムで不正な活動がないかフォレンジック調査を実施します。

*   **予防的措置 (Proactive Measures)**
    1.  **SSH認証の強化**:
        *   **パスワード認証の無効化**: 可能であれば、SSHパスワード認証を完全に無効化し、公開鍵認証のみを強制します。
        *   **rootログインの禁止**: `root` ユーザーでのSSH直接ログインを禁止し、必要に応じて `sudo` を介して昇格することを義務付けます。
        *   **強力なパスワードポリシー**: 複雑さ、長さ、有効期限など、より強力なパスワードポリシーを適用し、脆弱なパスワードの使用を排除します。
        *   **多要素認証 (MFA)**: SSHログインに多要素認証を導入し、セキュリティを強化します。
    2.  **ブルートフォース攻撃対策**:
        *   **侵入検知/防御システム (IDS/IPS)**: Fail2banのようなツールを導入し、一定回数以上の認証失敗があったIPアドレスを自動的にブロックする設定を行います。
        *   **SSHポートの変更**: 標準の22番ポートから非標準のポートに変更することで、多くの自動化されたスキャンや攻撃を回避できます（セキュリティバイオブスキュリティ）。
    3.  **ロギングと監視の強化**:
        *   SSHのログイン試行、成功、失敗、およびコマンド実行に関するログを詳細に記録し、SIEM (Security Information and Event Management) などの集中監視システムで異常パターン（例: 短期間での多数のログイン失敗、未知のユーザーからのログイン、`authorized_keys` ファイルへの変更など）をリアルタイムで検知できる体制を強化します。
    4.  **脆弱性管理**:
        *   定期的なセキュリティスキャンとペネトレーションテストを実施し、公開されているSSHサービスやその他サービスの脆弱性を特定し、修正します。
    5.  **脅威インテリジェンスの活用**:
        *   今回の攻撃で使用された公開鍵情報（特にコメント `mdrfckr`）をOSINT (Open Source Intelligence) などで調査し、既知の攻撃グループやマルウェア、ツールセットに関連する情報がないか確認し、脅威インテリジェンスとして活用します。

以上