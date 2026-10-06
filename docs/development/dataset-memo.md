# データセット仕様

目的：   
ハニーポットから送信元IPごとの活動・深刻度・攻撃成否、不明点、判断確度を構造化JSONとして出力するモデルを作成する


1サンプルの単位：   
1つの元ログファイル内における、1つの送信元IPの一連の行動を１サンプルとする。

入力：  
- VPS1 Cowrie元ログ
- VPS2 Webハニーポット元ログ
- VPS3 DBハニーポット元ログ
- VPS4 IoTハニーポット元ログ
- VPS1 Cowrie AIレポート
- VPS2~4 AIレポート
- VPS2~4 手動解析IR

1サンプルの入力に含める情報：   
- source_file
- honeypot
- target_vps
- src_ip
- first_seen
- last_seen
- event_count
- services
- target_ports
- raw_events

出力項目：
- activity：送信元IPの主な活動を表す文字列
- severity：low / medium / high

- success：success / failure / unknown
successの判定基準：
- success：ログイン成功、ファイル取得完了など、攻撃者が試みた段階の成功をログから明確に確認できる
- failure：認証失敗、接続拒否、コマンド失敗などが明確に記録されている
- unknown：接続やコマンド送信は確認できるが、処理結果を確認できない

successはハニーポット上で観測された段階の成功を示し、
実システムの侵害成功を意味しない。


- evidence：判断根拠となったログ内容の配列
- uncertainty：現在のログから判断できない点の配列
- confidence：low / medium / high

複数イベントのsuccess判定：
- 1サンプル内にsuccess相当のイベントが1件以上あればsuccessとする。
- successがなく、明確な失敗イベントだけが存在する場合はfailureとする。
- 接続、コマンド送信、状態遷移だけで結果が不明な場合はunknownとする。
- failureの後にsuccessがある場合はsuccessを優先し、失敗履歴はevidenceに残す。

ラベルの扱い：
- vps2~4 手動IR：正解データ(gold)
- VPS2〜4 AIレポート：手動IRとの比較専用
- Cowrie AIレポート：未確認の擬似ラベル(pseudo)
- AIレポートのないログ：未ラベル(unlabeled)
- 元ログと対応しないレポート：除外(excluded)
- 内容がNoneまたは解析結果が空のレポート：除外（excluded）   


手動IRのラベル変換：
- 簡易版IRは表の1行を1つのIPラベルとして扱う。
- 詳細版IRは送信元IP別の記述を抽出する。
- レポート全体の深刻度を各IPへ無条件にコピーしない。
- IP別の判断が存在しない場合は要確認またはexcludedとする。
- 手動IRにない情報をAIレポートから補完してgoldにしない。

長大ログの処理：
- 重複イベントを除去する。
- 同じ種類の反復イベントは件数として集約する。
- 危険なコマンド、認証、ファイル取得などの重要イベントは省略しない。
- 入力が最大トークン数を超える場合は、集計情報と代表イベントへ変換する。
- 省略したイベント数と省略理由をメタデータに記録する。

VPS2〜4 AIレポートの対応：
- レポート名の観測時刻と元ログの時間帯を使用して対応付ける。
- レポート内のIP、VPS、サービスと元ログを照合する。
- 一意に対応できないレポートは比較対象外とする。
- AIレポートの記述をgoldラベルの補完には使用しない。




重複処理：   
1.元ログのイベントを正規化して内容ハッシュを計算する。   
2.内容ハッシュが完全に同一のサンプルは1件だけ残す。   
3.同一送信元IP、同一セッションID、同一時刻、同一イベント内容のイベントを重複とする。   
4.同じイベントが複数の定期取得ファイルに含まれる場合は1件に統合する。   
5.同一IP・同一セッション・同一ペイロードから作成されたサンプルは、trainとvalidation/testをまたがせない。   
6.削除した重複はduplicate_report.jsonへ記録する。   
7.元ファイル自体は削除・変更しない   


分割：
- train：70%
- validation：15%
- test：15%

分割比率：
70/15/15は目標値とし、送信元IP、セッション、
ペイロードの分離を比率より優先する。

分割後に、サンプル数、IP数、severity、success、
honeypotの分布をdataset_summary.jsonへ記録する。


分割条件：   
- 送信元IP単位でグループ分割する。   
- 同一IPのサンプルはすべて同じ分割先へ入れる。   
- 同一セッションまたは同一ペイロードも同じ分割先へ入れる。   
- validationとtestにはgoldラベルだけを使用する。   
- pseudoラベルはtrainへ直接混ぜず、別ファイルに保存する。   
- unlabeledは分割対象外とする。   
- severityとsuccessの比率が極端に偏らないように調整する。   
- 乱数seedを固定して、同じ分割を再現可能にする。   
- 分割に使用する乱数seedは42とする。

最大トークン数について：
- 最大トークン数はベースモデル決定後に設定する。
- 使用したモデル、トークナイザー、最大トークン数をdataset_card.mdへ記録する。


出力形式：
- JSONL
- utf-8
- 1行1サンプル

出力ファイル名：
- dataset_gold_all.jsonl
- train_gold.jsonl
- validation_gold.jsonl
- test_gold.jsonl
- cowrie_pseudo.jsonl
- cowrie_unlabeled.jsonl
- vps2_4_ai_comparison.jsonl
- excluded_samples.jsonl
- duplicate_report.json
- dataset_summary.json
- dataset_card.md
