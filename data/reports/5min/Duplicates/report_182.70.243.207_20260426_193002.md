# SOC自動分析レポート: 182.70.243.207

**生成日時:** 2026-04-26 19:33:10

---

## SOCアナリストによる攻撃ログ分析レポート

### 1. 攻撃の概要と目的

このログは、攻撃元IPアドレス `182.70.243.207` から、ターゲットシステム（Cowrieハニーポット）のSSHサービスに対する、一連のサイバー攻撃を示しています。

**攻撃の種類**:
*   **ブルートフォース攻撃/辞書攻撃**: 複数のユーザー名とパスワードの組み合わせを試行しており、特に`root`ユーザーアカウントへの不正ログインを狙った、典型的なSSHブルートフォース攻撃です。
*   **永続化攻撃（Persistence）**: ログイン成功後、システムに攻撃者の公開鍵を埋め込むことで、パスワードなしでの将来的なアクセス経路（バックドア）を確立しようとしています。

**攻撃の目的**:
SSHサービスへの不正ログインを成功させ、システムに対する`root`権限を取得することです。その後、バックドアを設置し、システムへの永続的なアクセス経路を確保することを目的としています。これにより、攻撃者は情報を窃取したり、システムを不正に操作したり、さらに他の攻撃の踏み台にしたりする可能性があります。

### 2. 推測される手法・使用ツール

**手法**:

1.  **偵察および初期アクセス**:
    *   攻撃者はまず、様々なユーザー名（`steam`, `root`, `tunnel`, `cloud`, `gitlab`, `345gs5662d34` など）とパスワードの組み合わせでSSHログインを試行しています。これは自動化されたブルートフォースツールや辞書攻撃ツールを使用している可能性が高いです。
    *   特に`root`ユーザーアカウントを繰り返しターゲットにし、最終的に複数の異なるパスワード（`QAZwsx`, `3245gs5662d34`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#`）でログインに成功しています。
2.  **永続化 (Persistence)**:
    *   ログイン成功後、攻撃者は以下のコマンドを実行しています。
        *   `cd ~; chattr -ia .ssh; lockr -ia .ssh`: `.ssh`ディレクトリのimmutable/append-only属性を解除しようとしています。`lockr`コマンドは存在しないため失敗していますが、`.ssh`ディレクトリの保護を解除し、内容を操作することが意図されています。
        *   `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~`:
            *   既存の`.ssh`ディレクトリを削除し、再作成します。
            *   攻撃者の公開鍵（`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`）を`.ssh/authorized_keys`ファイルに追加します。
            *   `.ssh`ディレクトリのパーミッションを適切に設定し、攻撃者がパスワードなしでSSHログインできるようにするバックドアを確立しようとしています。

**使用ツール**:
ログからは特定のツール名は特定できませんが、自動化されたSSHブルートフォースツール（例: Hydra, Nmapの`ssh-brute`スクリプトなど）が使用されている可能性が高いです。ログイン後のコマンド実行も、スクリプト化された手順に基づいていると考えられます。

### 3. 脅威レベルとその理由

**脅威レベル: 高 (High)**

**理由**:
1.  **root権限の奪取**: 攻撃者は最も特権の高い`root`アカウントで複数回ログインに成功しており、これはシステムに対する完全な制御権を獲得したことを意味します。
2.  **永続的なバックドアの設置試行**: `authorized_keys`に攻撃者の公開鍵を追加する試みは、将来にわたるシステムへの不正アクセス経路を確立しようとする明確な意図を示しています。これが成功していれば、攻撃者はパスワードを知らなくても、追加した公開鍵の秘密鍵を使って自由にシステムにアクセスできるようになります。
3.  **執拗な攻撃**: 短時間のうちに多数のログイン試行と複数のログイン成功が記録されており、攻撃者の執拗さと、自動化された攻撃フレームワークを使用している可能性が高いことを示唆しています。
4.  **潜在的な深刻な影響**: `root`権限とバックドアの存在は、情報漏洩、システム破壊、ランサムウェア感染、DDoS攻撃の踏み台化、さらにはネットワーク内の他のシステムへの横展開など、極めて深刻なセキュリティインシデントに発展する可能性があります。

