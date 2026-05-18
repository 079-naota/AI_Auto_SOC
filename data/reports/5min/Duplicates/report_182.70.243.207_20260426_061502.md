# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 06:16:14

---

## SOC分析レポート

**分析日時:** 2026-04-26T01:34:44Z以降 (ログ終了時点)
**攻撃元IP:** 182.70.243.207
**攻撃対象サービス:** SSH (TCP/22)
**ログソース:** Cowrie (SSHハニーポット)

---

### 1. 攻撃の概要と目的

攻撃元IP `182.70.243.207` から、当方ハニーポットシステムに対するSSHブルートフォース/辞書攻撃が行われました。攻撃者は複数の異なるユーザー名とパスワードを試行し、特に `root` ユーザーのパスワードを複数回突破しています。

ログイン成功後、攻撃者はシステムへの永続的なアクセス経路を確立しようと、`~/.ssh/authorized_keys` に自身の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を追加するコマンドを繰り返し実行しています。また、`chattr`や`lockr`コマンドで`.ssh`ディレクトリの属性変更も試みており、バックドアの隠蔽やアクセス権限の強化も意図していると推測されます。

この攻撃の目的は、標的システムへの不正な特権アクセスを獲得し、バックドアを設置することで長期的なコントロールを確立することにあります。

---

### 2. 推測される手法・使用ツール

*   **手法:**
    *   **ブルートフォース/辞書攻撃:** `steam`, `tunnel`, `cloud`, `gitlab`などの一般的なユーザー名や、`QAZwsx`, `3245gs5662d34`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#`といった多様なパスワードを繰り返し試行し、`root`ユーザーでのログイン成功を複数回達成しています。これは自動化された広範なパスワード推測攻撃を示唆しています。
    *   **永続化 (Persistence):** ログイン成功後、`rm -rf .ssh && mkdir .ssh && echo "..." >> .ssh/authorized_keys && chmod -R go= ~/.ssh`という一連のコマンドを実行し、攻撃者の公開鍵を`authorized_keys`に追加することで、パスワードなしでのSSHログインを可能にするバックドアを設置しようとしています。これはシステムへの長期的なアクセスを目的とした典型的な手口です。
    *   **痕跡隠蔽/強化の試行:** `chattr -ia .ssh; lockr -ia .ssh`というコマンドも実行しており、`.ssh`ディレクトリに対する変更不可属性や追加のみ属性を解除し、ファイルの操作性を高めたり、不正な変更を隠蔽したりする意図が推測されます。（ただし、`lockr`コマンドは失敗しています。）
*   **使用ツール:**
    *   **SSHクライアント:** 攻撃者がSSH接続を確立するために使用。
    *   **自動化されたブルートフォースツール/スクリプト:** 連続的かつ組織的なログイン試行パターンから、HydraやMedusaのようなSSHブルートフォースツール、またはカスタムスクリプトが使用されている可能性が高いです。
    *   **公開鍵ペア:** 永続化のために、`mdrfckr`というコメントが付与された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を用意して使用しています。

---

### 3. 脅威レベルとその理由

*   **脅威レベル:** **高 (Critical)**
*   **理由:**
    1.  **root権限の奪取:** 攻撃者は最上位の特権を持つ`root`ユーザーとして複数回ログインに成功しており、これはシステム全体を完全に制御される可能性を意味します。現実のシステムであれば、情報窃取、システム破壊、マルウェア感染、他のシステムへの攻撃拠点化など、甚大な被害につながる恐れがあります。
    2.  **永続化の試行:** 攻撃者がバックドア（公開鍵認証）の設置を試みていることから、一度システムを掌握した後に、検出や対策が講じられても再侵入する準備をしていたことが分かります。これにより、侵害からの復旧が困難になるリスクが高まります。
    3.  **自動化された攻撃:** 攻撃は断続的かつ自動化されており、特定のシステムへの標的型攻撃というよりは、広範囲なスキャンとブルートフォース攻撃の一部である可能性が高いです。これは、攻撃者が複数のシステムへのアクセスを確立しようとしていることを示唆します。
    4.  **複数の有効なパスワードの発見:** 攻撃者は一貫して同じパスワードでログインするのではなく、複数の異なる`root`パスワードを見つけており、その辞書攻撃の有効性が高いか、または豊富なクレデンシャルリストを利用していることを示しています。

---

### 4. 推奨アクション

このログはハニーポットからのものであるため、実際にシステムが侵害されたわけではありませんが、現実のシステムであれば深刻な侵害に至っていたことを前提に、以下の推奨アクションを提案します。

1.  **攻撃元IPのブロック:**
    *   攻撃元IPアドレス `182.70.243.207` をファイアウォール、IDS/IPS、WAF、またはセキュリティグループ等で即座にブロックリストに追加し、今後のアクセスを遮断します。
    *   必要であれば、このIPアドレスが属するASや地域からのアクセスも制限することを検討します。
2.  **既存システムに対する緊急監査と脆弱性診断:**
    *   **SSHサービスの設定確認:** 全てのLinux/Unixサーバー上でSSHサービスの設定（`/etc/ssh/sshd_config`など）をレビューします。
        *   **`PermitRootLogin no`** を設定し、`root`ユーザーの直接ログインを禁止します。
        *   **パスワード認証の無効化** (`PasswordAuthentication no`) を検討し、可能な限り公開鍵認証のみに制限します。
        *   **強力なパスワードポリシー** を適用し、既存のユーザーパスワードがブルートフォースされにくいものか確認・強化を促します。
        *   **多要素認証 (MFA)** の導入を検討します。
    *   **`authorized_keys` ファイルの確認:** 全てのユーザーの `~/.ssh/authorized_keys` ファイルを監査し、本ログに記載された公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) やその他の不審な鍵が追加されていないか確認し、削除します。
    *   **アカウントロックアウトの設定:** 短時間でのログイン失敗回数に応じたアカウントロックアウト（例: `pam_faillock`や`fail2ban`の導入）を有効にします。
    *   **既知の脆弱性スキャン:** SSHサービスを含む全ての公開サービスに対して、脆弱性スキャンを実行し、設定不備やソフトウェアの脆弱性を洗い出して修正します。
3.  **ログ監視の強化:**
    *   SSHログインログ（`auth.log`など）の監視を強化し、異常なログイン試行パターン（特に`root`ユーザーに対する試行）や、予期しない時間帯・IPアドレスからのログイン成功をリアルタイムで検知できるアラートを設定します。
    *   重要なシステムファイル（例: `~/.ssh/authorized_keys`）への変更を監視するFIM (File Integrity Monitoring) ソリューションの導入を検討します。
4.  **脅威インテリジェンスの活用:**
    *   攻撃に使用されたIPアドレス、公開鍵のフィンガープリント、ユーザー名、成功したパスワードなどを脅威インテリジェンスプラットフォームで検索し、既知のマルウェアキャンペーンや攻撃グループとの関連性を調査します。
    *   特に公開鍵のコメント `mdrfckr` は、攻撃グループを特定する手がかりになる可能性があります。
5.  **セキュリティ意識向上トレーニング:**
    *   システム管理者や特権ユーザーに対し、パスワード管理の重要性やフィッシング、ソーシャルエンジニアリングに対するセキュリティ意識向上トレーニングを実施します。

---
以上。