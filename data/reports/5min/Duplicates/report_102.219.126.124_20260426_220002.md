# SOC自動分析レポート: 102.219.126.124

**生成日時:** 2026-04-26 22:03:01

---

## セキュリティインシデント分析レポート

**報告日時**: 2026-04-26T08:00:00Z
**分析対象**: SSHハニーポット（Cowrie）攻撃ログ
**攻撃元IP**: 102.219.126.124

---

### 1. 攻撃の概要と目的

攻撃元IP `102.219.126.124` から、当ハニーポットシステムに対し継続的なSSHブルートフォース/辞書攻撃が行われました。攻撃者は複数のユーザー名とパスワードを試行し、最終的に `root` ユーザーの認証情報を複数回突破することに成功しています。

ログイン成功後、攻撃者は以下の2つの主要な目的を達成しようと試みています。

1.  **永続的なアクセスの確立（バックドアの設置）**: SSH公開鍵認証を利用して、自身の公開鍵をシステム上の `root` ユーザーの `authorized_keys` ファイルに埋め込むことで、パスワードなしで将来的にシステムへアクセスできるバックドアを設置しようとしています。
2.  **既存のアクセス障壁の除去**: `chattr -ia .ssh` コマンドにより、`~/.ssh` ディレクトリの不変属性 (immutable/append-only) を無効化し、自身の公開鍵書き込みを妨げる可能性のある設定を解除しようとしています。`lockr` コマンドも同様の目的で実行されていますが、これはシステムに存在しないコマンドのようです。

この一連の攻撃は、システムへの不正アクセスと永続的な制御奪取を企図した、典型的な初期アクセスおよび永続化のフェーズに該当します。

### 2. 推測される手法・使用ツール

*   **認証情報攻撃 (Credential Stuffing / Brute-force / Dictionary Attack)**: ログには `drcom:drcom123` や `ubuntu:Aa12345!` のような一般的なユーザー名とパスワードの組み合わせ、および `root` ユーザーに対して複数の強力なパスワード（例: `1qaz@WSX3edc$RFV!@`, `ali123456`, `Root8`, `Aa112211.`, `Config123`, `Aa123321`）を試行し、ログイン成功を繰り返している記録があります。これは、事前に取得した認証情報リスト（Credential Stuffing）や、辞書攻撃、あるいはブルートフォース攻撃を組み合わせて行われた可能性が高いです。
*   **永続化 (Persistence)**:
    *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
        この一連のコマンドは、既存の `.ssh` ディレクトリを削除し、新たに作成したディレクトリに攻撃者の公開鍵（コメント: `mdrfckr`）を `authorized_keys` として設置し、適切なパーミッションを設定することで、公開鍵認証によるバックドアを確立しようとするものです。
    *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`
        このコマンドは、`.ssh` ディレクトリの属性を変更し、書き込み権限を保護する可能性のある設定を解除しようとしています。特に `chattr -ia` はimmutable/append-only属性を解除するもので、`lockr` は攻撃者が特定の環境向けに用意したコマンドであるか、一般的なLinux環境には存在しないコマンドです。
*   **使用ツール**: 攻撃ログに見られる自動化された一連の動作（ログイン試行、コマンド実行、ログアウト）から、HydraやNmapなどの認証情報攻撃ツールと連携した自動化スクリプトやボットが使用されている可能性が高いと推測されます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由:**

*   **認証突破の成功**: 攻撃者はシステム最高権限である `root` ユーザーとして複数回ログインに成功しています。これは、実際のシステムであれば、攻撃者がシステムに対する完全な制御権を獲得したことを意味します。
*   **永続化の試み**: ログイン成功後、攻撃者は直ちに `authorized_keys` ファイルへの不正な公開鍵の埋め込みを試みています。これにより、たとえパスワードが変更されたとしても、攻撃者は公開鍵認証を利用してシステムへのアクセスを維持できる状態になるため、非常に深刻なバックドアが設置されることになります。
*   **攻撃の自動化と継続性**: 短時間で複数の認証情報試行とそれに続くコマンド実行を繰り返していることから、攻撃は自動化されており、継続的な侵害活動の一環である可能性が高いです。
*   **広範な影響の可能性**: 実際の環境でこの攻撃が成功した場合、システムデータの窃取、改ざん、破壊、ランサムウェアの展開、他の内部システムへの横展開（ラテラルムーブメント）、外部へのDDoS攻撃の中継点としての利用など、極めて重大な被害が発生する可能性があります。

### 4. 推奨アクション

このログはハニーポットのものであるため、システム自体は侵害されていませんが、実際のシステムで同様の事象が発生したと仮定して、以下の推奨アクションを提案します。

#### 即時対応 (Immediate Actions):

1.  **攻撃元IPのブロック**: `102.219.126.124` からの全てのインバウンド通信（特にSSHポート22）をファイアウォールで即座にブロックします。
2.  **緊急パスワードリセット**: `root` ユーザーを含む、ログに記載されているログイン成功時のユーザー名（このケースでは主に `root`）のパスワードを直ちに複雑で推測困難なものに変更します。
3.  **不正なSSH鍵の確認と削除**: `/root/.ssh/authorized_keys` ファイルおよび他の特権ユーザーの `~/.ssh/authorized_keys` ファイルの内容を精査し、不正な公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` を含む）がないか確認し、発見した場合は直ちに削除します。
4.  **システムログの確認**: 侵害された可能性のある期間（2026-04-26T07:33:00Z以降）のSSH認証ログ (`/var/log/auth.log` や `journalctl`) を詳細に確認し、他の不正なログイン試行や成功がないか、また不審なコマンド実行履歴がないか調査します。
5.  **不審なアクティビティの検出**: 認証成功後に実行されたコマンド以外に、不審なプロセス、ネットワーク接続、ファイル変更がないか確認します。`chattr` コマンドの実行履歴も確認します。

