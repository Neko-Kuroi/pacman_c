# パックマンを書く TypeScript 版（ミニ版）全文連結版 第1版

# パックマンを書く TypeScript 版（ミニ版）

floooh の pacman.c（C99、4,303行）を TypeScript へ
移植した実装を題材に、C 実装との対応と、ブラウザ
という実行環境の作法を追うミニ版教科書です。

C版教科書『パックマンを書く』、Python ミニ版、
Nim 版、Go 版に続く5冊目です。前の4冊と違い、
この題材はブラウザで動きます。描画は Canvas 2D、
音は AudioWorklet、入口は HTML です。言語の違い
よりも「動く場所の違い」が大きい移植なので、
本の軸もそこに置きました。

## 題材

- pacman.c の TypeScript 移植（ブラウザ版）
- 手書き 3,168行 + 生成データ 607行、テスト 946行
- 土台はブラウザ標準のみ（Canvas 2D、AudioWorklet、
  ES モジュール）。ライブラリは使わない
- 仕様の決定は SPEC の T1〜T10。本では T番号で
  参照し、決定そのものは収録しない

## 構成

- 序章: 5つ目の移植は「場所」が違う
- 第1章: 全体地図（HTML とモジュール、主ループ）
- 第2章: 状態（state.ts）
- 第3章: 時間（timing.ts）
- 第4章: 幾何（geom.ts）
- 第5章: データ（romdata.ts と生成器）
- 第6章: ルール（rules.ts）
- 第7章: ゴーストの思考（ghost.ts）
- 第8章: 家と速さ
- 第9章: 描画（Canvas 2D）
- 第10章: 音（AudioWorklet）
- 第11章: 入力（キーボードとタッチ）
- 第12章: テストと検証
- 終章: 5つの移植で書くということ
- 付録A: TypeScript ソース全文
- 付録B: C ⇔ TypeScript 対応表
- 付録C: 検証の記録

各章には、その章のコードで使う TypeScript の
型と書き方を解説する「TS の道具」を置きました。
引用したコードと行番号は、題材の凍結コピー
（全 4,810行）と照合済みです。

# 序章 5つ目の移植は「場所」が違う

## この本の題材

題材は、floooh の pacman.c（C99、単一ファイル
4,303行）を TypeScript へ移植したブラウザ版です。
これまでに、C版の教科書、Python ミニ版、Nim 版、
Go 版と、同じ原典から4冊の本が出ています。
この本は5冊目です。

移植の進め方は先行する版と揃えてあります。
仕様と挙動の正本は pacman.c で、先に決めることは
仕様書 SPEC に T1〜T10 として決めてから書き、
検証は Node のヘッドレス実行で、Nim 版・Go 版と
同じ合格条件（自動プレイ 60,000 ティックで
スコア 350、ドット 66）を使います。

## 何が違うのか

では、この版のどこが「独自」なのでしょうか。
言語そのものの違いは、実はそれほど大きく
ありません。モジュールの分け方は Nim 版に倣い、
関数の対応も原典とほぼ1対1です。

違うのは、プログラムが動く場所です。

- 描画は、シェーダーではなく Canvas 2D です。
  パレットの色は、ピクセルを描くときに解決する
  のではなく、画像を作る時点で焼き込みます
- 音は、コールバックでなく AudioWorklet です。
  合成はブラウザの音声スレッドで走り、ゲーム側
  とはメッセージでしかつながりません
- 入口は実行ファイルではなく HTML です。
  プログラムはページの一部として読み込まれます
- ブラウザには作法があります。音は利用者の
  操作があるまで出せません。タブを隠すと
  描画の合図が止まります。キーボードのない
  機械（スマートフォン）でも遊べなければ
  なりません

この本は、その「場所の違い」がコードのどこに
どう現れるかを追います。ゲームの中身（ルール、
ゴースト、音の計算）は原典どおりなので、章の
割り振りも前半は前の本と似た並びですが、
第9章（描画）、第10章（音）、第11章（入力）は
ブラウザ固有の章になります。

## SPEC の地図

本では仕様の決定を T番号で参照します。全体像は
次のとおりです。

- T1: 描画は Canvas 2D。タイルとスプライトは
  色ごとに画像化しておき、盤面は差分更新
- T2: 論理サイズは 224×288。表示は整数倍
  スケーリングで、F キーで全画面
- T3: 音は AudioWorklet。合成はプロセッサ側で、
  ゲーム側はレジスタのスナップショットを送る
- T4: 音の開始は最初の利用者操作で
  AudioContext を resume する
- T5: 数値は float64 に、C の整数の意味論が
  要る場所では |0、>>>0、Math.imul の規律で
- T6: 凍結フラグは Set で持つ
- T7: 座標 Int2 は素のオブジェクトと自由関数
- T8: 入力はキーボードとタッチ。タッチは
  スワイプで方向、タップで開始
- T9: ROM データは生成ファイル romdata.ts
- T10: ビルドは tsc のみ。バンドラなし、
  ES モジュールで配る

## 行数の内訳

題材の大きさは次のとおりです（凍結コピーの
実測）。

| 部分 | 行数 |
|---|---|
| 手書き（本体12ファイル + worklet.d.ts） | 3,168 |
| 生成（romdata.ts） | 607 |
| ゲーム合計 | 3,775 |
| テスト（7ファイル） | 946 |
| index.html | 30 |
| 生成器（tools/extract.mjs） | 59 |

手書きの内訳は、state 573、render 685、
rules 545、ghost 286、input 271、sound 243、
geom 149、main 162、timing 107、synth 94、
worklet 37、worklet.d.ts 16 です。

原典のコード部分（約3,256行）と比べると、
手書きはほぼ同じ桁です。Nim 版（2,226行）や
Go 版（2,725行）より長いのは、型注釈と、
ブラウザとの境目（描画の画像化、音の橋渡し、
入力の合流）の記述が増えるためです。行数の
読み方は終章でもう一度扱います。

## 読み方

各章は、原典との対応、その章の中心になる
コード、の順に進みます。各章の末尾には
「TS の道具」として、その章で使った
TypeScript の型と書き方をまとめました。
文法だけの章は置いていません。

引用の行番号は、すべて題材の凍結コピーの
行番号です。付録A にソース全文を収めて
あるので、手元で照らし合わせながら
読めます。

# 第1章 全体地図 ― HTML とモジュールと主ループ

## 入口は HTML

この移植の入口は、実行ファイルではなく
HTML です。全文で30行しかありません。

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>pacman.c — TypeScript port</title>
```

（index.html 1〜5行）

ページの中身は、スタイルと、canvas が1つと、
モジュールを読み込む script が1つだけです。

```html
<body>
<canvas id="game" width="224" height="288"></canvas>
<script type="module" src="dist/src/main.js"></script>
</body>
</html>
```

（index.html 26〜30行）

canvas の幅と高さは論理サイズの 224×288
そのものです（SPEC T2）。表示上の大きさは
CSS で決めますが、その値は HTML には書かず、
main.ts がウィンドウに合わせて設定します
（第9章）。

`type="module"` の script は、ES モジュール
として読み込まれます。ビルドは tsc のみで、
バンドラは使いません（T10）。TypeScript の
各ファイルが、そのまま JavaScript の
モジュール1つに対応します。

なお、この構成では `file://` でページを
開いても動きません。モジュールの読み込みが
ブラウザの同一オリジン規則に触れるためで、
静的サーバー経由で開く必要があります。

## モジュールの地図

ファイルの分け方は Nim 版に倣いました。
原典の区画（状態・時間・思考・ルール・
描画・音）が、そのままモジュールになって
います。

| ファイル | 役割 | 原典の区画 |
|---|---|---|
| state.ts | 状態と定数とデータ表 | 構造体と表 |
| timing.ts | 時計とトリガーと乱数 | 時間 |
| geom.ts | 座標と移動の判定 | 幾何 |
| ghost.ts | ゴーストの思考 | 思考 |
| rules.ts | ゲームのルールとティック | ルール |
| render.ts | 描画（状態層と Canvas 層） | 描画 |
| sound.ts | 音のレジスタ層 | 音 |
| synth.ts | 波形の合成 | 音 |
| worklet.ts | 音声スレッド側の受け口 | （ブラウザ固有） |
| input.ts | キーボードとタッチの合流 | 入力 |
| main.ts | 主ループとブラウザとの接続 | 入り口 |
| romdata.ts | ROM データ（生成） | データ |

worklet.ts だけは、原典にも Nim 版にも
対応物がありません。ブラウザの音声
スレッドで動く部品で、第10章の主題です。

## 主ループ: rAF と蓄積時計

ブラウザで周期的に動くには、
`requestAnimationFrame`（rAF）を使います。
ブラウザが「次の描画の前」に呼んでくれる
仕掛けで、呼ばれる間隔は画面の更新に
おおむね同期します。

main.ts の `frame`（93〜113行）が主ループ
です。形は原典の `frame()` の蓄積方式を
そのまま持ち運びました。

```ts
function frame(): void {
  const nowMs = performance.now();
  let frameTimeNs = Math.trunc((nowMs - state.timing.laptimeStore) * 1_000_000);
  state.timing.laptimeStore = nowMs;
  if (frameTimeNs > FRAME_TIME_MAX_NS) frameTimeNs = FRAME_TIME_MAX_NS;
  if (frameTimeNs < 0) frameTimeNs = 0;
  state.timing.tickAccum += frameTimeNs;
  pollInput();
  let ticks = 0;
  while (state.timing.tickAccum > -TICK_TOLERANCE_NS) {
    state.timing.tickAccum -= TICK_DURATION_NS;
    runTick();
    ticks++;
  }
  drawFrame();
  if (audioPort !== null && ticks > 0) {
    audioPort.postMessage(voiceSnapshot());
  }
  requestAnimationFrame(frame);
}
```

（main.ts 93〜113行）

読みどころは3つあります。

1つ目は、経過時間を先に貯金へ入れ、
1ティック分（16,666,666 ナノ秒）を
払いながら `runTick()` を回す「先払い、
後決算」の形です。許容誤差（TICK_TOLERANCE_NS、
1,000,000 ナノ秒）があるので、蓄積が
わずかに負でも1ティック進みます。原典と
Nim 版で見た設計そのままです。

2つ目は、フレーム時間の上限です。
`FRAME_TIME_MAX_NS` は 33,333,333（約2
ティック分）で、タブが裏に回って長時間
止まっても、復帰時に何百ティックも
一気に進むことはありません。

3つ目は、`pollInput()` の位置です。
ティックを回す前に、入力の確定を1回
だけ行います。タップの「押した」が
ちょうど1フレーム分だけ見える設計で、
第11章で扱います。

音のスナップショットは、ティックが
進んだフレームにだけ送ります。1フレーム
で2ティック進んだ場合、中間の状態は
送られません。これは近似で、第10章で
正直に検討します。

## 初期化

`init`（main.ts 142〜161行）は、canvas を
取り、ゲーム側の初期化（`initGame`）、
描画の初期化（`initRenderer`）、入力の
接続（`attachInput`）を行い、表示サイズを
合わせ、音の開始と可視性のリスナーを
登録して、最初の rAF を予約します。
ファイルの最後で `init()` が呼ばれ、
ページの読み込みと同時にゲームが
始まります。

## TS の道具: モジュールと型チェック

TypeScript のモジュールは、ファイルが
そのまま1単位です。`export` したもの
だけが外から見え、`import` は
`from './state.js'` のように、出力後の
JavaScript の名前で書きます（拡張子が
`.js` なのはそのためです）。

ビルドは `tsc` の型チェックと変換だけ
です。型は実行時には消えます。つまり
型は「書くときの検査」であって、
プログラムの部品ではありません。この
割り切りが、状態の持ち方（第2章）や
音の橋渡し（第10章）の設計に効いて
きます。

# 第2章 状態 ― ゼロ値のない言語の初期化

## 状態は1つのオブジェクト

原典では、ゲームの状態は1つの大きな
構造体 `state` に集まっていました。Nim 版
も Go 版も同じ形です。TypeScript 版も
この形を受け継ぎます。state.ts の
`State` インターフェース（455〜463行）が
全体の目次です。

```ts
export interface State {
  gamestate: GameState;
  timing: TimingState;
  intro: IntroState;
  game: Game;
  input: InputState;
  audio: AudioState;
  gfx: GfxState;
}
```

（state.ts 455〜463行）

## factory 関数の並び

C には「ゼロで初期化される」という約束が
あります。構造体を静的に置けば、中身は
全部ゼロから始まります。Nim も Go も、
ゼロ値の約束がある言語でした。

TypeScript には、その約束がありません。
オブジェクトは、作ったときに書いた
ものしか持っていません。そこで state.ts
には、構造の各部分を作る factory 関数が
並びます。`newTrigger`、`newActor`、
`newGhost`、`newSprite`、`newVoice`、
`newSound`、`newGame`、`newInputState`、
`newAudioState`、`newGfxState`、そして
全体を組み立てる `newState`（465〜477行）
です。

```ts
export function newState(): State {
  return {
    gamestate: GameState.GAMESTATE_INTRO,
    timing: { tick: 0, laptimeStore: 0, tickAccum: 0 },
    intro: { started: newTrigger() },
    game: newGame(),
    input: newInputState(),
    audio: newAudioState(),
    gfx: newGfxState(),
  };
}

export const state: State = newState();
```

（state.ts 465〜479行）

プログラム全体で使う状態は、この
`state` 1つだけです。モジュールが
読み込まれたときに1回だけ作られます。

factory 方式には、ゼロ値方式にはない
利点もあります。初期値が「ゼロである
こと」に頼らず、すべて目に見える形で
書かれていることです。たとえば凍結
フラグは `new Set<FreezeType>()` という
空の集合として始まります（state.ts
387行）。C のビットフィールドのゼロが
「何も凍結していない」ことに対応します
（T6。第6章）。

## 音の状態を直列化可能に保つ

この章でいちばん TypeScript 版らしい
設計が、音の関数ポインタの扱いです。

原典の音の定義（sound_desc_t）には、
波形を作る関数へのポインタが入って
います。Nim 版も関数を値として持て
ました。しかし TypeScript 版では、
音の合成はブラウザの音声スレッド
（AudioWorklet）で走り、ゲーム側の
状態とはメッセージでしかつながり
ません。関数はメッセージに乗せて
送れません。

そこで、関数そのものではなく、関数を
指す数値の ID を持つことにしました
（state.ts 289〜298行）。

```ts
export type SoundFuncId = number;
export const NO_SOUND_FUNC: SoundFuncId = -1;

export interface SoundDesc {
  fn: SoundFuncId;
  data: Uint32Array | null; // register dump data (null for procedural sounds)
  size: number; // byte size of register dump data
  voice: [boolean, boolean, boolean];
}
```

（state.ts 289〜298行）

ID から実際の関数への対応は、sound.ts
の `soundGenerators` 配列（162〜170行）が
持ちます。ID の定義（`GEN_EATDOT1` など
6つ）は sound.ts の 155〜160行です。

この置き換えで、ゲームの状態は「データ
だけ」でできている、という性質が保たれ
ました。状態をそのまま送ったり比べたり
できることは、第12章のテストでも
効いてきます。

## 共有する表は凍結する

もう1つ、状態まわりで言語固有の注意が
あります。JavaScript では、配列や
オブジェクトは参照で渡されます。
`ghostScatterTargets` のような共有の
表を、位置の計算の途中で書き換えて
しまうと、事故が静かに広がります。

そこで、共有する位置の表とレベル表の
行は `Object.freeze` で凍結してあります
（state.ts 505〜506行と 564〜566行）。
書き換えようとすると、開発時には例外、
通常時は無言で失敗するので、少なくとも
「うっかり書き換えて他が壊れる」事故の
芽を摘めます。

## TS の道具: 型注釈とインターフェース

`interface` は、オブジェクトの形の
約束です。実行時には何も残りません。
`type SoundFuncId = number` のような
型の別名も同じで、「この数値は音の
関数の ID である」という意図を、
型検査に伝えるための注釈です。

`[boolean, boolean, boolean]` は
タプル型で、「要素が3つの配列」と
いうより「3つの真偽値の組」を表し
ます。原典の `bool voice[3]` の
対応として選ばれました。

# 第3章 時間 ― トリガーと int32 の規律

## ティックという時計

このゲームの時間は、ティック（1/60 秒）
で数えます。timing.ts は、原典の時間の
語彙をそのまま持ち運んだモジュールです。

中心は Trigger です。「将来のティック
番号を書いたメモ」で、状態の中に埋め
込まれています。作る（`start`、
`startAfter`）、消す（`disable`）、
読む（`now`、`since`、`between`、
`afterOnce`、`after`、`before`）の
語彙は、原典・Nim 版・Go 版と共通です。

```ts
// set time trigger to the next game tick
export function start(t: Trigger): void {
  t.tick = state.timing.tick + 1;
}
```

（timing.ts 25〜27行）

```ts
// return the number of ticks since a time trigger was triggered
export function since(t: Trigger): number {
  if (state.timing.tick >= t.tick) {
    return state.timing.tick - t.tick;
  }
  return DISABLED_TICKS;
}
```

（timing.ts 50〜55行）

`DISABLED_TICKS` は 0xFFFFFFFF、つまり
「決して来ない未来」です。無効な
トリガーは、この番兵の値を持ちます。
`since` が番兵を返すことで、「まだ
起きていない」と「無効である」を
同じ経路で扱えます。

## 時計は止まらない

大事な性質を1つ。ティックの時計は、
ゲームが凍結している間も進み続けます。
凍結（freeze）とは「役者が動かない」
ことであって、「時間が止まる」ことでは
ありません。だから、食べた直後の静止も、
死の演出も、すべて「何ティック経ったか」
で測れます。この設計は原典のもので、
各版がそのまま受け継いできました。

## 乱数も状態の中に

乱数（xorshift32）も、種ごと状態の中に
あります（state.game.xorshift）。種は
ラウンドの初期化で植え直されます。
この「乱数が状態の一部」という設計が、
決定性の検証（第12章の 350/66）を
可能にしています。

```ts
export function xorshift32(): number {
  let x = state.game.xorshift | 0;
  x ^= x << 13;
  x ^= x >>> 17;
  x ^= x << 5;
  state.game.xorshift = x >>> 0;
  return x >>> 0;
}
```

（timing.ts 15〜23行）

## int32 の規律（T5）

ここが TypeScript 版の数値の核心です。
JavaScript の数値は、すべて float64
（倍精度浮動小数）です。整数専用の型は
ありません。その代わり、ビット演算を
すると、オペランドは一度 int32 に
変換され、結果も int32 になります。

xorshift の引用を見てください。`x << 13`
のようなシフトは int32 の世界で行われ、
`>>> 0` で符号なし32ビットとして読み
直しています。`x >>> 17` の `>>>` は
符号なし右シフトです。この規律――
C の uint32 の意味論が要る場所では
`| 0`、`>>> 0`、`Math.imul` を使う
（SPEC T5）――のおかげで、原典の
32ビットの桁あふれがそのまま再現され、
乱数の列も原典と一致します。

対照的に、ティックのカウンタ自体は
float64 のまま数えます。2^53 まで
正確に数えられるので、原典の uint32
が約2年で桁あふれするのに対し、
こちらは実質あふれません。これは
意図した差異ではなく、言語の既定に
従った結果の差異です。終章でまとめ
ます。

## TS の道具: ビット演算と数値

JavaScript のビット演算（`& | ^ ~ << >> >>>`）
は、すべて int32 の演算です。割り算の
`/` は float64 の割り算で、剰余の `%` は
切り捨て型です（第4章）。

数値リテラルには `16_666_666` のように
アンダースコアで区切りを入れられます
（state.ts 12行の TICK_DURATION_NS）。
桁の読み間違いを防ぐための、書く側への
配慮です。

# 第4章 幾何 ― 割り算と剰余と Int2

## idiv: 切り捨ての割り算

geom.ts は、座標と移動の判定のモジュール
です。最初に出てくるのが、小さいけれど
大事な関数 `idiv`（22〜24行）です。

```ts
export function idiv(a: number, b: number): number {
  return Math.trunc(a / b);
}
```

（geom.ts 22〜24行）

JavaScript の `/` は float64 の割り算で、
`Math.trunc` で小数部を切り捨てると、
C の整数の割り算と同じ切り捨て型に
なります。負の数が絡む場所で、床関数型
（小さいほうへ丸める）との違いが出る
ため、この1行が意味を持ちます。

## % は C と同じ

続くコメントは、この移植シリーズ全体の
教訓の記録です。

```ts
// Note: no cmod helper is needed here. JavaScript's % operator already
// truncates toward zero exactly like C's %, unlike Python's %.
export function distToTileMid(pos: Int2): Int2 {
  return i2(
    (TILE_WIDTH >> 1) - (pos.x % TILE_WIDTH),
    (TILE_HEIGHT >> 1) - (pos.y % TILE_HEIGHT),
  );
}
```

（geom.ts 26〜33行）

JavaScript の `%` は切り捨て型で、C の
`%` と同じです。だから補助関数は要り
ません。

背景を短く書いておきます。Nim 版の
執筆時、こちらの思い込みで「Nim の mod
は床関数型だ」とされ、不要な補助関数
cmod が入りました。実測すると Nim の
mod は C と同じ切り捨て型で、cmod は
不要だった、という顛末です。思い込みは
教科書と計画書にまで継承されました。
この版では最初から実測に基づいており、
その記録としてコメントが残っています。
言語をまたぐとき、剰余のような既定の
挙動は「同じはず」と決めつけず、実測
すること。これがシリーズを通じた教訓
です。

## 赤ゾーンと移動の判定

`isRedzone`（106〜108行）は、ゴーストが
上を向けない区域の判定です。

```ts
export function isRedzone(tilePos: Int2): boolean {
  return tilePos.x >= 11 && tilePos.x <= 16 && (tilePos.y === 14 || tilePos.y === 26);
}
```

（geom.ts 106〜108行）

x の範囲 11〜16 は原典（pacman.c
1298〜1300行）のとおりです。Python 版
の提出稿ではここが 12〜15 になっていて、
教科書化の前の点検で原典に合わせて
直された、という履歴があります
（Python ミニ版 第8章の解剖メモに
記録があります）。

`canMove`（111〜127行）と `move`
（130〜149行）は、原典の判定と移動を
そのまま移したものです。`move` の
末尾では、トンネルの通り抜け
（画面左端から右端へ）が、座標の
折り返しとして書かれています。

## Int2 は素のオブジェクト

座標の型 Int2 は、state.ts の
インターフェース（185〜188行）で、
`{ x: number, y: number }` という
ただの形です。演算は `i2`、`add`、
`sub`、`scale` という自由関数で
行います（T7）。

Go 版ではメソッド連鎖で書く設計
でしたが、TypeScript では関数を
素直に並べる形を選びました。位置は
「書き換える」のではなく、計算結果の
新しいオブジェクトで置き換えるのが
原則です（共有する表の凍結について
第2章）。

## TS の道具: 構造的型付け

TypeScript の型は構造的です。名前が
違っても、形が合えば同じ型として
扱われます。`Int2` と書く代わりに
`{ x: number, y: number }` と書いても
同じ意味になります。

この性質は、テストでモックの
オブジェクトを渡すとき（第11章、
第12章）に効きます。クラスでなく
形で決まるので、必要な部分だけを
持つ偽物が、そのまま本物の代わりに
なります。

# 第5章 データ ― ROM データの生成

## romdata.ts は生成物

原典 pacman.c の末尾（3389〜4303行）には、
タイルとスプライトの図形、色のパレット、
波形の表、劇中曲と死の音のレジスタダンプが、
値の表として埋め込まれています。合計
9,316 個の値です。

TypeScript 版では、この部分は手で書き
写しません。生成器 tools/extract.mjs
（59行）が pacman.c を読み、romdata.ts
（607行）を機械的に生成します（T9）。

```ts
// romdata.ts -- ROM data extracted mechanically from pacman.c (lines 3389-4303).
// Generated by tools/extract.mjs. Do not edit by hand.

export const romTiles = new Uint8Array([
  0xCC, 0xEE, 0x11, 0x11, 0x33, 0xEE, 0xCC, 0x00, 0x11, 0x33, 0x66, 0x44, 0x44, 0x33, 0x11, 0x00,
```

（romdata.ts 1〜5行）

生成器は、対象の配列ごとに、名前、型、
個数、16進の桁数を表で持ちます。

```js
const specs = [
  { cName: 'rom_tiles', tsName: 'romTiles', typ: 'Uint8Array', count: 4096, hex: 2 },
  { cName: 'rom_sprites', tsName: 'romSprites', typ: 'Uint8Array', count: 4096, hex: 2 },
  { cName: 'rom_hwcolors', tsName: 'romHWColors', typ: 'Uint8Array', count: 32, hex: 2 },
  { cName: 'rom_palette', tsName: 'romPalette', typ: 'Uint8Array', count: 256, hex: 2 },
  { cName: 'rom_wavetable', tsName: 'romWavetable', typ: 'Uint8Array', count: 256, hex: 2 },
  { cName: 'snd_dump_prelude', tsName: 'sndDumpPrelude', typ: 'Uint32Array', count: 490, hex: 8 },
  { cName: 'snd_dump_dead', tsName: 'sndDumpDead', typ: 'Uint32Array', count: 90, hex: 8 },
];
```

（extract.mjs 10〜18行）

生成のたびに、個数が表の期待と合うかを
検査し、合計値を表示します。合計値は
原典側の照合（Nim 版の報告書で確立した
値）と突き合わせます。タイル 267889、
スプライト 227290、ハードウェア色 1852、
パレット 589、波形 1856、劇中曲ダンプ
1523003578600、死のダンプ 275197360640
です。再生成すると、生成物はバイト単位で
同一になります。

## なぜ手で写さないのか

9,316 個の値を手で写せば、必ずどこかで
写し間違えます。そして間違いは、画面の
どこか1ピクセルの色違いのような、見つけ
にくい形で現れます。機械生成＋個数と
合計値の照合は、この種の間違いを
「起きない」ではなく「検出できる」に
変えるための仕掛けです。Nim 版、Go 版
でも同じ方法を取りました。

型付き配列（`Uint8Array`、`Uint32Array`）
で持つ点も言語固有です。通常の配列と
違い、要素の範囲が保証され、メモリの
形も原典の配列に近くなります。

## TS の道具: 生成コードの扱い

生成物には、手を入れないことが分かる
よう、冒頭に生成であることと生成器の
名前を書きます（引用の2行目）。本の
付録A でも、romdata.ts は全文を収めて
ありますが、それは「写し」として
読むためのもので、編集の対象では
ありません。

生成器自体（extract.mjs）は、型の
ない素の JavaScript で書かれています。
ビルドの一部ではなく、題材を作る
ときだけ使う道具なので、本体とは
違う割り切りが許される、という
判断です。

# 第6章 ルール ― runTick と開始連鎖

## 1ティックの姿

rules.ts は、ゲームのルールを担う
モジュールです。その入口 `runTick`
（531〜545行）は、原典の tick の姿を
最も短く表しています。

```ts
// perform exactly one game tick: the tick part of pacman.nim's frame().
export function runTick(): void {
  state.timing.tick += 1;
  sndTick();
  if (now(state.intro.started)) {
    state.gamestate = GameState.GAMESTATE_INTRO;
  }
  if (now(state.game.started)) {
    state.gamestate = GameState.GAMESTATE_GAME;
  }
  if (state.gamestate === GameState.GAMESTATE_INTRO) {
    introTick();
  } else {
    gameTick();
  }
}
```

（rules.ts 531〜545行）

順番が大事です。まず時計を1つ進め、
音を1ティック進め、それから「開始」の
メモ（トリガー）が今日のものかを
見て場面を切り替え、場面の処理を
呼びます。場面の切り替えが「フラグ」
ではなく「時刻つきのメモ」で行われる
のが、この設計の味です（第3章）。

## 開始連鎖

`initGame`（525〜528行）は、描画の
初期化をして、イントロの開始を予約
するだけです。

```ts
export function initGame(): void {
  gfxInit();
  start(state.intro.started);
}
```

（rules.ts 525〜528行）

ゲームの開始、ラウンドの開始、実の
出現、面クリア、ゲームオーバー。
場面の移り変わりは、すべて同じ
仕掛け（トリガーを立てる→時が来たら
場面が替わる）で書かれています。
原典の設計で、各版が受け継いだ部分
です。

## 凍結は Set（T6）

