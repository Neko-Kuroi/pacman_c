# 別冊 Python 構文集 ― pacman.py に出てきた構文だけ

これは、教科書『パックマンを書く Python 版』
（ミニ版）の別冊です。本編では文法の説明を
省いたので、題材 pacman.py（581行）に実際に
出てきた Python の構文だけを切り離して、
ここにまとめて解説します。出てこなかった
構文は載せていません。

各項目は、実例（pacman.py の行番号つき）、
意味、C ではどうだったか、の順です。
C に対応物がある項目には、pacman.c の
実物も併記しました（行番号は pacman.c の
ものです）。その場で見比べられます。

---

## 1. 式の書き方

### 1.1 条件式 ― 値を選ぶ if

```python
def since(t): return S.timing.tick-t.tick if S.timing.tick>=t.tick else DISABLED
```
（125行）

`値A if 条件 else 値B` で、条件が成り立てば
値A、だめなら値B という「式」です。文では
なく式なので、`return` の後ろや代入の右辺に
直接書けます。

入れ子にもできます。盤面を作る変換は、
4つの値をこの形で選んでいます（184〜185行）。

```python
            S.gfx.vram[row+3][x]=(DOT if ch=='.' else PILL if ch=='P'
                else EMPTY if ch==' ' else DOOR if ch=='-' else WALL)
```

**C では**: 三項演算子 `条件 ? 値A : 値B` が
同じ役目です。語順が逆で、C は条件が先、
Python は選ばれる値が先に来ます。実物は
ゴーストの速さの関数の中にあります。

```c
            return (state.timing.tick & 1) ? 1 : 2;
```
（pacman.c 1763行。同じ関数の1767行と
1772行にも、同じ形があります）

### 1.2 連鎖比較

```python
def between(t,a,b): return t.tick!=DISABLED and a<=since(t)<b
```
（126行）

`a <= x < b` と、比較を鎖のようにつなげて
書けます。「a 以上で b 未満」の数学の
書き方そのままです。先日の修正で入った
`2<abs(a.x-DOOR_X)<=16`（341行）も同じ形です。

**C では**: `a <= x && x < b` と、x を2回
書いて `&&` でつなぎます。実物は、同じ
between です。

```c
static bool between(trigger_t t, uint32_t begin, uint32_t end) {
    assert(begin < end);
    if (t.tick != DISABLED_TICKS) {
        uint32_t ticks = since(t);
        return (ticks >= begin) && (ticks < end);
    }
```
（pacman.c 879〜885行）

### 1.3 真偽の扱い

```python
    if g.fruit and abs(pm.x-FRUIT_POS[0])<=4 and abs(pm.y-FRUIT_POS[1])<=4:
```
（321行）

`if g.fruit:` は「フルーツが出ているか」の
判定です。Python では、0 でない数や、
空でない並びは「真」として扱えます。
`and` と `or` は短絡評価で、左が決め手に
なれば右は見ません。また `and`／`or` は
真偽ではなく、最後に評価した値そのものを
返す点も、C と違います。

**C では**: 数値の 0／非0 で真偽を表す点は
似ていますが、Python の方が広い種類の値を
そのまま条件に使えます。

### 1.4 // と % ― 割り算の2種類

```python
    q=abs(a)//abs(b); return -q if (a<0)!=(b<0) else q
```
（142行、`cdiv`）

`//` は割り算の商（床割り、つまり小さい方へ
丸める）、`%` は余りです。`/` は小数になる
割り算です。点滅の周期のような計算にも
`//` が使われています（`(S.timing.tick//12)%2`）。

**C では**: 整数同士の `/` が商、`%` が余り
ですが、丸めの向きが違います（C は0方向、
Python の `//` と `%` は床方向）。その違いを
吸収するのが `cdiv` と `cmod` でした
（本編 第6章）。C の `%` の実物は、
4.2 の dist_to_tile_mid（pacman.c 989行）
にあります。

### 1.5 ビット演算と、複合代入

```python
    x^=(x<<13)&0xFFFFFFFF; x^=x>>17; x^=(x<<5)&0xFFFFFFFF
```
（137行、xorshift32）