#### フォレンジック調査 (Forensic Investigation):

1.  **影響範囲の特定**: 攻撃者が他にどのような操作を行ったか、どのファイルにアクセスしたか、他のシステムへの接続を試みたかなど、侵害の範囲と深さを特定するための詳細なフォレンジック調査を実施します。
2.  **公開鍵の脅威インテリジェンス化**: 攻撃者が使用した公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を脅威インテリジェンスとして登録し、他のシステムやログでこの鍵が発見されないか継続的に監視します。

#### 再発防止策 (Preventative Measures):

1.  **SSHセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能な限り公開鍵認証のみに移行し、パスワード認証を無効化します。
    *   **rootログインの禁止**: `/etc/ssh/sshd_config` で `PermitRootLogin no` を設定し、`root` ユーザーの直接ログインを禁止します。一般ユーザーでログイン後、`sudo` を利用して特権操作を行う運用に切り替えます。
    *   **Fail2Banの導入**: ブルートフォース攻撃を自動で検出し、攻撃元IPを一定時間ブロックする `Fail2Ban` などのツールを導入します。
    *   **ポート変更**: 標準のSSHポート22番から、非標準のポートに変更することを検討します（ただし、これは恒久的な解決策ではなく、一時的なノイズ軽減策です）。
    *   **多要素認証 (MFA) の導入**: SSHログインに多要素認証を導入し、セキュリティを大幅に強化します。
2.  **強力なパスワードポリシー**: 定期的なパスワード変更を義務付け、複雑性要件を満たす強力なパスワードポリシーを徹底します。
3.  **不要なサービスの停止/ユーザーの削除**: システム上で稼働している不要なサービスや、未使用のユーザーアカウントを特定し、停止または削除します。
4.  **セキュリティ監視の強化**: ログ監視システムを導入し、異常なログイン試行、認証成功、特権操作、不審なファイル変更などをリアルタイムで検知・アラートできる体制を構築します。
5.  **定期的な脆弱性診断とパッチ適用**: システムおよびアプリケーションの脆弱性診断を定期的に実施し、発見された脆弱性には速やかにパッチを適用します。