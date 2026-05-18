# SOC自動分析レポート: 43.155.21.198

**生成日時:** 2026-04-27 09:00:34

---

## SOC分析レポート

### 1. 攻撃の概要と目的

提供されたCowrie（ハニーポット）ログの分析結果、攻撃元IPアドレス `43.155.21.198` からのSSHサービスに対する継続的な攻撃が確認されました。この攻撃は、主に以下の2つの目的を達成しようとしていたと推測されます。

*   **不正ログインの試み**: ターゲットシステム（ハニーポット）の `root` アカウントへのパスワードによる不正ログインを試みています。複数の異なるパスワードを短期間に繰り返し試行しており、これはブルートフォース攻撃または辞書攻撃の兆候です。
*   **永続的なアクセス経路の確立**: `root` アカウントでのログインに成功した後、自身のSSH公開鍵をターゲットの `~/.ssh/authorized_keys` ファイルに追加しようとしています。これにより、次回以降のアクセスにおいてパスワード認証なしでSSH接続が可能となり、システムの永続的な制御を確立することを目的としています。

攻撃は2026年04月27日03:31:15Zから03:39:09Zまでの約8分間にわたり、連続的に実行されました。

### 2. 推測される手法・使用ツール

攻撃者は、以下の手法および自動化ツールを使用していると推測されます。

*   **ブルートフォース/辞書攻撃**: `root` ユーザーに対して、`6yhnji90-`, `3245gs5662d34`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234` など、複数の異なるパスワードを試行しています。これは、HydraやMedusaのようなSSHブルートフォースツール、あるいはカスタムスクリプトによる辞書攻撃と見られます。
*   **SSH公開鍵認証による永続化**: ログイン成功後のセッションで、攻撃者は以下のコマンドを実行しようとしています。
    `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`
    このコマンドは、既存の `.ssh` ディレクトリを削除し、新しいディレクトリを作成した上で、攻撃者のSSH公開鍵（コメント `mdrfckr` を含む）を `authorized_keys` に書き込み、適切なパーミッションを設定するものです。これは、SSHによるバックドアを設置する一般的な手法です。
*   **ファイル属性変更の試み**: 攻撃者はまた、`chattr -ia .ssh; lockr -ia .ssh` のようなコマンドも試みています。これは、`authorized_keys` ファイルへの変更を妨げる可能性のあるimmutable (不変) 属性やappend-only (追記のみ) 属性を解除しようとする試みです。`lockr` は一般的なLinuxコマンドではないため、誤入力かハニーポットが認識しないコマンドである可能性があります。
*   **自動化された攻撃スクリプト**: 一連のログイン試行とコマンド実行が非常に短時間に繰り返されていることから、攻撃全体が自動化されたスクリプトまたはボットネットの一部によって行われていると判断されます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:

*   **特権アカウント (root) への標的**: 攻撃者はシステム上で最高の権限を持つ `root` アカウントを執拗に狙っており、もしこれが実際のシステムであった場合、ログイン成功によりシステムは完全に侵害された状態になります。
*   **永続化の試み**: 攻撃は単なる侵入だけでなく、自身のSSH公開鍵を設置して永続的なアクセス経路を確保しようとしています。これにより、一度侵害に成功すれば、その後の検出や排除が非常に困難になります。
*   **自動化された攻撃**: 広範囲なシステムを対象とした自動化された攻撃である可能性が高く、防御が手薄なシステムは容易に標的となり得ます。
*   **潜在的な影響の深刻さ**: 実際のシステムでこの攻撃が成功した場合、以下の深刻な被害が想定されます。
    *   機密データの窃取、改ざん、破壊
    *   システム設定の変更、マルウェアのインストール
    *   システムが他の攻撃の踏み台として利用される
    *   サービス停止やシステムダウン

### 4. 推奨アクション

この攻撃の深刻度を踏まえ、以下の緊急および予防措置を推奨します。

#### 緊急対応

1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `43.155.21.198` からのすべての通信を、ファイアウォールやセキュリティグループで即座にブロックしてください。
2.  **既存のrootパスワードの確認とリセット**: ログに記録された `root` ユーザーで「成功」したパスワード (`6yhnji90-`, `3245gs5662d34`, `Pan5202614`, `zhaojia`, `P@$$w0rd12`, `Login!@456`, `mail@1234`) が、もし実際のシステムで使用されている場合は、直ちにパスワードを強力なものに変更してください。また、これらのパスワードが他のサービスで使い回されていないか確認し、使用されている場合は同様にリセットしてください。
3.  **rootアカウントの`.ssh/authorized_keys`ファイルの確認**: 実際のサーバーの `root` ユーザーの `~/.ssh/authorized_keys` ファイルに、ログに記録された攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) と一致するエントリがないか確認してください。もし発見された場合は、直ちに削除し、ファイルパーミッションを `600` に設定してください。

#### 予防措置

1.  **SSHパスワード認証の無効化**: 可能な限り、パスワード認証を無効にし、公開鍵認証のみを許可するようにSSHサーバーを設定してください。これにより、パスワードブルートフォース攻撃のリスクを根本的に排除できます。
2.  **多要素認証 (MFA) の導入**: SSHログインに多要素認証を導入し、セキュリティを強化してください。
3.  **強力なパスワードポリシーの強制**: 全てのユーザーに対し、複雑なパスワード（長さ、文字種混合）の使用を義務付け、定期的な変更を促してください。辞書攻撃で破られやすいパスワード（例: `1234qwer`, `zhaojia` など）は許可しないようにポリシーを設定してください。
4.  **SSHログの継続的な監視とアラート設定**:
    *   SSHログイン失敗回数の閾値設定を行い、異常なログイン試行を自動的に検知・ブロックする（例: Fail2banの導入）。
    *   `root` ユーザーへのログイン試行、または `authorized_keys` ファイルへの変更などのセキュリティ関連イベントについて、リアルタイムアラートを設定してください。
5.  **システムセキュリティの強化**:
    *   **OS/ソフトウェアの定期的なアップデート**: 既知の脆弱性を悪用した攻撃を防ぐため、常に最新の状態に保ってください。
    *   **不要なサービスの停止**: 攻撃対象となるリスクを減らすため、使用していないサービスは停止してください。
    *   **セキュリティ設定の見直し**: SSHポートの変更（非標準ポートへの変更）、AllowUsers/DenyUsers設定、PermitRootLogin noの設定など、SSHサーバーのセキュリティ設定を見直してください。
6.  **C2サーバー/既知の脅威アクターの調査**: 攻撃者が設置しようとしたSSH公開鍵のフィンガープリント（`SHA256:ArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を基に、公開データベースや脅威インテリジェンスソースで既知の攻撃グループやキャンペーンとの関連性を調査してください。