# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 04:11:06

---

SOCアナリストとして、提供された攻撃ログを分析し、以下のレポートを作成しました。

---

### SOC分析レポート

**インシデント名**: SSHブルートフォース攻撃と持続性確保の試み
**分析日時**: 2026-04-26T01:34:44Z以降
**攻撃元IP**: 182.70.243.207

---

### 1. 攻撃の概要と目的

攻撃元IP `182.70.243.207` から、`2026-04-26T01:17:32Z` から `01:34:44Z` にかけて、SSHサービスに対する一連の自動化された攻撃が観測されました。

**攻撃の主な段階:**

1.  **初期偵察および認証情報の試行**:
    *   まず、`steam` ユーザーでのログイン失敗が記録されています。
    *   その後、`01:26:28Z` から約8分間にわたり、`root`、`345gs5662d34`、`tunnel`、`cloud`、`gitlab` など、複数の一般的なユーザー名やサービス関連のユーザー名、およびランダムな文字列（と思われる）ユーザー名を使用してSSHログイン試行が継続的に行われました。
    *   特に `root` ユーザーに対しては、辞書攻撃またはブルートフォース攻撃によって複数のパスワードが試行されました。
2.  **アカウント侵害 (root)**:
    *   この攻撃中、複数回にわたり、`root` ユーザーとして異なるパスワードでのログインに成功しています（ログ上のパスワード例: `QAZwsx`, `3245gs5662d34`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#`）。
3.  **持続性の確保 (Persistence)**:
    *   ログイン成功後、攻撃者は直ちに以下のコマンドを実行しています。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`：`.ssh` ディレクトリの不変属性・追記属性の解除を試みているようです（`lockr` コマンドは一般的なLinuxコマンドではないため、誤入力か特定のツールの一部である可能性があります）。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`：これは、既存の `.ssh` ディレクトリを削除し、新たに作成した上で、自身のSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を `authorized_keys` に追加し、権限を適切に設定するものです。これにより、パスワードなしでの再侵入経路を確保しようとしました。

**攻撃の目的**:
SSHサービスへの不正ログインを試み、成功した場合は自身のSSH公開鍵を登録することで、将来的なアクセス経路（バックドア）を確立し、システムの永続的な制御を目的としていると考えられます。これは、感染したシステムをボットネットに組み込んだり、さらなる攻撃の中継点として利用したりするための初期段階の活動である可能性が高いです。

---

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース攻撃 / 辞書攻撃**: 大量の異なるユーザー名とパスワードの組み合わせを試行してSSHログインを試みています。特に `root` ユーザーに対して集中的に試行し、複数のパスワードで成功しています。
    *   **持続性の確保 (Persistence)**: ログイン成功後に、SSH公開鍵認証を利用したバックドアを設置しようとしています。これは、一旦システムへのアクセスを確立した後も、パスワード変更などがあってもアクセスを維持するための一般的な手法です。
*   **使用ツール**:
    *   ログの連続性、非常に短い間隔での接続、定型的なコマンド実行パターンから、攻撃者は**自動化されたスクリプトまたはツール**を使用している可能性が高いです。具体的なツール名は特定できませんが、Hydraのようなパスワードクラッキングツールと、その後にバックドア設置スクリプトを組み合わせたもの、またはボットネットの一部である可能性が考えられます。
    *   公開鍵のコメント `mdrfckr` は、攻撃者グループやツールのシグネチャの一部である可能性があります。

---

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:

*   **アカウント侵害の成功**: `root` ユーザーでのログインが複数回成功しており、ハニーポット環境でなければシステムに対する完全な制御が奪われていた可能性が極めて高いです。`root` 権限の奪取は、システムに深刻な影響を与える最大の脅威となります。
*   **持続性の確保の試み**: 攻撃者が `authorized_keys` ファイルに自身の公開鍵を追加しようとしたことは、永続的なアクセス経路を確保し、長期的にシステムを悪用する意図があることを明確に示しています。これにより、一度侵入された場合、パスワードを変更しても攻撃者がアクセスを維持できるリスクが高まります。
*   **自動化された広範囲な攻撃**: 攻撃の頻度とパターンから、これは特定のターゲットを狙った手動攻撃ではなく、広範囲なインターネットスキャンと自動化されたログイン試行の一環であると考えられます。このような攻撃は、脆弱なシステムを探索し、乗っ取られたシステムをボットネットに組み込んだり、さらなる攻撃の中継点として利用したりする目的で行われることが多いです。

---

### 4. 推奨アクション

1.  **攻撃元IPのブロック**:
    *   ファイアウォールやIPS/IDSにて、攻撃元IP `182.70.243.207` からのアクセスを即座にブロックリストに追加してください。
2.  **SSHセキュリティの緊急強化**:
    *   **パスワード認証の無効化**: 可能な限り公開鍵認証のみを許可し、パスワード認証を無効にしてください。
    *   **PermitRootLogin no の設定**: `/etc/ssh/sshd_config` にて `PermitRootLogin no` を設定し、`root` ユーザーの直接ログインを禁止してください。必要であれば一般ユーザーでログイン後、`sudo` を利用するようにしてください。
    *   **多要素認証 (MFA) の導入**: 重要なシステムへのSSHアクセスにはMFAを必須としてください。
    *   **強力なパスワードポリシーの強制**: ユーザー名 `root` でのブルートフォース攻撃が成功しているため、すべてのユーザーアカウント（特に特権アカウント）に対して、複雑で長いパスワードを強制し、定期的な変更を促してください。
    *   **Fail2Banなどの導入**: 複数回のログイン失敗を検知し、一時的または永続的にIPアドレスをブロックするツール（Fail2Banなど）を導入し、設定を最適化してください。
    *   **IP制限**: 信頼できるIPアドレスのみがSSHサービスにアクセスできるよう、ファイアウォールでアクセス元IPを厳しく制限してください。
3.  **既存アカウントの徹底的な監査**:
    *   SSHログインに使用されているすべてのユーザーアカウント（特に `root`）について、不審なログイン履歴がないか、不正な公開鍵が登録されていないかを緊急で確認してください。
    *   全ユーザーの `~/.ssh/authorized_keys` ファイルの内容を精査し、ログに記載された公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）または見覚えのない公開鍵が存在しないか確認し、発見された場合は直ちに削除してください。
4.  **システムログの監視強化とSIEM連携**:
    *   SSHログイン失敗、成功、コマンド実行履歴など、SSH関連のログの監視を強化し、異常を検知した際にアラートを発する体制を構築してください。
    *   CowrieログのようなハニーポットのログをSIEM（Security Information and Event Management）システムに連携し、リアルタイムでの検知・分析能力を強化してください。
5.  **脅威インテリジェンスの活用**:
    *   攻撃元IP `182.70.243.207` や、`mdrfckr` というSSH公開鍵のコメントを既存の脅威インテリジェンスソースと照合し、既知の攻撃グループやマルウェアとの関連性を調査してください。これにより、将来的な攻撃を予測し、防御策を講じるのに役立ちます。

---