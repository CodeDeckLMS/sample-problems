# CodeDeck教材リポジトリの形式（codedeck-content/v2）

CodeDeckの教材・問題・テストケースを、Gitで管理するファイルとして書くための形式です。CodeDeckは `content-validate` でこの形式を検査し、`content-plan` と `content-apply` でDBへ反映します。形式に合わないファイルや未知の項目は、無視せずにエラーにします。

v1も引き続き読み込めます。v1は従来どおり`body.md`・`statement.md`と従来の添付拡張子を使います。v2は教材・問題の制限付きMDX、問題の添付と公開サンプルの説明、問題全体の解説、動画・字幕・HTMLを追加します。採点データの形式はv1から変更しません。アプリの表示と検証範囲は[教材形式v2と安全な表示](../docs/authored-content-v2.md)と[問題形式v2](../docs/problem-content-v2.md)に記録します。

## 全体の構成

```text
codedeck-content.yaml                 リポジトリの識別情報（必須）
materials/                            教材カテゴリと教材（任意）
  README.md                           説明（任意・取り込まない）
  python/category.yaml                教材カテゴリ（最上位）
  python/intro/category.yaml          子カテゴリ
  python/intro/<教材>/material.yaml   教材。本文は同じ場所の body.md または body.mdx
  python/intro/<教材>/starter/        エディターの初期コード（任意）
problems/                             問題カテゴリと問題（任意）
  README.md                           説明（任意・取り込まない）
  basics/category.yaml                問題カテゴリ（最上位）
  basics/io/category.yaml             子カテゴリ
  basics/io/<問題ID>/problem.yaml     問題の設定
  basics/io/<問題ID>/statement.md     問題文
  basics/io/<問題ID>/data/sample/     公開サンプル（受講生に表示する）
  basics/io/<問題ID>/data/secret/     秘密テスト（受講生に返さない）
  basics/io/<問題ID>/starter/         エディターの初期コード（任意）
  basics/io/<問題ID>/solutions/       作成者の解答（取り込まない）
  basics/io/<問題ID>/generators/      入力の生成プログラム（取り込まない）
  basics/io/<問題ID>/notes.md         作成メモ（取り込まない）
```

教材と問題は同じ考え方のフォルダ構造です。`category.yaml` のあるディレクトリがカテゴリで、その中のディレクトリが子カテゴリ、または教材・問題になります。教材・問題は、置かれたフォルダのカテゴリに属します。`materials/`・`problems/` の直下に置いた教材・問題は、カテゴリなしになります。フォルダは16階層までです。

最上位の上記以外のファイル（`README.md`、`AGENTS.md`、`scripts/`、`.github/` など）は取り込みません。`materials/` と `problems/` の中では、決められた名前以外のファイルをエラーにします。隠しファイルとシンボリックリンクも使えません。

## IDの規則

- `id` は英小文字・数字・ハイフンで1〜64文字です。先頭と末尾にハイフンは使えません。例: `python-input-and-output`
- IDはCodeDeckでのURLと学習記録の紐づけに使います。**一度反映したIDは変更しないでください。** 変更すると別の教材として作られ、古いIDの教材は非公開になります。
- ディレクトリは移動・改名できます。親カテゴリは、置かれたディレクトリで決まります。
- 問題は、ディレクトリ名と `id` を同じにします。問題IDはフォルダが違っても重複できません。
- 教材と教材カテゴリは同じID空間です。問題・問題カテゴリはそれぞれ別のID空間です。
- CodeDeckに同じIDの記録が既にある場合（画面で作った教材、旧システムから移行した記録、別のリポジトリの記録）は、上書きせずに `conflict` として止めます。別のIDを付けてください。

## codedeck-content.yaml

```yaml
format: codedeck-content/v2
repository: uec-pg-main # このリポジトリのID。反映後は変更しない
title: UEC PG 教材 # 任意
defaultAudience: enrolled # 任意。enrolled / authenticated（ログイン済み全ユーザー）
```