ゲームの進行を止める要因（実を食べた、
ゴーストを食べた、死んだ、など）は、
原典ではビットフィールドの freeze
フラグでした。TypeScript 版では
`Set<FreezeType>` で持ちます
（state.ts 358行の `freeze` フィールド、
156行の列挙型）。

集合なら、「要因を足す」「要因を引く」
「空かどうか」が、そのまま集合の
操作になります。Go 版では集合型が
ないためビット型＋メソッドで置き
換えましたが、TypeScript には Set が
あるので、意図に最も近い形が選べ
ました。言語ごとに「同じ意図の、
違う置き換え」が出る好例です。

## ドットを食べる

ルール側の代表として、`gameUpdateDotsEaten`
（283〜298行）を見ます。

```ts
function gameUpdateDotsEaten(): void {
  state.game.numDotsEaten = (state.game.numDotsEaten + 1) & 0xff;
  if (state.game.numDotsEaten === NUM_DOTS) {
    start(state.game.roundWon);
    sndClear();
  } else if (state.game.numDotsEaten === 70 || state.game.numDotsEaten === 170) {
    start(state.game.fruitActive);
  }
  // alternating crunch sound effect
  if ((state.game.numDotsEaten & 1) !== 0) {
    sndStart(2, sndEatdot1);
  } else {
    sndStart(2, sndEatdot2);
  }
}
```

（rules.ts 283〜298行）

数え方は原典どおりです。244 個目で
面クリアの開始を予約し、70 個目と
170 個目で実を出現させ、食べる音は
2種類を交互に出します。カウンタの
`& 0xff` は、原典の uint8_t の桁
あふれを再現するためのものです
（第3章の規律）。

なお、食べる音の開始が if/else の
外にある点も原典どおりです。Python 版
の点検で一度「音が交互にならないの
では」と疑われた箇所ですが、原典の
pacman.c（2101〜2107行）でも音の
開始は分岐の外にあり、同じ挙動でした。

## TS の道具: Set と列挙型

`enum FreezeType` は、名前つきの
数値の組を作ります。実行時にも
小さなオブジェクトとして残る点が、
純粋な型注釈との違いです。

`Set` は重複のない集合で、`add`、
`delete`、`has`、`size` が基本の
操作です。ビット演算の知識なしに
「要因の集合」をそのまま書けるのが、
この置き換えの利点です。

# 第7章 ゴーストの思考

## 構成は原典のまま

ghost.ts（286行）は、ゴーストの思考を
担います。関数の並びは原典のゴースト
区画（pacman.c 1750〜2087行）に
対応します。

| 関数 | 行 | 役割 |
|---|---|---|
| ghostSpeed | 40 | 状態ごとの速さ |
| scatterChasePhase | 60 | 散開と追跡の交代 |
| updateGhostState | 73 | 状態の切り替え |
| updateGhostTarget | 143 | 目標タイルの計算 |
| updateGhostDir | 197 | 方向の決定 |
| updateGhosthouseDotCounters | 274 | 家のカウンタ（第8章） |

この章の要点は、「思考の内容は原典と
同じで、言語の違いは書き方の表面に
しか出ない」ということです。前の本と
重なる部分は短くし、TypeScript らしい
箇所だけを取り上げます。

## 散開と追跡の予定表

`scatterChasePhase`（60〜71行）は、
ラウンド開始からの経過で、散開
（SCATTER）と追跡（CHASE）を切り
替える予定表です。

```ts
export function scatterChasePhase(): GhostState {
  const t = since(state.game.roundStarted);
  if (t < 7 * 60) return GhostState.GHOSTSTATE_SCATTER;
  if (t < 27 * 60) return GhostState.GHOSTSTATE_CHASE;
  if (t < 34 * 60) return GhostState.GHOSTSTATE_SCATTER;
  if (t < 54 * 60) return GhostState.GHOSTSTATE_CHASE;
  if (t < 59 * 60) return GhostState.GHOSTSTATE_SCATTER;
  if (t < 79 * 60) return GhostState.GHOSTSTATE_CHASE;
  if (t < 84 * 60) return GhostState.GHOSTSTATE_SCATTER;
  return GhostState.GHOSTSTATE_CHASE;
}
```

（ghost.ts 60〜71行）

7秒、20秒、7秒、20秒、5秒、20秒、
5秒、そして以後は追跡のまま、という
原典の予定表（pacman.c 1777行付近）が、
境界の列として読めます。単位が
ティック（`* 60`）であること、恐怖
状態の間もこの時計は進むことも、
原典どおりです。

## 目標と方向

`updateGhostTarget`（143〜196行）は、
ゴーストごとの目標タイルの計算です。
ブリンキーはパックマン自身、ピンキーは
4タイル先、インキーはブリンキーとの
対点、クライドは近づくと散開目標へ、
という原典の規則が、そのまま条件分岐
になっています。目（EYES）の目標は
家の入口（13,14）です（pacman.c
1946行）。

`updateGhostDir`（197〜272行）は、
タイルの中心に来たときにだけ、次の
方向を選びます。候補のうち目標に
最も近いものを選び、同点なら
上、左、下、右の優先順位で決める、
という原典の規則です。恐怖状態では
乱数で目標を作り直すため、ティック
ごとに xorshift を消費します。この
「目標の再計算は毎ティック、方向の
決定は中心でだけ」という非対称も
原典のままです。

方向の決定がティックごとでない点は、
移植の事故が起きやすい場所でも
あります。Python 版では、方向の計算を
移動の段数に関係なく毎ティック呼んで
しまい、クライドが止まる不具合に
なりました（Python ミニ版で扱いました）。
この版は原典の呼び出し位置を守って
います。

## TS の道具: 列挙型の状態機械

ゴーストの状態は `GhostState` という
列挙型で、状態の切り替えは switch で
書かれています。TypeScript の switch
は、列挙型の値に対して「すべての
場合を書き尽くしたか」を型検査で
確かめる助けになります。原典の
状態機械のような「値の組＋分岐」の
コードは、この形に素直に移ります。

# 第8章 家と速さ

## 速さは「進む段数」で決まる

このゲームの速さは、ピクセル/秒の
ような連続量ではなく、「このティックで
何ピクセル進むか」の段数で決まります。
`ghostSpeed`（ghost.ts 40〜58行）が
その表です。

```ts
export function ghostSpeed(ghost: Ghost): number {
  switch (ghost.state) {
    case GhostState.GHOSTSTATE_HOUSE:
    case GhostState.GHOSTSTATE_LEAVEHOUSE:
    case GhostState.GHOSTSTATE_FRIGHTENED:
      // inside house / frightened: half speed
      return state.timing.tick & 1;
    case GhostState.GHOSTSTATE_EYES:
    case GhostState.GHOSTSTATE_ENTERHOUSE:
      // estimated 1.5x in eye state
      return (state.timing.tick & 1) !== 0 ? 1 : 2;
    default:
      if (isTunnel(pixelToTilePos(ghost.actor.pos))) {
        return ((state.timing.tick * 2) % 4) !== 0 ? 1 : 0;
      }
      return state.timing.tick % 7 !== 0 ? 1 : 0;
  }
}
```

（ghost.ts 40〜58行）

読み方はこうです。家の中と恐怖状態は
半分の速さ（ティックの偶奇で 0 か 1）。
目は 1 と 2 の交互で、平均 1.5 ピクセル
/ティック（通常の約1.75倍）。通常は
7ティックに6ピクセル（`tick % 7` が
0 のティックだけ休む）。トンネルでは
さらに半分です。原典（pacman.c
1750行付近）の式が、そのまま読めます。

ティック番号そのものを使って速さを
決めるので、速さのパターンは全員で
同期します。これも「時計は1つ」という
設計の帰結です。

## 家のドットカウンタ

ゴーストが家を出る条件は、ドットを
食べた数です。`updateGhosthouseDotCounters`
（ghost.ts 274〜286行）が数えます。

```ts
export function updateGhosthouseDotCounters(): void {
  if (state.game.globalDotCounterActive) {
    state.game.globalDotCounter = (state.game.globalDotCounter + 1) & 0xff;
  } else {
    for (let i = 0; i < state.game.ghost.length; i++) {
      const g = state.game.ghost[i]!;
      if (g.dotCounter < g.dotLimit) {
        g.dotCounter += 1;
        break;
      }
    }
  }
}
```

（ghost.ts 274〜286行）

上限（dotLimit）は、ブリンキー 0、
ピンキー 0、インキー 30、クライド 60
です。数え進めるのは「上限に達して
いない最初の1匹」だけで、家にいるか
どうかは見ません。この割り切りは
原典の癖で、各版がそのまま再現して
きました。

死んだあとは、全体カウンタ
（globalDotCounter）に切り替わります。
閾値はピンキー 7、インキー 17、
クライド 32 です。ドットを食べない
時間が 4 秒（240ティック）続くと
強制的に家を出る規則も、原典どおり
入っています。

数えるきっかけは「ドットを食べた
とき」だけで、パワーペレットでは
数えません。これも原典どおりです。

## TS の道具: 配列の要素の断定

引用の中の `state.game.ghost[i]!` の
`!` は、非 null 断定です。TypeScript
の配列の添字アクセスは「要素がない
かもしれない」型になりますが、ここ
ではループの範囲で存在が保証される
ため、断定で型検査に伝えます。

断定は「検査を止める」宣言なので、
保証が崩れれば実行時の事故になり
ます。使う場所は、保証の根拠が
近くで読める場所に限る、という
運用が、この題材全体で通してあり
ます。

# 第9章 描画 ― Canvas 2D と事前画像化

## 2層の構造

render.ts（685行）は、この移植で最も
大きいファイルです。中身は2層に分かれて
います。

下の層は「状態層」です。原典の描画区画の
うち、盤面の文字やタイルを状態として
持つ部分（`vid*`、`spr*`、`gameUpdateTiles`、
`gameUpdateSprites`）で、Canvas のことは
何も知りません。原典や Nim 版とほぼ
同じコードです。

上の層が「Canvas 層」で、ブラウザ固有の
部分です。この章は主にこちらを扱います。

## パレットは焼き込む（T1）

原典（sokol 版）は、索引つきのピクセルを
シェーダーで色に変換して描きます。
TypeScript 版にはシェーダーがありません。
代わりに、Go 版と同じく、色を画像の時点で
焼き込みます。タイル 256 種×色 32 色、
スプライト 64 種×色 32 色の組み合わせを、
起動時に小さな canvas として全部作って
おくのです（`initRenderer`、render.ts
579〜600行付近）。

```ts
  tileImages = [];
  for (let code = 0; code < 256; code++) {
    const row: HTMLCanvasElement[] = [];
    for (let c = 0; c < 32; c++) {
      row.push(bakeImage(code * TILE_WIDTH, 0, TILE_WIDTH, TILE_HEIGHT, c));
    }
    tileImages.push(row);
  }
```

（render.ts 587〜594行）

下地になる図形の解読は `gfxDecodeTile`
（431〜436行）などで行い、ROM の
ビットパターンを索引ピクセルに展開
します。ここは原典の解読そのままです。

起動時に約1万個の小さな canvas を作る
ので、起動の重さが気になる向きも
あるでしょう。実際に使う組み合わせ
だけを使うときに作る（遅延生成）手も
ありますが、実測で遅さが問題になって
いないため、現状は一括生成のままです。
レビューでも指摘された点で、「実機で
遅いと感じたら直す」と判断が記録
されています。

## 盤面は差分更新

画面の組み立ては `drawFrame`
（640〜685行）です。盤面は 224×288 の
裏 canvas に、セルの変わった所だけを
描き直し（`updateBoard`）、それを
表示 canvas へ転送して、スプライトを
重ね、最後にフェードの黒を重ねます。
描く順番は原典の gfx_draw の順です。

パレットの索引 0 は透明なので、盤面の
セルを描くときは、先に黒で消してから
画像を重ねます。ここを忘れると前の
絵が透けて残ります。状態層が「タイルと
色」の世界で、Canvas 層が「画像」の
世界であることの、境目らしい注意点
です。

## 表示サイズは整数倍（T2）

canvas 自体は 224×288 のままです。
表示の大きさは、main.ts の `fitCanvas`
（126〜140行）が CSS の幅と高さで
決めます。

```ts
function fitCanvas(canvas: HTMLCanvasElement): void {
  const fit = Math.min(window.innerWidth / DISPLAY_PIXELS_X, window.innerHeight / DISPLAY_PIXELS_Y);
  const scale = Math.floor(fit);
  let w: number;
  let h: number;
  if (scale >= 1) {
    w = DISPLAY_PIXELS_X * scale;
    h = DISPLAY_PIXELS_Y * scale;
  } else {
    w = Math.max(1, Math.floor(DISPLAY_PIXELS_X * fit));
    h = Math.max(1, Math.floor(DISPLAY_PIXELS_Y * fit));
  }
  canvas.style.width = `${w}px`;
  canvas.style.height = `${h}px`;
}
```

（main.ts 126〜140行）

ウィンドウに収まる最大の整数倍を
選び、`image-rendering: pixelated`
（index.html）の指定で、拡大しても
ピクセルがくっきり見えるように
します。ウィンドウのリサイズにも
追随します。

この処理は、最初からあったわけでは
ありません。当初は 448×576 の固定
サイズで、スマートフォンの縦画面
（幅 360〜430 ピクセル）では左右が
切れていました。レビューで指摘を
受け、SPEC T2 の本来の形（整数倍
スケーリング）に直したものです。
F キーの全画面でも、この計算の
おかげで実際に拡大されるように
なりました。

## フェードは float32 の丸めで

フェード（画面の暗転）は、原典では
float32 の計算です。`gfxFade`
（499〜519行）は、各段で
`Math.fround` を挟み、float32 の
丸めを再現します。

```ts
export function gfxFade(): void {
  // The original computes in float32; Math.fround at each step
  // reproduces its rounding exactly (in float64, six of the fadein
  // steps would come out one unit brighter).
  if (between(state.gfx.fadein, 0, FADE_TICKS)) {
    const t = Math.fround(since(state.gfx.fadein) / FADE_TICKS);
    state.gfx.fade = Math.trunc(Math.fround(255.0 * Math.fround(1.0 - t)));
  }
```

（render.ts 499〜507行）

float64 のまま計算すると、フェード
イン全31段のうち6段が、原典より
1/255 だけ明るくなります。目では
分からない差ですが、「原典と一致
させる」という検証の物差しでは
検出できる差でした。全31段の値を
テストで固定してあります（第12章）。

## TS の道具: DOM の型

`HTMLCanvasElement` や
`CanvasRenderingContext2D` は、
ブラウザの DOM の型です。TypeScript
には DOM の型定義が付属しており、
`canvas.getContext('2d')` の戻りが
「null かもしれない」ことも型に
現れます。`initRenderer` の
`canvas.getContext('2d')!` の `!` は、
第8章で見た非 null 断定です。

# 第10章 音 ― AudioWorklet とブラウザの作法

## 音は別のスレッドで鳴る

この移植で、原典と構造が最も違うのが
音です。原典（sokol_audio）は、音声の
コールバックの中で波形を作る「pull 型」
でした。TypeScript 版も pull 型ですが、
波形を作る場所がブラウザの音声スレッド
（AudioWorklet）という、別の実行環境に
なります（T3）。

部品は3つです。

- sound.ts: ゲーム側のレジスタ層。
  原典の音の計算（手続き関数6つ、
  `snd_tick`、ダンプの再生）はここに
  あり、ゲームのティックで進みます
- synth.ts: 波形の合成（Synth クラス）。
  音声スレッド側で、サンプルレートに
  合わせてサンプルを作ります
- worklet.ts: 音声スレッドの受け口。
  ゲーム側からのメッセージを Synth に
  渡し、`process` で出力を埋めます

## 境目を渡るのはレジスタだけ

ゲーム側と音声側のあいだを渡れるのは、
メッセージに乗るデータだけです。
そこで、渡すものを「音のレジスタの
スナップショット」に絞りました。
sound.ts の `voiceSnapshot`
（237〜243行）が、3ボイス分の
周波数・波形・音量を、ただの
オブジェクトとして返します。

```ts
export function voiceSnapshot(): VoiceRegs[] {
  return state.audio.voice.map((v) => ({
    frequency: v.frequency,
    waveform: v.waveform,
    volume: v.volume,
  }));
}
```

（sound.ts 237〜243行）

位相のカウンタ（counter、sampleAcc、
sampleDiv）は音声側に置きます。ゲーム
側のティックと音声側のサンプルは
進み方が違うので、混ぜないほうが
素直なのです。送るのは main.ts の
`frame` で、ティックが進んだフレーム
に1回です（第1章）。

worklet.ts（37行）は受け口です。

```ts
class PacmanSynthProcessor extends AudioWorkletProcessor {
  private readonly synth: Synth;

  constructor() {
    super();
    this.synth = new Synth(sampleRate);
    this.port.onmessage = (event: MessageEvent) => {
      this.synth.setVoices(event.data as VoiceRegs[]);
    };
  }
```

（worklet.ts 12〜22行）

サンプルレートは、AudioContext の
ものをそのまま使います。Synth の
`voiceTickPeriod` は、96kHz の
ティックを何サンプル分進めるかを
サンプルレートから割り算で求めます
（synth.ts 33行）。原典の snd_init の
計算と同じ形です。

関数ポインタを数値 ID に置き換えた
設計（第2章）は、この境目のため
でした。ID とレジスタはデータなので、
スナップショットにできます。

## 正直な差異: 音の段飛び

この橋渡しには、近似が1つあります。
スナップショットはフレームに1回
しか送らないので、1フレームで
2ティック進むと、中間のティックの
レジスタ状態は音声側に届きません。
音の掃引（周波数の滑らかな変化）が、
負荷の高い場面では段になって
聞こえる可能性があります。

通常の 60Hz 動作では1フレーム
1ティックなので、実質は原典と
同じです。レビューでも「性能の話
として、気になったら直す」範囲と
判断されました。直すなら、ティック
ごとにスナップショットを貯めて
まとめて送る形になります。

## ブラウザの作法、その1: 自動再生ポリシー

ブラウザでは、音は利用者の操作が
あるまで出せません。AudioContext は
作っても `suspended` のまま止まって
おり、操作の中で `resume()` して
初めて鳴ります（T4）。

main.ts の音の開始（`setupAudio`）は
この作法に合わせた形です。要点は
3つあります。

1. AudioContext の生成と `resume()` は、
   操作の処理の中で同期的に呼ぶ。
   モジュールの読み込み（`await
   addModule(...)`）を先にすると、
   resume が「操作の直後」の範囲から
   外れ、特に iOS で開始に失敗する
   ことがあります
2. 開始のきっかけは一度きりにしない。
   `keydown`、`pointerdown`、
   `touchend`、`click` のたびに、
   止まっていれば resume を再試行
   します。再開の条件は「running で
   なければ」で、iOS の割り込み後の
   `interrupted` も拾います
   （`resumeAudio`、main.ts 35〜43行）
3. モジュールの読み込みに失敗したら、
   状態を初期化して、次の操作で
   最初からやり直します。一度の
   失敗でセッション中ずっと無音に
   ならないためです

この3点は、いずれもレビューの指摘を
受けて直したものです。最初の版は
「await のあとに resume」「一度きり」
の形で、実機の条件に弱い作りに
なっていました。

## ブラウザの作法、その2: 可視性

タブを裏に回すと、rAF が止まり、
ゲームの更新が止まります。ところが
音声スレッドは止まらないので、最後に
送ったスナップショットの音が鳴り
続けてしまいます。

対策は `visibilitychange` です
（main.ts 75〜83行）。タブが隠れたら
AudioContext を `suspend()` し、
戻ったら再開します。ゲームの側の
時計には上限（第1章）があるので、
復帰時に一気に進みすぎることも
ありません。

## TS の道具: 型定義ファイル

AudioWorklet の側には、`sampleRate`
や `registerProcessor` のような、
その実行環境専用の名前があります。
DOM の標準の型定義には入っていない
ため、worklet.d.ts（16行）という
型定義ファイルで宣言を補います。
worklet.ts の冒頭の
`/// <reference path="./worklet.d.ts" />`
が、その宣言を取り込む指定です。

型定義ファイルは「この名前はこういう
型である」という宣言だけで、実行
されるコードは含みません。

# 第11章 入力 ― キーボードとタッチの合流

## 入力は2系統

input.ts（271行）は、入力の合流点です。
受け付けるのはキーボードとタッチの
2系統で、ゲーム側に見せるのは、原典と
同じ「方向のフラグと anykey」だけです
（T8）。

キーボードは矢印キーと WASD です。
タッチは、スワイプで方向、タップで
開始（anykey）です。スマートフォンには
キーボードがないので、タッチがなければ
そもそも遊べません。この版の最初の
形はキーボードのみで、Android では
詰む、という指摘を受けてタッチを
足した経緯があります。設計は Go 版の
H8 と同じで、しきい値と優先順位を
揃えてあります。

## スワイプとラッチ

スワイプの判定は `swipeDirection`
（30〜37行）です。

```ts
export function swipeDirection(dx: number, dy: number): Dir | null {
  if (Math.max(Math.abs(dx), Math.abs(dy)) < TOUCH_SWIPE_THRESHOLD) return null;
  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? Dir.DIR_RIGHT : Dir.DIR_LEFT;
  }
  return dy > 0 ? Dir.DIR_DOWN : Dir.DIR_UP;
}
```

（input.ts 30〜37行）

移動量が 24 論理ピクセル（タイル
約3つ分）に届かなければ無効、大きい
ほうの軸を取り、同点なら縦を優先
します。

スワイプで決めた方向は「ラッチ」
として保持され、次のスワイプまで
残ります。指を離しても方向が残る
ので、押し続ける必要がありません。
キーボードとの合流は `resolveDirections`
（47〜57行）で、押されているキー
があればそちらが勝ち、何も押されて
いなければラッチが効きます。

## タップは1フレームだけ

タップの anykey は、`pollInput`
（88〜105行）が管理します。タップが
あったら、次のフレームのティックに
だけ anykey が見え、その次の
フレームでは消えます。入力が無効な
間のタップは、書き込まずに捨てます。

```ts
export function pollInput(): void {
  if (tapClearArmed) {
    tapClearArmed = false;
    tapActive = false;
    if (state.input.enabled) writeAnykey();
  }
  if (tapPending) {
    tapPending = false;
    if (state.input.enabled) {
      tapActive = true;
      writeAnykey();
      tapClearArmed = true;
    }
  }
}
```

（input.ts 88〜105行）

初期の実装はタイマー（setTimeout）で
約120ミリ秒（約7ティック）anykey を
出し続けていました。Go 版の「1ティック
だけ」と揃えるため、フレーム単位の
この形に直したものです。

## 教訓: kb 控えと forgetKey

この章の中心は、レビューで見つかった
バグです。再現手順はこうでした。

1. 「↑」を押してゲームを開始する
2. 画面が暗くなる約0.5秒（入力が
   無効な間）に「↑」を離す
3. ゲームが始まったあと、「←」だけを
   押しても「↑」と判定される

原因は、入力の持ち方にあります。
この版の input.ts は、押下状態の控え
（`kb`）をモジュール内に持ち、確定の
ときにゲーム側の状態へ写します。
ところが `onKey` は、入力が無効な間は
キーイベントを丸ごと捨てていました。
ゲーム側の状態は `inputDisable` で
初期化されるのに、控えのほうは初期化
されず、「↑が押されたまま」が残った
のです。原典では、コールバックが
フラグそのものを書き、無効化で
フラグをゼロにするので、この食い違い
は起きません。

直しは、無効な間でも「離した」だけは
控えに記録することです（`forgetKey`、
116〜137行）。

```ts
function onKey(e: KeyboardEvent, btnDown: boolean): void {
  // keep the page from scrolling on the arrow keys (this is a page
  // concern, so it applies whether or not input is enabled)
  if (e.code.startsWith('Arrow')) e.preventDefault();
  if (!state.input.enabled) {
    if (!btnDown) forgetKey(e.code);
    return;
  }
```

（input.ts 138〜146行）

テストが見逃した理由も、記録に値
します。テストは `state.input` を
直接書き換えていて、input.ts を
通っていなかったのです。直しと
同時に、DOM のスタブ経由で本物の
リスナーを駆動する回帰テストを
追加しました（第12章）。

引用の冒頭にある `preventDefault` は、
矢印キーでページがスクロールする
のを防ぐものです。入力の有効・無効
とは別の「ページの都合」なので、
無効な間でも効く位置に置いて
あります。

## TS の道具: イベントの型

ブラウザのイベントには、DOM の型が
付いています。`KeyboardEvent` の
`code` は、キーの物理的な位置を
表す文字列です（`'ArrowUp'`、
`'KeyW'` など）。レイアウトに
依存しないので、ゲームの入力には
`key`（文字）より `code` が向いて
います。

テストで偽のイベントを作るときも、
形が合えば渡せます（第4章の構造的
型付け）。回帰テストでは
`{ code, preventDefault }` だけを
持つオブジェクトを、イベントとして
渡しています。

# 第12章 テストと検証

## 検証の土台は Node

ブラウザ向けの移植ですが、検証の
土台は Node です。ゲームのロジックは
ブラウザの API に触れない形に
分けてあるので（描画と音の橋渡しが
境目）、Node のヘッドレス実行で
そのまま回せます。テストは7ファイル、
全27件です。

| ファイル | 件数 | 中身 |
|---|---|---|
| foundation.test.ts | ― | 基礎（定数、乱数、トリガー） |
| headless.test.ts | 3 | 自動プレイ、決定性、勝利 |
| probes.test.ts | ― | 挙動プローブ17件 |
| audio.test.ts | ― | 合成の数値 |
| input.test.ts | 5 | スワイプ、合流、キーの残り |
| render.test.ts | ― | フェード全31段 |
| race.test.ts | 1 | 最終面の同着 |

## 合格条件は 350/66

中心の検証は headless.test.ts の
自動プレイです。ゲームを起動し、
自動操縦で 60,000 ティック遊ばせて、
スコア 350、ドット 66 を確認します
（93行のテスト）。この数値は Nim 版
のヘッドレス検証で得られたもので、
Go 版、TypeScript 版と、同じ物差しで
測ってきました。決定性（同じ種と
入力で同じ結果）と、勝利のシナリオ
（最後のドットで面クリア）も同じ
ファイルにあります。

乱数の列そのものも照合してあります。
種 0x12345678 からの最初の5値は
2274908837、358294691、1210119364、
2176035992、1882851208 で、C の
意味論と一致します（第3章）。

## 同着レースをテストに固定する

最終面（残りライフ 0）で、最後の
ドットを食べるティックと死が同着
になった場合の挙動は、原典の癖が
最も濃く出る場所です。実測の結果は
こうでした。食べたティックを T と
して、面クリアの開始が T+1、
ゲームオーバーが T+210、次の
ラウンドの初期化が T+241、
イントロへの帰還が T+420 で、
ライフは 0 のまま増えません。

この値は当初、手元の使い捨て
スクリプトで確認しただけでした。
レビューで「テストにない」と指摘を
受け、race.test.ts（40行のテスト）
として固定しました。使い捨ての
確認と、残るテストの違いは、
このシリーズで繰り返し出てきた
論点です。

## レビューで増えたテスト

外部レビューは、この版では2度
ありました。テストの側の収穫は
2つです。

1つは第11章の回帰テストです。
入力のテストが input.ts を通って
いなかった、という盲点そのものを
塞ぐため、DOM スタブ経由で本物の
リスナーを駆動する形（input.test.ts
57行のテスト）にしました。

もう1つは render.test.ts のフェード
全31段です。float32 の丸めの差は、
「明るさが1段違う」という形でしか
現れません。全段の値を書き並べて
固定することで、将来の変更で
静かにずれることを防ぎます。

## ブラウザでしか確かめられないこと

最後に、検証の届かない範囲を明記
します。Node のテストで確かめられる
のは、ロジックと数値までです。

- 実ブラウザでの画面の見え方
- AudioWorklet の読み込みと実音
- 実機でのタッチの操作感
- iOS での音の開始と割り込み

これらは手元での確認の扱いです。
テストが合格したことと、手元で
動いたことは、別の確認として
区別して記録します。この区別は、
シリーズ全体で守ってきた約束です。

## TS の道具: node:test

テストは Node 標準の `node:test` と
`node:assert` で書かれています。
追加のテストフレームワークは
使いません。ビルド（tsc）の出力に
対して `node --test` を実行する
だけです。