`<<` と `>>` はビットのずらし、`&`、`|`、`^` は
ビットごとの演算、`>>=` や `^=` のような
`= `の前の演算子は「その演算をして代入」
の複合代入です。得点の計算
`10*(1<<g.num_ghosts_eaten)`（327行）の
`1<<n` は「2の n 乗」です。フラグの立て下げは
`g.freeze|=Freeze.EAT_GHOST`（328行）と
`g.freeze&=~Freeze.READY`（384行）です。

**C では**: ほぼ同じ顔つきで書けます。
このあたりは、両言語で一番似ている部分です。
ただし実物を見比べると、違いが1つあります。

```c
// xorshift random number generator
static uint32_t xorshift32(void) {
    uint32_t x = state.game.xorshift;
    x ^= x<<13;
    x ^= x>>17;
    x ^= x<<5;
    return state.game.xorshift = x;
}
```
（pacman.c 826〜833行）

C には `&0xFFFFFFFF` がありません。
`uint32_t` はあふれると自然に巻き戻りますが、
Python の整数は大きくなる一方なので、
32ビットに切り取る印が要るのです。
フラグの実物も、同じ出来事の場所にあります
（Python の328行の相手です）。

```c
                    state.game.freeze |= FREEZETYPE_EAT_GHOST;
```
（pacman.c 2173行）

### 1.6 None と is

```python
        if want is not None and can_move(pm.x,pm.y,want,True): pm.dir=want
```
（308行）

`None` は「値がない」ことを表す特別な値です。
あるかどうかは `==` ではなく `is`（同じもの
かどうか）で比べるのが作法で、`is not None` と
書きます。音の再生でも `if s is None: return`
（547行）と使われています。

**C では**: `NULL` ポインタに相当します。
C は「指す先がない」、Python は「値そのものが
ない」という違いがあります。

---

## 2. 入れ物と並び

### 2.1 リスト、タプル、辞書、集合

pacman.py の入れ物は4種類です。

- **リスト** `[...]`: 順番のある並びで、後から
  変えられる。`LEVELSPEC` や `FRUIT_RGB`、
  `S.game.ghost` など
- **タプル** `(...)`: 順番のある並びで、
  変えられない。`MAZE`（文字列のタプル）、
  `DIRVEC`、座標の組 `(x, y)` など
- **辞書** `{キー: 値}`: キーで引く表。
  `TEXT_RGB`、`GLOBAL_LIMIT`、文字のキャッシュ
  `self.glyph` など
- **集合** `{...}`: 重複のない集まり。
  壁の位置の集合（433行）など

**C では**: 配列と構造体が中心で、長さは
固定、混ぜられる型も決まっていました。
Python の入れ物は長さが変わり、辞書や
集合のような「引くための入れ物」が
標準であります。座標の組のような小さな
入れ物も、C では専用の構造体を作ります。

```c
// a 2D integer vector (used both for pixel- and tile-coordinates)
typedef struct {
    int16_t x;
    int16_t y;
} int2_t;
```
（pacman.c 327〜331行）

### 2.2 添字とスライス

```python
            for i,f in enumerate(S.game.fruit_history[-7:]):
```
（511行）

`[-7:]` は「後ろから7個分」という切り取り
（スライス）です。負の添字は後ろから数え
ます。スライスは元の並びを変えず、新しい
並びを返します。口の開きの表引き
`[0,1,2,1][(pm.anim//2)%4]` のように、
その場で作ったリストに添字を付ける書き方も
あります。

**C では**: スライスはありません。範囲を
使うには、ループで1つずつ取るか、ポインタと
長さを渡します。

### 2.3 .get ― ないかもしれないキーを引く

```python
            if S.game.global_counter==GLOBAL_LIMIT.get(g.type,-1):
```
（270行）

辞書を `d[キー]` で引くと、キーがないときに
例外（KeyError）で止まります。`d.get(キー,
既定値)` は、ないときに既定値を返します。
`TEXT_RGB.get(col,(255,255,255))`（445行）や
`KEYMAP.get(ev.key)`（568行、既定値は None）
も同じです。

**C では**: 相当する仕掛けはありません。
連想配列自体がないので、表は配列の添字か、
自前の探索で引きます。

### 2.4 内包表記 ― ループを式にする

```python
    vram:list=field(default_factory=lambda:[[EMPTY]*TX for _ in range(TY)])
```
（107行）

