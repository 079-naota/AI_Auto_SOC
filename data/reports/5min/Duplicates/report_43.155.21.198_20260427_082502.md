# SOC自動分析レポート: 43.155.21.198

**生成日時:** 2026-04-27 08:25:41

---

## SOC分析レポート

### 1. 攻撃の概要と目的

この攻撃は、IPアドレス `43.155.21.198` から発信された、SSHサービスに対する自動化されたブルートフォース/辞書攻撃であり、成功したログインセッションを利用してシステムへの永続的なアクセス経路を確立することを明確な目的としています。

攻撃者はまず、複数の異なるユーザー名とパスワードの組み合わせ（例: `rootwww/1234qwer`）を試行し、最終的に `root` ユーザーに対する複数のパスワード（例: `6yhnji90-`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`）でログイン成功（ハニーポットの応答）を得ています。

ログイン成功後、攻撃者は以下の重要なコマンドを実行し、システムの制御を維持しようとしました。

*   **永続化の試み**:
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
        *   このコマンドは、既存の `.ssh` ディレクトリを削除し、新しい空の `.ssh` ディレクトリを作成した後、攻撃者自身の公開鍵（コメント `mdrfckr` 付き）を `authorized_keys` ファイルに追加しています。これにより、攻撃者はパスワードなしでのSSHログインを可能にするバックドアを設置し、永続的なアクセス手段を確保しようとしています。また、`.ssh` ディレクトリの権限を適切に設定し、機能するようにしています。
*   **防御回避の試み**:
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`
        *   このコマンドは、`.ssh` ディレクトリのi属性（不変属性）とa属性（追記のみ属性）を解除しようとする試みです。これは、ディレクトリ内のファイルを自由に操作できるようにするための防御回避の手法と考えられます（ハニーポット環境では失敗）。`lockr` は一般的なLinuxコマンドではない可能性がありますが、同様の目的を持つコマンドの一部として試行されたと推測されます。

攻撃の主な目的は、標的システムへの初期アクセスを確立し、その後SSH公開鍵認証による永続的なアクセス手段を確保することにあると判断されます。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **初期アクセス**: SSHブルートフォース攻撃または辞書攻撃による認証情報の窃取（ここでは `root` ユーザーのパスワード）。
    *   **永続化 (Persistence)**: 侵害したシステムにSSH公開鍵認証によるバックドア（`authorized_keys`への攻撃者の公開鍵追加）を設置し、将来的なパスワードなしのアクセスを確保。これはMITRE ATT&CKのT1098.004 (Account Manipulation: SSH Authorized Keys) に該当します。
    *   **防御回避 (Defense Evasion)**: `chattr` コマンドを使用して、重要なシステムファイル（`.ssh` ディレクトリ）の属性を変更し、監視や改ざん防止機能を回避しようとする試み。これはMITRE ATT&CKのT1562.001 (Impair Defenses: Disable or Modify System Firewall) のような防御変更の一部と見なせます。
*   **使用ツール**:
    *   SSHクライアント機能を持つスクリプトまたは自動化ツール (例: `Hydra`, `Medusa`などのブルートフォースツール、またはカスタムスクリプト)。攻撃は自動化されており、異なるパスワードでのログイン試行からバックドア設置までが迅速に行われています。
    *   標準的なLinuxシェルコマンド (`cd`, `rm`, `mkdir`, `echo`, `chmod`) を利用。
    *   `chattr`, `lockr` など、ファイル属性を変更するコマンドも使用していることから、広範なOSコマンド知識を持つマルウェアまたは攻撃者が関与している可能性を示唆します。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