題材の規模では、この素朴な形で
十分でした。テストファイルも
TypeScript で書き、型検査の対象に
含めることで、テストの側の型の
ずれもビルドで検出できます。

# 終章 5つの移植で書くということ

## 揃ったもの、違ったもの

pacman.c は、これで5つの実装に
なりました。原典の C、Python、
Nim、Go、そして TypeScript です。
仕様と挙動は全版で揃えてあり、
検証の物差し（350/66、プローブ、
同着レースの値）も共通です。

違ったのは、はみ出し方です。

- Python 版は、設計だけを移す移植
  でした。素材も音も作り直しです
- Nim 版は、原典に最も近い移植
  でした。シェーダーまで含めて、
  区画と関数が対応します
- Go 版は、仕様の決定（H1〜H9）を
  先に固定し、フレームワーク
  （Ebitengine）の流儀に乗せる
  移植でした
- TypeScript 版は、場所が違う移植
  でした。相手は言語の流儀という
  より、ブラウザという実行環境の
  作法です

## 場所が変わると何が変わるか

この版で学んだことを、3つに
まとめます。

1つ目は、境目の設計が本体を決める、
ということです。音声スレッドとの
境目を「レジスタのスナップショット」
に絞ったことが、関数ポインタを
数値 ID に置き換える設計（第2章）を
生み、結果として状態がデータだけで
できたことは、テストのしやすさにも
つながりました。

2つ目は、プラットフォームの作法は
コードの形に出る、ということです。
自動再生ポリシー、可視性、整数倍
スケーリング、タッチ。どれも
ゲームのルールとは無関係ですが、
欠ければ「動かない」「鳴らない」
「切れる」という形で、利用者には
本体の不具合と区別がつきません。
レビューで見つかった問題が、ゲーム
の中身ではなくブラウザに出す部分に
集中していたのは、その表れです。

3つ目は、既定の挙動は言語ごとに
違い、実測だけが頼りだという
ことです。剰余の切り捨て（第4章）、
フェードの float32（第9章）、
ティックカウンタの桁あふれの有無
（第3章）。「同じはず」で進めると、
思い込みは文書にまで継承されます。

## 行数の読み方

最後に、行数の話を置いておきます。
手書きの行数は、C のコード部分
約3,256行に対し、Python 581、
Nim 2,226、Go 2,725、TypeScript
3,168 でした。

この数字は、言語の優劣ではあり
ません。何を数えたか（生成物や
素材を含むか）、土台がどこまでを
引き受けるか（シェーダーか、
画像化か、フレームワークか）、
境目の記述がどれだけ要るか、で
動きます。TypeScript 版が Nim 版
より長いのは、型注釈と、ブラウザ
との境目（描画の画像化、音の
橋渡し、入力の合流）の分です。

行数は、移植の「設計の置き場」を
映す鏡として読むのが、この
シリーズでの結論です。

## 残っていること

ブラウザでの実画面、実音、実機の
タッチは、手元での確認待ちです
（第12章）。性能の2件（起動時の
画像の一括生成、音の段飛び）は、
実機で遅いと感じたときに直す、
という判断のまま置いてあります。

原典は1つのファイルでした。それを
5つの場所で書き直して分かったのは、
ゲームの中身は驚くほどそのまま
運べること、そして運べない部分こそ
が、それぞれの場所の姿を教えて
くれることでした。

# 付録A TypeScript ソース全文

題材の凍結コピー（本体13ファイル、index.html、生成器、テスト7本、全 4,810行）を、そのまま収めます。romdata.ts は生成物です。

## state.ts

```ts
// state.ts -- constants, types and the single global state object.
// Corresponds to pacman.c lines 142-678 (config, enums, structs, data tables).
// Inside this module the writing follows TypeScript conventions where the
// C code's intent allows it (e.g. freeze flags are a Set, not a bitfield).
// See SPEC.md (T5) for the numeric-semantics rules: values that are
// integers by design pass through |0 / >>>0 at the boundaries.

// --- config (pacman.c 144-152) ---
export const AUDIO_VOLUME = 0.5;

// --- global constants (pacman.c 161-193) ---
export const TICK_DURATION_NS = 16_666_666;
export const TICK_TOLERANCE_NS = 1_000_000;
export const NUM_VOICES = 3;
export const NUM_SOUNDS = 3;
export const NUM_SAMPLES = 128;
export const DISABLED_TICKS = 0xFFFFFFFF;
export const TILE_WIDTH = 8;
export const TILE_HEIGHT = 8;
export const SPRITE_WIDTH = 16;
export const SPRITE_HEIGHT = 16;
export const DISPLAY_TILES_X = 28;
export const DISPLAY_TILES_Y = 36;
export const DISPLAY_PIXELS_X = DISPLAY_TILES_X * TILE_WIDTH;
export const DISPLAY_PIXELS_Y = DISPLAY_TILES_Y * TILE_HEIGHT;
export const NUM_SPRITES = 8;
export const NUM_DEBUG_MARKERS = 16;
export const TILE_TEXTURE_WIDTH = 256 * TILE_WIDTH;
export const TILE_TEXTURE_HEIGHT = TILE_HEIGHT + SPRITE_HEIGHT;
export const FADE_TICKS = 30;
export const NUM_LIVES = 3;
export const NUM_STATUS_FRUITS = 7;
export const NUM_DOTS = 244;
export const NUM_PILLS = 4;
export const ANTEPORTAS_X = 14 * TILE_WIDTH;
export const ANTEPORTAS_Y = 14 * TILE_HEIGHT + (TILE_HEIGHT >> 1);
export const GHOST_EATEN_FREEZE_TICKS = 60;
export const PACMAN_EATEN_TICKS = 60;
export const PACMAN_DEATH_TICKS = 150;
export const GAMEOVER_TICKS = 3 * 60;
export const ROUNDWON_TICKS = 4 * 60;
export const FRUITACTIVE_TICKS = 10 * 60;

// --- tile, sprite and color codes (pacman.c 198-248) ---
export const TILE_SPACE = 0x40;
export const TILE_DOT = 0x10;
export const TILE_PILL = 0x14;
export const TILE_GHOST = 0xB0;
export const TILE_LIFE = 0x20;
export const TILE_CHERRIES = 0x90;
export const TILE_STRAWBERRY = 0x94;
export const TILE_PEACH = 0x98;
export const TILE_BELL = 0x9C;
export const TILE_APPLE = 0xA0;
export const TILE_GRAPES = 0xA4;
export const TILE_GALAXIAN = 0xA8;
export const TILE_KEY = 0xAC;
export const TILE_DOOR = 0xCF;

export const SPRITETILE_INVISIBLE = 30;
export const SPRITETILE_SCORE_200 = 40;
export const SPRITETILE_SCORE_400 = 41;
export const SPRITETILE_SCORE_800 = 42;
export const SPRITETILE_SCORE_1600 = 43;
export const SPRITETILE_CHERRIES = 0;
export const SPRITETILE_STRAWBERRY = 1;
export const SPRITETILE_PEACH = 2;
export const SPRITETILE_BELL = 3;
export const SPRITETILE_APPLE = 4;
export const SPRITETILE_GRAPES = 5;
export const SPRITETILE_GALAXIAN = 6;
export const SPRITETILE_KEY = 7;
export const SPRITETILE_PACMAN_CLOSED_MOUTH = 48;

export const COLOR_BLANK = 0x00;
export const COLOR_DEFAULT = 0x0F;
export const COLOR_DOT = 0x10;
export const COLOR_PACMAN = 0x09;
export const COLOR_BLINKY = 0x01;
export const COLOR_PINKY = 0x03;
export const COLOR_INKY = 0x05;
export const COLOR_CLYDE = 0x07;
export const COLOR_FRIGHTENED = 0x11;
export const COLOR_FRIGHTENED_BLINKING = 0x12;
export const COLOR_GHOST_SCORE = 0x18;
export const COLOR_EYES = 0x19;
export const COLOR_CHERRIES = 0x14;
export const COLOR_STRAWBERRY = 0x0F;
export const COLOR_PEACH = 0x15;
export const COLOR_BELL = 0x16;
export const COLOR_APPLE = 0x14;
export const COLOR_GRAPES = 0x17;
export const COLOR_GALAXIAN = 0x09;
export const COLOR_KEY = 0x16;
export const COLOR_WHITE_BORDER = 0x1F;
export const COLOR_FRUIT_SCORE = 0x03;

// --- enums (pacman.c 254-320) ---
export enum GameState {
  GAMESTATE_INTRO,
  GAMESTATE_GAME,
}

// NOTE: bit0==0: horizontal movement, bit0==1: vertical movement
export enum Dir {
  DIR_RIGHT,
  DIR_DOWN,
  DIR_LEFT,
  DIR_UP,
  NUM_DIRS,
}

export enum Fruit {
  FRUIT_NONE,
  FRUIT_CHERRIES,
  FRUIT_STRAWBERRY,
  FRUIT_PEACH,
  FRUIT_APPLE,
  FRUIT_GRAPES,
  FRUIT_GALAXIAN,
  FRUIT_BELL,
  FRUIT_KEY,
  NUM_FRUITS,
}

export enum SpriteIndex {
  SPRITE_PACMAN,
  SPRITE_BLINKY,
  SPRITE_PINKY,
  SPRITE_INKY,
  SPRITE_CLYDE,
  SPRITE_FRUIT,
}

export enum GhostType {
  GHOSTTYPE_BLINKY,
  GHOSTTYPE_PINKY,
  GHOSTTYPE_INKY,
  GHOSTTYPE_CLYDE,
  NUM_GHOSTS,
}

export enum GhostState {
  GHOSTSTATE_NONE,
  GHOSTSTATE_CHASE,
  GHOSTSTATE_SCATTER,
  GHOSTSTATE_FRIGHTENED,
  GHOSTSTATE_EYES,
  GHOSTSTATE_HOUSE,
  GHOSTSTATE_LEAVEHOUSE,
  GHOSTSTATE_ENTERHOUSE,
}

// In C these are (1<<n) bit values in a uint8. Here they are the members
// of a Set, so the enum values are just distinct tags (SPEC T6).
export enum FreezeType {
  FREEZETYPE_PRELUDE,
  FREEZETYPE_READY,
  FREEZETYPE_EAT_GHOST,
  FREEZETYPE_DEAD,
  FREEZETYPE_WON,
}

export enum SoundFlag {
  SOUNDFLAG_VOICE0,
  SOUNDFLAG_VOICE1,
  SOUNDFLAG_VOICE2,
}

export const SOUNDFLAG_ALL_VOICES: ReadonlySet<SoundFlag> = new Set([
  SoundFlag.SOUNDFLAG_VOICE0,
  SoundFlag.SOUNDFLAG_VOICE1,
  SoundFlag.SOUNDFLAG_VOICE2,
]);

// --- basic types (pacman.c 323-352) ---
export interface Trigger {
  tick: number; // uint32 by design (DISABLED_TICKS when inactive)
}

export function newTrigger(): Trigger {
  return { tick: 0 };
}

export interface Int2 {
  x: number; // int16 by design
  y: number;
}

export function i2(x: number, y: number): Int2 {
  return { x, y };
}

export function add(v0: Int2, v1: Int2): Int2 {
  return i2(v0.x + v1.x, v0.y + v1.y);
}

export function sub(v0: Int2, v1: Int2): Int2 {
  return i2(v0.x - v1.x, v0.y - v1.y);
}

export function scale(v: Int2, s: number): Int2 {
  return i2(v.x * s, v.y * s);
}

export function squaredDistance(v0: Int2, v1: Int2): number {
  const dx = v1.x - v0.x;
  const dy = v1.y - v0.y;
  return dx * dx + dy * dy;
}

export function nearEqual(v0: Int2, v1: Int2, tolerance: number): boolean {
  return Math.abs(v1.x - v0.x) <= tolerance && Math.abs(v1.y - v0.y) <= tolerance;
}

export function actorToSpritePos(pos: Int2): Int2 {
  return i2(pos.x - (SPRITE_WIDTH >> 1), pos.y - (SPRITE_HEIGHT >> 1));
}

export interface Actor {
  dir: Dir;
  pos: Int2;
  animTick: number; // uint32
}

export function newActor(): Actor {
  return { dir: Dir.DIR_RIGHT, pos: i2(0, 0), animTick: 0 };
}

export interface Ghost {
  actor: Actor;
  typ: GhostType;
  nextDir: Dir;
  targetPos: Int2;
  state: GhostState;
  frightened: Trigger;
  eaten: Trigger;
  dotCounter: number; // uint16
  dotLimit: number; // uint16
}

export function newGhost(): Ghost {
  return {
    actor: newActor(),
    typ: GhostType.GHOSTTYPE_BLINKY,
    nextDir: Dir.DIR_RIGHT,
    targetPos: i2(0, 0),
    state: GhostState.GHOSTSTATE_NONE,
    frightened: newTrigger(),
    eaten: newTrigger(),
    dotCounter: 0,
    dotLimit: 0,
  };
}

export interface Pacman {
  actor: Actor;
}

// --- renderer types (pacman.c 360-385) ---
export interface Sprite {
  enabled: boolean;
  tile: number; // uint8
  color: number; // uint8
  flipx: boolean;
  flipy: boolean;
  pos: Int2;
}

export function newSprite(): Sprite {
  return { enabled: false, tile: 0, color: 0, flipx: false, flipy: false, pos: i2(0, 0) };
}

export interface DebugMarker {
  enabled: boolean;
  tile: number; // uint8
  color: number; // uint8
  tilePos: Int2;
}

export function newDebugMarker(): DebugMarker {
  return { enabled: false, tile: 0, color: 0, tilePos: i2(0, 0) };
}

// --- sound types (pacman.c 388-418) ---
// A sound generator is identified by its index into the generator table
// in synth.ts, so that sound state stays serializable for the
// AudioWorklet boundary (SPEC T3). -1 means "no generator".
export type SoundFuncId = number;
export const NO_SOUND_FUNC: SoundFuncId = -1;

export interface SoundDesc {
  fn: SoundFuncId;
  data: Uint32Array | null; // register dump data (null for procedural sounds)
  size: number; // byte size of register dump data
  voice: [boolean, boolean, boolean];
}

export interface Voice {
  counter: number; // uint32
  frequency: number; // uint32
  waveform: number; // uint8
  volume: number; // uint8
  sampleAcc: number; // float32 by design
  sampleDiv: number; // float32 by design
}

export function newVoice(): Voice {
  return { counter: 0, frequency: 0, waveform: 0, volume: 0, sampleAcc: 0, sampleDiv: 0 };
}

export interface Sound {
  curTick: number; // uint32
  fn: SoundFuncId;
  numTicks: number; // uint32
  stride: number; // uint32
  data: Uint32Array | null;
  flags: Set<SoundFlag>;
}

export function newSound(): Sound {
  return {
    curTick: 0,
    fn: NO_SOUND_FUNC,
    numTicks: 0,
    stride: 0,
    data: null,
    flags: new Set<SoundFlag>(),
  };
}

// --- the global state (pacman.c 420-540) ---
export interface TimingState {
  tick: number; // uint32
  laptimeStore: number; // milliseconds from performance.now()
  tickAccum: number; // nanoseconds remainder (exact in float64 here)
}

export interface IntroState {
  started: Trigger;
}

export interface Game {
  xorshift: number; // uint32
  hiscore: number; // uint32
  started: Trigger;
  readyStarted: Trigger;
  roundStarted: Trigger;
  roundWon: Trigger;
  gameOver: Trigger;
  dotEaten: Trigger;
  pillEaten: Trigger;
  ghostEaten: Trigger;
  pacmanEaten: Trigger;
  fruitEaten: Trigger;
  forceLeaveHouse: Trigger;
  fruitActive: Trigger;
  freeze: Set<FreezeType>;
  round: number; // uint8
  score: number; // uint32, in 10-point units
  numLives: number; // int8
  numGhostsEaten: number; // uint8
  numDotsEaten: number; // uint8
  globalDotCounterActive: boolean;
  globalDotCounter: number; // uint8
  ghost: Ghost[];
  pacman: Pacman;
  activeFruit: Fruit;
}

export function newGame(): Game {
  return {
    xorshift: 0,
    hiscore: 0,
    started: newTrigger(),
    readyStarted: newTrigger(),
    roundStarted: newTrigger(),
    roundWon: newTrigger(),
    gameOver: newTrigger(),
    dotEaten: newTrigger(),
    pillEaten: newTrigger(),
    ghostEaten: newTrigger(),
    pacmanEaten: newTrigger(),
    fruitEaten: newTrigger(),
    forceLeaveHouse: newTrigger(),
    fruitActive: newTrigger(),
    freeze: new Set<FreezeType>(),
    round: 0,
    score: 0,
    numLives: 0,
    numGhostsEaten: 0,
    numDotsEaten: 0,
    globalDotCounterActive: false,
    globalDotCounter: 0,
    ghost: [newGhost(), newGhost(), newGhost(), newGhost()],
    pacman: { actor: newActor() },
    activeFruit: Fruit.FRUIT_NONE,
  };
}

export interface InputState {
  enabled: boolean;
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  esc: boolean;
  anykey: boolean;
}

export function newInputState(): InputState {
  return { enabled: false, up: false, down: false, left: false, right: false, esc: false, anykey: false };
}

export interface AudioState {
  voice: Voice[];
  sound: Sound[];
}

export function newAudioState(): AudioState {
  return {
    voice: [newVoice(), newVoice(), newVoice()],
    sound: [newSound(), newSound(), newSound()],
  };
}

export interface GfxState {
  fadein: Trigger;
  fadeout: Trigger;
  fade: number; // uint8
  videoRam: number[][]; // [DISPLAY_TILES_Y][DISPLAY_TILES_X] of uint8
  colorRam: number[][];
  sprite: Sprite[];
  debugMarker: DebugMarker[];
  tilePixels: Uint8Array; // [TILE_TEXTURE_HEIGHT * TILE_TEXTURE_WIDTH]
  colorPalette: Uint32Array; // [256]
}

export function newGfxState(): GfxState {
  const ram = () =>
    Array.from({ length: DISPLAY_TILES_Y }, () => new Array<number>(DISPLAY_TILES_X).fill(0));
  return {
    fadein: newTrigger(),
    fadeout: newTrigger(),
    fade: 0,
    videoRam: ram(),
    colorRam: ram(),
    sprite: Array.from({ length: NUM_SPRITES }, () => newSprite()),
    debugMarker: Array.from({ length: NUM_DEBUG_MARKERS }, () => newDebugMarker()),
    tilePixels: new Uint8Array(TILE_TEXTURE_WIDTH * TILE_TEXTURE_HEIGHT),
    colorPalette: new Uint32Array(256),
  };
}

export interface State {
  gamestate: GameState;
  timing: TimingState;
  intro: IntroState;
  game: Game;
  input: InputState;
  audio: AudioState;
  gfx: GfxState;
}

export function newState(): State {
  return {
    gamestate: GameState.GAMESTATE_INTRO,
    timing: { tick: 0, laptimeStore: 0, tickAccum: 0 },
    intro: { started: newTrigger() },
    game: newGame(),
    input: newInputState(),
    audio: newAudioState(),
    gfx: newGfxState(),
  };
}

export const state: State = newState();

// --- data tables (pacman.c 542-623) ---
export const ghostScatterTargets: Int2[] = [i2(25, 0), i2(2, 0), i2(27, 34), i2(0, 34)];

// starting positions for ghosts (pixel coords), pacman.c 548-553
export const ghostStartingPos: Int2[] = [
  i2(14 * 8, 14 * 8 + 4),
  i2(14 * 8, 17 * 8 + 4),
  i2(12 * 8, 17 * 8 + 4),
  i2(16 * 8, 17 * 8 + 4),
];

// target positions for ghosts entering the ghost house, pacman.c 556-561
export const ghostHouseTargetPos: Int2[] = [
  i2(14 * 8, 17 * 8 + 4),
  i2(14 * 8, 17 * 8 + 4),
  i2(12 * 8, 17 * 8 + 4),
  i2(16 * 8, 17 * 8 + 4),
];

// The position tables above are shared by reference (a ghost's
// targetPos or starting pos IS the table entry until movement
// replaces it with a fresh object). In C these are static const and
// in Nim value copies; here they are frozen instead, so an
// accidental in-place write throws instead of silently corrupting
// the table for everyone.
for (const table of [ghostScatterTargets, ghostStartingPos, ghostHouseTargetPos]) {
  for (const p of table) Object.freeze(p);
  Object.freeze(table);
}

export const fruitTilesColors: number[][] = [
  [0, 0, 0],
  [TILE_CHERRIES, SPRITETILE_CHERRIES, COLOR_CHERRIES],
  [TILE_STRAWBERRY, SPRITETILE_STRAWBERRY, COLOR_STRAWBERRY],
  [TILE_PEACH, SPRITETILE_PEACH, COLOR_PEACH],
  [TILE_APPLE, SPRITETILE_APPLE, COLOR_APPLE],
  [TILE_GRAPES, SPRITETILE_GRAPES, COLOR_GRAPES],
  [TILE_GALAXIAN, SPRITETILE_GALAXIAN, COLOR_GALAXIAN],
  [TILE_BELL, SPRITETILE_BELL, COLOR_BELL],
  [TILE_KEY, SPRITETILE_KEY, COLOR_KEY],
];

export const fruitScoreTiles: number[][] = [
  [0x40, 0x40, 0x40, 0x40],
  [0x40, 0x81, 0x85, 0x40],
  [0x40, 0x82, 0x85, 0x40],
  [0x40, 0x83, 0x85, 0x40],
  [0x40, 0x84, 0x85, 0x40],
  [0x40, 0x86, 0x8d, 0x8e],
  [0x87, 0x88, 0x8d, 0x8e],
  [0x89, 0x8a, 0x8d, 0x8e],
  [0x8b, 0x8c, 0x8d, 0x8e],
];

export interface LevelSpec {
  bonusFruit: Fruit;
  bonusScore: number; // uint16
  frightTicks: number; // uint16
}

export const MAX_LEVELSPEC = 21;
export const levelspecTable: LevelSpec[] = [
  { bonusFruit: Fruit.FRUIT_CHERRIES, bonusScore: 10, frightTicks: 6 * 60 },
  { bonusFruit: Fruit.FRUIT_STRAWBERRY, bonusScore: 30, frightTicks: 5 * 60 },
  { bonusFruit: Fruit.FRUIT_PEACH, bonusScore: 50, frightTicks: 4 * 60 },
  { bonusFruit: Fruit.FRUIT_PEACH, bonusScore: 50, frightTicks: 3 * 60 },
  { bonusFruit: Fruit.FRUIT_APPLE, bonusScore: 70, frightTicks: 2 * 60 },
  { bonusFruit: Fruit.FRUIT_APPLE, bonusScore: 70, frightTicks: 5 * 60 },
  { bonusFruit: Fruit.FRUIT_GRAPES, bonusScore: 100, frightTicks: 2 * 60 },
  { bonusFruit: Fruit.FRUIT_GRAPES, bonusScore: 100, frightTicks: 2 * 60 },
  { bonusFruit: Fruit.FRUIT_GALAXIAN, bonusScore: 200, frightTicks: 1 * 60 },
  { bonusFruit: Fruit.FRUIT_GALAXIAN, bonusScore: 200, frightTicks: 5 * 60 },
  { bonusFruit: Fruit.FRUIT_BELL, bonusScore: 300, frightTicks: 2 * 60 },
  { bonusFruit: Fruit.FRUIT_BELL, bonusScore: 300, frightTicks: 1 * 60 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 * 60 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 3 * 60 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 * 60 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 * 60 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 * 60 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 },
  { bonusFruit: Fruit.FRUIT_KEY, bonusScore: 500, frightTicks: 1 },
];

// levelspec() hands out rows by reference; freeze them like the
// position tables above (callers only read).
for (const row of levelspecTable) Object.freeze(row);
Object.freeze(levelspecTable);

export function levelspec(round: number): LevelSpec {
  if (round < 0) throw new Error('levelspec: round < 0');
  const r = Math.min(round, MAX_LEVELSPEC - 1);
  return levelspecTable[r]!;
}
```

## timing.ts

```ts
// timing.ts -- the time-trigger vocabulary and input helpers.
// Corresponds to pacman.c lines 826-943 (xorshift, triggers, input).

import {
  state,
  newInputState,
  DISABLED_TICKS,
  Dir,
  type Trigger,
} from './state.js';

// xorshift random number generator (pacman.c 827-833).
// Bitwise operators coerce to int32, which reproduces the C uint32
// wraparound exactly; the stored value is normalized with >>>0 (SPEC T5).
export function xorshift32(): number {
  let x = state.game.xorshift | 0;
  x ^= x << 13;
  x ^= x >>> 17;
  x ^= x << 5;
  state.game.xorshift = x >>> 0;
  return x >>> 0;
}

// set time trigger to the next game tick
export function start(t: Trigger): void {
  t.tick = state.timing.tick + 1;
}

// set time trigger to a future tick
export function startAfter(t: Trigger, ticks: number): void {
  t.tick = state.timing.tick + ticks;
}

// deactivate a time trigger
export function disable(t: Trigger): void {
  t.tick = DISABLED_TICKS;
}

// return a disabled time trigger
export function disabledTimer(): Trigger {
  return { tick: DISABLED_TICKS };
}

// check if a time trigger is triggered
export function now(t: Trigger): boolean {
  return t.tick === state.timing.tick;
}

// return the number of ticks since a time trigger was triggered
export function since(t: Trigger): number {
  if (state.timing.tick >= t.tick) {
    return state.timing.tick - t.tick;
  }
  return DISABLED_TICKS;
}

// check if a time trigger is between begin and end tick
export function between(t: Trigger, begin: number, end: number): boolean {
  if (!(begin < end)) throw new Error('between: begin < end required');
  if (t.tick !== DISABLED_TICKS) {
    const ticks = since(t);
    return ticks >= begin && ticks < end;
  }
  return false;
}

// check if a time trigger was triggered exactly N ticks ago
export function afterOnce(t: Trigger, ticks: number): boolean {
  return since(t) === ticks;
}

// check if a time trigger was triggered more than N ticks ago
export function after(t: Trigger, ticks: number): boolean {
  const s = since(t);
  if (s !== DISABLED_TICKS) {
    return s >= ticks;
  }
  return false;
}

// same as between(t, 0, ticks)
export function before(t: Trigger, ticks: number): boolean {
  const s = since(t);
  if (s !== DISABLED_TICKS) {
    return s < ticks;
  }
  return false;
}

// clear input state and disable input
export function inputDisable(): void {
  state.input = newInputState();
}

// enable input again
export function inputEnable(): void {
  state.input.enabled = true;
}

// get the current input as Dir
export function inputDir(defaultDir: Dir): Dir {
  if (state.input.up) return Dir.DIR_UP;
  if (state.input.down) return Dir.DIR_DOWN;
  if (state.input.right) return Dir.DIR_RIGHT;
  if (state.input.left) return Dir.DIR_LEFT;
  return defaultDir;
}
```

## geom.ts

