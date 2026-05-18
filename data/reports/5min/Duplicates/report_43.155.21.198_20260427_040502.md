# SOC自動分析レポート: 43.155.21.198

**生成日時:** 2026-04-27 04:05:41

---

## SOCアナリストレポート

### 攻撃ログ分析結果

**攻撃元IPアドレス:** 43.155.21.198
**ログ期間:** 2026-04-27T03:31:15Z から 2026-04-27T03:39:09Z

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `43.155.21.198` から、SSHサービスに対して継続的なブルートフォース/辞書攻撃が行われました。攻撃者は主に `root` ユーザーを標的とし、複数の異なるパスワードを試行してログインに成功しています。

ログイン成功後、攻撃者は以下の2種類のコマンドを迅速に実行しようとしています。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリの不変属性（immutable/append-only）を削除し、特定のロックメカニズムを無効にしようとする試み。`chattr` は標準的なLinuxコマンドですが、`lockr` は通常存在しないコマンドであり、このコマンド自体は失敗しています。
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: 既存の `.ssh` ディレクトリを削除し、新たに作成した後、自身の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を `authorized_keys` ファイルに追加し、パーミッションを適切に設定する試みです。

**攻撃の主な目的は、システムへの不正アクセスを確立し、自身の公開鍵をシステムに追加することで永続的なアクセス経路を確保することにあると推測されます。** これにより、パスワード認証を迂回していつでもシステムに再侵入できるようになります。

---

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **ブルートフォース/辞書攻撃:** `root` ユーザーに対する複数のパスワード試行から、自動化されたブルートフォース攻撃または辞書攻撃が行われていると判断されます。
    *   **永続化 (Persistence):** `authorized_keys` ファイルに攻撃者の公開鍵を追加することで、システムへのバックドアを設置し、将来的なアクセスを保証しようとしています。これは、MITRE ATT&CKフレームワークの「T1098.004: Account Manipulation: SSH Authorized Keys」に該当します。
    *   **防御回避 (Defense Evasion):** `chattr -ia .ssh` コマンドは、ファイル属性を変更することで、システムの防御メカニズムを回避し、重要なファイルを改変可能にしようとする意図が見られます。
*   **使用ツール:**
    *   **SSHクライアント:** SSH接続を行うための標準的なクライアント。
    *   **自動化されたブルートフォースツール:** 継続的かつ多様なパスワードを試行していることから、Hydra、Medusa、NmapのSSHブルートフォーススクリプト、またはカスタムスクリプトなどの自動化ツールが使用されている可能性が高いです。

---

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **複数の root ユーザーログイン成功:** 攻撃者は複数の異なるパスワードで `root` ユーザーとしてログインに成功しています。`root` ユーザーはLinuxシステムにおいて最高権限を持つため、これにより攻撃者はシステムのあらゆる操作（データの閲覧、変更、削除、マルウェアのインストール、設定の改変など）が可能になります。
2.  **永続化の試み:** ログイン成功後、速やかに `authorized_keys` に自身の公開鍵を追加しようとしています。この行為は、システムへの永続的なアクセス経路を確立するためのものであり、仮にパスワードが変更されても攻撃者はシステムへのアクセスを維持できます。
3.  **組織的かつ自動化された攻撃:** 短時間のうちに繰り返しログイン試行とバックドア設置のためのコマンド実行が行われていることから、これは単独の手動操作ではなく、自動化されたスクリプトやボットネットの一部として実行されている可能性が高いです。
4.  **高い影響の可能性:** `root` 権限の奪取と永続化の成功は、システムの完全な侵害を意味します。データ漏洩、システム破壊、サービス停止、さらなる内部ネットワークへの横展開など、極めて重大な影響を引き起こす可能性があります。

---

### 4. 推奨アクション

1.  **緊急対応 (Immediate Actions):**
    *   **対象システムの緊急遮断/隔離:** もしこれが実際のシステムであれば、直ちにネットワークから隔離し、攻撃の拡大とさらなる被害を防止してください。
    *   **不正な公開鍵の削除:** すべてのユーザー（特に `root` ユーザー）の `~/.ssh/authorized_keys` ファイルを緊急で確認し、上記ログに記載されている攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、存在する場合は直ちに削除してください。
    *   **すべてのパスワードのリセット:** ログインに成功した `root` ユーザーだけでなく、システム上のすべてのユーザーのパスワードを直ちに、かつ強力なものに変更してください。特に `root` のパスワードは複雑なものに設定し直してください。
    *   **SSHサービスのアクセス制限/一時停止:** 外部からのSSHアクセスを一時的に無効にするか、特定の信頼できるIPアドレスからのアクセスのみに厳しく制限してください。
    *   **攻撃元IPのブロック:** ファイアウォールまたはIPSで攻撃元IPアドレス `43.155.21.198` からのすべての通信をブロックしてください。

2.  **フォレンジック調査 (Forensic Investigation):**
    *   **ログの詳細分析:** SSHログ、システム認証ログ（`/var/log/auth.log` や `/var/log/secure` など）、Cowrie以外のIDS/IPSログ、ファイアウォールログなどを詳細に分析し、攻撃者がログイン成功後に実行した可能性のある他の活動（データ窃取、マルウェアの展開、他のアカウントへの横展開など）を特定してください。
    *   **システムイメージの取得:** 影響を受けた可能性のあるシステムのディスクイメージを取得し、オフラインで詳細なフォレンジック分析を実施してください。これにより、マルウェアの痕跡、設定変更、バックドアなどの詳細な情報を検出できます。

3.  **再発防止策 (Preventive Measures):**
    *   **SSHパスワード認証の無効化（推奨）:** 可能な限り、SSHのパスワード認証を無効にし、公開鍵認証のみに限定してください。公開鍵は適切に管理し、パスフレーズで保護してください。
    *   **強力なパスワードポリシーの適用:** すべてのシステムアカウントに対して、強力で複雑なパスワードを強制し、定期的な変更を促すポリシーを適用してください。
    *   **多要素認証 (MFA) の導入:** 可能な場合は、SSHアクセスに対して多要素認証 (MFA) を導入し、セキュリティを大幅に強化してください。
    *   **rootユーザーの直接SSHログイン禁止:** `PermitRootLogin no` を設定し、`root` ユーザーの直接的なSSHログインを禁止してください。必要な場合は、一般ユーザーでログイン後に `su` や `sudo` を使用するようにしてください。
    *   **レートリミットとIPブロックツールの導入:** Fail2banなどのツールを導入し、SSHへのログイン試行回数にレートリミットを設定し、不正なログイン試行を行うIPアドレスを自動的にブロックする仕組みを構築してください。
    *   **脆弱性管理:** 定期的な脆弱性スキャンを実施し、システムやソフトウェアの脆弱性を迅速に特定しパッチを適用してください。
    *   **ログ監視とアラートの強化:** SSHログイン試行の失敗、成功、重要なファイルへのアクセス、不明なコマンド実行など、異常なアクティビティをリアルタイムで検出し、SOCにアラートを発する監視体制を強化してください。
    *   **システムベースラインの確立と変更検知:** 重要なシステムファイル（例：`/etc/ssh/sshd_config`, `~/.ssh/authorized_keys` など）のベースラインを確立し、不正な変更を検知できるシステム（例：AIDE, Tripwire）を導入してください。