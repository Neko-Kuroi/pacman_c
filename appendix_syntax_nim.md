# 別冊 Nim 構文集 ― pacman.c の Nim 移植に現れた構文

Nim 版（ミニ版）の本編では、Nim の文法レクチャーを
省きました。この別冊は、その補いです。題材の Nim
ソース（`src/` の10ファイル）に実際に現れた構文だけを
拾い、「C ではこうだったものが、Nim ではこうなる」を
対でまとめます。本編とは別の冊子で、全文連結版には
含まれません。

各項目は、Nim の実例（ファイル名と行番号つき）→
意味 → C の対応、の順です。引用はすべて実ファイルと
照合してあります。

---

## 1. 式の書き方

### 1.1 if 式 ― 三項演算子の代わり

Nim に `?:` はありません。代わりに、`if` そのものが
値を返す「式」として書けます。家の出口への誘導で
使われています（ghost.nim 145行）。

```nim
        ghost.nextDir = if pos.x > ANTEPORTAS_X: DIR_LEFT else: DIR_RIGHT
```

C では三項演算子でした（pacman.c 1988行）。

```c
                ghost->next_dir = (pos.x > ANTEPORTAS_X) ? DIR_LEFT:DIR_RIGHT;
```

### 1.2 整数リテラルの型サフィックス

数字の後ろに型を付けて、「このリテラルはこの型」と
明示できます（rules.nim 329行、ghost.nim 169行）。

```nim
  var delay = 30'u32
```

```nim
      var minDist = 100000'i32
```

C では、リテラルの型は文脈（代入先や演算相手）で
決まるのが基本で、サフィックス（`U` や `L`）は
あまり表に出ません。Nim は、型の違う値どうしの
演算に厳しいので、こうして型を書く場面が出ます。

### 1.3 演算子を自分で定義する

`Int2` の足し算は、演算子として定義されています
（pacstate.nim 144〜146行）。

```nim
proc `+`*(v0, v1: Int2): Int2 = i2(v0.x + v1.x, v0.y + v1.y)
proc `-`*(v0, v1: Int2): Int2 = i2(v0.x - v1.x, v0.y - v1.y)
proc `*`*(v: Int2, s: int16): Int2 = i2(v.x * s, v.y * s)
```

定義してしまえば、`a + b`、`p - blinkyPos`、
`pmDir * 4` のように算数の形で書けます。C では
関数でした（pacman.c 952〜954行）。

```c
static int2_t add_i2(int2_t v0, int2_t v1) {
    return (int2_t) { v0.x+v1.x, v0.y+v1.y };
}
```

### 1.4 文字列の連結 `&`

迷路の文字列は、`&` でつないで作られています
（rules.nim 15〜16行）。

```nim
  const tiles =
    "0UUUUUUUUUUUU45UUUUUUUUUUUU1" &
```

C では、文字列リテラルを隣に並べるだけで連結
されました。Nim では連結も演算子の仕事です。

### 1.5 集合リテラルと `in`

ゲームを止める理由は集合で持ちます。代入は
波括弧のリテラル（rules.nim 89行）、所属の確認は
`in`（rules.nim 288行）です。

```nim
  state.game.freeze = {FREEZETYPE_PRELUDE}
```

```nim
  if FREEZETYPE_EAT_GHOST in state.game.freeze:
```

C ではビット演算でした。足す（pacman.c 2173行）、
外す、全部落ちたか見る、がそれぞれ対応します。

```c
                    state.game.freeze |= FREEZETYPE_EAT_GHOST;
```

---

## 2. 入れ物と並び

### 2.1 固定長配列 `array[N, T]`

画面の表は、36行×28列の固定長配列です
（pacstate.nim、GfxState の中）。

```nim
  videoRam*: array[DISPLAY_TILES_Y, array[DISPLAY_TILES_X, uint8]]
```

C の `uint8_t video_ram[DISPLAY_TILES_Y][DISPLAY_TILES_X]`
にあたります。長さが型の一部になっているので、
範囲外の代入はコンパイルの段階で見つかります。

### 2.2 列挙型と `ord`

列挙の値は、そのままでは整数として使えません。
添字に使うときは `ord` で番号に直します
（rules.nim 133行）。

```nim
  state.game.ghost[ord(GHOSTTYPE_BLINKY)] = Ghost(
```

C では、列挙の値は最初から整数として扱えたので、
この変換は要りませんでした。Nim の列挙は
「番号である前に、意味のある値」として
区別されます。

### 2.3 範囲つき for

盤面の書き込みは、範囲の for で回します
（rules.nim 73〜74行）。

```nim
  for y in 3..33:
    for x in 0..<28:
```