```ts
// geom.ts -- geometry and playfield queries.
// Corresponds to pacman.c lines 988-991 and 1230-1361.

import {
  state,
  i2,
  add,
  TILE_WIDTH,
  TILE_HEIGHT,
  DISPLAY_TILES_X,
  DISPLAY_TILES_Y,
  DISPLAY_PIXELS_X,
  TILE_DOT,
  TILE_PILL,
  Dir,
  type Int2,
} from './state.js';

// Integer division truncating toward zero, matching C and Nim's div.
// (JavaScript's / is floating-point division; Math.trunc restores the
// integer semantics where the original relies on them, SPEC T5.)
export function idiv(a: number, b: number): number {
  return Math.trunc(a / b);
}

// Note: no cmod helper is needed here. JavaScript's % operator already
// truncates toward zero exactly like C's %, unlike Python's %.
export function distToTileMid(pos: Int2): Int2 {
  return i2(
    (TILE_WIDTH >> 1) - (pos.x % TILE_WIDTH),
    (TILE_HEIGHT >> 1) - (pos.y % TILE_HEIGHT),
  );
}

export function pixelToTilePos(pixPos: Int2): Int2 {
  return i2(idiv(pixPos.x, TILE_WIDTH), idiv(pixPos.y, TILE_HEIGHT));
}

// clamp tile pos to valid playfield coords
export function clampedTilePos(tilePos: Int2): Int2 {
  const result = i2(tilePos.x, tilePos.y);
  if (result.x < 0) {
    result.x = 0;
  } else if (result.x >= DISPLAY_TILES_X) {
    result.x = DISPLAY_TILES_X - 1;
  }
  if (result.y < 3) {
    result.y = 3;
  } else if (result.y >= DISPLAY_TILES_Y - 2) {
    result.y = DISPLAY_TILES_Y - 3;
  }
  return result;
}

const dirMap: Int2[] = [i2(1, 0), i2(0, 1), i2(-1, 0), i2(0, -1)];
// dirToVec hands out these vectors by reference; freeze them (and
// the table) so a stray in-place write cannot corrupt every caller.
for (const v of dirMap) Object.freeze(v);
Object.freeze(dirMap);

export function dirToVec(dir: Dir): Int2 {
  if (!(dir >= Dir.DIR_RIGHT && dir < Dir.NUM_DIRS)) throw new Error('dirToVec: bad dir');
  return dirMap[dir]!;
}

export function reverseDir(dir: Dir): Dir {
  switch (dir) {
    case Dir.DIR_RIGHT:
      return Dir.DIR_LEFT;
    case Dir.DIR_DOWN:
      return Dir.DIR_UP;
    case Dir.DIR_LEFT:
      return Dir.DIR_RIGHT;
    default:
      return Dir.DIR_DOWN;
  }
}

export function tileCodeAt(tilePos: Int2): number {
  if (
    !(tilePos.x >= 0 && tilePos.x < DISPLAY_TILES_X) ||
    !(tilePos.y >= 0 && tilePos.y < DISPLAY_TILES_Y)
  ) {
    throw new Error('tileCodeAt: out of range');
  }
  return state.gfx.videoRam[tilePos.y]![tilePos.x]!;
}

export function isBlockingTile(tilePos: Int2): boolean {
  return tileCodeAt(tilePos) >= 0xc0;
}

export function isDot(tilePos: Int2): boolean {
  return tileCodeAt(tilePos) === TILE_DOT;
}

export function isPill(tilePos: Int2): boolean {
  return tileCodeAt(tilePos) === TILE_PILL;
}

export function isTunnel(tilePos: Int2): boolean {
  return tilePos.y === 17 && (tilePos.x <= 5 || tilePos.x >= 22);
}

// positions where upward movement is forbidden for ghosts
export function isRedzone(tilePos: Int2): boolean {
  return tilePos.x >= 11 && tilePos.x <= 16 && (tilePos.y === 14 || tilePos.y === 26);
}

// test if movement from a pixel position in a wanted direction is possible
export function canMove(pos: Int2, wantedDir: Dir, allowCornering: boolean): boolean {
  const dirVec = dirToVec(wantedDir);
  const distMid = distToTileMid(pos);
  let moveDistMid: number;
  let perpDistMid: number;
  if (dirVec.y !== 0) {
    moveDistMid = distMid.y;
    perpDistMid = distMid.x;
  } else {
    moveDistMid = distMid.x;
    perpDistMid = distMid.y;
  }
  const tilePos = pixelToTilePos(pos);
  const checkPos = clampedTilePos(add(tilePos, dirVec));
  const blocked = isBlockingTile(checkPos);
  return !((!allowCornering && perpDistMid !== 0) || (blocked && moveDistMid === 0));
}

// compute a new pixel position along a direction (without blocking check)
export function move(pos: Int2, dir: Dir, allowCornering: boolean): Int2 {
  const dirVec = dirToVec(dir);
  const result = add(pos, dirVec);
  if (allowCornering) {
    const distMid = distToTileMid(result);
    if (dirVec.x !== 0) {
      if (distMid.y < 0) result.y -= 1;
      else if (distMid.y > 0) result.y += 1;
    } else if (dirVec.y !== 0) {
      if (distMid.x < 0) result.x -= 1;
      else if (distMid.x > 0) result.x += 1;
    }
  }
  if (result.x < 0) {
    result.x = DISPLAY_PIXELS_X - 1;
  } else if (result.x >= DISPLAY_PIXELS_X) {
    result.x = 0;
  }
  return result;
}
```

## ghost.ts

```ts
// ghost.ts -- ghost speed, state machine, target selection and steering.
// Corresponds to pacman.c lines 1750-2087.
// Translation of the Nim port's ghost.nim.

import {
  state,
  i2,
  add,
  sub,
  scale,
  squaredDistance,
  nearEqual,
  levelspec,
  ghostScatterTargets,
  ghostHouseTargetPos,
  TILE_HEIGHT,
  DISPLAY_TILES_X,
  DISPLAY_TILES_Y,
  ANTEPORTAS_X,
  ANTEPORTAS_Y,
  Dir,
  GhostState,
  GhostType,
  type Ghost,
  type Int2,
} from './state.js';
import { since, before, afterOnce, start, disable, xorshift32 } from './timing.js';
import {
  idiv,
  pixelToTilePos,
  clampedTilePos,
  dirToVec,
  reverseDir,
  distToTileMid,
  isBlockingTile,
  isTunnel,
  isRedzone,
} from './geom.js';

export function ghostSpeed(ghost: Ghost): number {
  switch (ghost.state) {
    case GhostState.GHOSTSTATE_HOUSE:
    case GhostState.GHOSTSTATE_LEAVEHOUSE:
    case GhostState.GHOSTSTATE_FRIGHTENED:
      // inside house / frightened: half speed
      return state.timing.tick & 1;
    case GhostState.GHOSTSTATE_EYES:
    case GhostState.GHOSTSTATE_ENTERHOUSE:
      // estimated 1.5x in eye state
      return (state.timing.tick & 1) !== 0 ? 1 : 2;
    default:
      if (isTunnel(pixelToTilePos(ghost.actor.pos))) {
        return ((state.timing.tick * 2) % 4) !== 0 ? 1 : 0;
      }
      return state.timing.tick % 7 !== 0 ? 1 : 0;
  }
}

// return the current global scatter or chase phase
export function scatterChasePhase(): GhostState {
  const t = since(state.game.roundStarted);
  if (t < 7 * 60) return GhostState.GHOSTSTATE_SCATTER;
  if (t < 27 * 60) return GhostState.GHOSTSTATE_CHASE;
  if (t < 34 * 60) return GhostState.GHOSTSTATE_SCATTER;
  if (t < 54 * 60) return GhostState.GHOSTSTATE_CHASE;
  if (t < 59 * 60) return GhostState.GHOSTSTATE_SCATTER;
  if (t < 79 * 60) return GhostState.GHOSTSTATE_CHASE;
  if (t < 84 * 60) return GhostState.GHOSTSTATE_SCATTER;
  return GhostState.GHOSTSTATE_CHASE;
}

// takes care of switching a ghost into a new state
export function updateGhostState(ghost: Ghost): void {
  let newState = ghost.state;
  switch (ghost.state) {
    case GhostState.GHOSTSTATE_EYES:
      if (nearEqual(ghost.actor.pos, i2(ANTEPORTAS_X, ANTEPORTAS_Y), 1)) {
        newState = GhostState.GHOSTSTATE_ENTERHOUSE;
      }
      break;
    case GhostState.GHOSTSTATE_ENTERHOUSE:
      if (nearEqual(ghost.actor.pos, ghostHouseTargetPos[ghost.typ]!, 1)) {
        newState = GhostState.GHOSTSTATE_LEAVEHOUSE;
      }
      break;
    case GhostState.GHOSTSTATE_HOUSE:
      if (afterOnce(state.game.forceLeaveHouse, 4 * 60)) {
        newState = GhostState.GHOSTSTATE_LEAVEHOUSE;
        start(state.game.forceLeaveHouse);
      } else if (state.game.globalDotCounterActive) {
        if (ghost.typ === GhostType.GHOSTTYPE_PINKY && state.game.globalDotCounter === 7) {
          newState = GhostState.GHOSTSTATE_LEAVEHOUSE;
        } else if (ghost.typ === GhostType.GHOSTTYPE_INKY && state.game.globalDotCounter === 17) {
          newState = GhostState.GHOSTSTATE_LEAVEHOUSE;
        } else if (ghost.typ === GhostType.GHOSTTYPE_CLYDE && state.game.globalDotCounter === 32) {
          newState = GhostState.GHOSTSTATE_LEAVEHOUSE;
          // the global dot counter is deactivated when Clyde leaves at 32
          state.game.globalDotCounterActive = false;
        }
      } else if (ghost.dotCounter === ghost.dotLimit) {
        newState = GhostState.GHOSTSTATE_LEAVEHOUSE;
      }
      break;
    case GhostState.GHOSTSTATE_LEAVEHOUSE:
      if (ghost.actor.pos.y === ANTEPORTAS_Y) {
        newState = GhostState.GHOSTSTATE_SCATTER;
      }
      break;
    default:
      if (before(ghost.frightened, levelspec(state.game.round).frightTicks)) {
        newState = GhostState.GHOSTSTATE_FRIGHTENED;
      } else {
        newState = scatterChasePhase();
      }
      break;
  }
  // handle state transitions
  if (newState !== ghost.state) {
    switch (ghost.state) {
      case GhostState.GHOSTSTATE_LEAVEHOUSE:
        ghost.nextDir = Dir.DIR_LEFT;
        ghost.actor.dir = Dir.DIR_LEFT;
        break;
      case GhostState.GHOSTSTATE_ENTERHOUSE:
        // a ghost that was eaten is immune to frighten until the next pill
        disable(ghost.frightened);
        break;
      case GhostState.GHOSTSTATE_FRIGHTENED:
        break; // don't reverse direction when leaving frightened state
      case GhostState.GHOSTSTATE_SCATTER:
      case GhostState.GHOSTSTATE_CHASE:
        // any transition from scatter/chase causes a reversal of direction
        ghost.nextDir = reverseDir(ghost.actor.dir);
        break;
      default:
        break;
    }
    ghost.state = newState;
  }
}

// update the ghost's target position
export function updateGhostTarget(ghost: Ghost): void {
  let pos: Int2 = ghost.targetPos;
  switch (ghost.state) {
    case GhostState.GHOSTSTATE_SCATTER:
      pos = ghostScatterTargets[ghost.typ]!;
      break;
    case GhostState.GHOSTSTATE_CHASE: {
      const pm = state.game.pacman.actor;
      const pmPos = pixelToTilePos(pm.pos);
      const pmDir = dirToVec(pm.dir);
      switch (ghost.typ) {
        case GhostType.GHOSTTYPE_BLINKY:
          pos = pmPos;
          break;
        case GhostType.GHOSTTYPE_PINKY:
          // 4 tiles ahead of Pacman (without the arcade 'diagonal overflow')
          pos = add(pmPos, scale(pmDir, 4));
          break;
        case GhostType.GHOSTTYPE_INKY: {
          const blinkyPos = pixelToTilePos(
            state.game.ghost[GhostType.GHOSTTYPE_BLINKY]!.actor.pos,
          );
          const p = add(pmPos, scale(pmDir, 2));
          const d = sub(p, blinkyPos);
          pos = add(blinkyPos, scale(d, 2));
          break;
        }
        case GhostType.GHOSTTYPE_CLYDE:
          if (squaredDistance(pixelToTilePos(ghost.actor.pos), pmPos) > 64) {
            pos = pmPos;
          } else {
            pos = ghostScatterTargets[GhostType.GHOSTTYPE_CLYDE]!;
          }
          break;
        default:
          break;
      }
      break;
    }
    case GhostState.GHOSTSTATE_FRIGHTENED:
      // random target position (random direction at each intersection)
      pos = i2(xorshift32() % DISPLAY_TILES_X, xorshift32() % DISPLAY_TILES_Y);
      break;
    case GhostState.GHOSTSTATE_EYES:
      pos = i2(13, 14);
      break;
    default:
      break;
  }
  ghost.targetPos = pos;
}

// compute the next ghost direction; returns true if the resulting movement
// should always happen (movement inside the ghost house)
export function updateGhostDir(ghost: Ghost): boolean {
  if (ghost.state === GhostState.GHOSTSTATE_HOUSE) {
    if (ghost.actor.pos.y <= 17 * TILE_HEIGHT) {
      ghost.nextDir = Dir.DIR_DOWN;
    } else if (ghost.actor.pos.y >= 18 * TILE_HEIGHT) {
      ghost.nextDir = Dir.DIR_UP;
    }
    ghost.actor.dir = ghost.nextDir;
    return true;
  } else if (ghost.state === GhostState.GHOSTSTATE_LEAVEHOUSE) {
    const pos = ghost.actor.pos;
    if (pos.x === ANTEPORTAS_X) {
      if (pos.y > ANTEPORTAS_Y) {
        ghost.nextDir = Dir.DIR_UP;
      }
    } else {
      const midY = 17 * TILE_HEIGHT + idiv(TILE_HEIGHT, 2);
      if (pos.y > midY) {
        ghost.nextDir = Dir.DIR_UP;
      } else if (pos.y < midY) {
        ghost.nextDir = Dir.DIR_DOWN;
      } else {
        ghost.nextDir = pos.x > ANTEPORTAS_X ? Dir.DIR_LEFT : Dir.DIR_RIGHT;
      }
    }
    ghost.actor.dir = ghost.nextDir;
    return true;
  } else if (ghost.state === GhostState.GHOSTSTATE_ENTERHOUSE) {
    const pos = ghost.actor.pos;
    const tilePos = pixelToTilePos(pos);
    const tgtPos = ghostHouseTargetPos[ghost.typ]!;
    if (tilePos.y === 14) {
      if (pos.x !== ANTEPORTAS_X) {
        ghost.nextDir = pos.x < ANTEPORTAS_X ? Dir.DIR_RIGHT : Dir.DIR_LEFT;
      } else {
        ghost.nextDir = Dir.DIR_DOWN;
      }
    } else if (pos.y === tgtPos.y) {
      ghost.nextDir = pos.x < tgtPos.x ? Dir.DIR_RIGHT : Dir.DIR_LEFT;
    }
    ghost.actor.dir = ghost.nextDir;
    return true;
  } else {
    // scatter/chase/frightened: head towards the current target point
    const distToMid = distToTileMid(ghost.actor.pos);
    if (distToMid.x === 0 && distToMid.y === 0) {
      ghost.actor.dir = ghost.nextDir;
      const dirVec = dirToVec(ghost.actor.dir);
      const lookaheadPos = add(pixelToTilePos(ghost.actor.pos), dirVec);
      const dirs = [Dir.DIR_UP, Dir.DIR_LEFT, Dir.DIR_DOWN, Dir.DIR_RIGHT];
      let minDist = 100000;
      for (const dir of dirs) {
        // in the two 'red zones', upward movement is forbidden (except eyes)
        if (
          isRedzone(lookaheadPos) &&
          dir === Dir.DIR_UP &&
          ghost.state !== GhostState.GHOSTSTATE_EYES
        ) {
          continue;
        }
        const revdir = reverseDir(dir);
        const testPos = clampedTilePos(add(lookaheadPos, dirToVec(dir)));
        if (revdir !== ghost.actor.dir && !isBlockingTile(testPos)) {
          const dist = squaredDistance(testPos, ghost.targetPos);
          if (dist < minDist) {
            minDist = dist;
            ghost.nextDir = dir;
          }
        }
      }
    }
    return false;
  }
}

// update the dot counters used to decide whether ghosts must leave the house
// (called each time Pacman eats a dot)
export function updateGhosthouseDotCounters(): void {
  if (state.game.globalDotCounterActive) {
    state.game.globalDotCounter = (state.game.globalDotCounter + 1) & 0xff;
  } else {
    for (let i = 0; i < state.game.ghost.length; i++) {
      const g = state.game.ghost[i]!;
      if (g.dotCounter < g.dotLimit) {
        g.dotCounter += 1;
        break;
      }
    }
  }
}
```

## rules.ts

```ts
// rules.ts -- playfield setup, round setup, actor updates, the game tick
// and the intro tick. Corresponds to pacman.c lines 1377-1583, 1733-1748,
// 2089-2403. Translation of the Nim port's rules.nim, plus the tick driver
// (runTick) and startup (initGame) mirrored from pacman.nim's frame()/init().

import {
  state,
  i2,
  add,
  newActor,
  newSprite,
  levelspec,
  ghostStartingPos,
  TILE_WIDTH,
  TILE_HEIGHT,
  TILE_SPACE,
  TILE_GHOST,
  TILE_DOT,
  TILE_PILL,
  TILE_DOOR,
  COLOR_DEFAULT,
  COLOR_DOT,
  COLOR_PACMAN,
  COLOR_BLINKY,
  COLOR_PINKY,
  COLOR_INKY,
  COLOR_CLYDE,
  NUM_LIVES,
  NUM_DOTS,
  FADE_TICKS,
  GAMEOVER_TICKS,
  ROUNDWON_TICKS,
  FRUITACTIVE_TICKS,
  GHOST_EATEN_FREEZE_TICKS,
  PACMAN_EATEN_TICKS,
  PACMAN_DEATH_TICKS,
  GameState,
  Dir,
  Fruit,
  SpriteIndex,
  GhostType,
  GhostState,
  FreezeType,
  type Ghost,
} from './state.js';
import {
  start,
  startAfter,
  disable,
  disabledTimer,
  now,
  since,
  afterOnce,
  after,
  inputDir,
  inputEnable,
  inputDisable,
} from './timing.js';
import { idiv, pixelToTilePos, isDot, isPill, canMove, move } from './geom.js';
import {
  ghostSpeed,
  updateGhostState,
  updateGhostTarget,
  updateGhostDir,
  updateGhosthouseDotCounters,
} from './ghost.js';
import {
  vidClear,
  vidColorPlayfield,
  vidColor,
  vidTile,
  vidColorTile,
  vidColorText,
  vidText,
  vidColorScore,
  vidFruitScore,
  sprClear,
  gameUpdateTiles,
  gameUpdateSprites,
  gfxInit,
} from './render.js';
import {
  sndClear,
  sndStart,
  sndTick,
  sndPrelude,
  sndDead,
  sndEatdot1,
  sndEatdot2,
  sndEatghost,
  sndEatfruit,
  sndWeeooh,
  sndFrightened,
} from './sound.js';

// initialize the playfield tiles from the ASCII map (pacman.c 1377-1432)
function gameInitPlayfield(): void {
  vidColorPlayfield(COLOR_DOT);
  const tiles = [
    '0UUUUUUUUUUUU45UUUUUUUUUUUU1',
    'L............rl............R',
    'L.ebbf.ebbbf.rl.ebbbf.ebbf.R',
    'LPr  l.r   l.rl.r   l.r  lPR',
    'L.guuh.guuuh.gh.guuuh.guuh.R',
    'L..........................R',
    'L.ebbf.ef.ebbbbbbf.ef.ebbf.R',
    'L.guuh.rl.guuyxuuh.rl.guuh.R',
    'L......rl....rl....rl......R',
    '2BBBBf.rzbbf rl ebbwl.eBBBB3',
    '     L.rxuuh gh guuyl.R     ',
    '     L.rl          rl.R     ',
    '     L.rl mjs--tjn rl.R     ',
    'UUUUUh.gh i      q gh.gUUUUU',
    '      .   i      q   .      ',
    'BBBBBf.ef i      q ef.eBBBBB',
    '     L.rl okkkkkkp rl.R     ',
    '     L.rl          rl.R     ',
    '     L.rl ebbbbbbf rl.R     ',
    '0UUUUh.gh guuyxuuh gh.gUUUU1',
    'L............rl............R',
    'L.ebbf.ebbbf.rl.ebbbf.ebbf.R',
    'L.guyl.guuuh.gh.guuuh.rxuh.R',
    'LP..rl.......  .......rl..PR',
    '6bf.rl.ef.ebbbbbbf.ef.rl.eb8',
    '7uh.gh.rl.guuyxuuh.rl.gh.gu9',
    'L......rl....rl....rl......R',
    'L.ebbbbwzbbf.rl.ebbwzbbbbf.R',
    'L.guuuuuuuuh.gh.guuuuuuuuh.R',
    'L..........................R',
    '2BBBBBBBBBBBBBBBBBBBBBBBBBB3',
  ].join('');
  const t: number[] = new Array<number>(128).fill(TILE_DOT);
  const set = (ch: string, code: number): void => {
    t[ch.charCodeAt(0)] = code;
  };
  set(' ', 0x40); set('0', 0xd1); set('1', 0xd0);
  set('2', 0xd5); set('3', 0xd4); set('4', 0xfb);
  set('5', 0xfa); set('6', 0xd7); set('7', 0xd9);
  set('8', 0xd6); set('9', 0xd8); set('U', 0xdb);
  set('L', 0xd3); set('R', 0xd2); set('B', 0xdc);
  set('b', 0xdf); set('e', 0xe7); set('f', 0xe6);
  set('g', 0xeb); set('h', 0xea); set('l', 0xe8);
  set('r', 0xe9); set('u', 0xe5); set('w', 0xf5);
  set('x', 0xf2); set('y', 0xf3); set('z', 0xf4);
  set('m', 0xed); set('n', 0xec); set('o', 0xef);
  set('p', 0xee); set('j', 0xdd); set('i', 0xd2);
  set('k', 0xdb); set('q', 0xd3); set('s', 0xf1);
  set('t', 0xf0); set('-', TILE_DOOR); set('P', TILE_PILL);
  let i = 0;
  for (let y = 3; y <= 33; y++) {
    for (let x = 0; x < 28; x++) {
      state.gfx.videoRam[y]![x] = t[tiles.charCodeAt(i) & 127]!;
      i += 1;
    }
  }
  // ghost house gate colors
  vidColor(i2(13, 15), 0x18);
  vidColor(i2(14, 15), 0x18);
}

// disable all game loop timers
function gameDisableTimers(): void {
  disable(state.game.roundWon);
  disable(state.game.gameOver);
  disable(state.game.dotEaten);
  disable(state.game.pillEaten);
  disable(state.game.ghostEaten);
  disable(state.game.pacmanEaten);
  disable(state.game.fruitEaten);
  disable(state.game.forceLeaveHouse);
  disable(state.game.fruitActive);
}

// one-time init at start of game state
function gameInit(): void {
  inputEnable();
  gameDisableTimers();
  state.game.round = 0;
  state.game.freeze = new Set([FreezeType.FREEZETYPE_PRELUDE]);
  state.game.numLives = NUM_LIVES;
  state.game.globalDotCounterActive = false;
  state.game.globalDotCounter = 0;
  state.game.numDotsEaten = 0;
  state.game.score = 0;
  vidClear(TILE_SPACE, COLOR_DOT);
  vidColorText(i2(9, 0), COLOR_DEFAULT, 'HIGH SCORE');
  gameInitPlayfield();
  vidColorText(i2(9, 14), 0x5, 'PLAYER ONE');
  vidColorText(i2(11, 20), 0x9, 'READY!');
}

function makeGhost(
  typ: GhostType,
  dir: Dir,
  ghostState: GhostState,
  dotLimit: number,
): Ghost {
  const actor = newActor();
  actor.dir = dir;
  actor.pos = ghostStartingPos[typ]!;
  return {
    actor,
    typ,
    nextDir: dir,
    targetPos: i2(0, 0),
    state: ghostState,
    frightened: disabledTimer(),
    eaten: disabledTimer(),
    dotCounter: 0,
    dotLimit,
  };
}

function makeSprite(color: number) {
  const s = newSprite();
  s.enabled = true;
  s.color = color;
  return s;
}

// setup state at start of a game round
function gameRoundInit(): void {
  sprClear();
  vidColorText(i2(9, 14), 0x10, '          ');
  if (state.game.numDotsEaten === NUM_DOTS) {
    // round won: redraw the playfield, reset the global dot counter
    state.game.round = (state.game.round + 1) & 0xff;
    state.game.numDotsEaten = 0;
    gameInitPlayfield();
    state.game.globalDotCounterActive = false;
  } else {
    if (state.game.numLives !== NUM_LIVES) {
      state.game.globalDotCounterActive = true;
      state.game.globalDotCounter = 0;
    }
    state.game.numLives -= 1;
  }
  if (state.game.numLives < 0) throw new Error('gameRoundInit: numLives < 0');

  state.game.activeFruit = Fruit.FRUIT_NONE;
  state.game.freeze = new Set([FreezeType.FREEZETYPE_READY]);
  state.game.xorshift = 0x12345678; // random-number-generator seed
  state.game.numGhostsEaten = 0;
  gameDisableTimers();
  vidColorText(i2(11, 20), 0x9, 'READY!');
  start(state.game.forceLeaveHouse);

  const pmActor = newActor();
  pmActor.dir = Dir.DIR_LEFT;
  pmActor.pos = i2(14 * 8, 26 * 8 + 4);
  state.game.pacman = { actor: pmActor };
  state.gfx.sprite[SpriteIndex.SPRITE_PACMAN] = makeSprite(COLOR_PACMAN);

  state.game.ghost[GhostType.GHOSTTYPE_BLINKY] = makeGhost(
    GhostType.GHOSTTYPE_BLINKY, Dir.DIR_LEFT, GhostState.GHOSTSTATE_SCATTER, 0);
  state.gfx.sprite[SpriteIndex.SPRITE_BLINKY] = makeSprite(COLOR_BLINKY);

  state.game.ghost[GhostType.GHOSTTYPE_PINKY] = makeGhost(
    GhostType.GHOSTTYPE_PINKY, Dir.DIR_DOWN, GhostState.GHOSTSTATE_HOUSE, 0);
  state.gfx.sprite[SpriteIndex.SPRITE_PINKY] = makeSprite(COLOR_PINKY);

  state.game.ghost[GhostType.GHOSTTYPE_INKY] = makeGhost(
    GhostType.GHOSTTYPE_INKY, Dir.DIR_UP, GhostState.GHOSTSTATE_HOUSE, 30);
  state.gfx.sprite[SpriteIndex.SPRITE_INKY] = makeSprite(COLOR_INKY);

  state.game.ghost[GhostType.GHOSTTYPE_CLYDE] = makeGhost(
    GhostType.GHOSTTYPE_CLYDE, Dir.DIR_UP, GhostState.GHOSTSTATE_HOUSE, 60);
  state.gfx.sprite[SpriteIndex.SPRITE_CLYDE] = makeSprite(COLOR_CLYDE);
}

// return true if Pacman should move in this tick
function pacmanShouldMove(): boolean {
  if (now(state.game.dotEaten)) {
    return false; // eating a dot stops Pacman for 1 tick
  } else if (since(state.game.pillEaten) < 3) {
    return false; // eating a pill stops Pacman for 3 ticks
  } else {
    return state.timing.tick % 8 !== 0;
  }
}

// called when a dot or pill has been eaten
function gameUpdateDotsEaten(): void {
  state.game.numDotsEaten = (state.game.numDotsEaten + 1) & 0xff;
  if (state.game.numDotsEaten === NUM_DOTS) {
    start(state.game.roundWon);
    sndClear();
  } else if (state.game.numDotsEaten === 70 || state.game.numDotsEaten === 170) {
    start(state.game.fruitActive);
  }
  // alternating crunch sound effect
  if ((state.game.numDotsEaten & 1) !== 0) {
    sndStart(2, sndEatdot1);
  } else {
    sndStart(2, sndEatdot2);
  }
}

// the central Pacman and ghost behaviour function, called once per game tick
function gameUpdateActors(): void {
  // Pacman "AI"
  if (pacmanShouldMove()) {
    const actor = state.game.pacman.actor;
    const wantedDir = inputDir(actor.dir);
    if (canMove(actor.pos, wantedDir, true)) {
      actor.dir = wantedDir;
    }
    if (canMove(actor.pos, actor.dir, true)) {
      actor.pos = move(actor.pos, actor.dir, true);
      actor.animTick += 1;
    }
    const tilePos = pixelToTilePos(actor.pos);
    if (isDot(tilePos)) {
      vidTile(tilePos, TILE_SPACE);
      state.game.score += 1;
      start(state.game.dotEaten);
      start(state.game.forceLeaveHouse);
      gameUpdateDotsEaten();
      updateGhosthouseDotCounters();
    }
    if (isPill(tilePos)) {
      vidTile(tilePos, TILE_SPACE);
      state.game.score += 5;
      gameUpdateDotsEaten();
      start(state.game.pillEaten);
      state.game.numGhostsEaten = 0;
      for (let i = 0; i < state.game.ghost.length; i++) {
        start(state.game.ghost[i]!.frightened);
      }
      sndStart(1, sndFrightened);
    }
    // check if Pacman eats the bonus fruit
    if (state.game.activeFruit !== Fruit.FRUIT_NONE) {
      const testPos = pixelToTilePos(add(actor.pos, i2(idiv(TILE_WIDTH, 2), 0)));
      if (testPos.x === 14 && testPos.y === 20) {
        start(state.game.fruitEaten);
        state.game.score += levelspec(state.game.round).bonusScore;
        vidFruitScore(state.game.activeFruit);
        state.game.activeFruit = Fruit.FRUIT_NONE;
        sndStart(2, sndEatfruit);
      }
    }
    // check if Pacman collides with any ghost
    for (let i = 0; i < state.game.ghost.length; i++) {
      const ghost = state.game.ghost[i]!;
      const ghostTilePos = pixelToTilePos(ghost.actor.pos);
      if (tilePos.x === ghostTilePos.x && tilePos.y === ghostTilePos.y) {
        if (ghost.state === GhostState.GHOSTSTATE_FRIGHTENED) {
          ghost.state = GhostState.GHOSTSTATE_EYES;
          start(ghost.eaten);
          start(state.game.ghostEaten);
          state.game.numGhostsEaten = (state.game.numGhostsEaten + 1) & 0xff;
          // increase score by 20, 40, 80, 160 (in 10-point units)
          state.game.score += 10 * (1 << state.game.numGhostsEaten);
          state.game.freeze.add(FreezeType.FREEZETYPE_EAT_GHOST);
          sndStart(2, sndEatghost);
        } else if (
          ghost.state === GhostState.GHOSTSTATE_CHASE ||
          ghost.state === GhostState.GHOSTSTATE_SCATTER
        ) {
          sndClear();
          start(state.game.pacmanEaten);
          state.game.freeze.add(FreezeType.FREEZETYPE_DEAD);
          if (state.game.numLives > 0) {
            startAfter(state.game.readyStarted, PACMAN_EATEN_TICKS + PACMAN_DEATH_TICKS);
          } else {
            startAfter(state.game.gameOver, PACMAN_EATEN_TICKS + PACMAN_DEATH_TICKS);
          }
        }
      }
    }
  }

  // Ghost "AIs"
  for (let ghostIndex = 0; ghostIndex < state.game.ghost.length; ghostIndex++) {
    const ghost = state.game.ghost[ghostIndex]!;
    updateGhostState(ghost);
    updateGhostTarget(ghost);
    const numMoveTicks = ghostSpeed(ghost);
    for (let i = 0; i < numMoveTicks; i++) {
      const forceMove = updateGhostDir(ghost);
      if (forceMove || canMove(ghost.actor.pos, ghost.actor.dir, false)) {
        ghost.actor.pos = move(ghost.actor.pos, ghost.actor.dir, false);
        ghost.actor.animTick += 1;
      }
    }
  }
}

// the central game tick function, called at 60 Hz
export function gameTick(): void {
  if (now(state.game.started)) {
    start(state.gfx.fadein);
    startAfter(state.game.readyStarted, 2 * 60);
    sndStart(0, sndPrelude);
    gameInit();
  }
  if (now(state.game.readyStarted)) {
    gameRoundInit();
    startAfter(state.game.roundStarted, 2 * 60 + 10);
  }
  if (now(state.game.roundStarted)) {
    state.game.freeze.delete(FreezeType.FREEZETYPE_READY);
    vidColorText(i2(11, 20), 0x10, '      ');
    sndStart(1, sndWeeooh);
  }

  // activate/deactivate bonus fruit
  if (now(state.game.fruitActive)) {
    state.game.activeFruit = levelspec(state.game.round).bonusFruit;
  } else if (afterOnce(state.game.fruitActive, FRUITACTIVE_TICKS)) {
    state.game.activeFruit = Fruit.FRUIT_NONE;
  }

  // stop frightened sound and restart the weeooh sound
  if (afterOnce(state.game.pillEaten, levelspec(state.game.round).frightTicks)) {
    sndStart(1, sndWeeooh);
  }

  // unfreeze after Pacman ate a ghost
  if (state.game.freeze.has(FreezeType.FREEZETYPE_EAT_GHOST)) {
    if (afterOnce(state.game.ghostEaten, GHOST_EATEN_FREEZE_TICKS)) {
      state.game.freeze.delete(FreezeType.FREEZETYPE_EAT_GHOST);
    }
  }

  // play the pacman-death sound
  if (afterOnce(state.game.pacmanEaten, PACMAN_EATEN_TICKS)) {
    sndStart(2, sndDead);
  }

  if (state.game.freeze.size === 0) {
    gameUpdateActors();
  }
  gameUpdateTiles();
  gameUpdateSprites();

  if (state.game.score > state.game.hiscore) {
    state.game.hiscore = state.game.score;
  }

  // check for end-of-round conditions
  if (now(state.game.roundWon)) {
    state.game.freeze.add(FreezeType.FREEZETYPE_WON);
    startAfter(state.game.readyStarted, ROUNDWON_TICKS);
  }
  if (now(state.game.gameOver)) {
    vidColorText(i2(9, 20), 0x01, 'GAME  OVER');
    inputDisable();
    startAfter(state.gfx.fadeout, GAMEOVER_TICKS);
    startAfter(state.intro.started, GAMEOVER_TICKS + FADE_TICKS);
  }
}

// the intro screen tick function
export function introTick(): void {
  if (now(state.intro.started)) {
    sndClear();
    sprClear();
    start(state.gfx.fadein);
    inputEnable();
    vidClear(TILE_SPACE, COLOR_DEFAULT);
    vidText(i2(3, 0), '1UP   HIGH SCORE   2UP');
    vidColorScore(i2(6, 1), COLOR_DEFAULT, 0);
    if (state.game.hiscore > 0) {
      vidColorScore(i2(16, 1), COLOR_DEFAULT, state.game.hiscore);
    }
    vidText(i2(7, 5), 'CHARACTER / NICKNAME');
    vidText(i2(3, 35), 'CREDIT  0');
  }

  let delay = 30;
  const names = ['-SHADOW', '-SPEEDY', '-BASHFUL', '-POKEY'];
  const nicknames = ['BLINKY', 'PINKY', 'INKY', 'CLYDE'];
  for (let i = 0; i < 4; i++) {
    const color = 2 * i + 1;
    const y = 3 * i + 6;
    delay += 30;
    if (afterOnce(state.intro.started, delay)) {
      vidColorTile(i2(4, y + 0), color, TILE_GHOST + 0);
      vidColorTile(i2(5, y + 0), color, TILE_GHOST + 1);
      vidColorTile(i2(4, y + 1), color, TILE_GHOST + 2);
      vidColorTile(i2(5, y + 1), color, TILE_GHOST + 3);
      vidColorTile(i2(4, y + 2), color, TILE_GHOST + 4);
      vidColorTile(i2(5, y + 2), color, TILE_GHOST + 5);
    }
    delay += 60;
    if (afterOnce(state.intro.started, delay)) {
      vidColorText(i2(7, y + 1), color, names[i]!);
    }
    delay += 30;
    if (afterOnce(state.intro.started, delay)) {
      vidColorText(i2(17, y + 1), color, nicknames[i]!);
    }
  }

  delay += 60;
  if (afterOnce(state.intro.started, delay)) {
    vidColorTile(i2(10, 24), COLOR_DOT, TILE_DOT);
    vidText(i2(12, 24), '10 \x5D\x5E\x5F');
    vidColorTile(i2(10, 26), COLOR_DOT, TILE_PILL);
    vidText(i2(12, 26), '50 \x5D\x5E\x5F');
  }

  delay += 60;
  if (after(state.intro.started, delay)) {
    if ((since(state.intro.started) & 0x20) !== 0) {
      vidColorText(i2(3, 31), 3, '                       ');
    } else {
      vidColorText(i2(3, 31), 3, 'PRESS ANY KEY TO START!');
    }
  }

  if (state.input.anykey) {
    inputDisable();
    start(state.gfx.fadeout);
    startAfter(state.game.started, FADE_TICKS);
  }
}

// startup initialization, mirroring pacman.nim's init(): decode the
// graphics data and start the intro. (The Nim sndInit has no counterpart
// in the sound state layer; the AudioContext setup belongs to the
// browser layer, SPEC T3/T4.)
export function initGame(): void {
  gfxInit();
  start(state.intro.started);
}

// perform exactly one game tick: the tick part of pacman.nim's frame().
export function runTick(): void {
  state.timing.tick += 1;
  sndTick();
  if (now(state.intro.started)) {
    state.gamestate = GameState.GAMESTATE_INTRO;
  }
  if (now(state.game.started)) {
    state.gamestate = GameState.GAMESTATE_GAME;
  }
  if (state.gamestate === GameState.GAMESTATE_INTRO) {
    introTick();
  } else {
    gameTick();
  }
}
```

