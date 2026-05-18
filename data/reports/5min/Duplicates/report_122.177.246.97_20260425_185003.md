# SOC自動分析レポート: 122.177.246.97

**生成日時:** 2026-04-25 18:51:19

---

## SOCアナリストレポート

### 攻撃ログ分析レポート

**日付**: 2026年04月25日
**分析者**: SOCアナリスト
**関連IPアドレス**: 122.177.246.97

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `122.177.246.97` から、ターゲットシステム（Cowrieハニーポット）のSSHサービスに対して、断続的なブルートフォース/辞書攻撃が行われました。攻撃者は複数のユーザー名とパスワードの組み合わせを試行し、最終的に `root` ユーザーの複数の認証情報（`ccQQ123`, `3245gs5662d34`, `AAaa112233`, `Master2025`）の特定に成功しました。

ログイン成功後、攻撃者は以下のコマンドを繰り返し実行し、システムへの永続的なアクセス経路（バックドア）を確立しようと試みました。
1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`

これらの行動から、攻撃の主な目的は、SSH公開鍵をターゲットシステムの `root` ユーザーの `authorized_keys` ファイルに追加することで、パスワード認証なしでいつでもシステムに再侵入できるバックドアを設置し、永続的なアクセス権を確保することであると推測されます。

### 2. 推測される手法・使用ツール

*   **ブルートフォース/辞書攻撃**:
    *   `deployer`, `deploy`, `vnc`, `345gs5662d34`, `root` といった一般的なユーザー名に加え、複数の異なるパスワードを短時間で試行していることから、自動化されたパスワードクラッキングツール（例: Hydra, Nmapのssh-bruteスクリプトなど）が使用されている可能性が高いです。
*   **バックドア設置（永続化）**:
    *   `root` ユーザーとしてログイン成功後、`.ssh` ディレクトリを操作し、攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) を `authorized_keys` に書き込もうとしています。これにより、攻撃者はパスワード認証なしでSSH接続が可能になります。
    *   `chattr -ia .ssh` はファイル属性を変更し、`.ssh` ディレクトリの不変属性などを解除することで、ファイルの改ざんを容易にしようとする試みです。`lockr` は標準的なLinuxコマンドではないため、タイプミスか、特定の環境依存コマンドを試行した可能性があります。
*   **権限昇格の試み**:
    *   `root` ユーザーアカウントに対する集中的な攻撃と、その認証情報の奪取成功から、攻撃者はシステムに対する最高レベルの権限（管理者権限）の獲得を意図していることが明らかです。

### 3. 脅威レベルとその理由

**脅威レベル: 重大 (Critical)**

**理由**:
1.  **root権限の奪取**: 攻撃者はシステムの最高権限である `root` ユーザーの複数の認証情報（`ccQQ123`, `3245gs5662d34`, `AAaa112233`, `Master2025`）を特定し、ログインに成功しています。これは、もしこれが本物のシステムであれば、攻撃者がシステムに対して完全な制御権を獲得したことを意味します。
2.  **永続的アクセスの確立**: 攻撃者はログイン成功後、直ちにSSH公開鍵を `root` ユーザーの `authorized_keys` ファイルに書き込むことで、恒久的なバックドアを設置しようと試みました。これにより、パスワードが変更されたとしても、攻撃者は秘密鍵を使い自由にシステムへ再侵入できる状態を作り出そうとしています。
3.  **自動化された広範な攻撃**: ログのタイムスタンプと試行回数から、攻撃は自動化されたツールによって行われている可能性が高く、特定のターゲットを狙ったものではなく、インターネットに露出した脆弱なSSHサービスを探索・悪用する広範な攻撃キャンペーンの一部であると考えられます。
4.  **深刻な二次被害の可能性**: 仮に本物のシステムが侵害された場合、攻撃者はデータの窃取、マルウェアの展開、システムの破壊、他のシステムへの攻撃拠点としての利用など、あらゆる悪意のある活動を行うことが可能となります。

### 4. 推奨アクション

このログはハニーポットの記録であるため、実際のシステム侵害には至っていませんが、もしこのような脆弱性が本番環境に存在する場合、以下の緊急および恒久的な対策が必須です。

#### (1) 緊急対応 (Immediate Actions)

*   **攻撃元IPの即時ブロック**: 攻撃元IPアドレス `122.177.246.97` をファイアウォールやIDS/IPSで直ちにブロックリストに追加し、今後のアクセスを拒否します。
*   **SSHパスワード認証の無効化**: 可能な限り速やかに、SSHサービスにおけるパスワード認証を無効化し、SSH鍵認証のみの使用に限定します。
*   **`root`ユーザーによるSSHログインの禁止**: SSH設定ファイル (`/etc/ssh/sshd_config` など) にて `PermitRootLogin no` を設定し、`root`ユーザーによる直接のSSHログインを禁止します。特権操作が必要な場合は、一般ユーザーでログイン後、`sudo` を利用する運用に切り替えます。
*   **漏洩パスワードの緊急変更**: ログに記録されたログイン成功パスワード (`ccQQ123`, `3245gs5662d34`, `AAaa112233`, `Master2025`) がもし本番環境のシステムや他のサービスで使われている場合、直ちにそれらのパスワードを、より複雑で推測されにくい新しいパスワードに変更します。
*   **類似環境の緊急監査**: このハニーポットと同様のSSH設定（特に弱いパスワードの使用）を持つ他の本番環境のシステムについて、同様のログイン試行やバックドア設置の痕跡がないか、緊急でログを確認・調査します。特に `root` ユーザーの `~/.ssh/authorized_keys` ファイルの内容を確認し、見覚えのない公開鍵が存在しないかチェックします。

#### (2) 恒久対策 (Long-term Actions)

*   **強力なパスワードポリシーの徹底**:
    *   全てのシステムアカウントに対し、長さ、大文字、小文字、数字、記号を含む複雑なパスワードの使用を義務付けます。
    *   定期的なパスワード変更を推奨または強制します。
    *   一般的なパスワードや辞書攻撃で推測されやすいパスワードの使用を禁止するポリシーを導入します。
*   **多要素認証 (MFA) の導入**: SSHログインにおいて、パスワード認証に加えて多要素認証を導入することで、セキュリティを大幅に強化します。
*   **SSH鍵認証の厳格な運用**:
    *   SSH鍵認証を導入し、公開鍵と秘密鍵を適切に管理します（秘密鍵へのパスフレーズ設定、アクセス権限の厳格化など）。
    *   不要なSSH公開鍵は定期的に削除します。
*   **不正ログイン試行の監視強化**:
    *   `fail2ban` のような侵入検知・防止システム (IDS/IPS) を導入し、不正なSSHログイン試行を検知・自動ブロックする仕組みを構築します。
    *   SSHログをSIEM (Security Information and Event Management) システムに集約し、異常なログイン試行やコマンド実行をリアルタイムで監視・分析する体制を確立します。
*   **不要なサービスの停止・アクセス制限**:
    *   SSHサービスがインターネットに公開されている必要がない場合は、VPN経由でのアクセスに限定するか、サービスを停止します。
    *   SSHポートを標準の22番から変更することも一時的な対策にはなりますが、根本的な解決にはなりません。
*   **脅威インテリジェンスの活用**: 攻撃に使用されたSSH公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) のフィンガープリントや攻撃元IPアドレスを脅威インテリジェンスプラットフォーム（例: VirusTotal, Shodanなど）と照合し、関連する他の攻撃情報やマルウェアキャンペーンがないか調査します。