## 公開範囲（audience）

- `enrolled`: 在籍中、または有効な期限付き受講権限のある利用者向け。受講生という種別だけでは許可しません。
- `authenticated`: ログイン済みの有効な全ユーザー向け。ログインしていない人には配信しません。
- `public`: 従来の公開問題の互換用。問題だけに指定でき、匿名でも読めます。教材には指定できません。

`material.yaml`・教材の`category.yaml`・`problem.yaml`に`audience`を指定します。教材の省略値は親カテゴリ、最上位ではmanifestの`defaultAudience`を使い、問題の省略値はmanifestを使います。`defaultAudience`は`enrolled`または`authenticated`です。manifestも省略した旧形式は、教材`enrolled`・問題`public`を維持します。空文字・null・未知の値・文字列以外は拒否します。

親の公開状態・公開範囲を越えて配下を公開することはできません。同じフォルダに両方の範囲の教材を置く場合、親カテゴリを`authenticated`にし、限定する教材だけ`enrolled`にします。`enrolled`の親の配下に`authenticated`を指定すると検査エラーです。

`published: false`とCodeDeck側のリポジトリ非公開設定は、`audience`より優先します。本文・初期コード・添付・クイズ・実行・AI本文・過去会話は同じ認可に従います。秘密テストの配信範囲は広がりません。

## 教材カテゴリ（category.yaml）

`materials/` 直下のカテゴリは最上位（ROOT）、その下のカテゴリはフォルダ（FOLDER）になります。カテゴリのディレクトリには `category.yaml` と子ディレクトリだけを置きます。

```yaml
id: python
title: Python # 600バイトまで
order: 1 # 0〜1000000。同じ親の中での並び順
published: true # 公開するか
```

## 教材（material.yaml と本文）

教材のディレクトリには `material.yaml`、`body.md`または`body.mdx`のどちらか1つ、任意の `assets/`・`starter/` だけを置きます。教材の下に子ディレクトリは作れません。

```yaml
id: python-input-and-output
title: 入力を受け取って計算する
order: 1
published: false # 確認が終わるまで false にしておく
audience: enrolled # 任意。全ユーザー向けは authenticated（親カテゴリも同じ範囲にする）
problem: sum-two # 任意。関連問題のID（このリポジトリの problems/ にあるもの）
codeExecutionEnabled: true # 任意。教材画面のコード実行欄を表示するか。省略時は true
```

- 2026-10-24に習得・バッジ機能を廃止しました。旧 `masteryLanguages` は既存リポジトリの互換性のため読み込み・保存を維持しますが、習得判定やバッジの付与には使いません。従来どおり対応言語IDの配列と `problem` が必要です。新規教材では省略してください。
- `codeExecutionEnabled: false`でコード実行欄と開閉ボタンを非表示にできます。HTML・動画・PDF・スライド・読解用クイズなどに使います。v1/v2とも省略時は`true`で、既存の表示とdigestを維持します。AI Tutor、関連問題のリンク、問題ページのコード実行やサーバーの実行認可は変更しません。
- `body.md` はMarkdown、`body.mdx`は下記の制限付きMDXです。UTF-8で48000バイトまでです。
- `assets/` には、教材の添付ファイルを平らに置きます。拡張子は `.png`、`.jpg`、`.jpeg`、`.pdf`、`.json`、`.md` と、v2の `.mp4`、`.webm`、`.vtt`、`.html`。1件20MiB（HTMLは1MiB）・1教材100件・合計64MiBまでです。`.vtt`は`WEBVTT`で始め、HTML・字幕・MarkdownはUTF-8のテキストにします。添付のダウンロードと表示・動画のRange取得にも本文と同じ認可を毎回適用します。Markdown画像は`![図の説明](assets/figure.png)`のように参照し、外部画像は自動表示しません。
- 有料教材の本文・添付は、CodeDeckの受講権限で配信を制御します。リポジトリ自体も非公開にしてください。

### 制限付きMDX