## render.ts

```ts
// render.ts -- video RAM writes, sprite animation, and the Canvas renderer.
// Corresponds to pacman.c lines 993-1229 (vid/spr), 1584-1732 (tile/sprite
// updates) and 2404-3124 (gfx subsystem; the sokol part is replaced by
// Canvas 2D pre-rendered images, SPEC T1).

import {
  state,
  i2,
  levelspec,
  TILE_WIDTH,
  TILE_HEIGHT,
  SPRITE_WIDTH,
  SPRITE_HEIGHT,
  DISPLAY_TILES_X,
  DISPLAY_TILES_Y,
  DISPLAY_PIXELS_X,
  DISPLAY_PIXELS_Y,
  NUM_SPRITES,
  NUM_DEBUG_MARKERS,
  NUM_PILLS,
  NUM_LIVES,
  NUM_STATUS_FRUITS,
  TILE_TEXTURE_WIDTH,
  TILE_TEXTURE_HEIGHT,
  TILE_LIFE,
  COLOR_DEFAULT,
  COLOR_DOT,
  COLOR_PACMAN,
  COLOR_BLINKY,
  COLOR_FRIGHTENED,
  COLOR_FRIGHTENED_BLINKING,
  COLOR_GHOST_SCORE,
  COLOR_EYES,
  COLOR_FRUIT_SCORE,
  COLOR_WHITE_BORDER,
  SPRITETILE_INVISIBLE,
  SPRITETILE_PACMAN_CLOSED_MOUTH,
  SPRITETILE_SCORE_200,
  FADE_TICKS,
  PACMAN_EATEN_TICKS,
  GHOST_EATEN_FREEZE_TICKS,
  Dir,
  Fruit,
  GhostType,
  GhostState,
  SpriteIndex,
  FreezeType,
  fruitScoreTiles,
  fruitTilesColors,
  actorToSpritePos,
  type Int2,
  type Sprite,
  type Trigger,
} from './state.js';
import { afterOnce, after, before, since, disable, between } from './timing.js';
import { idiv } from './geom.js';
import { romTiles, romSprites, romHWColors, romPalette } from './romdata.js';

// --- vid: writes into the tile/color buffers (pacman.c 993-1133) ---

export function vidClear(tileCode: number, colorCode: number): void {
  for (let y = 0; y < DISPLAY_TILES_Y; y++) {
    for (let x = 0; x < DISPLAY_TILES_X; x++) {
      state.gfx.videoRam[y]![x] = tileCode;
      state.gfx.colorRam[y]![x] = colorCode;
    }
  }
}

export function vidColorPlayfield(colorCode: number): void {
  for (let y = 3; y < DISPLAY_TILES_Y - 2; y++) {
    for (let x = 0; x < DISPLAY_TILES_X; x++) {
      state.gfx.colorRam[y]![x] = colorCode;
    }
  }
}

function validTilePos(tilePos: Int2): boolean {
  return (
    tilePos.x >= 0 &&
    tilePos.x < DISPLAY_TILES_X &&
    tilePos.y >= 0 &&
    tilePos.y < DISPLAY_TILES_Y
  );
}

export function vidColor(tilePos: Int2, colorCode: number): void {
  if (!validTilePos(tilePos)) throw new Error('vidColor: bad pos');
  state.gfx.colorRam[tilePos.y]![tilePos.x] = colorCode;
}

export function vidTile(tilePos: Int2, tileCode: number): void {
  if (!validTilePos(tilePos)) throw new Error('vidTile: bad pos');
  state.gfx.videoRam[tilePos.y]![tilePos.x] = tileCode;
}

export function vidColorTile(tilePos: Int2, colorCode: number, tileCode: number): void {
  if (!validTilePos(tilePos)) throw new Error('vidColorTile: bad pos');
  state.gfx.videoRam[tilePos.y]![tilePos.x] = tileCode;
  state.gfx.colorRam[tilePos.y]![tilePos.x] = colorCode;
}

// translate ASCII char into "NAMCO char"
function convChar(c: string): number {
  switch (c) {
    case ' ':
      return 0x40;
    case '/':
      return 58;
    case '-':
      return 59;
    case '"':
      return 38;
    case '!':
      return 'Z'.charCodeAt(0) + 1;
    default:
      return c.charCodeAt(0);
  }
}

function vidColorChar(tilePos: Int2, colorCode: number, chr: string): void {
  if (!validTilePos(tilePos)) throw new Error('vidColorChar: bad pos');
  state.gfx.videoRam[tilePos.y]![tilePos.x] = convChar(chr);
  state.gfx.colorRam[tilePos.y]![tilePos.x] = colorCode;
}

function vidChar(tilePos: Int2, chr: string): void {
  if (!validTilePos(tilePos)) throw new Error('vidChar: bad pos');
  state.gfx.videoRam[tilePos.y]![tilePos.x] = convChar(chr);
}

export function vidColorText(tilePos: Int2, colorCode: number, text: string): void {
  if (!validTilePos(tilePos)) throw new Error('vidColorText: bad pos');
  const tp = i2(tilePos.x, tilePos.y);
  for (const chr of text) {
    if (tp.x < DISPLAY_TILES_X) {
      vidColorChar(tp, colorCode, chr);
      tp.x += 1;
    } else {
      break;
    }
  }
}

export function vidText(tilePos: Int2, text: string): void {
  if (!validTilePos(tilePos)) throw new Error('vidText: bad pos');
  const tp = i2(tilePos.x, tilePos.y);
  for (const chr of text) {
    if (tp.x < DISPLAY_TILES_X) {
      vidChar(tp, chr);
      tp.x += 1;
    } else {
      break;
    }
  }
}

// print a score (scores are /10, printed right to left, last digit always 0)
export function vidColorScore(tilePos: Int2, colorCode: number, score: number): void {
  const tp = i2(tilePos.x, tilePos.y);
  let s = score;
  vidColorChar(tp, colorCode, '0');
  tp.x -= 1;
  for (let digit = 0; digit < 8; digit++) {
    const chr = String.fromCharCode((s % 10) + '0'.charCodeAt(0));
    if (validTilePos(tp)) {
      vidColorChar(tp, colorCode, chr);
      tp.x -= 1;
      s = idiv(s, 10);
      if (s === 0) break;
    }
  }
}

// draw a 2x2 tile quad (used for lives and status fruits)
export function vidDrawTileQuad(tilePos: Int2, colorCode: number, tileCode: number): void {
  for (let yy = 0; yy < 2; yy++) {
    for (let xx = 0; xx < 2; xx++) {
      const t = tileCode + (yy * 2 + (1 - xx));
      vidColorTile(i2(xx + tilePos.x, yy + tilePos.y), colorCode, t);
    }
  }
}

// draw the fruit bonus score tiles (when Pacman has eaten the bonus fruit)
export function vidFruitScore(fruitType: Fruit): void {
  if (!(fruitType >= Fruit.FRUIT_NONE && fruitType < Fruit.NUM_FRUITS))
    throw new Error('vidFruitScore: bad fruit');
  const colorCode = fruitType === Fruit.FRUIT_NONE ? COLOR_DOT : COLOR_FRUIT_SCORE;
  for (let i = 0; i < 4; i++) {
    vidColorTile(i2(12 + i, 20), colorCode, fruitScoreTiles[fruitType]![i]!);
  }
}

// --- spr: sprite state and animation (pacman.c 1134-1229) ---

export function sprClear(): void {
  for (let i = 0; i < NUM_SPRITES; i++) {
    const s = state.gfx.sprite[i]!;
    s.enabled = false;
    s.tile = 0;
    s.color = 0;
    s.flipx = false;
    s.flipy = false;
    s.pos = i2(0, 0);
  }
}

export function sprPacman(): Sprite {
  return state.gfx.sprite[SpriteIndex.SPRITE_PACMAN]!;
}

export function sprGhost(typ: GhostType): Sprite {
  if (!(typ >= GhostType.GHOSTTYPE_BLINKY && typ < GhostType.NUM_GHOSTS))
    throw new Error('sprGhost: bad type');
  return state.gfx.sprite[SpriteIndex.SPRITE_BLINKY + typ]!;
}

export function sprFruit(): Sprite {
  return state.gfx.sprite[SpriteIndex.SPRITE_FRUIT]!;
}

export function sprAnimPacman(dir: Dir, tick: number): void {
  const tiles: number[][] = [
    [44, 46, 48, 46], // horizontal (needs flipx)
    [45, 47, 48, 47], // vertical (needs flipy)
  ];
  const spr = sprPacman();
  const phase = idiv(tick, 2) & 3;
  spr.tile = tiles[dir & 1]![phase]!;
  spr.color = COLOR_PACMAN;
  spr.flipx = dir === Dir.DIR_LEFT;
  spr.flipy = dir === Dir.DIR_UP;
}

export function sprAnimPacmanDeath(tick: number): void {
  const spr = sprPacman();
  let tile = 52 + idiv(tick, 8);
  if (tile > 63) tile = 63;
  spr.tile = tile;
  spr.flipx = false;
  spr.flipy = false;
}

export function sprAnimGhost(ghostType: GhostType, dir: Dir, tick: number): void {
  if (!(dir >= Dir.DIR_RIGHT && dir < Dir.NUM_DIRS)) throw new Error('sprAnimGhost: bad dir');
  const tiles: number[][] = [
    [32, 33],
    [34, 35],
    [36, 37],
    [38, 39],
  ];
  const phase = idiv(tick, 8) & 1;
  const spr = sprGhost(ghostType);
  spr.tile = tiles[dir]![phase]!;
  spr.color = COLOR_BLINKY + 2 * ghostType;
  spr.flipx = false;
  spr.flipy = false;
}

export function sprAnimGhostFrightened(ghostType: GhostType, tick: number): void {
  const tiles: number[] = [28, 29];
  const phase = idiv(tick, 4) & 1;
  const spr = sprGhost(ghostType);
  spr.tile = tiles[phase]!;
  // towards the end of the frightened period, start blinking (the C code
  // casts the possibly negative difference to uint32, replicated here
  // with >>>0, SPEC T5)
  if (tick > ((levelspec(state.game.round).frightTicks - 60) >>> 0)) {
    spr.color = (tick & 0x10) !== 0 ? COLOR_FRIGHTENED : COLOR_FRIGHTENED_BLINKING;
  } else {
    spr.color = COLOR_FRIGHTENED;
  }
  spr.flipx = false;
  spr.flipy = false;
}

export function sprAnimGhostEyes(ghostType: GhostType, dir: Dir): void {
  if (!(dir >= Dir.DIR_RIGHT && dir < Dir.NUM_DIRS)) throw new Error('sprAnimGhostEyes: bad dir');
  const tiles: number[] = [32, 34, 36, 38];
  const spr = sprGhost(ghostType);
  spr.tile = tiles[dir]!;
  spr.color = COLOR_EYES;
  spr.flipx = false;
  spr.flipy = false;
}

// --- dynamic tile and sprite updates (pacman.c 1584-1732) ---

export function gameUpdateTiles(): void {
  vidColorScore(i2(6, 1), COLOR_DEFAULT, state.game.score);
  if (state.game.hiscore > 0) {
    vidColorScore(i2(16, 1), COLOR_DEFAULT, state.game.hiscore);
  }

  const pillPos: Int2[] = [i2(1, 6), i2(26, 6), i2(1, 26), i2(26, 26)];
  for (let i = 0; i < NUM_PILLS; i++) {
    if (state.game.freeze.size !== 0) {
      vidColor(pillPos[i]!, COLOR_DOT);
    } else {
      vidColor(pillPos[i]!, (state.timing.tick & 0x8) !== 0 ? 0x10 : 0x00);
    }
  }

  if (afterOnce(state.game.fruitEaten, 2 * 60)) {
    vidFruitScore(Fruit.FRUIT_NONE);
  }

  for (let i = 0; i < NUM_LIVES; i++) {
    const color = i < state.game.numLives ? COLOR_PACMAN : 0;
    vidDrawTileQuad(i2(2 + 2 * i, 34), color, TILE_LIFE);
  }

  // bonus fruit list in the bottom-right corner
  {
    let x = 24;
    const round = state.game.round;
    for (let i = round - NUM_STATUS_FRUITS + 1; i <= round; i++) {
      if (i >= 0) {
        const fruit = levelspec(i).bonusFruit;
        vidDrawTileQuad(i2(x, 34), fruitTilesColors[fruit]![2]!, fruitTilesColors[fruit]![0]!);
        x -= 2;
      }
    }
  }

  // if the round was won, blink the whole playfield blue/white
  if (after(state.game.roundWon, 1 * 60)) {
    if ((since(state.game.roundWon) & 0x10) !== 0) {
      vidColorPlayfield(COLOR_DOT);
    } else {
      vidColorPlayfield(COLOR_WHITE_BORDER);
    }
  }
}

export function gameUpdateSprites(): void {
  // Pacman sprite
  {
    const spr = sprPacman();
    if (spr.enabled) {
      const actor = state.game.pacman.actor;
      spr.pos = actorToSpritePos(actor.pos);
      if (state.game.freeze.has(FreezeType.FREEZETYPE_EAT_GHOST)) {
        spr.tile = SPRITETILE_INVISIBLE;
      } else if (
        state.game.freeze.has(FreezeType.FREEZETYPE_PRELUDE) ||
        state.game.freeze.has(FreezeType.FREEZETYPE_READY)
      ) {
        spr.tile = SPRITETILE_PACMAN_CLOSED_MOUTH;
      } else if (state.game.freeze.has(FreezeType.FREEZETYPE_DEAD)) {
        if (after(state.game.pacmanEaten, PACMAN_EATEN_TICKS)) {
          sprAnimPacmanDeath(since(state.game.pacmanEaten) - PACMAN_EATEN_TICKS);
        }
      } else {
        sprAnimPacman(actor.dir, actor.animTick);
      }
    }
  }

  // ghost sprites
  for (let i = 0; i < state.game.ghost.length; i++) {
    const sprite = sprGhost(i as GhostType);
    if (sprite.enabled) {
      const ghost = state.game.ghost[i]!;
      sprite.pos = actorToSpritePos(ghost.actor.pos);
      if (state.game.freeze.has(FreezeType.FREEZETYPE_DEAD)) {
        if (after(state.game.pacmanEaten, PACMAN_EATEN_TICKS)) {
          sprite.tile = SPRITETILE_INVISIBLE;
        }
      } else if (state.game.freeze.has(FreezeType.FREEZETYPE_WON)) {
        sprite.tile = SPRITETILE_INVISIBLE;
      } else {
        switch (ghost.state) {
          case GhostState.GHOSTSTATE_EYES:
            if (before(ghost.eaten, GHOST_EATEN_FREEZE_TICKS)) {
              // show the score number for the just-eaten ghost
              sprite.tile = SPRITETILE_SCORE_200 + state.game.numGhostsEaten - 1;
              sprite.color = COLOR_GHOST_SCORE;
            } else {
              sprAnimGhostEyes(i as GhostType, ghost.nextDir);
            }
            break;
          case GhostState.GHOSTSTATE_ENTERHOUSE:
            sprAnimGhostEyes(i as GhostType, ghost.actor.dir);
            break;
          case GhostState.GHOSTSTATE_FRIGHTENED:
            sprAnimGhostFrightened(i as GhostType, since(ghost.frightened));
            break;
          default:
            sprAnimGhost(i as GhostType, ghost.nextDir, ghost.actor.animTick);
            break;
        }
      }
    }
  }

  // bonus fruit sprite
  if (state.game.activeFruit === Fruit.FRUIT_NONE) {
    sprFruit().enabled = false;
  } else {
    const spr = sprFruit();
    spr.enabled = true;
    spr.pos = i2(13 * TILE_WIDTH, 19 * TILE_HEIGHT + (TILE_HEIGHT >> 1));
    spr.tile = fruitTilesColors[state.game.activeFruit]![1]!;
    spr.color = fruitTilesColors[state.game.activeFruit]![2]!;
  }
}

// --- gfx decode: ROM data into the tile texture and palette (pacman.c 2404-2640) ---

function gfxDecodeTile8x4(
  texX: number,
  texY: number,
  tileBase: Uint8Array,
  tileStride: number,
  tileOffset: number,
  tileCode: number,
): void {
  for (let tx = 0; tx < TILE_WIDTH; tx++) {
    const ti = tileCode * tileStride + tileOffset + (7 - tx);
    for (let ty = 0; ty < TILE_HEIGHT >> 1; ty++) {
      const pHi = (tileBase[ti]! >> (7 - ty)) & 1;
      const pLo = (tileBase[ti]! >> (3 - ty)) & 1;
      const p = (pHi << 1) | pLo;
      state.gfx.tilePixels[(texY + ty) * TILE_TEXTURE_WIDTH + (texX + tx)] = p;
    }
  }
}

function gfxDecodeTile(tileCode: number): void {
  const x = tileCode * TILE_WIDTH;
  gfxDecodeTile8x4(x, 0, romTiles, 16, 8, tileCode);
  gfxDecodeTile8x4(x, TILE_HEIGHT >> 1, romTiles, 16, 0, tileCode);
}

function gfxDecodeSprite(spriteCode: number): void {
  const x0 = spriteCode * SPRITE_WIDTH;
  const x1 = x0 + TILE_WIDTH;
  const y0 = TILE_HEIGHT;
  const y1 = y0 + (TILE_HEIGHT >> 1);
  const y2 = y1 + (TILE_HEIGHT >> 1);
  const y3 = y2 + (TILE_HEIGHT >> 1);
  gfxDecodeTile8x4(x0, y0, romSprites, 64, 40, spriteCode);
  gfxDecodeTile8x4(x1, y0, romSprites, 64, 8, spriteCode);
  gfxDecodeTile8x4(x0, y1, romSprites, 64, 48, spriteCode);
  gfxDecodeTile8x4(x1, y1, romSprites, 64, 16, spriteCode);
  gfxDecodeTile8x4(x0, y2, romSprites, 64, 56, spriteCode);
  gfxDecodeTile8x4(x1, y2, romSprites, 64, 24, spriteCode);
  gfxDecodeTile8x4(x0, y3, romSprites, 64, 32, spriteCode);
  gfxDecodeTile8x4(x1, y3, romSprites, 64, 0, spriteCode);
}

function gfxDecodeTiles(): void {
  for (let tileCode = 0; tileCode < 256; tileCode++) {
    gfxDecodeTile(tileCode);
  }
  for (let spriteCode = 0; spriteCode < 64; spriteCode++) {
    gfxDecodeSprite(spriteCode);
  }
  // a special opaque 16x16 block used for the fade effect (sprite tile 64)
  for (let y = TILE_HEIGHT; y < TILE_TEXTURE_HEIGHT; y++) {
    for (let x = 64 * SPRITE_WIDTH; x < 65 * SPRITE_WIDTH; x++) {
      state.gfx.tilePixels[y * TILE_TEXTURE_WIDTH + x] = 1;
    }
  }
}

function gfxDecodeColorPalette(): void {
  const hwColors = new Array<number>(32).fill(0);
  for (let i = 0; i < 32; i++) {
    const rgb = romHWColors[i]!;
    const r = ((rgb >> 0) & 1) * 0x21 + ((rgb >> 1) & 1) * 0x47 + ((rgb >> 2) & 1) * 0x97;
    const g = ((rgb >> 3) & 1) * 0x21 + ((rgb >> 4) & 1) * 0x47 + ((rgb >> 5) & 1) * 0x97;
    const b = ((rgb >> 6) & 1) * 0x47 + ((rgb >> 7) & 1) * 0x97;
    hwColors[i] = (0xff000000 | (b << 16) | (g << 8) | r) >>> 0;
  }
  for (let i = 0; i < 256; i++) {
    state.gfx.colorPalette[i] = hwColors[romPalette[i]! & 0xf]!;
    if ((i & 3) === 0) {
      state.gfx.colorPalette[i] = (state.gfx.colorPalette[i]! & 0x00ffffff) >>> 0;
    }
  }
}

// State-side gfx initialization (decode ROM graphics). The Canvas-side
// resources are created separately by the Canvas layer in this module.
export function gfxInit(): void {
  disable(state.gfx.fadein);
  disable(state.gfx.fadeout);
  state.gfx.fade = 0xff;
  sprClear();
  gfxDecodeTiles();
  gfxDecodeColorPalette();
}

// The fade value for the current frame (pacman.c gfx_fade), used by the
// Canvas layer.
export function gfxFade(): void {
  // The original computes in float32; Math.fround at each step
  // reproduces its rounding exactly (in float64, six of the fadein
  // steps would come out one unit brighter).
  if (between(state.gfx.fadein, 0, FADE_TICKS)) {
    const t = Math.fround(since(state.gfx.fadein) / FADE_TICKS);
    state.gfx.fade = Math.trunc(Math.fround(255.0 * Math.fround(1.0 - t)));
  }
  if (afterOnce(state.gfx.fadein, FADE_TICKS)) {
    state.gfx.fade = 0;
  }
  if (between(state.gfx.fadeout, 0, FADE_TICKS)) {
    const t = Math.fround(since(state.gfx.fadeout) / FADE_TICKS);
    state.gfx.fade = Math.trunc(Math.fround(255.0 * t));
  }
  if (afterOnce(state.gfx.fadeout, FADE_TICKS)) {
    state.gfx.fade = 255;
  }
}

// --- Canvas renderer (SPEC T1/T2) ---
//
// The sokol version renders indexed pixels through a palette shader.
// Here, as in the Go port, the palette is baked into pre-rendered
// images instead: one offscreen canvas per (tile, color) and
// (sprite, color) pair. The board is a 224x288 offscreen canvas that
// is updated only where cells changed, then blitted to the visible
// canvas, followed by the sprites, the debug markers and the fade
// overlay (the draw order of pacman.c's gfx_draw).

let viewCanvas: HTMLCanvasElement | null = null;
let viewCtx: CanvasRenderingContext2D | null = null;
let boardCanvas: HTMLCanvasElement | null = null;
let boardCtx: CanvasRenderingContext2D | null = null;
let tileImages: HTMLCanvasElement[][] = []; // [256][32]
let spriteImages: HTMLCanvasElement[][] = []; // [64][32]
let prevVideo: number[][] = [];
let prevColor: number[][] = [];
let boardValid = false;

function makeCanvas(width: number, height: number): HTMLCanvasElement {
  const c = document.createElement('canvas');
  c.width = width;
  c.height = height;
  return c;
}

// Bake one (code, color) image from the decoded pixel buffer.
// Palette indexing mirrors the Go port exactly: the palette entry for
// pixel value p (0..3) under color code c is colorPalette[c*4 + p],
// packed 0xAABBGGRR with the alpha byte cleared for p == 0, so
// transparent pixels let whatever is underneath show through.
function bakeImage(
  texX: number,
  texY: number,
  width: number,
  height: number,
  colorCode: number,
): HTMLCanvasElement {
  const img = makeCanvas(width, height);
  const ctx = img.getContext('2d')!;
  const imageData = ctx.createImageData(width, height);
  const px = imageData.data;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const pix = state.gfx.tilePixels[(texY + y) * TILE_TEXTURE_WIDTH + (texX + x)]!;
      const packed = state.gfx.colorPalette[colorCode * 4 + pix]!;
      const o = (y * width + x) * 4;
      px[o] = packed & 0xff;
      px[o + 1] = (packed >> 8) & 0xff;
      px[o + 2] = (packed >> 16) & 0xff;
      px[o + 3] = (packed >> 24) & 0xff;
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return img;
}

// Set up the Canvas renderer: state-side gfx init, baked tile/sprite
// images, the board offscreen canvas, and reset diff snapshots.
export function initRenderer(canvas: HTMLCanvasElement): void {
  gfxInit();
  viewCanvas = canvas;
  viewCtx = canvas.getContext('2d')!;
  viewCtx.imageSmoothingEnabled = false;

  tileImages = [];
  for (let code = 0; code < 256; code++) {
    const row: HTMLCanvasElement[] = [];
    for (let c = 0; c < 32; c++) {
      row.push(bakeImage(code * TILE_WIDTH, 0, TILE_WIDTH, TILE_HEIGHT, c));
    }
    tileImages.push(row);
  }
  spriteImages = [];
  for (let code = 0; code < 64; code++) {
    const row: HTMLCanvasElement[] = [];
    for (let c = 0; c < 32; c++) {
      row.push(bakeImage(code * SPRITE_WIDTH, TILE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT, c));
    }
    spriteImages.push(row);
  }

  boardCanvas = makeCanvas(DISPLAY_PIXELS_X, DISPLAY_PIXELS_Y);
  boardCtx = boardCanvas.getContext('2d')!;
  boardCtx.fillStyle = '#000';
  boardCtx.fillRect(0, 0, DISPLAY_PIXELS_X, DISPLAY_PIXELS_Y);

  const blank = () =>
    Array.from({ length: DISPLAY_TILES_Y }, () => new Array<number>(DISPLAY_TILES_X).fill(0));
  prevVideo = blank();
  prevColor = blank();
  boardValid = false;
}

// Redraw only the board cells whose tile or color changed.
function updateBoard(): void {
  const ctx = boardCtx!;
  for (let y = 0; y < DISPLAY_TILES_Y; y++) {
    for (let x = 0; x < DISPLAY_TILES_X; x++) {
      const tile = state.gfx.videoRam[y]![x]!;
      const col = state.gfx.colorRam[y]![x]! & 0x1f;
      if (boardValid && tile === prevVideo[y]![x]! && col === (prevColor[y]![x]! & 0x1f)) {
        continue;
      }
      // Clear the cell first: tile images have transparent pixels
      // (palette alpha is 0 for pixel value 0), so compositing the
      // new tile over the old one would leave stale pixels behind
      // (e.g. an eaten dot must disappear completely).
      ctx.fillStyle = '#000';
      ctx.fillRect(x * TILE_WIDTH, y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT);
      ctx.drawImage(tileImages[tile]![col]!, x * TILE_WIDTH, y * TILE_HEIGHT);
      prevVideo[y]![x] = tile;
      prevColor[y]![x] = state.gfx.colorRam[y]![x]!;
    }
  }
  boardValid = true;
}

// Draw one frame (the gfx_draw counterpart): fade value update, board,
// sprites in order, debug markers as tiles, fade overlay.
export function drawFrame(): void {
  if (viewCtx === null || boardCanvas === null) {
    throw new Error('drawFrame: renderer not initialized');
  }
  const ctx = viewCtx;
  gfxFade();
  updateBoard();
  ctx.drawImage(boardCanvas, 0, 0);

  // sprites, in array order
  for (let i = 0; i < NUM_SPRITES; i++) {
    const spr = state.gfx.sprite[i]!;
    if (!spr.enabled) continue;
    const img = spriteImages[spr.tile]![spr.color & 0x1f]!;
    if (!spr.flipx && !spr.flipy) {
      ctx.drawImage(img, spr.pos.x, spr.pos.y);
    } else {
      ctx.save();
      ctx.translate(
        spr.pos.x + (spr.flipx ? SPRITE_WIDTH : 0),
        spr.pos.y + (spr.flipy ? SPRITE_HEIGHT : 0),
      );
      ctx.scale(spr.flipx ? -1 : 1, spr.flipy ? -1 : 1);
      ctx.drawImage(img, 0, 0);
      ctx.restore();
    }
  }

  // debug markers are drawn as playfield tiles (never enabled by the
  // game itself)
  for (let i = 0; i < NUM_DEBUG_MARKERS; i++) {
    const dbg = state.gfx.debugMarker[i]!;
    if (!dbg.enabled) continue;
    ctx.drawImage(
      tileImages[dbg.tile]![dbg.color & 0x1f]!,
      dbg.tilePos.x * TILE_WIDTH,
      dbg.tilePos.y * TILE_HEIGHT,
    );
  }

  // fade: a black overlay whose opacity is the fade value
  if (state.gfx.fade > 0) {
    ctx.fillStyle = `rgba(0, 0, 0, ${state.gfx.fade / 255})`;
    ctx.fillRect(0, 0, DISPLAY_PIXELS_X, DISPLAY_PIXELS_Y);
  }
}
```