1.  **重要サービスへの直接攻撃**: SSHはシステム管理において最も重要なリモートアクセスプロトコルの一つであり、これに対するブルートフォース攻撃は高い脅威となります。成功した場合、システムの完全な制御を奪われる可能性があります。
2.  **`root` ユーザーに対する攻撃**: 攻撃者はシステム上で最高の権限を持つ `root` ユーザーを標的としており、このアカウントへの侵害はシステム全体が完全に制御される危険性を意味します。
3.  **永続化の試み**: ログイン成功後に `authorized_keys` ファイルを操作してバックドアを設置しようとすることは、単なる一時的な侵入ではなく、長期的なシステム支配を意図していることを明確に示しています。これにより、攻撃者は検出を回避しながら、いつでもシステムに再アクセスできる状態を作り出そうとします。
4.  **既知の悪用される公開鍵**: ログに含まれる公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) は、インターネット上でMiraiボットネットや他の悪意のある活動で広く使用されている既知の攻撃者の鍵であることが報告されています。これは、この攻撃が大規模なマルウェアキャンペーンの一部である可能性を示唆し、脅威の深刻度を高めます。

### 4. 推奨アクション

1.  **攻撃元IPのブロック**:
    *   攻撃元IPアドレス `43.155.21.198` を組織のファイアウォール、IDS/IPS、またはWAFで即座にブロックし、さらなる通信を遮断します。
2.  **SSHセキュリティ強化（緊急対応）**:
    *   **パスワード認証の無効化**: 可能な限り、パスワード認証を無効化し、公開鍵認証のみを使用するようにSSH設定（`/etc/ssh/sshd_config`）を強化します（`PasswordAuthentication no`）。
    *   **`root` ユーザーのログイン無効化**: `root` ユーザーのSSH直接ログインを無効化します（`PermitRootLogin no`）。必要な場合は`sudo`を使用するようにします。
    *   **SSHポートの変更**: 標準の22番ポートから変更するか、VPN経由でのみアクセスを許可します。
    *   **ブルートフォース対策**: `Fail2ban` などのツールを導入・設定し、不正なログイン試行を検知・遮断するようにします。
    *   **IP制限（ACL）**: 許可されたIPアドレスからのSSHアクセスのみを許可するアクセス制御リスト（ACL）を設定します。
3.  **認証情報の管理と見直し**:
    *   ログに記録されたパスワード (`6yhnji90-`, `3245gs5662d34`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`) は攻撃者が使用したものであり、これらのパスワードが他のシステムやサービスで使われていないか緊急で確認し、もし使用されている場合は即座に強力かつユニークなものへ変更することを推奨します。
4.  **システム監査と侵害調査**:
    *   **広範なログ調査**: 他のSSHログおよび認証ログ（`auth.log`, `secure` など）を広範に調査し、同様の手口で他のシステムが侵害されていないか、不審なログインがないか確認します。
    *   **`authorized_keys`の確認**: すべてのサーバー、特に`root`ユーザーや特権ユーザーのホームディレクトリ内にある `.ssh/authorized_keys` ファイルの内容を確認し、不正な公開鍵が追加されていないかチェックします。特に、この攻撃で用いられた公開鍵（フィンガープリント：`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）がないか確認し、発見された場合は即座に削除します。
    *   **ファイル属性の確認**: 重要なシステムファイルやディレクトリ（特に`/etc`, `/root`, `/home`配下など）の属性を`lsattr`コマンドなどで確認し、`chattr`によって不正に変更されていないか確認します。
    *   **マルウェアスキャン**: Rootkitや他のマルウェアがシステムにインストールされていないか、整合性チェックツール（例: `AIDE`, `Tripwire`）やアンチウイルススキャンを実行します。
5.  **脅威インテリジェンスの活用**:
    *   攻撃元IPアドレス (`43.155.21.198`) と使用された公開鍵情報について、最新の脅威インテリジェンスフィードと照合し、攻撃者の詳細、関連する脅威アクター、および彼らが標的とするシステムの共通点について情報を収集します。
6.  **監視体制の強化**:
    *   SSHログインの成功・失敗、不審なコマンド実行、およびファイルシステム変更（特に`.ssh`ディレクトリ内やシステム設定ファイル）をリアルタイムで監視する仕組みを強化します。SIEMやEDRソリューションを最大限に活用し、異常検知アラートのチューニングを行います。