この攻撃はハニーポットで検知されているため実際のシステムへの直接的な被害はありませんが、攻撃者の意図と能力は非常に高く、現実の環境であれば即座に広範な侵害につながる深刻な攻撃です。

### 4. 推奨アクション

この攻撃はCowrieハニーポットで検知されたものですが、もし同様の活動が本番環境で発生した場合を想定し、以下の推奨アクションを提案します。

**A. 即時対応 (Incident Response)**

1.  **攻撃元IPのブロック**:
    *   攻撃元IPアドレス `182.70.243.207` からのすべての通信をファイアウォールで即座にブロックします。
2.  **侵害されたアカウントのパスワード変更**:
    *   ログに記録された`root`ユーザーのログイン成功に使用されたすべてのパスワード（`QAZwsx`, `3245gs5662d34`, `Root1234567@@`, `1q2w3e..`, `root123123!!`, `@a123456`, `Root11111111@#`）を直ちに無効化し、`root`ユーザーのパスワードを非常に強力なものに変更します。
    *   他の不正ログイン試行のあったユーザー名（`steam`, `tunnel`, `cloud`, `gitlab`, `345gs5662d34`）についても、パスワードが推測されやすい場合は変更を検討します。
3.  **バックドアの確認と削除**:
    *   すべてのLinuxサーバーにおいて、`root`ユーザーのホームディレクトリ (`/root/.ssh/authorized_keys`) および他の特権ユーザーの`.ssh/authorized_keys`ファイルに、攻撃者の公開鍵 (`ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr`) が含まれていないか確認し、存在する場合は直ちに削除します。
4.  **フォレンジック調査**:
    *   対象システム（もし本番環境であれば）のシステムログ、認証ログ、ネットワークログなどを詳細に分析し、攻撃者が他にどのような活動を行ったか、他のシステムへの横展開の有無などを確認します。
    *   不審なファイル、プロセス、ネットワーク接続がないか徹底的に調査します。

**B. 予防策 (Proactive Measures)**

1.  **SSH設定の強化**:
    *   `sshd_config`ファイルで**`PermitRootLogin no`** を設定し、`root`ユーザーによるSSHログインを禁止します（通常の運用では、一般ユーザーでログインし、`sudo`を使用して権限昇格します）。
    *   **`PasswordAuthentication no`** を設定し、鍵認証のみを許可します。これにより、ブルートフォース攻撃によるパスワード認証突破を防ぎます。
    *   SSHポートを標準の22番から変更することも、攻撃対象を減らす一助となります（セキュリティバイオブスキュリティの一環）。
2.  **強固なパスワードポリシーの徹底**:
    *   すべてのシステムユーザーに対し、複雑性要件（大文字、小文字、数字、記号の組み合わせ）と十分な長さ（12文字以上推奨）を満たすパスワードの使用を義務付けます。
    *   定期的なパスワード変更を推奨し、過去に使用したパスワードの再利用を禁止します。
3.  **多要素認証 (MFA) の導入**:
    *   SSHログインに多要素認証を導入し、認証の強度を高めます。
4.  **不正ログイン検知・防止ツールの導入**:
    *   Fail2Banなどのツールを導入し、不正なログイン試行を自動的に検知・ブロックする仕組みを構築します。
5.  **システムおよびソフトウェアの定期的なパッチ適用**:
    *   SSHサーバーソフトウェアを含む、すべてのシステムおよびアプリケーションを最新の状態に保ち、既知の脆弱性を解消します。
6.  **ログ監視とアラート体制の強化**:
    *   SSHログインログ（成功・失敗両方）の監視を強化し、異常なログイン試行や成功時に即座にSOCへアラートが上がるように設定します。
7.  **公開鍵管理の厳格化**:
    *   `authorized_keys`ファイルへの公開鍵の追加や変更は厳格に管理し、定期的にレビューを行います。

この分析結果を基に、セキュリティ対策を速やかに実施することを強く推奨します。