## sound.ts

```ts
// sound.ts -- the Namco sound-board register layer and sound effects.
// Corresponds to pacman.c lines 638-678 (descriptions) and 3125-3388
// (logic). The sample generation itself lives in synth.ts and runs in
// the AudioWorklet (SPEC T3); this module maintains the sound/voice
// register state on the game side, exactly like the original.

import {
  state,
  newVoice,
  newSound,
  NUM_VOICES,
  NUM_SOUNDS,
  SoundFlag,
  SOUNDFLAG_ALL_VOICES,
  NO_SOUND_FUNC,
  type SoundDesc,
} from './state.js';
import { sndDumpPrelude, sndDumpDead } from './romdata.js';

// clear all active sound effects and start outputting silence
export function sndClear(): void {
  for (let i = 0; i < NUM_VOICES; i++) {
    state.audio.voice[i] = newVoice();
  }
  for (let i = 0; i < NUM_SOUNDS; i++) {
    state.audio.sound[i] = newSound();
  }
}

// stop a sound effect
export function sndStop(slot: number): void {
  if (!(slot >= 0 && slot < NUM_SOUNDS)) throw new Error('sndStop: bad slot');
  for (let i = 0; i < NUM_VOICES; i++) {
    if (state.audio.sound[slot]!.flags.has(i as SoundFlag)) {
      state.audio.voice[i] = newVoice();
    }
  }
  state.audio.sound[slot] = newSound();
}

// start a sound effect
export function sndStart(slot: number, desc: SoundDesc): void {
  if (!(slot >= 0 && slot < NUM_SOUNDS)) throw new Error('sndStart: bad slot');
  if (!((desc.data !== null && desc.size !== 0) || desc.fn !== NO_SOUND_FUNC))
    throw new Error('sndStart: empty desc');
  const snd = newSound();
  state.audio.sound[slot] = snd;
  let numVoices = 0;
  for (let i = 0; i < NUM_VOICES; i++) {
    if (desc.voice[i]) {
      snd.flags.add(i as SoundFlag);
      numVoices += 1;
    }
  }
  if (desc.fn !== NO_SOUND_FUNC) {
    snd.fn = desc.fn;
  } else {
    if (!(numVoices > 0)) throw new Error('sndStart: dump needs voices');
    if (desc.size % (numVoices * 4) !== 0) throw new Error('sndStart: bad dump size');
    snd.stride = numVoices;
    snd.numTicks = Math.trunc(desc.size / (snd.stride * 4));
    snd.data = desc.data;
  }
}

// --- procedural sound effects (pacman.c 3281-3388) ---
// Identified by index into soundGenerators (see state.ts SoundFuncId).

function sndFuncEatdot1(slot: number): void {
  const snd = state.audio.sound[slot]!;
  const voice = state.audio.voice[2]!;
  if (snd.curTick === 0) {
    voice.volume = 12;
    voice.waveform = 2;
    voice.frequency = 0x1500;
  } else if (snd.curTick === 5) {
    sndStop(slot);
  } else {
    voice.frequency -= 0x0300;
  }
}

function sndFuncEatdot2(slot: number): void {
  const snd = state.audio.sound[slot]!;
  const voice = state.audio.voice[2]!;
  if (snd.curTick === 0) {
    voice.volume = 12;
    voice.waveform = 2;
    voice.frequency = 0x0700;
  } else if (snd.curTick === 5) {
    sndStop(slot);
  } else {
    voice.frequency += 0x300;
  }
}

function sndFuncEatghost(slot: number): void {
  const snd = state.audio.sound[slot]!;
  const voice = state.audio.voice[2]!;
  if (snd.curTick === 0) {
    voice.volume = 12;
    voice.waveform = 5;
    voice.frequency = 0;
  } else if (snd.curTick === 32) {
    sndStop(slot);
  } else {
    voice.frequency += 0x20;
  }
}

function sndFuncEatfruit(slot: number): void {
  const snd = state.audio.sound[slot]!;
  const voice = state.audio.voice[2]!;
  if (snd.curTick === 0) {
    voice.volume = 15;
    voice.waveform = 6;
    voice.frequency = 0x1600;
  } else if (snd.curTick === 23) {
    sndStop(slot);
  } else if (snd.curTick < 11) {
    voice.frequency -= 0x200;
  } else {
    voice.frequency += 0x0200;
  }
}

function sndFuncWeeooh(slot: number): void {
  const snd = state.audio.sound[slot]!;
  const voice = state.audio.voice[1]!;
  if (snd.curTick === 0) {
    voice.volume = 6;
    voice.waveform = 6;
    voice.frequency = 0x1000;
  } else if (snd.curTick % 24 < 12) {
    voice.frequency += 0x0200;
  } else {
    voice.frequency -= 0x0200;
  }
}

function sndFuncFrightened(slot: number): void {
  const snd = state.audio.sound[slot]!;
  const voice = state.audio.voice[1]!;
  if (snd.curTick === 0) {
    voice.volume = 10;
    voice.waveform = 4;
    voice.frequency = 0x0180;
  } else if (snd.curTick % 8 === 0) {
    voice.frequency = 0x0180;
  } else {
    voice.frequency += 0x180;
  }
}

export const GEN_EATDOT1 = 0;
export const GEN_EATDOT2 = 1;
export const GEN_EATGHOST = 2;
export const GEN_EATFRUIT = 3;
export const GEN_WEEOOH = 4;
export const GEN_FRIGHTENED = 5;

export const soundGenerators: ((slot: number) => void)[] = [
  sndFuncEatdot1,
  sndFuncEatdot2,
  sndFuncEatghost,
  sndFuncEatfruit,
  sndFuncWeeooh,
  sndFuncFrightened,
];

// --- sound effect descriptions (pacman.c 638-678) ---
export const sndPrelude: SoundDesc = {
  fn: NO_SOUND_FUNC,
  data: sndDumpPrelude,
  size: sndDumpPrelude.byteLength,
  voice: [true, true, false],
};
export const sndDead: SoundDesc = {
  fn: NO_SOUND_FUNC,
  data: sndDumpDead,
  size: sndDumpDead.byteLength,
  voice: [false, false, true],
};
export const sndEatdot1: SoundDesc = { fn: GEN_EATDOT1, data: null, size: 0, voice: [false, false, true] };
export const sndEatdot2: SoundDesc = { fn: GEN_EATDOT2, data: null, size: 0, voice: [false, false, true] };
export const sndEatghost: SoundDesc = { fn: GEN_EATGHOST, data: null, size: 0, voice: [false, false, true] };
export const sndEatfruit: SoundDesc = { fn: GEN_EATFRUIT, data: null, size: 0, voice: [false, false, true] };
export const sndWeeooh: SoundDesc = { fn: GEN_WEEOOH, data: null, size: 0, voice: [false, true, false] };
export const sndFrightened: SoundDesc = { fn: GEN_FRIGHTENED, data: null, size: 0, voice: [false, true, false] };

// the sound system's 60 Hz tick function (called from the game tick)
export function sndTick(): void {
  for (let slot = 0; slot < NUM_SOUNDS; slot++) {
    let snd = state.audio.sound[slot]!;
    let skipIncrement = false;
    if (snd.fn !== NO_SOUND_FUNC) {
      soundGenerators[snd.fn]!(slot);
      // a generator may stop its own sound, which replaces the slot
      // object (sndStop); the increment below must land on the
      // current object, as in Nim where the slot is reached through
      // a pointer after the call
      snd = state.audio.sound[slot]!;
    } else if (snd.flags.size > 0 && [...snd.flags].some((f) => SOUNDFLAG_ALL_VOICES.has(f))) {
      if (snd.data === null) throw new Error('sndTick: dump sound without data');
      if (snd.curTick === snd.numTicks) {
        sndStop(slot);
        skipIncrement = true;
      } else {
        let idx = snd.curTick * snd.stride;
        for (let i = 0; i < NUM_VOICES; i++) {
          if (snd.flags.has(i as SoundFlag)) {
            const voice = state.audio.voice[i]!;
            const val = snd.data[idx]!;
            idx += 1;
            voice.frequency = val & ((1 << 20) - 1);
            voice.waveform = (val >>> 24) & 7;
            voice.volume = (val >>> 28) & 0xf;
          }
        }
      }
    }
    if (!skipIncrement) {
      snd.curTick += 1;
    }
  }
}

// The current voice registers, for the AudioWorklet bridge (SPEC T3).
// The synth keeps its own phase counters; only the register values
// cross the boundary.
export interface VoiceRegs {
  frequency: number;
  waveform: number;
  volume: number;
}

export function voiceSnapshot(): VoiceRegs[] {
  return state.audio.voice.map((v) => ({
    frequency: v.frequency,
    waveform: v.waveform,
    volume: v.volume,
  }));
}
```

## synth.ts

```ts
// synth.ts -- the sample-generation side of the Namco sound board.
// Corresponds to the audio-callback half of pacman.c (snd_voice_tick
// and snd_sample_tick). The register layer in sound.ts updates the
// voice registers at 60 Hz on the game side; this class turns register
// snapshots into samples and runs inside the AudioWorklet (SPEC T3).
// The phase counters (counter, sampleAcc, sampleDiv) live here, not
// in the snapshot, exactly as in the original where they are part of
// the sound-board state driven by the audio callback.

import { AUDIO_VOLUME, NUM_VOICES } from './state.js';
import { romWavetable } from './romdata.js';
import type { VoiceRegs } from './sound.js';

interface SynthVoice {
  // register values, copied in by setVoices()
  frequency: number;
  waveform: number;
  volume: number;
  // phase state, owned by the synth
  counter: number; // uint32 phase accumulator
  sampleAcc: number;
  sampleDiv: number;
}

export class Synth {
  private readonly voiceTickPeriod: number; // in milli-units of a 96 kHz tick
  private voiceTickAccum = 0;
  private readonly voices: SynthVoice[] = [];

  constructor(sampleRate: number) {
    // number of 96 kHz ticks per output sample, times 1000 for
    // precision; integer division like the original's snd_init
    this.voiceTickPeriod = Math.trunc(96_000_000 / sampleRate);
    for (let i = 0; i < NUM_VOICES; i++) {
      this.voices.push({
        frequency: 0,
        waveform: 0,
        volume: 0,
        counter: 0,
        sampleAcc: 0,
        sampleDiv: 0,
      });
    }
  }

  // Copy a register snapshot from the game side (sound.ts
  // voiceSnapshot). Only frequency/waveform/volume cross the
  // boundary; the phase counters stay here.
  setVoices(regs: VoiceRegs[]): void {
    for (let i = 0; i < NUM_VOICES; i++) {
      const v = this.voices[i]!;
      const r = regs[i]!;
      v.frequency = r.frequency;
      v.waveform = r.waveform;
      v.volume = r.volume;
    }
  }

  // Fill out with mono samples at the constructor's sample rate.
  render(out: Float32Array): void {
    for (let i = 0; i < out.length; i++) {
      this.voiceTickAccum -= this.voiceTickPeriod;
      while (this.voiceTickAccum < 0) {
        this.voiceTickAccum += 1000;
        this.voiceTick();
      }
      out[i] = this.sampleTick();
    }
  }

  // updates the Namco sound generator once (must be called at 96 kHz)
  private voiceTick(): void {
    for (const voice of this.voices) {
      voice.counter = (voice.counter + voice.frequency) >>> 0;
      const waveIndex =
        ((voice.waveform << 5) | ((voice.counter >>> 15) & 0x1f)) & 0xff;
      voice.sampleAcc += ((romWavetable[waveIndex]! & 0xf) - 8) * voice.volume;
      voice.sampleDiv += 128;
    }
  }

  // computes one output sample from the per-voice averages
  private sampleTick(): number {
    let sm = 0;
    for (const voice of this.voices) {
      if (voice.sampleDiv > 0) {
        sm += voice.sampleAcc / voice.sampleDiv;
        voice.sampleAcc = 0;
        voice.sampleDiv = 0;
      }
    }
    return sm * 0.333333 * AUDIO_VOLUME;
  }
}
```

## worklet.ts

```ts
// worklet.ts -- the AudioWorklet processor (SPEC T3). Runs on the
// audio rendering thread. The game side posts a voice register
// snapshot (sound.ts voiceSnapshot) once per game tick; this
// processor turns the snapshots into samples via Synth. Ambient
// declarations for this scope live in worklet.d.ts.

/// <reference path="./worklet.d.ts" />

import { Synth } from './synth.js';
import type { VoiceRegs } from './sound.js';

class PacmanSynthProcessor extends AudioWorkletProcessor {
  private readonly synth: Synth;

  constructor() {
    super();
    this.synth = new Synth(sampleRate);
    this.port.onmessage = (event: MessageEvent) => {
      this.synth.setVoices(event.data as VoiceRegs[]);
    };
  }

  process(
    _inputs: Float32Array[][],
    outputs: Float32Array[][],
  ): boolean {
    const channels = outputs[0]!;
    const left = channels[0]!;
    this.synth.render(left);
    if (channels.length > 1) {
      channels[1]!.set(left);
    }
    return true;
  }
}

registerProcessor('pacman-synth', PacmanSynthProcessor);
```

## worklet.d.ts

```ts
// worklet.d.ts -- minimal ambient declarations for the AudioWorklet
// global scope, which the DOM lib does not describe. Kept in a
// separate declaration file so worklet.ts can be type-checked in the
// same program as the DOM-based game code without conflicts.

declare class AudioWorkletProcessor {
  readonly port: MessagePort;
  constructor();
}

declare const sampleRate: number;

declare function registerProcessor(
  name: string,
  processorCtor: new () => AudioWorkletProcessor,
): void;
```

## input.ts

```ts
// input.ts -- keyboard and touch input (SPEC T8).
// Corresponds to the input() callback in pacman.nim (pacman.c's
// sokol-app event callback): DOM key events are the closest browser
// equivalent for the keyboard. Touch follows the design decided for
// the Go port (SPEC H8 there): swipe with a latch, tap is "any key".
//
// This module is the single input merge point: the keyboard and touch
// listeners below resolve into the state.input fields, and nothing
// else in the game reads input devices. A future gamepad source
// would feed the same resolution. Like the original's event
// callback, nothing is written while input is disabled.
//
// Resolution (as in the Go port): held keyboard directions win;
// the latched touch direction applies only when nothing is held.
// timing.ts inputDir() then applies the original's priority
// (up, down, right, left) to the resolved flags.

import {
  state,
  Dir,
  DISPLAY_PIXELS_X,
  DISPLAY_PIXELS_Y,
} from './state.js';

// logical pixels a swipe must travel before it counts (about 3 tiles)
export const TOUCH_SWIPE_THRESHOLD = 24;

// The direction of a swipe delta, or null below the threshold.
// The larger axis wins; a tie goes vertical (as in the Go port).
export function swipeDirection(dx: number, dy: number): Dir | null {
  if (Math.max(Math.abs(dx), Math.abs(dy)) < TOUCH_SWIPE_THRESHOLD) return null;
  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? Dir.DIR_RIGHT : Dir.DIR_LEFT;
  }
  return dy > 0 ? Dir.DIR_DOWN : Dir.DIR_UP;
}

export interface HeldDirs {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

// Resolve held keyboard directions and the touch latch into the
// direction flags the game sees: held first, then the latch.
export function resolveDirections(kb: HeldDirs, latch: Dir | null): HeldDirs {
  if (kb.up || kb.down || kb.left || kb.right) {
    return { up: kb.up, down: kb.down, left: kb.left, right: kb.right };
  }
  return {
    up: latch === Dir.DIR_UP,
    down: latch === Dir.DIR_DOWN,
    left: latch === Dir.DIR_LEFT,
    right: latch === Dir.DIR_RIGHT,
  };
}

// --- merged input state (this module only) ---
const kb: HeldDirs = { up: false, down: false, left: false, right: false };
let kbAny = false;
let touchLatch: Dir | null = null;
let tapActive = false;

function publishDirections(): void {
  const r = resolveDirections(kb, touchLatch);
  state.input.up = r.up;
  state.input.down = r.down;
  state.input.left = r.left;
  state.input.right = r.right;
}

function writeAnykey(): void {
  state.input.anykey = kbAny || tapActive;
}

let tapPending = false;
let tapClearArmed = false;

function pulseTap(): void {
  tapPending = true;
}

// Called once per frame from main.ts (the counterpart of the Go
// port's per-Update input read): a tap's "any key" is visible for
// exactly one frame's ticks, and a tap that lands while input is
// disabled is dropped -- nothing is written while disabled.
export function pollInput(): void {
  if (tapClearArmed) {
    tapClearArmed = false;
    tapActive = false;
    if (state.input.enabled) writeAnykey();
  }
  if (tapPending) {
    tapPending = false;
    if (state.input.enabled) {
      tapActive = true;
      writeAnykey();
      tapClearArmed = true;
    }
  }
}

// --- keyboard ---

function toggleFullscreen(): void {
  if (document.fullscreenElement) {
    void document.exitFullscreen();
  } else {
    void document.documentElement.requestFullscreen();
  }
}

// A key release must be remembered even while input is disabled, or the
// held flag stays true and wins the resolution after input is enabled again.
function forgetKey(code: string): void {
  switch (code) {
    case 'ArrowUp':
    case 'KeyW':
      kb.up = false;
      break;
    case 'ArrowDown':
    case 'KeyS':
      kb.down = false;
      break;
    case 'ArrowLeft':
    case 'KeyA':
      kb.left = false;
      break;
    case 'ArrowRight':
    case 'KeyD':
      kb.right = false;
      break;
  }
  kbAny = false;
}

function onKey(e: KeyboardEvent, btnDown: boolean): void {
  // keep the page from scrolling on the arrow keys (this is a page
  // concern, so it applies whether or not input is enabled)
  if (e.code.startsWith('Arrow')) e.preventDefault();
  if (!state.input.enabled) {
    if (!btnDown) forgetKey(e.code);
    return;
  }
  switch (e.code) {
    case 'ArrowUp':
    case 'KeyW':
      kb.up = btnDown;
      kbAny = btnDown;
      publishDirections();
      writeAnykey();
      break;
    case 'ArrowDown':
    case 'KeyS':
      kb.down = btnDown;
      kbAny = btnDown;
      publishDirections();
      writeAnykey();
      break;
    case 'ArrowLeft':
    case 'KeyA':
      kb.left = btnDown;
      kbAny = btnDown;
      publishDirections();
      writeAnykey();
      break;
    case 'ArrowRight':
    case 'KeyD':
      kb.right = btnDown;
      kbAny = btnDown;
      publishDirections();
      writeAnykey();
      break;
    case 'Escape':
      state.input.esc = btnDown;
      kbAny = btnDown;
      writeAnykey();
      break;
    case 'KeyF':
      if (btnDown) toggleFullscreen();
      break;
    default:
      kbAny = btnDown;
      writeAnykey();
      break;
  }
}

// --- touch: swipe with a latch, tap is "any key" ---

interface TouchTrack {
  id: number;
  originX: number;
  originY: number;
  swiped: boolean;
}

let track: TouchTrack | null = null;

function toLogical(canvas: HTMLCanvasElement, clientX: number, clientY: number): { x: number; y: number } {
  const rect = canvas.getBoundingClientRect();
  return {
    x: ((clientX - rect.left) * DISPLAY_PIXELS_X) / rect.width,
    y: ((clientY - rect.top) * DISPLAY_PIXELS_Y) / rect.height,
  };
}

function attachTouch(canvas: HTMLCanvasElement): void {
  canvas.addEventListener(
    'touchstart',
    (e) => {
      if (!state.input.enabled) return;
      e.preventDefault();
      if (track === null) {
        const t = e.changedTouches[0]!;
        const p = toLogical(canvas, t.clientX, t.clientY);
        track = { id: t.identifier, originX: p.x, originY: p.y, swiped: false };
      }
    },
    { passive: false },
  );
  canvas.addEventListener(
    'touchmove',
    (e) => {
      if (!state.input.enabled) return;
      e.preventDefault();
      if (track === null) return;
      const tr = track;
      for (const t of Array.from(e.changedTouches)) {
        if (t.identifier !== tr.id) continue;
        const p = toLogical(canvas, t.clientX, t.clientY);
        const dir = swipeDirection(p.x - tr.originX, p.y - tr.originY);
        if (dir !== null) {
          touchLatch = dir;
          tr.swiped = true;
          // advance the origin so a long swipe keeps producing directions
          tr.originX = p.x;
          tr.originY = p.y;
          publishDirections();
        }
      }
    },
    { passive: false },
  );
  const end = (e: TouchEvent, allowTap: boolean): void => {
    if (track === null) return;
    const tr = track;
    for (const t of Array.from(e.changedTouches)) {
      if (t.identifier !== tr.id) continue;
      track = null;
      // a release counts as a tap; an OS interruption (touchcancel)
      // does not (as in the Go port, where a tap is judged from the
      // touch being released)
      if (allowTap && !tr.swiped && state.input.enabled) {
        pulseTap();
      }
    }
  };
  canvas.addEventListener('touchend', (e) => end(e, true));
  canvas.addEventListener('touchcancel', (e) => end(e, false));
}

export function attachInput(): void {
  window.addEventListener('keydown', (e) => onKey(e, true));
  window.addEventListener('keyup', (e) => onKey(e, false));
  const canvas = document.getElementById('game');
  if (canvas instanceof HTMLCanvasElement) {
    attachTouch(canvas);
  }
}
```