部品は文章と分けたブロックに置きます。開始タグの属性は複数行に分けられます。属性は引用符付きの文字列だけで、JavaScript式・import・export・イベント属性・生HTML・文章中の部品は使えません。`{}`やタグを示すコード例はコードフェンスまたはインラインコードで囲み、必ず閉じます。Calloutは16階層まで、部品は1教材128個までです。

```mdx
<Callout kind="info" title="学習の目標">

**Markdown**で説明を書けます。

</Callout>

<Video src="assets/lesson.mp4" captions="assets/lesson.vtt" title="操作の説明" />
<PDF src="assets/notes.pdf" title="補足資料" />
<HTML src="assets/example.html" title="HTMLの動作例" />
```

- `Callout`: `kind`は`info`（既定）・`success`・`warning`・`error`。`title`は任意で、本文にMarkdownやCalloutを入れられます。
- `Video`: `src`はローカルのMP4/WebM、`captions`はローカルのWebVTT（必須）。`poster`にローカルのPNG/JPEGを指定できます。
- `PDF`・`HTML`: `src`はローカルのPDFまたはHTMLです。HTMLは静的プレビューに限定し、スクリプト・CSS・画像・フォーム・リンク遷移を除去します。`details`などのブラウザー標準の折り畳みは使えます。原本はダウンロードできますが、アプリと同じオリジンで実行しません。
- `Slides`: `src`に`https://docs.google.com/presentation/d/<ID>/embed`または`preview`を指定します。公開用の`d/e/<ID>/embed`も使えます。クエリは`start=false`・`loop=false`・`delayms=1000〜60000`だけです。
- `YouTube`: `id`に11文字の動画IDを指定します。

メディア部品は自己終了タグで、説明的な`title`が必須です。ローカルの参照は`assets/<ファイル名>`とし、参照先も同じ教材の添付として存在する必要があります。未知の部品・属性やパスの遡及は拒否します。

## 教材内クイズ（v2）

通常の教材ディレクトリに`quiz.yaml`と`choices/`、回答後の解説を置きます。本文は問題文になり、クイズは教材の受講権限・公開状態に従います。公開コーディング問題の採点パッケージとは分けて扱います。

```yaml
type: single # single | multiple | true_false
choices:
  - id: first
    file: choices/first.md
  - id: second
    file: choices/second.mdx
correct: [first]
explanation: explanation.md
```

選択肢は2〜20件、IDは既存の教材IDと同じ小文字英数字・ハイフンの規則で重複不可です。本文は`choices/<名前>.md`または`.mdx`に置き、1件48000バイト・選択肢の合計128KiBまでです。参照先のファイルは重複不可で、未宣言のファイルや子ディレクトリは置けません。選択肢と解説は教材と同じ`assets/`を参照できます。

単一選択・○×は正解IDが1つ、複数選択は1つ以上必要です。○×のIDは引用符付きの`"true"`・`"false"`の2つに固定します。解説は`explanation.md`か`explanation.mdx`の1つを宣言して置きます。本文・選択肢・解説のMDXは同じ定義済み部品だけを使います。正解と解説は非公開の正本で管理し、回答前のAPIへ含めません。

クイズの本文・選択肢・正解・解説・添付の変更を非公開の内容digestで検知し、版ごとに推測不能な不透明IDを割り当てます。このIDをAPIの`revision`として返し、正解を含むdigest自体は返しません。表示後に内容が変わった回答はそのまま採点せず、正誤と履歴を当時の版に結び付けます。編集はGitHubで行います。取込みだけで画面や実接続まで検証済みとは扱いません。

## 問題カテゴリ（problems/ の category.yaml）

カテゴリのディレクトリには `category.yaml` と子ディレクトリだけを置きます。問題カテゴリには公開設定がなく、カテゴリ名は公開の分類情報として表示します。

