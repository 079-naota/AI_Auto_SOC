# SOC自動分析レポート: 102.219.126.124

**生成日時:** 2026-04-26 12:01:11

---

## SOCアナリストレポート

### 攻撃ログ分析レポート

**件名: SSHサービスへのブルートフォース攻撃および永続化試行の検出**

**攻撃元IPアドレス**: 102.219.126.124
**分析期間**: 2026-04-26T07:33:56Z から 2026-04-26T07:57:09Z

---

### 1. 攻撃の概要と目的

攻撃元IPアドレス `102.219.126.124` から、当社のSSHサービス（Cowrieハニーポット）に対して、継続的なブルートフォース（辞書攻撃）が実行されました。この攻撃は、まず不正なパスワード認証によってSSHアクセスを試み、複数の異なるユーザー名とパスワードの組み合わせを試行しています。

特に注目すべきは、`root` ユーザーに対する複数のログイン成功記録です。ログイン成功後、攻撃者は以下のコマンドシーケンスを繰り返し実行しています。

1.  `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh` ディレクトリのファイル属性（immutable/append-onlyなど）を変更しようと試みていますが、ハニーポット上では失敗しています。
2.  `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`: これは、攻撃者の公開鍵を `root` ユーザーの `~/.ssh/authorized_keys` ファイルに書き込み、パスワードなしでSSH接続できる永続的なバックドアを確立しようとするものです。公開鍵のコメントは `mdrfckr` です。

攻撃の主な目的は、SSHサービスへの不正侵入を達成し、root権限での永続的なアクセス経路を確立することにあると推測されます。これにより、将来的に任意のタイミングでシステムにアクセスし、マルウェアの展開、データ窃取、さらなるネットワーク内の横展開などを行うことが可能になります。

### 2. 推測される手法・使用ツール

*   **手法**:
    *   **ブルートフォース/辞書攻撃**: 多数のユーザー名とパスワードの組み合わせを試行しており、特に `root` ユーザーを標的としています。
    *   **認証情報の永続化 (Persistence)**: ログイン成功後、システムに攻撃者の公開鍵を埋め込み、恒久的なバックドアを設置しようとしています。これは、初期侵入後の段階で行われる一般的な手法です。
    *   **自動化された攻撃**: 一連のログイン試行とコマンド実行がほぼ同じパターンと間隔で繰り返されていることから、攻撃は自動化されたスクリプトやツールによって実行されている可能性が高いです。
*   **使用ツール**:
    *   **SSHクライアント**: ブルートフォース攻撃にはHydra、Medusa、NmapのNSEスクリプト、またはカスタムスクリプトなどのツールが使用されている可能性があります。
    *   **攻撃者の公開鍵**: `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` という公開鍵が攻撃活動に利用されています。この鍵のコメントである `mdrfckr` も攻撃者の特徴を示す可能性があります。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:

1.  **複数のrootログイン成功**: ログには複数の異なるパスワードで `root` ユーザーのログインに成功した記録があります。これが現実のシステムであれば、すでにroot権限での完全な侵害が発生していることを意味し、極めて深刻な状況です。
2.  **持続的アクセス経路の確立試行**: 攻撃者はログイン成功後、バックドアとして利用可能な公開鍵を設置しようと試みています。これにより、パスワードが変更されたとしても攻撃者はシステムにアクセスし続けることができ、長期的なシステム乗っ取りのリスクがあります。
3.  **攻撃の自動化**: 攻撃が繰り返し自動的に行われていることから、これは組織的な攻撃グループやボットネットの一部である可能性があり、単発的な試行よりも広範囲な脅威を示唆します。
4.  **潜在的な影響の大きさ**: 攻撃者がroot権限でシステムにアクセスした場合、データ破壊、機密情報漏洩、マルウェア感染（ランサムウェア、仮想通貨マイニングマルウェアなど）、他のシステムへの攻撃拠点化といった重大な被害につながる可能性があります。

### 4. 推奨アクション

**緊急対応**:

*   **攻撃元IPアドレスのブロック**: ファイアウォール、IDS/IPS、またはエッジルーターにて、攻撃元IPアドレス `102.219.126.124` からの全ての通信を即座にブロックしてください。
*   **公開鍵の調査**: ログに記録されている公開鍵 `ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr` のハッシュ値を計算し、脅威インテリジェンスプラットフォーム (VirusTotal, AlienVault OTXなど) で検索して、既知の脅威や攻撃グループとの関連性を調査してください。
*   **パスワードリセットと監査**: ログに記録されているログイン成功に使用されたパスワード (`1qaz@WSX3edc$RFV!@`, `3245gs5662d34`, `ali123456`, `Root8`, `Aa112211.`, `Config123`, `Aa123321`) が、もし実際のシステムで使用されている場合は、直ちに全てのシステムでこれらのパスワードを複雑なものに変更してください。また、関連する可能性のある全てのシステムアカウントについてもパスワードの変更と強制的なログアウトを検討してください。
*   **侵害調査**: 万一、同様のSSHサービスが稼働している実システムがある場合は、当該期間中のシステムログ、SSHログ、認証ログを徹底的に調査し、実際の侵害があったかどうかを確認してください。特に `.ssh/authorized_keys` ファイルの改ざんがないか、不審なプロセスが実行されていないかを確認が必要です。

**予防的対策**:

*   **SSH設定の強化**:
    *   **パスワード認証の無効化**: 可能な限り、SSHのパスワード認証を無効にし、強固な公開鍵認証のみを許可するように設定してください (`PasswordAuthentication no` in `sshd_config`)。
    *   **rootログインの禁止**: `PermitRootLogin no` を設定し、rootユーザーの直接ログインを禁止してください。特権操作が必要な場合は、一般ユーザーでログイン後、`sudo` を利用するようにしてください。
    *   **デフォルトポートの変更**: SSHサービスをデフォルトの22番ポートから変更することで、一般的なスキャンからの検出リスクを低減できます。
    *   **アクセス元IPアドレスの制限**: セキュリティグループやファイアウォールで、SSHアクセスを許可された特定のIPアドレス範囲に限定してください。
    *   **2要素認証 (MFA) の導入**: SSHアクセスにMFAを導入し、認証の強度を高めることを検討してください。
*   **認証ログの監視強化**:
    *   SSHログイン試行ログ（特に失敗ログ、頻繁なログイン試行）を継続的に監視し、しきい値を超えた場合に自動でアラートを生成するシステムを導入してください。
    *   ログイン成功後、特権コマンドの実行や `authorized_keys` ファイルの変更などの重要なファイルシステム操作があった場合にアラートを発生させるよう、SIEMやログ監視ツールを設定してください。
*   **システムおよびソフトウェアの更新**: OSおよびSSHサービス関連のソフトウェアを常に最新の状態に保ち、既知の脆弱性が悪用されるリスクを低減してください。
*   **ハニーポットの活用**: 今回のCowrieハニーポットのように、脅威インテリジェンス収集のため、ハニーポットを継続的に運用し、攻撃者の新しい手法やトレンドを把握してください。