`..` は両端を含み、`..<` は終わりを含みません。
C の `for (int y = 3; y <= 33; y++)` にあたります。
「以下」と「未満」の書き分けが、記号に表れて
います。

### 2.4 定数の表

散らばり先のような表は、定数の配列として
置かれます（pacstate.nim 309〜310行）。

```nim
const ghostScatterTargets*: array[4, Int2] = [
  i2(25, 0), i2(2, 0), i2(27, 34), i2(0, 34)]
```

C の `static const` の配列と同じ置き方です。
コンパイル時に中身が決まるので、実行時の
初期化は要りません。

---

## 3. 文と流れ

### 3.1 case ― 値で分ける

場面の振り分けは `case` です（pacman.nim 31〜35行）。

```nim
    case state.gamestate
    of GAMESTATE_INTRO:
      introTick()
    of GAMESTATE_GAME:
      gameTick()
```

C の `switch` にあたります。Nim の `case` は、
列挙のすべての値を扱い忘れるとコンパイルで
教えてくれるので、「場面の足し忘れ」が
起きにくくなっています。

### 3.2 while の蓄積ループ

フレームの中でティックを消化するループです
（pacman.nim 24〜25行）。

```nim
  while state.timing.tickAccum > -TICK_TOLERANCE_NS.int32:
    state.timing.tickAccum -= TICK_DURATION_NS
```

`.int32` は型の変換です（5.3 を参照）。C の
while と同じ形ですが、Nim では条件の中でも
変換を書く必要があります。

### 3.3 assert

前提の確認は `assert` で書きます
（render.nim 37行）。

```nim
  assert(validTilePos(tilePos))
```

C の `assert` と同じ名前、同じ役割です。
デバッグのビルドでは有効で、リリースでは
外れます。この移植でも、盤面の初期化の
 assert（残機が負にならないこと）まで、
C と同じ場所に置かれています。

### 3.4 discard ― 戻り値を捨てる

戻り値のある関数を、値を捨てて呼ぶときは
`discard` を付けます（sound.nim、sndSampleTick の中）。

```nim
    discard saudio.push(addr state.audio.sampleBuffer[0],
                        state.audio.numSamples.int32)
```

C では、戻り値は黙って捨てることができました。
Nim では「捨てる」ことも明示します。

---

## 4. 関数

### 4.1 proc と公開マーク `*`

関数は `proc` で定義します。名前の後ろの `*` は
「他のモジュールから見える」という印です
（timing.nim 16〜18行）。

```nim
# set time trigger to the next game tick
proc start*(t: var Trigger) =
  t.tick = state.timing.tick + 1
```

C では、公開するかどうかは `static` の有無で
決まっていました（pacman.c 844〜846行）。

```c
static void start(trigger_t* t) {
    t->tick = state.timing.tick + 1;
}
```

Nim では「見える」が印、`static` の側は
「見えない」が印、と向きが逆です。

### 4.2 var 引数 ― 書き換える引数

引数を書き換える手続きは、型に `var` を付けます
（ghost.nim 35行）。

```nim
proc updateGhostState*(ghost: var Ghost) =
```

C ではポインタで渡していました
（pacman.c 1792行）。

```c
static void game_update_ghost_state(ghost_t* ghost) {
```

`var` 引数は「借りて書き換える」意味が型に
出ます。呼び出し側で `&` を書く必要は
ありません。

### 4.3 result ― 戻り値の変数

手続きの中には、戻り値そのものを表す `result`
という変数があります（geom.nim 20〜21行）。

```nim
proc clampedTilePos*(tilePos: Int2): Int2 =
  result = tilePos
```

最後まで残った `result` が返ります。C では
「ローカル変数を1つ作って、書き換えて、
最後に return する」流れを、手続きの仕組みの
側が肩代わりした形です。

### 4.4 関数型

関数の型にも名前が付けられます
（pacstate.nim 193行）。

```nim
type SoundFunc* = proc(slot: int32) {.nimcall.}
```

効果音の手続きを入れる場所（`SoundDesc` の
`fn`）の型です。C では関数ポインタの typedef
でした（pacman.c 381行）。

```c
typedef void (*sound_func_t)(int sound_slot);
```

`{.nimcall.}` は呼び出し規約の指定で、
「Nim の流儀で呼ぶ関数」という印です。

---

## 5. 型と object

### 5.1 object 型 ― 構造体

C の構造体にあたるのが `object` です
（pacstate.nim 297〜306行）。

```nim
type State* = object
  gamestate*: GameState
  timing*: TimingState
  intro*: IntroState
  game*: Game
  input*: InputState
  audio*: AudioState
  gfx*: GfxState

var state*: State
```