`[式 for 変数 in 並び]` は、並びの各要素に
式を適用したリストを作る書き方です。ここでは
「`[EMPTY]*TX`（TX 個の並び）を、TY 回作る」
で2次元の表ができています。

大事なのは、`[EMPTY]*TX` の `*` は「同じ
リストを TX 個」ではなく「要素を TX 個に
複製」だという点と、外側を内包表記で TY 回
作り直しているので、行同士が共有されない
点です。もし `[[EMPTY]*TX]*TY` と書くと、
全部の行が同じリストになり、1行変えると
全部変わります。

集合を作る内包表記もあります（433行）。

```python
        wall={(x,y) for y,l in enumerate(MAZE) for x,ch in enumerate(l) if ch not in ".P "}
```

`for` を重ねて、`if` で絞り込むところまで
1つの式に書けます。

**C では**: 全部ループで書きます。内包表記は
「ループで作る」という手続きを、作られる
ものの形で書く書き方です。C 側の盤面作りは、
文字からタイルへの変換表（配列）を引く
二重ループでした。1.1 で見た Python の
条件式と、見比べてください。

```c
    t['t']=0xF0; t['-']=TILE_DOOR; t['P']=TILE_PILL;
    for (int y = 3, i = 0; y <= 33; y++) {
        for (int x = 0; x < 28; x++, i++) {
            state.gfx.video_ram[y][x] = t[tiles[i] & 127];
```
（pacman.c 1422〜1425行）

### 2.5 複数代入とアンパック

```python
            a.x,a.y=DOOR_X,DOOR_Y; new=GState.ENTERHOUSE
```
（263行）

左辺と右辺に並びを並べると、対応する位置
同士で代入されます。関数の戻り値を受ける
`a.x,a.y=move(...)`（348行）や、
`move_d,perp_d=(my,mx) if dy else (mx,my)`
（154行）も同じです。`for i,ch in enumerate(s)`
（173行）の `i,ch` も、組をほどいて
（アンパック）受けています。

**C では**: 戻り値が複数のときは、構造体で
返すか、ポインタで受け渡します。代入も
1つずつ書きます。

### 2.6 in ― 所属の判定

```python
    if st in (GState.HOUSE,GState.LEAVEHOUSE,GState.FRIGHTENED): return t&1
```
（213行）

`x in 並び` は「x が並びの中にあるか」です。
否定は `not in`（433行の `ch not in ".P "`。
文字列に対しては「部分文字列でないか」に
なります）。

**C では**: `x == A || x == B || x == C` と
書くところです。この場所（ゴーストの速さ）
では、C は switch で状態を分けていました。

```c
static int game_ghost_speed(const ghost_t* ghost) {
    assert(ghost);
    switch (ghost->state) {
        case GHOSTSTATE_HOUSE:
        case GHOSTSTATE_LEAVEHOUSE:
```
（pacman.c 1750〜1754行）

---

## 3. 文と流れ

### 3.1 セミコロンと、1行に並ぶ文

pacman.py は、短い文を `;` でつないで1行に
並べる文体です（たとえば137行）。Python の
文の区切りは本来は改行で、`;` は「同じ行に
もう1文置く」ときの印です。ブロック
（if や for の中身）は、字下げ（インデント）
で表します。波括弧はありません。

**C では**: 文の終わりに `;` が必須で、
ブロックは `{ }` で囲みます。字下げは
見た目のためだけです。Python では字下げ
そのものが文法です。

```c
static void vid_clear(uint8_t tile_code, uint8_t color_code) {
    memset(&state.gfx.video_ram, tile_code, sizeof(state.gfx.video_ram));
    memset(&state.gfx.color_ram, color_code, sizeof(state.gfx.color_ram));
}
```
（pacman.c 993〜996行。波括弧で囲まれた
4行が、Python では字下げだけになります）

### 3.2 for と range と enumerate

```python
    for y in range(TY):
        for x in range(TX): S.gfx.vram[y][x]=EMPTY
```
（180〜181行）

`range(n)` は 0 から n-1 までの数の並びを
表します。`for` は「並びから1つずつ取る」
形が基本で、数え上げも range を取ることで
行います。`enumerate(並び)` は、要素と
番号の組を順に返します（173行）。