## main.ts

```ts
// main.ts -- application entry point.
// Corresponds to pacman.nim (pacman.c lines 716-825: the sokol-app
// init/frame callbacks), with sokol-app replaced by
// requestAnimationFrame and DOM events (SPEC T2/T8/T10) and
// sokol-audio replaced by an AudioWorklet bridge (SPEC T3/T4).

import {
  state,
  TICK_DURATION_NS,
  TICK_TOLERANCE_NS,
  DISPLAY_PIXELS_X,
  DISPLAY_PIXELS_Y,
} from './state.js';
import { runTick, initGame } from './rules.js';
import { initRenderer, drawFrame } from './render.js';
import { attachInput, pollInput } from './input.js';
import { voiceSnapshot } from './sound.js';

// --- audio bridge (SPEC T3/T4) ---
//
// The AudioContext is created lazily on the first user gesture
// (autoplay policy). If setup fails, the game simply runs silently.
//
// Two robustness points (external review): resume() is called
// synchronously inside the gesture, before any await -- after an
// await the call may fall outside the gesture window and the
// context stays suspended (notably on iOS). And the gesture
// listeners are not one-shot: a later gesture retries the resume
// if the first attempt did not start the sound.

let audioCtx: AudioContext | null = null;
let audioPort: MessagePort | null = null;
let audioSetupStarted = false;

function resumeAudio(): void {
  if (audioCtx === null) return;
  // 'interrupted' (iOS, after an interruption) needs a resume just
  // like 'suspended'; a closed context cannot be resumed
  if (audioCtx.state !== 'running' && audioCtx.state !== 'closed') {
    void audioCtx.resume();
  }
}

async function setupAudio(): Promise<void> {
  if (audioCtx !== null) {
    resumeAudio();
    return;
  }
  if (audioSetupStarted) return;
  audioSetupStarted = true;
  try {
    const ctx = new AudioContext();
    audioCtx = ctx;
    void ctx.resume();
    await ctx.audioWorklet.addModule(new URL('./worklet.js', import.meta.url));
    const node = new AudioWorkletNode(ctx, 'pacman-synth');
    node.connect(ctx.destination);
    audioPort = node.port;
  } catch {
    audioPort = null;
    // reset, so the next gesture retries the setup from the
    // beginning (a failed module load must not silence the game
    // for the whole session)
    const failed = audioCtx;
    audioCtx = null;
    audioSetupStarted = false;
    if (failed !== null) void failed.close();
  }
}

// While the tab is hidden, requestAnimationFrame stops and no new
// register snapshots reach the worklet, which would keep sounding
// the last state forever; suspend the context instead, and resume
// when the tab is visible again.
function onVisibilityChange(): void {
  if (audioCtx === null) return;
  if (document.hidden) {
    void audioCtx.suspend();
  } else {
    resumeAudio();
  }
}

// --- the frame loop: pacman.nim frame() ---
//
// Run the game at a fixed tick rate regardless of frame rate: real
// elapsed time is accumulated and converted into whole ticks, with
// the frame time clamped to 33,333,333 ns (the original's design,
// carried over unchanged -- SPEC section 1).

const FRAME_TIME_MAX_NS = 33_333_333;

function frame(): void {
  const nowMs = performance.now();
  let frameTimeNs = Math.trunc((nowMs - state.timing.laptimeStore) * 1_000_000);
  state.timing.laptimeStore = nowMs;
  if (frameTimeNs > FRAME_TIME_MAX_NS) frameTimeNs = FRAME_TIME_MAX_NS;
  if (frameTimeNs < 0) frameTimeNs = 0;
  state.timing.tickAccum += frameTimeNs;
  pollInput();
  let ticks = 0;
  while (state.timing.tickAccum > -TICK_TOLERANCE_NS) {
    state.timing.tickAccum -= TICK_DURATION_NS;
    runTick();
    ticks++;
  }
  drawFrame();
  if (audioPort !== null && ticks > 0) {
    audioPort.postMessage(voiceSnapshot());
  }
  requestAnimationFrame(frame);
}

// --- init: pacman.nim init() ---
//
// initGame() (rules.ts) performs the game-side init: gfxInit and the
// intro start; the xorshift seed is set by gameInit in rules.ts.
// initRenderer then creates the Canvas resources (it runs the
// idempotent gfxInit decode once more). sndInit's counterpart is the
// lazy AudioContext setup above.

// Scale the display to the window at an integer multiple of the
// logical 224x288 (SPEC T2), so the game fits phone screens
// instead of being clipped at a fixed 448x576. If even 1x does not
// fit, fall back to a fractional fit rather than clipping.
function fitCanvas(canvas: HTMLCanvasElement): void {
  const fit = Math.min(window.innerWidth / DISPLAY_PIXELS_X, window.innerHeight / DISPLAY_PIXELS_Y);
  const scale = Math.floor(fit);
  let w: number;
  let h: number;
  if (scale >= 1) {
    w = DISPLAY_PIXELS_X * scale;
    h = DISPLAY_PIXELS_Y * scale;
  } else {
    w = Math.max(1, Math.floor(DISPLAY_PIXELS_X * fit));
    h = Math.max(1, Math.floor(DISPLAY_PIXELS_Y * fit));
  }
  canvas.style.width = `${w}px`;
  canvas.style.height = `${h}px`;
}

function init(): void {
  const canvas = document.getElementById('game');
  if (!(canvas instanceof HTMLCanvasElement)) throw new Error('main: #game canvas not found');
  initGame();
  initRenderer(canvas);
  attachInput();
  fitCanvas(canvas);
  window.addEventListener('resize', () => fitCanvas(canvas));
  const kickAudio = (): void => {
    void setupAudio();
  };
  window.addEventListener('keydown', kickAudio);
  window.addEventListener('pointerdown', kickAudio);
  window.addEventListener('touchend', kickAudio);
  window.addEventListener('click', kickAudio);
  document.addEventListener('visibilitychange', onVisibilityChange);
  state.timing.laptimeStore = performance.now();
  requestAnimationFrame(frame);
}

init();
```

## romdata.ts

```ts
// romdata.ts -- ROM data extracted mechanically from pacman.c (lines 3389-4303).
// Generated by tools/extract.mjs. Do not edit by hand.

export const romTiles = new Uint8Array([
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
]);

export const romSprites = new Uint8Array([
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
]);

export const romHWColors = new Uint8Array([
  0x00, 0x07, 0x66, 0xEF, 0x00, 0xF8, 0xEA, 0x6F, 0x00, 0x3F, 0x00, 0xC9, 0x38, 0xAA, 0xAF, 0xF6,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]);

export const romPalette = new Uint8Array([
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
]);

export const romWavetable = new Uint8Array([
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
]);

export const sndDumpPrelude = new Uint32Array([
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
]);

export const sndDumpDead = new Uint32Array([
  0xF1001F00, 0xF1001E00, 0xF1001D00, 0xF1001C00, 0xF1001B00, 0xF1001C00, 0xF1001D00, 0xF1001E00, 0xF1001F00, 0xF1002000, 0xF1002100, 0xE1001D00, 0xE1001C00, 0xE1001B00, 0xE1001A00, 0xE1001900,
  0xE1001800, 0xE1001900, 0xE1001A00, 0xE1001B00, 0xE1001C00, 0xE1001D00, 0xE1001E00, 0xD1001B00, 0xD1001A00, 0xD1001900, 0xD1001800, 0xD1001700, 0xD1001600, 0xD1001700, 0xD1001800, 0xD1001900,
  0xD1001A00, 0xD1001B00, 0xD1001C00, 0xC1001900, 0xC1001800, 0xC1001700, 0xC1001600, 0xC1001500, 0xC1001400, 0xC1001500, 0xC1001600, 0xC1001700, 0xC1001800, 0xC1001900, 0xC1001A00, 0xB1001700,
  0xB1001600, 0xB1001500, 0xB1001400, 0xB1001300, 0xB1001200, 0xB1001300, 0xB1001400, 0xB1001500, 0xB1001600, 0xB1001700, 0xB1001800, 0xA1001500, 0xA1001400, 0xA1001300, 0xA1001200, 0xA1001100,
  0xA1001000, 0xA1001100, 0xA1001200, 0x80000800, 0x80001000, 0x80001800, 0x80002000, 0x80002800, 0x80003000, 0x80003800, 0x80004000, 0x80004800, 0x80005000, 0x80005800, 0x00000000, 0x80000800,
  0x80001000, 0x80001800, 0x80002000, 0x80002800, 0x80003000, 0x80003800, 0x80004000, 0x80004800, 0x80005000, 0x80005800,
]);

```

## index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>pacman.c — TypeScript port</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    background: #000;
    height: 100%;
  }
  body {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  #game {
    /* the display size is set by main.ts (integer scaling that
       fits the window); the canvas itself stays 224x288 */
    image-rendering: pixelated;
    touch-action: none;
  }
</style>
</head>
<body>
<canvas id="game" width="224" height="288"></canvas>
<script type="module" src="dist/src/main.js"></script>
</body>
</html>
```

## extract.mjs

```js
// extract.mjs -- generate src/romdata.ts (ROM data) from pacman.c.
//
// Usage: node tools/extract.mjs [path-to-pacman.c] [out-path]
//
// The ROM arrays in pacman.c are pure data; they are carried over
// mechanically, never by hand. Counts are verified here and the sums
// are printed for comparison with SPEC section 1.
import { readFileSync, writeFileSync } from 'node:fs';

const specs = [
  { cName: 'rom_tiles', tsName: 'romTiles', typ: 'Uint8Array', count: 4096, hex: 2 },
  { cName: 'rom_sprites', tsName: 'romSprites', typ: 'Uint8Array', count: 4096, hex: 2 },
  { cName: 'rom_hwcolors', tsName: 'romHWColors', typ: 'Uint8Array', count: 32, hex: 2 },
  { cName: 'rom_palette', tsName: 'romPalette', typ: 'Uint8Array', count: 256, hex: 2 },
  { cName: 'rom_wavetable', tsName: 'romWavetable', typ: 'Uint8Array', count: 256, hex: 2 },
  { cName: 'snd_dump_prelude', tsName: 'sndDumpPrelude', typ: 'Uint32Array', count: 490, hex: 8 },
  { cName: 'snd_dump_dead', tsName: 'sndDumpDead', typ: 'Uint32Array', count: 90, hex: 8 },
];

function extractArray(src, name) {
  const defRe = new RegExp(name + '\\[\\d+\\]\\s*=\\s*\\{');
  const m = defRe.exec(src);
  if (!m) throw new Error(`definition of ${name} not found`);
  const rest = src.slice(m.index + m[0].length);
  const end = rest.indexOf('};');
  if (end < 0) throw new Error(`end of ${name} not found`);
  const body = rest.slice(0, end);
  const tokens = body.match(/0[xX][0-9a-fA-F]+|\d+/g) || [];
  return tokens.map((t) => Number(t));
}

const srcPath = process.argv[2] || new URL('../../floooh-pacman-c/pacman.c', import.meta.url).pathname;
const outPath = process.argv[3] || new URL('../src/romdata.ts', import.meta.url).pathname;
const src = readFileSync(srcPath, 'utf8');

let out = '// romdata.ts -- ROM data extracted mechanically from pacman.c (lines 3389-4303).\n';
out += '// Generated by tools/extract.mjs. Do not edit by hand.\n\n';

for (const sp of specs) {
  const vals = extractArray(src, sp.cName);
  if (vals.length !== sp.count) {
    console.error(`${sp.cName}: got ${vals.length} values, want ${sp.count}`);
    process.exit(1);
  }
  let sum = 0;
  for (const v of vals) sum += v;
  console.log(`${sp.cName}: ${vals.length} values, sum ${sum}`);
  out += `export const ${sp.tsName} = new ${sp.typ}([\n`;
  for (let i = 0; i < vals.length; i += 16) {
    const chunk = vals.slice(i, i + 16)
      .map((v) => '0x' + v.toString(16).toUpperCase().padStart(sp.hex, '0'))
      .join(', ');
    out += `  ${chunk},\n`;
  }
  out += ']);\n\n';
}

writeFileSync(outPath, out);
console.log(`wrote ${outPath}`);
```

## foundation.test.ts

```ts
// foundation.test.ts -- Phase 1 checks: ROM data, xorshift, levelspec,
// trigger vocabulary (SPEC section 4).
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { state, levelspec, MAX_LEVELSPEC, Fruit } from '../src/state.js';
import { xorshift32, start, startAfter, disable, since, between } from '../src/timing.js';
import {
  romTiles,
  romSprites,
  romHWColors,
  romPalette,
  romWavetable,
  sndDumpPrelude,
  sndDumpDead,
} from '../src/romdata.js';

function sum(a: Uint8Array | Uint32Array): number {
  let s = 0;
  for (const v of a) s += v;
  return s;
}

test('romdata counts and sums match pacman.c', () => {
  assert.equal(romTiles.length, 4096);
  assert.equal(sum(romTiles), 267889);
  assert.equal(romSprites.length, 4096);
  assert.equal(sum(romSprites), 227290);
  assert.equal(romHWColors.length, 32);
  assert.equal(sum(romHWColors), 1852);
  assert.equal(romPalette.length, 256);
  assert.equal(sum(romPalette), 589);
  assert.equal(romWavetable.length, 256);
  assert.equal(sum(romWavetable), 1856);
  assert.equal(sndDumpPrelude.length, 490);
  assert.equal(sum(sndDumpPrelude), 1523003578600);
  assert.equal(sndDumpDead.length, 90);
  assert.equal(sum(sndDumpDead), 275197360640);
});

test('xorshift32 sequence matches C semantics', () => {
  state.game.xorshift = 0x12345678;
  const got = [xorshift32(), xorshift32(), xorshift32(), xorshift32(), xorshift32()];
  assert.deepEqual(got, [2274908837, 358294691, 1210119364, 2176035992, 1882851208]);
});

test('levelspec clamps to the last entry', () => {
  assert.equal(levelspec(0).bonusFruit, Fruit.FRUIT_CHERRIES);
  assert.equal(levelspec(0).frightTicks, 360);
  assert.equal(levelspec(999), levelspec(MAX_LEVELSPEC - 1));
});

test('trigger vocabulary', () => {
  state.timing.tick = 100;
  const t = { tick: 0 };
  start(t);
  assert.equal(t.tick, 101);
  startAfter(t, 10);
  assert.equal(t.tick, 110);
  state.timing.tick = 115;
  assert.equal(since(t), 5);
  assert.equal(between(t, 0, 10), true);
  assert.equal(between(t, 6, 10), false);
  disable(t);
  assert.equal(since(t), 0xffffffff);
  assert.equal(between(t, 0, 10), false);
});
```

## headless.test.ts

```ts
// headless.test.ts -- drives the game logic tick by tick without graphics
// or audio output. Translation of the Nim port's tests/headless.nim
// (the tick driver is rules.runTick, the frame loop's tick part).
import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  state,
  newState,
  i2,
  add,
  DISPLAY_TILES_X,
  DISPLAY_TILES_Y,
  TILE_DOT,
  TILE_PILL,
  TILE_SPACE,
  GameState,
  Dir,
  GhostState,
  GhostType,
  FreezeType,
  type Int2,
} from '../src/state.js';
import { start } from '../src/timing.js';
import { pixelToTilePos, dirToVec, isDot, isPill, isBlockingTile } from '../src/geom.js';
import { runTick } from '../src/rules.js';

function resetAll(): void {
  Object.assign(state, newState());
  start(state.intro.started); // what init() does
}

function pressAnyKey(): void {
  state.input.anykey = true;
  runTick();
  state.input.anykey = false;
}

function countDots(): number {
  let n = 0;
  for (let y = 0; y < DISPLAY_TILES_Y; y++) {
    for (let x = 0; x < DISPLAY_TILES_X; x++) {
      const c = state.gfx.videoRam[y]![x]!;
      if (c === TILE_DOT || c === TILE_PILL) n += 1;
    }
  }
  return n;
}

// BFS over non-blocking tiles to the nearest dot/pill; returns first step dir
function steerDir(): Dir {
  const startT = pixelToTilePos(state.game.pacman.actor.pos);
  const visited: boolean[][] = Array.from({ length: DISPLAY_TILES_Y }, () =>
    new Array<boolean>(DISPLAY_TILES_X).fill(false),
  );
  const firstStep: Dir[][] = Array.from({ length: DISPLAY_TILES_Y }, () =>
    new Array<Dir>(DISPLAY_TILES_X).fill(Dir.DIR_RIGHT),
  );
  const queue: Int2[] = [startT];
  let head = 0;
  visited[startT.y]![startT.x] = true;
  const dirs = [Dir.DIR_UP, Dir.DIR_LEFT, Dir.DIR_DOWN, Dir.DIR_RIGHT];
  while (head < queue.length) {
    const cur = queue[head++]!;
    if ((cur.x !== startT.x || cur.y !== startT.y) && (isDot(cur) || isPill(cur))) {
      return firstStep[cur.y]![cur.x]!;
    }
    for (const d of dirs) {
      const n = add(cur, dirToVec(d));
      if (
        n.x >= 0 && n.x < DISPLAY_TILES_X &&
        n.y >= 0 && n.y < DISPLAY_TILES_Y &&
        !visited[n.y]![n.x] &&
        !isBlockingTile(n)
      ) {
        visited[n.y]![n.x] = true;
        firstStep[n.y]![n.x] =
          cur.x === startT.x && cur.y === startT.y ? d : firstStep[cur.y]![cur.x]!;
        queue.push(n);
      }
    }
  }
  return state.game.pacman.actor.dir;
}

function setInput(d: Dir): void {
  state.input.up = d === Dir.DIR_UP;
  state.input.down = d === Dir.DIR_DOWN;
  state.input.left = d === Dir.DIR_LEFT;
  state.input.right = d === Dir.DIR_RIGHT;
}

test('headless play: boot, start a game, play autonomously for 60000 ticks', () => {
  resetAll();
  for (let i = 0; i < 100; i++) runTick();
  const bootState: GameState = state.gamestate;
  assert.equal(bootState, GameState.GAMESTATE_INTRO);
  pressAnyKey();
  let sawGame = false;
  let inkyLeftHouse = false;
  let maxGhostsOut = 0;
  for (let i = 0; i < 60000; i++) {
    runTick();
    if (state.gamestate === GameState.GAMESTATE_GAME) {
      if (!sawGame) {
        sawGame = true;
        assert.equal(countDots(), 244, 'playfield must start with 244 dots/pills');
      }
      if (state.game.freeze.size === 0) {
        setInput(steerDir());
      }
      let outCount = 0;
      for (const g of state.game.ghost) {
        if (g.state !== GhostState.GHOSTSTATE_HOUSE) outCount += 1;
      }
      maxGhostsOut = Math.max(maxGhostsOut, outCount);
      if (state.game.ghost[GhostType.GHOSTTYPE_INKY]!.state !== GhostState.GHOSTSTATE_HOUSE) {
        inkyLeftHouse = true;
      }
    }
  }
  assert.ok(sawGame, 'never entered the game scene');
  // the same end state as the Nim and Go ports' identical scenario
  assert.equal(state.game.score, 350);
  assert.equal(state.game.numDotsEaten, 66);
  assert.equal(maxGhostsOut, 4, 'all 4 ghosts must leave the house');
  assert.ok(inkyLeftHouse);
  // all lives lost: death -> game over -> back to the intro
  assert.equal(state.game.numLives, 0);
  assert.equal(state.gamestate, GameState.GAMESTATE_INTRO);
});

test('determinism: same seed and inputs, same outcome', () => {
  const runShort = (): number[] => {
    resetAll();
    for (let i = 0; i < 100; i++) runTick();
    pressAnyKey();
    for (let i = 0; i < 20000; i++) {
      runTick();
      if (state.gamestate === GameState.GAMESTATE_GAME && state.game.freeze.size === 0) {
        setInput(steerDir());
      }
    }
    return [
      state.game.score,
      state.game.numDotsEaten,
      state.game.pacman.actor.pos.x,
      state.game.pacman.actor.pos.y,
      state.game.ghost[0]!.actor.pos.x,
      state.game.ghost[0]!.actor.pos.y,
    ];
  };
  const r1 = runShort();
  const r2 = runShort();
  assert.deepEqual(r1, r2);
});

test('win scenario: eating the last dot wins the round', () => {
  resetAll();
  for (let i = 0; i < 100; i++) runTick();
  pressAnyKey();
  // advance until the round is running
  for (let i = 0; i < 1000; i++) {
    runTick();
    if (
      state.gamestate === GameState.GAMESTATE_GAME &&
      !state.game.freeze.has(FreezeType.FREEZETYPE_READY) &&
      !state.game.freeze.has(FreezeType.FREEZETYPE_PRELUDE)
    ) {
      break;
    }
  }
  // remove all dots except the one at (1,4) and pretend 243 were eaten
  for (let y = 0; y < DISPLAY_TILES_Y; y++) {
    for (let x = 0; x < DISPLAY_TILES_X; x++) {
      const c = state.gfx.videoRam[y]![x]!;
      if (c === TILE_DOT || c === TILE_PILL) {
        state.gfx.videoRam[y]![x] = TILE_SPACE;
      }
    }
  }
  state.gfx.videoRam[4]![1] = TILE_DOT;
  state.game.numDotsEaten = 243;
  // place Pacman just right of the dot, heading left
  state.game.pacman.actor.pos = i2(2 * 8 + 4, 4 * 8 + 4);
  state.game.pacman.actor.dir = Dir.DIR_LEFT;
  setInput(Dir.DIR_LEFT);
  let won = false;
  for (let i = 0; i < 2000; i++) {
    runTick();
    if (state.game.freeze.has(FreezeType.FREEZETYPE_WON)) {
      won = true;
    }
    if (won && state.game.round === 1 && countDots() === 244) {
      break;
    }
  }
  assert.ok(won, 'round was not won');
  assert.equal(state.game.round, 1);
  assert.equal(countDots(), 244);
  assert.equal(state.game.globalDotCounterActive, false);
});
```

## probes.test.ts

```ts
// probes.test.ts -- targeted behavioural probes: speeds, phase timing,
// house dot counters, frightened duration, ghost-eaten scores and event
// timing, all against the C original's rules. Translation of the Nim
// port's tests/audit_probes.nim (17 probes).
import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  state,
  newState,
  i2,
  add,
  ghostStartingPos,
  DISPLAY_TILES_X,
  DISPLAY_TILES_Y,
  DISPLAY_PIXELS_X,
  TILE_DOT,
  TILE_SPACE,
  DISABLED_TICKS,
  GameState,
  Dir,
  GhostState,
  GhostType,
  FreezeType,
  type Int2,
} from '../src/state.js';
import { start, before } from '../src/timing.js';
import {
  pixelToTilePos,
  dirToVec,
  isDot,
  isPill,
  isBlockingTile,
  isTunnel,
} from '../src/geom.js';
import { runTick } from '../src/rules.js';

function resetAll(): void {
  Object.assign(state, newState());
  start(state.intro.started);
}

function pressAnyKey(): void {
  state.input.anykey = true;
  runTick();
  state.input.anykey = false;
}

// BFS over non-blocking tiles to the nearest dot/pill; returns first step dir
function steerDir(): Dir {
  const startT = pixelToTilePos(state.game.pacman.actor.pos);
  const visited: boolean[][] = Array.from({ length: DISPLAY_TILES_Y }, () =>
    new Array<boolean>(DISPLAY_TILES_X).fill(false),
  );
  const firstStep: Dir[][] = Array.from({ length: DISPLAY_TILES_Y }, () =>
    new Array<Dir>(DISPLAY_TILES_X).fill(Dir.DIR_RIGHT),
  );
  const queue: Int2[] = [startT];
  let head = 0;
  visited[startT.y]![startT.x] = true;
  const dirs = [Dir.DIR_UP, Dir.DIR_LEFT, Dir.DIR_DOWN, Dir.DIR_RIGHT];
  while (head < queue.length) {
    const cur = queue[head++]!;
    if ((cur.x !== startT.x || cur.y !== startT.y) && (isDot(cur) || isPill(cur))) {
      return firstStep[cur.y]![cur.x]!;
    }
    for (const d of dirs) {
      const n = add(cur, dirToVec(d));
      if (
        n.x >= 0 && n.x < DISPLAY_TILES_X &&
        n.y >= 0 && n.y < DISPLAY_TILES_Y &&
        !visited[n.y]![n.x] &&
        !isBlockingTile(n)
      ) {
        visited[n.y]![n.x] = true;
        firstStep[n.y]![n.x] =
          cur.x === startT.x && cur.y === startT.y ? d : firstStep[cur.y]![cur.x]!;
        queue.push(n);
      }
    }
  }
  return state.game.pacman.actor.dir;
}

function setInput(d: Dir): void {
  state.input.up = d === Dir.DIR_UP;
  state.input.down = d === Dir.DIR_DOWN;
  state.input.left = d === Dir.DIR_LEFT;
  state.input.right = d === Dir.DIR_RIGHT;
}

function toGameplay(): void {
  resetAll();
  for (let i = 0; i < 100; i++) runTick();
  pressAnyKey();
  for (let i = 0; i < 2000; i++) {
    runTick();
    if (state.gamestate === GameState.GAMESTATE_GAME && state.game.freeze.size === 0) {
      return;
    }
  }
  assert.fail('never reached gameplay');
}

test('event timing: prelude 120, ready->round 130, scatter->chase +420', () => {
  toGameplay();
  const dtReady = state.game.readyStarted.tick - state.game.started.tick;
  const dtRound = state.game.roundStarted.tick - state.game.readyStarted.tick;
  assert.equal(dtReady, 120, 'started->readyStarted');
  assert.equal(dtRound, 130, 'readyStarted->roundStarted');

  // scatter -> chase switch at +420 ticks from round start
  const base = state.game.roundStarted.tick;
  while (state.timing.tick < base + 419) runTick();
  const s419 = state.game.ghost[GhostType.GHOSTTYPE_BLINKY]!.state;
  runTick();
  const s420 = state.game.ghost[GhostType.GHOSTTYPE_BLINKY]!.state;
  assert.equal(s419, GhostState.GHOSTSTATE_SCATTER, 'scatter@419');
  assert.equal(s420, GhostState.GHOSTSTATE_CHASE, 'chase@420');
});

test('pacman speed on a clear corridor: 7/8 px per tick', () => {
  // empty corridor (row 17, wraps through the tunnel)
  toGameplay();
  for (let x = 0; x < DISPLAY_TILES_X; x++) {
    if (state.gfx.videoRam[17]![x] === TILE_DOT) {
      state.gfx.videoRam[17]![x] = TILE_SPACE; // row 17 has dots at tiles 6 and 21
    }
  }
  state.game.pacman.actor.pos = i2(60, 17 * 8 + 4);
  state.game.pacman.actor.dir = Dir.DIR_LEFT;
  setInput(Dir.DIR_LEFT);
  let movedClear = 0;
  let prevX = state.game.pacman.actor.pos.x;
  for (let i = 0; i < 112; i++) {
    runTick();
    const x = state.game.pacman.actor.pos.x;
    let d = prevX - x;
    if (d < -100) d += DISPLAY_PIXELS_X; // wrapped
    movedClear += d;
    prevX = x;
  }
  assert.equal(movedClear, 98, '112 ticks * 7/8');
});