フィールドの後ろの `*` は、4.1 と同じ
公開マークです。

### 5.2 コンストラクタ式

値の組み立ては、型名にフィールドを名前つきで
渡す形で書けます（rules.nim 133〜137行）。

```nim
  state.game.ghost[ord(GHOSTTYPE_BLINKY)] = Ghost(
    actor: Actor(dir: DIR_LEFT, pos: ghostStartingPos[ord(GHOSTTYPE_BLINKY)]),
    typ: GHOSTTYPE_BLINKY, nextDir: DIR_LEFT, state: GHOSTSTATE_SCATTER,
    frightened: disabledTimer(), eaten: disabledTimer(),
    dotCounter: 0, dotLimit: 0)
```

C の指定子つき初期化（複合リテラル）と同じ
発想で、書かなかったフィールドは0（既定値）に
なります。ラウンドの初期化で、ゴースト4匹の
初期値がこの形で並んでいます。

### 5.3 型の変換

型の違う値への変換は、`.型名` や型名の
呼び出しで書きます。得点の計算では、ビット
シフトの結果を `uint32` に直しています
（rules.nim、衝突の分岐）。

```nim
          state.game.score += (10 * (1 shl state.game.numGhostsEaten)).uint32
```

青の点滅判定では、符号つきで引いてから
変換する、という C の手順も写しました
（render.nim 169行）。

```nim
  if tick > (levelspec(state.game.round.int).frightTicks.int32 - 60).uint32:
```

C の `(uint32_t)` キャストにあたります。
Nim は暗黙の変換が少ないので、変換の場所が
目に見える形で残ります。

---

## 6. モジュールと状態

### 6.1 import と `as`

モジュールの読み込みは `import` です。
名前が長いライブラリには別名を付けられます
（pacman.nim 4〜5行）。

```nim
import sokol/log as slog
import sokol/app as sapp
```

C の `#include` にあたりますが、Nim の
import は「そのモジュールの公開された名前を
使えるようにする」もので、ファイルの単純な
貼り込みではありません。

### 6.2 大域変数は var で

状態の実体は、モジュールの大域変数です
（pacstate.nim 306行、5.1 の引用も参照）。

```nim
var state*: State
```

C では、構造体の定義と実体の宣言が1か所に
ありました。Nim では型（`State`）と実体
（`state`）が別の行に分かれます。読み込み
（import）したモジュールは、この1つの実体を
共有します。

### 6.3 let ― 変えない束縛

効果音の記述子は `let` で置かれています
（sound.nim 182行）。

```nim
let sndEatdot1* = SoundDesc(fn: sndFuncEatdot1, voice: [false, false, true])
```

`let` は「初期化のあと変えない」束縛です。
C の `static const` の表にあたります。
`var`（変える）との書き分けが、そのまま
「これは設定か、状態か」の区別になります。

---

## 7. ポインタとプラグマ

### 7.1 addr ― 住所を取る

配列の中の1匹を書き換えるために、住所を
取って変数に持ちます（rules.nim 190行）。

```nim
    var actor = addr state.game.pacman.actor
```

C の `&state.game.pacman.actor` にあたります。
取った住所（ポインタ）経由の書き換えは、
元の場所に届きます。この移植では、ポインタが
表に出るのは、こうした「配列の要素を手続きに
渡す」場所と、次のダンプ読み取りくらいです。

### 7.2 ptr UncheckedArray ― 検査なしの配列

レジスタダンプのデータは、検査なしの配列への
ポインタで持ちます（pacstate.nim 195〜198行）。

```nim
type SoundDesc* = object
  fn*: SoundFunc
  data*: ptr UncheckedArray[uint32]  # register dump data (nil for procedural sounds)
  size*: uint32          # byte size of register dump data
  voice*: array[3, bool]
```

C の `const uint32_t* ptr` にあたります。
「C の配列のように読む」ことを型で明示する
書き方で、データの正しさは機械抽出と検証で
担保します（本編 第11章）。

### 7.3 {.cdecl.} ― 呼び出し規約のプラグマ

sokol から呼ばれるコールバックには、
`{.cdecl.}` という印（プラグマ）が付きます
（pacman.nim 12行）。

```nim
proc init() {.cdecl.} =
```

「C の流儀で呼ばれる関数」という指定です。
C では通常の関数がそのままコールバックに
なりましたが、Nim から C の世界に渡す関数には、
この橋渡しの印が要ります。プラグマは、
こうした「コンパイラへの注文」を括弧で
付ける仕組みです。

---

*この別冊の項目は、題材に現れた構文だけから
選んでいます。Nim の構文の全体像（テンプレート、
マクロ、イテレータなど）は、題材に現れなかった
ため扱っていません。*