**C では**: `for (i = 0; i < n; i++)` が
基本形です。Python の for は、C の
「並びをたどる」用途に寄せた形に
なっています。実物は 2.4 で引用した
`for (int y = 3, i = 0; y <= 33; y++)`
（pacman.c 1423行）で、初期化のところに
2つの変数を並べられる点も、C の for の
特徴です。

### 3.3 1行の if

```python
        if s is None: return
```
（547行）

中身が1文だけのときは、`if 条件: 文` と
同じ行に書けます。pacman.py では、この
形がよく使われています（308行など）。

**C では**: 波括弧を省いた
`if (cond) stmt;` に近い感覚です。

### 3.4 assert と f文字列

```python
    assert g.lives >= 0, f"lives={g.lives}"
```
（368行）

`assert 条件, メッセージ` は、条件が
成り立たなければ例外で止めます。後ろの
`f"..."` は f文字列で、`{}` の中に式を
埋め込むと、その値が文字列になります。

**C では**: assert は同じ役目で、同じ
場所にあります。

```c
        state.game.num_lives--;
    }
    assert(state.game.num_lives >= 0);
```
（pacman.c 1491〜1493行）

文字列への埋め込みは printf の書式
（`%d` など）で、C は置く場所と値を
別々に書きますが、f文字列は値の式を
その場に書きます。

---

## 4. 関数

### 4.1 既定値つきの引数と、キーワード引数

```python
def put_text(x,y,s,color=7):
```
（172行）

`color=7` は引数の既定値で、呼び出しで
省くと 7 になります。呼び出し側では、
`Actor(dir=Dir.LEFT,x=112,y=26*TILE+4)` の
ように、名前を指定して渡すこともできます
（352行）。名前なしで順に渡すのが位置引数
（`pygame.font.Font(None,18)` の2つなど）です。

**C では**: 既定値もキーワード引数も
ありません。全部を順に渡します。

### 4.2 組を返す関数

`move`（157行）や `tile_of`（144行）、
`clamp_tile`（145行）は、座標の組
（タプル）を返します。受ける側は 2.5 の
複数代入でほどきます。戻り値は常に
1つですが、その1つが組なのです。

**C では**: 2つの値を返すには構造体を
返すのが普通で、pacman.c の `int2_t` が
まさにそれでした。

```c
int2_t dist_to_tile_mid(int2_t pos) {
    return i2((TILE_WIDTH/2) - pos.x % TILE_WIDTH, (TILE_HEIGHT/2) - pos.y % TILE_HEIGHT);
}
```
（pacman.c 988〜990行。`i2(...)` は int2_t を
作る小さな関数です。`%` は 1.4 の余りで、
Python の `tile_of` や `dist_mid` の相手に
なります）

### 4.3 docstring ― 説明の文字列

```python
def step_tick(snd):
    """frame の while の中身。描画も入力も知らない (第11章)。"""
```
（415〜416行）

関数やクラスの先頭に置いた文字列は
docstring（説明文字列）です。ただの
コメントと違い、プログラムから読み出す
こともできます。`Renderer`（425行）や
`house_move`（243行）、`ghost_dir`（218行）
にも付いています。

**C では**: コメント `/* */` が説明の
置き場所で、実行時には消えています。

### 4.4 lambda ― 名前のない小さな関数

```python
    vram:list=field(default_factory=lambda:[[EMPTY]*TX for _ in range(TY)])
```
（107行。`field(...)` の中身として）

`lambda: 式` は、その場で作る名前のない
関数です。ここでは「呼ぶたびに新しい表を
作る」という作り方そのものを、値として
渡すために使われています（5.2）。

**C では**: 関数ポインタが近い役目ですが、
「作り方を渡す」という使い方の文化は
Python の方にあります。実物は音の表です。

```c
static const sound_desc_t snd_eatghost = {
    .func = snd_func_eatghost,
    .voice = { false, false, true }
};
```
（pacman.c 660〜663行。関数の名前を表に
登録しておいて、後で呼びます。lambda が
「その場で作る関数」なのに対して、こちらは
「名前のある関数を指す」形です）

---

## 5. クラスと dataclass

### 5.1 dataclass と型注釈

```python
@dataclass
class Trigger: tick:int=DISABLED
```
（66〜67行）

`class` の前に `@dataclass` を付けると、
「データを入れる入れ物」としてのクラスに
なり、初期化の関数（`__init__`）などが
自動で作られます。`tick:int=DISABLED` は
「tick という項目、目印は int、初期値は
DISABLED」という宣言です。

