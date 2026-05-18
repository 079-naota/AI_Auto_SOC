# SOC自動分析レポート: 103.48.192.48

**生成日時:** 2026-04-26 09:23:19

---

## 攻撃ログ分析レポート

**SOCアナリスト:** [あなたの名前/チーム名]
**日付:** 2026-04-26

### 1. 攻撃の概要と目的

攻撃元IPアドレス `103.48.192.48` から、複数のSSH接続試行が確認されました。この攻撃は、ターゲットシステムへの不正ログイン、およびログイン成功後の永続的なアクセス経路確立を目的としています。

**攻撃の具体的な流れ:**
1.  **ブルートフォース攻撃（辞書攻撃）:** 攻撃者は様々なユーザー名（例: `ftpuser`, `boss`, `admin`, `teszt`, `bot`, `claude`, `j`）とパスワードの組み合わせ、特に特権ユーザーである`root`アカウントに対して複数のパスワード（例: `Asd123!@#`, `Csdx@13579`, `Pa55word`, `Test123!!`, `Zt123456`）を試行しています。
2.  **ログイン成功と永続化の試み:** `root`ユーザーでのログインが複数回成功したと記録されています（ハニーポット上でのシミュレーション）。ログイン成功後、攻撃者は以下のコマンドを実行しようとしました。
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh`ディレクトリのファイル属性を変更し、変更保護を無効化しようとする試み。`lockr`は一般的なコマンドではないため、環境に依存する、または誤ったコマンド入力の可能性もあります。
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: `.ssh`ディレクトリを再作成し、攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を`authorized_keys`ファイルに追加することで、公開鍵認証によるバックドアを設置しようとする意図が見られます。
3.  **テスト接続:** 鍵設置コマンド実行後、すぐに別のユーザー（`345gs5662d34`で失敗、`root`/`3245gs5662d34`で成功）での接続試行が複数回確認されており、これはバックドアが正常に機能するかどうかのテスト、またはさらなる認証情報の試行であると考えられます。

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **ブルートフォース/辞書攻撃:** 大量のユーザー名とパスワードの組み合わせを自動的に試行しています。
    *   **永続化メカニズムの利用:** SSH公開鍵認証を利用して、一度ログインしたシステムへの永続的なアクセス経路を確立しようとしています。
    *   **ファイルシステムの改変:** システムファイルを操作して（`.ssh`ディレクトリの削除と再作成、`authorized_keys`の書き換え）、アクセス制御を迂回しようとしています。
*   **使用ツール:**
    *   ログの詳細から特定のツールを断定することは困難ですが、SSHプロトコルを介してブルートフォース攻撃を実行し、シェルコマンドを自動的に入力する機能を持つスクリプトまたはツール（例: `Hydra`, `Medusa`などのブルートフォースツール、あるいはカスタムシェルスクリプト）が使用されている可能性が高いです。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**
*   **特権ユーザー（root）でのログイン成功:** 攻撃者が`root`アカウントの認証情報を突破した（ハニーポット環境ではシミュレーションですが、現実のシステムであれば深刻な侵害となります）ことは、システムに対する完全な制御権奪取の可能性を示唆します。
*   **永続化の試み:** 攻撃者が公開鍵を設置しようとしていることは、将来にわたってパスワード変更の影響を受けずにシステムへのアクセスを維持する意図があることを意味します。これは、検出されにくく、削除が困難なバックドアの設置を目的とした、より高度な攻撃段階です。
*   **自動化された攻撃:** 短時間で多数のログイン試行と、ログイン成功後の定型的なコマンド実行が繰り返されていることから、これは自動化されたスクリプトやボットネットによる大規模な攻撃キャンペーンの一部である可能性が高いです。
*   **潜在的な影響の大きさ:** もし実際のシステムでこのような攻撃が成功した場合、システムデータの窃取、マルウェアの展開、他のシステムへの踏み台としての利用など、広範かつ深刻な被害につながる可能性があります。

### 4. 推奨アクション

#### 4.1. 即時対応（Containment & Eradication）

1.  **攻撃元IPのブロック:** ファイアウォール、IDS/IPS、または`iptables`などのOSレベルのセキュリティ機能を用いて、攻撃元IPアドレス `103.48.192.48` からの全ての通信を即座にブロックしてください。
2.  **関連ログの緊急調査:** ログがハニーポットのものであることを理解した上で、実際のプロダクション環境や重要システムにおいて、以下の緊急調査を実施してください。
    *   **SSHログの確認:** 全てのシステムでSSHログを確認し、同じ攻撃元IPからの接続試行や、`root`ユーザーを含む不正なログイン試行がないか確認してください。
    *   **認証情報の変更履歴確認:** ログで確認されたパスワード（`Asd123!@#`, `Csdx@13579`, `Pa55word`, `Test123!!`, `Zt123456`, `3245gs5662d34`など）が、過去にどのユーザーのパスワードとして使用されたことがないかを確認してください。
    *   **`authorized_keys`ファイルの監査:** 全てのユーザーの`~/.ssh/authorized_keys`ファイルの内容を精査し、ログに記載された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が追加されていないか確認し、発見された場合は直ちに削除してください。

#### 4.2. 事後対策（Post-Incident Activity & Prevention）

1.  **SSHセキュリティ強化:**
    *   **ポート変更:** SSHサービスがデフォルトのポート22で稼働している場合は、非標準のポートに変更することを検討してください。
    *   **パスワード認証の無効化:** 可能であれば、SSHパスワード認証を完全に無効にし、公開鍵認証のみを許可してください。
    *   **多要素認証（MFA）の導入:** 特権アカウントに対しては、多要素認証を必須としてください。
    *   **ブルートフォース対策ツールの導入:** `Fail2ban`や`CrowdSec`などのツールを導入し、一定回数ログインに失敗したIPアドレスを自動的にブロックするように設定してください。
2.  **強力なパスワードポリシーの徹底:**
    *   全てのシステムユーザーに対して、複雑性、長さ、更新頻度に関する厳格なパスワードポリシーを適用してください。
    *   一般的なパスワード辞書に含まれるような弱いパスワードの使用を禁止してください。
3.  **公開鍵認証の適切な管理:**
    *   `~/.ssh`ディレクトリおよび`authorized_keys`ファイルのパーミッションを厳格に設定してください（例: `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/authorized_keys`）。
    *   全ての公開鍵が正当なものであることを定期的に監査してください。
4.  **脅威インテリジェンスの活用:**
    *   検出された攻撃元IPアドレスや公開鍵の情報（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を外部の脅威インテリジェンスプラットフォームやデータベース（例: VirusTotal, Shodan, AbuseIPDB）で検索し、既知の攻撃グループやマルウェアとの関連性を調査してください。
5.  **セキュリティ監視の強化:**
    *   SIEM（Security Information and Event Management）システムにSSHログを統合し、不審なログイン試行やコマンド実行に対するアラートを設定してください。
    *   システムへの不正なファイル変更やパーミッション変更を検知するためのファイル整合性監視（FIM）ソリューションの導入を検討してください。