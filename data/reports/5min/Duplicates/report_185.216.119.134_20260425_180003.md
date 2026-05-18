# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 18:01:56

---

## SOC分析レポート

### 1. 攻撃の概要と目的

提供されたログはSSHハニーポット（Cowrie）に対する攻撃の記録です。攻撃元IPアドレス `185.216.119.134` から、複数のユーザー名とパスワードの組み合わせを使用したSSHブルートフォース/辞書攻撃が観測されました。

攻撃者は様々なユーザー名（例: `zabbix`, `john`, `satya`, `admin`, `test`, `user`）と、それに続く試行の中から、最終的に`root`ユーザーに対する複数の異なるパスワード（`123.com.`, `nPSpP4PBW0`, `Aa112211.`, `123Qwe!@#`, `Admin12!@#`）でログインに成功しています。また、`root`ユーザーでのログイン成功後、攻撃者は以下のコマンドを実行しようとしています。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh`ディレクトリの属性を変更し、不変または追加専用にすることで、削除や改変を防ごうとする試みです。`lockr`コマンドは一般的ではないため、エラーとなっている可能性があります。
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: 既存の`.ssh`ディレクトリを削除し、再作成した上で、自身のSSH公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を`authorized_keys`に追加し、パーミッションを適切に設定することで、パスワードなしで永続的にアクセスできるバックドアを確立しようとしています。

この攻撃の目的は、SSHサービスへの不正アクセスを試み、成功した場合には自身の公開鍵を埋め込むことで、以降はパスワードなしでシステムに再侵入できる永続的なアクセス経路を確保することにあると推測されます。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース攻撃 / 辞書攻撃**: 大量のユーザー名とパスワードの組み合わせを短時間に試行しており、これは自動化されたブルートフォースまたは辞書攻撃の典型的なパターンです。
    *   **永続化 (Persistence)**: ログインに成功した後、自身のSSH公開鍵を`~/.ssh/authorized_keys`に追加することで、認証情報が変更されてもアクセスを維持できるバックドアを設置しようとしています。これは攻撃者がシステムへの長期的なアクセスを意図していることを示します。
*   **使用ツール**:
    *   ログの時間間隔や試行回数から、特定のSSHクライアントを利用した自動化スクリプト、またはSSHブルートフォースツール（例: Hydra, Medusa）が使用されている可能性が高いです。
    *   攻撃者が埋め込もうとしたSSH公開鍵は、マルウェアやボットネットのキャンペーンで頻繁に使用される既知の鍵である可能性があります。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **root権限でのログイン成功**: 攻撃者が最も高い権限を持つ`root`ユーザーとして複数回ログインに成功している点は非常に危険です。もしこれが実システムであれば、攻撃者はシステムの完全な制御権を掌握したことになります。
2.  **永続化の試み**: ログイン成功後に自身のSSH公開鍵を設置しようとする行動は、一時的なアクセスではなく、永続的なバックドアを確立しようとする意図を明確に示しています。これにより、攻撃者は将来にわたっていつでもシステムにアクセス可能となるリスクがあります。
3.  **自動化された攻撃**: ブルートフォース攻撃は自動化されたツールやボットネットによって行われている可能性が高く、これは特定のターゲットだけでなく、インターネットに公開された広範なシステムを狙った無差別攻撃の一部である可能性があります。

このログはハニーポットのものであるため、実際のシステムが侵害されたわけではありませんが、もし実システムであった場合、上記理由により非常に深刻な事態に発展する可能性がありました。

### 4. 推奨アクション

#### 4.1. 緊急対応 (もし実システムであった場合)

*   **攻撃元IPのブロック**: ファイアウォールやWAF、IPS/IDSにて、攻撃元IPアドレス `185.216.119.134` からの全ての通信を即座にブロックリストに追加する。
*   **不正なSSH鍵の確認と削除**: `root`ユーザーの`~/.ssh/authorized_keys`ファイルに、攻撃者が書き込もうとした公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないことを確認し、もし存在すれば直ちに削除する。また、他のユーザーの`authorized_keys`ファイルも同様に確認する。
*   **パスワードリセット**: ログインに成功した`root`ユーザー（および試行された他のユーザー）のパスワードを直ちに、より複雑なものに変更する。
*   **システムのスキャンと侵害調査**: 侵害の可能性を考慮し、ルートキット、マルウェア、バックドアがないかシステム全体をスキャンし、詳細なフォレンジック調査を実施する。

#### 4.2. 予防策とセキュリティ強化

*   **SSHセキュリティ設定の強化**:
    *   **パスワード認証の無効化**: 可能な限り、SSHのパスワード認証を無効にし、公開鍵認証のみを許可する (`PasswordAuthentication no`, `ChallengeResponseAuthentication no`)。
    *   **rootログインの禁止**: `root`ユーザーによる直接SSHログインを禁止する (`PermitRootLogin no`)。必要に応じて一般ユーザーでログイン後、`sudo`を利用する。
    *   **デフォルトポートの変更**: SSHのデフォルトポート（22番）を別の非標準ポートに変更する。これにより、自動化されたスキャンからの検出を軽減できるが、セキュリティの本質的改善ではない。
    *   **接続元IPアドレスの制限**: SSHへのアクセスを特定の信頼できるIPアドレス範囲に限定する。
*   **アカウントと認証情報の管理**:
    *   **多要素認証 (MFA) の導入**: SSHログインにMFAを必須とすることで、仮にパスワードが漏洩しても不正アクセスを防ぐ。
    *   **強力なパスワードポリシーの適用**: 全ユーザーに対し、複雑性、長さ、定期的な変更を義務付けるパスワードポリシーを適用する。
    *   **未使用アカウントの削除**: 使用されていないSSHアカウントを定期的に棚卸し、削除する。
*   **ログ監視とアラート**:
    *   **SSH認証ログの監視強化**: SSHログインの成功・失敗、特に`root`ユーザーへのログイン試行、特定のアカウントへの大量のログイン失敗について、SIEMや集中ログ管理システムで監視し、即時アラートを発するルールを設定する。
    *   **ファイル整合性監視**: `~/.ssh/authorized_keys`などの重要なシステムファイルや設定ファイルの変更を監視し、不正な変更があった場合にアラートを出す。
*   **侵入検知システム (IDS/IPS) の導入・強化**:
    *   SSHブルートフォース攻撃を検知し、自動的にブロックするIDS/IPSを導入またはルールを強化する。
    *   `fail2ban`などのツールを導入し、一定回数以上の認証失敗があったIPアドレスを一時的にブロックする。
*   **定期的なセキュリティ監査と脆弱性管理**:
    *   システムとアプリケーションの脆弱性スキャンを定期的に実施し、発見された脆弱性には速やかにパッチを適用する。
    *   セキュリティ設定の監査を定期的に行い、ベストプラクティスに準拠していることを確認する。

今回のログはハニーポットのものであるため、実際のシステムへの被害は発生していませんが、このログは攻撃者が実システムに対してどのような行動をとるかを示す貴重な情報です。この分析結果を元に、自社のSSHサービスのセキュリティ体制を見直し、強化することを強く推奨します。