注意として、`int` のような型注釈は
**目印**で、実行時に型を強制しません。
違う型を入れても、その場では止まりません。

**C では**: struct の定義に近く、項目の
型は本物（メモリの形そのもの）です。
Python の注釈は、C の型ほど強い意味を
持ちません。Trigger の相手は、これです。

```c
typedef struct {
    uint32_t tick;
} trigger_t;
```
（pacman.c 323〜325行）

### 5.2 field(default_factory=...) ― 共有されない初期値

```python
    frightened:Trigger=field(default_factory=Trigger)
```
（74行）

初期値に「作りたてのもの」が必要なときは、
値そのものではなく、作る関数を
`default_factory` に渡します。こうすると、
インスタンスごとに新しい Trigger が
作られ、共有されません。リストの初期値
（107行）も同じ理由で、lambda が渡されて
います（4.4）。もし初期値を直接書くと、
全員が同じ1個を共有してしまいます。

**C では**: 構造体の初期化は値のコピー
なので、この問題自体がありません。
Python の「代入は参照」という性質
（本編 第2章）から来る、Python 特有の
作法です。

### 5.3 IntEnum と IntFlag

```python
class GState(IntEnum): CHASE=0;SCATTER=1;FRIGHTENED=2;EYES=3;HOUSE=4;LEAVEHOUSE=5;ENTERHOUSE=6
class Freeze(IntFlag): NONE=0;PRELUDE=1;READY=2;EAT_GHOST=4;DEAD=8;WON=16
```
（26、28行）

`IntEnum` は、数値としても使える列挙型です。
`GState.EYES` のように名前で書きながら、
数値との比較や計算もできます。`IntFlag` は
ビットフラグ用で、`|` で重ねたり `&` で
調べたりできます（328、384行）。

**C では**: enum と、`#define` や enum で
作るビットフラグが相当します。C の enum は
ただの整数の別名ですが、Python の IntEnum は
「型」として区別もされます。実物です。

```c
typedef enum {
    GAMESTATE_INTRO,
    GAMESTATE_GAME,
} gamestate_t;
```
（pacman.c 254〜257行。Scene の相手です）

```c
typedef enum {
    FREEZETYPE_PRELUDE   = (1<<0),  // game prelude is active (with the game start tune playing)
    FREEZETYPE_READY     = (1<<1),  // READY! phase is active (at start of a new game round)
    FREEZETYPE_EAT_GHOST = (1<<2),  // Pacman has eaten a ghost
    FREEZETYPE_DEAD      = (1<<3),  // Pacman was eaten by a ghost
    FREEZETYPE_WON       = (1<<4),  // game round was won by eating all dots
} freezetype_t;
```
（pacman.c 314〜320行。Freeze の相手で、
`(1<<n)` の書き方まで同じです）

### 5.4 普通のクラス、self、__init__

```python
class Renderer:
    """表を読むだけ。ゲームのルールを知らない。"""
    def __init__(self):
        pygame.font.init()
        self.font=pygame.font.Font(None,18); self.glyph={}
```
（424〜428行）

`Renderer` と `Sound` は dataclass では
ない普通のクラスです。メソッド（クラスの中の
関数）の第1引数は `self` で、「その
インスタンス自身」を受け取ります。
`self.font` のように、自分の項目は self 経由で
触ります。`__init__` は、作られたときに
呼ばれる初期化の関数です。

**C では**: 構造体と、その構造体への
ポインタを第1引数に取る関数の組が
相当します。`self` は、そのポインタを
言語の側で決まった書き方にしたものです。

```c
static void start(trigger_t* t) {
    t->tick = state.timing.tick + 1;
}
```
（pacman.c 844〜846行。第1引数の
`trigger_t* t` が self に当たり、
`t->tick` が `self.tick` に当たります）

### 5.5 継承 ― 括弧の中の名前

`class Dir(IntEnum)` の括弧は、「IntEnum を
継いだ（性質を受け継いだ）クラス」という
意味です。pacman.py での継承は、この標準の
型を継ぐ場面だけに現れます。自前のクラス
同士の継承はありません。

**C では**: 継承はありません。構造体の
入れ子（ghost_t の中の actor_t のように）
で組み立てます。Python 版の Ghost の中の
Actor も、同じ入れ子の形でした（本編 第2章）。

