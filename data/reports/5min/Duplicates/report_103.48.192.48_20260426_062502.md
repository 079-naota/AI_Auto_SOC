# SOC自動分析レポート: 103.48.192.48

**生成日時:** 2026-04-26 06:26:48

---

## SOC分析レポート

### 1. 攻撃の概要と目的

このログは、攻撃元IP `103.48.192.48` からのSSHサービスに対するブルートフォース攻撃を示しています。攻撃者は、複数の一般的なユーザー名とパスワードの組み合わせを試行した後、`root`ユーザーとして複数回のログインに成功しています。ログイン成功後、攻撃者はシステムに永続的なアクセス経路を確立しようとしています。

**攻撃元IP**: 103.48.192.48
**攻撃対象サービス**: SSH
**攻撃時刻**: 2026-04-26T03:17:02Z から 2026-04-26T03:38:51Z
**攻撃の目的**:
1.  SSHブルートフォース/辞書攻撃による初期アクセス権の獲得。
2.  `root`権限を持つアカウントでのログイン成功。
3.  攻撃者のSSH公開鍵を`~/.ssh/authorized_keys`に追加することで、永続的なアクセス経路（バックドア）を確立し、パスワードなしでいつでもシステムに接続できるようにする。

### 2. 推測される手法・使用ツール

*   **ブルートフォース/辞書攻撃**: 多数のユーザー名（`ftpuser`, `root`, `boss`, `admin`, `teszt`, `bot`, `claude`, `j`など）とパスワードの組み合わせを短時間で繰り返し試行していることから、HydraやMedusa、Nmapの`ssh-brute`スクリプトなどの自動化されたブルートフォースツールまたは辞書攻撃ツールが使用されていると推測されます。特に`root`ユーザーに対しては、様々なパスワード（`Asd123!@#`, `Csdx@13579`, `Pa55word`, `Test123!!`, `Zt123456`, `3245gs5662d34`）を試行し、複数回成功させています。
*   **永続化のためのバックドア設置**: ログイン成功後、攻撃者は以下のコマンドを実行しています。
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh`ディレクトリの不変属性を解除しようとしていますが、`lockr`コマンドは失敗しています。これは、後続のファイル操作を可能にするための準備と考えられます。
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`:
        1.  既存の`.ssh`ディレクトリを削除し、新規作成。
        2.  特定のSSH公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を`~/.ssh/authorized_keys`に追加。
        3.  `.ssh`ディレクトリのパーミッションを厳格化（他のグループやユーザーからのアクセスを制限）。
        この一連のコマンドは、攻撃者がパスワードなしでSSH接続できるよう、システムにバックドアを設置する典型的な手法です。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
*   **root権限の奪取**: 攻撃者が`root`ユーザーとして複数回ログインに成功しているため、システムに対する完全な制御権を獲得している可能性が極めて高いです。
*   **永続的なアクセス経路の確立**: 攻撃者が自身のSSH公開鍵を`authorized_keys`ファイルに追加しているため、システムへの継続的なアクセスが可能です。これにより、パスワードが変更されたとしても、攻撃者はシステムへのアクセスを維持できます。
*   **自動化された攻撃の兆候**: ブルートフォース攻撃とそれに続く永続化の手順が反復して行われていることから、自動化されたスクリプトやマルウェアが関与している可能性が高く、これは他のシステムへの攻撃拡大やボットネット活動の一部であることも示唆しています。
*   **潜在的な影響の深刻さ**: `root`権限の奪取と永続的なアクセス経路の確立は、データ窃取、マルウェアの展開、システムの破壊、他のシステムへの踏み台利用、C&Cサーバーとしての悪用など、あらゆる種類の深刻な被害につながる可能性があります。

### 4. 推奨アクション

**緊急対応 (Immediate Actions)**

1.  **攻撃元IPのブロック**:
    *   `103.48.192.48`からの全てのインバウンド通信を、ファイアウォール、IDS/IPS、またはACLで直ちにブロックしてください。
2.  **侵害されたアカウントのパスワード変更**:
    *   **`root`ユーザーのパスワードを直ちに変更**し、強力でユニークなパスワードを設定してください。
    *   ログに記録されたログイン成功パスワード（`Asd123!@#`, `Csdx@13579`, `Pa55word`, `Test123!!`, `Zt123456`, `3245gs5662d34`）が他のシステムやユーザーで利用されていないか確認し、もし利用されている場合は直ちに変更してください。
3.  **侵害されたシステムの特定と隔離**:
    *   このログが本番システムのものであれば、直ちにネットワークから隔離（物理的または論理的に切断）し、これ以上の被害拡大を防いでください。
    *   ハニーポットのログである場合も、同様の脆弱性を持つ本番システムがないか緊急で監査を実施してください。
4.  **SSH公開鍵の削除**:
    *   侵害されたシステム上の`~/.ssh/authorized_keys`ファイルを確認し、攻撃者が追加した公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を削除してください。
5.  **フォレンジック分析の開始**:
    *   システムのディスクイメージを取得し、マルウェア感染の有無、データの改ざん、追加されたバックドア、攻撃者の活動履歴などを詳細に調査してください。

**中期的な対策 (Medium-Term Actions)**

1.  **SSH設定の強化**:
    *   **パスワード認証の無効化**: 可能な限りパスワード認証を無効にし、鍵認証のみを許可してください。
    *   **`root`ユーザーの直接ログイン禁止**: `/etc/ssh/sshd_config`で`PermitRootLogin no`を設定し、一般ユーザーでログイン後に`sudo`を使用する運用に切り替えてください。
    *   **多要素認証 (MFA) の導入**: SSHログインにMFAを必須としてください。
    *   **ポートの変更**: SSHの標準ポート（22番）を非標準のポートに変更することを検討してください（ただし、これはセキュリティの主要な防御策ではなく、攻撃を遅らせる効果に限定されます）。
2.  **侵入検知/防御システムの導入**:
    *   Fail2banやその他のIDS/IPSを導入し、繰り返されるログイン失敗を自動的に検知・ブロックする仕組みを構築してください。
3.  **ユーザーアカウントの棚卸しとパスワードポリシーの強化**:
    *   不要なアカウントを削除し、定期的にパスワードの棚卸しを実施してください。
    *   全てのユーザーに強力なパスワードポリシー（文字数、文字種、定期的な変更など）を強制してください。
4.  **ログ監視の強化**:
    *   SSHログインの成功/失敗、特に`root`ユーザーのログイン試行、および不審なコマンド実行を監視するアラートシステムを強化してください。

**長期的な対策 (Long-Term Actions)**

1.  **脆弱性スキャンとペネトレーションテスト**:
    *   定期的にシステム全体の脆弱性スキャンとペネトレーションテストを実施し、潜在的なセキュリティホールを特定・修正してください。
2.  **セキュリティ意識向上トレーニング**:
    *   システム管理者およびユーザーに対して、セキュリティのベストプラクティス、フィッシング対策、パスワード管理などに関する定期的なトレーニングを実施してください。
3.  **インシデントレスポンス計画の見直し**:
    *   今回のようなインシデント発生時の対応手順（検知、封じ込め、根絶、復旧、事後分析）を確認・改善し、IR訓練を実施してください。

---
以上