test('pacman speed while eating: about 0.80 px per tick', () => {
  // row 23 left segment, 11 dots
  toGameplay();
  state.game.pacman.actor.pos = i2(12 * 8 + 4, 23 * 8 + 4);
  state.game.pacman.actor.dir = Dir.DIR_LEFT;
  setInput(Dir.DIR_LEFT);
  let ticksEat = 0;
  while (state.game.pacman.actor.pos.x > 12 && ticksEat < 300) {
    runTick();
    ticksEat += 1;
  }
  const ratio = 88 / ticksEat;
  assert.ok(ratio > 0.77 && ratio < 0.83, `ticks for 88px=${ticksEat} ratio=${ratio}`);
});

test('ghost normal speed: 6/7 px per tick', () => {
  // Blinky, scatter/chase, outside tunnel
  toGameplay();
  let gTicks = 0;
  let gMoved = 0;
  let prevPos = i2(
    state.game.ghost[0]!.actor.pos.x,
    state.game.ghost[0]!.actor.pos.y,
  );
  for (let i = 0; i < 3000; i++) {
    runTick();
    const g = state.game.ghost[0]!;
    const d = Math.abs(g.actor.pos.x - prevPos.x) + Math.abs(g.actor.pos.y - prevPos.y);
    if (
      (g.state === GhostState.GHOSTSTATE_SCATTER || g.state === GhostState.GHOSTSTATE_CHASE) &&
      !isTunnel(pixelToTilePos(g.actor.pos)) &&
      state.game.freeze.size === 0
    ) {
      gTicks += 1;
      gMoved += d;
    }
    prevPos = i2(g.actor.pos.x, g.actor.pos.y);
  }
  const gRatio = gMoved / gTicks;
  assert.ok(gRatio > 0.83 && gRatio < 0.88, `ratio=${gRatio} over ${gTicks} ticks`);
});

test('house dot counters: Inky leaves at 30 dots, Clyde at 90 (+pills)', () => {
  toGameplay();
  let inkyAt = -1;
  let clydeAt = -1;
  let pills = 0;
  let lastPillTick = DISABLED_TICKS;
  const lives0 = state.game.numLives;
  while (state.game.numDotsEaten < 120 && state.game.numLives === lives0) {
    runTick();
    if (
      state.game.pillEaten.tick !== DISABLED_TICKS &&
      state.game.pillEaten.tick !== lastPillTick
    ) {
      lastPillTick = state.game.pillEaten.tick;
      pills += 1;
    }
    // pin the two roaming ghosts so Pacman survives long enough; this does
    // not touch the dot-counter mechanism under test
    state.game.ghost[0]!.actor.pos = i2(ghostStartingPos[0]!.x, ghostStartingPos[0]!.y);
    if (state.game.ghost[1]!.state !== GhostState.GHOSTSTATE_HOUSE) {
      state.game.ghost[1]!.actor.pos = i2(ghostStartingPos[1]!.x, ghostStartingPos[1]!.y);
    }
    if (state.game.freeze.size === 0) {
      setInput(steerDir());
    }
    if (inkyAt < 0 && state.game.ghost[GhostType.GHOSTTYPE_INKY]!.state !== GhostState.GHOSTSTATE_HOUSE) {
      inkyAt = state.game.numDotsEaten;
    }
    if (clydeAt < 0 && state.game.ghost[GhostType.GHOSTTYPE_CLYDE]!.state !== GhostState.GHOSTSTATE_HOUSE) {
      clydeAt = state.game.numDotsEaten;
    }
  }
  assert.equal(inkyAt, 30, 'inky leaves at 30 dots');
  if (clydeAt >= 0) {
    // pills raise numDotsEaten but do not advance the house counters
    // (the C pill branch never calls the counter update), so Clyde's
    // exit shifts by the number of pills eaten
    assert.equal(clydeAt, 90 + pills, `clydeAt=${clydeAt} pills=${pills}`);
  }
});

test('global dot counter after a death: Pinky 7, Inky 17, Clyde 32', () => {
  toGameplay();
  // stage a death: put Blinky (chase) onto Pacman's tile
  state.game.ghost[0]!.state = GhostState.GHOSTSTATE_CHASE;
  state.game.ghost[0]!.actor.pos = i2(
    state.game.pacman.actor.pos.x,
    state.game.pacman.actor.pos.y,
  );
  runTick();
  assert.notEqual(state.game.pacmanEaten.tick, DISABLED_TICKS, 'death sets pacmanEaten');
  // start() stores tick+1 while startAfter() stores tick+N, so the stored
  // trigger values differ by 209 even though the delay is 210 ticks (the C
  // code has the same arithmetic)
  const dtDeath = state.game.readyStarted.tick - state.game.pacmanEaten.tick;
  assert.equal(dtDeath, 209, 'death->ready timing');
  // wait for the new round to run, then eat dots and watch the global counter
  for (let i = 0; i < 2000; i++) {
    runTick();
    if (state.game.freeze.size === 0 && state.game.globalDotCounterActive) {
      break;
    }
  }
  let gPinky = -1;
  let gInky = -1;
  let gClyde = -1;
  let guard = 0;
  while (gClyde < 0 && guard < 30000) {
    runTick();
    guard += 1;
    if (state.game.freeze.size === 0) {
      setInput(steerDir());
    }
    if (gPinky < 0 && state.game.ghost[GhostType.GHOSTTYPE_PINKY]!.state !== GhostState.GHOSTSTATE_HOUSE) {
      gPinky = state.game.globalDotCounter;
    }
    if (gInky < 0 && state.game.ghost[GhostType.GHOSTTYPE_INKY]!.state !== GhostState.GHOSTSTATE_HOUSE) {
      gInky = state.game.globalDotCounter;
    }
    if (gClyde < 0 && state.game.ghost[GhostType.GHOSTTYPE_CLYDE]!.state !== GhostState.GHOSTSTATE_HOUSE) {
      gClyde = state.game.globalDotCounter;
    }
  }
  assert.equal(gPinky, 7, 'global pinky@7');
  assert.equal(gInky, 17, 'global inky@17');
  assert.equal(gClyde, 32, 'global clyde@32');
});

test('frightened duration: 360 ticks on round 1', () => {
  toGameplay();
  state.game.pacman.actor.pos = i2(1 * 8 + 4, 6 * 8 + 4); // on the pill tile
  setInput(Dir.DIR_LEFT);
  let frightStart = -1;
  for (let i = 0; i < 60; i++) {
    runTick();
    if (state.game.ghost[0]!.state === GhostState.GHOSTSTATE_FRIGHTENED) {
      frightStart = state.timing.tick;
      break;
    }
  }
  assert.ok(frightStart > 0, 'pill frightens blinky');
  // park Pacman far away in the bottom right corner area
  state.game.pacman.actor.pos = i2(26 * 8 + 4, 32 * 8 + 4);
  let leftAt = -1;
  for (let i = 0; i < 500; i++) {
    runTick();
    const st = state.game.ghost[0]!.state;
    if (st !== GhostState.GHOSTSTATE_FRIGHTENED) {
      leftAt = state.timing.tick - frightStart;
      break;
    }
  }
  assert.equal(leftAt, 360, 'frightened lasts 360');
});

test('ghost-eaten scores: 20, 40, 80, 160 (10-point units)', () => {
  toGameplay();
  state.game.pacman.actor.pos = i2(1 * 8 + 4, 6 * 8 + 4);
  setInput(Dir.DIR_LEFT);
  for (let i = 0; i < 60; i++) {
    runTick();
    if (
      state.game.ghost[0]!.frightened.tick !== DISABLED_TICKS &&
      before(state.game.ghost[0]!.frightened, 10)
    ) {
      break;
    }
  }
  const deltas: number[] = [];
  for (let gi = 0; gi < 4; gi++) {
    const g = state.game.ghost[gi]!;
    if (g.state === GhostState.GHOSTSTATE_EYES || g.state === GhostState.GHOSTSTATE_ENTERHOUSE) {
      continue;
    }
    g.state = GhostState.GHOSTSTATE_FRIGHTENED;
    start(g.frightened);
    g.actor.pos = i2(state.game.pacman.actor.pos.x, state.game.pacman.actor.pos.y);
    const s0 = state.game.score;
    for (let i = 0; i < 30; i++) {
      runTick();
      if (state.game.freeze.has(FreezeType.FREEZETYPE_EAT_GHOST)) {
        break;
      }
    }
    deltas.push(state.game.score - s0);
    // wait out the eat-ghost freeze
    for (let i = 0; i < 80; i++) {
      runTick();
      if (!state.game.freeze.has(FreezeType.FREEZETYPE_EAT_GHOST)) {
        break;
      }
    }
  }
  assert.deepEqual(deltas, [20, 40, 80, 160]);
});
```

## audio.test.ts

```ts
// audio.test.ts -- Phase 4 checks: the Synth sample generation,
// driven by the real register layer (sound.ts) in Node (SPEC T3).
// The global `state` is shared across the tests in this file; each
// test resets the audio state with sndClear() first and builds a
// fresh Synth, so they can run in file order.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { state, NO_SOUND_FUNC } from '../src/state.js';
import {
  sndClear,
  sndStart,
  sndTick,
  sndPrelude,
  sndEatdot1,
  voiceSnapshot,
} from '../src/sound.js';
import { Synth } from '../src/synth.js';

const SAMPLE_RATE = 44100;
const SAMPLES_PER_TICK = 735; // 44100 / 60, one game tick of samples

test('silence: zeroed registers render all-zero samples', () => {
  sndClear();
  const synth = new Synth(SAMPLE_RATE);
  synth.setVoices(voiceSnapshot());
  const out = new Float32Array(SAMPLES_PER_TICK);
  synth.render(out);
  assert.ok(out.every((v) => v === 0));
});

test('prelude: audible, bounded, and the slot stops after the dump', () => {
  sndClear();
  const synth = new Synth(SAMPLE_RATE);
  sndStart(0, sndPrelude);
  let anyNonZero = false;
  let maxAbs = 0;
  for (let t = 0; t < 60; t++) {
    sndTick();
    synth.setVoices(voiceSnapshot());
    const out = new Float32Array(SAMPLES_PER_TICK);
    synth.render(out);
    for (const v of out) {
      if (v !== 0) anyNonZero = true;
      const a = Math.abs(v);
      if (a > maxAbs) maxAbs = a;
    }
  }
  assert.ok(anyNonZero, 'prelude rendered only silence');
  // Bound derived from the original math: one voice's averaged
  // sample is at most (8 * 15) / 128 (waveform value -8, volume 15),
  // the prelude uses 2 voices, and the output scales by
  // 0.333333 * AUDIO_VOLUME (0.5) -- so 0.3125 is the hard ceiling.
  // The actual prelude data peaks at about 0.302 (both voices near
  // full volume in the first tick), so a tighter bound would fail
  // a faithful implementation.
  assert.ok(maxAbs <= 0.3125, `max |sample| was ${maxAbs}`);

  // The dump is 245 ticks (490 values, stride 2). sndTick loads the
  // last entry on tick 245; one further tick sees curTick ===
  // numTicks and stops the slot, zeroing its voices.
  for (let t = 60; t <= 245; t++) {
    sndTick();
  }
  const snap = voiceSnapshot();
  assert.equal(snap[0]!.frequency, 0);
  assert.equal(snap[0]!.volume, 0);
  assert.equal(snap[1]!.frequency, 0);
  assert.equal(snap[1]!.volume, 0);
});

test('eatdot1: the sound stops itself after 6 ticks', () => {
  sndClear();
  sndStart(2, sndEatdot1);
  for (let t = 0; t < 6; t++) {
    sndTick();
  }
  const snd = state.audio.sound[2]!;
  assert.equal(snd.fn, NO_SOUND_FUNC);
  assert.equal(snd.flags.size, 0);
});

test('determinism: two identical prelude runs are byte-identical', () => {
  const run = (): Float32Array => {
    sndClear();
    const synth = new Synth(SAMPLE_RATE);
    sndStart(0, sndPrelude);
    const all = new Float32Array(60 * SAMPLES_PER_TICK);
    for (let t = 0; t < 60; t++) {
      sndTick();
      synth.setVoices(voiceSnapshot());
      const chunk = new Float32Array(SAMPLES_PER_TICK);
      synth.render(chunk);
      all.set(chunk, t * SAMPLES_PER_TICK);
    }
    return all;
  };
  const a = run();
  const b = run();
  const aBytes = Buffer.from(a.buffer, a.byteOffset, a.byteLength);
  const bBytes = Buffer.from(b.buffer, b.byteOffset, b.byteLength);
  assert.ok(aBytes.equals(bBytes));
});
```

## input.test.ts

```ts
// input.test.ts -- touch swipe resolution (SPEC T8, following the
// Go port's H8 design). Only the DOM-free parts are tested here:
// the swipe direction function and the held/latch resolution.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { state, Dir } from '../src/state.js';
import {
  swipeDirection,
  resolveDirections,
  TOUCH_SWIPE_THRESHOLD,
  attachInput,
} from '../src/input.js';
import { inputDisable, inputEnable, inputDir } from '../src/timing.js';

test('swipe threshold is 24 logical pixels', () => {
  assert.equal(TOUCH_SWIPE_THRESHOLD, 24);
  assert.equal(swipeDirection(23, 0), null);
  assert.equal(swipeDirection(0, 0), null);
  assert.equal(swipeDirection(24, 0), Dir.DIR_RIGHT);
});

test('swipe direction: larger axis wins, tie goes vertical', () => {
  assert.equal(swipeDirection(30, 10), Dir.DIR_RIGHT);
  assert.equal(swipeDirection(-30, 10), Dir.DIR_LEFT);
  assert.equal(swipeDirection(10, 30), Dir.DIR_DOWN);
  assert.equal(swipeDirection(10, -30), Dir.DIR_UP);
  assert.equal(swipeDirection(24, 24), Dir.DIR_DOWN);
  assert.equal(swipeDirection(-24, -24), Dir.DIR_UP);
});

test('resolution: held keyboard directions win over the latch', () => {
  const kb = { up: false, down: false, left: true, right: false };
  const r = resolveDirections(kb, Dir.DIR_UP);
  assert.deepEqual(r, { up: false, down: false, left: true, right: false });
});

test('resolution: latch applies only when nothing is held', () => {
  const none = { up: false, down: false, left: false, right: false };
  assert.deepEqual(resolveDirections(none, Dir.DIR_DOWN), {
    up: false,
    down: true,
    left: false,
    right: false,
  });
  assert.deepEqual(resolveDirections(none, null), none);
});

// Regression (external review): a key released while input is
// disabled must still be forgotten. Otherwise the held mirror in
// input.ts survives inputDisable()'s reset, and the released
// direction resurrects at the next key event -- start the game with
// Up, release it during the dark interval, and the game would steer
// Up forever. The other tests write state.input directly and never
// exercised this path, so this one drives the real listeners
// through a minimal DOM stub.
test('a key released while input is disabled does not stick', () => {
  const listeners = new Map<string, ((e: KeyboardEvent) => void)[]>();
  const g = globalThis as unknown as Record<string, unknown>;
  g.window = {
    addEventListener: (t: string, f: (e: KeyboardEvent) => void) => {
      const arr = listeners.get(t) ?? [];
      arr.push(f);
      listeners.set(t, arr);
    },
  };
  g.HTMLCanvasElement = class {};
  g.document = { getElementById: () => null, fullscreenElement: null };
  attachInput();
  const key = (type: string, code: string): void => {
    for (const f of listeners.get(type) ?? []) {
      f({ code, preventDefault: () => undefined } as KeyboardEvent);
    }
  };

  inputEnable();
  key('keydown', 'ArrowUp'); // start the game with Up
  assert.equal(state.input.up, true);
  inputDisable(); // the intro tick disables input (dark interval)
  key('keyup', 'ArrowUp'); // released while disabled
  inputEnable(); // the game enables input again
  key('keydown', 'ArrowLeft'); // the player now holds only Left
  assert.equal(inputDir(Dir.DIR_RIGHT), Dir.DIR_LEFT, 'must steer Left, not the stuck Up');
  key('keyup', 'ArrowLeft');
  assert.equal(state.input.up, false, 'Up must not be stuck');
});
```

## render.test.ts

```ts
// render.test.ts -- the fade values (gfxFade). The original computes
// in float32, and the port reproduces that rounding with Math.fround;
// these tables are the float32 results for every step, checked
// against the C computation. In float64, six fadein steps would be
// one unit brighter (e.g. step 10: 170 instead of 169).
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { state, newState, DISABLED_TICKS } from '../src/state.js';
import { gfxFade } from '../src/render.js';

const FADEIN: number[] = [
  255, 246, 238, 229, 221, 212, 204, 195, 187, 178, 169, 161, 153, 144, 135,
  127, 118, 110, 101, 93, 84, 76, 67, 59, 50, 42, 33, 25, 16, 8, 0,
];
const FADEOUT: number[] = [
  0, 8, 17, 25, 34, 42, 51, 59, 68, 76, 85, 93, 102, 110, 119, 127, 136, 144,
  153, 161, 170, 178, 187, 195, 204, 212, 221, 229, 238, 246, 255,
];

function fadeAt(which: 'fadein' | 'fadeout', sinceTicks: number): number {
  Object.assign(state, newState());
  state.timing.tick = 1000;
  state.gfx.fadein.tick = DISABLED_TICKS;
  state.gfx.fadeout.tick = DISABLED_TICKS;
  state.gfx[which].tick = 1000 - sinceTicks;
  gfxFade();
  return state.gfx.fade;
}

test('fadein values match the float32 computation at every step', () => {
  for (let s = 0; s <= 30; s++) {
    assert.equal(fadeAt('fadein', s), FADEIN[s], `fadein at ${s} ticks`);
  }
});

test('fadeout values match the float32 computation at every step', () => {
  for (let s = 0; s <= 30; s++) {
    assert.equal(fadeAt('fadeout', s), FADEOUT[s], `fadeout at ${s} ticks`);
  }
});
```

## race.test.ts

```ts
// race.test.ts -- the last-life win/death race: on the final life,
// Pacman eats the last dot on the same tick a ghost catches him.
// The original's structure then runs both sequences at once: the win
// freeze starts the next tick, GAME OVER fires at +210, yet the new
// round still begins (win branch) at +241 during the GAME OVER
// display, and the intro returns at +420. Measured on the Nim port
// as well; the values are identical. This test pins the behavior so
// it cannot silently change.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  state,
  newState,
  i2,
  DISPLAY_TILES_X,
  DISPLAY_TILES_Y,
  TILE_DOT,
  TILE_PILL,
  TILE_SPACE,
  GameState,
  Dir,
  GhostState,
  FreezeType,
} from '../src/state.js';
import { start, now } from '../src/timing.js';
import { runTick } from '../src/rules.js';

function resetAll(): void {
  Object.assign(state, newState());
  start(state.intro.started); // what init() does
}

// read through a call so TypeScript does not narrow the scene to a
// single enum member across runTick() calls
function scene(): GameState {
  return state.gamestate;
}

test('last life: last dot and death on the same tick', () => {
  resetAll();
  for (let i = 0; i < 100; i++) runTick();
  state.input.anykey = true;
  runTick();
  state.input.anykey = false;
  // advance until the round is running
  for (let i = 0; i < 1000; i++) {
    runTick();
    if (
      state.gamestate === GameState.GAMESTATE_GAME &&
      !state.game.freeze.has(FreezeType.FREEZETYPE_READY) &&
      !state.game.freeze.has(FreezeType.FREEZETYPE_PRELUDE)
    ) {
      break;
    }
  }
  assert.ok(state.gamestate === GameState.GAMESTATE_GAME, 'round never started');

  // one dot left at (1,4), 243 eaten, no lives left
  for (let y = 0; y < DISPLAY_TILES_Y; y++) {
    for (let x = 0; x < DISPLAY_TILES_X; x++) {
      const c = state.gfx.videoRam[y]![x]!;
      if (c === TILE_DOT || c === TILE_PILL) {
        state.gfx.videoRam[y]![x] = TILE_SPACE;
      }
    }
  }
  state.gfx.videoRam[4]![1] = TILE_DOT;
  state.game.numDotsEaten = 243;
  state.game.numLives = 0;
  // Pacman just right of the dot, heading left; Blinky is pinned
  // onto the dot tile until the eating tick, so the collision lands
  // on the same tick
  state.game.pacman.actor.pos = i2(2 * 8 + 4, 4 * 8 + 4);
  state.game.pacman.actor.dir = Dir.DIR_LEFT;
  state.input.left = true;

  const seen: Record<string, number> = {};
  for (let i = 0; i < 700; i++) {
    if (seen.eat === undefined) {
      const b = state.game.ghost[0]!;
      b.actor.pos = i2(1 * 8 + 4, 4 * 8 + 4);
      b.state = GhostState.GHOSTSTATE_SCATTER;
    }
    runTick();
    const t = state.timing.tick;
    if (seen.eat === undefined && state.game.numDotsEaten === 244) seen.eat = t;
    if (seen.eat !== undefined) {
      if (seen.won === undefined && state.game.freeze.has(FreezeType.FREEZETYPE_WON)) seen.won = t;
      if (seen.over === undefined && now(state.game.gameOver)) seen.over = t;
      if (seen.round === undefined && state.game.round === 1) seen.round = t;
      if (seen.intro === undefined && scene() === GameState.GAMESTATE_INTRO) {
        seen.intro = t;
        break;
      }
    }
  }

  assert.notEqual(seen.eat, undefined, 'the last dot was never eaten');
  assert.equal(seen.won! - seen.eat!, 1, 'win freeze starts the next tick');
  assert.equal(seen.over! - seen.eat!, 210, 'GAME OVER fires at +210');
  assert.equal(seen.round! - seen.eat!, 241, 'the new round begins at +241, during GAME OVER');
  assert.equal(seen.intro! - seen.eat!, 420, 'back to the intro at +420');
  assert.equal(state.game.numLives, 0, 'lives must not go negative');
});
```

# 付録B C ⇔ TypeScript 対応表

原典 pacman.c の区画と関数が、TypeScript 版の
どこに対応するかの早見表です。行番号は、
原典は floooh/pacman.c（HEAD ccfc0e84）、
TypeScript 版は凍結コピーのものです。

## モジュールの対応

| pacman.c の区画 | TypeScript のファイル |
|---|---|
| 定数・列挙型・構造体・状態 | state.ts |
| 時間、トリガー、乱数、入力の土台 | timing.ts |
| 幾何（座標、判定、移動） | geom.ts |
| ゴーストの思考 | ghost.ts |
| ルール、ティック、初期化 | rules.ts |
| 描画（vid/spr、図形の解読） | render.ts（状態層） |
| 描画の実装（シェーダー相当） | render.ts（Canvas 層） |
| 音の手続きとレジスタ | sound.ts |
| 音の合成（コールバック相当） | synth.ts + worklet.ts |
| 入力のコールバック | input.ts |
| 入り口と主ループ | main.ts + index.html |
| ROM データ（3389〜4303行） | romdata.ts（生成） |

## 関数の対応（抜粋）

| pacman.c | TypeScript | 場所 |
|---|---|---|
| xorshift32 | xorshift32 | timing.ts 15 |
| start / start_after / disable | start / startAfter / disable | timing.ts 25 / 30 / 35 |
| now / since / between | now / since / between | timing.ts 45 / 50 / 58 |
| after_once / after / before | afterOnce / after / before | timing.ts 68 / 73 / 82 |
| input_disable / input_enable | inputDisable / inputEnable | timing.ts 91 / 96 |
| input_dir | inputDir | timing.ts 101 |
| dist_to_tile_mid | distToTileMid | geom.ts 28 |
| clamped_tile_pos | clampedTilePos | geom.ts 40 |
| is_redzone | isRedzone | geom.ts 106 |
| can_move / move | canMove / move | geom.ts 111 / 130 |
| ghost_speed | ghostSpeed | ghost.ts 40 |
| ghost_scatter_chase_phase 相当 | scatterChasePhase | ghost.ts 60 |
| update_ghost_state | updateGhostState | ghost.ts 73 |
| update_ghost_target | updateGhostTarget | ghost.ts 143 |
| update_ghost_dir | updateGhostDir | ghost.ts 197 |
| update_ghosthouse_dot_counters | updateGhosthouseDotCounters | ghost.ts 274 |
| game_init / game_round_init | gameInit / gameRoundInit | rules.ts 175 / 222 |
| game_update_dots_eaten | gameUpdateDotsEaten | rules.ts 283 |
| game_update_actors | gameUpdateActors | rules.ts 300 |
| game_tick / intro_tick | gameTick / introTick | rules.ts 391 / 456 |
| frame のティック部 | runTick | rules.ts 531 |
| vid_* / spr_* | vid* / spr* | render.ts 61〜 |
| game_update_tiles / _sprites | gameUpdateTiles / gameUpdateSprites | render.ts 290 / 337 |
| gfx_decode_tile / _sprite | gfxDecodeTile / gfxDecodeSprite | render.ts 431 / 437 |
| gfx_fade | gfxFade | render.ts 499 |
| gfx_draw 相当 | drawFrame | render.ts 640 |
| snd_start / snd_stop / snd_clear | sndStart / sndStop / sndClear | sound.ts 42 / 31 / 21 |
| snd_tick | sndTick | sound.ts 192 |
| voice_tick 相当 | Synth（合成） | synth.ts 25〜 |
| sokol_main / frame | init / frame | main.ts 142 / 93 |

## 置き換えの対応

| 原典の仕掛け | TypeScript での置き換え | 章 |
|---|---|---|
| 構造体のゼロ初期化 | factory 関数（newState など） | 第2章 |
| 音の関数ポインタ | 数値 ID（SoundFuncId）と配列 | 第2章 |
| freeze のビットフィールド | Set<FreezeType> | 第6章 |
| uint32 の桁あふれ | \|0、>>>0、Math.imul の規律 | 第3章 |
| uint8_t の桁あふれ | & 0xff | 第6章 |
| パレットシェーダー | 色を焼いた画像（事前画像化） | 第9章 |
| 音声コールバック | AudioWorklet + スナップショット | 第10章 |
| キー入力のコールバック | イベント + kb 控え + pollInput | 第11章 |

# 付録C 検証の記録

題材の TypeScript 版について、こちらで
行った検証の記録です。「こちらの環境で
確かめたこと」と「手元での確認待ち」を
分けて書きます。

## こちらの環境で確かめたこと

- tsc のビルドがエラーなしで通る
- Node のテスト全27件が合格する
  （基礎、ヘッドレス、プローブ17件、
  音響、入力5件、描画、レース1件）
- ヘッドレス自動プレイ 60,000 ティックで、
  スコア 350、ドット 66。Nim 版・Go 版の
  実測と一致
- 決定性: 同じ種と入力で、結果が完全一致
- 勝利のシナリオ: 最後のドットで面クリア
- 乱数の列: 種 0x12345678 からの最初の
  5値が C の意味論と一致
- 同着レース: 最終面で、食べたティック
  に対し面クリア +1、ゲームオーバー
  +210、ラウンド初期化 +241、イントロ
  帰還 +420、ライフ 0 のまま
- フェード: 全31段（イン・アウトとも）が
  float32 計算の原典の値と一致
- 音の合成: 手続き関数の数値が原典の
  計算と一致（劇中曲のピーク実測 0.30208、
  2ボイスの理論上限 0.3125 の範囲内）
- ROM データ: 生成のたびに個数と合計値を
  照合し、再生成がバイト単位で同一
- 速度の実測（この VM、Node）: ロジック
  0.63 マイクロ秒/ティック、音の合成は
  実時間の約366倍

## レビューで直したこと

- 小さい指摘5件（フェードの丸め、自己
  停止した音の curTick の加算先、タップ
  の持続、touchcancel の扱い、共有表の
  凍結）
- 入力のバグ: 無効中に離したキーが控えに
  残る問題（forgetKey で修正、回帰テスト
  を追加）
- 画面: 固定サイズから整数倍スケーリング
  へ
- 音: タブを隠したら suspend、開始の
  resume を同期的に、再試行つきに。
  再開条件を interrupted にも拡大し、
  モジュール読み込みの失敗時は次の
  操作で再試行

## 手元での確認待ち

- 実ブラウザでの画面と音、AudioWorklet
  の読み込み
- 実機でのタッチの操作感、iOS での
  音の開始と割り込み
- 他の Node の版でのテスト（Node 22 で
  全件合格の報告あり。こちらは 24 系）
