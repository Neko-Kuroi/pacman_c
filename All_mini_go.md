# パックマンを書く ― Go 版（ミニ版）

（全文連結版・第1版）


---

# パックマンを書く ― Go 版（ミニ版）

C版教科書『パックマンを書く』（floooh/pacman.c を題材に、
序章＋準備編＋全27章＋付録A〜E）、Python 版（ミニ版）、
Nim 版（ミニ版）に続く、4冊目のミニ版教科書です。

題材は、pacman.c を Go へ移植した実装（pacman-go）です。
手書き 2,725 行に、生成したデータ 608 行とテスト
824 行が付きます。土台はゲームエンジン Ebitengine
（v2.10.6）です。

この版の特徴は、移植の前に**仕様書（SPEC）を立てた**
ことです。仕様と挙動は原典どおりに踏襲し、Go と
Ebitengine の都合で原典からはみ出す箇所は、H1〜H9 の
決定として先に固定してから実装しました。本書は、その
決定がどう実装になったかを追う形で書かれています。

前2冊のミニ版が文法レクチャーを省いたのに対し、本書は
Go の構文と、Go 特有のデザインパターンの解説も入れます。
各章の「Go の道具」がその場所です。

## 読み方

- 前提は、C版教科書を読んでいること（または pacman.c の
  設計を知っていること）。Python 版・Nim 版を読んで
  いると、4つの言語の対比が効きます。
- 引用には、Go のファイル名と行番号を付けます
  （例: state.go 394行）。対応する pacman.c の
  箇所には、C の行番号も併記します。
- 仕様書 SPEC は本書に収録しません。はみ出しの決定は
  H番号（H1〜H9）で参照します。
- Go ソースの全文は付録Aにあります。引用はすべて、
  手元で照合できます。

## 目次

- [序章 4つ目の言語と、仕様書という進め方](00_序章.md)
- [第1章 全体地図](01_第1章.md)
- [第2章 状態は1つの Game 型](02_第2章.md)
- [第3章 時間の語彙](03_第3章.md)
- [第4章 幾何と Int2](04_第4章.md)
- [第5章 盤面とデータ](05_第5章.md)
- [第6章 ルールと場面](06_第6章.md)
- [第7章 ゴーストの思考](07_第7章.md)
- [第8章 家と速さ](08_第8章.md)
- [第9章 描画](09_第9章.md)
- [第10章 音](10_第10章.md)
- [第11章 入力](11_第11章.md)
- [第12章 テストと検証](12_第12章.md)
- [終章 4つの言語で書くということ](13_終章.md)

### 付録

- [付録A Go ソース全文](付録A_Goソース全文.md)
- [付録B C⇔Go 対応表](付録B_CGo対応表.md)
- [付録C 検証の記録](付録C_検証の記録.md)

---

*題材の Go ソースは、移植と検証を経た版を正本として
固定しています（序章を参照）。原典 pacman.c は
floooh によるもので、コミット `ccfc0e84` を用います。
Go は 1.27.4、Ebitengine は v2.10.6 を用います。*

---

# 序章 ― 4つ目の言語と、仕様書という進め方

## この本は何か

C版教科書『パックマンを書く』は、floooh の pacman.c
（4,303行の C）を題材に、C の文法から始めてゲームの
設計を読み通す本でした。Python 版（ミニ版）は、その
設計を Python へ持ち運んだ単一ファイルの実装
`pacman.py`（581行）を、Nim 版（ミニ版）は pacman.c を
Nim へ移植した実装（2,242行）を題材に、対応を見通す
本でした。

この本は4冊目です。題材は、pacman.c を Go へ移植した
実装（pacman-go）です。手書き 2,725 行、生成した
データ（data.go）608 行、テスト 824 行。土台には
ゲームエンジン Ebitengine を使います。各ファイルの
冒頭には、対応する pacman.c の行範囲が書かれています。
たとえば状態のファイルは、こう始まります。

```go
// state.go -- constants, types and the single game state object.
// Corresponds to pacman.c lines 142-678 (config, enums, structs, data tables).
```

狙いは前2冊と同じく「対応を見通すこと」ですが、
今回は読み方が1つ増えます。**仕様書の決定が、どう
実装になったか**を追うことです。あわせて、Go の構文と
Go 特有のデザインパターンも、各章の「Go の道具」で
解説します。前2冊が文法レクチャーを省いたのに対し、
この本では道具も読みどころに入ります。

## 4つの移植は、持ち運び方が違います

同じ設計の移植でも、版ごとに性格が違います。

- **Python 版**: 設計だけを持ち運んだ移植。絵も音も
  自作で、ROM データは持ち運びませんでした
- **Nim 版**: 原典にいちばん近い移植。原典と同じ
  sokol の公式バインディングを使い、ROM データや
  シェーダーまで機械抽出して持ち運びました
- **Go 版**: 仕様書を立てた移植。土台は sokol では
  なく Ebitengine で、原典の部品のいくつかは
  エンジン側に吸収されて消えます。消えるもの、
  替わるものを先に決めたのが、この版の進め方です

行数でいうと、C の 4,303 行に対して Go は本体合計
3,333 行（手書き 2,725 行＋生成データ 608 行）で、
約77%です。ただしこの比較には注意が要ります。
Go 版には、原典に無かった入力の拡張（ゲームパッドと
タッチ、第11章）とテスト 824 行の土台作りが
混ざっています。コード部分だけを比べると、
C の約3,256行（全体4,303行から、冒頭の説明
コメント132行と、ROM データの915行（3389行から
末尾まで）を引いた数）に対して、Go の手書き
2,725 行で約84%です。行数の読み方は終章で
改めて扱います。

## 仕様書 SPEC という進め方

Go 版の移植は、コードの前に仕様書（SPEC）を
書くところから始まりました。方針はこうです。

- 仕様と挙動の正本は pacman.c。ゲームのデザインと
  ルールは原典を踏襲する
- プログラミングの構成は C から離れてよい
- Go（Ebitengine）にする都合で原典から**はみ出す
  箇所**は、種別つきで列挙し、それぞれに決定を
  与えてから実装する

はみ出しは9件（H1〜H9）あり、種別は4つです。
**置換**（仕組みが替わるが挙動は同じ）、**消滅**
（原典の部品が不要になる）、**変形**（形は変わるが
役割は同じ）、**追加**（原典に無かったものが増える）。
たとえば ――

- H1（置換）: 原典の「実時間を蓄積してティックに
  変える」仕組みは、Ebitengine の Update に吸収され、
  「1回の Update ＝ 1ティック」になる（第1章）
- H3（置換）: 音の出口は push 型から pull 型
  （`io.Reader`）に替わる（第10章）
- H5（消滅）: letterbox とシェーダーは持ち運ばない。
  拡縮と配置は `Layout` に任せる（第9章）
- H7（変形）: 状態は `Game` 型に集め、振る舞いは
  メソッドにする（第2章、第6章）
- H8（追加）: 入力はキーボードに加えてゲームパッドと
  タッチに対応する（第11章）

本書の各章は、対応する H番号を置いて進みます。
「なぜ原典と違う形なのか」に、すべて仕様書の側の
答えがある、というのがこの版の読みどころです。

## 移植の方針 ― 何を揃えて、何を任せたか

連作の決まりは、この版でも同じです。

- **揃えるもの**: 仕様と挙動。そして「区画と関数の
  対応」―― C のどの関数が Go のどこにあるか、
  対応表が取れること（付録B）
- **言語に任せるもの**: 関数の中身の書き方。たとえば
  ゲームを止めるフラグは、C では `uint8` のビット
  演算でしたが、Go には集合型がないので、ビット
  フラグの型にメソッドを持たせた形で受けます
  （第6章）

そのうえで Go 版には、仕様書という形で「任せる
範囲を先に文書にした」という段取りが加わりました。

## 読み方の約束

- 引用には、Go のファイル名と行番号を付けます
  （例: state.go 394行）。対応する pacman.c の
  箇所には、C の行番号も併記します
- Go ソースの全文は付録Aにあります。生成データ
  data.go（608行）も含みます
- C版教科書への参照は「C版 第N章」、Python 版は
  「Python 版 第N章」、Nim 版は「Nim 版 第N章」の
  形で書きます
- 仕様書へは「SPEC H3」のように H番号で参照します。
  SPEC 自体は本書に収録しません

## 正本について

この本が題材にする Go ソースは、移植と検証を経た版を
複写して固定したものです。検証では、画面なしで
ティックだけを回すヘッドレス検証（60,000ティックの
自動プレイ、決定性の確認、面クリアの確認）と、
速度やカウンタなどを狙った挙動プローブを通しました。
自動プレイの到達点（スコア350、ドット66個）は
Nim 版と完全一致しています。記録は付録Cにあります。

なお、こちらで確認できているのは画面なしの環境での
動作と、Xvfb 上の描画までです。実際の画面と音、
WASM のブラウザ実行は未確認で、その区別は付録Cに
明記します。

## この本の進み方

序章のあと、第1章で全体の地図を描き、第2章から
第11章で設計判断と仕様書の決定を1つずつ追い、
第12章でテストと検証の仕組みを読みます。終章は、
4つの言語で同じものを書くということのまとめです。

---

### 次回予告

**第1章 全体地図**
― 入り口の `main.go` を読みます。Ebitengine の
Game インターフェースを「満たす」という書き方と、
原典の時間の蓄積が消えて「1 Update ＝ 1ティック」
になったことを確認します。

---

# 第1章 全体地図

## 前章までのあらすじ

序章で、Go 版は「仕様書を立てた移植」だという話を
しました。仕様と挙動は原典どおり、はみ出す箇所は
H1〜H9 の決定として先に固定する。この章では
入り口の `main.go`（104行）を読み、決定のうち
H1（時間の進み方）と H2（入り口）が、コードの
形としてどう現れているかを見ます。対応する C は
pacman.c 716〜825行です。

## 1.1 入り口は「登録」から「引き渡し」へ

C版 第4章で読んだとおり、原典の入り口は sokol の
コールバック登録でした。`sokol_main` が、初期化・
フレーム・入力・終了の4つの関数ポインタを枠組みに
渡し、あとは枠組みから呼ばれる、という形です。

Go 版の入り口は、関数ポインタの束ではなく、
**1つのオブジェクトを引き渡す**形です。`main`
関数の最後を見てください（main.go 78〜104行）。

```go
func main() {
	a := &app{game: NewGame()}
	a.renderer = newRenderer(a.game)
	a.reader = &InputReader{}
	setupAudio(a)
```

```go
	ebiten.SetTPS(60)
	ebiten.SetWindowSize(DisplayPixelsX*2, DisplayPixelsY*2)
	ebiten.SetWindowTitle("pacman.c")
	ebiten.SetWindowResizingMode(ebiten.WindowResizingModeEnabled)
	if err := ebiten.RunGame(a); err != nil && err != ebiten.Termination {
```

`ebiten.RunGame(a)` に渡している `a` が、ゲームの
実体です。あとは Ebitengine が、`a` のメソッドを
呼び続けます。これが SPEC H2 の決定 ――「Ebitengine
の `Game` インターフェース（`Update` / `Draw` /
`Layout`）を実装する型を渡す」― の実装の姿です。

## 1.2 app 型 ― 呼ばれる3つのメソッド

`a` の型 `app` は main.go 19〜29行で定義されて
います。

```go
type app struct {
	game     *Game
	renderer *Renderer
	reader   *InputReader
	synth    *Synth
	player   *audio.Player

	frames      int
	smokeFrames int  // >0: exit after this many updates (headless smoke)
	smokePlay   bool // smoke: press "any key" at frame 120 to start a game
}
```

Ebitengine から呼ばれるメソッドは3つです。

`Update`（main.go 31〜47行）は、1ティック分の
進行です。入力を読み、ゲームを1ティック進めます。

```go
func (a *app) Update() error {
	if a.reader != nil {
		a.reader.Read(&a.game.Input)
	}
	if a.smokePlay && a.frames == 120 {
		a.game.Input.Anykey = true
	}
	a.game.Tick()
	a.game.Input.Anykey = false
	a.frames++
```

中心は `a.game.Tick()` の1行です。ゲームの本体は
`Game` 型の側（rules.go）にあり、`main.go` は
「Ebitengine の呼び出しを、ゲームのティックに
つなぐ」だけをしています。

`Draw`（main.go 49〜51行）は描画で、実体は
`Renderer` に委ねます。

```go
func (a *app) Draw(screen *ebiten.Image) {
	a.renderer.Draw(screen)
}
```

`Layout`（main.go 53〜55行）は、外側の窓サイズに
対して「中身の論理サイズはいくつか」を答える
メソッドです。

```go
func (a *app) Layout(outsideWidth, outsideHeight int) (int, int) {
	return DisplayPixelsX, DisplayPixelsY
}
```

原典にあった letterbox（画面の中央寄せと余白の
計算）は、この `Layout` に吸収されて消えました
（SPEC H5、第9章）。Go 版の `Layout` がやることは、
224×288 という内部解像度を返すことだけです。

## 1.3 1 Update ＝ 1ティック（H1）

原典の時間は、C版 第3章で読んだ「先に払って、
あとで精算する」蓄積の仕組みでした。実時間を
ナノ秒で貯めて、16,666,666 ナノ秒たまるごとに
ティックを1つ消化する。許容誤差と、1フレームで
消化できる上限（クランプ）もありました。

Go 版に、その蓄積はありません。main.go 90行の

```go
	ebiten.SetTPS(60)
```

で「1秒に60回 `Update` を呼ぶ」とエンジンに
約束させ、`Update` が呼ばれること自体が
1ティックなのです（SPEC H1）。状態の側にも
痕跡があります。C の状態には蓄積用の残高の
フィールドがありましたが、Go 版の `TimingState`
（state.go 317〜319行）はティックカウンタ
1つだけです。

```go
type TimingState struct {
	Tick uint32
}
```

コメントには「C の蓄積用のフィールドは消えた。
Ebitengine がティックごとに `Update` を呼ぶから」
と書かれています。消えた部品は、コメントと
仕様書に理由を残して消える ―― これもこの版の
進め方です。

## 1.4 ロジックは Ebitengine を知らない

`app` の定義の上のコメント（main.go 16〜18行）に、
大事な約束が書かれています。

```go
// app is the ebiten game object. The game logic lives in Game; the
// renderer, input reader and synth are attached here so the logic
// files never import ebiten.
```

ゲームのロジック（`Game` とその仲間）は `app` の
側に持ち、描画・入力・音の Ebitengine 寄りの部品は
`app` にぶら下げます。おかげで、ロジック側の
ファイル（state.go、rules.go、ghost.go など）は
Ebitengine を import しません。`Game.Tick()`
（rules.go 331行）は画面なしで直接呼べるので、
テストはエンジンなしで回ります。これが SPEC H9
（ロジックは Ebitengine に依存しない形に保つ）の
土台で、第12章の検証の仕組みにつながります。

原典との対比でいうと、C では「枠組みに呼ばれる
関数」と「ゲームの関数」が同じファイルに並んで
いました。Go 版は、呼ばれる側の都合を `main.go` の
104行に閉じ込めて、本体を枠組みから切り離した、
という読み方ができます。

## 1.5 音の用意と、エラーは外に出す

`main` の中ほどにある `setupAudio`（main.go 62〜76行）
は、音の初期化です。ここには Phase 0 のスパイクで
分かった知見が刻まれています。音響装置のない
機械では、プレイヤーの生成がドライバの初期化に
失敗し、そのエラーが `RunGame` を即座に終わらせて
しまう。そこで、環境変数 `PACMAN_AUDIO=off` で
音そのものを飛ばせるようにしてあります。

```go
func setupAudio(a *app) {
	if os.Getenv("PACMAN_AUDIO") == "off" {
		return
	}
```

H2 の決定の後半 ――「初期化の失敗は `error` として
外に出す」― も、`RunGame` の戻り値の扱い
（main.go 94〜103行）に現れています。失敗は
握りつぶさず、標準エラーに出して終了コード1で
終わる。音が原因らしい場合は、ヒントも添えます。

---

## Go の道具 ― インターフェースの暗黙の実装

Go のインターフェースは、「メソッドの集まり」に
名前を付けたものです。Ebitengine の `Game`
インターフェースは、だいたい次の形をしています。

```go
type Game interface {
	Update() error
	Draw(screen *Image)
	Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int)
}
```

ここで Go 特有なのは、**「この型はこのインター
フェースを実装します」という宣言がどこにも
書かれない**ことです。`app` 型は、`Update`、
`Draw`、`Layout` の3メソッドを持っている、という
事実だけで `ebiten.Game` を満たします。これを
暗黙の実装（implicit satisfaction）と呼びます。

効き目は2つあります。1つは、型の定義側が
インターフェースの存在を知らなくてよいこと。
`app` の定義（main.go 19行）には Ebitengine の
インターフェースへの言及がありません。もう1つは、
満たしているかどうかは使う側（`RunGame(a)` を
呼ぶ箇所）でコンパイル時に判定されること。
メソッドが1つ欠ければ、その場でエラーになります。

C の関数ポインタの束（原典のコールバック登録）と
比べてみてください。やっていることは似ています
――「枠組みが呼ぶ関数の組を渡す」。違うのは、
組の形をインターフェースという型で表し、組の
不足をコンパイラが検出する点です。Nim 版の sokol
コールバック（Nim 版 第1章）とも並べて読むと、
3つの言語の「入り口の作法」の違いが見えます。

もう1つ、`Update` の戻り値の `error` も Go の
作法です。失敗は例外ではなく、戻り値として
返します。`Update` が `ebiten.Termination` を
返せば正常終了、それ以外の `error` は異常として
`RunGame` から戻ります。

---

## 解剖メモ（第1章）

- 入り口は、コールバック登録（C）から、
  インターフェースを満たすオブジェクトの
  引き渡し（Go）へ。`RunGame(a)` の1行が接続点。
- 時間の蓄積は消滅した（H1）。`SetTPS(60)` と
  「Update ＝ 1ティック」の約束が代わりを務め、
  状態からも残高のフィールドが消えている。
- letterbox は `Layout` に吸収されて消えた（H5）。
- ロジックは Ebitengine を import しない（H9）。
  呼ばれる側の都合は main.go の104行に閉じる。
- 音の初期化には、装置のない環境への逃げ道
  （`PACMAN_AUDIO=off`）が付いている。

## 手を動かす（読解演習）

1. `main.go` の中で、Ebitengine を import して
   いる箇所と、していないファイルを分けて
   ください。ロジック側のファイルが import
   していないことは、どう確かめられますか。
2. 原典 pacman.c 716〜825行の `sokol_main` と
   コールバック群を拾い、Go 版の `main` と
   `app` のメソッドにどう対応するか、対応表を
   作ってください。対応先のないコールバックは
   ありますか。
3. `Layout` が返す `DisplayPixelsX`、
   `DisplayPixelsY` は、state.go の何行で
   どう定義されていますか。タイル数とタイルの
   大きさから追ってください。

## 確認問題

**問1**：Go 版で「1ティック」は、何をもって
1ティックですか。

<details>
<summary>答え</summary>

Ebitengine が `Update` を1回呼ぶことです。
`SetTPS(60)` で毎秒60回の呼び出しを約束させ、
原典にあった実時間の蓄積と換算の仕組みは
持っていません（SPEC H1）。
</details>

**問2**：`app` 型が `ebiten.Game` インターフェースを
満たすことは、コードのどこに書かれていますか。

<details>
<summary>答え</summary>

どこにも書かれていません。`app` が `Update`、
`Draw`、`Layout` の3メソッドを持っているという
事実だけで満たします（暗黙の実装）。不足が
あれば `RunGame(a)` の呼び出しがコンパイル
エラーになります。
</details>

**問3**：`PACMAN_AUDIO=off` は、なぜありますか。

<details>
<summary>答え</summary>

音響装置のない機械では、プレイヤーの生成時に
ドライバの初期化が失敗し、そのエラーで
`RunGame` が即座に終わってしまうためです。
環境変数で音の初期化そのものを飛ばし、音なしで
起動できるようにしています。
</details>

---

### 次回予告

**第2章 状態は1つの Game 型**
― `state.go` を開きます。ゲームの状態すべてを
抱える `Game` 構造体と、その中身の7つの部屋、
そして「ゼロ値が初期状態」という Go の約束を
読みます。

---

# 第2章 状態は1つの Game 型

## 前章までのあらすじ

第1章で、入り口は `main.go` に閉じていて、本体は
`Game` 型の側にあることを見ました。この章では
`state.go`（489行）を開き、ゲームの状態すべてを
抱える `Game` 構造体と、その中身を読みます。
対応する C は pacman.c 142〜678行です。
SPEC H7 の決定 ――「状態は `Game` 型に集め、
振る舞いはメソッドにする」― の、状態の側の
実装です。

## 2.1 Game 構造体 ― 7つの部屋

`Game` の定義は state.go 394〜402行です。

```go
type Game struct {
	Scene  Scene
	Timing TimingState
	Intro  IntroState
	Play   PlayState
	Input  InputState
	Audio  AudioState
	Gfx    GfxState
}
```

C の状態は大域に1つの構造体でした（C版 第5章）。
Go 版も「状態は1つ」という設計は同じですが、
置き場所が大域変数から、`Game` 型の値へ移って
います。大域に置かないことの効き目は、テストが
「もう1つのゲーム」を作れることです（第12章）。

中身は7つの部屋に分かれています。

- `Scene`: いまの場面（イントロか、ゲームか）
- `Timing`: ティックカウンタ
- `Intro`: イントロ場面の状態
- `Play`: ゲーム本編の状態
- `Input`: 機器から合流した入力
- `Audio`: 音のハードウェア状態
- `Gfx`: 描画側が読む盤面データ

C では `state.game`、`state.input` のように
ドットでたどった階層が、そのまま構造体の
フィールドになっています。

## 2.2 部屋の中身

`Timing` の中身は第1章で見たとおり、ティック
カウンタ1つです（state.go 317〜319行）。蓄積用の
フィールドは H1 で消えました。

本編の状態 `PlayState` は state.go 327〜355行です。
冒頭にトリガーが12個並びます。

```go
type PlayState struct {
	Xorshift        uint32
	Hiscore         uint32
	Started         Trigger
	ReadyStarted    Trigger
	RoundStarted    Trigger
	RoundWon        Trigger
	GameOver        Trigger
	DotEaten        Trigger
	PillEaten       Trigger
	GhostEaten      Trigger
	PacmanEaten     Trigger
	FruitEaten      Trigger
	ForceLeaveHouse Trigger
	FruitActive     Trigger
	Freeze          Freeze
	Round           uint8
	Score           uint32
	NumLives        int8
	NumGhostsEaten  uint8
	NumDotsEaten    uint8
```

（引用は途中まで。このあと全体カウンタ、ゴースト
4匹とパックマンの実体、出現中のフルーツが続きます）

C の `state.game` とほぼ同じ顔ぶれです。トリガーの
型 `Trigger` は state.go 219〜221行で、発火する
ティックを1つ持つだけの小さな構造体として定義
され、メソッドは timing.go に置かれています
（第3章）。

```go
type Trigger struct {
	Tick uint32
}
```

`Freeze` は、ゲームが止まる理由の集合です。
C では `uint8` のビット値でしたが、Go 版では
`Freeze` という型にし、操作はメソッドの後ろに
隠してあります（2.4節）。`Round` が `uint8` なのは
原典どおりで、256 の次は 0 に戻ります（SPEC 第2節）。

`Gfx` の部屋には、盤面の表（`VideoRAM` と
`ColorRAM`、28×36 の2次元配列）やスプライトの
表が入ります。ただし GPU 側の資源はここには
ありません。画像の実体は render.go の `Renderer`
が持ちます（第9章）。「状態の表」と「描画の
資源」を分けたのも、H6 の描画方式に合わせた
切り分けです。

## 2.3 ゼロ値が初期状態 ― NewGame

ゲームの生成は rules.go 320〜324行の `NewGame`
です。

```go
func NewGame() *Game {
	g := &Game{}
	g.Intro.Started.Start(g.Timing.Tick)
	return g
}
```

注目点は `&Game{}` です。フィールドを何も指定
しない複合リテラルは、全フィールドが**ゼロ値**
（数値なら 0、真偽値なら false）の値を作ります。
Go では「ゼロ値がそのまま使える状態であること」
が設計の約束になっていて、このゲームも、ゼロ値の
`Game` がほぼ初期状態になるように作られています。

足りないのは1つだけ。イントロの開始トリガーを
立てることです。`Start` は「次のティック」を
書くので、この時点（ティック 0）で立てると
ティック 1 で発火し、最初の `Tick()` で場面が
イントロになります。原典の初期化コールバックが
最初のフレームの前にイントロを開始していた
ことの、写しです。

C や Nim では、初期化は「大域の状態に値を書き込む
関数」の仕事でした。Go 版では「ゼロ値＋1手」に
なり、初期化のコードがほぼ消えています。これは
H7 の「状態は `Game` 型に集める」決定が連れて
きた、副産物の簡素さです。

## 2.4 メソッドとレシーバ ― Freeze の操作

`Freeze` の操作は state.go 193〜204行にあります。

```go
// Has reports whether the given freeze reason is present.
func (f Freeze) Has(o Freeze) bool { return f&o != 0 }

// Add sets the given freeze reason.
func (f *Freeze) Add(o Freeze) { *f |= o }

// Clear removes the given freeze reason (C: freeze &= ~o).
func (f *Freeze) Clear(o Freeze) { *f &^= o }

// Empty reports whether no freeze reason is present.
func (f Freeze) Empty() bool { return f == 0 }
```

関数の前の `(f Freeze)` が**レシーバ**です。
「この関数は `Freeze` 型の値に属する」という
宣言で、呼び出しは `g.Play.Freeze.Has(FreezeReady)`
のように、値の後ろにドットで続けます。

読みだけの `Has` と `Empty` は値レシーバ
（`f Freeze`）、書き換える `Add` と `Clear` は
ポインタレシーバ（`f *Freeze`）です。値レシーバは
コピーを受け取るので、元の値を書き換えられません。
書き換えたいメソッドは、ポインタで受け取る必要が
あります。この使い分けは第3章でもう一度出てきます。

ビット演算そのもの（`|`、`&`、反転の `&^`）は
メソッドの中に隠れ、呼び出し側は「理由があるか」
「理由を足す」という出来事の言葉で書けます。
Freeze の使い道の全体は第6章で読みます。

もう1つ、置き場所の話を。`Trigger` のメソッドは
state.go ではなく timing.go にあります。Go では、
メソッドは「型と同じパッケージ」であれば、どの
ファイルに書いても構いません。型の定義と振る舞いを
ファイル単位で分けられるので、区画ごとのファイル
分割（H7）が成り立ちます。

## 2.5 定義型と iota ― 列挙の作り方

場面の型 `Scene` は state.go 108〜113行です。

```go
type Scene int

const (
	SceneIntro Scene = iota
	SceneGame
)
```

`type Scene int` は、`int` を土台にした新しい型
（定義型）を作ります。`Scene` と `int` は別の型
として扱われ、場面のつもりでない整数を間違えて
渡すと、コンパイルで止まります。

定数の並びの `iota` は、Go の列挙の道具です。
`const` ブロックの中で「何行目か」を表す特別な
値で、最初の行が 0、次が 1 と増えます。右辺の
式は省略すると前の行の式が繰り返されるので、
`SceneGame` は自動的に 1 になります。

方向の `Dir`（state.go 117〜125行）、フルーツの
`Fruit`（state.go 128〜141行）も同じ作りです。
どちらも末尾に `NumDirs`、`NumFruits` という
「数え上げの番兵」が付いていて、要素の個数が
そのまま定数になります。

`Freeze` の定数（state.go 183〜191行）は、
`iota` の応用編です。

```go
type Freeze uint8

const (
	FreezePrelude Freeze = 1 << iota
	FreezeReady
	FreezeEatGhost
	FreezeDead
	FreezeWon
)
```

`1 << iota` は「1 を iota の分だけ左へずらす」
で、行ごとに 1、2、4、8、16 というビット値に
なります。式の繰り返しと組み合わせて、「ビット
フラグの列挙」を型つきで書く定石です。土台が
`uint8` なのは、C の `freezetype_t` が `uint8` の
ビット値だったことの踏襲です。

---

## Go の道具 ― 構造体と type 宣言、iota

この章に出てきた道具を、まとめておきます。

**構造体（struct）** は、名前つきのフィールドを
束ねた型です。

```go
type Int2 struct {
	X int16
	Y int16
}
```

これは state.go 225〜228行の座標型です。値の
生成は `Int2{X: 3, Y: 4}` のような複合リテラルで
行い、フィールドは `p.X` の形で読み書きします。
生成の補助として `I2(x, y)` という小さな関数も
用意されています（state.go 231行）。

**type 宣言** には2つの顔があります。`type Int2
struct {...}` のように新しい構造を作る顔と、
`type Scene int` のように既存の型を土台に新しい
型を作る顔（定義型）です。定義型は、土台の型とは
別の型として扱われます。ここが C の `typedef` と
違うところで、C の `typedef` は別名にすぎませんが、
Go の定義型は「同じ表現を持つ別の型」です。
列挙に定義型を使うと、取り違えをコンパイラが
検出してくれます。

**iota** は `const` ブロック専用のカウンタです。
ブロックの先頭行で 0、1行ごとに 1 増えます。
右辺を省略した行は、直前の行の式（と型）を
そのまま使います。だから

- 素直な連番: `Scene = iota` と書けば 0、1、2…
- ビット値: `1 << iota` と書けば 1、2、4、8…

の2つの列挙が、同じ仕組みで書けます。Nim 版の
`enum`（Nim 版 第2章）と並べると、Nim は言語に
列挙型そのものがあり、Go は「定義型＋定数＋iota」
の組み合わせで列挙を作る、という違いが見えます。
結果として得られる安全性（取り違えの検出）は
近いものになります。

---

## 解剖メモ（第2章）

- 状態は大域変数から `Game` 型の値へ（H7）。
  「状態は1つ」の設計は C と同じで、置き場所が
  変わった。
- ゼロ値がほぼ初期状態。`NewGame` の仕事は
  イントロの開始トリガーを立てる1手だけ。
- `Freeze` は、ビット演算をメソッドの後ろに
  隠した定義型。値レシーバ（読む）とポインタ
  レシーバ（書く）の使い分けがここに出る。
- 列挙は「定義型＋`iota`」で作る。`Freeze` の
  `1 << iota` はビットフラグ列挙の定石。
- メソッドは型と同じパッケージなら別ファイルに
  置ける。区画ごとのファイル分割の土台。

## 手を動かす（読解演習）

1. `PlayState` のフィールドを数えて、C の
   `state.game`（pacman.c 420〜540行あたり）と
   対応表を作ってください。Go 版にだけある
   もの、C にだけあるものはありますか。
2. `Dir` の定義（state.go 117〜125行）にある
   コメント「bit0==0: horizontal, bit0==1:
   vertical」を確かめてください。4つの定数の
   値から、この約束が成り立つことを示して
   ください。
3. `NewGame` で `Started.Start` を呼ばずに
   `&Game{}` だけを返したら、最初の `Tick()` で
   何が起きるか（起きないか）。`Trigger` の
   ゼロ値と、`Tick` の中の `Now` の判定から
   考えてください。

## 確認問題

**問1**：`Game` 型のフィールドはいくつで、
何という名前ですか。

<details>
<summary>答え</summary>

7つです。`Scene`、`Timing`、`Intro`、`Play`、
`Input`、`Audio`、`Gfx`。C の状態階層を、
構造体のフィールドとしてそのまま抱えた形に
なっています（state.go 394〜402行）。
</details>

**問2**：`Freeze` の `Has` が値レシーバで、
`Add` がポインタレシーバなのはなぜですか。

<details>
<summary>答え</summary>

値レシーバはコピーを受け取るため、元の値を
書き換えられないからです。読むだけの `Has` は
値レシーバで十分ですが、理由を足す `Add` は
元の `Freeze` を書き換える必要があるので、
ポインタレシーバにします。
</details>

**問3**：`FreezePrelude` から `FreezeWon` までの
値は、それぞれいくつですか。

<details>
<summary>答え</summary>

1、2、4、8、16 です。`1 << iota` の式が
行ごとに繰り返され、iota が 0、1、2、3、4 と
増えるため、1 をその分だけ左へずらした
ビット値になります（state.go 186〜191行）。
</details>

---

### 次回予告

**第3章 時間の語彙**
― `timing.go` を開きます。`Trigger` のメソッド群
（`Start`、`Now`、`Since` ほか）が、C の関数群と
どう対応するか。そして、時刻を引数で渡す形に
なった理由を読みます。

---

# 第3章 時間の語彙

## 前章までのあらすじ

第2章で、状態の置き場所を見ました。ゲームの状態は
1つの `Game` 型に集まり、その中には時間トリガーが
いくつも並んでいました。この章では、そのトリガーを
扱う語彙 ―― `timing.go`（97行）― を読みます。
対応する C は pacman.c 826〜943行です。

## 3.1 Trigger は、フィールド1つの型

トリガーとは、「何ティック目に起きるか」を1つの
数字で持つ仕組みでした。Go 版の `Trigger` は、
`state.go` でこう定義されています（state.go
217〜221行）。

```go
// Trigger remembers one future tick (C: trigger_t).
// The methods live in timing.go.
type Trigger struct {
	Tick uint32
}
```

フィールドは `Tick uint32` の1つだけです。C の
`trigger_t` と同じ形ですが、違うのはメソッドの
置き場所です。コメントにあるとおり、メソッドは
`timing.go` の側にまとめてあります。Go では、
型の定義とそのメソッドを同じパッケージの中なら
別ファイルに分けられます。「データの形は state.go、
振る舞いは timing.go」という分担です。

## 3.2 今のティックは、引数で渡す

C 版と Nim 版のトリガーは、グローバルな状態から
「今のティック」を勝手に読んでいました。Go 版は
違います。メソッドはすべて、今のティックを引数
`now` で受け取ります。中心の4つを引用します
（timing.go 20〜32行）。

```go
// Start sets the trigger to the next game tick.
func (t *Trigger) Start(now uint32) { t.Tick = now + 1 }

// StartAfter sets the trigger to a future tick.
func (t *Trigger) StartAfter(now, ticks uint32) { t.Tick = now + ticks }

// Disable deactivates the trigger.
func (t *Trigger) Disable() { t.Tick = DisabledTicks }

// （中略: DisabledTrigger）

// Now reports whether the trigger fires at the given tick.
func (t Trigger) Now(now uint32) bool { return t.Tick == now }
```

この4つの間、26行と32行の間には、無効化された
トリガーを作って返す `DisabledTrigger`
（timing.go 29行）も挟まっています。

なぜ引数で渡すのかは、ファイルの冒頭コメントに
書かれています（timing.go 4〜6行）。グローバルを
読まないので、語彙がヘッドレスのテストからも
そのまま使える、というのが理由です。呼び出す側は、
今のティックを明示して渡します。たとえば rules.go
ではこうなります（rules.go 154行）。

```go
g.Play.ForceLeaveHouse.Start(g.Timing.Tick)
```

`Start` の **+1** は C と同じ約束です。「開始する」
とは「次のティックで発火する」こと。この約束が
あるおかげで、「今ティック起きた出来事」は、その
ティックの残りの処理ではまだ発火していないものと
して扱えます。時間の意味は、言語が変わっても
1つも変わっていません。

## 3.3 since と、その仲間たち

「発火してから何ティック経ったか」を返すのが
`Since`（timing.go 35〜40行）です。

```go
// Since returns the number of ticks since the trigger fired.
func (t Trigger) Since(now uint32) uint32 {
	if now >= t.Tick {
		return now - t.Tick
	}
	return DisabledTicks
}
```

まだ発火していない、あるいは無効化された
トリガーについては、大きな番兵の値
`DisabledTicks`（0xFFFFFFFF）を返します。この
番兵が効くので、`Between`（範囲内か）、
`AfterOnce`（ちょうどNティック前か）、`After`
（Nティック以上前か）、`Before`（Nティック未満
前か）といった判定が、すべて「無効なら偽」で
統一できます。

Go らしい小さな違いが1つあります。`Between` は、
範囲の指定そのものがおかしい（`begin >= end`）
場合に `panic` で落とします（timing.go 44〜48行）。
呼び出し側の書き間違いは、静かに間違った答えを
返すより、その場で止めて知らせる方がよい、という
判断です。

## 3.4 xorshift ― マスクが要らない理由

乱数は C と同じ xorshift です。Go 版では
`PlayState` のメソッドになっています
（timing.go 10〜17行）。

```go
// xorshift32 is the xorshift random number generator (pacman.c 827-833).
func (p *PlayState) xorshift32() uint32 {
	x := p.Xorshift
	x ^= x << 13
	x ^= x >> 17
	x ^= x << 5
	p.Xorshift = x
	return x
}
```

Python 版では、32ビットに収めるために各行で
`& 0xFFFFFFFF` のマスクが必要でした。Go 版に
マスクがないのは、`uint32` 型の値が C の
`uint32_t` と同じく、あふれた分を自然に
切り捨てるからです。「型が幅を持っている」ことの
効き目が、ここに出ています。種 0x12345678 から
始めた列が C と完全一致することは、検証で
確認済みです（付録C）。

## 3.5 ティックは、エンジンが数える

最後に、ティックそのものの数え方です。C 版は、
実時間を蓄積してティックに変える方式でした
（1ティック = 16,666,666 ナノ秒、許容誤差つき、
「先に払って、あとで精算する」残高の仕組み）。

Go 版では、この仕組みが丸ごと消えています。
仕様書の決定 H1 ―― **1回の `Update` = 1ティック、
TPS は 60 に固定** ― により、蓄積と精算は
Ebitengine の側が引き受けるからです。残ったのは
ティックカウンタ1つだけです（state.go 315〜319行）。

```go
// TimingState holds the tick counter. The C accumulator fields are
// gone: Ebitengine calls Update once per tick (SPEC H1).
type TimingState struct {
	Tick uint32
}
```

コメントに「C の蓄積用フィールドは消えた」と
明記されているのが、この移植の進め方らしい
ところです。はみ出す箇所は、先に仕様書で決めて、
コードの中にも痕跡を残す。本書が H 番号を
引いて進むのは、そのためです。

## 3.6 Go の道具 ― 値レシーバとポインタレシーバ

この章のメソッドには、2種類の顔つきがありました。
`Start` は `func (t *Trigger)`、`Now` は
`func (t Trigger)` です。括弧の中身が
**レシーバ**で、「このメソッドはどの型のものか」
を示します。アスタリスクの有無が、使い分けの
目印です。

- **ポインタレシーバ**（`*Trigger`）― 中身を
  書き換えるメソッド。`Start`、`StartAfter`、
  `Disable` がそうです。ポインタで受けるので、
  `t.Tick = ...` の代入が呼び出し側の実物に届きます
- **値レシーバ**（`Trigger`）― 読むだけの
  メソッド。`Now`、`Since`、`Between` など判定系は
  すべてこちらです。コピーを受け取って読むだけ
  なので、実物を壊す心配がありません

目安は単純で、「変えるならポインタ、変えないなら
値」です。`xorshift32` が `*PlayState` を受ける
のも、乱数の状態を書き換えるからでした。

もう1つ、入力側の例を。`InputState` の `Disable`
は、フィールドを1つずつ消すのではなく、ゼロ値を
丸ごと代入します（timing.go 77行）。

```go
func (in *InputState) Disable() { *in = InputState{} }
```

「空の構造体を代入すれば初期状態に戻る」という
書き方ができるのは、ゼロ値が意味を持つように
型を設計してあるからです。この話は第2章の
ゼロ値の話とつながっています。

---

## 解剖メモ（第3章）

- トリガーの語彙は C とほぼ同形。`Start` の
  +1 の約束もそのままで、時間の意味は
  変わらない。
- ただし「今のティック」は引数 `now` で渡す。
  グローバルを読まないので、語彙がテストから
  そのまま使える（timing.go 冒頭コメント）。
- `Since` の番兵 `DisabledTicks` が、判定の
  語彙全体を「無効なら偽」で統一する。
- `Between` は不正な範囲指定を `panic` で
  止める。C にはなかった、Go 側の判断。
- ティックの蓄積と精算は H1 によりエンジン側へ。
  `TimingState` にはカウンタ1つだけが残った。

## 手を動かす（読解演習）

1. `timing.go` のメソッドを全部拾って、
   pacman.c 844〜943行の関数と対応表を
   作ってください。対応しないものは
   ありますか。
2. `Start` の +1 がないと、どの場面で
   困るか。rules.go の中で `Start` が呼ばれる
   場面を1つ選んで考えてください。
3. `Between` の `panic` を取り除いて、代わりに
   「常に偽を返す」作りにしたら、何が困るか
   述べてください。

## 確認問題

**問1**：Go 版のトリガーが、今のティックを
引数で受け取るのはなぜですか。

<details>
<summary>答え</summary>

グローバルな状態を読まないためです。おかげで
トリガーの語彙が、画面も音もないヘッドレスの
テストからそのまま使えます（timing.go 4〜6行の
コメント）。呼び出し側は `g.Timing.Tick` を
明示して渡します。
</details>

**問2**：`Since` が番兵を返すのは、
どんな場合ですか。

<details>
<summary>答え</summary>

トリガーがまだ発火していない（発火予定の
ティックが今より先）場合と、無効化されて
いる場合です。どちらも「経過ティック数は
意味を持たない」ので、大きな値
`DisabledTicks` を返し、それを使う判定は
すべて偽になります。
</details>

**問3**：`Start` と `Now` で、レシーバの
形が違うのはなぜですか。

<details>
<summary>答え</summary>

`Start` はトリガーの中身（`Tick`）を書き換える
のでポインタレシーバ `*Trigger`、`Now` は
読んで判定するだけなので値レシーバ `Trigger`
です。「変えるならポインタ、変えないなら値」が
このファイルの使い分けです。
</details>

---

### 次回予告

**第4章 幾何と Int2**
― 盤面の座標を扱う `geom.go` に進みます。
演算子オーバーロードのない Go で、C の
演算子式をどう書くか。そして剰余 `%` を
めぐる、移植者自身の勘違いの顛末も
正直にお話しします。

---

# 第4章 幾何と Int2

## 前章までのあらすじ

第3章で、時間の語彙を読みました。トリガーは
「今のティック」を引数で受け取り、ティックの
蓄積そのものはエンジンに任せるのでした。
この章では、座標の語彙 ―― `geom.go`（170行）
― に進みます。対応する C は pacman.c
988〜991行と 1230〜1361行です。

## 4.1 Int2 と、I2 という作り方

座標は `Int2` という型で表します（state.go
223〜231行）。

```go
// Int2 is a 2D integer vector (C: int2_t).
// Arithmetic methods live in geom.go.
type Int2 struct {
	X int16
	Y int16
}

// I2 constructs an Int2.
func I2(x, y int16) Int2 { return Int2{X: x, Y: y} }
```

`I2(3, 4)` と書けば座標が1つできます。C の
複合リテラルをいちいち書く代わりに、短い
コンストラクタ関数を用意する ―― これが
Go でよく見る形です。フィールドは `int16`。
画面は 224×288 ピクセルしかないので、16ビットで
足ります。

## 4.2 演算子が作れない言語で

C では、座標の足し算は演算子で書けました。
Nim 版では、演算子オーバーロードで `+` や `-` を
`Int2` 用に定義できました。**Go には、その仕組みが
ありません**。演算子は言語が用意したものだけ。
ではどうするか。答えは、メソッドにする、です
（geom.go 10〜17行）。

```go
// Add returns v + o.
func (v Int2) Add(o Int2) Int2 { return I2(v.X+o.X, v.Y+o.Y) }

// Sub returns v - o.
func (v Int2) Sub(o Int2) Int2 { return I2(v.X-o.X, v.Y-o.Y) }

// Scale returns v * s.
func (v Int2) Scale(s int16) Int2 { return I2(v.X*s, v.Y*s) }
```

C で `a + b` と書いていたものは、Go では
`a.Add(b)` になります。読みにくくなるかと
思えば、そうでもありません。メソッドは値を
受け取って新しい値を返すだけなので、式の
意味は演算子と変わらないからです。距離の
2乗（geom.go 19〜24行）も同じ形です。

```go
// SquaredDistance returns the squared distance between v and o.
func (v Int2) SquaredDistance(o Int2) int32 {
	dx := int32(o.X - v.X)
	dy := int32(o.Y - v.Y)
	return dx*dx + dy*dy
}
```

ゴーストが「目標にいちばん近い方向」を選ぶ
判定（第7章）で、この `SquaredDistance` が
使われます。平方根を取らないのは C と同じで、
大小の比較だけなら2乗のままで足りるからです。

## 4.3 マスの中心までの距離と、剰余

`distToTileMid` は、ピクセル位置から「そのマスの
中心までのずれ」を返します（geom.go 44〜47行）。

```go
// distToTileMid returns the distance from a pixel position to the
// middle of its tile (pacman.c 988-991).
func distToTileMid(pos Int2) Int2 {
	return I2(TileWidth/2-pos.X%TileWidth, TileHeight/2-pos.Y%TileHeight)
}
```

ここで `%`（剰余）が効いています。位置が負に
なる場面 ―― テレポットトンネルで画面の端を
回り込むとき ―― では、剰余の符号の決まり方が
そのまま挙動になります。C の `%` は、割り算の
切り捨てに合わせて「余りの符号は割られる数と
同じ」です。Go の `%` と `/` も、まったく同じ
切り捨て型です。だからこの行は、C と1文字も
変えずにそのまま動きます。

## 4.4 cmod の顛末 ― 正直な話

ここで、移植者（この本の書き手）の勘違いを
1つ、正直にお話しします。

Nim 版を作ったとき、こちらは「Nim の `mod` は
床関数型（負の数では C と違う答えになる）」と
思い込んでいました。根拠は Python の `%` の
振る舞いです。Python の `%` は本当に床関数型
なので、それを持ち込んでしまったのです。
念のため、geom には `cmod` という補助関数
（C の `%` を再現するつもりのもの）を用意して、
そちらを使うようにしていました。

ところが 2026-11-20、実測で確かめ直すと、
**Nim の `mod` と `div` も C と同じ切り捨て型**
でした。たとえば `-7 mod 8` は、床関数型なら
1、C と同じなら −7 です。答えは −7 でした。
つまり `cmod` は `mod` とまったく同じもので、
最初から要らなかったのです。当時「cmod が
正しく動く」と確認した検証も、`mod` と答えが
同じだったために勘違いを見抜けませんでした。

Go 版は、この顛末を知ったうえで書かれています。
ファイルの冒頭コメントに、はっきり書いてあります
（geom.go 4〜6行）。

```go
// Go's % and / truncate toward zero just like C, so the Nim version's
// cmod helper is not needed here; negative positions in the teleport
// tunnel behave identically by construction.
```

教訓は2つあります。1つ、言語の演算の意味は、
隣の言語からの類推ではなく、その言語で実測
すること。もう1つ、検証は「自分の思い込みと
違う答えが出る条件」で組まないと、思い込みを
素通りさせること。この話は付録C の検証の記録
にも残してあります。

## 4.5 盤面への問い合わせ

`geom.go` の後半は、盤面に問い合わせる語彙です。
範囲を丸める `clampedTilePos`（geom.go 54〜70行）、
マスのコードを取る `tileCodeAt`（94〜100行）、
トンネルかどうか（114〜116行）、ゴーストが
上向きに進めない赤ゾーンかどうか（119〜121行）。

```go
// isTunnel reports whether a tile is in the teleport tunnel.
func isTunnel(tilePos Int2) bool {
	return tilePos.Y == 17 && (tilePos.X <= 5 || tilePos.X >= 22)
}
```

そして移動の判定 `canMove`（125〜141行）と、
実際に動かす `move`（145〜170行）です。
`canMove` の中では、メソッド連鎖が実戦で
使われています（geom.go 137行）。

```go
	checkPos := clampedTilePos(tilePos.Add(dirVec))
```

「今のマスに方向ベクトルを足して、範囲に丸める」
という処理が、1行で読めます。C では関数呼び出しの
入れ子でしたが、メソッドにすると左から右へ、
処理の順番どおりに読めるのが利点です。

なお `tileCodeAt` は、範囲外の座標を渡されると
`panic` で止まります（geom.go 94〜100行）。
第3章の `Between` と同じで、「呼び出し側の
間違いは、その場で知らせる」というこの移植の
方針です。

## 4.6 Go の道具 ― メソッド連鎖

この章の道具は **メソッド連鎖**です。`Add` や
`Sub` のような「値を受け取って、新しい値を返す」
メソッドは、戻り値に対してそのまま次のメソッドを
呼んで、鎖のようにつなげられます。

```go
tilePos.Add(dirVec)          // 座標 + ベクトル（書式の例）
pos.Add(dirVec).Scale(2)     // 足してから2倍（書式の例）
```

大事なのは、`Int2` が **値型** だということです。
連鎖の途中のメソッドは、元の値を書き換えません。
`a.Add(b)` を呼んでも `a` は元のまま。だから
連鎖は「式」として安心して書けます。もし
ポインタで受けて中身を書き換えるメソッドだったら、
連鎖の途中で思わぬものが壊れます。

C の演算子式 `a + b * 2` に比べると、Go の連鎖は
演算子の優先順位を持ちません。書いた順番に、
左から右へ評価されます。制約ではありますが、
「読む順番と評価の順番が同じ」という分かり
やすさと引き換えです。この移植では、演算子が
作れないことを欠点としてではなく、書き方の
前提として受け入れています。

---

## 解剖メモ（第4章）

- Go には演算子オーバーロードがない。座標の
  演算は `Add` / `Sub` / `Scale` のメソッドに
  なり、メソッド連鎖で式を組む。
- `%` と `/` は C と同じ切り捨て型なので、
  `distToTileMid` は原典のまま移せる。
- Nim 版で用意した `cmod` は、実測の結果
  不要だった（Nim の `mod` も切り捨て型）。
  Go では最初から置いていない。類推でなく
  実測すること、が教訓。
- 範囲外の座標など、呼び出し側の間違いは
  `panic` でその場で知らせる方針。

## 手を動かす（読解演習）

1. `geom.go` のメソッドと関数を全部拾って、
   pacman.c 1230〜1361行の関数と対応表を
   作ってください。
2. Go で `-7 % 8` と `-7 / 8` を計算し、
   Python の `-7 % 8` と比べてください。
   違いがトンネルの挙動にどう響くか、
   `distToTileMid` を例に考えてください。
3. `move`（geom.go 145〜170行）の中で、
   画面の端を回り込む処理（`r.X < 0` の
   分岐）を読み、トンネルを通るゴーストの
   座標がどう変化するか追ってください。

## 確認問題

**問1**：Go で座標の足し算を `a + b` と
書けないのはなぜですか。

<details>
<summary>答え</summary>

Go には演算子オーバーロードの仕組みがなく、
演算子は言語が用意した型にしか使えない
からです。その代わり `a.Add(b)` のように
メソッドで表し、戻り値をつないでメソッド
連鎖で式を組みます。
</details>

**問2**：Nim 版の `cmod` は、結局
何だったのですか。

<details>
<summary>答え</summary>

不要な補助関数でした。Nim の `mod` は
Python の `%` と違って C と同じ切り捨て型
なので、`cmod` は `mod` とまったく同じ
答えを返すものでした。2026-11-20 の実測で
判明しました。思い込みの根拠は Python の
振る舞いの持ち込みです。
</details>

**問3**：メソッド連鎖が安心して書けるのは、
`Int2` のどんな性質のおかげですか。

<details>
<summary>答え</summary>

値型であり、メソッドが元の値を書き換えず
新しい値を返すからです。`a.Add(b)` を呼んでも
`a` は変わらないので、連鎖を「式」として
扱えます。
</details>

---

### 次回予告

**第5章 盤面とデータ**
― ROM データ 9,316 個を、どうやって
間違いなく持ち運ぶか。手で写さず、プログラムに
写させる「コード生成」の話をします。

---

# 第5章 盤面とデータ

## 前章までのあらすじ

第4章で、座標の語彙を読みました。演算子が
作れない Go では、座標の演算はメソッドと連鎖で
書くのでした。この章では、ゲームの絵と音の
もとになる ROM データ ―― 9,316個の値 ―― を
どう持ち運ぶかを見ます。主役は、生成された
ファイル `data.go`（608行）と、それを生む
生成器 `tools/extract.go`（113行）です。

## 5.1 決定 H4 ― 生成した Go ソースに埋め込む

原典 pacman.c の末尾（3389〜4303行）には、
タイルやスプライトの絵柄、色、波形といった
ROM データが、C の配列として埋め込まれています。

Go 版の持ち運び方は、仕様書の決定 H4 で
こう決めました。

- 抽出スクリプトで生成した Go ソース
  （`data.go`）に、値の列として埋め込む
- 外部ファイルは持たない（実行時にファイルを
  読む作りにしない）
- 検証は、個数と合計値で行う

Nim 版でも ROM データは機械抽出でした。Go 版も
方針は同じで、違うのは「生成」という形を
はっきりさせたことです。`data.go` は、人が
書くファイルではなく、プログラムが書くファイル
として扱います。

## 5.2 data.go の形

`data.go` の冒頭はこうなっています
（data.go 1〜7行）。

```go
// data.go -- ROM data extracted mechanically from pacman.c (lines 3389-4303).
// Generated by tools/extract.go. Do not edit by hand.

package main

var romTiles = [4096]uint8{
	0xCC, 0xEE, 0x11, 0x11, 0x33, 0xEE, 0xCC, 0x00, 0x11, 0x33, 0x66, 0x44, 0x44, 0x33, 0x11, 0x00,
```

「tools/extract.go が生成した。手で編集するな」
と宣言してあるのが大事な点です。中身は7つの
配列で、値の総数は 9,316 個です。

| Go の変数 | C の配列 | 型 | 個数 |
|---|---|---|---|
| romTiles | rom_tiles | uint8 | 4,096 |
| romSprites | rom_sprites | uint8 | 4,096 |
| romHWColors | rom_hwcolors | uint8 | 32 |
| romPalette | rom_palette | uint8 | 256 |
| romWavetable | rom_wavetable | uint8 | 256 |
| sndDumpPrelude | snd_dump_prelude | uint32 | 490 |
| sndDumpDead | snd_dump_dead | uint32 | 90 |

タイルとスプライトの絵柄が 4,096 個ずつ、
色の表が 32 と 256、音の波形が 256、そして
プレリュード（開始音楽）と死亡音のダンプが
490 と 90 です。音楽のダンプだけ `uint32` で、
他はすべて `uint8` です。並びは1行に16個ずつ。
`romTiles` は data.go 6〜263行、`romHWColors`
は 524〜527行、最後の `sndDumpDead` は
601〜608行にあります。

## 5.3 生成器 extract.go の仕組み

生成器は3つの部分からできています。

まず、抽出の仕様を表にした `specs`
（extract.go 26〜34行）です。

```go
var specs = []arraySpec{
	{"rom_tiles", "romTiles", "uint8", 4096, "0x%02X"},
	{"rom_sprites", "romSprites", "uint8", 4096, "0x%02X"},
	{"rom_hwcolors", "romHWColors", "uint8", 32, "0x%02X"},
	{"rom_palette", "romPalette", "uint8", 256, "0x%02X"},
	{"rom_wavetable", "romWavetable", "uint8", 256, "0x%02X"},
	{"snd_dump_prelude", "sndDumpPrelude", "uint32", 490, "0x%08X"},
	{"snd_dump_dead", "sndDumpDead", "uint32", 90, "0x%08X"},
}
```

1行が1配列で、C 側の名前、Go 側の名前、型、
期待する個数、出力の書式を持ちます。表に
しておくことで、配列が増えても行を足すだけで
済みます。

次に、抽出そのものの `extractArray`
（extract.go 38〜57行）。やることは素朴です。
正規表現で `rom_tiles[4096] = {` のような
定義の始まりを探し、そこから `};` までを
切り取り、その中にある数値の字句を全部拾って
数に直します。C の構文をきちんと解析するのでは
なく、「データの並び」としてだけ読むのが
割り切りです。純粋なデータの配列だからこそ、
これで足ります。

最後に `main`（extract.go 59〜113行）が、
配列ごとに個数を数えて仕様と照合し、合計値を
表示しながら、Go のソースとして書き出します。
個数が合わなければ、その場でエラーにして
止まります（extract.go 78〜81行）。

再生成は Makefile から `make data` で行います。
中では生成器を走らせたあと、`gofmt` で整形して
います。生成し直しても結果がバイト単位で
同じになること（再現性）も確認済みです。

## 5.4 照合 ― 個数と合計値

9,316 個の値が全部正しいかどうかを、1つずつ
目で見ることはできません。そこで使うのが、
個数と合計値という「指紋」です。

生成器は抽出のたびに合計値を表示し、テスト
（data_test.go 5〜33行）は同じ合計値を期待値と
して持ちます。実測された合計値はこうです。

| 配列 | 個数 | 合計値 |
|---|---|---|
| romTiles | 4,096 | 267,889 |
| romSprites | 4,096 | 227,290 |
| romHWColors | 32 | 1,852 |
| romPalette | 256 | 589 |
| romWavetable | 256 | 1,856 |
| sndDumpPrelude | 490 | 1,523,003,578,600 |
| sndDumpDead | 90 | 275,197,360,640 |

合計値が1つでもずれれば、どこかの値が欠けたか
化けたことが分かります。もちろん、2つの値が
入れ替わっても合計は変わりませんから、これは
完全な証明ではありません。ただ、個数と合わせれば、
機械抽出で起きがちな事故（途中での欠落、
切り取り範囲のずれ）はほぼ拾えます。さらに
この合計値は、Nim 版の抽出で得た値とも一致して
います。別々の生成器が同じ指紋を出したことが、
二重の裏づけになっています。

## 5.5 Go の道具 ― スライスと配列、生成コードの扱い

Go には、よく似た2つのものがあります。

- **配列** ― 長さが型の一部です。`[4096]uint8` と
  `[256]uint8` は別の型で、代入も比較もできません。
  `data.go` の変数はすべて配列です。「個数が
  決まっているデータ」であることが、型に
  表れています
- **スライス** ― 配列（など）への「窓」です。
  長さは型に含まれず、実行時の値です

テストが合計値を計算するときは、配列から
スライスを作って渡しています（data_test.go
11〜17行）。

```go
		{"romTiles", sumU8(romTiles[:]), 267889},
		{"romSprites", sumU8(romSprites[:]), 227290},
```

`romTiles[:]` が「配列全体を見るスライス」を
作る書き方です。合計を取る関数 `sumU8` は
スライスを受け取るので、長さの違う配列にも
同じ関数が使えます。「データの置き場所は配列で
固定し、処理はスライスで受ける」という分担が、
Go の定石です。

生成コードの扱いも、この章の道具のうちです。
約束は3つあります。生成されたファイルは手で
編集しない。直したいときは生成器を直して
再生成する。そして、生成物もソースと一緒に
置いておく（ビルドに生成手順が要らない）。
`data.go` の冒頭コメントは、この約束を
読み手に伝えるための看板です。

---

## 解剖メモ（第5章）

- データの持ち運びは H4 の決定どおり、
  生成した Go ソースへの埋め込み。外部
  ファイルは持たない。
- `data.go` は7配列・9,316個の値。人は
  書かず、生成器 `tools/extract.go` が
  pacman.c から機械抽出する。
- 生成器は「仕様の表 + 字句を拾う抽出 +
  個数の照合と書き出し」という素朴な作り。
  C の構文解析はしない。
- 照合の指紋は個数と合計値。テストにも
  同じ期待値があり、Nim 版の抽出とも
  合計値が一致した。

## 手を動かす（読解演習）

1. `make data` を実行して、`data.go` が
   バイト単位で変わらないことを確認して
   ください（変わる場合は、何が違うか
   差分を見てください）。
2. extract.go の `specs` に、存在しない
   配列名を1行足して実行すると、どう
   止まりますか。エラーの出方を確認して
   ください（試したら元に戻すこと）。
3. 合計値では検出できないデータの化け方を
   2つ挙げてください。そのうえで、個数と
   合計値の組み合わせで十分だと言える
   理由を述べてください。

## 確認問題

**問1**：`data.go` を手で編集しては
いけないのはなぜですか。

<details>
<summary>答え</summary>

生成されたファイルだからです。手で直しても、
次に生成器を走らせれば上書きされて消えます。
直したいときは生成器（tools/extract.go）を
直して再生成するのが、この移植の約束です。
</details>

**問2**：照合に「合計値」を使う理由と、
その限界は何ですか。

<details>
<summary>答え</summary>

9,316個の値を1つずつ目で確かめることは
できないので、個数と合計値を指紋として
使うためです。欠落や切り取り範囲のずれは
これで拾えます。限界は、値の入れ替わりや、
合計が偶然一致する化け方を検出できない
ことです。
</details>

**問3**：`romTiles[:]` という書き方は
何をしていますか。

<details>
<summary>答え</summary>

配列 `romTiles` 全体を見るスライスを
作っています。配列は長さが型の一部ですが、
スライスにすれば長さを問わない処理
（合計を取る `sumU8` など）に渡せます。
</details>

---

### 次回予告

**第6章 ルールと場面**
― ゲームの進行を担う `rules.go` に
進みます。開始の連鎖の読み方と、Go に
集合型がないことへの答え ― ビット型 +
メソッド ― を見ます。

---

# 第6章 ルールと場面

## 前章までのあらすじ

第5章で、データの置き場所を見ました。ROM データは
生成された `data.go` に収まり、迷路やレベルの表は
`state.go` の表として置かれています。この章では、
その状態を動かす側 ―― `rules.go`（481行）― を
読みます。1ティックの処理順、場面の切り替わり、
そして「止まる理由」を束ねる `Freeze` が中心です。
対応する C は pacman.c 1377〜1583行と
2089〜2403行です。

## 6.1 1ティックの処理順

全体の入り口は `Tick` です（rules.go 331〜348行）。

```go
func (g *Game) Tick() {
	g.Timing.Tick++
	g.sndTick()
	now := g.Timing.Tick
	if g.Intro.Started.Now(now) {
		g.Scene = SceneIntro
	}
	if g.Play.Started.Now(now) {
		g.Scene = SceneGame
	}
	switch g.Scene {
	case SceneIntro:
		g.introTick()
	case SceneGame:
		g.gameTick()
	}
}
```

順番は4つです。

1. ティックカウンタを1つ進める
2. 音のティックを回す
3. 「開始」トリガーが発火していたら場面を切り替える
4. 今の場面のティック（`introTick` か `gameTick`）を呼ぶ

C版のフレームコールバックと同じ並びです。Go 版では
SPEC の H1（1回の `Update` = 1ティック）により、
実時間の蓄積は Ebitengine の側に吸収されました。
そのおかげで、この関数は「画面なしでも呼べる」
形になっています。`main.go` の `Update` からも、
テストからも、同じ `Tick` が呼ばれます（H9）。

## 6.2 開始の連鎖

ゲーム場面の本体 `gameTick`（rules.go 350行）の
冒頭は、トリガーの連鎖になっています。

```go
	if g.Play.Started.Now(now) {
		g.Gfx.Fadein.Start(now)
		g.Play.ReadyStarted.StartAfter(now, 2*60)
		g.sndStart(0, sndPrelude)
		g.gameInit()
	}
	if g.Play.ReadyStarted.Now(now) {
		g.gameRoundInit()
		g.Play.RoundStarted.StartAfter(now, 2*60+10)
	}
	if g.Play.RoundStarted.Now(now) {
		g.Play.Freeze.Clear(FreezeReady)
		g.vidColorText(I2(11, 20), 0x10, "      ")
		g.sndStart(1, sndWeeooh)
	}
```

数字を拾うと、開始の連鎖はこうなります。

- ゲーム開始 → プレリュードが鳴り、`ReadyStarted`
  が **120ティック**（2×60）後に発火する
- `ReadyStarted` → ラウンドの準備（`gameRoundInit`）
  をして、`RoundStarted` が **130ティック**
  （2×60+10）後に発火する
- `RoundStarted` → READY の凍結が解けて、
  キャラクターが動き出す

散らばり／追跡の時刻表も、この `RoundStarted`
からの経過で決まります。最初の境目は **+420**
（7×60）で、散らばりから追跡に切り替わります
（時刻表そのものは第8章で読みます）。

`gameInit`（rules.go 110行）はゲーム全体の初期化で、
`Freeze` を `FreezePrelude` にして止めた状態から
始めます。`gameRoundInit`（rules.go 128行）は
ラウンドごとの準備で、こちらは `FreezeReady` を
立てます（rules.go 149行）。「止まった状態で
用意して、トリガーが解く」というのが、原典から
続く作法です。

小さな注意を1つ。`gameRoundInit` の「勝っていない
とき」の分岐は、**最初のラウンドでも通ります**。
残機は初期値3のまま分岐に入り、そこで1つ減って
2になります。残機の数には「今プレイしている
1機」が含まれている、という原典の数え方です。

## 6.3 Freeze ― 止まる理由の集合

ゲームが止まる理由は5つあります。プレリュード、
READY、ゴースト捕食、死亡、面クリア。理由が
1つでも残っていればキャラクターは動きません。
`gameTick` の中の判定は1行です（rules.go
393〜395行）。

```go
	if g.Play.Freeze.Empty() {
		g.gameUpdateActors()
	}
```

理由の立て方と消し方も、出来事の場所に散らばって
います。ゴーストを食べたら `FreezeEatGhost` を
立てる（rules.go 282行）、パックマンが死んだら
`FreezeDead` を立てる（同 288行）、面クリアなら
`FreezeWon`（同 405行）。時間切れで消えるものは
`gameTick` の中で `Clear` されます。

得点について、ここで1つ約束を確認しておきます。
この移植のスコアは、原典と同じく **10点単位の
内部表現**です。ドットは +1、パワーエサは +5、
表示するときに10倍します。ゴースト捕食の加算は
rules.go 281行にあり、食べた匹数を数えてから
ずらすので、内部値で 20、40、80、160（表示で
200、400、800、1600）になります。

```go
					// increase score by 20, 40, 80, 160 (in 10-point units)
					g.Play.Score += uint32(10 * (1 << g.Play.NumGhostsEaten))
```

## 6.4 Go の道具 ― ビット演算と定義型へのメソッド

`Freeze` の実体は `state.go` にあります
（state.go 180〜203行）。

```go
// Freeze is the set of reasons the game is frozen (C: freezetype_t).
// In C these are (1<<n) bit values in a uint8; here the bit operations
// are hidden behind methods so call sites read as events.
type Freeze uint8

const (
	FreezePrelude Freeze = 1 << iota
	FreezeReady
	FreezeEatGhost
	FreezeDead
	FreezeWon
)

// Has reports whether the given freeze reason is present.
func (f Freeze) Has(o Freeze) bool { return f&o != 0 }

// Add sets the given freeze reason.
func (f *Freeze) Add(o Freeze) { *f |= o }

// Clear removes the given freeze reason (C: freeze &= ~o).
func (f *Freeze) Clear(o Freeze) { *f &^= o }

// Empty reports whether no freeze reason is present.
func (f Freeze) Empty() bool { return f == 0 }
```

C では `uint8` の各ビットが理由に対応し、呼び出し側が
`freeze |= FREEZETYPE_DEAD` のようにビット演算を
直接書いていました。Nim 版では、言語に集合型
（`set`）があったので、そのまま集合で受けました。

Go には集合型がありません。そこで SPEC の H7 は、
**ビットフラグの型にメソッドを持たせる**形を
選びました。実体は C と同じ `uint8` のビットです。
違うのは、ビット演算を `Freeze` 型の中に閉じ込めて、
呼び出し側には `Add`、`Clear`、`Has`、`Empty` という
「出来事の言葉」だけを見せる点です。6.3 で見た
`g.Play.Freeze.Add(FreezeEatGhost)` は、その形が
そのまま文章になっています。

文法の要点は3つです。

- `type Freeze uint8` は、既存の型をもとにした
  **定義型**の宣言です。`uint8` とは別の型として
  扱われ、メソッドを持てます
- 定数は `1 << iota` で 1、2、4、8、16 と並びます。
  `iota` は定数ブロックの中で 0、1、2…と増える
  番号で、2行目以降は式が省略されても同じ形が
  繰り返されます
- `Clear` の `&^` は Go 特有の演算子で、
  「ビットクリア」です。`f &^= o` は
  「`o` に立っているビットを `f` から落とす」で、
  C の `f &= ~o` と同じ意味です

読み取りだけの `Has` と `Empty` は値レシーバ、
書き換える `Add` と `Clear` はポインタレシーバで
受けています。第3章で見た使い分けが、ここでも
そのまま出てきます。

---

## 解剖メモ（第6章）

- `Tick` の処理順は、ティックを進める → 音 →
  場面の切替 → 場面のティック。C のフレーム
  コールバックと同じ並びで、H1 のおかげで
  画面なしに呼べる。
- 開始の連鎖は 120（プレリュード）→ 130
  （READY からラウンド開始）。散らばり／追跡の
  時計も `RoundStarted` が起点で、最初の
  境目は +420。
- `Freeze` は「止まる理由」の集合。空のとき
  だけ `gameUpdateActors` が呼ばれる。
- Go には集合型がないので、H7 はビット型 +
  メソッドで受けた。実体は C と同じビットで、
  呼び出し側の言葉だけが変わっている。
- スコアは10点単位の内部表現。ゴースト捕食は
  内部値で 20、40、80、160。

## 手を動かす（読解演習）

1. `rules.go` の中で `Freeze` の `Add` と
   `Clear` が呼ばれる場所を全部拾い、理由ごとに
   「立てる出来事」と「消える条件」の対応表を
   作ってください。
2. `gameTick` の冒頭3つの `if` を読み、
   ゲーム開始からキャラクターが動き出すまでに
   発火するトリガーを、発火ティックの数字つきで
   並べてください。
3. `Freeze` を C の流儀（素の `uint8` と
   呼び出し側のビット演算）で書いた場合と
   比べて、メソッドに閉じ込めたことで
   呼び出し側の読み方がどう変わるか、
   `FreezeEatGhost` の解除（rules.go 384行）を
   例に述べてください。

## 確認問題

**問1**：`Tick` の中で、場面の切り替わりは
どの順番で判定されますか。

<details>
<summary>答え</summary>

ティックカウンタを進め、音のティックを回した
あとです。`Intro.Started` と `Play.Started` の
発火を見て `Scene` を切り替え、それから今の
場面のティックを呼びます。
</details>

**問2**：READY の凍結が解けるのは、
ラウンド準備から何ティック後ですか。

<details>
<summary>答え</summary>

130ティック後です。`ReadyStarted` の発火時に
`RoundStarted` が `2*60+10` 後にセットされ、
その発火で `FreezeReady` が消えます。
</details>

**問3**：Go 版が `Freeze` にビット型 +
メソッドを選んだ理由は何ですか。

<details>
<summary>答え</summary>

Go には Nim のような集合型がないからです
（SPEC H7）。実体は C と同じ `uint8` の
ビットフラグで、ビット演算を型の中に隠し、
呼び出し側は `Add` や `Clear` といった
出来事の言葉で書けるようにしています。
</details>

---

### 次回予告

**第7章 ゴーストの思考**
― `ghost.go` に移ります。4匹のゴーストが
それぞれ違う目標タイルを持つ仕組みと、
状態機械の読み方を見ます。

---

# 第7章 ゴーストの思考

## 前章までのあらすじ

第6章で、`rules.go` の1ティックの処理順と、
止まる理由を束ねる `Freeze` を読みました。
キャラクターを動かす `gameUpdateActors` の中で、
ゴースト側の処理は `ghost.go`（258行）に
分かれています。この章では、ゴーストの状態機械と
目標タイルの計算を読みます。対応する C は
pacman.c 1750〜2087行です。

## 7.1 状態は8つ

ゴーストの状態は `GhostState` という定義型で
表されます（state.go 167〜177行）。

```go
// GhostState is a ghost's movement state (C: ghoststate_t).
type GhostState int

const (
	GhostStateNone GhostState = iota
	GhostStateChase
	GhostStateScatter
	GhostStateFrightened
	GhostStateEyes
	GhostStateHouse
	GhostStateLeaveHouse
	GhostStateEnterHouse
)
```

実際に動くのは `None` を除く7つです。追跡
（Chase）と散らばり（Scatter）が通常の2態、
青（Frightened）、目（Eyes）、そして家に
まつわる3態（House、LeaveHouse、EnterHouse）
です。

状態を決めるのは `updateGhostState`
（ghost.go 57行）です。今の状態ごとに
「次はどの状態か」を計算し、変わったときだけ
移行の後始末をします（ghost.go 98行〜）。
後始末の中身も原典どおりで、たとえば散らばり／
追跡から別の状態へ移るときは進行方向を反転
させます。青から抜けるときは反転させません。

呼び出しの側を見ると、この関数は
`gameUpdateActors` のゴーストのループの中で、
**毎ティック**呼ばれます（rules.go 304〜305行）。

```go
		g.updateGhostState(ghost)
		g.updateGhostTarget(ghost)
```

状態の判定も、目標の計算も、ティックごとに
やり直すのがこの実装の前提です。次の節と
7.3 で効いてきます。

## 7.2 目標タイルの計算

思考の中心は `updateGhostTarget`
（ghost.go 118〜152行）です。状態ごとに
目標タイルを1つ決めます。散らばりでは、
4匹それぞれの「持ち場」が表になっています
（state.go 406行〜）。Blinky は右上、Pinky は
左上、Inky は右下、Clyde は左下です。

追跡のときは、4匹で計算が全部違います。

```go
		pmPos := pixelToTilePos(pm.Pos)
		pmDir := dirToVec(pm.Dir)
		switch ghost.Typ {
		case GhostBlinky:
			pos = pmPos
		case GhostPinky:
			// 4 tiles ahead of Pacman (without the arcade 'diagonal overflow')
			pos = pmPos.Add(pmDir.Scale(4))
		case GhostInky:
			blinkyPos := pixelToTilePos(g.Play.Ghost[GhostBlinky].Actor.Pos)
			p := pmPos.Add(pmDir.Scale(2))
			d := p.Sub(blinkyPos)
			pos = blinkyPos.Add(d.Scale(2))
		case GhostClyde:
			if ghost.Actor.Pos.pixelToTile().SquaredDistance(pmPos) > 64 {
				pos = pmPos
			} else {
				pos = ghostScatterTargets[GhostClyde]
			}
		}
```

1匹ずつ読むと、性格の違いが見えます。

- **Blinky** は、パックマンの今いるマスそのもの
- **Pinky** は、パックマンの向きの **4マス先**。
  原作アーケード版には、上向きのときに斜めに
  ずれる癖がありましたが、原典が未再現なので
  ここもありません（コメントに明記されています）
- **Inky** は、パックマンの **2マス先**を支点に、
  Blinky の位置を反転させた点。`p` から Blinky
  へのずれ `d` を2倍にして、Blinky の位置に
  足し戻しています。第4章で見た `Int2` の
  メソッド連鎖（`Add`、`Sub`、`Scale`）が、
  ここで実戦投入されています
- **Clyde** は、パックマンとの距離で切り替わります。
  距離の2乗が 64（= 8タイルの2乗）より大きければ
  パックマン自身、小さければ自分の持ち場。
  近づきすぎると逃げる、という性格はこの
  1つの条件から出ています

目（Eyes）の目標は固定です（ghost.go 150行）。

```go
	case GhostStateEyes:
		pos = I2(13, 14)
```

家の扉の前のマス (13, 14) を目指し、着いたら
EnterHouse に移って家の中へ降りていきます。

## 7.3 青の目標は、毎ティック引き直す

Frightened の目標は、乱数で決まります
（ghost.go 145〜148行）。

```go
	case GhostStateFrightened:
		// random target position (random direction at each intersection)
		pos = I2(int16(g.Play.xorshift32()%DisplayTilesX),
			int16(g.Play.xorshift32()%DisplayTilesY))
```

ここで 7.1 の前提が効きます。`updateGhostTarget`
は毎ティック呼ばれるので、青いゴーストは
**毎ティック目標を引き直し、そのたびに乱数を
2回消費します**。「マスの中心に着いたときだけ
抽選する」のではありません。コメントに
「交差点ごとにランダムな方向」とあるのは
原典のコメントの写しで、実際の消費は
ティックごとです。原典の構造そのままで、
Go 版もそこは変えていません。

なお、目標が毎ティック変わっても、進む方向が
毎ティック変わるわけではありません。方向の
決定には別の歯止めがあります（7.4）。

## 7.4 方向を決めるのは、マスの中心だけ

`updateGhostDir`（ghost.go 161行）は、
次の方向 `NextDir` を選ぶ関数です。通常の
状態（散らばり／追跡／青）では、まず今いる
位置がマスの中心かどうかを調べます
（ghost.go 217〜218行）。

```go
		distToMid := distToTileMid(ghost.Actor.Pos)
		if distToMid.X == 0 && distToMid.Y == 0 {
```

中心にいるときだけ、4方向を試して、目標に
いちばん近いマスへ進む方向を `NextDir` に
入れます。試すときの約束も原典どおりで、
来た方向への逆走はしない、赤ゾーンでは
上向きを選ばない（目だけは例外）。中心から
外れている間は、前の `NextDir` のまま進みます。

家の中と出入りの方向は、この貪欲な選択では
なく、決め打ちの誘導です。House では上下に
揺れるだけ、LeaveHouse では扉の前へ、
EnterHouse では自分の席へ、位置を見ながら
方向を上書きし、「必ず動く」ことを示す
`true` を返します。

## 7.5 Go の道具 ― switch による状態分岐

この章のコードは、`switch` がよく働いています。
Go の `switch` には2つの形があります。

1つ目は、値で分ける形です。`updateGhostTarget`
の `switch ghost.Typ` がそうで、C の `switch`
と似ていますが、Go では各 `case` の終わりに
`break` が要りません。通過（fallthrough）は
既定では起きず、必要なら `fallthrough` と
明示的に書きます。

2つ目は、条件で分ける形です。タグを書かずに
`switch { case 条件: ... }` とすると、
上から順に条件を試す `if`／`else if` の列と
同じ意味になります。第8章で読む全体カウンタの
判定（ghost.go 74行〜）がこの形です。

```go
			switch {
			case ghost.Typ == GhostPinky && g.Play.GlobalDotCounter == 7:
				newState = GhostStateLeaveHouse
			case ghost.Typ == GhostInky && g.Play.GlobalDotCounter == 17:
				newState = GhostStateLeaveHouse
			case ghost.Typ == GhostClyde && g.Play.GlobalDotCounter == 32:
				newState = GhostStateLeaveHouse
```

「状態 × 条件」の表を、そのまま文章として
書けるのがこの形の利点です。状態機械の
コードでは、分岐の表が読み物として残るかどうかが
効いてきます。

---

## 解剖メモ（第7章）

- ゴーストの状態は8値（実質7つ）。状態の判定と
  目標の計算は、毎ティックやり直される。
- 追跡の目標は4匹で全部違う。Blinky は本人、
  Pinky は4マス先、Inky は2マス先と Blinky の
  中点の反転、Clyde は距離8タイルで切替。
- 青の目標は毎ティック引き直され、乱数は
  ティックごとに2回消費される。原典の構造
  そのままで、コメントの「交差点ごと」は
  実態とずれている。
- 方向の決定はマスの中心でのみ。目標の変化と
  方向の変化は、別の頻度で起きる。
- 目の目標は (13, 14) 固定。

## 手を動かす（読解演習）

1. `updateGhostState`（ghost.go 57行〜）を
   読み、状態の移行を全部拾って、移行図
   （どの状態からどの状態へ、何がきっかけか）を
   描いてください。
2. Inky の目標計算を、具体的な数字で
   追ってください。パックマンが (10, 10) を
   右向きに進み、Blinky が (6, 12) にいるとき、
   目標はどこになりますか。
3. 青の間に乱数が毎ティック消費されることは、
   検証の決定性（同じ入力で同じ結果）に
   影響しますか。`xorshift32` の種がどこで
   決まるか（第6章の `gameRoundInit`）と
   あわせて考えてください。

## 確認問題

**問1**：Pinky の追跡目標は、パックマンの
どこですか。

<details>
<summary>答え</summary>

パックマンの向いている方向の4マス先です。
原作の上向きの斜めずれの癖は、原典が未再現の
ため、ここにもありません。
</details>

**問2**：青いゴーストの目標は、どの頻度で
決め直されますか。

<details>
<summary>答え</summary>

毎ティックです。`updateGhostTarget` が
ティックごとに呼ばれ、そのたびに乱数を
2回消費して盤面内のランダムなマスを
目標にします。
</details>

**問3**：ゴーストが進む方向を決め直すのは、
どんな場所ですか。

<details>
<summary>答え</summary>

マスの中心に着いたときだけです
（`distToTileMid` が両方向とも0のとき）。
それ以外の場所では、前に決めた `NextDir` の
まま進みます。
</details>

---

### 次回予告

**第8章 家と速さ**
― 家を出る順番を決める2種類のカウンタと、
「何ティックに何回進むか」で作る速さの
パターンを読みます。

---

# 第8章 家と速さ

## 前章までのあらすじ

第7章で、ゴーストの状態機械と目標タイルの
計算を読みました。この章では、家を出る順番を
決める2種類のカウンタと、「何ティックに
何回進むか」で速さを作るパターンを読みます。
中心は引き続き `ghost.go` で、設定の側は
`rules.go` の `gameRoundInit` と `state.go` の
表です。対応する C は pacman.c 1750〜1831行
あたりです。

## 8.1 個人カウンタ ― ドットで数える

ラウンドの開始時、家の中のゴーストには
「あと何ドット食べれば出られるか」の上限が
設定されます（rules.go 165〜189行）。

- Blinky: 0（最初から家の外）
- Pinky: 0（すぐ出る）
- Inky: 30
- Clyde: 60

数えるのは `updateGhosthouseDotCounters`
（ghost.go 247〜258行）です。パックマンが
ドットを食べるたびに呼ばれます
（rules.go 246行。パワーエサでは呼ばれません）。

```go
func (g *Game) updateGhosthouseDotCounters() {
	if g.Play.GlobalDotCounterActive {
		g.Play.GlobalDotCounter++
	} else {
		for i := range g.Play.Ghost {
			if g.Play.Ghost[i].DotCounter < g.Play.Ghost[i].DotLimit {
				g.Play.Ghost[i].DotCounter++
				break
			}
		}
	}
}
```

読みどころは2つあります。

1つ目は、`break` です。1ドットで増えるのは
1匹だけ。配列の順（Blinky、Pinky、Inky、
Clyde）に走査して、上限に達していない
最初の1匹を増やして終わります。上限0の
2匹は最初から「達している」ので、数えは
実質 Inky から始まります。Inky が30に
達したら、次は Clyde が数え始めます。
Clyde の上限は60ですが、Inky の30の
あとに数えるので、**Clyde が出るのは
通算90ドット目**です。「上限60なのに
90で出る」のは、この積み重ねの結果です。

2つ目は、この走査が **家の中にいるかどうかを
見ていない**ことです。見ているのは
カウンタと上限だけ。家の外に出たゴーストの
カウンタは上限に達したまま動かないので、
結果として家の中の順番待ちに効きますが、
判定そのものは「家にいるか」ではなく
「まだ数え終わっていないか」です。

上限に達したゴーストは、`updateGhostState` の
House の分岐で LeaveHouse に移ります
（ghost.go 84〜86行）。

## 8.2 全体カウンタ ― 死亡後の切り替え

パックマンが死ぬと、カウンタの方式が
切り替わります。切り替えは `gameRoundInit` の
「勝っていないとき」の分岐にあります
（rules.go 138〜142行）。残機の数が初期値と
違う ―― つまり一度死んでいる ―― ときだけ、
全体カウンタが有効になります。

全体カウンタは、個人の上限を持ちません。
ドットを食べるたびに1つの数が増えていき
（8.1 の関数の前半）、その数が節目に達した
ゴーストから順に出ます（ghost.go 74〜84行）。

- Pinky: 7
- Inky: 17
- Clyde: 32

Clyde が32で出ると、全体カウンタは無効に
戻ります（ghost.go 82行）。面クリアのときも、
`gameRoundInit` の勝ちの分岐で無効に戻ります
（rules.go 136行）。「死亡後の間だけ使う
予備の物差し」という位置づけです。

## 8.3 強制退出 ― 240ティックの物差し

ドットを食べない時間が続くと、カウンタが
進まず、家から出られなくなります。その保険が
`ForceLeaveHouse` トリガーです。

仕組みは「最後にドットを食べた時刻」を
覚えることです。ラウンド開始時にセットされ
（rules.go 154行）、ドットを食べるたびに
セットし直されます（rules.go 244行）。
House の分岐では、その時刻からちょうど
240ティック（4×60）経った瞬間を調べます
（ghost.go 70〜72行）。

```go
		if g.Play.ForceLeaveHouse.AfterOnce(now, 4*60) {
			newState = GhostStateLeaveHouse
			g.Play.ForceLeaveHouse.Start(now)
		}
```

発火したら、そのゴーストは上限に関係なく
出ます。そしてトリガーを張り直すので、
次の1匹にもまた240ティックの猶予が
付きます。「ドットを食べない状態が
240ティック続くと、次の1匹が強制的に
出る」という SPEC の規則は、この3行に
なっています。

## 8.4 速さのパターン

速さは、ピクセル/秒のような実数では
表されていません。「何ティックに何回、
1ピクセル進むか」のパターンで作ります。

パックマンは `pacmanShouldMove`
（rules.go 195〜206行）です。

```go
func (g *Game) pacmanShouldMove() bool {
	now := g.Timing.Tick
	switch {
	case g.Play.DotEaten.Now(now):
		return false // eating a dot stops Pacman for 1 tick
	case g.Play.PillEaten.Since(now) < 3:
		return false // eating a pill stops Pacman for 3 ticks
	default:
		return (g.Timing.Tick % 8) != 0
	}
}
```

素の速さは「8ティックに7回進む」で、
**7/8 = 0.875 ピクセル/ティック**。ドットを
食べたティックは1回休み、パワーエサでは
3ティック休むので、食べながらの実効速度は
それだけ落ちます。「食事中は遅い」は、
別の速さの値ではなく、休みの挿入で
作られています。

ゴーストは `ghostSpeed`（ghost.go 7〜32行）が
「このティックに何ピクセル進むか」を返し、
呼び出し側がその回数だけ移動を繰り返します
（第7章で見た rules.go 307〜313行のループ）。

```go
	switch ghost.State {
	case GhostStateHouse, GhostStateLeaveHouse, GhostStateFrightened:
		// inside house / frightened: half speed
		return int(tick & 1)
	case GhostStateEyes, GhostStateEnterHouse:
		// estimated 1.5x in eye state
		if tick&1 != 0 {
			return 1
		}
		return 2
	default:
		if isTunnel(pixelToTilePos(ghost.Actor.Pos)) {
			if (tick*2)%4 != 0 {
				return 1
			}
			return 0
		}
		if tick%7 != 0 {
			return 1
		}
		return 0
	}
```

パターンをほぐすと、こうなります。

- 通常: 「7ティックに6回」で **6/7 ≒ 0.857**
  ピクセル/ティック
- 家の中、出入り、青: ティックの偶奇で
  0か1。半分の速さ
- 目と帰り: 1と2の交互で、**平均 1.5**
  ピクセル/ティック。通常（6/7）と比べると
  **約1.75倍**です。「1.5倍速」ではなく、
  「平均1.5ピクセル/ティック」が正確な
  言い方になります
- トンネルの中: 通常パターンの半分の頻度で
  進む（半分の速さ）

速さはラウンドで変わりません。ラウンドで
変わるのはフルーツと青時間だけです。青時間は
レベルの表にあり、ラウンド1では **360ティック**
（6×60）です（state.go 455〜456行。表の
1行目 `{FruitCherries, 10, 6 * 60}` の
3つ目の値）。

散らばり／追跡の時刻表も、ここで一緒に
置いておきます。`scatterChasePhase`
（ghost.go 34〜54行）は、`RoundStarted`
からの経過ティックで局面を返します。
境目は 7、27、34、54、59、79、84（×60）
で、区間に直すと 散らばり7秒、追跡20秒、
散らばり7秒、追跡20秒、散らばり5秒、
追跡20秒、散らばり5秒、その後は追跡の
ままです。第6章で見た「最初の切替は
+420」は、この最初の境目 7×60 のことです。
青の間もこの時計は止まりません。

## 8.5 Go の道具 ― テーブル駆動のデータ表現

この章の数値は、どれも「表」として
置かれています。代表はレベルの表です
（state.go 455行〜）。

```go
var levelSpecTable = [maxLevelSpec]LevelSpec{
	{FruitCherries, 10, 6 * 60},
	{FruitStrawberry, 30, 5 * 60},
```

1行が構造体 `LevelSpec`（フルーツ、得点、
青時間）で、表全体は構造体の **配列**です。
`[maxLevelSpec]LevelSpec{...}` という書き方は、
「要素数21の配列を、この値で初期化する」という
複合リテラルです。行の値が `{FruitCherries, 10, 6 * 60}`
のように波括弧だけで書けるのは、要素の型が
文脈から分かるためで、Go ではこの省略が
普通の書き方になっています。

取り出し側の `levelSpec`（state.go 481行〜）は、
範囲外のラウンドを最後の行に寄せる
（クランプする）小さな関数です。表そのものは
ただのデータで、規則は取り出し側に1か所だけ
ある、という分担です。

時刻表も同じ発想です。区間の長さ
（7、20、7、20、5、20、5）を並べる代わりに、
境目の累積（7、27、34、…）を `switch` の
条件として並べています。データの置き方には
いつも「並べる形」と「使う形」の間の
選択があり、この移植では使う形に寄せて
あります。第12章で読む表駆動テストも、
同じ「表で持って、コードは表をなぞる」
発想の延長です。

---

## 解剖メモ（第8章）

- 個人カウンタは、ドットごとに「上限未満の
  最初の1匹」だけが増える。家の中かどうかは
  見ていない。Clyde は Inky の30のあとに
  60を数えるので、通算90ドット目に出る。
- 全体カウンタは死亡後のみ有効。節目は
  Pinky 7、Inky 17、Clyde 32 で、Clyde の
  家出で無効に戻る。
- 強制退出は「最後にドットを食べてから
  240ティック」。発火のたびにトリガーが
  張り直される。
- 速さはパターンで作る。パックマン 7/8、
  ゴースト通常 6/7、目は平均 1.5
  ピクセル/ティック（通常の約1.75倍）、
  トンネルと青と家は半分。
- 青時間はラウンド1で 360ティック。
  散らばり／追跡の時計は青の間も進む。

## 手を動かす（読解演習）

1. ラウンド開始直後から、Inky が家を出る
   までに必要なドットの数を、個人カウンタの
   走査を手で追って確かめてください。続けて
   Clyde が出るまでの通算も求めてください。
2. パックマンが死んだ直後のラウンドで、
   Pinky、Inky、Clyde がそれぞれ何ドット目に
   出るか、全体カウンタのコードから
   読み取ってください。
3. `ghostSpeed` の戻り値を、ティック
   0〜13 について状態ごとに表にしてください。
   通常と目について、14ティックで何ピクセル
   進むかも計算してください。

## 確認問題

**問1**：Clyde の個人カウンタの上限は60なのに、
通算90ドット目に出るのはなぜですか。

<details>
<summary>答え</summary>

カウンタは「上限に達していない最初の1匹」
だけが増える仕組みだからです。Inky が先に
30ドット分を数え終えてから、Clyde の
60の数えが始まるので、通算は 30 + 60 = 90
になります。
</details>

**問2**：全体カウンタが有効になるのは、
どんなときですか。

<details>
<summary>答え</summary>

パックマンが一度死んだあとのラウンドです。
`gameRoundInit` で、残機の数が初期値と
違うときに有効化されます。Clyde が
32で家を出るか、面クリアで無効に戻ります。
</details>

**問3**：目の速さは、通常のゴーストの
何倍ですか。

<details>
<summary>答え</summary>

約1.75倍です。目は1と2の交互で平均
1.5ピクセル/ティック、通常は 6/7 ≒ 0.857
ピクセル/ティックなので、比は
1.5 ÷ (6/7) = 1.75 になります。
</details>

---

### 次回予告

**第9章 描画**
― ルール側を離れて、描く側に移ります。
タイル絵を画像として先に作る方式（H6）と、
盤面の差分更新を読みます。

---

# 第9章 描画

## 前章までのあらすじ

第8章で、家の中のドットカウンタと、ゴーストの
速さを見ました。ここまでの章で読んできたのは、
すべて「状態」の側です。盤面は、タイル番号の表
（VideoRAM）と色コードの表（ColorRAM）として
`Game` の中にあり、キャラクターはスプライトの
状態として置かれていました。

この章では、その表が実際の画面になるまでを
読みます。題材は `render.go`（651行）です。
対応する C は、pacman.c 993〜1229行（vid と spr）、
1584〜1732行（タイルとスプライトの更新）、
2404〜3124行（gfx）です。仕様書の決定は、
H5（letterbox とシェーダーを持ち運ばない）と
H6（描画の作り方）です。

## 9.1 状態層は C と同形 ― 表への書き込み

render.go の前半は、状態層です。やっている
ことは C と同じで、VideoRAM と ColorRAM への
書き込みだけです。たとえば `vidClear`
（render.go 14〜21行）。

```go
func (g *Game) vidClear(tileCode, colorCode uint8) {
	for y := 0; y < DisplayTilesY; y++ {
		for x := 0; x < DisplayTilesX; x++ {
			g.Gfx.VideoRAM[y][x] = tileCode
			g.Gfx.ColorRAM[y][x] = colorCode
		}
	}
}
```

`vidTile`、`vidColor`、`vidColorText`、
`vidColorScore` と、名前も役割も C の `vid_*`
の写しです。違いは2つだけあります。1つは、
範囲外の座標が来たら `panic` すること
（`vidTile`、render.go 43〜48行。C の assert の
置き換えです）。もう1つは、書き込み先が
大域変数ではなく `g.Gfx` の中にあること
（第2章で見た `Game` 型の形です）。

毎ティックの更新も状態層の仕事です。
`gameUpdateTiles`（render.go 261〜314行）が
スコア、残機、パワーエサの点滅を表に書き、
`gameUpdateSprites`（render.go 315〜383行）が
スプライトの絵柄と位置と色を決めます。

小さな癖の再現もここにあります。青い
ゴーストが終わり近くで点滅する判定では、
C が「負になりうる差を uint32 にキャスト
する」書き方をしていて、Go でもコメント
つきでそのまま写してあります
（render.go 232行）。

```go
	fright := uint32(int32(levelSpec(int(g.Play.Round)).FrightTicks) - 60)
```

## 9.2 描画層 ― Renderer という別の型

表を画面にする側は、`Game` のメソッドでは
なく、`Renderer` という別の型の仕事です
（render.go 401〜415行）。

```go
// Renderer owns the Ebitengine-side drawing resources.
type Renderer struct {
	g *Game

	tilePixels [tileTextureHeight][tileTextureWidth]uint8

	tileImgs   [256][32]*ebiten.Image
	spriteImgs [64][32]*ebiten.Image

	board      *ebiten.Image
	boardValid bool
	lastVideo  [DisplayTilesY][DisplayTilesX]uint8
	lastColor  [DisplayTilesY][DisplayTilesX]uint8

	white *ebiten.Image
}
```

Renderer が持つのは、Ebitengine の画像
（`*ebiten.Image`）と、前回の表の控えです。
逆に、状態層の関数（`vid*`、`spr*`、
`gameUpdate*`）は、ebiten の型に一切
触れません。render.go という1つのファイルの
中に、2つの層が同居しています。

境界がこう切れているのは、H9 のためです。
「ロジックは Ebitengine に依存しない形に
保つ」ので、テストは状態層だけを相手に
できます（第12章）。main.go の `app` の
コメントにも、同じ意図が書かれています
（main.go 16〜18行）。

```go
// app is the ebiten game object. The game logic lives in Game; the
// renderer, input reader and synth are attached here so the logic
// files never import ebiten.
```

## 9.3 事前画像化 ― パレットを焼き込む

C は、タイル番号と色コードを GPU に渡し、
シェーダーの中で「タイルの画素 → パレットの
色」という2段のデコードをしていました。
Ebitengine にはパレットの仕組みがないので、
同じ手は使えません。

H6 の決定は、「タイル絵 × 色」の組み合わせを、
起動時に全部画像として作ってしまうことです。
手順は3段あります。

まず、ROM のビットプレーンを画素値の並びに
デコードします（`gfxDecodeTiles`、
render.go 455〜463行）。並べ方は C の
テクスチャと同じで、タイル256枚が上の段、
スプライト64枚が下の段です（render.go
395〜398行の定数が、その寸法です）。

次に、ハードウェアパレットを色にデコード
します（`gfxDecodeColorPalette`、
render.go 467〜483行）。各4色の組の先頭
（インデックスが4の倍数）はアルファを
落として透明にする、という C の決まりも
そのままです。

最後に、組み合わせを焼きます
（`bakeAtlases`、render.go 496〜538行）。
タイルは 256種 × 32色で 8,192枚、スプライトは
64種 × 32色で 2,048枚の小さな画像ができます。
色コードが32色（5ビット）なのは C と同じで、
使う側は `& 0x1F` で切り取ります。

起動時に一度だけ計算を払って、毎フレームの
デコードをなくす。これが、この設計の芯です。
準備は `newRenderer`（render.go 542〜557行）が
まとめて行います。

## 9.4 盤面は差分更新

盤面全体（224×288）は、1枚のオフスクリーン
画像として持ちます。毎フレーム全部を
描き直すのではなく、変わったマスだけを
描き直すのが `updateBoard`
（render.go 578〜599行）です。

```go
// updateBoard redraws the changed tiles into the board offscreen.
func (r *Renderer) updateBoard() {
	g := r.g
	if !r.boardValid {
		r.board.Fill(color.Black)
	}
	for y := 0; y < DisplayTilesY; y++ {
		for x := 0; x < DisplayTilesX; x++ {
			tile := g.Gfx.VideoRAM[y][x]
			col := g.Gfx.ColorRAM[y][x] & 0x1F
			if r.boardValid && tile == r.lastVideo[y][x] && col == (r.lastColor[y][x]&0x1F) {
				continue
			}
			op := &ebiten.DrawImageOptions{Filter: ebiten.FilterNearest}
			op.GeoM.Translate(float64(x*TileWidth), float64(y*TileHeight))
			r.board.DrawImage(r.tileImgs[tile][col], op)
			r.lastVideo[y][x] = tile
			r.lastColor[y][x] = g.Gfx.ColorRAM[y][x]
		}
	}
	r.boardValid = true
}
```

前回の表（`lastVideo`、`lastColor`）と比べて、
タイル番号も色も同じマスは飛ばします。
初回だけは `boardValid` が偽なので、黒で
塗ってから全マスを描きます。

この仕組みのおかげで、面クリア時の迷路の
点滅（青と白の入れ替え）に、描画層の特別な
処理が要りません。点滅は、状態層の側で
ColorRAM を書き換える出来事だからです
（render.go 306〜313行）。

```go
	// if the round was won, blink the whole playfield blue/white
	if g.Play.RoundWon.After(now, 1*60) {
		if (g.Play.RoundWon.Since(now) & 0x10) != 0 {
			g.vidColorPlayfield(ColorDot)
		} else {
			g.vidColorPlayfield(ColorWhiteBorder)
		}
	}
```

色が変わったマスは、差分更新が拾って盤面に
描き直します。H6 の「盤面フラッシュのような
色の反転は、盤面のオフスクリーンを表から
描き直すことで受ける」は、このことです。

## 9.5 1フレームの描画順

`Draw`（render.go 601〜651行）が、1フレームの
描画です。順番は4つあります。

1. フェードの値を進める（`gfxFade`、
   render.go 559〜576行。状態の計算なので、
   こちらは `Game` のメソッドです）
2. 盤面の差分更新をして、画面に貼る
3. スプライトを、状態層が決めた絵柄・位置・
   反転で描く。反転は、描画行列の負の倍率で
   表します（render.go 619〜626行）

```go
		if spr.FlipX {
			sx = -1
			tx += SpriteWidth
		}
		if spr.FlipY {
			sy = -1
			ty += SpriteHeight
		}
```

4. フェード。1×1の白い画像（`white`）を
   画面全体に引き伸ばし、色倍率で RGB を
   0 にして黒に変え、不透明度にフェード値を
   使って重ねます（render.go 644〜650行）

```go
	// fade: a black overlay whose opacity is the fade value
	if g.Gfx.Fade > 0 {
		fop := &ebiten.DrawImageOptions{Filter: ebiten.FilterNearest}
		fop.GeoM.Scale(DisplayPixelsX, DisplayPixelsY)
		fop.ColorScale.Scale(0, 0, 0, float32(g.Gfx.Fade)/255)
		screen.DrawImage(r.white, fop)
	}
```

C のシェーダーがやっていた暗転を、画像の
重ね描きで受けた形です。デバッグマーカーの
描画も Draw の中にありますが、ゲーム自身は
有効にしない部品です。

## 9.6 窓と拡縮 ― Layout の仕事

画面の拡縮と配置は、Ebitengine の `Layout` に
任せます（main.go 53〜55行）。

```go
func (a *app) Layout(outsideWidth, outsideHeight int) (int, int) {
	return DisplayPixelsX, DisplayPixelsY
}
```

論理サイズは常に 224×288 で、窓の大きさに
合わせた引き伸ばしはエンジン側が行います。
既定の窓は、その2倍の 448×576 です
（main.go 90〜91行）。

```go
	ebiten.SetTPS(60)
	ebiten.SetWindowSize(DisplayPixelsX*2, DisplayPixelsY*2)
```

拡大でドットがにじまないよう、描画のたびに
`FilterNearest` を指定します（`updateBoard` と
`Draw` の各所）。C にあった letterbox
（中央寄せの計算）と GLSL シェーダーは、
この仕組みに吸収されて消えました。
H5 の種別で言えば「消滅」です。

## Go の道具 ― 依存を型の中に閉じる

この章の道具は、ライブラリへの依存を
1つの型の中に閉じ込める、という切り方です。

Renderer の中には `*ebiten.Image` が並びますが、
外から見えるのは `newRenderer` と `Draw`
だけです。`Game` も、rules.go や ghost.go の
ロジックも、ebiten の型を名前で呼ぶことは
ありません。ebiten を知っているのは、
render.go の描画層と、main.go と input.go
だけです。

この切り方が効く場面は2つあります。1つは
テストで、画面なしにロジックだけを回せます
（第12章）。もう1つは土台の交換で、描き方を
変えたくなっても、触るのは Renderer の中
だけです。

「どの型が、どのライブラリを知っているか」を
決めることが、Go では設計の中心になります。
第10章の `Synth`、第11章の `InputReader` も、
同じ切り方でできています。

---

## 解剖メモ（第9章）

- 状態層（vid / spr / 更新）は C と同形で、
  表への書き込みだけをする。ebiten の型には
  触れない。
- 描画層は Renderer 型に閉じている。H9 の
  「ロジックは Ebitengine に依存しない」は、
  この境界で守られている。
- パレットの2段デコードは、起動時の事前
  画像化（タイル 8,192枚、スプライト
  2,048枚）に置き換わった（H6）。
- 盤面は差分更新。迷路の点滅も「色が
  変わった」という差分として、自然に
  処理される。
- フェードはシェーダーではなく、黒い
  オーバーレイの重ね描き。letterbox と
  シェーダーは Layout に吸収されて
  消滅した（H5）。

## 手を動かす（読解演習）

1. render.go の関数を、状態層と描画層に
   分けてください。`Game` のメソッドと
   `Renderer` のメソッドで、きれいに
   分かれますか。
2. `bakeAtlases` が作る画像の総数を、
   ループの範囲から数えてください。また、
   色コードを `& 0x1F` で切っている箇所が、
   `Draw` と `updateBoard` のどこにあるか
   探してください。
3. 面クリア時の点滅で、`updateBoard` が
   1回の Draw で描き直すマスは、最大で
   いくつですか。`vidColorPlayfield` の
   範囲（render.go 23〜29行）から見積もって
   ください。

## 確認問題

**問1**：事前画像化で作られる画像は、
タイルとスプライトで、それぞれ何枚ですか。

<details>
<summary>答え</summary>

タイルは 256種 × 32色で 8,192枚、
スプライトは 64種 × 32色で 2,048枚です。
`bakeAtlases`（render.go 496〜538行）が、
起動時に全部を作ります。
</details>

**問2**：迷路の点滅（面クリア時）に、
描画層の特別な処理が要らないのは
なぜですか。

<details>
<summary>答え</summary>

点滅は、状態層が ColorRAM を書き換える
ことで起きるからです。`updateBoard` の
差分更新が、色の変わったマスを拾って
盤面に描き直すので、点滅も通常の差分と
同じ扱いになります。
</details>

**問3**：`Layout` が返す論理サイズと、
既定の窓サイズはいくつですか。

<details>
<summary>答え</summary>

論理サイズは 224×288
（`DisplayPixelsX` × `DisplayPixelsY`）で、
既定の窓はその2倍の 448×576 です。
拡縮と配置は Ebitengine 側が行います。
</details>

---

### 次回予告

**第10章 音** ― 音の出口は、C の push 型から
Ebitengine の pull 型（`io.Reader`）に
替わります。1ティック = 735 サンプルという
割り切れる数と、音のない機械でもゲームが
止まらないための工夫を読みます。

---

# 第10章 音

## 前章までのあらすじ

第9章で、描画の出口を読みました。状態層は
C と同形で、出口の型（`Renderer`）だけが
Ebitengine に合わせてありました。

音も同じ構図です。音の状態を進める側
（`snd` で始まる関数群）は C と同形で、
出口だけが違います。題材は `audio.go`
（303行）です。対応する C は、pacman.c
638〜678行（効果音の記述）と 3125〜3388行
（音のロジック）です。仕様書の決定は
H3（音の出口）です。

## 10.1 状態層は C と同形

効果音の記述は、パッケージ変数として
並んでいます（audio.go 193〜208行）。
ダンプ再生の2つ（プレリュードと死亡音）は
`Data` にレジスタの列を持ち、手続き型の
6つは `Fn` に関数を持ちます。スロットの
配分（0 = プレリュード専用、1 = 青の音と
通常時の音、2 = それ以外全部）も、C の
ままです。

開始と停止と、60Hz の進行は `Game` の
メソッドです。`sndTick`（audio.go 64〜95行）は
`Game.Tick` から毎ティック呼ばれて、
ダンプの再生位置を進めたり、手続き型の
関数を呼んだりして、声のレジスタ
（周波数・波形・音量）を書き換えます。
レジスタを書くのはこの側だけで、出口の側は
書きません。

## 10.2 出口の置き換え ― push から pull へ

C は sokol-audio への push 型でした。
フレームのコールバックの中でサンプルを作り、
音の受け口に押し込んでいく形です。

Ebitengine の音は pull 型です。プレイヤーが
「次のサンプルをください」と読みに来るので、
こちらは読み手（`io.Reader`）を渡しておく
形になります。audio.go の末尾のコメントが、
この置き換えをそのまま述べています
（audio.go 210〜217行）。

```go
// --- the pull-type sample output (SPEC H3) ---
//
// The C version pushes samples from the frame callback; Ebitengine
// pulls them through an io.Reader on the audio thread. The register
// state is advanced by Game.Tick (sndTick, 60 Hz) on the game thread
// and read here as it stands -- the same lock-free relationship the
// original has with the sound hardware. One tick is exactly 735
// samples at 44,100 Hz.
```

読み手の型は `Synth` です
（audio.go 226〜234行）。

```go
// Synth converts the Namco voice state into a sample stream.
type Synth struct {
	g *Game

	voiceTickAccum  int32 // in thousandths of a 96 kHz tick
	voiceTickPeriod int32 // 96,000,000 / SampleRate = 2176

	buf []byte // one tick of generated samples
	pos int
}
```

持っているのは、ゲームへの参照と、後で
出てくる蓄積の変数と、1ティックぶんの
バッファだけです。

## 10.3 形式 ― 44,100Hz、735 サンプル

受け口の形式は、H3 で決めたとおり、
44,100Hz、16ビット、2チャンネルです
（audio.go 219〜223行）。

```go
const (
	SampleRate     = 44100
	SamplesPerTick = SampleRate / 60 // 735
	bytesPerSample = 4               // 16-bit stereo
)
```

原典の合成はモノラルなので、ステレオの
左右には同じ値を複製します。`generate`
（audio.go 274〜290行）が、1ティックぶん
（735サンプル）を内部バッファに作る関数で、
同じ値を左と右の両方に書いています。

```go
// generate fills the internal buffer with one tick of samples.
func (s *Synth) generate() {
	for i := 0; i < SamplesPerTick; i++ {
		s.voiceTickAccum -= s.voiceTickPeriod
		for s.voiceTickAccum < 0 {
			s.voiceTickAccum += 1000
			s.voiceTick()
		}
		v := int16(s.sampleTick() * 32767)
		o := i * bytesPerSample
		s.buf[o+0] = byte(v)
		s.buf[o+1] = byte(v >> 8)
		s.buf[o+2] = byte(v)
		s.buf[o+3] = byte(v >> 8)
	}
	s.pos = 0
}
```

44,100 ÷ 60 = 735 と割り切れるのが、
この設計の気持ちよさです。ティックと
サンプルの境目がずれていかないので、
バッファは「1ティックぶん」で固定できます。
`NewSynth`（audio.go 237〜245行）は、
`pos` をバッファの末尾に置いて「空」の
状態から始めるので、最初の読み取りで
最初のティックが生成されます。

## 10.4 96kHz の声を、44.1kHz から割る

原典の音源は、96kHz で声を進める作りです。
出力1サンプルごとに、96kHz のティックは
96,000 ÷ 44,100 ≒ 2.176 回進むはずですが、
割り切れません。

Synth は、この端数を千分率の蓄積で処理
します。`voiceTickPeriod` は
96,000,000 ÷ 44,100 = 2176、つまり
「96kHz ティック 2.176 回」を千倍した数です。
サンプルごとに蓄積から 2176 を引いて、
負になったら 1000 を足して声を1回進めます
（`generate` の内側のループ）。平均すれば、
ちょうど 2.176 回 / サンプルになります。

声を1回進める `voiceTick`
（audio.go 247〜258行）は、C の音源
そのものです。

```go
// voiceTick updates the Namco sound generator once (96 kHz).
func (s *Synth) voiceTick() {
	for i := 0; i < NumVoices; i++ {
		voice := &s.g.Audio.Voice[i]
		voice.Counter += voice.Frequency
		waveIndex := ((uint32(voice.Waveform) << 5) |
			((voice.Counter >> 15) & 0x1F)) & 0xFF
		sample := (int32(romWavetable[waveIndex]&0xF) - 8) * int32(voice.Volume)
		voice.SampleAcc += float32(sample)
		voice.SampleDiv += 128
	}
}
```

出力1サンプルの値は、`sampleTick`
（audio.go 260〜272行）が作ります。
蓄えた値を、声が進んだ回数で割って平均し、
3つの声を合計して、× 0.333333 ×
`AudioVolume`（0.5、state.go 9行）を掛けます。
16ビットへの変換は `generate` の中の
× 32767 です。こうして得られるピークは
約 0.156 で、原典の音量感をそのまま
写した値です。大きくも小さくもして
いません。

## 10.5 ロックなし ― ハードウェアとの関係のまま

状態を進めるのは、ゲームスレッドの
`sndTick` です。読むのは、音声スレッドの
Synth です。両者の間にロックはありません。
Synth は、レジスタの値を「その瞬間の姿」で
読みます。

これは手抜きではなく、原典とハードウェアの
関係の写しです。実機でも、CPU がレジスタを
書くそばから、音源チップが読んでいました。
60Hz の更新に対して読み取りは 44,100Hz と
圧倒的に細かいので、途中の姿が見えても、
音としては破綻しません。

## 10.6 音のない機械でも止まらない ― Phase 0 の知見

実装の Phase 0（土台のスパイク）で、
思わぬ落とし穴が見つかりました。音響装置の
ない環境では、プレイヤーを作る時点での
ドライバ初期化がエラーになり、そのエラーが
`RunGame` を即座に終わらせてしまうのです。
音が出ないだけではなく、ゲーム自体が
起動しません。

対策は2段です。まず `setupAudio`
（main.go 62〜76行）で、プレイヤー作成の
エラーを受け取ったら、無音で続行します。

```go
func setupAudio(a *app) {
	if os.Getenv("PACMAN_AUDIO") == "off" {
		return
	}
	a.synth = NewSynth(a.game)
	ctx := audio.NewContext(SampleRate)
	player, err := ctx.NewPlayer(a.synth)
	if err != nil {
		fmt.Fprintln(os.Stderr, "audio unavailable, continuing silently:", err)
		a.synth = nil
		return
	}
	a.player = player
	player.Play()
}
```

それでも RunGame が音響初期化のエラーで
戻る場合に備えて、main の末尾では、
プレイヤーがあった場合にだけ
「PACMAN_AUDIO=off を試して」という案内を
出すようにしてあります（main.go 94〜103行）。

そして、環境変数 `PACMAN_AUDIO=off` が
用意されています。この場合は Synth も
プレイヤーも作りません。音は「あれば鳴る」
部品であって、ゲームの起動を人質に取らない。
これが Phase 0 から得た、設計の決まりです。

## Go の道具 ― io.Reader と、エラーは値

この章の道具は2つです。

1つ目は `io.Reader`。`Read(p []byte) (int, error)`
という、たった1つのメソッドの
インターフェースです。Synth の `Read`
（audio.go 292〜303行）が、その実装です。

```go
// Read implements io.Reader for the Ebitengine audio player.
func (s *Synth) Read(p []byte) (int, error) {
	n := 0
	for n < len(p) {
		if s.pos >= len(s.buf) {
			s.generate()
		}
		m := copy(p[n:], s.buf[s.pos:])
		s.pos += m
		n += m
	}
	return n, nil
}
```

「Read メソッドを持つものは io.Reader で
ある」という暗黙の実装は、第1章の
`ebiten.Game` と同じ仕組みです。プレイヤーは
Synth の中身を知らず、Read だけを呼びます。
バッファが尽きたら次のティックを作る、
という詰め替えの都合は、全部 Synth の中に
閉じています。

2つ目は「エラーは値」です。Go には例外が
なく、失敗は戻り値の `error` として返り、
受ける側がその場で判断します。setupAudio の
`player, err := ctx.NewPlayer(a.synth)` と、
直後の `if err != nil` が、その型どおりの
姿です。「音が出なければ無音で続ける」と
いう判断が、エラーを受ける場所に、そのまま
書けています。

---

## 解剖メモ（第10章）

- 状態層（`snd*`）は C と同形。出口だけが
  push 型から pull 型（`io.Reader`）に
  替わった（H3）。
- 44,100 ÷ 60 = 735 で割り切れるため、
  バッファは1ティックぶんで固定できる。
- 96kHz の声は、周期 2176 の千分率の蓄積で
  44,100Hz に割り付けられる。
- 音声スレッドとの間はロックなし。原典と
  ハードウェアの関係の写し。
- 音は任意の部品。`PACMAN_AUDIO=off` で
  生成自体を飛ばし、プレイヤー作成の失敗は
  無音での続行に変える（Phase 0 の知見）。

## 手を動かす（読解演習）

1. `generate` が1回で作るバイト数を、
   `SamplesPerTick` と `bytesPerSample` から
   計算してください。また `Read` が、要求
   された長さに届くまで `generate` を
   繰り返すことを確認してください。
2. `voiceTickPeriod` が 2176 になる理由を、
   96,000,000 と 44,100 の関係から説明して
   ください。もし 2177 だったら、音は
   どうずれていきますか。
3. `sndTick`（audio.go 64〜95行）の中で、
   ダンプ再生が終わったときの処理
   （`CurTick` と `NumTicks` の比較）を
   見つけてください。出口の側（Synth）に、
   再生の終わりを知る仕組みはありますか。

## 確認問題

**問1**：1ティックは、なぜ 735 サンプル
なのですか。

<details>
<summary>答え</summary>

44,100Hz ÷ 60ティック/秒 = 735 で、
割り切れるからです。H3 の決定で、
ティックとサンプルの境目がずれません。
</details>

**問2**：ステレオの左右には、何が
入りますか。

<details>
<summary>答え</summary>

同じモノラル信号の複製です。原典の合成は
モノラルなので、`generate` が同じ値を
左右の両方に書きます。
</details>

**問3**：`PACMAN_AUDIO=off` は、何を
止めますか。

<details>
<summary>答え</summary>

Synth とプレイヤーの生成自体です。
音響装置のない環境で、ドライバ初期化の
エラーが `RunGame` を止めてしまうのを
避けるための指定です（Phase 0 の知見）。
</details>

---

### 次回予告

**第11章 入力** ― 最後の機器依存は入力です。
キーボード、ゲームパッド、タッチの3機器の
意図を、1つの `InputState` に合流させる
`InputReader` を読みます。

---

# 第11章 入力

## 前章までのあらすじ

第10章で、音の出口を読みました。描画の
`Renderer`、音の `Synth` ときて、この章は
最後の機器依存、入力です。

原典の入力はキーボードだけでした。Go 版では
H8 で「追加」が決まり、キーボード、
ゲームパッド、タッチの3機器に対応します。
題材は `input.go`（172行）です。ルール側が
見るのは、合流の結果である `InputState`
だけです（state.go 359〜367行）。

```go
type InputState struct {
	Enabled bool
	Up      bool
	Down    bool
	Left    bool
	Right   bool
	Esc     bool
	Anykey  bool
}
```

## 11.1 合流の形

input.go の冒頭のコメントが、設計の全体を
述べています（input.go 1〜16行）。

```go
// input.go -- merge keyboard, gamepad and touch into the game's
// InputState (SPEC H8). The rules only ever see the resolved input;
// which device produced it is known only here.
//
//   - keyboard: arrow keys and WASD, held state is the intent
//   - gamepad: first pad, standard layout D-pad and left stick
//     (deadzone 0.5, the larger axis wins)
//   - touch: swipe with a latch -- the direction persists until the
//     next swipe; a tap counts as "any key"
//   - no mouse, no vibration (decided 2026-11-20)
//
// Held directions are resolved with the original's priority
// (up, down, right, left); the latched touch direction is used only
// when nothing is held. The F key toggles fullscreen, as in the
// original. Like the original's event callback, nothing is written
// while input is disabled.
```

入り口は `InputReader.Read`
（input.go 42〜158行）で、毎ティック、
`app` の `Update` から呼ばれます。最初に
`Enabled` を見て、無効なら何も書きません。
原典のイベントコールバックが、入力無効の
間は状態を触らなかったことの写しです。

`InputReader` という型が持つのは、タッチの
ラッチと、追跡中のスワイプの情報だけです
（input.go 31〜39行）。

```go
type InputReader struct {
	latched  Dir
	hasLatch bool
	activeID ebiten.TouchID
	tracking bool
	swiped   bool
	originX  int
	originY  int
}
```

## 11.2 キーボード ― 保持が意図

方向は「押されているか」で読みます
（input.go 53〜56行）。

```go
	up := ebiten.IsKeyPressed(ebiten.KeyArrowUp) || ebiten.IsKeyPressed(ebiten.KeyW)
	down := ebiten.IsKeyPressed(ebiten.KeyArrowDown) || ebiten.IsKeyPressed(ebiten.KeyS)
	right := ebiten.IsKeyPressed(ebiten.KeyArrowRight) || ebiten.IsKeyPressed(ebiten.KeyD)
	left := ebiten.IsKeyPressed(ebiten.KeyArrowLeft) || ebiten.IsKeyPressed(ebiten.KeyA)
```

矢印と WASD の両方を受け、押されている間
ずっと意図として残ります。「押した瞬間」
ではなく「押されている状態」を読むのが
方向キーです。この後のゲームパッドも、
同じ4つの真偽（up、down、right、left）に
足し込む形で合流します。

## 11.3 ゲームパッド ― 先頭の1台、大きい軸

パッドは、見つかった先頭の1台だけを使い
ます（input.go 60〜64行）。標準レイアウトが
使える場合に限り、十字キーを方向に足し
込みます（input.go 65〜68行）。

```go
			up = up || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftTop)
			down = down || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftBottom)
			right = right || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftRight)
			left = left || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftLeft)
```

左スティックは、横と縦のうち絶対値の
大きい軸を採用し、0.5 を超えたらその
方向を立てます（input.go 69〜82行）。

```go
			x := ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickHorizontal)
			y := ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickVertical)
			if absF(x) > absF(y) {
				if x < -stickDeadzone {
					left = true
				} else if x > stickDeadzone {
					right = true
				}
			} else {
				if y < -stickDeadzone {
					up = true
				} else if y > stickDeadzone {
					down = true
				}
			}
```

斜めに倒したとき、意図した1方向だけが
立つようにする工夫です。デッドゾーン
0.5 は H8 の決定で、閾値の定数は
input.go 24〜27行にあります。

```go
const (
	touchSwipeThreshold = 24 // logical pixels, about 3 tiles
	stickDeadzone       = 0.5
)
```

パッドのボタンは、「何か押した」にも
使われます。どれか1つでも押された瞬間が
あれば `padAny` が立ちます
（input.go 83〜90行）。

## 11.4 タッチ ― スワイプとラッチ

タッチには「押されている方向」が
ありません。そこで、スワイプ（指を
滑らせる動き）で方向を決め、その方向を
次のスワイプまで保持します。この保持が
ラッチです。

指が触れたら追跡を始めます
（input.go 96〜106行）。原点から 24 論理
ピクセル（約3タイル）以上動いたら、
大きいほうの軸の向きをラッチに書きます
（input.go 113〜133行）。

```go
			x, y := ebiten.TouchPosition(r.activeID)
			dx, dy := x-r.originX, y-r.originY
			if max(abs(dx), abs(dy)) >= touchSwipeThreshold {
				if abs(dx) > abs(dy) {
					if dx > 0 {
						r.latched = DirRight
					} else {
						r.latched = DirLeft
					}
				} else {
					if dy > 0 {
						r.latched = DirDown
					} else {
						r.latched = DirUp
					}
				}
				r.hasLatch = true
				r.swiped = true
				// advance the origin so a long swipe keeps
				// producing directions
				r.originX, r.originY = x, y
			}
```

方向を書いたら、原点を今の位置に進めます。
この一行があるので、指を離さない長い
スワイプの途中でも、方向を変えられます。

スワイプにならなかったタッチ（閾値を
超えずに離したもの）は、タップとして
数えます（input.go 107〜112行）。

```go
		if inpututil.IsTouchJustReleased(r.activeID) {
			if !r.swiped {
				tap = true
			}
			r.tracking = false
		} else {
```

タップは「何か押した」として、イントロから
ゲームを始める合図になります。

## 11.5 解決 ― 保持が先、ラッチは後

3機器の結果は、最後に `InputState` へ
書かれます（input.go 138〜152行）。

```go
	// --- resolve: held first (original priority), then the latch ---
	if !(up || down || right || left) && r.hasLatch {
		switch r.latched {
		case DirUp:
			up = true
		case DirDown:
			down = true
		case DirRight:
			right = true
		case DirLeft:
			left = true
		}
	}
	in.Up, in.Down, in.Right, in.Left = up, down, right, left
	in.Esc = ebiten.IsKeyPressed(ebiten.KeyEscape)
```

順番が大事です。キーボードやパッドで何か
押されている間は、そちらが勝ちます。
ラッチは、何も押されていないときだけ
補います。タッチだけの環境では、ラッチが
ずっと効いて方向を保ちます。

`InputState` に入った4方向を1つに絞る
優先順位は、原典どおり上、下、右、左です。
これは使う側の約束で、`DirOr`
（timing.go 82〜97行）が持っています
（第3章で読みました）。input.go の仕事は、
真偽をそろえるところまでです。

「何か押した」（`Anykey`）は、押された
瞬間の縁で作ります。キーは
`AppendJustPressedKeys`、パッドはボタンの
縁、タッチはタップです
（input.go 154〜157行）。

```go
	// --- "any key": key edges, pad button edges, taps ---
	var keys []ebiten.Key
	keys = inpututil.AppendJustPressedKeys(keys)
	in.Anykey = len(keys) > 0 || padAny || tap
```

`app` の `Update` は、ティックの後で
`Anykey` を消します（main.go 39行）。
縁は1ティックだけ生きる、という約束です。

## 11.6 F キーと Esc、そして「ない」もの

F キーはフルスクリーンの切り替えで、
原典の操作の踏襲です（input.go 47〜50行）。

```go
	// fullscreen toggle (the original's F key handling)
	if inpututil.IsKeyJustPressed(ebiten.KeyF) {
		ebiten.SetFullscreen(!ebiten.IsFullscreen())
	}
```

Esc は、`InputState` に書かれるだけです
（input.go 152行）。終了の判断はどこにも
なく、押してもゲームは終わりません。
これも原典どおりで、終了はウィンドウを
閉じる操作に任されています。

マウスと振動は、コードのどこにも
現れません。H8 の決定（マウス操作なし、
振動なし）が、「書かれていない」という
形で守られています。

## Go の道具 ― 小さな道具の組み合わせ

この章の道具は、`inpututil` のような
小さな道具の組み合わせ方です。

使われている道具は、どれも小さいものです。
`IsKeyPressed`（状態）と `IsKeyJustPressed`
（縁）、`AppendJustPressedKeys`（縁のあった
キーをスライスに追記する）、
`AppendGamepadIDs`（接続中のパッドを
追記する）。方向は状態で読み、合図は縁で
読む、という使い分けが、道具の分かれ方と
そのまま一致しています。

「Append〜」という名前の関数は、Go の
標準の `append` と同じ流儀で、スライスを
受け取って、伸ばして返します。呼び出し側は
`ids = ebiten.AppendGamepadIDs(ids)` のように、
戻り値を受け直します。小さな道具をこの形に
そろえておくと、組み合わせる側のコードが
読み方を迷いません。

そして、機器ごとの知識は `InputReader` の
中に閉じ、外に出るのは `InputState` だけ
です。第9章の `Renderer`、第10章の `Synth` と
同じ構図で、「機器を知っている型」と
「機器を知らないルール」の境界が、ここでも
引かれています。ルール側は、方向がキーから
来たのか指から来たのかを、永遠に知りません。

---

## 解剖メモ（第11章）

- 3機器は、4つの真偽（up / down / right /
  left）に足し込む形で合流する。機器の
  区別は input.go の外に出ない。
- 方向は「保持」を読み、`Anykey` と F は
  「縁」を読む。状態と縁の使い分けが、
  inpututil の道具の分かれ方と一致している。
- タッチはスワイプ（閾値 24）で方向を決め、
  ラッチで保持する。タップは `Anykey`。
- 解決の順序は、保持（キーボードとパッド）が
  先で、ラッチは補い。1方向への優先順位
  （上 > 下 > 右 > 左）は、使う側の
  `DirOr` の約束。
- Esc は書かれるだけで、終了しない。
  マウスと振動は、決定どおり存在しない。

## 手を動かす（読解演習）

1. `Read` の中で、`up` が立つ経路を全部
   挙げてください（キーボード、十字キー、
   スティック、ラッチ）。それぞれ行番号で
   示してください。
2. 長いスワイプの途中で方向を変えられる
   のは、どの行の工夫ですか。また、
   スワイプの途中で指を止めた場合、
   ラッチはどうなりますか。
3. パッドが2台つながっている場合と、
   標準レイアウトが使えないパッドの
   場合に、`Read` が何をするか追って
   ください。

## 確認問題

**問1**：ラッチが効くのは、どんな
ときですか。

<details>
<summary>答え</summary>

キーボードやパッドで、何も押されて
いないときだけです。何か押されていれば、
そちらの保持が勝ちます
（input.go 138〜150行）。
</details>

**問2**：タップが `Anykey` になる
条件は何ですか。

<details>
<summary>答え</summary>

スワイプにならなかったタッチを離した
ときです。閾値（24 論理ピクセル）以上
動かないまま離されると、`swiped` が
偽のままなので、タップとして数えます
（input.go 107〜112行）。
</details>

**問3**：Esc を押すと、ゲームは
どうなりますか。

<details>
<summary>答え</summary>

何も起きません。`InputState.Esc` に
書かれるだけで、終了の処理はどこにも
ありません。原典どおりの扱いです。
</details>

---

### 次回予告

**第12章 テストと検証** ― 機器依存を全部
閉じ込めた結果、ロジックは画面なしで
回せるようになりました。表駆動テストと
ヘッドレス検証で、Nim 版と同じ 350/66 に
行き着くまでを読みます。

---

# 第12章 テストと検証

## 前章までのあらすじ

第11章で入力を見ました。キーボード、ゲーム
パッド、タッチの3機器が、解決済みの
`InputState` に合流する形でした。これで
本体のコードは全部読み終わりました。

最後の章では、検証の側を読みます。題材は
テストファイル8本、824行です。仕様書の
決定 H9 ――「ロジックは Ebitengine に依存
させず、ヘッドレスで検証できる形に保ち、
テストは表駆動で書く」― が、実際にどう
効いたかを見る章でもあります。

## 12.1 検証できる形にしておく

H9 の出発点は、ゲームのロジックが画面や
音響装置なしで回せることです。第2章で
見たとおり、状態は `Game` 型に集まり、
1ティックの進行は `Game.Tick()` を呼ぶ
だけです。描画（第9章）と音の出力（第10章）
は外側にあり、ロジックは Ebitengine の型を
知りません。

だからテストは、窓も音もなしに
`Game.Tick()` を直接回せます。
headless_test.go の冒頭コメントが、その
設計をそのまま述べています（5〜7行）。

```go
// Headless drivers: the same scenarios as the Nim port's
// tests/headless.nim, driving Game.Tick directly (no graphics, no
// audio output).
```

「Nim 版と同じシナリオ」という一文も
大事です。検証の物差し自体を、前の移植と
揃えてあるのです。物差しが同じなら、
結果の数字がそのまま比較になります
（12.4 で見る 350 と 66 がそれです）。

テストからゲームを始める定型も、小さな
道具として用意されています。たとえば
キー入力は、こう書けます（9〜13行）。

```go
func pressAnyKey(g *Game) {
	g.Input.Anykey = true
	g.Tick()
	g.Input.Anykey = false
}
```

入力は「解決済みの `InputState`」として
状態に書くだけなので（第11章）、実機の
キーボードがなくても「キーを押したこと」
にできます。`toGameplay`（67〜82行）は、
イントロを抜けてプレイ中まで進めた
`Game` を返す道具で、プローブ（12.5）の
各テストがこれを土台に使います。

## 12.2 テストの全体像

テストファイルは、本体と同じパッケージに
8本あります。

| ファイル | 行数 | 中身 |
|---|---|---|
| state_test.go | 39 | レベル仕様、Freeze のメソッド |
| timing_test.go | 71 | xorshift の列、Trigger の語彙、入力の優先順位 |
| geom_test.go | 37 | 負の位置の剰余、クランプ、Int2 の連鎖 |
| data_test.go | 45 | ROM データの個数と合計値 |
| headless_test.go | 210 | 自動プレイ、決定性、面クリア |
| probes_test.go | 270 | 挙動プローブ9本 |
| render_test.go | 59 | デコードとパレット（構造テスト） |
| audio_test.go | 93 | 音声合成（無音、信号、決定性） |

テスト関数は全部で25個です。本体2,725行に
対してテスト824行、およそ3割の分量を
検証に割いています。C の原典にも、Python 版
にも、Nim 版の題材にも、テストは付いて
いませんでした。Go 版でテストが本体と
並んで存在するのは、H9 の決定の結果です。

同じパッケージに置くことにも意味があり
ます。テストは `package main` の一員なので、
公開されていない内部の値（トリガーの
ティック数やカウンタ）にも直接触れます。
検証したいのは内部の数字なので、この
置き方が要ります。

基礎のテストは小さいものが揃っています。
たとえば xorshift は、種 0x12345678 から
始めた最初の5値が C の意味論と一致する
ことを確かめます（timing_test.go 5行〜）。
データの検証は第5章で見た「個数と合計値」
の形で、data_test.go にあります。その
書き方が、次の「Go の道具」の主題です。

## 12.3 Go の道具 ― 表駆動テストと _test.go の置き方

Go のテストは、標準ライブラリの `testing`
パッケージだけで書けます。約束は3つだけ
です。

- ファイル名を `〜_test.go` にする
- テスト関数は `Test` で始める名前で、
  引数は `t *testing.T` 1つ
- 失敗は `t.Error` / `t.Errorf`（記録して
  続行）か `t.Fatal` / `t.Fatalf`（その
  テストを中止）で伝える

実行は `go test` です。専用のテスト
フレームワークも、アサーションライブラリも
要りません。

その上で、Go のテストの書き方の中心に
あるのが**表駆動テスト**（table-driven
tests）です。「入力と期待値の組」を構造体の
スライスとして表に並べ、ループで1件ずつ
確かめる書き方です。data_test.go の
合計値の検証が、その典型です
（5〜23行）。

```go
func TestROMDataCountsAndSums(t *testing.T) {
	cases := []struct {
		name string
		sum  uint64
		want uint64
	}{
		{"romTiles", sumU8(romTiles[:]), 267889},
		{"romSprites", sumU8(romSprites[:]), 227290},
		{"romHWColors", sumU8(romHWColors[:]), 1852},
		{"romPalette", sumU8(romPalette[:]), 589},
		{"romWavetable", sumU8(romWavetable[:]), 1856},
		{"sndDumpPrelude", sumU32(sndDumpPrelude[:]), 1523003578600},
		{"sndDumpDead", sumU32(sndDumpDead[:]), 275197360640},
	}
	for _, c := range cases {
		if c.sum != c.want {
			t.Errorf("%s: sum = %d, want %d", c.name, c.sum, c.want)
		}
	}
```

読みどころは3つあります。1つ目、表の要素は
**無名の構造体**です。`[]struct{ ... }` と、
その場で型を書いて値を並べています。検証の
ためだけの型に名前を付ける必要がない、
という判断です。2つ目、失敗には `t.Errorf`
を使い、1件違っても残りの件を全部調べます。
データの照合では「どこまで合っていて、
どこから違うか」を一度に見たいからです。
3つ目、期待値の数字（267889 など）は、
C と Nim で得た合計値そのものです。
第5章で見た機械抽出の検証が、この表に
着地しています。

もう1例、入力の優先順位のテストです
（timing_test.go 55〜71行）。

```go
func TestInputDirPriority(t *testing.T) {
	cases := []struct {
		in   InputState
		want Dir
	}{
		{InputState{Up: true, Left: true}, DirUp},
		{InputState{Down: true, Right: true}, DirDown},
		{InputState{Right: true, Left: true}, DirRight},
		{InputState{Left: true}, DirLeft},
		{InputState{}, DirDown}, // default passed below
	}
	for i, c := range cases {
		if got := c.in.DirOr(DirDown); got != c.want {
			t.Errorf("case %d: got %v, want %v", i, got, c.want)
		}
	}
}
```

「上と左が同時に押されたら上が勝つ」という
第11章の約束が、表の1行になっています。
仕様の文を、そのままテストの行に写せる
のが表駆動の強みです。件を増やすときは、
表に行を足すだけです。

補助関数には `t.Helper()` という印も
あります。`toGameplay` の先頭（68行）で
呼ばれていて、「この関数の中で失敗したら、
呼び出し元の行を失敗箇所として報告して
ほしい」という意味です。共通の前準備が
失敗したときに、報告の場所がずれない
ための小さな気配りです。

## 12.4 自動プレイと、350 と 66

いちばん大きなテストは、60,000ティックの
自動プレイです（headless_test.go 84行〜）。
パックマンには自動運転が付いていて、
最寄りのドットへの経路を幅優先探索で探して
進みます（`steerDir`、29行〜）。テストの
骨格はこうです（84〜101行）。

```go
func TestHeadlessPlay(t *testing.T) {
	g := NewGame()
	for i := 0; i < 100; i++ {
		g.Tick()
	}
	if g.Scene != SceneIntro {
		t.Fatalf("scene = %v, want intro", g.Scene)
	}
	pressAnyKey(g)
	sawGame := false
	inkyLeftHouse := false
	maxGhostsOut := 0
	for i := 0; i < 60000; i++ {
```

100ティック回してイントロであることを
確かめ、キーを押して始め、60,000ティック
（実時間で約17分ぶん）回し続けます。その
間に、開始直後のドットが244個であること、
全4匹が家を出ること、死亡してゲーム
オーバーになり、イントロへ戻ることまでを
観測します。

結果は `t.Logf` で記録されます
（125〜127行）。

```go
	t.Logf("score=%d dotsEaten=%d lives=%d round=%d scene=%v maxGhostsOut=%d inkyLeft=%v",
		g.Play.Score, g.Play.NumDotsEaten, g.Play.NumLives, g.Play.Round,
		g.Scene, maxGhostsOut, inkyLeftHouse)
```

実施時にこのログへ出た値が、**スコア 350、
ドット 66** でした。そしてこの2つの数字は、
Nim 版の同一シナリオ（自動運転の進み方まで
揃えたもの）で得た値と**完全一致**しました。
Nim 版の数値の出典は、Nim 移植の実施報告書
（REPORT.md）のヘッドレス検証の記録です。

ここは書き方に注意が要ります。このテスト
自体の合否条件は「スコアが0より大きい」
「家を出たゴーストが3匹以上」といった
大づかみなものです。350 と 66 の一致は、
テストの合否ではなく、**実行してログを
読む**形で確認した事実です。それでも
意味は大きい。別々に書いた2つの移植が、
同じ物差しで測って同じ数字を出したことは、
両方が原典の挙動を同じだけ写せている
ことの、強い証拠になるからです。

## 12.5 決定性と面クリア

`TestDeterminism`（136行〜）は、20,000
ティックの短い実行を2回行い、スコア、
ドット数、パックマンと1匹目のゴーストの
座標、合計6つの値を配列にして比べます。
乱数は xorshift で種が固定されているので
（第3章）、同じ入力列からは同じ結果が
出るはずで、実際に完全一致します。
「決定的であること」自体が、移植の
正しさの一部として検証されているわけです。

`TestWinScenario`（161行〜）は、面クリアの
シナリオです。盤面のドットを1個だけ残し、
「243個食べた」ことにしてから、その1個を
食べさせます。確かめるのは、勝ちの凍結が
立つこと、ラウンドが1へ進むこと、盤面に
244個のドットが戻ること、そして全体
ドットカウンタが無効になることです
（207〜209行）。

```go
	if g.Play.GlobalDotCounterActive {
		t.Error("global dot counter must be inactive after a win")
	}
```

状態を直接書き換えて場面を作るのは、
テストが同じパッケージにいるからできる
ことです（12.2）。実際のプレイで244個目を
食べるまで待つ必要はありません。

## 12.6 挙動プローブ ― 数字で原典と突き合わせる

probes_test.go には、挙動プローブが9本
あります。Nim 版の点検で使った17項目の
プローブの、Go 版にあたります。やり方は
どれも同じで、場面を整えてティックを回し、
**原典の数字と一致するか**を見ます。

開始連鎖は、トリガーの差で測ります
（10〜20行）。

```go
func TestProbeEventTiming(t *testing.T) {
	g := toGameplay(t)
	dtReady := int64(g.Play.ReadyStarted.Tick) - int64(g.Play.Started.Tick)
	if dtReady != 120 {
		t.Errorf("prelude timing: started->readyStarted = %d, want 120", dtReady)
	}
	dtRound := int64(g.Play.RoundStarted.Tick) - int64(g.Play.ReadyStarted.Tick)
	if dtRound != 130 {
		t.Errorf("ready timing: readyStarted->roundStarted = %d, want 130", dtRound)
	}
}
```

プレリュードの開始から READY まで120、
そこからラウンド開始まで130。第6章で
読んだ開始連鎖が、数字のまま残っています。

散らばりから追跡への切り替わりは、
境界の両側を見ます（22〜35行）。

```go
func TestProbeScatterChaseSwitch(t *testing.T) {
	g := toGameplay(t)
	base := int64(g.Play.RoundStarted.Tick)
	for int64(g.Timing.Tick) < base+419 {
		g.Tick()
	}
	if s := g.Play.Ghost[GhostBlinky].State; s != GhostStateScatter {
		t.Errorf("at +419: Blinky state = %v, want scatter", s)
	}
	g.Tick()
	if s := g.Play.Ghost[GhostBlinky].State; s != GhostStateChase {
		t.Errorf("at +420: Blinky state = %v, want chase", s)
	}
}
```

+419 ではまだ散らばり、+420 で追跡。
境界の前後を両方押さえるのが、プローブの
書き方の型です。

残りのプローブも、同じ型で原典の数字を
押さえます。

- 速さ： パックマンは空き地で112ティックに
  98ピクセル（7/8）、食事中は約0.80、
  ゴーストは約6/7（0.857）
- 家のカウンタ： Inky は30ドットで出る。
  Clyde は90に、食べたエサの数が乗る
  （エサは家のカウンタを進めない、という
  原典の癖ごと測っています）
- 全体カウンタ： 死亡後のラウンドでは、
  Pinky が7、Inky が17、Clyde が32で出る
- 青の持続： 360ティック
- 捕食得点： 20、40、80、160（内部単位。
  表示はこの10倍です）

捕食得点の期待値は、テストの中でこう
書かれています（261行）。

```go
	want := []int{20, 40, 80, 160}
```

プローブの中で、とくに読み応えがあるのが
死亡のプローブです（`TestProbeGlobalCounter`、
145行〜）。死亡から READY までの差は
209 と測れますが、本来の遅延は210のはず、
という箇所に、コメントで理由が書かれて
います（154〜156行）。`start` は「今+1」に、
`StartAfter` は「今+N」に書くので、保存
された値の差は209になる。原典の C にも
同じ計算があり、移植の誤りではない、と
いう記録です。プローブは、数字だけでなく
「なぜその数字になるか」の置き場にも
なっています。

## 12.7 描画と音の、構造のテスト

描画と音は、実物を見たり聞いたりする
検証がこの環境ではできません（12.8）。
それでも、テストで押さえられる部分は
押さえてあります。鍵は、どちらも
「環境に触れる部分」と「計算だけの部分」を
分けてあることです（第9章、第10章）。

描画では、デコードの半分が通常のバッファ
の上で動き、グラフィクス環境なしで検証
できます。render_test.go の冒頭コメントが
そう述べています（5〜7行）。

```go
// The decode half of the renderer works on plain buffers, so it can
// be verified without a graphics context: known tiles decode to
// known shapes, and the palette follows the hardware rules.
```

確かめるのは、空白タイル（0x40）が全部0に
デコードされること、ドットのタイルと
パックマンのスプライトには絵があること、
パレットは4つ組の先頭が透明で残りが不透明
というハードウェアの規則どおりである
ことです。絵の「見た目」ではなく、デコードの
**構造**を確かめるので、構造テストと
呼んでいます。

音も同じです。audio_test.go の冒頭
（5〜7行）にあるとおり、音響装置なしで、
無音が無音のままであること、ダンプ音を
始めるとサンプルが出ること、生成が決定的
であることを確かめます。無音の確認は
こうです（31〜39行）。

```go
	// no voices active: pure silence
	if _, err := s.Read(buf); err != nil {
		t.Fatal(err)
	}
	for i, b := range buf {
		if b != 0 {
			t.Fatalf("silence broken at byte %d: %d", i, b)
		}
	}
```

Synth は `io.Reader` なので（第10章）、
スピーカーではなくテストのバッファへ
読ませることができます。あわせて、
プレリュードのデコードが stride 2 /
245ティック、死亡音が stride 1 / 90ティック
と、C・Nim と一致することもテストに
なっています（audio_test.go 9行〜）。

## 12.8 確かめられていないこと

最後に、検証の及んでいない範囲を正直に
書いておきます。実施報告書（REPORT.md）の
未確認事項が、正本です。

- **WASM はビルド成功のみ**です。ブラウザで
  実際に動くところは未確認です。移植側の
  実行環境からブラウザへ到達できなかった
  ためで、コードの問題と切り分けられた
  わけでもありません
- **実画面の見た目**（色、フェード、拡大時の
  粗さ）は未確認です。この環境では Xvfb の
  仮想画面で、イントロ600フレームとプレイ
  3,600フレームのスモークまでを確認しました
- **実音**は未確認です。実行環境に音響装置が
  なく、12.7 の構造の確認までが範囲です
  （C 版・Nim 版も同じ事情でした）
- **ゲームパッドとタッチの操作感**は
  未確認です。第11章の合流の計算は
  コードの上では決まっていますが、実機の
  触り心地は人の手でしか分かりません
- **他 OS（Windows / macOS）でのビルド**も
  未確認です

つまり、ここまでの章で「確かめた」と
書いたのは、すべて「こちらの環境で、
画面と音なしに測れる範囲」の話です。
残りは、手元で動かしてもらって初めて
分かることです。検証済みと未確認を
分けて書くのが、この連載の約束でした。
Go 版でも、その約束は同じです。

---

## 解剖メモ（第12章）

- H9 の効き目は、ロジックが Ebitengine の
  型を知らないこと。`Game.Tick()` を直接
  回せるので、画面も音もなしに検証できる。
- 表駆動テストは「仕様の文を表の行に写す」
  書き方。無名構造体のスライスと `range` で
  回し、失敗は `Errorf`（続行）と `Fatalf`
  （中止）を使い分ける。
- 60,000ティックの自動プレイで、スコア 350、
  ドット 66 が Nim 版と完全一致した。
  ただし一致の確認は、テストの合否では
  なくログを読む形である。
- プローブは「境界の両側を数字で押さえる」
  型。死亡の 209 のように、数字の理由まで
  コメントで残す置き場にもなっている。
- 描画と音は構造テストまで。WASM の実行、
  実画面、実音、操作感、他 OS は未確認。

## 手を動かす（読解演習）

1. timing_test.go の `TestTriggerVocabulary`
   （15行〜）を読んで、`Start` の +1 の約束が
   どの行で確かめられているか、指摘して
   ください。
2. probes_test.go のプローブを1つ選び、
   「場面の整え方」「測る数字」「境界の
   両側を見ているか」の3点で読み解いて
   ください。
3. `TestHeadlessPlay` の合否条件と、
   ログで記録されるだけの値を分け、
   「350 と 66 の一致」がどちらの側の
   事実か、自分の言葉で説明してください。

## 確認問題

**問1**：Go 版のゲームロジックが、
画面なしでテストできるのはなぜですか。

<details>
<summary>答え</summary>

ロジックが Ebitengine の型に依存して
いないからです（仕様書の決定 H9）。状態は
`Game` 型に集まり、進行は `Game.Tick()` を
呼ぶだけなので、テストは窓も音響装置も
なしにティックを直接回せます。入力も
`InputState` を状態に書くだけで再現
できます。
</details>

**問2**：表駆動テストで、データの合計値の
検証に `t.Errorf` が使われているのは
なぜですか。

<details>
<summary>答え</summary>

1件違っても残りの件を全部調べたいから
です。`Errorf` は失敗を記録して続行し、
`Fatalf` はそのテストを中止します。合計値の
照合では、どの配列まで合っていてどこから
違うかを一度に見たいので、続行する側を
選びます。
</details>

**問3**：Go 版について「未確認」と
されているものを、2つ挙げてください。

<details>
<summary>答え</summary>

たとえば、WASM のブラウザでの実行と、
実音です（ほかにも、実画面の見た目、
ゲームパッドとタッチの操作感、他 OS での
ビルドがあります）。テストとスモークで
確かめたのは、こちらの環境で画面と音なしに
測れる範囲までです。
</details>

---

# 終章 ― 4つの言語で書くということ

## 前章までのあらすじ

第12章で、テストと検証を読みました。
60,000ティックの自動プレイで、Go 版と
Nim 版が同じ数字を出したところまでが、
この連載の到達点です。この章では、4つの
実装を横に並べて、全体をまとめます。

## 13.1 4つの実装、1つの設計

同じ pacman.c の設計から、4つの実装が
生まれました。

| | C（原典） | Python 版 | Nim 版 | Go 版 |
|---|---|---|---|---|
| 題材の行数 | 4,303 | 581 | 2,242 | 3,333 |
| ファイル | 単一 | 単一 | 10モジュール | 10ファイル+生成器 |
| 土台 | sokol（C） | pygame-ce | sokol-nim | Ebitengine |
| 絵と音 | ROM データ | 自作 | ROM データ（機械抽出） | ROM データ（生成コード） |
| 入り口 | 呼ばれる | 回す | 呼ばれる | 呼ばれる |
| 状態 | 構造体 | dataclass | object | 構造体+メソッド |
| フラグ | ビット演算 | 真偽値の並び | 集合型 | ビット型+メソッド |

Go 版の 3,333 は、手書き 2,725 と生成
データ 608 の合計です。これにテスト 824 が
別にあります。

4つの実装を通して、変わらなかったものが
あります。状態は1か所に集めること。時間は
固定ティックとトリガーで扱うこと。場面は
ティックの境界で切り替えること。思考は
目標＋貪欲で作ること。調整する数字は表に
すること。設計判断は、4言語で残りました。

変わったのは、各言語の「自然な書き方」に
当たる部分です。フラグは、ビット演算から
真偽値の並び、集合型、そしてビット型＋
メソッドへ。ベクトルの計算は、関数の
入れ子、演算子、そしてメソッド連鎖へ。
音は、土台のコールバックから `io.Reader`
の pull 型へ。変わる部分の顔ぶれは、
言語ごとに違います。

## 13.2 行数の読み方

上の表の行数は、そのままでは比べられ
ません。理由は3つあります。

1つ目は、**データの持ち方**です。ROM
データは、値の個数こそ9,316で共通ですが、
書式で行数が大きく変わります。C は1行に
16値で915行、Nim は配列を1行に寄せて
16行、Go は C と同じ16値/行で 608行
（データの種類が違うため C とは行数が
一致しません）。C の 4,303 から冒頭
コメント132行と ROM データ915行を引いた
「コード部分 約3,256」と、Nim のコード
部分 2,226、Go の手書き 2,725 を比べる
のが、まだしも実態に近い見方です。

2つ目は、**テストの有無**です。Go 版には
824行のテストがありますが、これは題材の
行数 3,333 には含まれていません。C、
Python、Nim の各題材には、テスト自体が
付いていませんでした。「テストを書く
文化」の分は、行数の外にあります。

3つ目は、**土台の違い**です。Python 版の
581行が小さいのは、ROM データを持たず、
描画と音を pygame と自作の小さな仕組みで
済ませているからです。逆に Go の手書きが
Nim より約500行多い理由は、実施報告書に
読み取りがあります。演算子オーバーロードが
ない分のメソッド連鎖、検査を明示する
書き方、ファイルごとの定型、そして
input.go の172行が原典にない追加分
（3機器の入力）であることです。

つまり行数は、「何を持ち運んだか」
「検証をどこまで書いたか」「土台がどこ
まで面倒を見るか」で大きく動きます。
言語そのものの比較は、状態やフラグや
ベクトル演算のように、**同じ部品の
書き方の違い**で見るのが正確です。

## 13.3 はみ出し方は、言語ごとに違う

4つの移植は、原典から「はみ出す」場所が
それぞれ違いました。

Python 版は、**設計だけ**を持ち運びました。
状態、トリガー、思考、表というデータの
形は写しましたが、ROM データは持たず、
絵も音も自作です。原典からの距離が
いちばん大きい代わりに、いちばん小さい
実装になりました。

Nim 版は、**原典の土台ごと**持ち運び
ました。土台は原典と同じ sokol の系譜で、
ROM データも機械抽出してそのまま持って
います。区画と関数の対応を原典と揃えた、
4つの中で原典に最も近い移植です。

Go 版は、はみ出し方を**仕様書で先に
決めました**。仕様書 SPEC に、原典の仕様を
踏襲する部分と、Go ではみ出す箇所 H1〜H9
（置換4、消滅1、変形2、追加2）を書き、
全件に決定を付けてから実装に入りました。
この本の各章が H 番号を引いてきたのは、
その進め方の反映です。はみ出すこと自体は
他の版も同じですが、「決めてから書く」
形にしたのが Go 版の特徴です。

共通しているのは、線引きの存在です。
**何を揃えて、何を任せるか**。揃えるものは
仕様と挙動で、任せるものは各言語の自然な
書き方。この線引きがあるから、対応表を
取りながら、それぞれの言語らしく書く
ことができました。

## 13.4 移植という作業の進め方

4つの移植を通して、手順として残るものが
あります。Nim 版の終章で挙げた5つ ――
土台のスパイクを先にやる、区画を決めて
から書く、データは機械で運ぶ、ヘッドレスで
検証できる形を保つ、数字は実測する ―― は、
Go 版でもそのまま通用しました。Go 版は
そこに、3つを足しました。

1. **仕様の正本を持つ**: 原典の数値仕様を
   1か所にまとめ、実装も検証もそこを
   見るようにする。Go 版では SPEC.md が
   その役で、数値は pacman.c と照合済み
   です
2. **決定を文書にする**: はみ出す箇所は、
   実装しながら迷うのではなく、先に
   H1〜H9 の形で決めて書いておく。後から
   「なぜこうなっているか」を辿れる
   ことも、決定の文書化の効き目です
3. **検証を自動化する**: テストを本体と
   並べて置き、前の移植と同じ物差しで
   測る。60,000ティックの自動プレイで
   Nim 版と数字が一致したのは、物差しを
   揃えて自動で回し続けられたからです

逆に、自動化の届かない場所も残りました。
それが次の節です。

## 13.5 残る未確認事項

この本の終わりに、確かめられていない
ことをまとめておきます。

Go 版では、WASM のブラウザでの実行、
実画面の見た目、実音、ゲームパッドと
タッチの操作感、他 OS でのビルドが
未確認です（第12章）。Nim 版にも実画面と
実音の手元確認が残っていますし、
pacman.py も実画面・実音は未確認のまま
です。

これは、この連載の進め方の帰結でも
あります。こちらの環境で測れるものは
数字まで測り、測れないものは「未確認」と
明記して分ける。移植の成果物は、コードと
検証の記録と、この未確認のリストの、
3つで1組です。手元で動かして初めて
分かることが残っている、という前提で
読んでもらえればと思います。

## 13.6 この本の終わりに

C版教科書は「C を知らない人が、pacman.c を
完璧に書けるようになる」ための本でした。
Python 版、Nim 版、そしてこの Go 版は、
その設計が言語を越えてどう生きるかを
見る本です。

4つの実装を読み比べると、設計という
ものが、コードの書き方とは別の層にある
ことが見えてきます。書き方は言語ごとに
違ってよいし、違うべきです。設計が残る
からこそ、書き方を自由にできます。

Go 版がそこに足したのは、「決める」ことの
層です。仕様を正本として持ち、はみ出しを
先に決めて文書にし、検証を自動で回す。
設計、決定、検証の3つが揃うと、移植は
「写す作業」から「辿れる作業」に
変わります。

次の言語で書くときも、きっと同じです。

---

## 解剖メモ（終章）

- 行数は「何を持ち運んだか」「検証を
  どこまで書いたか」「土台の面倒の見方」で
  動く。言語の比較は、同じ部品の書き方で
  見る。
- はみ出し方は言語ごとに違う。Python は
  設計だけ、Nim は土台ごと、Go は仕様書で
  先に決めた。共通するのは「揃えるものと
  任せるもの」の線引き。
- Go 版が手順に足したのは、仕様の正本、
  決定の文書化、検証の自動化の3つ。
- 未確認事項は成果物の一部。検証済みと
  未確認を分けて書く。

## 手を動かす（読解演習）

1. 4つの実装から、同じ部品を1つ選んで
   （たとえば「音の出し方」）、書き方の
   違いを自分の言葉でまとめてください。
2. Go 版の H1〜H9 の中から1つ選んで、
   その決定がなかったら実装のどこで
   迷うことになったか、考えてください。
3. 付録Bの対応表を使って、C版教科書の
   好きな章を1つ、Go 版のコードで
   読み直してください。

## 確認問題

**問1**：Go 版（3,333行）と Nim 版
（2,242行）の行数差は、言語の差ですか。

<details>
<summary>答え</summary>

大半は違います。データの書式（Go は
16値/行で608行、Nim は1配列/行で16行）、
入力の追加分（input.go の172行）、
演算子がない分のメソッド連鎖などが
積み上がった差です。言語そのものの差は、
状態やフラグやベクトル演算といった、
同じ部品の書き方の違いに表れます。
なおテスト824行は、どちらの題材の行数
にも含まれていません。
</details>

**問2**：Go 版の「はみ出し方」が、
Python 版や Nim 版と違う点は何ですか。

<details>
<summary>答え</summary>

はみ出す箇所を、仕様書 SPEC の H1〜H9
として実装の前に決め、文書にしてから
書いたことです。Python 版は設計だけを
持ち運び、Nim 版は原典の土台ごと持ち
運びましたが、Go 版は「決めてから書く」
形にしたのが特徴です。
</details>

**問3**：移植の成果物は、何と何と
何で1組ですか。

<details>
<summary>答え</summary>

コードと、検証の記録と、未確認事項の
リストです。測れるものは数字まで測り、
測れないものは未確認と明記して分ける
ことで、手元での確認がどこから必要かが
分かる形になります。
</details>

---

*（付録Aに Go ソースの全文、付録Bに
C⇔Go の対応表、付録Cに検証の記録が
あります）*

---

# 付録A Go ソース全文

題材の Go ソースの全文です。正本として固定した複写（`src/`）と同一の内容です。本体10ファイルと、生成器 tools/extract.go、テスト7本を含みます。data.go は生成ファイルで、tools/extract.go が pacman.c から作ります。

## state.go（489行、対応: pacman.c 142〜678（定数・列挙型・構造体・状態・レベル表））

```go
// state.go -- constants, types and the single game state object.
// Corresponds to pacman.c lines 142-678 (config, enums, structs, data tables).
// Inside this file the writing follows Go conventions where the C code's
// intent allows it (e.g. freeze flags are a small int type with methods,
// not a raw uint8 bitfield at the call sites).
package main

// --- config (pacman.c 144-152) ---
const AudioVolume = 0.5

// --- global constants (pacman.c 161-193) ---
const (
	TickDurationNs  = 16_666_666
	TickToleranceNs = 1_000_000
	NumVoices       = 3
	NumSounds       = 3
	DisabledTicks   = 0xFFFFFFFF
	TileWidth       = 8
	TileHeight      = 8
	SpriteWidth     = 16
	SpriteHeight    = 16
	DisplayTilesX   = 28
	DisplayTilesY   = 36
	DisplayPixelsX  = DisplayTilesX * TileWidth
	DisplayPixelsY  = DisplayTilesY * TileHeight
	NumSprites      = 8
	NumDebugMarkers = 16
	FadeTicks       = 30
	NumLives        = 3
	NumStatusFruits = 7
	NumDots         = 244
	NumPills        = 4

	AnteportasX = 14 * TileWidth
	AnteportasY = 14*TileHeight + TileHeight/2

	GhostEatenFreezeTicks = 60
	PacmanEatenTicks      = 60
	PacmanDeathTicks      = 150
	GameoverTicks         = 3 * 60
	RoundwonTicks         = 4 * 60
	FruitactiveTicks      = 10 * 60
)

// --- tile, sprite and color codes (pacman.c 198-248) ---
const (
	TileSpace      = 0x40
	TileDot        = 0x10
	TilePill       = 0x14
	TileGhost      = 0xB0
	TileLife       = 0x20
	TileCherries   = 0x90
	TileStrawberry = 0x94
	TilePeach      = 0x98
	TileBell       = 0x9C
	TileApple      = 0xA0
	TileGrapes     = 0xA4
	TileGalaxian   = 0xA8
	TileKey        = 0xAC
	TileDoor       = 0xCF
)

const (
	SpritetileInvisible         = 30
	SpritetileScore200          = 40
	SpritetileScore400          = 41
	SpritetileScore800          = 42
	SpritetileScore1600         = 43
	SpritetileCherries          = 0
	SpritetileStrawberry        = 1
	SpritetilePeach             = 2
	SpritetileBell              = 3
	SpritetileApple             = 4
	SpritetileGrapes            = 5
	SpritetileGalaxian          = 6
	SpritetileKey               = 7
	SpritetilePacmanClosedMouth = 48
)

const (
	ColorBlank              = 0x00
	ColorDefault            = 0x0F
	ColorDot                = 0x10
	ColorPacman             = 0x09
	ColorBlinky             = 0x01
	ColorPinky              = 0x03
	ColorInky               = 0x05
	ColorClyde              = 0x07
	ColorFrightened         = 0x11
	ColorFrightenedBlinking = 0x12
	ColorGhostScore         = 0x18
	ColorEyes               = 0x19
	ColorCherries           = 0x14
	ColorStrawberry         = 0x0F
	ColorPeach              = 0x15
	ColorBell               = 0x16
	ColorApple              = 0x14
	ColorGrapes             = 0x17
	ColorGalaxian           = 0x09
	ColorKey                = 0x16
	ColorWhiteBorder        = 0x1F
	ColorFruitScore         = 0x03
)

// --- enums (pacman.c 254-320) ---

// Scene is the top-level game state (C: gamestate_t).
type Scene int

const (
	SceneIntro Scene = iota
	SceneGame
)

// Dir is a movement direction (C: dir_t).
// NOTE: bit0==0: horizontal movement, bit0==1: vertical movement.
type Dir int

const (
	DirRight Dir = iota
	DirDown
	DirLeft
	DirUp
	NumDirs
)

// Fruit is a bonus fruit kind (C: fruit_t).
type Fruit int

const (
	FruitNone Fruit = iota
	FruitCherries
	FruitStrawberry
	FruitPeach
	FruitApple
	FruitGrapes
	FruitGalaxian
	FruitBell
	FruitKey
	NumFruits
)

// SpriteIndex identifies a hardware sprite slot.
type SpriteIndex int

const (
	SpritePacman SpriteIndex = iota
	SpriteBlinky
	SpritePinky
	SpriteInky
	SpriteClyde
	SpriteFruit
)

// GhostType identifies one of the four ghosts.
type GhostType int

const (
	GhostBlinky GhostType = iota
	GhostPinky
	GhostInky
	GhostClyde
	NumGhosts
)

// GhostState is a ghost's movement state (C: ghoststate_t).
type GhostState int

const (
	GhostStateNone GhostState = iota
	GhostStateChase
	GhostStateScatter
	GhostStateFrightened
	GhostStateEyes
	GhostStateHouse
	GhostStateLeaveHouse
	GhostStateEnterHouse
)

// Freeze is the set of reasons the game is frozen (C: freezetype_t).
// In C these are (1<<n) bit values in a uint8; here the bit operations
// are hidden behind methods so call sites read as events.
type Freeze uint8

const (
	FreezePrelude Freeze = 1 << iota
	FreezeReady
	FreezeEatGhost
	FreezeDead
	FreezeWon
)

// Has reports whether the given freeze reason is present.
func (f Freeze) Has(o Freeze) bool { return f&o != 0 }

// Add sets the given freeze reason.
func (f *Freeze) Add(o Freeze) { *f |= o }

// Clear removes the given freeze reason (C: freeze &= ~o).
func (f *Freeze) Clear(o Freeze) { *f &^= o }

// Empty reports whether no freeze reason is present.
func (f Freeze) Empty() bool { return f == 0 }

// SoundFlags records which voices a playing sound uses (C: voice flags).
type SoundFlags uint8

const (
	SoundVoice0 SoundFlags = 1 << iota
	SoundVoice1
	SoundVoice2
	SoundAllVoices = SoundVoice0 | SoundVoice1 | SoundVoice2
)

// --- basic types (pacman.c 323-352) ---

// Trigger remembers one future tick (C: trigger_t).
// The methods live in timing.go.
type Trigger struct {
	Tick uint32
}

// Int2 is a 2D integer vector (C: int2_t).
// Arithmetic methods live in geom.go.
type Int2 struct {
	X int16
	Y int16
}

// I2 constructs an Int2.
func I2(x, y int16) Int2 { return Int2{X: x, Y: y} }

// Actor is anything that moves on the playfield.
type Actor struct {
	Dir      Dir
	Pos      Int2
	AnimTick uint32
}

// Ghost is one ghost and its house/thinking state.
type Ghost struct {
	Actor      Actor
	Typ        GhostType
	NextDir    Dir
	TargetPos  Int2
	State      GhostState
	Frightened Trigger
	Eaten      Trigger
	DotCounter uint16
	DotLimit   uint16
}

// Pacman is the player character.
type Pacman struct {
	Actor Actor
}

// --- renderer data types (pacman.c 360-385) ---

// Sprite is one sprite slot's data (the pixels live in render.go).
type Sprite struct {
	Enabled bool
	Tile    uint8
	Color   uint8
	FlipX   bool
	FlipY   bool
	Pos     Int2
}

// DebugMarker is a debug overlay marker.
type DebugMarker struct {
	Enabled bool
	Tile    uint8
	Color   uint8
	TilePos Int2
}

// --- sound types (pacman.c 388-418) ---

// SoundFunc is a procedural sound generator (C: sound_func_t).
// It receives the game because Go has no globals to reach for.
type SoundFunc func(g *Game, slot int32)

// SoundDesc describes a sound effect (C: snddesc_t).
// Data is a register dump (nil for procedural sounds); its length in
// uint32 words replaces the C byte-size field.
type SoundDesc struct {
	Fn    SoundFunc
	Data  []uint32
	Voice [3]bool
}

// Voice is one Namco-style sound voice.
type Voice struct {
	Counter   uint32
	Frequency uint32
	Waveform  uint8
	Volume    uint8
	SampleAcc float32
	SampleDiv float32
}

// Sound is one playing sound slot.
type Sound struct {
	CurTick  uint32
	Fn       SoundFunc
	NumTicks uint32
	Stride   uint32
	Data     []uint32
	Flags    SoundFlags
}

// --- the game state (pacman.c 420-540) ---

// TimingState holds the tick counter. The C accumulator fields are
// gone: Ebitengine calls Update once per tick (SPEC H1).
type TimingState struct {
	Tick uint32
}

// IntroState holds the intro scene's state.
type IntroState struct {
	Started Trigger
}

// PlayState is the state of one game in progress (C: state.game).
type PlayState struct {
	Xorshift        uint32
	Hiscore         uint32
	Started         Trigger
	ReadyStarted    Trigger
	RoundStarted    Trigger
	RoundWon        Trigger
	GameOver        Trigger
	DotEaten        Trigger
	PillEaten       Trigger
	GhostEaten      Trigger
	PacmanEaten     Trigger
	FruitEaten      Trigger
	ForceLeaveHouse Trigger
	FruitActive     Trigger
	Freeze          Freeze
	Round           uint8
	Score           uint32
	NumLives        int8
	NumGhostsEaten  uint8
	NumDotsEaten    uint8

	GlobalDotCounterActive bool
	GlobalDotCounter       uint8

	Ghost       [4]Ghost
	Pacman      Pacman
	ActiveFruit Fruit
}

// InputState is the resolved input (C: state.input).
// input.go fills this from the actual devices each tick.
type InputState struct {
	Enabled bool
	Up      bool
	Down    bool
	Left    bool
	Right   bool
	Esc     bool
	Anykey  bool
}

// AudioState holds the sound hardware state (C: state.audio).
// The sample output bookkeeping lives in audio.go's Synth.
type AudioState struct {
	Voice [NumVoices]Voice
	Sound [NumSounds]Sound
}

// GfxState holds the playfield data the renderer reads (C: state.gfx,
// minus the GPU resources, which live in render.go).
type GfxState struct {
	Fadein  Trigger
	Fadeout Trigger
	Fade    uint8

	VideoRAM    [DisplayTilesY][DisplayTilesX]uint8
	ColorRAM    [DisplayTilesY][DisplayTilesX]uint8
	Sprite      [NumSprites]Sprite
	DebugMarker [NumDebugMarkers]DebugMarker

	ColorPalette [256]uint32
}

// Game is the whole game state and the ebiten-facing game object.
// Behavior lives in rules.go (gameTick/introTick) and friends;
// the ebiten wiring lives in main.go.
type Game struct {
	Scene  Scene
	Timing TimingState
	Intro  IntroState
	Play   PlayState
	Input  InputState
	Audio  AudioState
	Gfx    GfxState
}

// --- data tables (pacman.c 542-623) ---

var ghostScatterTargets = [4]Int2{
	I2(25, 0), I2(2, 0), I2(27, 34), I2(0, 34),
}

// starting positions for ghosts (pixel coords), pacman.c 548-553
var ghostStartingPos = [4]Int2{
	I2(14*8, 14*8+4), I2(14*8, 17*8+4),
	I2(12*8, 17*8+4), I2(16*8, 17*8+4),
}

// target positions for ghosts entering the ghost house, pacman.c 556-561
var ghostHouseTargetPos = [4]Int2{
	I2(14*8, 17*8+4), I2(14*8, 17*8+4),
	I2(12*8, 17*8+4), I2(16*8, 17*8+4),
}

var fruitTilesColors = [9][3]uint8{
	{0, 0, 0},
	{TileCherries, SpritetileCherries, ColorCherries},
	{TileStrawberry, SpritetileStrawberry, ColorStrawberry},
	{TilePeach, SpritetilePeach, ColorPeach},
	{TileApple, SpritetileApple, ColorApple},
	{TileGrapes, SpritetileGrapes, ColorGrapes},
	{TileGalaxian, SpritetileGalaxian, ColorGalaxian},
	{TileBell, SpritetileBell, ColorBell},
	{TileKey, SpritetileKey, ColorKey},
}

var fruitScoreTiles = [9][4]uint8{
	{0x40, 0x40, 0x40, 0x40},
	{0x40, 0x81, 0x85, 0x40},
	{0x40, 0x82, 0x85, 0x40},
	{0x40, 0x83, 0x85, 0x40},
	{0x40, 0x84, 0x85, 0x40},
	{0x40, 0x86, 0x8D, 0x8E},
	{0x87, 0x88, 0x8D, 0x8E},
	{0x89, 0x8A, 0x8D, 0x8E},
	{0x8B, 0x8C, 0x8D, 0x8E},
}

// LevelSpec is one row of the level table (C: levelspec_t).
type LevelSpec struct {
	BonusFruit  Fruit
	BonusScore  uint16
	FrightTicks uint16
}

const maxLevelSpec = 21

var levelSpecTable = [maxLevelSpec]LevelSpec{
	{FruitCherries, 10, 6 * 60},
	{FruitStrawberry, 30, 5 * 60},
	{FruitPeach, 50, 4 * 60},
	{FruitPeach, 50, 3 * 60},
	{FruitApple, 70, 2 * 60},
	{FruitApple, 70, 5 * 60},
	{FruitGrapes, 100, 2 * 60},
	{FruitGrapes, 100, 2 * 60},
	{FruitGalaxian, 200, 1 * 60},
	{FruitGalaxian, 200, 5 * 60},
	{FruitBell, 300, 2 * 60},
	{FruitBell, 300, 1 * 60},
	{FruitKey, 500, 1 * 60},
	{FruitKey, 500, 3 * 60},
	{FruitKey, 500, 1 * 60},
	{FruitKey, 500, 1 * 60},
	{FruitKey, 500, 1},
	{FruitKey, 500, 1 * 60},
	{FruitKey, 500, 1},
	{FruitKey, 500, 1},
	{FruitKey, 500, 1},
}

// levelSpec returns the level spec for a round, clamped to the last
// table entry (pacman.c 835-843).
func levelSpec(round int) LevelSpec {
	if round < 0 {
		panic("levelSpec: negative round")
	}
	if round > maxLevelSpec-1 {
		round = maxLevelSpec - 1
	}
	return levelSpecTable[round]
}
```

## timing.go（97行、対応: pacman.c 826〜943 のうちトリガーと乱数（入力は input.go 側））

```go
// timing.go -- the time-trigger vocabulary and input helpers.
// Corresponds to pacman.c lines 826-943 (xorshift, triggers, input).
//
// Unlike the C and Nim versions, Trigger methods here take the current
// tick as an argument instead of reading a global, which keeps the
// vocabulary usable from headless tests.
package main

// xorshift32 is the xorshift random number generator (pacman.c 827-833).
func (p *PlayState) xorshift32() uint32 {
	x := p.Xorshift
	x ^= x << 13
	x ^= x >> 17
	x ^= x << 5
	p.Xorshift = x
	return x
}

// Start sets the trigger to the next game tick.
func (t *Trigger) Start(now uint32) { t.Tick = now + 1 }

// StartAfter sets the trigger to a future tick.
func (t *Trigger) StartAfter(now, ticks uint32) { t.Tick = now + ticks }

// Disable deactivates the trigger.
func (t *Trigger) Disable() { t.Tick = DisabledTicks }

// DisabledTrigger returns a deactivated trigger.
func DisabledTrigger() Trigger { return Trigger{Tick: DisabledTicks} }

// Now reports whether the trigger fires at the given tick.
func (t Trigger) Now(now uint32) bool { return t.Tick == now }

// Since returns the number of ticks since the trigger fired.
func (t Trigger) Since(now uint32) uint32 {
	if now >= t.Tick {
		return now - t.Tick
	}
	return DisabledTicks
}

// Between reports whether the trigger fired between begin and end
// ticks ago (begin <= since < end).
func (t Trigger) Between(now, begin, end uint32) bool {
	if begin >= end {
		panic("Trigger.Between: begin must be < end")
	}
	if t.Tick == DisabledTicks {
		return false
	}
	s := t.Since(now)
	return s >= begin && s < end
}

// AfterOnce reports whether the trigger fired exactly n ticks ago.
func (t Trigger) AfterOnce(now, n uint32) bool { return t.Since(now) == n }

// After reports whether the trigger fired at least n ticks ago.
func (t Trigger) After(now, n uint32) bool {
	s := t.Since(now)
	if s != DisabledTicks {
		return s >= n
	}
	return false
}

// Before reports whether the trigger fired less than n ticks ago.
func (t Trigger) Before(now, n uint32) bool {
	s := t.Since(now)
	if s != DisabledTicks {
		return s < n
	}
	return false
}

// Disable clears the input state and disables input (C: input_disable).
func (in *InputState) Disable() { *in = InputState{} }

// Enable enables input again (C: input_enable).
func (in *InputState) Enable() { in.Enabled = true }

// DirOr returns the currently wanted direction, or the given default
// (C: input_dir). Priority is up, down, right, left.
func (in InputState) DirOr(def Dir) Dir {
	switch {
	case in.Up:
		return DirUp
	case in.Down:
		return DirDown
	case in.Right:
		return DirRight
	case in.Left:
		return DirLeft
	default:
		return def
	}
}
```

## geom.go（170行、対応: pacman.c 988〜991、1230〜1361（幾何・盤面の問い合わせ））

```go
// geom.go -- geometry and playfield queries.
// Corresponds to pacman.c lines 988-991 and 1230-1361.
//
// Go's % and / truncate toward zero just like C, so the Nim version's
// cmod helper is not needed here; negative positions in the teleport
// tunnel behave identically by construction.
package main

// Add returns v + o.
func (v Int2) Add(o Int2) Int2 { return I2(v.X+o.X, v.Y+o.Y) }

// Sub returns v - o.
func (v Int2) Sub(o Int2) Int2 { return I2(v.X-o.X, v.Y-o.Y) }

// Scale returns v * s.
func (v Int2) Scale(s int16) Int2 { return I2(v.X*s, v.Y*s) }

// SquaredDistance returns the squared distance between v and o.
func (v Int2) SquaredDistance(o Int2) int32 {
	dx := int32(o.X - v.X)
	dy := int32(o.Y - v.Y)
	return dx*dx + dy*dy
}

// NearEqual reports whether v and o are within tolerance on both axes.
func (v Int2) NearEqual(o Int2, tolerance int16) bool {
	return abs16(o.X-v.X) <= tolerance && abs16(o.Y-v.Y) <= tolerance
}

func abs16(v int16) int16 {
	if v < 0 {
		return -v
	}
	return v
}

// ActorToSpritePos converts an actor position to a sprite position.
func (v Int2) ActorToSpritePos() Int2 {
	return I2(v.X-SpriteWidth/2, v.Y-SpriteHeight/2)
}

// distToTileMid returns the distance from a pixel position to the
// middle of its tile (pacman.c 988-991).
func distToTileMid(pos Int2) Int2 {
	return I2(TileWidth/2-pos.X%TileWidth, TileHeight/2-pos.Y%TileHeight)
}

// pixelToTilePos converts a pixel position to a tile position.
func pixelToTilePos(pixPos Int2) Int2 {
	return I2(pixPos.X/TileWidth, pixPos.Y/TileHeight)
}

// clampedTilePos clamps a tile position to valid playfield coords.
func clampedTilePos(tilePos Int2) Int2 {
	r := tilePos
	if r.X < 0 {
		r.X = 0
	} else if r.X >= DisplayTilesX {
		r.X = DisplayTilesX - 1
	}
	if r.Y < 3 {
		r.Y = 3
	} else if r.Y >= DisplayTilesY-2 {
		r.Y = DisplayTilesY - 3
	}
	return r
}

var dirMap = [4]Int2{I2(+1, 0), I2(0, +1), I2(-1, 0), I2(0, -1)}

// dirToVec converts a direction to a unit vector.
func dirToVec(dir Dir) Int2 {
	if dir < DirRight || dir >= NumDirs {
		panic("dirToVec: invalid dir")
	}
	return dirMap[dir]
}

// reverseDir returns the opposite direction.
func reverseDir(dir Dir) Dir {
	switch dir {
	case DirRight:
		return DirLeft
	case DirDown:
		return DirUp
	case DirLeft:
		return DirRight
	default:
		return DirDown
	}
}

// tileCodeAt returns the tile code at a tile position.
func (g *Game) tileCodeAt(tilePos Int2) uint8 {
	if tilePos.X < 0 || tilePos.X >= DisplayTilesX ||
		tilePos.Y < 0 || tilePos.Y >= DisplayTilesY {
		panic("tileCodeAt: out of range")
	}
	return g.Gfx.VideoRAM[tilePos.Y][tilePos.X]
}

// isBlockingTile reports whether a tile blocks movement.
func (g *Game) isBlockingTile(tilePos Int2) bool {
	return g.tileCodeAt(tilePos) >= 0xC0
}

// isDot reports whether a tile holds a dot.
func (g *Game) isDot(tilePos Int2) bool { return g.tileCodeAt(tilePos) == TileDot }

// isPill reports whether a tile holds a power pill.
func (g *Game) isPill(tilePos Int2) bool { return g.tileCodeAt(tilePos) == TilePill }

// isTunnel reports whether a tile is in the teleport tunnel.
func isTunnel(tilePos Int2) bool {
	return tilePos.Y == 17 && (tilePos.X <= 5 || tilePos.X >= 22)
}

// isRedzone reports whether a tile forbids upward movement for ghosts.
func isRedzone(tilePos Int2) bool {
	return tilePos.X >= 11 && tilePos.X <= 16 && (tilePos.Y == 14 || tilePos.Y == 26)
}

// canMove tests whether movement from a pixel position in a wanted
// direction is possible (pacman.c 1304-1331).
func (g *Game) canMove(pos Int2, wantedDir Dir, allowCornering bool) bool {
	dirVec := dirToVec(wantedDir)
	distMid := distToTileMid(pos)
	var moveDistMid, perpDistMid int16
	if dirVec.Y != 0 {
		moveDistMid = distMid.Y
		perpDistMid = distMid.X
	} else {
		moveDistMid = distMid.X
		perpDistMid = distMid.Y
	}
	tilePos := pixelToTilePos(pos)
	checkPos := clampedTilePos(tilePos.Add(dirVec))
	blocked := g.isBlockingTile(checkPos)
	return !((!allowCornering && perpDistMid != 0) ||
		(blocked && moveDistMid == 0))
}

// move computes a new pixel position along a direction, without a
// blocking check (pacman.c 1334-1361).
func move(pos Int2, dir Dir, allowCornering bool) Int2 {
	dirVec := dirToVec(dir)
	r := pos.Add(dirVec)
	if allowCornering {
		distMid := distToTileMid(r)
		if dirVec.X != 0 {
			if distMid.Y < 0 {
				r.Y--
			} else if distMid.Y > 0 {
				r.Y++
			}
		} else if dirVec.Y != 0 {
			if distMid.X < 0 {
				r.X--
			} else if distMid.X > 0 {
				r.X++
			}
		}
	}
	if r.X < 0 {
		r.X = DisplayPixelsX - 1
	} else if r.X >= DisplayPixelsX {
		r.X = 0
	}
	return r
}
```

## ghost.go（258行、対応: pacman.c 1750〜2087（ゴースト））

```go
// ghost.go -- ghost speed, state machine, target selection and steering.
// Corresponds to pacman.c lines 1750-2087.
package main

// ghostSpeed returns how many pixels the ghost moves this tick
// (pacman.c 1750-1775).
func (g *Game) ghostSpeed(ghost *Ghost) int {
	tick := g.Timing.Tick
	switch ghost.State {
	case GhostStateHouse, GhostStateLeaveHouse, GhostStateFrightened:
		// inside house / frightened: half speed
		return int(tick & 1)
	case GhostStateEyes, GhostStateEnterHouse:
		// estimated 1.5x in eye state
		if tick&1 != 0 {
			return 1
		}
		return 2
	default:
		if isTunnel(pixelToTilePos(ghost.Actor.Pos)) {
			if (tick*2)%4 != 0 {
				return 1
			}
			return 0
		}
		if tick%7 != 0 {
			return 1
		}
		return 0
	}
}

// scatterChasePhase returns the current global scatter or chase phase.
func (g *Game) scatterChasePhase() GhostState {
	t := g.Play.RoundStarted.Since(g.Timing.Tick)
	switch {
	case t < 7*60:
		return GhostStateScatter
	case t < 27*60:
		return GhostStateChase
	case t < 34*60:
		return GhostStateScatter
	case t < 54*60:
		return GhostStateChase
	case t < 59*60:
		return GhostStateScatter
	case t < 79*60:
		return GhostStateChase
	case t < 84*60:
		return GhostStateScatter
	default:
		return GhostStateChase
	}
}

// updateGhostState takes care of switching a ghost into a new state.
func (g *Game) updateGhostState(ghost *Ghost) {
	now := g.Timing.Tick
	newState := ghost.State
	switch ghost.State {
	case GhostStateEyes:
		if ghost.Actor.Pos.NearEqual(I2(AnteportasX, AnteportasY), 1) {
			newState = GhostStateEnterHouse
		}
	case GhostStateEnterHouse:
		if ghost.Actor.Pos.NearEqual(ghostHouseTargetPos[ghost.Typ], 1) {
			newState = GhostStateLeaveHouse
		}
	case GhostStateHouse:
		if g.Play.ForceLeaveHouse.AfterOnce(now, 4*60) {
			newState = GhostStateLeaveHouse
			g.Play.ForceLeaveHouse.Start(now)
		} else if g.Play.GlobalDotCounterActive {
			switch {
			case ghost.Typ == GhostPinky && g.Play.GlobalDotCounter == 7:
				newState = GhostStateLeaveHouse
			case ghost.Typ == GhostInky && g.Play.GlobalDotCounter == 17:
				newState = GhostStateLeaveHouse
			case ghost.Typ == GhostClyde && g.Play.GlobalDotCounter == 32:
				newState = GhostStateLeaveHouse
				// the global dot counter is deactivated when Clyde leaves at 32
				g.Play.GlobalDotCounterActive = false
			}
		} else if ghost.DotCounter == ghost.DotLimit {
			newState = GhostStateLeaveHouse
		}
	case GhostStateLeaveHouse:
		if ghost.Actor.Pos.Y == AnteportasY {
			newState = GhostStateScatter
		}
	default:
		if ghost.Frightened.Before(now, uint32(levelSpec(int(g.Play.Round)).FrightTicks)) {
			newState = GhostStateFrightened
		} else {
			newState = g.scatterChasePhase()
		}
	}
	// handle state transitions
	if newState != ghost.State {
		switch ghost.State {
		case GhostStateLeaveHouse:
			ghost.NextDir = DirLeft
			ghost.Actor.Dir = DirLeft
		case GhostStateEnterHouse:
			// a ghost that was eaten is immune to frighten until the next pill
			ghost.Frightened.Disable()
		case GhostStateFrightened:
			// don't reverse direction when leaving frightened state
		case GhostStateScatter, GhostStateChase:
			// any transition from scatter/chase causes a reversal of direction
			ghost.NextDir = reverseDir(ghost.Actor.Dir)
		}
		ghost.State = newState
	}
}

// updateGhostTarget updates the ghost's target position.
func (g *Game) updateGhostTarget(ghost *Ghost) {
	pos := ghost.TargetPos
	switch ghost.State {
	case GhostStateScatter:
		pos = ghostScatterTargets[ghost.Typ]
	case GhostStateChase:
		pm := g.Play.Pacman.Actor
		pmPos := pixelToTilePos(pm.Pos)
		pmDir := dirToVec(pm.Dir)
		switch ghost.Typ {
		case GhostBlinky:
			pos = pmPos
		case GhostPinky:
			// 4 tiles ahead of Pacman (without the arcade 'diagonal overflow')
			pos = pmPos.Add(pmDir.Scale(4))
		case GhostInky:
			blinkyPos := pixelToTilePos(g.Play.Ghost[GhostBlinky].Actor.Pos)
			p := pmPos.Add(pmDir.Scale(2))
			d := p.Sub(blinkyPos)
			pos = blinkyPos.Add(d.Scale(2))
		case GhostClyde:
			if ghost.Actor.Pos.pixelToTile().SquaredDistance(pmPos) > 64 {
				pos = pmPos
			} else {
				pos = ghostScatterTargets[GhostClyde]
			}
		}
	case GhostStateFrightened:
		// random target position (random direction at each intersection)
		pos = I2(int16(g.Play.xorshift32()%DisplayTilesX),
			int16(g.Play.xorshift32()%DisplayTilesY))
	case GhostStateEyes:
		pos = I2(13, 14)
	}
	ghost.TargetPos = pos
}

// pixelToTile is shorthand for pixelToTilePos on an actor position.
func (v Int2) pixelToTile() Int2 { return pixelToTilePos(v) }

// updateGhostDir computes the next ghost direction; it returns true if
// the resulting movement should always happen (movement inside the
// ghost house).
func (g *Game) updateGhostDir(ghost *Ghost) bool {
	switch ghost.State {
	case GhostStateHouse:
		if ghost.Actor.Pos.Y <= 17*TileHeight {
			ghost.NextDir = DirDown
		} else if ghost.Actor.Pos.Y >= 18*TileHeight {
			ghost.NextDir = DirUp
		}
		ghost.Actor.Dir = ghost.NextDir
		return true
	case GhostStateLeaveHouse:
		pos := ghost.Actor.Pos
		if pos.X == AnteportasX {
			if pos.Y > AnteportasY {
				ghost.NextDir = DirUp
			}
		} else {
			const midY = 17*TileHeight + TileHeight/2
			switch {
			case pos.Y > midY:
				ghost.NextDir = DirUp
			case pos.Y < midY:
				ghost.NextDir = DirDown
			case pos.X > AnteportasX:
				ghost.NextDir = DirLeft
			default:
				ghost.NextDir = DirRight
			}
		}
		ghost.Actor.Dir = ghost.NextDir
		return true
	case GhostStateEnterHouse:
		pos := ghost.Actor.Pos
		tilePos := pixelToTilePos(pos)
		tgtPos := ghostHouseTargetPos[ghost.Typ]
		if tilePos.Y == 14 {
			if pos.X != AnteportasX {
				if pos.X < AnteportasX {
					ghost.NextDir = DirRight
				} else {
					ghost.NextDir = DirLeft
				}
			} else {
				ghost.NextDir = DirDown
			}
		} else if pos.Y == tgtPos.Y {
			if pos.X < tgtPos.X {
				ghost.NextDir = DirRight
			} else {
				ghost.NextDir = DirLeft
			}
		}
		ghost.Actor.Dir = ghost.NextDir
		return true
	default:
		// scatter/chase/frightened: head towards the current target point
		distToMid := distToTileMid(ghost.Actor.Pos)
		if distToMid.X == 0 && distToMid.Y == 0 {
			ghost.Actor.Dir = ghost.NextDir
			dirVec := dirToVec(ghost.Actor.Dir)
			lookaheadPos := pixelToTilePos(ghost.Actor.Pos).Add(dirVec)
			dirs := [4]Dir{DirUp, DirLeft, DirDown, DirRight}
			minDist := int32(100000)
			for _, dir := range dirs {
				// in the two 'red zones', upward movement is forbidden (except eyes)
				if isRedzone(lookaheadPos) && dir == DirUp && ghost.State != GhostStateEyes {
					continue
				}
				revdir := reverseDir(dir)
				testPos := clampedTilePos(lookaheadPos.Add(dirToVec(dir)))
				if revdir != ghost.Actor.Dir && !g.isBlockingTile(testPos) {
					dist := testPos.SquaredDistance(ghost.TargetPos)
					if dist < minDist {
						minDist = dist
						ghost.NextDir = dir
					}
				}
			}
		}
		return false
	}
}

// updateGhosthouseDotCounters updates the dot counters used to decide
// whether ghosts must leave the house (called each time Pacman eats
// a dot).
func (g *Game) updateGhosthouseDotCounters() {
	if g.Play.GlobalDotCounterActive {
		g.Play.GlobalDotCounter++
	} else {
		for i := range g.Play.Ghost {
			if g.Play.Ghost[i].DotCounter < g.Play.Ghost[i].DotLimit {
				g.Play.Ghost[i].DotCounter++
				break
			}
		}
	}
}
```

## rules.go（481行、対応: pacman.c 1377〜1583、1733〜1748、2089〜2403（ルール））

```go
// rules.go -- playfield setup, round setup, actor updates, the game tick
// and the intro tick. Corresponds to pacman.c lines 1377-1583, 1733-1748,
// 2089-2403.
package main

// gameInitPlayfield initializes the playfield tiles from the ASCII map
// (pacman.c 1377-1432).
func (g *Game) gameInitPlayfield() {
	g.vidColorPlayfield(ColorDot)
	const tiles = "0UUUUUUUUUUUU45UUUUUUUUUUUU1" +
		"L............rl............R" +
		"L.ebbf.ebbbf.rl.ebbbf.ebbf.R" +
		"LPr  l.r   l.rl.r   l.r  lPR" +
		"L.guuh.guuuh.gh.guuuh.guuh.R" +
		"L..........................R" +
		"L.ebbf.ef.ebbbbbbf.ef.ebbf.R" +
		"L.guuh.rl.guuyxuuh.rl.guuh.R" +
		"L......rl....rl....rl......R" +
		"2BBBBf.rzbbf rl ebbwl.eBBBB3" +
		"     L.rxuuh gh guuyl.R     " +
		"     L.rl          rl.R     " +
		"     L.rl mjs--tjn rl.R     " +
		"UUUUUh.gh i      q gh.gUUUUU" +
		"      .   i      q   .      " +
		"BBBBBf.ef i      q ef.eBBBBB" +
		"     L.rl okkkkkkp rl.R     " +
		"     L.rl          rl.R     " +
		"     L.rl ebbbbbbf rl.R     " +
		"0UUUUh.gh guuyxuuh gh.gUUUU1" +
		"L............rl............R" +
		"L.ebbf.ebbbf.rl.ebbbf.ebbf.R" +
		"L.guyl.guuuh.gh.guuuh.rxuh.R" +
		"LP..rl.......  .......rl..PR" +
		"6bf.rl.ef.ebbbbbbf.ef.rl.eb8" +
		"7uh.gh.rl.guuyxuuh.rl.gh.gu9" +
		"L......rl....rl....rl......R" +
		"L.ebbbbwzbbf.rl.ebbwzbbbbf.R" +
		"L.guuuuuuuuh.gh.guuuuuuuuh.R" +
		"L..........................R" +
		"2BBBBBBBBBBBBBBBBBBBBBBBBBB3"
	var t [128]uint8
	for i := range t {
		t[i] = TileDot
	}
	t[' '] = 0x40
	t['0'] = 0xD1
	t['1'] = 0xD0
	t['2'] = 0xD5
	t['3'] = 0xD4
	t['4'] = 0xFB
	t['5'] = 0xFA
	t['6'] = 0xD7
	t['7'] = 0xD9
	t['8'] = 0xD6
	t['9'] = 0xD8
	t['U'] = 0xDB
	t['L'] = 0xD3
	t['R'] = 0xD2
	t['B'] = 0xDC
	t['b'] = 0xDF
	t['e'] = 0xE7
	t['f'] = 0xE6
	t['g'] = 0xEB
	t['h'] = 0xEA
	t['l'] = 0xE8
	t['r'] = 0xE9
	t['u'] = 0xE5
	t['w'] = 0xF5
	t['x'] = 0xF2
	t['y'] = 0xF3
	t['z'] = 0xF4
	t['m'] = 0xED
	t['n'] = 0xEC
	t['o'] = 0xEF
	t['p'] = 0xEE
	t['j'] = 0xDD
	t['i'] = 0xD2
	t['k'] = 0xDB
	t['q'] = 0xD3
	t['s'] = 0xF1
	t['t'] = 0xF0
	t['-'] = TileDoor
	t['P'] = TilePill
	i := 0
	for y := 3; y <= 33; y++ {
		for x := 0; x < 28; x++ {
			g.Gfx.VideoRAM[y][x] = t[tiles[i]&127]
			i++
		}
	}
	// ghost house gate colors
	g.vidColor(I2(13, 15), 0x18)
	g.vidColor(I2(14, 15), 0x18)
}

// gameDisableTimers disables all game loop timers.
func (g *Game) gameDisableTimers() {
	g.Play.RoundWon.Disable()
	g.Play.GameOver.Disable()
	g.Play.DotEaten.Disable()
	g.Play.PillEaten.Disable()
	g.Play.GhostEaten.Disable()
	g.Play.PacmanEaten.Disable()
	g.Play.FruitEaten.Disable()
	g.Play.ForceLeaveHouse.Disable()
	g.Play.FruitActive.Disable()
}

// gameInit is the one-time init at start of game state.
func (g *Game) gameInit() {
	g.Input.Enable()
	g.gameDisableTimers()
	g.Play.Round = 0
	g.Play.Freeze = FreezePrelude
	g.Play.NumLives = NumLives
	g.Play.GlobalDotCounterActive = false
	g.Play.GlobalDotCounter = 0
	g.Play.NumDotsEaten = 0
	g.Play.Score = 0
	g.vidClear(TileSpace, ColorDot)
	g.vidColorText(I2(9, 0), ColorDefault, "HIGH SCORE")
	g.gameInitPlayfield()
	g.vidColorText(I2(9, 14), 0x5, "PLAYER ONE")
	g.vidColorText(I2(11, 20), 0x9, "READY!")
}

// gameRoundInit sets up the state at start of a game round.
func (g *Game) gameRoundInit() {
	g.sprClear()
	g.vidColorText(I2(9, 14), 0x10, "          ")
	if g.Play.NumDotsEaten == NumDots {
		// round won: redraw the playfield, reset the global dot counter
		g.Play.Round++
		g.Play.NumDotsEaten = 0
		g.gameInitPlayfield()
		g.Play.GlobalDotCounterActive = false
	} else {
		if g.Play.NumLives != NumLives {
			g.Play.GlobalDotCounterActive = true
			g.Play.GlobalDotCounter = 0
		}
		g.Play.NumLives--
	}
	if g.Play.NumLives < 0 {
		panic("gameRoundInit: numLives < 0")
	}

	g.Play.ActiveFruit = FruitNone
	g.Play.Freeze = FreezeReady
	g.Play.Xorshift = 0x12345678 // random-number-generator seed
	g.Play.NumGhostsEaten = 0
	g.gameDisableTimers()
	g.vidColorText(I2(11, 20), 0x9, "READY!")
	g.Play.ForceLeaveHouse.Start(g.Timing.Tick)

	g.Play.Pacman = Pacman{Actor: Actor{
		Dir: DirLeft, Pos: I2(14*8, 26*8+4)}}
	g.Gfx.Sprite[SpritePacman] = Sprite{
		Enabled: true, Color: ColorPacman}

	g.Play.Ghost[GhostBlinky] = Ghost{
		Actor: Actor{Dir: DirLeft, Pos: ghostStartingPos[GhostBlinky]},
		Typ:   GhostBlinky, NextDir: DirLeft, State: GhostStateScatter,
		Frightened: DisabledTrigger(), Eaten: DisabledTrigger(),
		DotCounter: 0, DotLimit: 0}
	g.Gfx.Sprite[SpriteBlinky] = Sprite{
		Enabled: true, Color: ColorBlinky}

	g.Play.Ghost[GhostPinky] = Ghost{
		Actor: Actor{Dir: DirDown, Pos: ghostStartingPos[GhostPinky]},
		Typ:   GhostPinky, NextDir: DirDown, State: GhostStateHouse,
		Frightened: DisabledTrigger(), Eaten: DisabledTrigger(),
		DotCounter: 0, DotLimit: 0}
	g.Gfx.Sprite[SpritePinky] = Sprite{
		Enabled: true, Color: ColorPinky}

	g.Play.Ghost[GhostInky] = Ghost{
		Actor: Actor{Dir: DirUp, Pos: ghostStartingPos[GhostInky]},
		Typ:   GhostInky, NextDir: DirUp, State: GhostStateHouse,
		Frightened: DisabledTrigger(), Eaten: DisabledTrigger(),
		DotCounter: 0, DotLimit: 30}
	g.Gfx.Sprite[SpriteInky] = Sprite{
		Enabled: true, Color: ColorInky}

	g.Play.Ghost[GhostClyde] = Ghost{
		Actor: Actor{Dir: DirUp, Pos: ghostStartingPos[GhostClyde]},
		Typ:   GhostClyde, NextDir: DirUp, State: GhostStateHouse,
		Frightened: DisabledTrigger(), Eaten: DisabledTrigger(),
		DotCounter: 0, DotLimit: 60}
	g.Gfx.Sprite[SpriteClyde] = Sprite{
		Enabled: true, Color: ColorClyde}
}

// pacmanShouldMove returns true if Pacman should move in this tick.
func (g *Game) pacmanShouldMove() bool {
	now := g.Timing.Tick
	switch {
	case g.Play.DotEaten.Now(now):
		return false // eating a dot stops Pacman for 1 tick
	case g.Play.PillEaten.Since(now) < 3:
		return false // eating a pill stops Pacman for 3 ticks
	default:
		return (g.Timing.Tick % 8) != 0
	}
}

// gameUpdateDotsEaten is called when a dot or pill has been eaten.
func (g *Game) gameUpdateDotsEaten() {
	g.Play.NumDotsEaten++
	if g.Play.NumDotsEaten == NumDots {
		g.Play.RoundWon.Start(g.Timing.Tick)
		g.sndClear()
	} else if g.Play.NumDotsEaten == 70 || g.Play.NumDotsEaten == 170 {
		g.Play.FruitActive.Start(g.Timing.Tick)
	}
	// alternating crunch sound effect
	if (g.Play.NumDotsEaten & 1) != 0 {
		g.sndStart(2, sndEatdot1)
	} else {
		g.sndStart(2, sndEatdot2)
	}
}

// gameUpdateActors is the central Pacman and ghost behaviour function,
// called once per game tick.
func (g *Game) gameUpdateActors() {
	now := g.Timing.Tick
	// Pacman "AI"
	if g.pacmanShouldMove() {
		actor := &g.Play.Pacman.Actor
		wantedDir := g.Input.DirOr(actor.Dir)
		if g.canMove(actor.Pos, wantedDir, true) {
			actor.Dir = wantedDir
		}
		if g.canMove(actor.Pos, actor.Dir, true) {
			actor.Pos = move(actor.Pos, actor.Dir, true)
			actor.AnimTick++
		}
		tilePos := pixelToTilePos(actor.Pos)
		if g.isDot(tilePos) {
			g.vidTile(tilePos, TileSpace)
			g.Play.Score++
			g.Play.DotEaten.Start(now)
			g.Play.ForceLeaveHouse.Start(now)
			g.gameUpdateDotsEaten()
			g.updateGhosthouseDotCounters()
		}
		if g.isPill(tilePos) {
			g.vidTile(tilePos, TileSpace)
			g.Play.Score += 5
			g.gameUpdateDotsEaten()
			g.Play.PillEaten.Start(now)
			g.Play.NumGhostsEaten = 0
			for i := range g.Play.Ghost {
				g.Play.Ghost[i].Frightened.Start(now)
			}
			g.sndStart(1, sndFrightened)
		}
		// check if Pacman eats the bonus fruit
		if g.Play.ActiveFruit != FruitNone {
			testPos := pixelToTilePos(actor.Pos.Add(I2(TileWidth/2, 0)))
			if testPos == I2(14, 20) {
				g.Play.FruitEaten.Start(now)
				g.Play.Score += uint32(levelSpec(int(g.Play.Round)).BonusScore)
				g.vidFruitScore(g.Play.ActiveFruit)
				g.Play.ActiveFruit = FruitNone
				g.sndStart(2, sndEatfruit)
			}
		}
		// check if Pacman collides with any ghost
		for i := range g.Play.Ghost {
			ghost := &g.Play.Ghost[i]
			ghostTilePos := pixelToTilePos(ghost.Actor.Pos)
			if tilePos == ghostTilePos {
				if ghost.State == GhostStateFrightened {
					ghost.State = GhostStateEyes
					ghost.Eaten.Start(now)
					g.Play.GhostEaten.Start(now)
					g.Play.NumGhostsEaten++
					// increase score by 20, 40, 80, 160 (in 10-point units)
					g.Play.Score += uint32(10 * (1 << g.Play.NumGhostsEaten))
					g.Play.Freeze.Add(FreezeEatGhost)
					g.sndStart(2, sndEatghost)
				} else if ghost.State == GhostStateChase ||
					ghost.State == GhostStateScatter {
					g.sndClear()
					g.Play.PacmanEaten.Start(now)
					g.Play.Freeze.Add(FreezeDead)
					if g.Play.NumLives > 0 {
						g.Play.ReadyStarted.StartAfter(now,
							PacmanEatenTicks+PacmanDeathTicks)
					} else {
						g.Play.GameOver.StartAfter(now,
							PacmanEatenTicks+PacmanDeathTicks)
					}
				}
			}
		}
	}

	// Ghost "AIs"
	for i := range g.Play.Ghost {
		ghost := &g.Play.Ghost[i]
		g.updateGhostState(ghost)
		g.updateGhostTarget(ghost)
		numMoveTicks := g.ghostSpeed(ghost)
		for j := 0; j < numMoveTicks; j++ {
			forceMove := g.updateGhostDir(ghost)
			if forceMove || g.canMove(ghost.Actor.Pos, ghost.Actor.Dir, false) {
				ghost.Actor.Pos = move(ghost.Actor.Pos, ghost.Actor.Dir, false)
				ghost.Actor.AnimTick++
			}
		}
	}
}

// NewGame creates a game in its initial state: the intro scene is
// started at the first tick (pacman.c's init callback starts the
// intro trigger before the first frame).
func NewGame() *Game {
	g := &Game{}
	g.Intro.Started.Start(g.Timing.Tick)
	return g
}

// Tick advances the whole game by one tick. It is the headless entry
// point: main.go's Update calls it once per Ebiten tick (SPEC H1),
// and the tests call it directly. The order mirrors pacman.c's frame
// callback: advance the tick, tick the sound, switch scenes on the
// started triggers, then run the scene's tick.
func (g *Game) Tick() {
	g.Timing.Tick++
	g.sndTick()
	now := g.Timing.Tick
	if g.Intro.Started.Now(now) {
		g.Scene = SceneIntro
	}
	if g.Play.Started.Now(now) {
		g.Scene = SceneGame
	}
	switch g.Scene {
	case SceneIntro:
		g.introTick()
	case SceneGame:
		g.gameTick()
	}
}

// gameTick is the central game tick function, called at 60 Hz.
func (g *Game) gameTick() {
	now := g.Timing.Tick
	if g.Play.Started.Now(now) {
		g.Gfx.Fadein.Start(now)
		g.Play.ReadyStarted.StartAfter(now, 2*60)
		g.sndStart(0, sndPrelude)
		g.gameInit()
	}
	if g.Play.ReadyStarted.Now(now) {
		g.gameRoundInit()
		g.Play.RoundStarted.StartAfter(now, 2*60+10)
	}
	if g.Play.RoundStarted.Now(now) {
		g.Play.Freeze.Clear(FreezeReady)
		g.vidColorText(I2(11, 20), 0x10, "      ")
		g.sndStart(1, sndWeeooh)
	}

	// activate/deactivate bonus fruit
	if g.Play.FruitActive.Now(now) {
		g.Play.ActiveFruit = levelSpec(int(g.Play.Round)).BonusFruit
	} else if g.Play.FruitActive.AfterOnce(now, FruitactiveTicks) {
		g.Play.ActiveFruit = FruitNone
	}

	// stop frightened sound and restart the weeooh sound
	if g.Play.PillEaten.AfterOnce(now,
		uint32(levelSpec(int(g.Play.Round)).FrightTicks)) {
		g.sndStart(1, sndWeeooh)
	}

	// unfreeze after Pacman ate a ghost
	if g.Play.Freeze.Has(FreezeEatGhost) {
		if g.Play.GhostEaten.AfterOnce(now, GhostEatenFreezeTicks) {
			g.Play.Freeze.Clear(FreezeEatGhost)
		}
	}

	// play the pacman-death sound
	if g.Play.PacmanEaten.AfterOnce(now, PacmanEatenTicks) {
		g.sndStart(2, sndDead)
	}

	if g.Play.Freeze.Empty() {
		g.gameUpdateActors()
	}
	g.gameUpdateTiles()
	g.gameUpdateSprites()

	if g.Play.Score > g.Play.Hiscore {
		g.Play.Hiscore = g.Play.Score
	}

	// check for end-of-round conditions
	if g.Play.RoundWon.Now(now) {
		g.Play.Freeze.Add(FreezeWon)
		g.Play.ReadyStarted.StartAfter(now, RoundwonTicks)
	}
	if g.Play.GameOver.Now(now) {
		g.vidColorText(I2(9, 20), 0x01, "GAME  OVER")
		g.Input.Disable()
		g.Gfx.Fadeout.StartAfter(now, GameoverTicks)
		g.Intro.Started.StartAfter(now, GameoverTicks+FadeTicks)
	}
}

// introTick is the intro screen tick function.
func (g *Game) introTick() {
	now := g.Timing.Tick
	if g.Intro.Started.Now(now) {
		g.sndClear()
		g.sprClear()
		g.Gfx.Fadein.Start(now)
		g.Input.Enable()
		g.vidClear(TileSpace, ColorDefault)
		g.vidText(I2(3, 0), "1UP   HIGH SCORE   2UP")
		g.vidColorScore(I2(6, 1), ColorDefault, 0)
		if g.Play.Hiscore > 0 {
			g.vidColorScore(I2(16, 1), ColorDefault, g.Play.Hiscore)
		}
		g.vidText(I2(7, 5), "CHARACTER / NICKNAME")
		g.vidText(I2(3, 35), "CREDIT  0")
	}

	delay := uint32(30)
	names := [4]string{"-SHADOW", "-SPEEDY", "-BASHFUL", "-POKEY"}
	nicknames := [4]string{"BLINKY", "PINKY", "INKY", "CLYDE"}
	for i := 0; i < 4; i++ {
		color := uint8(2*i + 1)
		y := int16(3*i + 6)
		delay += 30
		if g.Intro.Started.AfterOnce(now, delay) {
			g.vidColorTile(I2(4, y+0), color, TileGhost+0)
			g.vidColorTile(I2(5, y+0), color, TileGhost+1)
			g.vidColorTile(I2(4, y+1), color, TileGhost+2)
			g.vidColorTile(I2(5, y+1), color, TileGhost+3)
			g.vidColorTile(I2(4, y+2), color, TileGhost+4)
			g.vidColorTile(I2(5, y+2), color, TileGhost+5)
		}
		delay += 60
		if g.Intro.Started.AfterOnce(now, delay) {
			g.vidColorText(I2(7, y+1), color, names[i])
		}
		delay += 30
		if g.Intro.Started.AfterOnce(now, delay) {
			g.vidColorText(I2(17, y+1), color, nicknames[i])
		}
	}

	delay += 60
	if g.Intro.Started.AfterOnce(now, delay) {
		g.vidColorTile(I2(10, 24), ColorDot, TileDot)
		g.vidText(I2(12, 24), "10 \x5D\x5E\x5F")
		g.vidColorTile(I2(10, 26), ColorDot, TilePill)
		g.vidText(I2(12, 26), "50 \x5D\x5E\x5F")
	}

	delay += 60
	if g.Intro.Started.After(now, delay) {
		if (g.Intro.Started.Since(now) & 0x20) != 0 {
			g.vidColorText(I2(3, 31), 3, "                       ")
		} else {
			g.vidColorText(I2(3, 31), 3, "PRESS ANY KEY TO START!")
		}
	}

	if g.Input.Anykey {
		g.Input.Disable()
		g.Gfx.Fadeout.Start(now)
		g.Play.Started.StartAfter(now, FadeTicks)
	}
}
```

## render.go（651行、対応: pacman.c 993〜1229、1584〜1732、2404〜3124（描画。Ebitengine への置き換えを含む））

```go
// render.go -- video RAM writes, sprite animation, and (from Phase 3)
// the Ebitengine renderer. Corresponds to pacman.c lines 993-1229
// (vid/spr), 1584-1732 (tile/sprite updates) and 2404-3124 (gfx).
package main

import (
	"image/color"

	"github.com/hajimehoshi/ebiten/v2"
)

// --- vid: writes into the tile/color buffers (pacman.c 993-1133) ---

func (g *Game) vidClear(tileCode, colorCode uint8) {
	for y := 0; y < DisplayTilesY; y++ {
		for x := 0; x < DisplayTilesX; x++ {
			g.Gfx.VideoRAM[y][x] = tileCode
			g.Gfx.ColorRAM[y][x] = colorCode
		}
	}
}

func (g *Game) vidColorPlayfield(colorCode uint8) {
	for y := 3; y < DisplayTilesY-2; y++ {
		for x := 0; x < DisplayTilesX; x++ {
			g.Gfx.ColorRAM[y][x] = colorCode
		}
	}
}

func validTilePos(tilePos Int2) bool {
	return tilePos.X >= 0 && tilePos.X < DisplayTilesX &&
		tilePos.Y >= 0 && tilePos.Y < DisplayTilesY
}

func (g *Game) vidColor(tilePos Int2, colorCode uint8) {
	if !validTilePos(tilePos) {
		panic("vidColor: invalid tile pos")
	}
	g.Gfx.ColorRAM[tilePos.Y][tilePos.X] = colorCode
}

func (g *Game) vidTile(tilePos Int2, tileCode uint8) {
	if !validTilePos(tilePos) {
		panic("vidTile: invalid tile pos")
	}
	g.Gfx.VideoRAM[tilePos.Y][tilePos.X] = tileCode
}

func (g *Game) vidColorTile(tilePos Int2, colorCode, tileCode uint8) {
	if !validTilePos(tilePos) {
		panic("vidColorTile: invalid tile pos")
	}
	g.Gfx.VideoRAM[tilePos.Y][tilePos.X] = tileCode
	g.Gfx.ColorRAM[tilePos.Y][tilePos.X] = colorCode
}

// convChar translates an ASCII char into a "NAMCO char".
func convChar(c byte) uint8 {
	switch c {
	case ' ':
		return 0x40
	case '/':
		return 58
	case '-':
		return 59
	case '"':
		return 38
	case '!':
		return 'Z' + 1
	default:
		return c
	}
}

func (g *Game) vidColorChar(tilePos Int2, colorCode uint8, chr byte) {
	if !validTilePos(tilePos) {
		panic("vidColorChar: invalid tile pos")
	}
	g.Gfx.VideoRAM[tilePos.Y][tilePos.X] = convChar(chr)
	g.Gfx.ColorRAM[tilePos.Y][tilePos.X] = colorCode
}

func (g *Game) vidChar(tilePos Int2, chr byte) {
	if !validTilePos(tilePos) {
		panic("vidChar: invalid tile pos")
	}
	g.Gfx.VideoRAM[tilePos.Y][tilePos.X] = convChar(chr)
}

func (g *Game) vidColorText(tilePos Int2, colorCode uint8, text string) {
	if !validTilePos(tilePos) {
		panic("vidColorText: invalid tile pos")
	}
	tp := tilePos
	for i := 0; i < len(text); i++ {
		if tp.X < DisplayTilesX {
			g.vidColorChar(tp, colorCode, text[i])
			tp.X++
		} else {
			break
		}
	}
}

func (g *Game) vidText(tilePos Int2, text string) {
	if !validTilePos(tilePos) {
		panic("vidText: invalid tile pos")
	}
	tp := tilePos
	for i := 0; i < len(text); i++ {
		if tp.X < DisplayTilesX {
			g.vidChar(tp, text[i])
			tp.X++
		} else {
			break
		}
	}
}

// vidColorScore prints a score (scores are /10, printed right to left,
// last digit always 0).
func (g *Game) vidColorScore(tilePos Int2, colorCode uint8, score uint32) {
	tp := tilePos
	s := score
	g.vidColorChar(tp, colorCode, '0')
	tp.X--
	for digit := 0; digit < 8; digit++ {
		chr := byte(s%10) + '0'
		if validTilePos(tp) {
			g.vidColorChar(tp, colorCode, chr)
			tp.X--
			s /= 10
			if s == 0 {
				break
			}
		}
	}
}

// vidDrawTileQuad draws a 2x2 tile quad (used for lives and status
// fruits).
func (g *Game) vidDrawTileQuad(tilePos Int2, colorCode, tileCode uint8) {
	for yy := 0; yy < 2; yy++ {
		for xx := 0; xx < 2; xx++ {
			t := tileCode + uint8(yy*2+(1-xx))
			g.vidColorTile(I2(tilePos.X+int16(xx), tilePos.Y+int16(yy)),
				colorCode, t)
		}
	}
}

// vidFruitScore draws the fruit bonus score tiles (when Pacman has
// eaten the bonus fruit).
func (g *Game) vidFruitScore(fruitType Fruit) {
	if fruitType < FruitNone || fruitType >= NumFruits {
		panic("vidFruitScore: invalid fruit")
	}
	colorCode := uint8(ColorFruitScore)
	if fruitType == FruitNone {
		colorCode = ColorDot
	}
	for i := 0; i < 4; i++ {
		g.vidColorTile(I2(int16(12+i), 20), colorCode,
			fruitScoreTiles[fruitType][i])
	}
}

// --- spr: sprite state and animation (pacman.c 1134-1229) ---

func (g *Game) sprClear() {
	for i := range g.Gfx.Sprite {
		g.Gfx.Sprite[i] = Sprite{}
	}
}

func (g *Game) sprPacman() *Sprite { return &g.Gfx.Sprite[SpritePacman] }

func (g *Game) sprGhost(typ GhostType) *Sprite {
	if typ < GhostBlinky || typ >= NumGhosts {
		panic("sprGhost: invalid ghost type")
	}
	return &g.Gfx.Sprite[int(SpriteBlinky)+int(typ)]
}

func (g *Game) sprFruit() *Sprite { return &g.Gfx.Sprite[SpriteFruit] }

func (g *Game) sprAnimPacman(dir Dir, tick uint32) {
	tiles := [2][4]uint8{
		{44, 46, 48, 46}, // horizontal (needs flipx)
		{45, 47, 48, 47}, // vertical (needs flipy)
	}
	spr := g.sprPacman()
	phase := (tick / 2) & 3
	spr.Tile = tiles[dir&1][phase]
	spr.Color = ColorPacman
	spr.FlipX = dir == DirLeft
	spr.FlipY = dir == DirUp
}

func (g *Game) sprAnimPacmanDeath(tick uint32) {
	spr := g.sprPacman()
	tile := 52 + tick/8
	if tile > 63 {
		tile = 63
	}
	spr.Tile = uint8(tile)
	spr.FlipX = false
	spr.FlipY = false
}

func (g *Game) sprAnimGhost(ghostType GhostType, dir Dir, tick uint32) {
	if dir < DirRight || dir >= NumDirs {
		panic("sprAnimGhost: invalid dir")
	}
	tiles := [4][2]uint8{{32, 33}, {34, 35}, {36, 37}, {38, 39}}
	phase := (tick / 8) & 1
	spr := g.sprGhost(ghostType)
	spr.Tile = tiles[dir][phase]
	spr.Color = ColorBlinky + uint8(2*ghostType)
	spr.FlipX = false
	spr.FlipY = false
}

func (g *Game) sprAnimGhostFrightened(ghostType GhostType, tick uint32) {
	tiles := [2]uint8{28, 29}
	phase := (tick / 4) & 1
	spr := g.sprGhost(ghostType)
	spr.Tile = tiles[phase]
	// towards the end of the frightened period, start blinking (the C
	// code casts the possibly negative difference to uint32,
	// replicated here)
	fright := uint32(int32(levelSpec(int(g.Play.Round)).FrightTicks) - 60)
	if tick > fright {
		if (tick & 0x10) != 0 {
			spr.Color = ColorFrightened
		} else {
			spr.Color = ColorFrightenedBlinking
		}
	} else {
		spr.Color = ColorFrightened
	}
	spr.FlipX = false
	spr.FlipY = false
}

func (g *Game) sprAnimGhostEyes(ghostType GhostType, dir Dir) {
	if dir < DirRight || dir >= NumDirs {
		panic("sprAnimGhostEyes: invalid dir")
	}
	tiles := [4]uint8{32, 34, 36, 38}
	spr := g.sprGhost(ghostType)
	spr.Tile = tiles[dir]
	spr.Color = ColorEyes
	spr.FlipX = false
	spr.FlipY = false
}

// --- dynamic tile and sprite updates (pacman.c 1584-1732) ---

func (g *Game) gameUpdateTiles() {
	now := g.Timing.Tick
	g.vidColorScore(I2(6, 1), ColorDefault, g.Play.Score)
	if g.Play.Hiscore > 0 {
		g.vidColorScore(I2(16, 1), ColorDefault, g.Play.Hiscore)
	}

	pillPos := [NumPills]Int2{I2(1, 6), I2(26, 6), I2(1, 26), I2(26, 26)}
	for i := 0; i < NumPills; i++ {
		if g.Play.Freeze != 0 {
			g.vidColor(pillPos[i], ColorDot)
		} else if (g.Timing.Tick & 0x8) != 0 {
			g.vidColor(pillPos[i], 0x10)
		} else {
			g.vidColor(pillPos[i], 0)
		}
	}

	if g.Play.FruitEaten.AfterOnce(now, 2*60) {
		g.vidFruitScore(FruitNone)
	}

	for i := 0; i < NumLives; i++ {
		color := uint8(0)
		if i < int(g.Play.NumLives) {
			color = ColorPacman
		}
		g.vidDrawTileQuad(I2(int16(2+2*i), 34), color, TileLife)
	}

	// bonus fruit list in the bottom-right corner
	{
		x := int16(24)
		round := int(g.Play.Round)
		for i := round - NumStatusFruits + 1; i <= round; i++ {
			if i >= 0 {
				fruit := levelSpec(i).BonusFruit
				g.vidDrawTileQuad(I2(x, 34), fruitTilesColors[fruit][2],
					fruitTilesColors[fruit][0])
				x -= 2
			}
		}
	}

	// if the round was won, blink the whole playfield blue/white
	if g.Play.RoundWon.After(now, 1*60) {
		if (g.Play.RoundWon.Since(now) & 0x10) != 0 {
			g.vidColorPlayfield(ColorDot)
		} else {
			g.vidColorPlayfield(ColorWhiteBorder)
		}
	}
}

func (g *Game) gameUpdateSprites() {
	now := g.Timing.Tick
	// Pacman sprite
	if spr := g.sprPacman(); spr.Enabled {
		actor := g.Play.Pacman.Actor
		spr.Pos = actor.Pos.ActorToSpritePos()
		switch {
		case g.Play.Freeze.Has(FreezeEatGhost):
			spr.Tile = SpritetileInvisible
		case g.Play.Freeze.Has(FreezePrelude) || g.Play.Freeze.Has(FreezeReady):
			spr.Tile = SpritetilePacmanClosedMouth
		case g.Play.Freeze.Has(FreezeDead):
			if g.Play.PacmanEaten.After(now, PacmanEatenTicks) {
				g.sprAnimPacmanDeath(g.Play.PacmanEaten.Since(now) - PacmanEatenTicks)
			}
		default:
			g.sprAnimPacman(actor.Dir, actor.AnimTick)
		}
	}

	// ghost sprites
	for i := 0; i < int(NumGhosts); i++ {
		sprite := g.sprGhost(GhostType(i))
		if sprite.Enabled {
			ghost := g.Play.Ghost[i]
			sprite.Pos = ghost.Actor.Pos.ActorToSpritePos()
			switch {
			case g.Play.Freeze.Has(FreezeDead):
				if g.Play.PacmanEaten.After(now, PacmanEatenTicks) {
					sprite.Tile = SpritetileInvisible
				}
			case g.Play.Freeze.Has(FreezeWon):
				sprite.Tile = SpritetileInvisible
			default:
				switch ghost.State {
				case GhostStateEyes:
					if ghost.Eaten.Before(now, GhostEatenFreezeTicks) {
						// show the score number for the just-eaten ghost
						sprite.Tile = uint8(int(SpritetileScore200) +
							int(g.Play.NumGhostsEaten) - 1)
						sprite.Color = ColorGhostScore
					} else {
						g.sprAnimGhostEyes(GhostType(i), ghost.NextDir)
					}
				case GhostStateEnterHouse:
					g.sprAnimGhostEyes(GhostType(i), ghost.Actor.Dir)
				case GhostStateFrightened:
					g.sprAnimGhostFrightened(GhostType(i),
						ghost.Frightened.Since(now))
				default:
					g.sprAnimGhost(GhostType(i), ghost.NextDir,
						ghost.Actor.AnimTick)
				}
			}
		}
	}

	// bonus fruit sprite
	if g.Play.ActiveFruit == FruitNone {
		g.sprFruit().Enabled = false
	} else {
		spr := g.sprFruit()
		spr.Enabled = true
		spr.Pos = I2(13*TileWidth, 19*TileHeight+TileHeight/2)
		spr.Tile = fruitTilesColors[g.Play.ActiveFruit][1]
		spr.Color = fruitTilesColors[g.Play.ActiveFruit][2]
	}
}

// --- the Ebitengine renderer (pacman.c 2404-3124, SPEC H5/H6) ---
//
// The sokol version renders indexed pixels through a palette shader.
// Here the palette is baked into RGBA atlases at startup instead:
// one image per (tile, color) and (sprite, color) pair, drawn with
// FilterNearest. The board keeps the original's table + an offscreen
// image that is updated only where tiles changed.

// tileTextureWidth/Height mirror the C layout of the decoded pixel
// buffer: 256 tiles of 8px on the top row band, 64 sprites of 16px
// below (pacman.c TILE_TEXTURE_WIDTH / TILE_TEXTURE_HEIGHT).
const (
	tileTextureWidth  = 256 * TileWidth
	tileTextureHeight = TileHeight + SpriteHeight
)

// Renderer owns the Ebitengine-side drawing resources.
type Renderer struct {
	g *Game

	tilePixels [tileTextureHeight][tileTextureWidth]uint8

	tileImgs   [256][32]*ebiten.Image
	spriteImgs [64][32]*ebiten.Image

	board      *ebiten.Image
	boardValid bool
	lastVideo  [DisplayTilesY][DisplayTilesX]uint8
	lastColor  [DisplayTilesY][DisplayTilesX]uint8

	white *ebiten.Image
}

// gfxDecodeTile8x4 decodes one 8x4 half of a tile or sprite from the
// ROM bitplanes into the pixel-value buffer.
func (r *Renderer) gfxDecodeTile8x4(texX, texY uint32, tileBase []uint8,
	tileStride, tileOffset uint32, tileCode uint8) {
	for tx := uint32(0); tx < TileWidth; tx++ {
		ti := uint32(tileCode)*tileStride + tileOffset + (7 - tx)
		for ty := uint32(0); ty < TileHeight/2; ty++ {
			pHi := (tileBase[ti] >> (7 - ty)) & 1
			pLo := (tileBase[ti] >> (3 - ty)) & 1
			p := (pHi << 1) | pLo
			r.tilePixels[texY+ty][texX+tx] = p
		}
	}
}

func (r *Renderer) gfxDecodeTile(tileCode uint8) {
	x := uint32(tileCode) * TileWidth
	r.gfxDecodeTile8x4(x, 0, romTiles[:], 16, 8, tileCode)
	r.gfxDecodeTile8x4(x, TileHeight/2, romTiles[:], 16, 0, tileCode)
}

func (r *Renderer) gfxDecodeSprite(spriteCode uint8) {
	x0 := uint32(spriteCode) * SpriteWidth
	x1 := x0 + TileWidth
	y0 := uint32(TileHeight)
	y1 := y0 + TileHeight/2
	y2 := y1 + TileHeight/2
	y3 := y2 + TileHeight/2
	r.gfxDecodeTile8x4(x0, y0, romSprites[:], 64, 40, spriteCode)
	r.gfxDecodeTile8x4(x1, y0, romSprites[:], 64, 8, spriteCode)
	r.gfxDecodeTile8x4(x0, y1, romSprites[:], 64, 48, spriteCode)
	r.gfxDecodeTile8x4(x1, y1, romSprites[:], 64, 16, spriteCode)
	r.gfxDecodeTile8x4(x0, y2, romSprites[:], 64, 56, spriteCode)
	r.gfxDecodeTile8x4(x1, y2, romSprites[:], 64, 24, spriteCode)
	r.gfxDecodeTile8x4(x0, y3, romSprites[:], 64, 32, spriteCode)
	r.gfxDecodeTile8x4(x1, y3, romSprites[:], 64, 0, spriteCode)
}

func (r *Renderer) gfxDecodeTiles() {
	for tileCode := 0; tileCode < 256; tileCode++ {
		r.gfxDecodeTile(uint8(tileCode))
	}
	for spriteCode := 0; spriteCode < 64; spriteCode++ {
		r.gfxDecodeSprite(uint8(spriteCode))
	}
}

// gfxDecodeColorPalette decodes the hardware color palette into
// g.Gfx.ColorPalette (packed 0xAABBGGRR, alpha cleared for index 0 of
// each group of 4), as in pacman.c.
func (g *Game) gfxDecodeColorPalette() {
	var hwColors [32]uint32
	for i := 0; i < 32; i++ {
		rgb := romHWColors[i]
		rr := uint32((rgb>>0)&1)*0x21 + uint32((rgb>>1)&1)*0x47 + uint32((rgb>>2)&1)*0x97
		gg := uint32((rgb>>3)&1)*0x21 + uint32((rgb>>4)&1)*0x47 + uint32((rgb>>5)&1)*0x97
		bb := uint32((rgb>>6)&1)*0x47 + uint32((rgb>>7)&1)*0x97
		hwColors[i] = 0xFF000000 | (bb << 16) | (gg << 8) | rr
	}
	for i := 0; i < 256; i++ {
		g.Gfx.ColorPalette[i] = hwColors[romPalette[i]&0xF]
		if (i & 3) == 0 {
			g.Gfx.ColorPalette[i] &= 0x00FFFFFF
		}
	}
}

// paletteColor converts a packed palette entry to an RGBA color.
func paletteColor(packed uint32) color.RGBA {
	return color.RGBA{
		R: uint8(packed & 0xFF),
		G: uint8((packed >> 8) & 0xFF),
		B: uint8((packed >> 16) & 0xFF),
		A: uint8((packed >> 24) & 0xFF),
	}
}

// bakeAtlases renders every (tile, color) and (sprite, color) pair
// into its own small image, using the decoded palette.
func (r *Renderer) bakeAtlases() {
	pal := &r.g.Gfx.ColorPalette
	// tiles: 8x8 at (0,0) band of tilePixels
	tileBuf := make([]byte, TileWidth*TileHeight*4)
	for code := 0; code < 256; code++ {
		for c := 0; c < 32; c++ {
			for y := 0; y < TileHeight; y++ {
				for x := 0; x < TileWidth; x++ {
					pix := r.tilePixels[y][code*TileWidth+x]
					col := paletteColor(pal[c*4+int(pix)])
					o := (y*TileWidth + x) * 4
					tileBuf[o+0] = col.R
					tileBuf[o+1] = col.G
					tileBuf[o+2] = col.B
					tileBuf[o+3] = col.A
				}
			}
			img := ebiten.NewImage(TileWidth, TileHeight)
			img.WritePixels(tileBuf)
			r.tileImgs[code][c] = img
		}
	}
	// sprites: 16x16 at the (0, TileHeight) band of tilePixels
	sprBuf := make([]byte, SpriteWidth*SpriteHeight*4)
	for code := 0; code < 64; code++ {
		for c := 0; c < 32; c++ {
			for y := 0; y < SpriteHeight; y++ {
				for x := 0; x < SpriteWidth; x++ {
					pix := r.tilePixels[TileHeight+y][code*SpriteWidth+x]
					col := paletteColor(pal[c*4+int(pix)])
					o := (y*SpriteWidth + x) * 4
					sprBuf[o+0] = col.R
					sprBuf[o+1] = col.G
					sprBuf[o+2] = col.B
					sprBuf[o+3] = col.A
				}
			}
			img := ebiten.NewImage(SpriteWidth, SpriteHeight)
			img.WritePixels(sprBuf)
			r.spriteImgs[code][c] = img
		}
	}
}

// newRenderer performs the state-side gfx init (fade triggers
// disabled, fade fully set, sprites cleared) and builds the atlases.
func newRenderer(g *Game) *Renderer {
	g.Gfx.Fadein.Disable()
	g.Gfx.Fadeout.Disable()
	g.Gfx.Fade = 0xFF
	g.sprClear()
	r := &Renderer{g: g}
	r.gfxDecodeTiles()
	g.gfxDecodeColorPalette()
	r.bakeAtlases()
	r.board = ebiten.NewImage(DisplayPixelsX, DisplayPixelsY)
	r.white = ebiten.NewImage(1, 1)
	r.white.Fill(color.White)
	return r
}

// gfxFade advances the fade value from the fade triggers, as in
// pacman.c's gfx_fade (called once per Draw).
func (g *Game) gfxFade() {
	now := g.Timing.Tick
	if g.Gfx.Fadein.Between(now, 0, FadeTicks) {
		t := float32(g.Gfx.Fadein.Since(now)) / FadeTicks
		g.Gfx.Fade = uint8(255.0 * (1.0 - t))
	}
	if g.Gfx.Fadein.AfterOnce(now, FadeTicks) {
		g.Gfx.Fade = 0
	}
	if g.Gfx.Fadeout.Between(now, 0, FadeTicks) {
		t := float32(g.Gfx.Fadeout.Since(now)) / FadeTicks
		g.Gfx.Fade = uint8(255.0 * t)
	}
	if g.Gfx.Fadeout.AfterOnce(now, FadeTicks) {
		g.Gfx.Fade = 255
	}
}

// updateBoard redraws the changed tiles into the board offscreen.
func (r *Renderer) updateBoard() {
	g := r.g
	if !r.boardValid {
		r.board.Fill(color.Black)
	}
	for y := 0; y < DisplayTilesY; y++ {
		for x := 0; x < DisplayTilesX; x++ {
			tile := g.Gfx.VideoRAM[y][x]
			col := g.Gfx.ColorRAM[y][x] & 0x1F
			if r.boardValid && tile == r.lastVideo[y][x] && col == (r.lastColor[y][x]&0x1F) {
				continue
			}
			op := &ebiten.DrawImageOptions{Filter: ebiten.FilterNearest}
			op.GeoM.Translate(float64(x*TileWidth), float64(y*TileHeight))
			r.board.DrawImage(r.tileImgs[tile][col], op)
			r.lastVideo[y][x] = tile
			r.lastColor[y][x] = g.Gfx.ColorRAM[y][x]
		}
	}
	r.boardValid = true
}

// Draw renders one frame: board, sprites, debug markers, fade.
func (r *Renderer) Draw(screen *ebiten.Image) {
	g := r.g
	g.gfxFade()
	r.updateBoard()

	op := &ebiten.DrawImageOptions{Filter: ebiten.FilterNearest}
	screen.DrawImage(r.board, op)

	// sprites
	for i := 0; i < NumSprites; i++ {
		spr := g.Gfx.Sprite[i]
		if !spr.Enabled {
			continue
		}
		img := r.spriteImgs[spr.Tile][spr.Color&0x1F]
		sop := &ebiten.DrawImageOptions{Filter: ebiten.FilterNearest}
		sx, sy := 1.0, 1.0
		tx, ty := float64(spr.Pos.X), float64(spr.Pos.Y)
		if spr.FlipX {
			sx = -1
			tx += SpriteWidth
		}
		if spr.FlipY {
			sy = -1
			ty += SpriteHeight
		}
		sop.GeoM.Scale(sx, sy)
		sop.GeoM.Translate(tx, ty)
		screen.DrawImage(img, sop)
	}

	// debug markers (never enabled by the game itself)
	for i := 0; i < NumDebugMarkers; i++ {
		dbg := g.Gfx.DebugMarker[i]
		if !dbg.Enabled {
			continue
		}
		dop := &ebiten.DrawImageOptions{Filter: ebiten.FilterNearest}
		dop.GeoM.Translate(float64(dbg.TilePos.X*TileWidth),
			float64(dbg.TilePos.Y*TileHeight))
		screen.DrawImage(r.tileImgs[dbg.Tile][dbg.Color&0x1F], dop)
	}

	// fade: a black overlay whose opacity is the fade value
	if g.Gfx.Fade > 0 {
		fop := &ebiten.DrawImageOptions{Filter: ebiten.FilterNearest}
		fop.GeoM.Scale(DisplayPixelsX, DisplayPixelsY)
		fop.ColorScale.Scale(0, 0, 0, float32(g.Gfx.Fade)/255)
		screen.DrawImage(r.white, fop)
	}
}
```

## audio.go（303行、対応: pacman.c 638〜678、3125〜3388（音。pull 型の Synth は H3 による追加））

```go
// audio.go -- the Namco sound-board state and sound effects.
// Corresponds to pacman.c lines 638-678 (descriptions) and 3125-3388
// (logic). The sample output (the pull-type Synth) is at the end of
// this file, added in Phase 4.
package main

// sndClear clears all active sound effects (the voices go silent).
func (g *Game) sndClear() {
	for i := range g.Audio.Voice {
		g.Audio.Voice[i] = Voice{}
	}
	for i := range g.Audio.Sound {
		g.Audio.Sound[i] = Sound{}
	}
}

// sndStop stops a sound effect.
func (g *Game) sndStop(slot int32) {
	if slot < 0 || slot >= NumSounds {
		panic("sndStop: invalid slot")
	}
	for i := 0; i < NumVoices; i++ {
		if g.Audio.Sound[slot].Flags&(SoundFlags(1<<i)) != 0 {
			g.Audio.Voice[i] = Voice{}
		}
	}
	g.Audio.Sound[slot] = Sound{}
}

// sndStart starts a sound effect in a slot.
func (g *Game) sndStart(slot int32, desc SoundDesc) {
	if slot < 0 || slot >= NumSounds {
		panic("sndStart: invalid slot")
	}
	if desc.Data == nil && desc.Fn == nil {
		panic("sndStart: desc has neither data nor fn")
	}
	snd := &g.Audio.Sound[slot]
	*snd = Sound{}
	numVoices := 0
	for i := 0; i < NumVoices; i++ {
		if desc.Voice[i] {
			snd.Flags |= SoundFlags(1 << i)
			numVoices++
		}
	}
	if desc.Fn != nil {
		snd.Fn = desc.Fn
	} else {
		if numVoices == 0 {
			panic("sndStart: dump sound with no voices")
		}
		if len(desc.Data)%numVoices != 0 {
			panic("sndStart: dump size not a multiple of the voice count")
		}
		snd.Stride = uint32(numVoices)
		snd.NumTicks = uint32(len(desc.Data)) / snd.Stride
		snd.Data = desc.Data
	}
}

// sndTick is the sound system's 60 Hz tick function (called from
// Game.Tick before the scene tick, as in pacman.c's frame callback).
func (g *Game) sndTick() {
	for slot := 0; slot < NumSounds; slot++ {
		snd := &g.Audio.Sound[slot]
		skipIncrement := false
		if snd.Fn != nil {
			snd.Fn(g, int32(slot))
		} else if snd.Flags&SoundAllVoices != 0 {
			if snd.Data == nil {
				panic("sndTick: dump sound without data")
			}
			if snd.CurTick == snd.NumTicks {
				g.sndStop(int32(slot))
				skipIncrement = true
			} else {
				idx := int(snd.CurTick * snd.Stride)
				for i := 0; i < NumVoices; i++ {
					if snd.Flags&(SoundFlags(1<<i)) != 0 {
						voice := &g.Audio.Voice[i]
						val := snd.Data[idx]
						idx++
						voice.Frequency = val & ((1 << 20) - 1)
						voice.Waveform = uint8((val >> 24) & 7)
						voice.Volume = uint8((val >> 28) & 0xF)
					}
				}
			}
		}
		if !skipIncrement {
			snd.CurTick++
		}
	}
}

// --- procedural sound effects (pacman.c 3281-3388) ---

func sndFuncEatdot1(g *Game, slot int32) {
	snd := &g.Audio.Sound[slot]
	voice := &g.Audio.Voice[2]
	switch {
	case snd.CurTick == 0:
		voice.Volume = 12
		voice.Waveform = 2
		voice.Frequency = 0x1500
	case snd.CurTick == 5:
		g.sndStop(slot)
	default:
		voice.Frequency -= 0x0300
	}
}

func sndFuncEatdot2(g *Game, slot int32) {
	snd := &g.Audio.Sound[slot]
	voice := &g.Audio.Voice[2]
	switch {
	case snd.CurTick == 0:
		voice.Volume = 12
		voice.Waveform = 2
		voice.Frequency = 0x0700
	case snd.CurTick == 5:
		g.sndStop(slot)
	default:
		voice.Frequency += 0x300
	}
}

func sndFuncEatghost(g *Game, slot int32) {
	snd := &g.Audio.Sound[slot]
	voice := &g.Audio.Voice[2]
	switch {
	case snd.CurTick == 0:
		voice.Volume = 12
		voice.Waveform = 5
		voice.Frequency = 0
	case snd.CurTick == 32:
		g.sndStop(slot)
	default:
		voice.Frequency += 0x20
	}
}

func sndFuncEatfruit(g *Game, slot int32) {
	snd := &g.Audio.Sound[slot]
	voice := &g.Audio.Voice[2]
	switch {
	case snd.CurTick == 0:
		voice.Volume = 15
		voice.Waveform = 6
		voice.Frequency = 0x1600
	case snd.CurTick == 23:
		g.sndStop(slot)
	case snd.CurTick < 11:
		voice.Frequency -= 0x200
	default:
		voice.Frequency += 0x0200
	}
}

func sndFuncWeeooh(g *Game, slot int32) {
	snd := &g.Audio.Sound[slot]
	voice := &g.Audio.Voice[1]
	switch {
	case snd.CurTick == 0:
		voice.Volume = 6
		voice.Waveform = 6
		voice.Frequency = 0x1000
	case (snd.CurTick % 24) < 12:
		voice.Frequency += 0x0200
	default:
		voice.Frequency -= 0x0200
	}
}

func sndFuncFrightened(g *Game, slot int32) {
	snd := &g.Audio.Sound[slot]
	voice := &g.Audio.Voice[1]
	switch {
	case snd.CurTick == 0:
		voice.Volume = 10
		voice.Waveform = 4
		voice.Frequency = 0x0180
	case (snd.CurTick % 8) == 0:
		voice.Frequency = 0x0180
	default:
		voice.Frequency += 0x180
	}
}

// --- sound effect descriptions (pacman.c 638-678) ---

var sndPrelude = SoundDesc{
	Data:  sndDumpPrelude[:],
	Voice: [3]bool{true, true, false},
}

var sndDead = SoundDesc{
	Data:  sndDumpDead[:],
	Voice: [3]bool{false, false, true},
}

var sndEatdot1 = SoundDesc{Fn: sndFuncEatdot1, Voice: [3]bool{false, false, true}}
var sndEatdot2 = SoundDesc{Fn: sndFuncEatdot2, Voice: [3]bool{false, false, true}}
var sndEatghost = SoundDesc{Fn: sndFuncEatghost, Voice: [3]bool{false, false, true}}
var sndEatfruit = SoundDesc{Fn: sndFuncEatfruit, Voice: [3]bool{false, false, true}}
var sndWeeooh = SoundDesc{Fn: sndFuncWeeooh, Voice: [3]bool{false, true, false}}
var sndFrightened = SoundDesc{Fn: sndFuncFrightened, Voice: [3]bool{false, true, false}}

// --- the pull-type sample output (SPEC H3) ---
//
// The C version pushes samples from the frame callback; Ebitengine
// pulls them through an io.Reader on the audio thread. The register
// state is advanced by Game.Tick (sndTick, 60 Hz) on the game thread
// and read here as it stands -- the same lock-free relationship the
// original has with the sound hardware. One tick is exactly 735
// samples at 44,100 Hz.

const (
	SampleRate     = 44100
	SamplesPerTick = SampleRate / 60 // 735
	bytesPerSample = 4               // 16-bit stereo
)

// Synth converts the Namco voice state into a sample stream.
type Synth struct {
	g *Game

	voiceTickAccum  int32 // in thousandths of a 96 kHz tick
	voiceTickPeriod int32 // 96,000,000 / SampleRate = 2176

	buf []byte // one tick of generated samples
	pos int
}

// NewSynth creates a Synth reading the game's audio state.
func NewSynth(g *Game) *Synth {
	return &Synth{
		g:               g,
		voiceTickPeriod: 96_000_000 / SampleRate,
		buf:             make([]byte, SamplesPerTick*bytesPerSample),
		pos:             SamplesPerTick * bytesPerSample, // start empty
	}
}

// voiceTick updates the Namco sound generator once (96 kHz).
func (s *Synth) voiceTick() {
	for i := 0; i < NumVoices; i++ {
		voice := &s.g.Audio.Voice[i]
		voice.Counter += voice.Frequency
		waveIndex := ((uint32(voice.Waveform) << 5) |
			((voice.Counter >> 15) & 0x1F)) & 0xFF
		sample := (int32(romWavetable[waveIndex]&0xF) - 8) * int32(voice.Volume)
		voice.SampleAcc += float32(sample)
		voice.SampleDiv += 128
	}
}

// sampleTick computes one output sample from the voice averages.
func (s *Synth) sampleTick() float32 {
	var sm float32
	for i := 0; i < NumVoices; i++ {
		voice := &s.g.Audio.Voice[i]
		if voice.SampleDiv > 0 {
			sm += voice.SampleAcc / voice.SampleDiv
			voice.SampleAcc = 0
			voice.SampleDiv = 0
		}
	}
	return sm * 0.333333 * AudioVolume
}

// generate fills the internal buffer with one tick of samples.
func (s *Synth) generate() {
	for i := 0; i < SamplesPerTick; i++ {
		s.voiceTickAccum -= s.voiceTickPeriod
		for s.voiceTickAccum < 0 {
			s.voiceTickAccum += 1000
			s.voiceTick()
		}
		v := int16(s.sampleTick() * 32767)
		o := i * bytesPerSample
		s.buf[o+0] = byte(v)
		s.buf[o+1] = byte(v >> 8)
		s.buf[o+2] = byte(v)
		s.buf[o+3] = byte(v >> 8)
	}
	s.pos = 0
}

// Read implements io.Reader for the Ebitengine audio player.
func (s *Synth) Read(p []byte) (int, error) {
	n := 0
	for n < len(p) {
		if s.pos >= len(s.buf) {
			s.generate()
		}
		m := copy(p[n:], s.buf[s.pos:])
		s.pos += m
		n += m
	}
	return n, nil
}
```

## input.go（172行、対応: pacman.c 928〜943 の input_dir 相当 + H8 の追加（ゲームパッド・タッチ））

```go
// input.go -- merge keyboard, gamepad and touch into the game's
// InputState (SPEC H8). The rules only ever see the resolved input;
// which device produced it is known only here.
//
//   - keyboard: arrow keys and WASD, held state is the intent
//   - gamepad: first pad, standard layout D-pad and left stick
//     (deadzone 0.5, the larger axis wins)
//   - touch: swipe with a latch -- the direction persists until the
//     next swipe; a tap counts as "any key"
//   - no mouse, no vibration (decided 2026-11-20)
//
// Held directions are resolved with the original's priority
// (up, down, right, left); the latched touch direction is used only
// when nothing is held. The F key toggles fullscreen, as in the
// original. Like the original's event callback, nothing is written
// while input is disabled.
package main

import (
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/inpututil"
)

const (
	touchSwipeThreshold = 24 // logical pixels, about 3 tiles
	stickDeadzone       = 0.5
)

// InputReader holds the cross-tick input state (the touch latch and
// the active swipe).
type InputReader struct {
	latched  Dir
	hasLatch bool
	activeID ebiten.TouchID
	tracking bool
	swiped   bool
	originX  int
	originY  int
}

// Read polls the devices and writes the resolved input.
func (r *InputReader) Read(in *InputState) {
	if !in.Enabled {
		return
	}

	// fullscreen toggle (the original's F key handling)
	if inpututil.IsKeyJustPressed(ebiten.KeyF) {
		ebiten.SetFullscreen(!ebiten.IsFullscreen())
	}

	// --- held directions: keyboard ---
	up := ebiten.IsKeyPressed(ebiten.KeyArrowUp) || ebiten.IsKeyPressed(ebiten.KeyW)
	down := ebiten.IsKeyPressed(ebiten.KeyArrowDown) || ebiten.IsKeyPressed(ebiten.KeyS)
	right := ebiten.IsKeyPressed(ebiten.KeyArrowRight) || ebiten.IsKeyPressed(ebiten.KeyD)
	left := ebiten.IsKeyPressed(ebiten.KeyArrowLeft) || ebiten.IsKeyPressed(ebiten.KeyA)

	// --- held directions: gamepad (first pad, standard layout) ---
	padAny := false
	var ids []ebiten.GamepadID
	ids = ebiten.AppendGamepadIDs(ids)
	if len(ids) > 0 {
		id := ids[0]
		if ebiten.IsStandardGamepadLayoutAvailable(id) {
			up = up || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftTop)
			down = down || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftBottom)
			right = right || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftRight)
			left = left || ebiten.IsStandardGamepadButtonPressed(id, ebiten.StandardGamepadButtonLeftLeft)
			x := ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickHorizontal)
			y := ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickVertical)
			if absF(x) > absF(y) {
				if x < -stickDeadzone {
					left = true
				} else if x > stickDeadzone {
					right = true
				}
			} else {
				if y < -stickDeadzone {
					up = true
				} else if y > stickDeadzone {
					down = true
				}
			}
			// any standard button just pressed counts as "any key"
			for b := ebiten.StandardGamepadButton(0); b < ebiten.StandardGamepadButtonMax; b++ {
				if inpututil.IsStandardGamepadButtonJustPressed(id, b) {
					padAny = true
					break
				}
			}
		}
	}

	// --- touch: swipe with latch, tap is "any key" ---
	tap := false
	var justIDs []ebiten.TouchID
	justIDs = inpututil.AppendJustPressedTouchIDs(justIDs)
	for _, id := range justIDs {
		if !r.tracking {
			r.tracking = true
			r.swiped = false
			r.activeID = id
			r.originX, r.originY = ebiten.TouchPosition(id)
		}
	}
	if r.tracking {
		if inpututil.IsTouchJustReleased(r.activeID) {
			if !r.swiped {
				tap = true
			}
			r.tracking = false
		} else {
			x, y := ebiten.TouchPosition(r.activeID)
			dx, dy := x-r.originX, y-r.originY
			if max(abs(dx), abs(dy)) >= touchSwipeThreshold {
				if abs(dx) > abs(dy) {
					if dx > 0 {
						r.latched = DirRight
					} else {
						r.latched = DirLeft
					}
				} else {
					if dy > 0 {
						r.latched = DirDown
					} else {
						r.latched = DirUp
					}
				}
				r.hasLatch = true
				r.swiped = true
				// advance the origin so a long swipe keeps
				// producing directions
				r.originX, r.originY = x, y
			}
		}
	}

	// --- resolve: held first (original priority), then the latch ---
	if !(up || down || right || left) && r.hasLatch {
		switch r.latched {
		case DirUp:
			up = true
		case DirDown:
			down = true
		case DirRight:
			right = true
		case DirLeft:
			left = true
		}
	}
	in.Up, in.Down, in.Right, in.Left = up, down, right, left
	in.Esc = ebiten.IsKeyPressed(ebiten.KeyEscape)

	// --- "any key": key edges, pad button edges, taps ---
	var keys []ebiten.Key
	keys = inpututil.AppendJustPressedKeys(keys)
	in.Anykey = len(keys) > 0 || padAny || tap
}

func abs(v int) int {
	if v < 0 {
		return -v
	}
	return v
}

func absF(v float64) float64 {
	if v < 0 {
		return -v
	}
	return v
}
```

## main.go（104行、対応: pacman.c 716〜825（入り口。Ebitengine の Game 実装））

```go
// main.go -- entry point and ebiten wiring.
// Corresponds to pacman.c lines 716-825 (sokol_main and callbacks),
// with the sokol accumulator replaced by Ebitengine's fixed TPS
// (SPEC H1/H2): one Update is one tick.
package main

import (
	"fmt"
	"os"
	"strconv"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/audio"
)

// app is the ebiten game object. The game logic lives in Game; the
// renderer, input reader and synth are attached here so the logic
// files never import ebiten.
type app struct {
	game     *Game
	renderer *Renderer
	reader   *InputReader
	synth    *Synth
	player   *audio.Player

	frames      int
	smokeFrames int  // >0: exit after this many updates (headless smoke)
	smokePlay   bool // smoke: press "any key" at frame 120 to start a game
}

func (a *app) Update() error {
	if a.reader != nil {
		a.reader.Read(&a.game.Input)
	}
	if a.smokePlay && a.frames == 120 {
		a.game.Input.Anykey = true
	}
	a.game.Tick()
	a.game.Input.Anykey = false
	a.frames++
	if a.smokeFrames > 0 && a.frames >= a.smokeFrames {
		fmt.Printf("smoke: %d frames done, scene=%v score=%d tick=%d\n",
			a.frames, a.game.Scene, a.game.Play.Score, a.game.Timing.Tick)
		return ebiten.Termination
	}
	return nil
}

func (a *app) Draw(screen *ebiten.Image) {
	a.renderer.Draw(screen)
}

func (a *app) Layout(outsideWidth, outsideHeight int) (int, int) {
	return DisplayPixelsX, DisplayPixelsY
}

// setupAudio attaches the synth to an Ebitengine audio player.
// Audio is optional (Phase 0 finding): creating a player initializes
// the audio driver, and on a machine without an audio device that
// error makes RunGame return immediately. Set PACMAN_AUDIO=off to
// skip audio entirely on such machines.
func setupAudio(a *app) {
	if os.Getenv("PACMAN_AUDIO") == "off" {
		return
	}
	a.synth = NewSynth(a.game)
	ctx := audio.NewContext(SampleRate)
	player, err := ctx.NewPlayer(a.synth)
	if err != nil {
		fmt.Fprintln(os.Stderr, "audio unavailable, continuing silently:", err)
		a.synth = nil
		return
	}
	a.player = player
	player.Play()
}

func main() {
	a := &app{game: NewGame()}
	a.renderer = newRenderer(a.game)
	a.reader = &InputReader{}
	setupAudio(a)
	if v := os.Getenv("PACMAN_SMOKE_FRAMES"); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			a.smokeFrames = n
		}
	}
	a.smokePlay = os.Getenv("PACMAN_SMOKE_PLAY") != ""

	ebiten.SetTPS(60)
	ebiten.SetWindowSize(DisplayPixelsX*2, DisplayPixelsY*2)
	ebiten.SetWindowTitle("pacman.c")
	ebiten.SetWindowResizingMode(ebiten.WindowResizingModeEnabled)
	if err := ebiten.RunGame(a); err != nil && err != ebiten.Termination {
		fmt.Fprintln(os.Stderr, err)
		if a.player != nil {
			fmt.Fprintln(os.Stderr,
				"hint: if this is the audio initialization error, "+
					"this machine may have no audio device; "+
					"try PACMAN_AUDIO=off")
		}
		os.Exit(1)
	}
}
```

## data.go（608行、対応: pacman.c 3389〜4303（ROM データ、生成ファイル））

```go
// data.go -- ROM data extracted mechanically from pacman.c (lines 3389-4303).
// Generated by tools/extract.go. Do not edit by hand.

package main

var romTiles = [4096]uint8{
	0xCC, 0xEE, 0x11, 0x11, 0x33, 0xEE, 0xCC, 0x00, 0x11, 0x33, 0x66, 0x44, 0x44, 0x33, 0x11, 0x00,
	0x11, 0x11, 0xFF, 0xFF, 0x11, 0x11, 0x00, 0x00, 0x00, 0x00, 0x77, 0x77, 0x22, 0x00, 0x00, 0x00,
	0x11, 0x99, 0xDD, 0xDD, 0xFF, 0x77, 0x33, 0x00, 0x33, 0x77, 0x55, 0x44, 0x44, 0x66, 0x22, 0x00,
	0x66, 0xFF, 0x99, 0x99, 0x99, 0x33, 0x22, 0x00, 0x44, 0x66, 0x77, 0x55, 0x44, 0x44, 0x00, 0x00,
	0x44, 0xFF, 0xFF, 0x44, 0x44, 0xCC, 0xCC, 0x00, 0x00, 0x77, 0x77, 0x66, 0x33, 0x11, 0x00, 0x00,
	0xEE, 0xFF, 0x11, 0x11, 0x11, 0x33, 0x22, 0x00, 0x00, 0x55, 0x55, 0x55, 0x55, 0x77, 0x77, 0x00,
	0x66, 0xFF, 0x99, 0x99, 0x99, 0xFF, 0xEE, 0x00, 0x00, 0x44, 0x44, 0x44, 0x66, 0x33, 0x11, 0x00,
	0x00, 0x00, 0x88, 0xFF, 0x77, 0x00, 0x00, 0x00, 0x66, 0x77, 0x55, 0x44, 0x44, 0x66, 0x66, 0x00,
	0x66, 0x77, 0xDD, 0xDD, 0x99, 0x99, 0x66, 0x00, 0x00, 0x33, 0x44, 0x44, 0x55, 0x77, 0x33, 0x00,
	0xCC, 0xEE, 0xBB, 0x99, 0x99, 0x99, 0x00, 0x00, 0x33, 0x77, 0x44, 0x44, 0x44, 0x77, 0x33, 0x00,
	0xFF, 0xFF, 0x44, 0x44, 0x44, 0xFF, 0xFF, 0x00, 0x11, 0x33, 0x66, 0x44, 0x66, 0x33, 0x11, 0x00,
	0x66, 0xFF, 0x99, 0x99, 0x99, 0xFF, 0xFF, 0x00, 0x33, 0x77, 0x44, 0x44, 0x44, 0x77, 0x77, 0x00,
	0x22, 0x33, 0x11, 0x11, 0x33, 0xEE, 0xCC, 0x00, 0x22, 0x66, 0x44, 0x44, 0x66, 0x33, 0x11, 0x00,
	0xCC, 0xEE, 0x33, 0x11, 0x11, 0xFF, 0xFF, 0x00, 0x11, 0x33, 0x66, 0x44, 0x44, 0x77, 0x77, 0x00,
	0x11, 0x99, 0x99, 0x99, 0xFF, 0xFF, 0x00, 0x00, 0x44, 0x44, 0x44, 0x44, 0x77, 0x77, 0x00, 0x00,
	0x00, 0x88, 0x88, 0x88, 0x88, 0xFF, 0xFF, 0x00, 0x44, 0x44, 0x44, 0x44, 0x44, 0x77, 0x77, 0x00,
	0x00, 0x00, 0x00, 0x08, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x08, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x08, 0x0C, 0x0C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x03, 0x01, 0x00, 0x00,
	0x00, 0x00, 0x08, 0x0C, 0x0C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x03, 0x01, 0x00, 0x00,
	0x0C, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x0C, 0x03, 0x07, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x03,
	0x0C, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x0C, 0x03, 0x07, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x03,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x77, 0xFF, 0xFF, 0xFF, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33,
	0xEE, 0xCC, 0xCC, 0x88, 0x88, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0x00, 0x00, 0x00, 0xCC, 0xEE, 0xFF, 0xFF, 0xFF,
	0x88, 0x88, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x77, 0x77, 0x33, 0x22, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x66, 0x66, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xDD, 0x00, 0xEE, 0xDD, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xDD, 0x00, 0xEE, 0xDD, 0x00, 0x00,
	0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x77, 0xFF, 0xCC, 0xCC, 0xCC, 0xCC, 0xFF, 0xFF,
	0xBB, 0xBB, 0xBB, 0xBB, 0xFF, 0xFF, 0x00, 0x00, 0xDD, 0xDD, 0xDD, 0xDD, 0xDD, 0x11, 0x00, 0x00,
	0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0xCC, 0xCC, 0xFF, 0xFF, 0x00, 0x00, 0x77, 0xFF,
	0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x77, 0xFF, 0xCC, 0xCC, 0xFF, 0xFF,
	0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0xFF, 0xEE, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xFF, 0x77,
	0x33, 0x33, 0x33, 0x33, 0xFF, 0xEE, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xFF, 0x77, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x77, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x88, 0xCC, 0x22, 0x22, 0x66, 0xCC, 0x88, 0x00, 0x33, 0x77, 0xCC, 0x88, 0x88, 0x77, 0x33, 0x00,
	0x22, 0x22, 0xEE, 0xEE, 0x22, 0x22, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x44, 0x00, 0x00, 0x00,
	0x22, 0x22, 0xAA, 0xAA, 0xEE, 0xEE, 0x66, 0x00, 0x66, 0xFF, 0xBB, 0x99, 0x99, 0xCC, 0x44, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0x66, 0x44, 0x00, 0x88, 0xDD, 0xFF, 0xBB, 0x99, 0x88, 0x00, 0x00,
	0x88, 0xEE, 0xEE, 0x88, 0x88, 0x88, 0x88, 0x00, 0x00, 0xFF, 0xFF, 0xCC, 0x66, 0x33, 0x11, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0x66, 0x44, 0x00, 0x11, 0xBB, 0xAA, 0xAA, 0xAA, 0xEE, 0xEE, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0xEE, 0xCC, 0x00, 0x00, 0x99, 0x99, 0x99, 0xDD, 0x77, 0x33, 0x00,
	0x00, 0x00, 0x00, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0xCC, 0xEE, 0xBB, 0x99, 0x88, 0xCC, 0xCC, 0x00,
	0xCC, 0xEE, 0xAA, 0xAA, 0x22, 0x22, 0xCC, 0x00, 0x00, 0x66, 0x99, 0x99, 0xBB, 0xFF, 0x66, 0x00,
	0x88, 0xCC, 0x66, 0x22, 0x22, 0x22, 0x00, 0x00, 0x77, 0xFF, 0x99, 0x99, 0x99, 0xFF, 0x66, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x88, 0x44, 0x22, 0x00, 0x88, 0x44, 0x22, 0x11, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x11, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88,
	0xFF, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0xFF,
	0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xEE, 0xEE, 0x88, 0x88, 0x88, 0xEE, 0xEE, 0x00, 0x33, 0x77, 0xCC, 0x88, 0xCC, 0x77, 0x33, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0xEE, 0xEE, 0x00, 0x66, 0xFF, 0x99, 0x99, 0x99, 0xFF, 0xFF, 0x00,
	0x44, 0x66, 0x22, 0x22, 0x66, 0xCC, 0x88, 0x00, 0x44, 0xCC, 0x88, 0x88, 0xCC, 0x77, 0x33, 0x00,
	0x88, 0xCC, 0x66, 0x22, 0x22, 0xEE, 0xEE, 0x00, 0x33, 0x77, 0xCC, 0x88, 0x88, 0xFF, 0xFF, 0x00,
	0x22, 0x22, 0x22, 0x22, 0xEE, 0xEE, 0x00, 0x00, 0x88, 0x99, 0x99, 0x99, 0xFF, 0xFF, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0x00, 0x88, 0x99, 0x99, 0x99, 0x99, 0xFF, 0xFF, 0x00,
	0xEE, 0xEE, 0x22, 0x22, 0x66, 0xCC, 0x88, 0x00, 0x99, 0x99, 0x99, 0x88, 0xCC, 0x77, 0x33, 0x00,
	0xEE, 0xEE, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0x00, 0xFF, 0xFF, 0x11, 0x11, 0x11, 0xFF, 0xFF, 0x00,
	0x22, 0x22, 0xEE, 0xEE, 0x22, 0x22, 0x00, 0x00, 0x88, 0x88, 0xFF, 0xFF, 0x88, 0x88, 0x00, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0x66, 0x44, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x22, 0x66, 0xEE, 0xCC, 0x88, 0xEE, 0xEE, 0x00, 0x88, 0xCC, 0x66, 0x33, 0x11, 0xFF, 0xFF, 0x00,
	0x22, 0x22, 0x22, 0x22, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00,
	0xEE, 0xEE, 0x00, 0x88, 0x00, 0xEE, 0xEE, 0x00, 0xFF, 0xFF, 0x77, 0x33, 0x77, 0xFF, 0xFF, 0x00,
	0xEE, 0xEE, 0xCC, 0x88, 0x00, 0xEE, 0xEE, 0x00, 0xFF, 0xFF, 0x11, 0x33, 0x77, 0xFF, 0xFF, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0xEE, 0xCC, 0x00, 0x77, 0xFF, 0x88, 0x88, 0x88, 0xFF, 0x77, 0x00,
	0x00, 0x88, 0x88, 0x88, 0x88, 0xEE, 0xEE, 0x00, 0x77, 0xFF, 0x88, 0x88, 0x88, 0xFF, 0xFF, 0x00,
	0xAA, 0xCC, 0xEE, 0xAA, 0x22, 0xEE, 0xCC, 0x00, 0x77, 0xFF, 0x88, 0x88, 0x88, 0xFF, 0x77, 0x00,
	0x22, 0x66, 0xEE, 0xCC, 0x88, 0xEE, 0xEE, 0x00, 0x77, 0xFF, 0x99, 0x88, 0x88, 0xFF, 0xFF, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0x66, 0x44, 0x00, 0x00, 0x55, 0xDD, 0x99, 0x99, 0xFF, 0x66, 0x00,
	0x00, 0x00, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0xFF, 0xFF, 0x88, 0x88, 0x00, 0x00,
	0xCC, 0xEE, 0x22, 0x22, 0x22, 0xEE, 0xCC, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00,
	0x00, 0x88, 0xCC, 0xEE, 0xCC, 0x88, 0x00, 0x00, 0xFF, 0xFF, 0x11, 0x00, 0x11, 0xFF, 0xFF, 0x00,
	0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0x00, 0xFF, 0xFF, 0x11, 0x33, 0x11, 0xFF, 0xFF, 0x00,
	0x66, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x66, 0x00, 0xCC, 0xEE, 0x77, 0x33, 0x77, 0xEE, 0xCC, 0x00,
	0x00, 0x00, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xFF, 0x11, 0x11, 0xFF, 0xEE, 0x00, 0x00,
	0x22, 0x22, 0x22, 0xAA, 0xEE, 0xEE, 0x66, 0x00, 0xCC, 0xEE, 0xFF, 0xBB, 0x99, 0x88, 0x88, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x88, 0x22, 0x00, 0x00, 0x00, 0xCC, 0xEE, 0xFF, 0x33, 0x00, 0x00, 0x00,
	0xCC, 0x22, 0x11, 0x55, 0x55, 0x99, 0x22, 0xCC, 0x33, 0x44, 0x88, 0xAA, 0xAA, 0x99, 0x44, 0x33,
	0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0x88, 0xEE, 0x22, 0x22, 0x00, 0x11, 0x22, 0x22, 0x22, 0x33,
	0xAA, 0xAA, 0xAA, 0x22, 0x00, 0x00, 0x00, 0xEE, 0x22, 0x22, 0x22, 0x11, 0x00, 0x22, 0x22, 0x33,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22,
	0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x33, 0x77, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x33, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0x00,
	0x33, 0x33, 0x77, 0x77, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
	0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x33, 0x33, 0x33, 0x33, 0x33, 0x77, 0x77, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x33, 0x33, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0x00, 0x00, 0x00,
	0x33, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCE, 0xEE, 0xEE, 0xEE, 0x66, 0x22, 0x22, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x22, 0xCC, 0x00, 0x22, 0xEE, 0x22, 0x00, 0x00, 0x88, 0x77, 0x00, 0x00, 0xFF, 0x44, 0x00, 0x00,
	0x22, 0xCC, 0x00, 0xCC, 0x22, 0x22, 0x22, 0x44, 0x88, 0x77, 0x00, 0x88, 0xDD, 0xAA, 0x88, 0x88,
	0x22, 0xCC, 0x00, 0xCC, 0x22, 0x22, 0x22, 0x44, 0x88, 0x77, 0x00, 0x99, 0xAA, 0xAA, 0xAA, 0xEE,
	0x22, 0xCC, 0x00, 0x00, 0x00, 0xEE, 0x00, 0x00, 0x88, 0x77, 0x00, 0xCC, 0xBB, 0x88, 0x88, 0xCC,
	0x00, 0xCC, 0x22, 0x22, 0xCC, 0x00, 0xCC, 0x22, 0x00, 0x77, 0x88, 0x88, 0x77, 0x00, 0x77, 0x88,
	0xCC, 0x22, 0x22, 0xCC, 0x00, 0x22, 0xEE, 0x22, 0x77, 0x88, 0x88, 0x77, 0x00, 0x00, 0xFF, 0x44,
	0x66, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0x66, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xCC, 0x22, 0x22, 0xCC, 0x00, 0x22, 0x22, 0xAA, 0x77, 0x88, 0x88, 0x77, 0x00, 0x66, 0x99, 0x88,
	0x22, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xCC, 0x22, 0x22, 0xCC, 0x00, 0xCC, 0x22, 0x22, 0x77, 0x88, 0x88, 0x77, 0x00, 0x88, 0xDD, 0xAA,
	0x22, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xCC, 0x22, 0x22, 0xCC, 0x00, 0xCC, 0x22, 0x22, 0x77, 0x88, 0x88, 0x77, 0x00, 0x99, 0xAA, 0xAA,
	0x22, 0xCC, 0x00, 0xCC, 0x22, 0x22, 0xCC, 0x00, 0x88, 0x77, 0x00, 0x77, 0x88, 0x88, 0x77, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x77, 0x88,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0xC0, 0x20, 0x90, 0x80, 0x00, 0x00, 0x30, 0x30, 0x10, 0x10, 0x00, 0x00,
	0x41, 0x21, 0x12, 0x03, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x08, 0x0C, 0x0C, 0x8C, 0x0C, 0x00, 0x00, 0x00, 0x07, 0x0F, 0x0F, 0xC3, 0x1F,
	0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0x08, 0x0F, 0x2F, 0x4F, 0x0E, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x07, 0x4F, 0x0F, 0xA7, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x10, 0x10,
	0xD3, 0x87, 0x97, 0x0F, 0x2F, 0x07, 0x00, 0x00, 0x33, 0x10, 0x10, 0x10, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x08, 0x00, 0x00, 0x00, 0x08, 0x0E, 0x8E, 0x1F, 0x0F,
	0x0C, 0x08, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4F, 0x1F, 0x0F, 0x4F, 0x0E, 0x08, 0x00, 0x00,
	0x00, 0x00, 0x01, 0x03, 0x87, 0x87, 0x87, 0x47, 0x00, 0x00, 0x00, 0x10, 0x10, 0x30, 0x30, 0x10,
	0xEF, 0x47, 0x07, 0x07, 0x03, 0x01, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x08, 0x08, 0x0C, 0x0C, 0x0C, 0x00, 0x00, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0C, 0x0C, 0x0C, 0x08, 0x08, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x01, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x02,
	0x0F, 0x0B, 0x0C, 0x0F, 0x01, 0x00, 0x00, 0x00, 0x02, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x0C, 0x68, 0x68, 0x68, 0x6E, 0x6E, 0x00, 0x00, 0x03, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x68, 0x68, 0x68, 0x68, 0x68, 0x0C, 0x00, 0x00, 0x0F, 0x0F, 0x07, 0x0C, 0x0F, 0x03, 0x00, 0x00,
	0x00, 0x00, 0x07, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 0x20,
	0x87, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x10, 0x00, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x08, 0x0C, 0x0C, 0x0C, 0x00, 0x00, 0x0C, 0x0F, 0xCF, 0x2F, 0x0F, 0x0F,
	0x08, 0x0C, 0x0C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0C, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x30, 0x52, 0x61, 0xF1, 0xBC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x02, 0x03,
	0xD2, 0x63, 0x52, 0x30, 0x00, 0x00, 0x00, 0x00, 0x02, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x80, 0x48, 0x84, 0xC2, 0xE0, 0x00, 0x00, 0xE0, 0xB4, 0x7C, 0xE1, 0x5B, 0xA5,
	0x68, 0x84, 0xC0, 0x80, 0x00, 0x00, 0x00, 0x00, 0xF5, 0xE1, 0x5A, 0xBE, 0xE0, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x0F, 0x33, 0x31, 0x71, 0xF3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF0, 0xF3, 0x71, 0x31, 0x33, 0x0F, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x0C, 0x8E, 0xCF, 0x88,
	0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x88, 0xCF, 0x8E, 0x0C, 0x08, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xE0, 0xF1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x10, 0x20,
	0xE0, 0xF1, 0xE0, 0xE0, 0x00, 0x00, 0x00, 0x00, 0x20, 0x20, 0x10, 0x10, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0xDD,
	0x22, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xFF, 0xEF, 0x67, 0x77, 0x33, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x11, 0x23, 0x67, 0x77, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x79, 0x69, 0x0F, 0x1F, 0xFF, 0xFF, 0x33, 0x00,
	0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x33, 0x79, 0x69, 0x0F, 0x1F, 0xFF, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0xCC, 0x88, 0x00, 0x88, 0xCC, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0x88, 0x00, 0x88, 0xCC, 0xCC, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xFF, 0xF0, 0xF0, 0xF7, 0x88, 0x00, 0x00, 0x00, 0x00, 0x33, 0x74, 0x74, 0xF8, 0xF9, 0xF9, 0xF9,
	0x00, 0x00, 0x00, 0x88, 0xF7, 0xF0, 0xF0, 0xFF, 0xF9, 0xF9, 0xF9, 0xF8, 0x74, 0x74, 0x33, 0x00,
	0xFF, 0xF0, 0xF0, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xF0, 0xF0, 0xFF, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0xFF, 0xF0, 0xF0, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xF0, 0xF0, 0xFF,
	0x00, 0xCC, 0xE2, 0xE2, 0xF1, 0xF9, 0xF9, 0xF9, 0xFF, 0xF0, 0xF0, 0xFE, 0x11, 0x00, 0x00, 0x00,
	0xF9, 0xF9, 0xF9, 0xF1, 0xE2, 0xE2, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x11, 0xFE, 0xF0, 0xF0, 0xFF,
	0xFF, 0xF0, 0xF0, 0xF0, 0xF0, 0xF8, 0xF8, 0xF8, 0xFF, 0xF0, 0xF0, 0xFE, 0x11, 0x00, 0x00, 0x00,
	0xF8, 0xF8, 0xF8, 0xF0, 0xF0, 0xF0, 0xF0, 0xFF, 0x00, 0x00, 0x00, 0x11, 0xFE, 0xF0, 0xF0, 0xFF,
	0xFF, 0xF0, 0xF0, 0xF7, 0x88, 0x00, 0x00, 0x00, 0xFF, 0xF0, 0xF0, 0xF0, 0xF0, 0xF1, 0xF1, 0xF1,
	0x00, 0x00, 0x00, 0x88, 0xF7, 0xF0, 0xF0, 0xFF, 0xF1, 0xF1, 0xF1, 0xF0, 0xF0, 0xF0, 0xF0, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9,
	0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0xE2, 0xE2, 0xF1, 0xF1, 0xF1, 0xF1,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF1, 0xF1, 0xF1, 0xF1, 0xE2, 0xE2, 0xCC, 0x00,
	0x00, 0x33, 0x74, 0x74, 0xF8, 0xF8, 0xF8, 0xF8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF8, 0xF8, 0xF8, 0xF8, 0x74, 0x74, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1, 0xF1,
	0x00, 0x00, 0x00, 0x00, 0x33, 0x74, 0xF8, 0xF8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF8, 0xF8, 0x74, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0xFF, 0xF0, 0xF0, 0xF0, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xF0, 0xF0, 0xF0,
	0xF0, 0xF0, 0xF0, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xF0, 0xF0, 0xF0, 0xFF, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0xE2, 0xF1, 0xF1,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF1, 0xF1, 0xE2, 0xCC, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0xFF, 0xF8, 0xF8, 0xF9, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF9, 0xF8, 0xF8, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xF1, 0xF1, 0xF9,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF9, 0xF1, 0xF1, 0xFF, 0x00, 0x00, 0x00, 0x00,
	0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xFF, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0xF9, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x88, 0xF7, 0xF0, 0xF0, 0xF0, 0xF1, 0xF1, 0xF1, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0,
	0xF0, 0xF0, 0xF0, 0xF7, 0x88, 0x00, 0x00, 0x00, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF1, 0xF1, 0xF1,
	0xF8, 0xF8, 0xF8, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0x00, 0x00, 0x00, 0x11, 0xFE, 0xF0, 0xF0, 0xF0,
	0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF8, 0xF8, 0xF8, 0xF0, 0xF0, 0xF0, 0xFE, 0x11, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x33, 0x74, 0xF8, 0xF8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF8, 0xF8, 0x74, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0xE2, 0xF1, 0xF1,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF1, 0xF1, 0xE2, 0xCC, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x88, 0xF7, 0xF0, 0xF0, 0xF0, 0xF9, 0xF9, 0xF9, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8,
	0xF0, 0xF0, 0xF0, 0xF7, 0x88, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF9, 0xF9, 0xF9,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
}

var romSprites = [4096]uint8{
	0x00, 0x00, 0x00, 0x08, 0x0C, 0x0C, 0x8C, 0x0C, 0x00, 0x00, 0x30, 0x30, 0x10, 0x10, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0xC0, 0x20, 0x90, 0x80, 0x00, 0x00, 0x00, 0x07, 0x0F, 0x0F, 0xC3, 0x1F,
	0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x41, 0x21, 0x12, 0x03, 0x03, 0x01, 0x00, 0x00, 0x07, 0x08, 0x0F, 0x2F, 0x4F, 0x0E, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x10, 0x10,
	0x00, 0x00, 0x00, 0x07, 0x4F, 0x0F, 0xA7, 0x87, 0x00, 0x00, 0x00, 0x08, 0x0E, 0x8E, 0x1F, 0x0F,
	0x0C, 0x08, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x10, 0x10, 0x10, 0x00, 0x00, 0x00, 0x00,
	0xD3, 0x87, 0x97, 0x0F, 0x2F, 0x07, 0x00, 0x00, 0x4F, 0x1F, 0x0F, 0x4F, 0x0E, 0x08, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x08, 0x08, 0x0C, 0x0C, 0x0C, 0x00, 0x00, 0x00, 0x10, 0x10, 0x30, 0x30, 0x10,
	0x00, 0x00, 0x01, 0x03, 0x87, 0x87, 0x87, 0x47, 0x00, 0x00, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0C, 0x0C, 0x0C, 0x08, 0x08, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xEF, 0x47, 0x07, 0x07, 0x03, 0x01, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x00, 0x00,
	0x00, 0x00, 0x0C, 0x68, 0x68, 0x68, 0x6E, 0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x02,
	0x00, 0x00, 0x00, 0x01, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x03, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x68, 0x68, 0x68, 0x68, 0x68, 0x0C, 0x00, 0x00, 0x02, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x0F, 0x0B, 0x0C, 0x0F, 0x01, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x07, 0x0C, 0x0F, 0x03, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x08, 0x0C, 0x0C, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 0x20,
	0x00, 0x00, 0x07, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x0C, 0x0F, 0xCF, 0x2F, 0x0F, 0x0F,
	0x08, 0x0C, 0x0C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00,
	0x87, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0C, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x80, 0x48, 0x84, 0xC2, 0xE0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x02, 0x03,
	0x00, 0x00, 0x00, 0x30, 0x52, 0x61, 0xF1, 0xBC, 0x00, 0x00, 0xE0, 0xB4, 0x7C, 0xE1, 0x5B, 0xA5,
	0x68, 0x84, 0xC0, 0x80, 0x00, 0x00, 0x00, 0x00, 0x02, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xD2, 0x63, 0x52, 0x30, 0x00, 0x00, 0x00, 0x00, 0xF5, 0xE1, 0x5A, 0xBE, 0xE0, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x0F, 0x33, 0x31, 0x71, 0xF3, 0x00, 0x00, 0x00, 0x08, 0x0C, 0x8E, 0xCF, 0x88,
	0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xF0, 0xF3, 0x71, 0x31, 0x33, 0x0F, 0x00, 0x00, 0xFF, 0x88, 0xCF, 0x8E, 0x0C, 0x08, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x10, 0x20,
	0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0xE0, 0xF1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0xDD,
	0x22, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x20, 0x10, 0x10, 0x00, 0x00, 0x00, 0x00,
	0xE0, 0xF1, 0xE0, 0xE0, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0xEE, 0xCC, 0x88, 0x8C, 0x4E, 0xEE, 0x88, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x00, 0x7F, 0xBF, 0x7F, 0xAF, 0x5F, 0x7F, 0xFF,
	0x88, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0x00,
	0x00, 0xCC, 0xEE, 0xEE, 0x8C, 0x08, 0xCC, 0xEE, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x00, 0x7F, 0xBF, 0x7F, 0xAF, 0x5F, 0x7F, 0xFF,
	0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0xCC, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0x00,
	0x00, 0x00, 0x00, 0xEE, 0xEE, 0xEE, 0xCC, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x60, 0x69, 0x0F, 0x71, 0x69, 0x0F, 0x17, 0x00, 0x00, 0x00, 0x88, 0xEE, 0xFF, 0xFF, 0xFF,
	0xCC, 0xCC, 0xCC, 0xEE, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x77, 0x33, 0x00, 0x00, 0x00,
	0x00, 0xEE, 0xEE, 0xEE, 0xCC, 0xCC, 0xCC, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x60, 0x69, 0x0F, 0x71, 0x69, 0x0F, 0x17, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	0xCC, 0xCC, 0xEE, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x77, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x44, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x11, 0x11, 0x00,
	0xEE, 0x66, 0x66, 0xEE, 0xEE, 0xEE, 0x66, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x44, 0xEE, 0xEE, 0xEE, 0xEE, 0x66, 0x66, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x66, 0x66, 0x66, 0x66, 0xEE, 0xEE, 0x66, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x08, 0x0C, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x07, 0x07, 0x03,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x0F, 0x0F, 0x0F, 0x07, 0x03, 0x01, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x07, 0x07, 0x07, 0x0F, 0x0F, 0x0F, 0x0F,
	0x00, 0x08, 0x0C, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x0C, 0x0E,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x0E, 0x0E, 0x0C, 0x00, 0x01, 0x03, 0x07, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x00, 0x0F, 0x0F, 0x0F, 0x0E, 0x0C, 0x08, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x0C, 0x0E, 0x0E, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x07, 0x00, 0x01, 0x03, 0x07, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0E, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x07, 0x07, 0x03,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x0F, 0x0F, 0x0F, 0x07, 0x03, 0x01, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03,
	0x00, 0x00, 0x01, 0x03, 0x07, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x08, 0x08, 0x0C, 0x0C, 0x0E, 0x0E,
	0x00, 0x00, 0x00, 0x08, 0x08, 0x08, 0x0C, 0x0C, 0x03, 0x07, 0x07, 0x07, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x0E, 0x0E, 0x0C, 0x07, 0x07, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x00, 0x0F, 0x0F, 0x0F, 0x0E, 0x0C, 0x08, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x01, 0x01, 0x03, 0x03, 0x07, 0x07, 0x00, 0x00, 0x08, 0x0C, 0x0E, 0x0F, 0x0F, 0x0F,
	0x0C, 0x0E, 0x0E, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 0x03, 0x03,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x07, 0x07, 0x03,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x0F, 0x0F, 0x0F, 0x07, 0x03, 0x01, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x07, 0x00,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03,
	0x00, 0x00, 0x01, 0x03, 0x07, 0x0F, 0x0F, 0x0F, 0x00, 0x07, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x03, 0x07, 0x07, 0x07, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x0E, 0x0E, 0x0C, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0C, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0E, 0x00, 0x0F, 0x0F, 0x0F, 0x0E, 0x0C, 0x08, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x0C, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x00, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x00, 0x00, 0x08, 0x0C, 0x0E, 0x0F, 0x0F, 0x0F,
	0x0C, 0x0E, 0x0E, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F,
	0x00, 0xE0, 0xC0, 0x80, 0xC0, 0xE0, 0xE0, 0x80, 0x00, 0x00, 0x00, 0x10, 0x30, 0x30, 0x70, 0x70,
	0x00, 0x10, 0xF0, 0xF0, 0xF0, 0xF3, 0xF3, 0xF0, 0x00, 0xF0, 0xF1, 0xF2, 0xF2, 0xF1, 0xF1, 0xF2,
	0x80, 0xE0, 0xE0, 0xC0, 0x80, 0xC0, 0xE0, 0x00, 0x70, 0x70, 0x30, 0x30, 0x10, 0x00, 0x00, 0x00,
	0xF0, 0xF3, 0xF3, 0xF0, 0xF0, 0xF0, 0x10, 0x00, 0xF2, 0xF1, 0xF1, 0xF2, 0xF2, 0xF1, 0xF0, 0x00,
	0x00, 0xC0, 0xE0, 0xE0, 0xC0, 0x80, 0xC0, 0xE0, 0x00, 0x00, 0x00, 0x10, 0x30, 0x30, 0x70, 0x70,
	0x00, 0x10, 0xF0, 0xF0, 0xF0, 0xF3, 0xF3, 0xF0, 0x00, 0xF0, 0xF1, 0xF2, 0xF2, 0xF1, 0xF1, 0xF2,
	0xE0, 0xC0, 0x80, 0xC0, 0xE0, 0xE0, 0xC0, 0x00, 0x70, 0x70, 0x30, 0x30, 0x10, 0x00, 0x00, 0x00,
	0xF0, 0xF3, 0xF3, 0xF0, 0xF0, 0xF0, 0x10, 0x00, 0xF2, 0xF1, 0xF1, 0xF2, 0xF2, 0xF1, 0xF0, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0x88, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xBC, 0x3C, 0x0F, 0x8F, 0xFF, 0xFF, 0x00, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0xFF,
	0x88, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xBC, 0x3C, 0x0F, 0x8F, 0xFF, 0xFF, 0x11, 0x00, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
	0x00, 0xCC, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xBC, 0x3C, 0x0F, 0x8F, 0xFF, 0xFF, 0x00, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0xFF,
	0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0xCC, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xBC, 0x3C, 0x0F, 0x8F, 0xFF, 0xFF, 0x11, 0x00, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
	0x00, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0x88, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xFF, 0xCF, 0x8F, 0x8F, 0xCF, 0xFF, 0x00, 0xFF, 0xFF, 0x7F, 0xF3, 0xF3, 0x7F, 0xFF,
	0x88, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0xCF, 0x8F, 0x8F, 0xCF, 0xFF, 0x11, 0x00, 0xFF, 0x7F, 0xF3, 0xF3, 0x7F, 0xFF, 0xFF, 0x00,
	0x00, 0xCC, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xFF, 0xCF, 0x8F, 0x8F, 0xCF, 0xFF, 0x00, 0xFF, 0xFF, 0x7F, 0xF3, 0xF3, 0x7F, 0xFF,
	0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0xCC, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0xCF, 0x8F, 0x8F, 0xCF, 0xFF, 0x11, 0x00, 0xFF, 0x7F, 0xF3, 0xF3, 0x7F, 0xFF, 0xFF, 0x00,
	0x00, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0x88, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF,
	0x88, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0x00,
	0x00, 0xCC, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x11, 0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF,
	0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0xCC, 0x00, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0xFF, 0x8F, 0x0F, 0x3C, 0xBC, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0xFF, 0xFF, 0x00,
	0x00, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0x88, 0x00, 0x00, 0x00, 0x01, 0x30, 0x30, 0x67, 0x77,
	0x00, 0x11, 0xFF, 0x3F, 0x1F, 0x1F, 0x3F, 0xFF, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	0x88, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x77, 0x67, 0x30, 0x30, 0x01, 0x00, 0x00, 0x00,
	0xFF, 0x3F, 0x1F, 0x1F, 0x3F, 0xFF, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
	0x00, 0xCC, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x30, 0x30, 0x67, 0x77,
	0x00, 0x11, 0xFF, 0x3F, 0x1F, 0x1F, 0x3F, 0xFF, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0xEE, 0xCC, 0x00, 0x77, 0x67, 0x30, 0x30, 0x01, 0x00, 0x00, 0x00,
	0xFF, 0x3F, 0x1F, 0x1F, 0x3F, 0xFF, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x07, 0x08, 0x08, 0x07, 0x00, 0x07, 0x08, 0x00, 0x0C, 0x02, 0x02, 0x0C, 0x00, 0x0C, 0x02,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x08, 0x07, 0x00, 0x06, 0x09, 0x08, 0x08, 0x06, 0x02, 0x0C, 0x00, 0x02, 0x02, 0x0A, 0x06, 0x02,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x07, 0x08, 0x08, 0x07, 0x00, 0x07, 0x08, 0x00, 0x0C, 0x02, 0x02, 0x0C, 0x00, 0x0C, 0x02,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x08, 0x07, 0x00, 0x00, 0x0F, 0x04, 0x02, 0x01, 0x02, 0x0C, 0x00, 0x08, 0x0E, 0x08, 0x08, 0x08,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x07, 0x08, 0x08, 0x07, 0x00, 0x07, 0x08, 0x00, 0x0C, 0x02, 0x02, 0x0C, 0x00, 0x0C, 0x02,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x08, 0x07, 0x00, 0x06, 0x09, 0x09, 0x09, 0x06, 0x02, 0x0C, 0x00, 0x0C, 0x02, 0x02, 0x02, 0x0C,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x07, 0x08, 0x08, 0x07, 0x00, 0x07, 0x08, 0x08, 0x0C, 0x02, 0x02, 0x0C, 0x00, 0x0C, 0x02, 0x02,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x07, 0x00, 0x09, 0x09, 0x09, 0x07, 0x00, 0x0F, 0x0C, 0x00, 0x0C, 0x02, 0x02, 0x0C, 0x00, 0x0E,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x66, 0x77,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11,
	0xCC, 0xCC, 0xCC, 0x88, 0x88, 0x00, 0x00, 0x00, 0x77, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00,
	0x88, 0xCC, 0xEE, 0xFF, 0xFF, 0xFF, 0x77, 0x00, 0x33, 0x77, 0xFF, 0xFF, 0xFF, 0xFF, 0xCC, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x00, 0x77, 0xFF, 0xFF, 0xFF, 0xEE, 0xCC, 0x00, 0x00, 0xCC, 0xCC, 0x88, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x77, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00,
	0x88, 0xCC, 0xEE, 0xFF, 0xFF, 0xFF, 0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0xCC, 0xCC, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0xCC, 0xCC, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x00, 0x00, 0x88, 0x88, 0xCC, 0xCC, 0xCC, 0x00, 0x00, 0x00, 0x33, 0x33, 0x77, 0x77, 0x77,
	0xCC, 0xCC, 0xCC, 0x88, 0x88, 0x00, 0x00, 0x00, 0x77, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00,
	0xEE, 0xEE, 0xEE, 0xFF, 0xFF, 0xFF, 0x77, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xCC, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x00, 0x77, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0xCC, 0xFF, 0xFF, 0xFF, 0xEE, 0x00,
	0x00, 0x00, 0x00, 0x88, 0x88, 0x00, 0x00, 0x00, 0x77, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00,
	0xCC, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x77, 0x00, 0x00, 0x00, 0xEE, 0xFF, 0xFF, 0xFF, 0xCC, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0xCC, 0xCC, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77, 0x77,
	0x00, 0x00, 0x77, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0xCC, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	0xCC, 0xCC, 0xCC, 0x88, 0x88, 0x00, 0x00, 0x00, 0x77, 0x77, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00,
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x77, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xCC, 0x00,
	0x01, 0x02, 0x04, 0x0C, 0x08, 0x84, 0x84, 0x08, 0x01, 0x00, 0x00, 0x00, 0x09, 0x05, 0x03, 0x00,
	0x00, 0x08, 0x07, 0x78, 0xFA, 0xF5, 0xEA, 0x7B, 0x00, 0x00, 0x00, 0x0B, 0xB5, 0xEA, 0x77, 0x32,
	0x08, 0x84, 0x84, 0x08, 0x0C, 0x04, 0x02, 0x01, 0x00, 0x01, 0x01, 0x01, 0x03, 0x04, 0x08, 0x00,
	0x26, 0x5D, 0xB2, 0x7C, 0x07, 0x00, 0x00, 0x00, 0x72, 0xE6, 0xCC, 0xFC, 0xE3, 0x0E, 0x00, 0x00,
	0x00, 0x60, 0x60, 0xE0, 0xE0, 0xE8, 0xCC, 0x88, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x67, 0x77,
	0x00, 0x11, 0xFF, 0x3F, 0x1F, 0x1F, 0x3F, 0xFF, 0x00, 0x00, 0xF0, 0xF8, 0xFD, 0xFF, 0xFF, 0xFF,
	0x88, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x77, 0x67, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
	0xFF, 0x3F, 0x1F, 0x1F, 0x3F, 0xFF, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
	0x00, 0x60, 0x60, 0xE0, 0xE0, 0xE8, 0xCC, 0x88, 0x00, 0x00, 0x00, 0x11, 0x23, 0x23, 0x77, 0x77,
	0x00, 0x11, 0xFF, 0x1D, 0x0C, 0x0F, 0x1F, 0xFF, 0x00, 0x00, 0xF0, 0xF8, 0xFD, 0xFF, 0xFF, 0xFF,
	0x88, 0xEE, 0xEE, 0xCC, 0x88, 0xCC, 0xEE, 0x00, 0x77, 0x77, 0x23, 0x23, 0x11, 0x00, 0x00, 0x00,
	0xFF, 0x1D, 0x0C, 0x0F, 0x1F, 0xFF, 0x11, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x11, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x77, 0x33, 0x11, 0x00, 0x00, 0x00, 0xCC, 0xEE, 0xEE, 0xFF, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x11, 0x00,
	0x00, 0x11, 0x33, 0x77, 0xFF, 0xFF, 0xFF, 0x00, 0xFF, 0xFF, 0xFF, 0xEE, 0xEE, 0xCC, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x77, 0xFF, 0x77, 0x77, 0x33, 0x11, 0x11, 0x00, 0x00, 0xCC, 0xEE, 0xEE, 0xFF, 0xFF, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x11, 0x11, 0x33, 0x77, 0x77, 0xFF, 0x77, 0xEE, 0xFF, 0xFF, 0xFF, 0xEE, 0xEE, 0xCC, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x33, 0x33, 0x33, 0x11, 0x11, 0x11, 0x00, 0x00, 0x88, 0xCC, 0xEE, 0xEE, 0xFF, 0xFF, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x11, 0x11, 0x11, 0x33, 0x33, 0x33, 0xEE, 0xFF, 0xFF, 0xFF, 0xEE, 0xEE, 0xCC, 0x88,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x11, 0x11, 0x11, 0x11, 0x00, 0x00, 0x00, 0x00, 0xCC, 0xEE, 0xEE, 0xFF, 0xFF, 0xFF, 0xFF,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x11, 0x11, 0x11, 0x11, 0xEE, 0xFF, 0xFF, 0xFF, 0xFF, 0xEE, 0xEE, 0xCC,
	0x00, 0x00, 0x00, 0x00, 0x88, 0x88, 0x88, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x66, 0x77, 0x77, 0x77, 0xFF, 0xFF, 0xFF,
	0x00, 0x88, 0x88, 0x88, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x77, 0x77, 0x77, 0x66,
	0x00, 0x00, 0x88, 0x88, 0xCC, 0xCC, 0xCC, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x33, 0x77, 0x77, 0xFF,
	0x00, 0x88, 0xCC, 0xCC, 0xCC, 0x88, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x77, 0x77, 0x33, 0x33, 0x33, 0x11,
	0x00, 0x00, 0xCC, 0xEE, 0xEE, 0xEE, 0xEE, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x33, 0x33, 0x77,
	0x88, 0xCC, 0xEE, 0xEE, 0xEE, 0xEE, 0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x77, 0x33, 0x33, 0x11, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x44, 0xEE, 0xEE, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x77,
	0xCC, 0xEE, 0xEE, 0xEE, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x77, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x44, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33,
	0xCC, 0xEE, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xCC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x22, 0x44, 0x11, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22, 0x11, 0x00, 0x00, 0x00, 0x11, 0x99, 0x44, 0x00, 0x00,
	0x00, 0x22, 0x11, 0x88, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x11, 0x22, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x88, 0x22, 0x22, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
}

var romHWColors = [32]uint8{
	0x00, 0x07, 0x66, 0xEF, 0x00, 0xF8, 0xEA, 0x6F, 0x00, 0x3F, 0x00, 0xC9, 0x38, 0xAA, 0xAF, 0xF6,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
}

var romPalette = [256]uint8{
	0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0B, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0B, 0x03,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0B, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0B, 0x07,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x0B, 0x01, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x0E, 0x00, 0x01, 0x0C, 0x0F,
	0x00, 0x0E, 0x00, 0x0B, 0x00, 0x0C, 0x0B, 0x0E, 0x00, 0x0C, 0x0F, 0x01, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x01, 0x02, 0x0F, 0x00, 0x07, 0x0C, 0x02, 0x00, 0x09, 0x06, 0x0F, 0x00, 0x0D, 0x0C, 0x0F,
	0x00, 0x05, 0x03, 0x09, 0x00, 0x0F, 0x0B, 0x00, 0x00, 0x0E, 0x00, 0x0B, 0x00, 0x0E, 0x00, 0x0B,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x0E, 0x01, 0x00, 0x0F, 0x0B, 0x0E, 0x00, 0x0E, 0x00, 0x0F,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
}

var romWavetable = [256]uint8{
	0x07, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0D, 0x0E, 0x0E, 0x0E, 0x0D, 0x0D, 0x0C, 0x0B, 0x0A, 0x09,
	0x07, 0x05, 0x04, 0x03, 0x02, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x01, 0x02, 0x03, 0x04, 0x05,
	0x07, 0x0C, 0x0E, 0x0E, 0x0D, 0x0B, 0x09, 0x0A, 0x0B, 0x0B, 0x0A, 0x09, 0x06, 0x04, 0x03, 0x05,
	0x07, 0x09, 0x0B, 0x0A, 0x08, 0x05, 0x04, 0x03, 0x03, 0x04, 0x05, 0x03, 0x01, 0x00, 0x00, 0x02,
	0x07, 0x0A, 0x0C, 0x0D, 0x0E, 0x0D, 0x0C, 0x0A, 0x07, 0x04, 0x02, 0x01, 0x00, 0x01, 0x02, 0x04,
	0x07, 0x0B, 0x0D, 0x0E, 0x0D, 0x0B, 0x07, 0x03, 0x01, 0x00, 0x01, 0x03, 0x07, 0x0E, 0x07, 0x00,
	0x07, 0x0D, 0x0B, 0x08, 0x0B, 0x0D, 0x09, 0x06, 0x0B, 0x0E, 0x0C, 0x07, 0x09, 0x0A, 0x06, 0x02,
	0x07, 0x0C, 0x08, 0x04, 0x05, 0x07, 0x02, 0x00, 0x03, 0x08, 0x05, 0x01, 0x03, 0x06, 0x03, 0x01,
	0x00, 0x08, 0x0F, 0x07, 0x01, 0x08, 0x0E, 0x07, 0x02, 0x08, 0x0D, 0x07, 0x03, 0x08, 0x0C, 0x07,
	0x04, 0x08, 0x0B, 0x07, 0x05, 0x08, 0x0A, 0x07, 0x06, 0x08, 0x09, 0x07, 0x07, 0x08, 0x08, 0x07,
	0x07, 0x08, 0x06, 0x09, 0x05, 0x0A, 0x04, 0x0B, 0x03, 0x0C, 0x02, 0x0D, 0x01, 0x0E, 0x00, 0x0F,
	0x00, 0x0F, 0x01, 0x0E, 0x02, 0x0D, 0x03, 0x0C, 0x04, 0x0B, 0x05, 0x0A, 0x06, 0x09, 0x07, 0x08,
	0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
	0x0F, 0x0E, 0x0D, 0x0C, 0x0B, 0x0A, 0x09, 0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00,
	0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
	0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
}

var sndDumpPrelude = [490]uint32{
	0xE20002E0, 0xF0001700, 0xD20002E0, 0xF0001700, 0xC20002E0, 0xF0001700, 0xB20002E0, 0xF0001700, 0xA20002E0, 0xF0000000, 0x920002E0, 0xF0000000, 0x820002E0, 0xF0000000, 0x720002E0, 0xF0000000,
	0x620002E0, 0xF0002E00, 0x520002E0, 0xF0002E00, 0x420002E0, 0xF0002E00, 0x320002E0, 0xF0002E00, 0x220002E0, 0xF0000000, 0x120002E0, 0xF0000000, 0x020002E0, 0xF0000000, 0xE2000000, 0xF0002280,
	0xD2000000, 0xF0002280, 0xC2000000, 0xF0002280, 0xB2000000, 0xF0002280, 0xA2000000, 0xF0000000, 0x92000000, 0xF0000000, 0x82000000, 0xF0000000, 0x72000000, 0xF0000000, 0xE2000450, 0xF0001D00,
	0xD2000450, 0xF0001D00, 0xC2000450, 0xF0001D00, 0xB2000450, 0xF0001D00, 0xA2000450, 0xF0000000, 0x92000450, 0xF0000000, 0x82000450, 0xF0000000, 0x72000450, 0xF0000000, 0xE20002E0, 0xF0002E00,
	0xD20002E0, 0xF0002E00, 0xC20002E0, 0xF0002E00, 0xB20002E0, 0xF0002E00, 0xA20002E0, 0xF0002280, 0x920002E0, 0xF0002280, 0x820002E0, 0xF0002280, 0x720002E0, 0xF0002280, 0x620002E0, 0xF0000000,
	0x520002E0, 0xF0000000, 0x420002E0, 0xF0000000, 0x320002E0, 0xF0000000, 0x220002E0, 0xF0000000, 0x120002E0, 0xF0000000, 0x020002E0, 0xF0000000, 0xE2000000, 0xF0001D00, 0xD2000000, 0xF0001D00,
	0xC2000000, 0xF0001D00, 0xB2000000, 0xF0001D00, 0xA2000000, 0xF0001D00, 0x92000000, 0xF0001D00, 0x82000000, 0xF0001D00, 0x72000000, 0xF0001D00, 0xE2000450, 0xF0000000, 0xD2000450, 0xF0000000,
	0xC2000450, 0xF0000000, 0xB2000450, 0xF0000000, 0xA2000450, 0xF0000000, 0x92000450, 0xF0000000, 0x82000450, 0xF0000000, 0x72000450, 0xF0000000, 0xE2000308, 0xF0001840, 0xD2000308, 0xF0001840,
	0xC2000308, 0xF0001840, 0xB2000308, 0xF0001840, 0xA2000308, 0xF0000000, 0x92000308, 0xF0000000, 0x82000308, 0xF0000000, 0x72000308, 0xF0000000, 0x62000308, 0xF00030C0, 0x52000308, 0xF00030C0,
	0x42000308, 0xF00030C0, 0x32000308, 0xF00030C0, 0x22000308, 0xF0000000, 0x12000308, 0xF0000000, 0x02000308, 0xF0000000, 0xE2000000, 0xF0002480, 0xD2000000, 0xF0002480, 0xC2000000, 0xF0002480,
	0xB2000000, 0xF0002480, 0xA2000000, 0xF0000000, 0x92000000, 0xF0000000, 0x82000000, 0xF0000000, 0x72000000, 0xF0000000, 0xE2000490, 0xF0001EC0, 0xD2000490, 0xF0001EC0, 0xC2000490, 0xF0001EC0,
	0xB2000490, 0xF0001EC0, 0xA2000490, 0xF0000000, 0x92000490, 0xF0000000, 0x82000490, 0xF0000000, 0x72000490, 0xF0000000, 0xE2000308, 0xF00030C0, 0xD2000308, 0xF00030C0, 0xC2000308, 0xF00030C0,
	0xB2000308, 0xF00030C0, 0xA2000308, 0xF0002480, 0x92000308, 0xF0002480, 0x82000308, 0xF0002480, 0x72000308, 0xF0002480, 0x62000308, 0xF0000000, 0x52000308, 0xF0000000, 0x42000308, 0xF0000000,
	0x32000308, 0xF0000000, 0x22000308, 0xF0000000, 0x12000308, 0xF0000000, 0x02000308, 0xF0000000, 0xE2000000, 0xF0001EC0, 0xD2000000, 0xF0001EC0, 0xC2000000, 0xF0001EC0, 0xB2000000, 0xF0001EC0,
	0xA2000000, 0xF0001EC0, 0x92000000, 0xF0001EC0, 0x82000000, 0xF0001EC0, 0x72000000, 0xF0001EC0, 0xE2000490, 0xF0000000, 0xD2000490, 0xF0000000, 0xC2000490, 0xF0000000, 0xB2000490, 0xF0000000,
	0xA2000490, 0xF0000000, 0x92000490, 0xF0000000, 0x82000490, 0xF0000000, 0x72000490, 0xF0000000, 0xE20002E0, 0xF0001700, 0xD20002E0, 0xF0001700, 0xC20002E0, 0xF0001700, 0xB20002E0, 0xF0001700,
	0xA20002E0, 0xF0000000, 0x920002E0, 0xF0000000, 0x820002E0, 0xF0000000, 0x720002E0, 0xF0000000, 0x620002E0, 0xF0002E00, 0x520002E0, 0xF0002E00, 0x420002E0, 0xF0002E00, 0x320002E0, 0xF0002E00,
	0x220002E0, 0xF0000000, 0x120002E0, 0xF0000000, 0x020002E0, 0xF0000000, 0xE2000000, 0xF0002280, 0xD2000000, 0xF0002280, 0xC2000000, 0xF0002280, 0xB2000000, 0xF0002280, 0xA2000000, 0xF0000000,
	0x92000000, 0xF0000000, 0x82000000, 0xF0000000, 0x72000000, 0xF0000000, 0xE2000450, 0xF0001D00, 0xD2000450, 0xF0001D00, 0xC2000450, 0xF0001D00, 0xB2000450, 0xF0001D00, 0xA2000450, 0xF0000000,
	0x92000450, 0xF0000000, 0x82000450, 0xF0000000, 0x72000450, 0xF0000000, 0xE20002E0, 0xF0002E00, 0xD20002E0, 0xF0002E00, 0xC20002E0, 0xF0002E00, 0xB20002E0, 0xF0002E00, 0xA20002E0, 0xF0002280,
	0x920002E0, 0xF0002280, 0x820002E0, 0xF0002280, 0x720002E0, 0xF0002280, 0x620002E0, 0xF0000000, 0x520002E0, 0xF0000000, 0x420002E0, 0xF0000000, 0x320002E0, 0xF0000000, 0x220002E0, 0xF0000000,
	0x120002E0, 0xF0000000, 0x020002E0, 0xF0000000, 0xE2000000, 0xF0001D00, 0xD2000000, 0xF0001D00, 0xC2000000, 0xF0001D00, 0xB2000000, 0xF0001D00, 0xA2000000, 0xF0001D00, 0x92000000, 0xF0001D00,
	0x82000000, 0xF0001D00, 0x72000000, 0xF0001D00, 0xE2000450, 0xF0000000, 0xD2000450, 0xF0000000, 0xC2000450, 0xF0000000, 0xB2000450, 0xF0000000, 0xA2000450, 0xF0000000, 0x92000450, 0xF0000000,
	0x82000450, 0xF0000000, 0x72000450, 0xF0000000, 0xE2000450, 0xF0001B40, 0xD2000450, 0xF0001B40, 0xC2000450, 0xF0001B40, 0xB2000450, 0xF0001B40, 0xA2000450, 0xF0001D00, 0x92000450, 0xF0001D00,
	0x82000450, 0xF0001D00, 0x72000450, 0xF0001D00, 0x62000450, 0xF0001EC0, 0x52000450, 0xF0001EC0, 0x42000450, 0xF0001EC0, 0x32000450, 0xF0001EC0, 0x22000450, 0xF0000000, 0x12000450, 0xF0000000,
	0x02000450, 0xF0000000, 0xE20004D0, 0xF0001EC0, 0xD20004D0, 0xF0001EC0, 0xC20004D0, 0xF0001EC0, 0xB20004D0, 0xF0001EC0, 0xA20004D0, 0xF0002080, 0x920004D0, 0xF0002080, 0x820004D0, 0xF0002080,
	0x720004D0, 0xF0002080, 0x620004D0, 0xF0002280, 0x520004D0, 0xF0002280, 0x420004D0, 0xF0002280, 0x320004D0, 0xF0002280, 0x220004D0, 0xF0000000, 0x120004D0, 0xF0000000, 0x020004D0, 0xF0000000,
	0xE2000568, 0xF0002280, 0xD2000568, 0xF0002280, 0xC2000568, 0xF0002280, 0xB2000568, 0xF0002280, 0xA2000568, 0xF0002480, 0x92000568, 0xF0002480, 0x82000568, 0xF0002480, 0x72000568, 0xF0002480,
	0x62000568, 0xF0002680, 0x52000568, 0xF0002680, 0x42000568, 0xF0002680, 0x32000568, 0xF0002680, 0x22000568, 0xF0000000, 0x12000568, 0xF0000000, 0x02000568, 0xF0000000, 0xE20005C0, 0xF0002E00,
	0xD20005C0, 0xF0002E00, 0xC20005C0, 0xF0002E00, 0xB20005C0, 0xF0002E00, 0xA20005C0, 0xF0002E00, 0x920005C0, 0xF0002E00, 0x820005C0, 0xF0002E00, 0x720005C0, 0xF0002E00, 0x620005C0, 0x00000E80,
	0x520005C0, 0x00000E80, 0x420005C0, 0x00000E80, 0x320005C0, 0x00000E80, 0x220005C0, 0x00000E80, 0x120005C0, 0x00000E80,
}

var sndDumpDead = [90]uint32{
	0xF1001F00, 0xF1001E00, 0xF1001D00, 0xF1001C00, 0xF1001B00, 0xF1001C00, 0xF1001D00, 0xF1001E00, 0xF1001F00, 0xF1002000, 0xF1002100, 0xE1001D00, 0xE1001C00, 0xE1001B00, 0xE1001A00, 0xE1001900,
	0xE1001800, 0xE1001900, 0xE1001A00, 0xE1001B00, 0xE1001C00, 0xE1001D00, 0xE1001E00, 0xD1001B00, 0xD1001A00, 0xD1001900, 0xD1001800, 0xD1001700, 0xD1001600, 0xD1001700, 0xD1001800, 0xD1001900,
	0xD1001A00, 0xD1001B00, 0xD1001C00, 0xC1001900, 0xC1001800, 0xC1001700, 0xC1001600, 0xC1001500, 0xC1001400, 0xC1001500, 0xC1001600, 0xC1001700, 0xC1001800, 0xC1001900, 0xC1001A00, 0xB1001700,
	0xB1001600, 0xB1001500, 0xB1001400, 0xB1001300, 0xB1001200, 0xB1001300, 0xB1001400, 0xB1001500, 0xB1001600, 0xB1001700, 0xB1001800, 0xA1001500, 0xA1001400, 0xA1001300, 0xA1001200, 0xA1001100,
	0xA1001000, 0xA1001100, 0xA1001200, 0x80000800, 0x80001000, 0x80001800, 0x80002000, 0x80002800, 0x80003000, 0x80003800, 0x80004000, 0x80004800, 0x80005000, 0x80005800, 0x00000000, 0x80000800,
	0x80001000, 0x80001800, 0x80002000, 0x80002800, 0x80003000, 0x80003800, 0x80004000, 0x80004800, 0x80005000, 0x80005800,
}
```

## tools/extract.go（113行、対応: 生成器（C に対応物なし））

```go
// extract.go -- generate data.go (ROM data) from pacman.c.
//
// Usage: go run ./tools -src ../floooh-pacman-c/pacman.c -out data.go
//
// The ROM arrays in pacman.c are pure data; they are carried over
// mechanically, never by hand. Counts and sums are verified here and
// again in data_test.go.
package main

import (
	"flag"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
)

type arraySpec struct {
	cName  string
	goName string
	typ    string
	count  int
	hexFmt string
}

var specs = []arraySpec{
	{"rom_tiles", "romTiles", "uint8", 4096, "0x%02X"},
	{"rom_sprites", "romSprites", "uint8", 4096, "0x%02X"},
	{"rom_hwcolors", "romHWColors", "uint8", 32, "0x%02X"},
	{"rom_palette", "romPalette", "uint8", 256, "0x%02X"},
	{"rom_wavetable", "romWavetable", "uint8", 256, "0x%02X"},
	{"snd_dump_prelude", "sndDumpPrelude", "uint32", 490, "0x%08X"},
	{"snd_dump_dead", "sndDumpDead", "uint32", 90, "0x%08X"},
}

var numRe = regexp.MustCompile(`0[xX][0-9a-fA-F]+|\d+`)

func extractArray(src, name string) ([]uint64, error) {
	// Find the definition: name[N] = { ... };
	defRe := regexp.MustCompile(regexp.QuoteMeta(name) + `\[\d+\]\s*=\s*\{`)
	loc := defRe.FindStringIndex(src)
	if loc == nil {
		return nil, fmt.Errorf("definition of %s not found", name)
	}
	rest := src[loc[1]:]
	end := strings.Index(rest, "};")
	if end < 0 {
		return nil, fmt.Errorf("end of %s not found", name)
	}
	body := rest[:end]
	var vals []uint64
	for _, tok := range numRe.FindAllString(body, -1) {
		v, err := strconv.ParseUint(tok, 0, 64)
		if err != nil {
			return nil, fmt.Errorf("%s: bad number %q", name, tok)
		}
		vals = append(vals, v)
	}
	return vals, nil
}

func main() {
	srcPath := flag.String("src", "../floooh-pacman-c/pacman.c", "path to pacman.c")
	outPath := flag.String("out", "data.go", "path to write")
	flag.Parse()

	raw, err := os.ReadFile(*srcPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	src := string(raw)

	var b strings.Builder
	b.WriteString("// data.go -- ROM data extracted mechanically from pacman.c (lines 3389-4303).\n")
	b.WriteString("// Generated by tools/extract.go. Do not edit by hand.\n\n")
	b.WriteString("package main\n\n")

	for _, sp := range specs {
		vals, err := extractArray(src, sp.cName)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		if len(vals) != sp.count {
			fmt.Fprintf(os.Stderr, "%s: got %d values, want %d\n", sp.cName, len(vals), sp.count)
			os.Exit(1)
		}
		var sum uint64
		for _, v := range vals {
			sum += v
		}
		fmt.Printf("%s: %d values, sum %d\n", sp.cName, len(vals), sum)
		fmt.Fprintf(&b, "var %s = [%d]%s{\n", sp.goName, sp.count, sp.typ)
		for i, v := range vals {
			if i%16 == 0 {
				b.WriteString("\t")
			}
			fmt.Fprintf(&b, sp.hexFmt+", ", v)
			if i%16 == 15 || i == len(vals)-1 {
				b.WriteString("\n")
			}
		}
		b.WriteString("}\n\n")
	}

	if err := os.WriteFile(*outPath, []byte(b.String()), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Printf("wrote %s\n", *outPath)
}
```

## tests/data_test.go（45行、対応: テスト（H9 による追加））

```go
package main

import "testing"

func TestROMDataCountsAndSums(t *testing.T) {
	cases := []struct {
		name string
		sum  uint64
		want uint64
	}{
		{"romTiles", sumU8(romTiles[:]), 267889},
		{"romSprites", sumU8(romSprites[:]), 227290},
		{"romHWColors", sumU8(romHWColors[:]), 1852},
		{"romPalette", sumU8(romPalette[:]), 589},
		{"romWavetable", sumU8(romWavetable[:]), 1856},
		{"sndDumpPrelude", sumU32(sndDumpPrelude[:]), 1523003578600},
		{"sndDumpDead", sumU32(sndDumpDead[:]), 275197360640},
	}
	for _, c := range cases {
		if c.sum != c.want {
			t.Errorf("%s: sum = %d, want %d", c.name, c.sum, c.want)
		}
	}
	if len(romTiles) != 4096 || len(romSprites) != 4096 || len(romHWColors) != 32 ||
		len(romPalette) != 256 || len(romWavetable) != 256 ||
		len(sndDumpPrelude) != 490 || len(sndDumpDead) != 90 {
		t.Error("array length mismatch")
	}
}

func sumU8(a []uint8) uint64 {
	var s uint64
	for _, v := range a {
		s += uint64(v)
	}
	return s
}

func sumU32(a []uint32) uint64 {
	var s uint64
	for _, v := range a {
		s += uint64(v)
	}
	return s
}
```

## tests/state_test.go（39行、対応: テスト（H9 による追加））

```go
package main

import "testing"

func TestLevelSpec(t *testing.T) {
	if ls := levelSpec(0); ls.BonusFruit != FruitCherries || ls.FrightTicks != 360 || ls.BonusScore != 10 {
		t.Errorf("round 0: got %+v", ls)
	}
	if ls := levelSpec(16); ls.FrightTicks != 1 {
		t.Errorf("round 16 fright: got %d, want 1", ls.FrightTicks)
	}
	// clamped to the last entry beyond the table
	if levelSpec(21) != levelSpec(20) || levelSpec(100) != levelSpec(20) {
		t.Error("levelSpec must clamp to the last entry")
	}
	if ls := levelSpec(12); ls.BonusFruit != FruitKey || ls.BonusScore != 500 {
		t.Errorf("round 12: got %+v", ls)
	}
}

func TestFreezeMethods(t *testing.T) {
	var f Freeze
	if !f.Empty() {
		t.Fatal("zero Freeze must be empty")
	}
	f.Add(FreezePrelude)
	f.Add(FreezeReady)
	if !f.Has(FreezePrelude) || !f.Has(FreezeReady) || f.Has(FreezeDead) {
		t.Error("Has/Add wrong")
	}
	f.Clear(FreezePrelude)
	if f.Has(FreezePrelude) || f.Empty() {
		t.Error("Clear wrong")
	}
	f.Clear(FreezeReady)
	if !f.Empty() {
		t.Error("Freeze must be empty after clearing all")
	}
}
```

## tests/timing_test.go（71行、対応: テスト（H9 による追加））

```go
package main

import "testing"

func TestXorshiftSequence(t *testing.T) {
	p := &PlayState{Xorshift: 0x12345678}
	want := []uint32{2274908837, 358294691, 1210119364, 2176035992, 1882851208}
	for i, w := range want {
		if got := p.xorshift32(); got != w {
			t.Errorf("step %d: got %d, want %d", i, got, w)
		}
	}
}

func TestTriggerVocabulary(t *testing.T) {
	var tr Trigger
	tr.Start(10) // promises tick 11
	if tr.Tick != 11 {
		t.Fatalf("Start: tick = %d, want 11", tr.Tick)
	}
	if !tr.Now(11) || tr.Now(10) {
		t.Error("Now semantics wrong")
	}
	if tr.Since(16) != 5 {
		t.Errorf("Since = %d, want 5", tr.Since(16))
	}
	if !tr.AfterOnce(16, 5) || tr.AfterOnce(15, 5) {
		t.Error("AfterOnce semantics wrong")
	}
	if !tr.After(16, 5) || tr.After(15, 5) {
		t.Error("After semantics wrong")
	}
	if !tr.Before(15, 5) || tr.Before(16, 5) {
		t.Error("Before semantics wrong")
	}
	if !tr.Between(16, 5, 10) || tr.Between(16, 0, 5) {
		t.Error("Between semantics wrong")
	}

	d := DisabledTrigger()
	if d.Since(100) != DisabledTicks {
		t.Error("disabled trigger: Since must be DisabledTicks")
	}
	if d.After(100, 0) || d.Before(100, 100) || d.Between(100, 0, 100) {
		t.Error("disabled trigger must never be After/Before/Between")
	}

	var sa Trigger
	sa.StartAfter(10, 30)
	if sa.Tick != 40 || !sa.Now(40) {
		t.Error("StartAfter semantics wrong")
	}
}

func TestInputDirPriority(t *testing.T) {
	cases := []struct {
		in   InputState
		want Dir
	}{
		{InputState{Up: true, Left: true}, DirUp},
		{InputState{Down: true, Right: true}, DirDown},
		{InputState{Right: true, Left: true}, DirRight},
		{InputState{Left: true}, DirLeft},
		{InputState{}, DirDown}, // default passed below
	}
	for i, c := range cases {
		if got := c.in.DirOr(DirDown); got != c.want {
			t.Errorf("case %d: got %v, want %v", i, got, c.want)
		}
	}
}
```

## tests/geom_test.go（37行、対応: テスト（H9 による追加））

```go
package main

import "testing"

func TestDistToTileMidNegative(t *testing.T) {
	// In the tunnel, positions go negative; C's % truncates toward
	// zero, and Go's % does the same, so no cmod helper is needed.
	if got := distToTileMid(I2(-13, 20)); got != I2(9, 0) {
		t.Errorf("distToTileMid(-13,20) = %v, want (9,0)", got)
	}
	if got := pixelToTilePos(I2(-1, 0)); got != I2(0, 0) {
		t.Errorf("pixelToTilePos(-1,0) = %v, want (0,0)", got)
	}
}

func TestClampedTilePos(t *testing.T) {
	if got := clampedTilePos(I2(30, 35)); got != I2(27, 33) {
		t.Errorf("got %v, want (27,33)", got)
	}
	if got := clampedTilePos(I2(-2, 0)); got != I2(0, 3) {
		t.Errorf("got %v, want (0,3)", got)
	}
}

func TestInt2Chain(t *testing.T) {
	// The Inky pivot computation, in method-chain form.
	pmPos, blinkyPos := I2(100, 100), I2(90, 92)
	p := pmPos.Add(dirToVec(DirRight).Scale(2))
	d := p.Sub(blinkyPos)
	pos := blinkyPos.Add(d.Scale(2))
	if pos != I2(114, 108) {
		t.Errorf("Inky target = %v, want (114,108)", pos)
	}
	if reverseDir(DirRight) != DirLeft || reverseDir(DirUp) != DirDown {
		t.Error("reverseDir wrong")
	}
}
```

## tests/headless_test.go（210行、対応: テスト（H9 による追加））

```go
package main

import "testing"

// Headless drivers: the same scenarios as the Nim port's
// tests/headless.nim, driving Game.Tick directly (no graphics, no
// audio output).

func pressAnyKey(g *Game) {
	g.Input.Anykey = true
	g.Tick()
	g.Input.Anykey = false
}

func countDots(g *Game) int {
	n := 0
	for y := 0; y < DisplayTilesY; y++ {
		for x := 0; x < DisplayTilesX; x++ {
			if g.Gfx.VideoRAM[y][x] == TileDot || g.Gfx.VideoRAM[y][x] == TilePill {
				n++
			}
		}
	}
	return n
}

// steerDir does a BFS over non-blocking tiles to the nearest dot/pill
// and returns the first step direction.
func steerDir(g *Game) Dir {
	startT := pixelToTilePos(g.Play.Pacman.Actor.Pos)
	var visited [DisplayTilesY][DisplayTilesX]bool
	var firstStep [DisplayTilesY][DisplayTilesX]Dir
	queue := []Int2{startT}
	visited[startT.Y][startT.X] = true
	dirs := [4]Dir{DirUp, DirLeft, DirDown, DirRight}
	for len(queue) > 0 {
		cur := queue[0]
		queue = queue[1:]
		if cur != startT && (g.isDot(cur) || g.isPill(cur)) {
			return firstStep[cur.Y][cur.X]
		}
		for _, d := range dirs {
			n := cur.Add(dirToVec(d))
			if n.X >= 0 && n.X < DisplayTilesX && n.Y >= 0 && n.Y < DisplayTilesY &&
				!visited[n.Y][n.X] && !g.isBlockingTile(n) {
				visited[n.Y][n.X] = true
				if cur == startT {
					firstStep[n.Y][n.X] = d
				} else {
					firstStep[n.Y][n.X] = firstStep[cur.Y][cur.X]
				}
				queue = append(queue, n)
			}
		}
	}
	return g.Play.Pacman.Actor.Dir
}

func setInput(g *Game, d Dir) {
	g.Input.Up = d == DirUp
	g.Input.Down = d == DirDown
	g.Input.Left = d == DirLeft
	g.Input.Right = d == DirRight
}

// toGameplay boots a fresh game and advances to running gameplay.
func toGameplay(t *testing.T) *Game {
	t.Helper()
	g := NewGame()
	for i := 0; i < 100; i++ {
		g.Tick()
	}
	pressAnyKey(g)
	for i := 0; i < 2000; i++ {
		g.Tick()
		if g.Scene == SceneGame && g.Play.Freeze.Empty() {
			return g
		}
	}
	t.Fatal("never reached gameplay")
	return nil
}

func TestHeadlessPlay(t *testing.T) {
	g := NewGame()
	for i := 0; i < 100; i++ {
		g.Tick()
	}
	if g.Scene != SceneIntro {
		t.Fatalf("scene = %v, want intro", g.Scene)
	}
	pressAnyKey(g)
	sawGame := false
	inkyLeftHouse := false
	maxGhostsOut := 0
	for i := 0; i < 60000; i++ {
		g.Tick()
		if g.Scene == SceneGame {
			if !sawGame {
				sawGame = true
				if n := countDots(g); n != 244 {
					t.Fatalf("playfield starts with %d dots/pills, want 244", n)
				}
			}
			if g.Play.Freeze.Empty() {
				setInput(g, steerDir(g))
			}
			outCount := 0
			for _, gh := range g.Play.Ghost {
				if gh.State != GhostStateHouse {
					outCount++
				}
			}
			if outCount > maxGhostsOut {
				maxGhostsOut = outCount
			}
			if g.Play.Ghost[GhostInky].State != GhostStateHouse {
				inkyLeftHouse = true
			}
		}
	}
	if !sawGame {
		t.Fatal("never entered the game scene")
	}
	t.Logf("score=%d dotsEaten=%d lives=%d round=%d scene=%v maxGhostsOut=%d inkyLeft=%v",
		g.Play.Score, g.Play.NumDotsEaten, g.Play.NumLives, g.Play.Round,
		g.Scene, maxGhostsOut, inkyLeftHouse)
	if g.Play.Score == 0 {
		t.Error("score must be > 0 after 60000 ticks of autopilot")
	}
	if maxGhostsOut < 3 {
		t.Errorf("maxGhostsOut = %d, want >= 3", maxGhostsOut)
	}
}

func TestDeterminism(t *testing.T) {
	runShort := func() [6]int64 {
		g := NewGame()
		for i := 0; i < 100; i++ {
			g.Tick()
		}
		pressAnyKey(g)
		for i := 0; i < 20000; i++ {
			g.Tick()
			if g.Scene == SceneGame && g.Play.Freeze.Empty() {
				setInput(g, steerDir(g))
			}
		}
		return [6]int64{
			int64(g.Play.Score), int64(g.Play.NumDotsEaten),
			int64(g.Play.Pacman.Actor.Pos.X), int64(g.Play.Pacman.Actor.Pos.Y),
			int64(g.Play.Ghost[0].Actor.Pos.X), int64(g.Play.Ghost[0].Actor.Pos.Y),
		}
	}
	r1, r2 := runShort(), runShort()
	if r1 != r2 {
		t.Errorf("determinism broken: %v vs %v", r1, r2)
	}
}

func TestWinScenario(t *testing.T) {
	g := NewGame()
	for i := 0; i < 100; i++ {
		g.Tick()
	}
	pressAnyKey(g)
	for i := 0; i < 1000; i++ {
		g.Tick()
		if g.Scene == SceneGame &&
			!g.Play.Freeze.Has(FreezeReady) && !g.Play.Freeze.Has(FreezePrelude) {
			break
		}
	}
	// remove all dots except the one at (1,4) and pretend 243 were eaten
	for y := 0; y < DisplayTilesY; y++ {
		for x := 0; x < DisplayTilesX; x++ {
			if g.Gfx.VideoRAM[y][x] == TileDot || g.Gfx.VideoRAM[y][x] == TilePill {
				g.Gfx.VideoRAM[y][x] = TileSpace
			}
		}
	}
	g.Gfx.VideoRAM[4][1] = TileDot
	g.Play.NumDotsEaten = 243
	// place Pacman just right of the dot, heading left
	g.Play.Pacman.Actor.Pos = I2(2*8+4, 4*8+4)
	g.Play.Pacman.Actor.Dir = DirLeft
	setInput(g, DirLeft)
	won := false
	for i := 0; i < 2000; i++ {
		g.Tick()
		if g.Play.Freeze.Has(FreezeWon) {
			won = true
		}
		if won && g.Play.Round == 1 && countDots(g) == 244 {
			break
		}
	}
	if !won {
		t.Error("round was not won")
	}
	if g.Play.Round != 1 {
		t.Errorf("round = %d, want 1", g.Play.Round)
	}
	if n := countDots(g); n != 244 {
		t.Errorf("dots after win = %d, want 244", n)
	}
	if g.Play.GlobalDotCounterActive {
		t.Error("global dot counter must be inactive after a win")
	}
}
```

## tests/probes_test.go（270行、対応: テスト（H9 による追加））

```go
package main

import "testing"

// Behavioural probes: the Go counterpart of the Nim port's
// tests/audit_probes.nim (17 checks). Speeds, phase timing, house dot
// counters, frightened duration, ghost-eaten scores and event timing,
// all against the C original's rules.

func TestProbeEventTiming(t *testing.T) {
	g := toGameplay(t)
	dtReady := int64(g.Play.ReadyStarted.Tick) - int64(g.Play.Started.Tick)
	if dtReady != 120 {
		t.Errorf("prelude timing: started->readyStarted = %d, want 120", dtReady)
	}
	dtRound := int64(g.Play.RoundStarted.Tick) - int64(g.Play.ReadyStarted.Tick)
	if dtRound != 130 {
		t.Errorf("ready timing: readyStarted->roundStarted = %d, want 130", dtRound)
	}
}

func TestProbeScatterChaseSwitch(t *testing.T) {
	g := toGameplay(t)
	base := int64(g.Play.RoundStarted.Tick)
	for int64(g.Timing.Tick) < base+419 {
		g.Tick()
	}
	if s := g.Play.Ghost[GhostBlinky].State; s != GhostStateScatter {
		t.Errorf("at +419: Blinky state = %v, want scatter", s)
	}
	g.Tick()
	if s := g.Play.Ghost[GhostBlinky].State; s != GhostStateChase {
		t.Errorf("at +420: Blinky state = %v, want chase", s)
	}
}

func TestProbePacmanClearSpeed(t *testing.T) {
	g := toGameplay(t)
	// row 17 has dots at tiles 6 and 21; clear them for an empty corridor
	for x := 0; x < DisplayTilesX; x++ {
		if g.Gfx.VideoRAM[17][x] == TileDot {
			g.Gfx.VideoRAM[17][x] = TileSpace
		}
	}
	g.Play.Pacman.Actor.Pos = I2(60, 17*8+4)
	g.Play.Pacman.Actor.Dir = DirLeft
	setInput(g, DirLeft)
	moved := 0
	prevX := g.Play.Pacman.Actor.Pos.X
	for i := 0; i < 112; i++ {
		g.Tick()
		x := g.Play.Pacman.Actor.Pos.X
		d := int(prevX - x)
		if d < -100 {
			d += DisplayPixelsX // wrapped through the tunnel
		}
		moved += d
		prevX = x
	}
	if moved != 98 {
		t.Errorf("clear speed: moved %d px in 112 ticks, want 98 (7/8)", moved)
	}
}

func TestProbePacmanEatingSpeed(t *testing.T) {
	g := toGameplay(t)
	g.Play.Pacman.Actor.Pos = I2(12*8+4, 23*8+4)
	g.Play.Pacman.Actor.Dir = DirLeft
	setInput(g, DirLeft)
	ticks := 0
	for g.Play.Pacman.Actor.Pos.X > 12 && ticks < 300 {
		g.Tick()
		ticks++
	}
	ratio := 88.0 / float64(ticks)
	if ratio <= 0.77 || ratio >= 0.83 {
		t.Errorf("eating speed: 88px in %d ticks, ratio %.3f, want ~0.80", ticks, ratio)
	}
}

func TestProbeGhostSpeed(t *testing.T) {
	g := toGameplay(t)
	gTicks, gMoved := 0, 0
	prevPos := g.Play.Ghost[0].Actor.Pos
	for i := 0; i < 3000; i++ {
		g.Tick()
		gh := g.Play.Ghost[0]
		d := int(abs16(gh.Actor.Pos.X-prevPos.X)) + int(abs16(gh.Actor.Pos.Y-prevPos.Y))
		if (gh.State == GhostStateScatter || gh.State == GhostStateChase) &&
			!isTunnel(pixelToTilePos(gh.Actor.Pos)) && g.Play.Freeze.Empty() {
			gTicks++
			gMoved += d
		}
		prevPos = gh.Actor.Pos
	}
	ratio := float64(gMoved) / float64(gTicks)
	if ratio <= 0.83 || ratio >= 0.88 {
		t.Errorf("ghost speed: ratio %.4f over %d ticks, want ~0.857 (6/7)", ratio, gTicks)
	}
}

func TestProbeHouseCounters(t *testing.T) {
	g := toGameplay(t)
	inkyAt, clydeAt := -1, -1
	pills := 0
	lastPillTick := uint32(DisabledTicks)
	lives0 := g.Play.NumLives
	for g.Play.NumDotsEaten < 120 && g.Play.NumLives == lives0 {
		g.Tick()
		if g.Play.PillEaten.Tick != DisabledTicks && g.Play.PillEaten.Tick != lastPillTick {
			lastPillTick = g.Play.PillEaten.Tick
			pills++
		}
		// pin the two roaming ghosts so Pacman survives long enough;
		// this does not touch the dot-counter mechanism under test
		g.Play.Ghost[0].Actor.Pos = ghostStartingPos[0]
		if g.Play.Ghost[1].State != GhostStateHouse {
			g.Play.Ghost[1].Actor.Pos = ghostStartingPos[1]
		}
		if g.Play.Freeze.Empty() {
			setInput(g, steerDir(g))
		}
		if inkyAt < 0 && g.Play.Ghost[GhostInky].State != GhostStateHouse {
			inkyAt = int(g.Play.NumDotsEaten)
		}
		if clydeAt < 0 && g.Play.Ghost[GhostClyde].State != GhostStateHouse {
			clydeAt = int(g.Play.NumDotsEaten)
		}
	}
	if inkyAt != 30 {
		t.Errorf("Inky left at %d dots, want 30", inkyAt)
	}
	if clydeAt >= 0 {
		// pills raise NumDotsEaten but do not advance the house
		// counters (the C pill branch never calls the counter
		// update), so Clyde's exit shifts by the pills eaten
		if clydeAt != 90+pills {
			t.Errorf("Clyde left at %d dots with %d pills, want %d", clydeAt, pills, 90+pills)
		}
	} else {
		t.Logf("Clyde check skipped (death or 120 dots first), dots=%d", g.Play.NumDotsEaten)
	}
}

func TestProbeGlobalCounter(t *testing.T) {
	g := toGameplay(t)
	// stage a death: put Blinky (chase) onto Pacman's tile
	g.Play.Ghost[0].State = GhostStateChase
	g.Play.Ghost[0].Actor.Pos = g.Play.Pacman.Actor.Pos
	g.Tick()
	if g.Play.PacmanEaten.Tick == DisabledTicks {
		t.Fatal("death did not set pacmanEaten")
	}
	// start() stores tick+1 while StartAfter() stores tick+N, so the
	// stored trigger values differ by 209 even though the delay is
	// 210 ticks (the C code has the same arithmetic)
	dtDeath := int64(g.Play.ReadyStarted.Tick) - int64(g.Play.PacmanEaten.Tick)
	if dtDeath != 209 {
		t.Errorf("death->ready timing: delta = %d, want 209", dtDeath)
	}
	// wait for the new round to run with the global counter active
	for i := 0; i < 2000; i++ {
		g.Tick()
		if g.Play.Freeze.Empty() && g.Play.GlobalDotCounterActive {
			break
		}
	}
	gPinky, gInky, gClyde := -1, -1, -1
	for guard := 0; gClyde < 0 && guard < 30000; guard++ {
		g.Tick()
		if g.Play.Freeze.Empty() {
			setInput(g, steerDir(g))
		}
		if gPinky < 0 && g.Play.Ghost[GhostPinky].State != GhostStateHouse {
			gPinky = int(g.Play.GlobalDotCounter)
		}
		if gInky < 0 && g.Play.Ghost[GhostInky].State != GhostStateHouse {
			gInky = int(g.Play.GlobalDotCounter)
		}
		if gClyde < 0 && g.Play.Ghost[GhostClyde].State != GhostStateHouse {
			gClyde = int(g.Play.GlobalDotCounter)
		}
	}
	if gPinky != 7 {
		t.Errorf("global counter: Pinky left at %d, want 7", gPinky)
	}
	if gInky != 17 {
		t.Errorf("global counter: Inky left at %d, want 17", gInky)
	}
	if gClyde != 32 {
		t.Errorf("global counter: Clyde left at %d, want 32", gClyde)
	}
}

func TestProbeFrightenedDuration(t *testing.T) {
	g := toGameplay(t)
	g.Play.Pacman.Actor.Pos = I2(1*8+4, 6*8+4) // on the pill tile
	setInput(g, DirLeft)
	frightStart := -1
	for i := 0; i < 60; i++ {
		g.Tick()
		if g.Play.Ghost[0].State == GhostStateFrightened {
			frightStart = int(g.Timing.Tick)
			break
		}
	}
	if frightStart < 0 {
		t.Fatal("pill did not frighten Blinky")
	}
	// park Pacman far away in the bottom right corner area
	g.Play.Pacman.Actor.Pos = I2(26*8+4, 32*8+4)
	leftAt := -1
	for i := 0; i < 500; i++ {
		g.Tick()
		if g.Play.Ghost[0].State != GhostStateFrightened {
			leftAt = int(g.Timing.Tick) - frightStart
			break
		}
	}
	if leftAt != 360 {
		t.Errorf("frightened lasted %d ticks, want 360", leftAt)
	}
}

func TestProbeGhostScores(t *testing.T) {
	g := toGameplay(t)
	g.Play.Pacman.Actor.Pos = I2(1*8+4, 6*8+4)
	setInput(g, DirLeft)
	for i := 0; i < 60; i++ {
		g.Tick()
		if g.Play.Ghost[0].Frightened.Tick != DisabledTicks &&
			g.Play.Ghost[0].Frightened.Before(g.Timing.Tick, 10) {
			break
		}
	}
	var deltas []int
	for gi := 0; gi < 4; gi++ {
		ghost := &g.Play.Ghost[gi]
		if ghost.State == GhostStateEyes || ghost.State == GhostStateEnterHouse {
			continue
		}
		ghost.State = GhostStateFrightened
		ghost.Frightened.Start(g.Timing.Tick)
		ghost.Actor.Pos = g.Play.Pacman.Actor.Pos
		s0 := int(g.Play.Score)
		for i := 0; i < 30; i++ {
			g.Tick()
			if g.Play.Freeze.Has(FreezeEatGhost) {
				break
			}
		}
		deltas = append(deltas, int(g.Play.Score)-s0)
		// wait out the eat-ghost freeze
		for i := 0; i < 80; i++ {
			g.Tick()
			if !g.Play.Freeze.Has(FreezeEatGhost) {
				break
			}
		}
	}
	want := []int{20, 40, 80, 160}
	if len(deltas) != len(want) {
		t.Fatalf("ghost score deltas = %v, want %v", deltas, want)
	}
	for i := range want {
		if deltas[i] != want[i] {
			t.Fatalf("ghost score deltas = %v, want %v", deltas, want)
		}
	}
}
```

## tests/render_test.go（59行、対応: テスト（H9 による追加））

```go
package main

import "testing"

// The decode half of the renderer works on plain buffers, so it can
// be verified without a graphics context: known tiles decode to
// known shapes, and the palette follows the hardware rules.

func TestDecodeTilesAndPalette(t *testing.T) {
	g := NewGame()
	r := &Renderer{g: g}
	r.gfxDecodeTiles()
	g.gfxDecodeColorPalette()

	// the space tile (0x40) is entirely blank
	for y := 0; y < TileHeight; y++ {
		for x := 0; x < TileWidth; x++ {
			if r.tilePixels[y][TileSpace*TileWidth+x] != 0 {
				t.Fatalf("space tile not blank at (%d,%d)", x, y)
			}
		}
	}
	// the dot tile (0x10) has non-zero pixels, the closed-mouth
	// pacman sprite (48) has non-zero pixels
	nonzero := 0
	for y := 0; y < TileHeight; y++ {
		for x := 0; x < TileWidth; x++ {
			if r.tilePixels[y][TileDot*TileWidth+x] != 0 {
				nonzero++
			}
		}
	}
	if nonzero == 0 {
		t.Error("dot tile decoded to nothing")
	}
	nonzero = 0
	for y := 0; y < SpriteHeight; y++ {
		for x := 0; x < SpriteWidth; x++ {
			if r.tilePixels[TileHeight+y][48*SpriteWidth+x] != 0 {
				nonzero++
			}
		}
	}
	if nonzero == 0 {
		t.Error("pacman sprite decoded to nothing")
	}
	// palette: index 0 of each group of 4 is transparent, the rest
	// are opaque
	for i := 0; i < 256; i += 4 {
		if got := g.Gfx.ColorPalette[i] >> 24; got != 0 {
			t.Errorf("palette[%d] alpha = %d, want 0", i, got)
		}
	}
	for _, i := range []int{1, 2, 3} {
		if got := g.Gfx.ColorPalette[i] >> 24; got != 0xFF {
			t.Errorf("palette[%d] alpha = %d, want 0xFF", i, got)
		}
	}
}
```

## tests/audio_test.go（93行、対応: テスト（H9 による追加））

```go
package main

import "testing"

// The Synth's sample generation is verified without an audio device:
// silence stays silent, a started dump sound produces samples and
// advances, and generation is deterministic for a fixed state.

func TestPreludeDescDecode(t *testing.T) {
	g := NewGame()
	g.sndStart(0, sndPrelude)
	snd := g.Audio.Sound[0]
	if snd.Stride != 2 || snd.NumTicks != 245 {
		t.Errorf("prelude: stride=%d numTicks=%d, want 2/245", snd.Stride, snd.NumTicks)
	}
	if snd.Flags != SoundVoice0|SoundVoice1 {
		t.Errorf("prelude flags = %v, want voices 0+1", snd.Flags)
	}
	g.sndStart(2, sndDead)
	snd = g.Audio.Sound[2]
	if snd.Stride != 1 || snd.NumTicks != 90 {
		t.Errorf("dead: stride=%d numTicks=%d, want 1/90", snd.Stride, snd.NumTicks)
	}
}

func TestSynthSilenceAndSignal(t *testing.T) {
	g := NewGame()
	s := NewSynth(g)
	buf := make([]byte, SamplesPerTick*bytesPerSample)

	// no voices active: pure silence
	if _, err := s.Read(buf); err != nil {
		t.Fatal(err)
	}
	for i, b := range buf {
		if b != 0 {
			t.Fatalf("silence broken at byte %d: %d", i, b)
		}
	}

	// start the prelude (a register dump): tick the sound state so
	// the registers load, then the synth must produce a signal
	g.sndStart(0, sndPrelude)
	for i := 0; i < 30; i++ {
		g.sndTick()
	}
	nonzero := 0
	for chunk := 0; chunk < 10; chunk++ {
		if _, err := s.Read(buf); err != nil {
			t.Fatal(err)
		}
		for _, b := range buf {
			if b != 0 {
				nonzero++
			}
		}
	}
	if nonzero == 0 {
		t.Error("prelude produced no samples")
	}

	// stereo channels must be identical (mono duplicated, SPEC H3)
	if _, err := s.Read(buf); err != nil {
		t.Fatal(err)
	}
	for i := 0; i+4 <= len(buf); i += 4 {
		if buf[i] != buf[i+2] || buf[i+1] != buf[i+3] {
			t.Fatalf("stereo mismatch at byte %d", i)
		}
	}
}

func TestSynthDeterministic(t *testing.T) {
	gen := func() []byte {
		g := NewGame()
		s := NewSynth(g)
		g.sndStart(1, sndWeeooh)
		for i := 0; i < 10; i++ {
			g.sndTick()
		}
		buf := make([]byte, SamplesPerTick*bytesPerSample*4)
		if _, err := s.Read(buf); err != nil {
			t.Fatal(err)
		}
		return buf
	}
	a, b := gen(), gen()
	for i := range a {
		if a[i] != b[i] {
			t.Fatalf("synth output differs at byte %d", i)
		}
	}
}
```

---

# 付録B C⇔Go 対応表

## モジュールの対応

| pacman.c | Go | 本の担当 |
|---|---|---|
| 142〜678（定数・列挙型・構造体・状態・表） | `state.go` | 第2章・第6章 |
| 826〜943 のうちトリガーと乱数 | `timing.go` | 第3章 |
| 988〜991、1230〜1361（幾何・盤面の問い合わせ） | `geom.go` | 第4章 |
| 1750〜2087（ゴースト） | `ghost.go` | 第7章・第8章 |
| 1377〜1583、1733〜1748、2089〜2403（ルール） | `rules.go` | 第6章 |
| 993〜1229、1584〜1732、2404〜3124（描画） | `render.go` | 第9章 |
| 638〜678、3125〜3388（音） | `audio.go` | 第10章 |
| 928〜943（入力）+ H8 の追加 | `input.go` | 第11章 |
| 716〜825（入り口） | `main.go` | 第1章 |
| 3389〜4303（ROM データ） | `data.go`（生成） | 第5章 |
| （対応物なし） | `tools/extract.go`（生成器） | 第5章 |
| （対応物なし） | テスト7本（H9） | 第12章 |

## 型と状態の対応

| C | Go（置き場所） |
|---|---|
| `state` 構造体（420〜540） | `Game` 構造体（state.go 394）に一元化。場面ごとの状態は `Scene` / `Timing` / `Intro` / `Play` / `Input` / `Audio` / `Gfx` の各フィールド |
| トリガー `uint32_t` のフィールド群 | `Trigger` 構造体（state.go 219）とそのメソッド（timing.go） |
| `freezetype_t` のビットフラグ（314〜320） | `Freeze`（uint8 の定義型、state.go 183）とメソッド `Has` / `Add` / `Clear` / `Empty` |
| `int2_t` と `add_i2` など | `Int2` 構造体（state.go 225）とメソッド連鎖（geom.go）。コンストラクタは `I2()` |
| `snddesc_t`（音の記述） | `SoundDesc` 構造体（state.go 287）。ダンプ再生は `Data []uint32` スライスで保持 |
| 音の関数ポインタ `sound_func_t`（381） | `SoundFunc` 型（state.go 282、`func(g *Game, slot int32)`） |
| 列挙型（254〜320） | 定義型 + `iota`（`Scene` 108、`Dir` 117、`Fruit` 128、`GhostType` 156、`GhostState` 167 など） |

## 関数の対応（主なもの）

| C | Go |
|---|---|
| `sokol_main`（716）、`init` / `frame` / `cleanup`（732〜824） | `main`（main.go 78）、`app.Update`（31）/ `app.Draw`（49）/ `app.Layout`（53）。Ebitengine の Game インターフェースの実装（H2） |
| `xorshift32`（827） | `PlayState.xorshift32`（timing.go 10） |
| `start` / `start_after` / `disable` / `now` / `since`（844〜915） | `Trigger.Start` / `StartAfter` / `Disable` / `Now` / `Since`（timing.go 20〜35）。時刻 `now` は引数で渡す |
| `between`（917〜） | `Trigger.Between`（timing.go 44） |
| `input_dir`（928） | `InputState.DirOr`（timing.go 84）と、機器の読み取り `InputReader.Read`（input.go 42） |
| `levelspec`（835） | `levelSpec`（state.go 481） |
| `dist_to_tile_mid`（988） | `distToTileMid`（geom.go 44）。Go の `%` は C と同じ切り捨てなので補正は不要（第4章） |
| `clamped_tile_pos`（1235） | `clampedTilePos`（geom.go 54） |
| `is_redzone`（1298） | `isRedzone`（geom.go 119） |
| `can_move` / `move`（1304 / 1334） | `canMove`（geom.go 125）/ `move`（145） |
| `game_init` / `game_round_init`（1447 / 1467） | `gameInit`（rules.go 110）/ `gameRoundInit`（128） |
| `game_tick` / `intro_tick`（2217 / 2326） | `Game.Tick`（rules.go 331）から `gameTick`（350）/ `introTick`（417）。生成は `NewGame`（320） |
| ゴーストの更新（1750〜2087） | `ghostSpeed`（ghost.go 7）、`scatterChasePhase`（34）、`updateGhostState`（57）、`updateGhostTarget`（118）、`updateGhostDir`（161）、`updateGhosthouseDotCounters`（247） |
| `game_update_dots_eaten`（2089） | `gameUpdateDotsEaten`（rules.go 208） |
| `game_update_actors`（2111） | `gameUpdateActors`（rules.go 226） |
| `vid_*` / `spr_*`（993〜1229、1584〜1732） | 同名のメソッド（render.go 14〜315）。状態層は C と同形、実描画は `Renderer`（render.go 419〜）が担う（H6） |
| `snd_*` と生成関数（3125〜3388） | 同名のメソッドと `sndFunc*`（audio.go 8〜236）。再生は pull 型の `Synth.Read`（audio.go 292、H3） |

## 仕様書 SPEC の決定（H1〜H9）と実装の対応

| 決定 | 内容 | 実装 | 本の担当 |
|---|---|---|---|
| H1 | 1 Update = 1 ティック、TPS 60 固定 | `app.Update` が `Game.Tick` を1回呼ぶ | 第1章 |
| H2 | Ebitengine の Game 実装、初期化失敗は `error` | `main.go` の `app` 型 | 第1章 |
| H3 | 音は pull 型（io.Reader）、44,100Hz、1ティック = 735 サンプル | `Synth`（audio.go） | 第10章 |
| H4 | ROM データは生成 Go ソース | `data.go` と `tools/extract.go` | 第5章 |
| H5 | letterbox なし、Layout と FilterNearest | `app.Layout`（main.go 53） | 第9章 |
| H6 | タイル×色の事前画像化、盤面は差分更新 | `Renderer`（render.go） | 第9章 |
| H7 | Game 型 + メソッド、Freeze はビット型、Int2 はメソッド連鎖、単一パッケージ | `state.go` ほか全体 | 第2章・第4章・第6章 |
| H8 | 入力はキーボード・ゲームパッド・タッチの合流（マウスなし、振動なし） | `input.go` | 第11章 |
| H9 | ロジックは Ebitengine 非依存、表駆動テスト | テスト7本 | 第12章 |

---

# 付録C 検証の記録

題材の Go ソースについて、こちらで確認したことと
確認できていないことを、区別して記録します。
いずれも「こちらの環境で確認した」範囲で、
利用者の手元での実行確認とは別物です。

## 1. 土台の確認（Phase 0 のスパイク）

- Go 1.27.4 を導入して固定し、Ebitengine v2.10.6 を
  go.mod / go.sum で固定した
- スパイクで、窓の表示、Layout（論理 224×288、
  窓 448×576）、FilterNearest のタイル描画が通り、
  Xvfb 下で 180 アップデートが正常終了した
- WASM のビルドが通った（実行は未確認、下記）
- 音響装置のないこの環境では、`audio.Player` の
  作成時のドライバ初期化エラーが `RunGame` を
  即座に終了させることを確認した。対策として、
  環境変数 `PACMAN_AUDIO=off` で音を無効化できる
  作りにした（第10章）

## 2. データの照合（Phase 1）

- `tools/extract.go` が生成する `data.go` の7配列が、
  C / Nim と個数・合計値で完全一致した
  （値の総数 9,316。タイル 4096 / 合計 267889、
  スプライト 4096 / 227290、ハードウェア色 32 / 1852、
  パレット 256 / 589、波形 256 / 1856、
  プレリュード 490 / 1523003578600、
  デッド 90 / 275197360640）
- 生成の再実行で `data.go` がバイト一致した

## 3. ヘッドレス検証（Phase 2〜5）

- `go vet` は無警告
- テストは全件合格。内訳は、基礎テスト
  （データ・状態・タイミング・幾何）、ヘッドレス
  検証、挙動プローブ、描画の構造テスト、音のテスト
- ヘッドレス検証: 60,000 ティックの自動プレイで
  スコア 350、ドット 66、4匹とも家を出て、
  死亡 → ゲームオーバー → イントロ復帰まで進んだ。
  スコアとドット数は Nim 版の同一シナリオと
  完全一致した（出典: Nim 移植の報告書 REPORT.md）
- 決定性: 同じ条件の2回の実行が完全一致した
- 面クリアのシナリオで、ラウンド進行と
  全体カウンタの無効化を確認した
- 挙動プローブ: 開始連鎖（プレリュード 120、
  ready→round 130、局面切替 +420）、速さ
  （Pac-Man 7/8、ゴースト 6/7）、家のカウンタ
  （Inky 30、Clyde 90）、全体カウンタ（7/17/32）、
  青時間 360、捕食得点（内部単位 20/40/80/160）、
  死亡 → READY の差 209 など、全件合格
- Xvfb スモーク: イントロ 600 フレームと、
  プレイ開始後の 3,600 フレームが正常に進んだ
- 音のテスト: 無音は無音、プレリュードで信号が
  出る、ステレオの左右が一致する、生成が
  決定的であることを確認した

## 4. 外部レビューでの再確認（2026-11-20）

- レビュアーが、描画のロジック部分を Ebitengine
  から切り分けて Go 1.22 でコンパイルし、テスト
  24件が全件合格、`TestHeadlessPlay` で
  スコア 350・ドット 66 を再現した
- 行数の指摘で、報告書の合計 3,334 は 3,333 の
  誤りと判明し、訂正した（data.go は 608行）
- あわせて、Nim の `mod` と `div` が C と同じ
  切り捨て型であることを Nim 2.2.14 で実測して
  確認した（`-7 mod 8 = -7` など 3,606 件）。
  Nim 版で用意した `cmod` は不要だったもので、
  Go では最初から使っていない（第4章）

## 5. 確認できていないこと

- 実画面と実音（この環境には音響装置がない）、
  ゲームパッドとタッチの操作感、他 OS での
  ビルドは、利用者の手元での確認待ち
- WASM はビルド成功のみで、ブラウザでの実行は
  未確認（こちらの実行環境のブラウザからは、
  この VM のローカルサーバーへ到達できなかった）
