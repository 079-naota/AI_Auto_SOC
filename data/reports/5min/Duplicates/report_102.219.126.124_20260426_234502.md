# SOC自動分析レポート: 102.219.126.124

**生成日時:** 2026-04-26 23:47:45

---

SOCアナリストとして、ご提供いただいた攻撃ログを分析し、以下のレポートを作成しました。

---

**SOCセキュリティインシデントレポート**

**レポートID**: SOC-20260426-001
**作成日時**: 2026-04-26T[現在時刻]
**分析者**: SOCアナリスト

### 1. 攻撃の概要と目的

攻撃元IPアドレス `102.219.126.124` から、SSHサービスに対して執拗なブルートフォース攻撃が確認されました。この攻撃では、複数の異なるユーザー名とパスワードの組み合わせが試行され、特に `root` ユーザーに対しては、以下のパスワードで複数回ログインに成功しています。

*   `1qaz@WSX3edc$RFV!@`
*   `3245gs5662d34` (複数回)
*   `ali123456`
*   `Root8`
*   `Aa112211.`
*   `Config123`
*   `Aa123321`

ログイン成功後、攻撃者は以下のコマンドを実行しようとしました。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

これらのコマンドから、攻撃の主な目的は以下の通りと推測されます。

*   **システムへの不正アクセス**: SSHブルートフォース攻撃により、root権限でのログインを試み、成功。
*   **永続的なアクセス経路の確立（バックドア設置）**: `root` ユーザーの `authorized_keys` ファイルに自身の公開鍵 `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` を追加することで、パスワードなしでシステムに再アクセスできるバックドアを設置しようとしています。また、`.ssh` ディレクトリの属性変更(`chattr -ia .ssh`)を試みることで、ファイルの変更を容易にしようとした可能性があります。

### 2. 推測される手法・使用ツール

*   **攻撃手法**:
    *   **SSHブルートフォース攻撃 / 辞書攻撃**: 大量のユーザー名とパスワードの組み合わせを自動的に試行し、SSH認証を突破しようとする手法です。ログから、`drcom`, `ubuntu`, `user` といった一般的なユーザー名や、複数の異なる複雑なパスワードが試行されていることから、広範な辞書攻撃が行われた可能性が高いです。
    *   **アカウント乗っ取り**: `root` ユーザーの認証情報を奪取し、システムの最高権限でのアクセスを実現しました。
    *   **永続化 (Persistence)**: `authorized_keys` にSSH公開鍵を追加することで、システムへの長期的なアクセスを可能にするバックドアを設置しようとしました。これにより、パスワードが変更されたとしても攻撃者はアクセスを維持できます。
    *   **防御回避**: `chattr -ia .ssh` コマンドは、Linuxファイルシステム上の特殊属性（例: `immutable` や `append-only`）を解除しようとするものです。これにより、`authorized_keys` ファイルへの変更を妨げる防御メカニズムを回避しようとしたと考えられます。

*   **使用ツール**:
    *   **自動化されたSSHクライアントまたはスクリプト**: 大量のログイン試行と、ログイン後の定型コマンド実行パターンから、攻撃者はHydraやMedusaなどのブルートフォースツール、またはカスタムスクリプトを使用している可能性が高いです。
    *   特定のSSH公開鍵 (`mdrfckr` というコメント付き) を使用しており、この鍵が特定の攻撃グループやマルウェアに関連付けられている可能性があります。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
1.  **最高権限アカウント (`root`) の侵害**: ログでは、最も機密性の高いアカウントである `root` ユーザーでのログインが複数回成功しており、これはシステムに対する完全な制御権を攻撃者に与える危険性があります。
2.  **永続的なアクセス経路の確立試行**: `authorized_keys` に攻撃者の公開鍵を追加しようとする行為は、バックドアの設置を意図しており、一度侵入が成功すれば、パスワードが変更されても攻撃者が自由に再アクセスできる状態になることを意味します。これは、長期的な脅威に繋がります。
3.  **防御回避の試み**: `chattr -ia .ssh` のようなコマンドの実行は、システム上の防御メカニズムを理解し、それを無効化しようとする高度な意図を示しています。
4.  **継続的な攻撃パターン**: 攻撃者は短期間に異なるパスワードで繰り返しログインを試み、成功するたびにバックドア設置のコマンドを実行しています。これは自動化された、組織的な攻撃である可能性が高いです。
5.  **広範な影響の可能性**: 攻撃に使用されたパスワードが他のシステムでも使用されている場合、組織全体のセキュリティが脅かされる可能性があります。