旧 `badgeRank`（問題カテゴリ）と `rank`（問題）は、`iron`・`bronze`・`silver`・`gold`・`platinum`の互換メタデータとして引き続き検査・保存します。`badgeRank`は空も許可し、`rank`の省略値は従来どおり`iron`です。画面表示・ランキング・達成判定には使いません。新規ファイルでは省略してください。

```yaml
id: basics-io
title: 入力と計算 # 200バイトまで
order: 1 # 同じ親の中での並び順（小さい順）
```

## 問題（problem.yaml と statement.md / statement.mdx）

問題のカテゴリは、置かれたフォルダで決まります。`problem.yaml` には書きません。

```yaml
id: sum-two # ディレクトリ名と同じ
title: 2つの整数の和
published: false
audience: enrolled # 任意。ログイン済み全ユーザー向けは authenticated
timeLimitMs: 2000 # 100〜10000。省略時は2000
memoryLimitMb: 128 # 16〜1024。省略時は128
checker: judge0-default # 必須（下記）
```

`checker: judge0-default` は、Judge0の既定の比較で正誤を判定してよいことを作成者が確認した宣言です。既定の比較は、各行末の空白と末尾の空行を無視し、それ以外は完全一致で比べます。小数の誤差許容、複数の正解、対話型の問題には対応していません。そのような問題は、出力が一通りに決まる形へ問題文を変えてください。

`statement.md` は問題文です。v2では代わりに`statement.mdx`を選べます。両方を置くことはできません。入力・出力の形式、制約、入出力例を書きます。48000バイトまでで、MDXの構文・部品は教材と同じです。

v2の問題は教材と同じ形式・上限の`assets/`を持てます。問題文とサンプル解説は同じ問題の添付を`assets/<名前>`で参照します。問題の本文と添付はその問題の公開状態に従い、`audience: public`の問題は匿名でも読めます。`authenticated`はログイン必須、`enrolled`は受講権限も必要です。有料教材の限定公開本文を公開問題やその添付へ複製しないでください。

### 問題全体の解説（v2・任意）

問題のディレクトリに`editorial.md`または`editorial.mdx`を1つ置くと、問題ページの「解説を見る」から読めます。YAMLへの指定は不要です。解説がない問題は未掲載と表示します。提出や正解を待たず、問題文と同じ公開状態・`audience`で閲覧できます。

考え方、正しさの説明、計算量、言語別の解答例、よくある誤りなどを書きます。解答例は言語ごとの見出しとコードフェンスで分けます。ひな形の`problems/basics/io/sum-two/editorial.md`を参考にしてください。

空の解説、2ファイルの同時配置、48000バイト超過を拒否します。MDXの構文と部品は教材と同じで、同じ問題の`assets/<名前>`を参照できます。解説は採点アーカイブへ含めず、追加・変更・削除でも採点パッケージを作り直しません。`solutions/`や`notes.md`は引き続き取り込まず、解説へ自動変換しません。AI Tutorへも解説を自動追加しません。

## テストケース（data/）

```text
data/sample/01.in   data/sample/01.ans
data/secret/01-zero.in   data/secret/01-zero.ans
```

- `.in` が入力、`.ans` が期待する出力です。同じ名前の `.in` と `.ans` を必ず対にします。
- 名前は英数字と `_` `.` `-` で、`sample/` と `secret/` の中に平らに置きます。名前の順に実行します。
- 公開サンプルを1〜10件、秘密テストを1件以上置きます。合計は200件、1ファイル4MiBまでです。
- UTF-8・改行はLFで、ファイルの最後は改行で終えます。
- 公開サンプルは受講生に表示します。問題文の入出力例と同じ内容にしてください。
- 秘密テストの入力と出力は受講生に返しません。
- v2では公開サンプルに`data/sample/01.md`または`01.mdx`の説明を付けられます。対応する`01.in`・`01.ans`が必要で、説明は1サンプル1つ・48000バイトまでです。`data/secret/`には説明を置けません。説明と添付は採点アーカイブへ含めず、変更しても採点用パッケージは作り直しません。

## 初期コード（starter/）

