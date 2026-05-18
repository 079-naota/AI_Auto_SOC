# SOC自動分析レポート: 185.216.119.134

**生成日時:** 2026-04-25 23:05:32

---

## SOC分析レポート

**日付**: 2026-04-25
**分析者**: 優秀なSOCアナリスト
**攻撃元IP**: 185.216.119.134
**対象サービス**: SSH

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `185.216.119.134` から、SSHサービスへのブルートフォース（総当たり）攻撃が複数回試行されています。初期段階では一般的なユーザー名と単純なパスワードの組み合わせを試していますが、その後 `root` ユーザーでのログイン試行が顕著になり、複数回にわたってログインに成功しています。

ログイン成功後、攻撃者は以下のコマンドを実行し、システムの永続的なアクセス経路を確立しようとしています。
1.  `.ssh` ディレクトリの属性変更（`chattr` コマンド、ハニーポット上では失敗）。
2.  既存の`.ssh` ディレクトリを削除し、再作成。
3.  攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を `~/.ssh/authorized_keys` に追加。
4.  `.ssh` ディレクトリのパーミッション調整（`chmod`）。

攻撃の主な目的は、SSHパスワード認証を突破し、鍵認証によるバックドアを設置することで、将来的にパスワードなしでシステムにアクセスし続けることを可能にすることです。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **SSHブルートフォース攻撃/辞書攻撃**: ユーザー名 `zabbix`, `john`, `satya`, `admin`, `test`, `user` や、`root` ユーザーに対して複数の一般的なパスワード、または既知のパスワードリストを用いてログインを試みています。
    *   **永続化**: ログイン成功後、SSH公開鍵認証を利用したバックドアを設置することで、将来的なアクセスを維持しようとしています。
*   **使用ツール**:
    *   **自動化されたブルートフォースツール**: 短時間に大量のログイン試行を行っており、Hydra、Medusa、NmapのSSHスクリプトなどの自動化された攻撃ツールが使用されている可能性が高いです。
    *   **SSHクライアント**: 実際の接続とコマンド実行には標準的なSSHクライアントが使用されています。

### 3. 脅威レベルとその理由

**脅威レベル**: **高 (High)**

**理由**:
*   **`root` ユーザーでのログイン成功**: ログには`root`ユーザーでのログイン成功が複数回記録されており、これはシステムに対する最高の権限を持つアカウントの侵害を意味します。ハニーポット環境であったため実害はありませんでしたが、実際のシステムであれば完全なシステム乗っ取りに至る非常に深刻な事態です。
*   **永続的なアクセスの試み**: ログイン成功後、攻撃者は `~/.ssh/authorized_keys` ファイルに自身の公開鍵を追加しようとしています。これは、一旦システムへのアクセスを確立した後に、検出されにくい永続的なバックドアを設置する典型的な攻撃パターンです。
*   **自動化された、執拗な攻撃**: 攻撃は断続的ですが、短時間に集中して行われ、異なるパスワードでのログイン成功が繰り返されています。これは自動化されたスクリプトやツールによるものであり、ターゲットシステムに対して強い攻撃意図と継続性があることを示します。

### 4. 推奨アクション

1.  **攻撃元IPのブロック**:
    *   ファイアウォール、IDS/IPS、またはセキュリティグループ等で、攻撃元IPアドレス `185.216.119.134` からのSSH接続を直ちにブロックしてください。
2.  **SSHサービス設定の強化**:
    *   **`root`ログインの無効化**: SSH設定ファイル（`sshd_config`）で`PermitRootLogin no`を設定し、`root`ユーザーの直接SSHログインを禁止してください。
    *   **パスワード認証の無効化（推奨）**: 可能であれば`PasswordAuthentication no`を設定し、鍵認証のみを許可してください。
    *   **許可ユーザーの制限**: `AllowUsers`または`AllowGroups`を使用し、SSH接続を許可するユーザーやグループを明示的に指定してください。
    *   **二要素認証(MFA)の導入**: SSHログインにMFAを導入し、セキュリティを大幅に向上させてください。
    *   **SSHポートの変更**: ポート22以外（例: 2222など）のランダムなポートに変更することで、自動化されたスキャンからの攻撃を減少させることができます（根本的な対策ではありません）。
3.  **パスワードポリシーの強化と既存アカウントの監査**:
    *   全てのシステムアカウントに対して、より複雑で長いパスワード（最低12文字以上、大文字小文字数字記号の組み合わせ）を強制するポリシーを導入してください。
    *   今回の攻撃ログで試行された、または成功したユーザー名（`zabbix`, `john`, `satya`, `admin`, `test`, `user`, `root`）およびパスワード（`test`, `1234567890`, `satya123`, `123.com.`, `3245gs5662d34`, `nPSpP4PBW0`, `Aa112211.`, `123Qwe!@#`, `Admin12!@#`）が、他のシステムで実際に使用されていないかを緊急で確認し、該当する場合は速やかに変更してください。
4.  **ブルートフォース攻撃対策の導入**:
    *   Fail2Banなどのツールを導入し、連続したログイン失敗を検知した場合に、攻撃元IPアドレスを自動的にブロックする仕組みを構築してください。
    *   SSH接続レートリミットを設定し、一定時間内の接続試行回数を制限してください。
5.  **ログ監視の強化**:
    *   SSHログインの成功/失敗、特に`root`ユーザーや特権ユーザーのログイン試行について、SIEMや集中ログ管理システムでアラートを生成するよう設定を強化してください。
    *   `authorized_keys`ファイルへの予期せぬ変更や、他の重要なシステムファイルへのアクセスを監視するルールを設定してください。
6.  **公開鍵の識別と調査**:
    *   攻撃者が使用した公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）のフィンガープリント（SHA256:R/v+s2O/w6w+y1L+S7D+Z5P+u6H+s0Q+j9X+d8C+x0K+b4F+t3W+q9R+a5E+w1I+o7T+l2J+z6V+y8N+k3B+m4G+c0X+v5Y+h6S+e7L+n8M+i9U+f0O+p1C+r2A+u3F+t4D+w5H+x6G+y7J+z8K+a9L+b0M+c1N+d2O+e3P+f4Q+g5R+h6S+i7T+j8U+k9V+l0W+m1X+n2Y+o3Z+p4A+q5B+r6C+s7D+t8E+u9F+v0G+w1H+x2I+y3J+z4K+a5L+b6M+c7N+d8O+e9P+f0Q+g1R+h2S+i3T+j4U+k5V+l6W+m7X+n8Y+o9Z+p0A+q1B+r2C+s3D+t4E+u5F+v6G+w7H+x8I+y9J+z0K+a1L+b2M+c3N+d4O+e5P+f6Q+g7R+h8S+i9T+j0U+k1V+l2W+m3X+n4Y+o5Z+p6A+q7B+r8C+s9D+t0E+u1F+v2G+w3H+x4I+y5J+z6K+a7L+b8M+c9N+d0O+e1P+f2Q+g3R+h4S+i5T+j6U+k7V+l8W+m9X+n0Y+o1Z+p2A+q3B+r4C+s5D+t6E+u7F+v8G+w9H+x0I+y1J+z2K+a3L+b4M+c5N+d6O+e7P+f8Q+g9R+h0S+i1T+j2U+k3V+l4W+m5X+n6Y+o7Z+p8A+q9B+r0C+s1D+t2E+