```c
typedef struct {
    actor_t actor;
    ghosttype_t type;
```
（pacman.c 341〜343行。ghost_t の冒頭で、
actor_t がそのまま中に入っています）

---

## 6. モジュールと状態

### 6.1 大域の S と、global の話

状態は、モジュール（ファイル）の大域にある
`S`（119行）から触ります。関数の中から
`S.timing.tick+=1`（main の中、576行）の
ように書き換えても、`global` の宣言は
要りません。宣言が要るのは
`S = ...` のように名前そのものを別のものに
付け替えるときだけで、属性（`.` の先）を
書き換えるのは付け替えではないからです。

**C では**: ファイルスコープの変数は、
どこからでもそのまま読み書きできます。
Python は「名前の付け替え」だけを
大域の操作として区別しています。

```c
static void input_enable(void) {
    state.input.enabled = true;
}
```
（pacman.c 923〜925行。大域の state を、
何の宣言もなく直接書き換えています）

### 6.2 import の置き場所

```python
# ===================== 描画 (第16・17章) =====================
import pygame
```
（422〜423行）

`import pygame` は、ファイルの途中、
描画の区画の頭にあります。Python の
モジュールは上から順に実行されるので、
import も「その行に来たら読み込む」文
です。だから、使う区画の近くに置けます。
本編 第1章で見たとおり、ルールの区画より
前には pygame が現れません。

**C では**: `#include` は先頭に集めるのが
普通で、プリプロセッサが先に処理します。
実行の順序とは別の仕組みです。

```c
#include "sokol_app.h"
#include "sokol_gfx.h"
#include "sokol_audio.h"
（中略）
#include <assert.h>
#include <string.h> // memset()
#include <stdlib.h> // abs()
```
（pacman.c 133〜141行）

---

## 7. 例外、非同期、バイト列

### 7.1 try / except ― 失敗しても進む

```python
        try: pygame.mixer.init(44100,-16,1,512); self.ok=True
        except Exception: return
```
（525〜526行）

`try` の中で例外（実行時の失敗）が起きると、
`except` の側に移ります。ここでは、音の
初期化に失敗したら、音なし（`ok=False` の
まま）で進む作りになっています（本編 第11章）。

**C では**: 失敗は戻り値で知るのが普通で、
呼び出しごとに確認します。例外は
「失敗が呼び出しの連鎖を飛び越えて
受け手に届く」仕組みです。

### 7.2 async def と await

```python
async def main():
```
（554行）

`main` は `async def` で定義された
コルーチン（途中で待てる関数）で、
末尾は `asyncio.run(main())`（581行）で
動かします。中にある
`await asyncio.sleep(0)`（577行）は
「ここで一度、主導権を返す」という印です。
ブラウザ（pygbag）で動かすための形でした
（本編 第4章）。

**C では**: `int main(void)` が入り口で、
待つという概念は関数の中にはありません。
sokol が frame を呼ぶ形（コールバック）との
違いが、ここに現れています。

```c
static void frame(void) {

    // run the game at a fixed tick rate regardless of frame rate
    uint32_t frame_time_ns = (uint32_t) (sapp_frame_duration() * 1000000000.0);
```
（pacman.c 744〜748行。frame は自分で
呼ばれるのを待つ側で、Python の main は
自分で回し続ける側です）

### 7.3 array('h') と tobytes ― 音の材料

```python
        a=array('h')
```
（536行）

`array('h')` は、符号つき16ビット整数の
配列です。音の波形をここに貯めて、
`a.tobytes()` でバイト列に変えて、
pygame のミキサーに渡します（543行）。

**C では**: `int16_t` の配列そのものです。
Python では、数値の並びとバイト列は
別のものなので、変換のひと手間が
入ります。

---

## おわりに

このファイルに出てくる構文は、以上です。
眺めてみると、C とほとんど同じ顔のもの
（ビット演算、assert）、C の仕掛けを
別の形にしたもの（条件式、組を返す関数、
self）、Python にしかないもの（内包表記、
スライス、.get、default_factory）に
分かれます。移植のときに言語差として
効いたのは、最後の群でした（本編 第6章の
`cdiv` と `cmod`、第2章の `default_factory`
など）。

本編に戻る: 『パックマンを書く Python 版』
README へ。
