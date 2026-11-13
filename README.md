# CodeDeck サンプル問題集

このリポジトリの教材・問題文・解説・図・クイズ・入出力・解答例は、すべてAIが生成したテストデータセットです。
実在する受講生の情報、既存の有料教材、本番用の秘密は含みません。内容の正確さや教材としての品質は保証しません。

CodeDeckの管理画面「教材・問題リポジトリ」で、`CodeDeckLMS/sample-problems`、ブランチ `main`、
repository ID `sample-problems`、種類 `問題`、取得方式「公開GitHub」を選び、計画を確認して反映します。

「タイルの面積」「非負の測定値」「測定値の増加回数」の3問です。
既存の非公開 `classroom-content` / `problem-content` とIDが重ならないため、既存の記録を上書きしません。
相互参照用の教材と問題の自動紐づけは行いません。

## 入力と判定

問題文の「入力」「出力」に形式を記載します。標準入力へ `data/sample/*.in` と `data/secret/*.in` を与え、
標準出力を同名の `.ans` とJudge0の `judge0-default` で比較します。
行末の空白・末尾の空行を無視し、残りは一致が必要です。小数の誤差許容・特殊checker・対話型ではありません。

公開リポジトリでは `data/secret/` と解答例も誰でも読めます。この名前は採点時の分類であり、GitHub上の秘密を意味しません。
CodeDeckの利用者APIから採点テストの入力・出力は返しません。実際の秘密テストや有料教材は別の非公開リポジトリへ置いてください。

## scriptsは作問時の任意の検査補助

`scripts/check.sh` は形式検査と解答例の検査をまとめ、`scripts/solutions.py` は作成者のPCで正解・誤答例を確認します。
CodeDeckへの取込み・提出時の採点では実行しません。誤差許容のcheckerではなく、フォルダごと削除しても取込み・採点できます。

```sh
CODEDECK_DIR=/path/to/CodeDeck sh scripts/check.sh
```

形式仕様は [FORMAT.md](FORMAT.md) を参照してください。生成元はCodeDeck本体の `tools/generate_public_samples.py` です。