### 4. 推奨アクション

このログはハニーポット (Cowrie) のものであるため、実際のシステムが侵害されたわけではありませんが、実環境で発生した場合を想定し、以下の推奨アクションを提案します。

#### 4.1. 緊急対応 (Immediate Actions)

1.  **攻撃元IPのブロック**: 攻撃元IPアドレス `102.219.126.124` からのSSH接続を、ファイアウォールやIDS/IPSで直ちにブロックします。
2.  **`root` ユーザーのパスワード変更**: 攻撃ログ内でログインに成功した全てのパスワード (`1qaz@WSX3edc$RFV!@`, `3245gs5662d34`, `ali123456`, `Root8`, `Aa112211.`, `Config123`, `Aa123321`) が他のシステムでも使用されていないか確認し、使用されている場合は即座に複雑で推測困難なパスワードに変更します。特に `root` ユーザーのパスワードは最優先で変更します。
3.  **`authorized_keys` ファイルの確認と不正な鍵の削除**: 全てのユーザーの `.ssh/authorized_keys` ファイルをレビューし、不正なSSH公開鍵（特に`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）が存在しないか確認し、発見した場合は削除します。また、`.ssh` ディレクトリおよびその内容に不正な `chattr` 属性が付与されていないか確認します。
4.  **関連ログの確認**: 過去のSSH認証ログ、システムログ、ネットワークログなどを詳細に確認し、このIPアドレスからの他の不審な活動や、他のユーザーアカウントへのログイン試行がないか調査します。

#### 4.2. 長期的な対策 (Long-term Actions)

1.  **SSHセキュリティ強化**:
    *   **パスワード認証の無効化**: 可能であれば、SSHパスワード認証を無効化し、公開鍵認証のみを許可するように設定します。
    *   **Rootログインの禁止**: `/etc/ssh/sshd_config` で `PermitRootLogin no` を設定し、`root` ユーザーの直接ログインを禁止します。必要な場合は、一般ユーザーでログイン後、`sudo` を使用してroot権限を取得するようにします。
    *   **多要素認証 (MFA) の導入**: 重要なシステムへのSSHアクセスには、MFAの導入を検討します。
    *   **SSHポートの変更**: 標準の22番ポートから非標準のポートに変更することで、自動化されたスキャン攻撃をある程度減らすことができます。
    *   **SSH鍵管理の徹底**: `authorized_keys` ファイルのパーミッションが適切であるか確認し、不必要な鍵が存在しないか定期的にレビューします。
2.  **パスワードポリシーの強化**:
    *   全ユーザーに対して、より複雑で長いパスワードの使用を義務付けます。
    *   定期的なパスワード変更ポリシーを導入します。
    *   アカウントロックアウトポリシーを導入し、一定回数以上のログイン失敗でアカウントを一時的にロックします。
3.  **侵入検知/防御システム (IDS/IPS) の導入と強化**: SSHブルートフォース攻撃を自動的に検知・防御できるIDS/IPSソリューションの導入または設定強化を検討します。
4.  **脅威インテリジェンスの活用**: 攻撃に使用されたSSH公開鍵のフィンガープリントやコメント (`mdrfckr`) を脅威インテリジェンスプラットフォームと照合し、既知の攻撃グループやマルウェアとの関連性を調査します。
5.  **セキュリティ監視の強化**: SIEM (Security Information and Event Management) システムを導入し、SSHログイン試行、成功、コマンド実行ログなどをリアルタイムで監視する体制を強化します。
6.  **ハニーポットの活用**: 今回のようにCowrieのようなハニーポットを引き続き運用し、攻撃者の手法や使用する認証情報、コマンドパターンを継続的に収集・分析することで、将来の攻撃への対策に役立てます。

---
このレポートが、今後のセキュリティ対策の一助となれば幸いです。