教材・問題のコード実行欄に、最初から入れておくコードです。教材・問題のディレクトリに `starter/` を作り、言語ごとに1ファイル置きます。

```text
starter/main.py    Python 3
starter/main.cpp   C++
starter/main.c     C
starter/main.js    JavaScript
```

- ファイル名は[対応言語の表](#対応言語と初期コードの名前)に従います。Javaは`Main.java`、PyPy3は`main.pypy3.py`です。UTF-8で、空でない64000文字までのテキストにします。
- 受講生がコード実行欄を開くと、選んだ言語の初期コードが入ります。Pythonの初期コードがない場合は、初期コードのある言語から始めます。
- 受講生がまだ書き換えていなければ、言語を切り替えたときにその言語の初期コードへ入れ替わります。書きかけのコードは消しません。「初期コードに戻す」で元に戻せます。
- 初期コードは教材本文と同じ受講権限で配信します。採点には使いません。
- 問題の答えそのものを書かないでください。入力の読み取りや関数の枠など、学習の目的ではない部分を用意する用途です。

## 解答と生成プログラム（取り込まない）

```text
solutions/accepted/main.py       全テストに正解する解答
solutions/accepted/main.cpp
solutions/wrong/two-lines.py     少なくとも1件で不正解になるはずの解答
generators/gen_random.py         入力を作るプログラム
```

解答の拡張子は下の対応言語に従います。PyPy3用の解答は末尾を`.pypy3.py`にします。Javaの公開クラス名はファイル名と揃えます。`scripts/solutions.py check` が、acceptedの全正解とwrongの不正解を手元で確かめます。CodeDeckへは取り込まず、受講生・AI Tutorにも渡しません。`generators/` の構成は自由です。

## 対応言語と初期コードの名前

| 言語ID       | 表示名     | starterのファイル名 | 手元の解答検査に使う処理系 |
| ------------ | ---------- | ------------------- | -------------------------- |
| `python`     | Python 3   | `main.py`           | Python 3                   |
| `pypy3`      | PyPy3      | `main.pypy3.py`     | pypy3                      |
| `cpp`        | C++        | `main.cpp`          | g++                        |
| `c`          | C          | `main.c`            | gcc                        |
| `javascript` | JavaScript | `main.js`           | node                       |
| `d`          | D          | `main.d`            | dmdまたはldc2              |
| `java`       | Java       | `Main.java`         | javac、java                |
| `rust`       | Rust       | `main.rs`           | rustc                      |
| `csharp`     | C#         | `main.cs`           | mcs、mono                  |
| `ruby`       | Ruby       | `main.rb`           | ruby                       |
| `go`         | Go         | `main.go`           | go                         |

初期コードは言語ごとに1ファイルです。PythonとPyPy3は同じ教材・問題にそれぞれ配置できます。手元に処理系がない解答はSKIPとして明示し、`--strict`では失敗にします。教材への取り込みは処理系を実行しません。CodeDeck上の利用可否とバージョンは、接続先Judge0の言語一覧で別途検証します。

## 取り込み後の扱い

- リポジトリで管理する教材・問題・カテゴリは、CodeDeckの管理画面から編集できません。リポジトリを変更して反映します。
- リポジトリから消した教材・問題は、学習記録を残すため削除せず、非公開にします。同じIDで戻すと再び公開設定に従います。問題カテゴリは消しても残ります。
- 問題のテストデータを変えると、新しい問題パッケージとして保存します。過去の提出は、提出時のパッケージに紐づいたままです。
- 解答・生成プログラム・作成メモを変えても、CodeDeckの内容は変わりません。

## 難易度

教材の `material.yaml` と問題の `problem.yaml` は、任意の `difficulty: 1`〜`difficulty: 5` を設定できます。整数以外・0・6以上は検査エラーになります。省略時は未設定で、既存のrankから推定しません。画面にはMaterial UIの星アイコンと「難易度 3/5」の読み上げ名を表示します。変更は教材リポジトリの同期から反映してください。
