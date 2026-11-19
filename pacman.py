# -*- coding: utf-8 -*-
"""
pacman.py -- 『パックマンを書く』の設計を Python へ移植した実装。
原典 floooh/pacman.c (ccfc0e84) の 8 つの設計判断を踏襲する。
絵と音は自作 (ナムコの ROM データ・原曲は含まない)。
  実行:     pip install pygame-ce && python pacman.py
  ブラウザ: pip install pygbag && pygbag pacman.py
"""
import math, time, asyncio
from array import array
from dataclasses import dataclass, field
from enum import IntEnum, IntFlag

# ===================== 定数 (第2章・第13章) =====================
TILE=8; TX,TY=28,36; PX,PY=TX*TILE,TY*TILE; SCALE=2; W,H=PX*SCALE,PY*SCALE
TICK_NS,TOL_NS,CLAMP_NS=16_666_666,1_000_000,33_333_333; DISABLED=0xFFFFFFFF
NUM_DOTS,NUM_LIVES=244,3
FADE_TICKS,PRELUDE_TICKS,READY_TICKS=30,120,130
EATGHOST_TICKS,PACMAN_EATEN_TICKS,PACMAN_DEATH_TICKS=60,60,150
GAMEOVER_TICKS,ROUNDWON_TICKS,FRUIT_TICKS,FORCE_LEAVE_TICKS=180,240,600,240
DOOR_X,DOOR_Y=112,116; FRUIT_POS=(112,164)

class Dir(IntEnum): RIGHT=0;DOWN=1;LEFT=2;UP=3        # bit0=1 が縦移動
DIRVEC={Dir.RIGHT:(1,0),Dir.DOWN:(0,1),Dir.LEFT:(-1,0),Dir.UP:(0,-1)}
def rev(d): return Dir(int(d)^2)
class GState(IntEnum): CHASE=0;SCATTER=1;FRIGHTENED=2;EYES=3;HOUSE=4;LEAVEHOUSE=5;ENTERHOUSE=6
class Scene(IntEnum): INTRO=0;GAME=1
class Freeze(IntFlag): NONE=0;PRELUDE=1;READY=2;EAT_GHOST=4;DEAD=8;WON=16

BLINKY,PINKY,INKY,CLYDE=0,1,2,3
GHOST_RGB=[(255,0,0),(255,184,255),(0,255,255),(255,184,82)]
GHOST_NAME=[("SHADOW","BLINKY"),("SPEEDY","PINKY"),("BASHFUL","INKY"),("POKEY","CLYDE")]
SCATTER_TARGETS=[(25,0),(2,0),(27,34),(0,34)]
HOME_POS=[(DOOR_X,DOOR_Y),(112,140),(96,140),(128,140)]
DOT_LIMIT=[0,0,30,60]; GLOBAL_LIMIT={PINKY:7,INKY:17,CLYDE:32}
TEXT_RGB={0:(0,0,0),1:(255,0,0),2:(255,184,255),3:(0,255,255),4:(255,184,82),
          5:(255,184,255),7:(255,255,255),9:(255,255,0)}

# ===================== 表 (第15章・第21章) =====================
MAZE=("0UUUUUUUUUUUU45UUUUUUUUUUUU1","L............rl............R",
"L.ebbf.ebbbf.rl.ebbbf.ebbf.R","LPr  l.r   l.rl.r   l.r  lPR",
"L.guuh.guuuh.gh.guuuh.guuh.R","L..........................R",
"L.ebbf.ef.ebbbbbbf.ef.ebbf.R","L.guuh.rl.guuyxuuh.rl.guuh.R",
"L......rl....rl....rl......R","2BBBBf.rzbbf rl ebbwl.eBBBB3",
"     L.rxuuh gh guuyl.R     ","     L.rl          rl.R     ",
"     L.rl mjs--tjn rl.R     ","UUUUUh.gh i      q gh.gUUUUU",
"      .   i      q   .      ","BBBBBf.ef i      q ef.eBBBBB",
"     L.rl okkkkkkp rl.R     ","     L.rl          rl.R     ",
"     L.rl ebbbbbbf rl.R     ","0UUUUh.gh guuyxuuh gh.gUUUU1",
"L............rl............R","L.ebbf.ebbbf.rl.ebbbf.ebbf.R",
"L.guyl.guuuh.gh.guuuh.rxuh.R","LP..rl.......  .......rl..PR",
"6bf.rl.ef.ebbbbbbf.ef.rl.eb8","7uh.gh.rl.guuyxuuh.rl.gh.gu9",
"L......rl....rl....rl......R","L.ebbbbwzbbf.rl.ebbwzbbbbf.R",
"L.guuuuuuuuh.gh.guuuuuuuuh.R","L..........................R",
"2BBBBBBBBBBBBBBBBBBBBBBBBBB3")
EMPTY,DOT,PILL,WALL,DOOR=0,1,2,3,4
FRUIT_RGB=[(0,0,0),(255,0,0),(255,60,90),(255,160,60),(200,40,40),
           (120,220,60),(255,220,0),(255,230,120),(180,220,255)]
LEVELSPEC=[(1,10,360),(2,30,300),(3,50,240),(3,50,180),(4,70,120),(4,70,300),
(5,100,120),(5,100,120),(6,200,60),(6,200,300),(7,300,120),(7,300,60),
(8,500,60),(8,500,180),(8,500,60),(8,500,60),(8,500,1),(8,500,60),
(8,500,1),(8,500,1),(8,500,1)]
def levelspec(r): return LEVELSPEC[min(r,len(LEVELSPEC)-1)]

# ===================== 状態の家 (第7章) =====================
@dataclass
class Trigger: tick:int=DISABLED
@dataclass
class Actor: dir:Dir=Dir.LEFT; x:int=0; y:int=0; anim:int=0
@dataclass
class Ghost:
    type:int; actor:Actor; home:tuple
    next_dir:Dir=Dir.LEFT; target:tuple=(0,0); state:GState=GState.HOUSE
    frightened:Trigger=field(default_factory=Trigger)
    eaten:Trigger=field(default_factory=Trigger)
    dot_counter:int=0; dot_limit:int=0
@dataclass
class Timing: tick:int=0; accum:int=0
@dataclass
class Intro: started:Trigger=field(default_factory=Trigger)
@dataclass
class Game:
    started:Trigger=field(default_factory=Trigger)
    ready_started:Trigger=field(default_factory=Trigger)
    round_started:Trigger=field(default_factory=Trigger)
    round_won:Trigger=field(default_factory=Trigger)
    game_over:Trigger=field(default_factory=Trigger)
    dot_eaten:Trigger=field(default_factory=Trigger)
    pill_eaten:Trigger=field(default_factory=Trigger)
    ghost_eaten:Trigger=field(default_factory=Trigger)
    pacman_eaten:Trigger=field(default_factory=Trigger)
    force_leave:Trigger=field(default_factory=Trigger)
    fruit_active:Trigger=field(default_factory=Trigger)
    freeze:Freeze=Freeze.NONE; xorshift:int=0x12345678
    round:int=0; score:int=0; hiscore:int=0; lives:int=NUM_LIVES
    num_dots:int=0; num_ghosts_eaten:int=0
    global_active:bool=False; global_counter:int=0
    after_death:bool=False; dying:bool=False
    fruit:int=0; fruit_history:list=field(default_factory=list)
    pacman:Actor=field(default_factory=Actor); ghost:list=field(default_factory=list)
@dataclass
class Keys:
    enabled:bool=True; anykey:bool=False
    up:bool=False; down:bool=False; left:bool=False; right:bool=False
@dataclass
class Gfx:
    vram:list=field(default_factory=lambda:[[EMPTY]*TX for _ in range(TY)])
    tram:list=field(default_factory=lambda:[[' ']*TX for _ in range(TY)])
    cram:list=field(default_factory=lambda:[[7]*TX for _ in range(TY)])
    fade:int=255
    fadein:Trigger=field(default_factory=Trigger); fadeout:Trigger=field(default_factory=Trigger)
@dataclass
class State:
    scene:Scene=Scene.INTRO
    timing:Timing=field(default_factory=Timing); intro:Intro=field(default_factory=Intro)
    game:Game=field(default_factory=Game); keys:Keys=field(default_factory=Keys)
    gfx:Gfx=field(default_factory=Gfx)
S=State()

# ===================== 時間の語彙 (第12章) =====================
def start(t): t.tick=S.timing.tick+1
def start_after(t,n): t.tick=S.timing.tick+n
def disable(t): t.tick=DISABLED
def now(t): return t.tick==S.timing.tick
def since(t): return S.timing.tick-t.tick if S.timing.tick>=t.tick else DISABLED
def between(t,a,b): return t.tick!=DISABLED and a<=since(t)<b
def after_once(t,n): return since(t)==n
def after(t,n):
    s=since(t); return s!=DISABLED and s>=n
def before(t,n):
    s=since(t); return s!=DISABLED and s<n
def input_enable(): S.keys.enabled=True
def input_disable():
    k=S.keys; k.enabled=False; k.up=k.down=k.left=k.right=k.anykey=False
def rnd():                                   # xorshift32 (第10章)
    x=S.game.xorshift
    x^=(x<<13)&0xFFFFFFFF; x^=x>>17; x^=(x<<5)&0xFFFFFFFF
    S.game.xorshift=x&0xFFFFFFFF; return S.game.xorshift

# ===================== 幾何 (第22章) =====================
def cdiv(a,b):
    q=abs(a)//abs(b); return -q if (a<0)!=(b<0) else q
def cmod(a,b): return a-b*cdiv(a,b)          # C の % (0 方向へ切り捨て)
def tile_of(x,y): return (cdiv(x,TILE),cdiv(y,TILE))
def clamp_tile(tx,ty): return (max(0,min(TX-1,tx)),max(3,min(TY-3,ty)))
def dist_mid(x,y): return (4-cmod(x,TILE),4-cmod(y,TILE))
def sqdist(a,b): return (b[0]-a[0])**2+(b[1]-a[1])**2
def is_wall(tx,ty):
    tx,ty=clamp_tile(tx,ty); return S.gfx.vram[ty][tx] in (WALL,DOOR)
def is_redzone(p): return p[1] in (14,26) and 11<=p[0]<=16
def is_tunnel(p): return p[1]==17 and (p[0]<=5 or p[0]>=22)
def can_move(x,y,d,cornering):
    dx,dy=DIRVEC[d]; mx,my=dist_mid(x,y)
    move_d,perp_d=(my,mx) if dy else (mx,my)
    tx,ty=tile_of(x,y); blocked=is_wall(tx+dx,ty+dy)
    return not ((not cornering and perp_d!=0) or (blocked and move_d==0))
def move(x,y,d,cornering):
    dx,dy=DIRVEC[d]; x+=dx; y+=dy
    if cornering:
        mx,my=dist_mid(x,y)
        if dx:
            if my<0: y-=1
            elif my>0: y+=1
        elif dy:
            if mx<0: x-=1
            elif mx>0: x+=1
    if x<0: x=PX-1
    elif x>=PX: x=0
    return x,y

# ===================== 表への書き込み (第15章) =====================
def put_text(x,y,s,color=7):
    for i,ch in enumerate(s):
        if 0<=x+i<TX and 0<=y<TY:
            S.gfx.tram[y][x+i]=ch; S.gfx.cram[y][x+i]=color
def clear_screen():
    for y in range(TY):
        for x in range(TX): S.gfx.vram[y][x]=EMPTY; S.gfx.tram[y][x]=' '
def build_playfield():
    for y in range(TY):
        for x in range(TX): S.gfx.vram[y][x]=EMPTY
    for row,line in enumerate(MAZE):
        for x,ch in enumerate(line):
            S.gfx.vram[row+3][x]=(DOT if ch=='.' else PILL if ch=='P'
                else EMPTY if ch==' ' else DOOR if ch=='-' else WALL)

# ===================== ゴーストの思考 (第14・20章) =====================
def scatter_chase_phase():
    t=since(S.game.round_started)
    for end,st in ((420,GState.SCATTER),(1620,GState.CHASE),(2040,GState.SCATTER),
                   (3240,GState.CHASE),(3540,GState.SCATTER),(4740,GState.CHASE),
                   (5040,GState.SCATTER)):
        if t<end: return st
    return GState.CHASE
def ghost_target(g):
    a,st=g.actor,g.state
    if st==GState.SCATTER: pos=SCATTER_TARGETS[g.type]
    elif st==GState.CHASE:
        pm=S.game.pacman; p=tile_of(pm.x,pm.y); d=DIRVEC[pm.dir]
        if g.type==BLINKY: pos=p
        elif g.type==PINKY: pos=(p[0]+4*d[0],p[1]+4*d[1])
        elif g.type==INKY:
            b=tile_of(S.game.ghost[BLINKY].actor.x,S.game.ghost[BLINKY].actor.y)
            q=(p[0]+2*d[0],p[1]+2*d[1])
            pos=(b[0]+2*(q[0]-b[0]),b[1]+2*(q[1]-b[1]))
        else: pos=p if sqdist(tile_of(a.x,a.y),p)>64 else SCATTER_TARGETS[CLYDE]
    elif st==GState.FRIGHTENED: pos=(rnd()%TX,rnd()%TY)
    elif st==GState.EYES: pos=(13,14)
    else: pos=g.target
    g.target=pos
def ghost_speed(g):
    t,st=S.timing.tick,g.state
    if st in (GState.HOUSE,GState.LEAVEHOUSE,GState.FRIGHTENED): return t&1
    if st in (GState.EYES,GState.ENTERHOUSE): return 1 if (t&1) else 2
    if is_tunnel(tile_of(g.actor.x,g.actor.y)): return 1 if ((t*2)%4) else 0
    return 1 if (t%7) else 0
def ghost_dir(g):
    """迷路では目標へ貪欲に選ぶ。家の中と出入りは house_move が担当。"""
    a,st=g.actor,g.state
    mx,my=dist_mid(a.x,a.y)
    if mx==0 and my==0:                      # タイルの中央だけで決める
        a.dir=g.next_dir
        dv=DIRVEC[a.dir]; tx,ty=tile_of(a.x,a.y)
        look=(tx+dv[0],ty+dv[1]); best=1<<30
        for d in (Dir.UP,Dir.LEFT,Dir.DOWN,Dir.RIGHT):
            if is_redzone(look) and d==Dir.UP and st!=GState.EYES: continue
            if rev(d)==a.dir: continue
            cx,cy=clamp_tile(look[0]+DIRVEC[d][0],look[1]+DIRVEC[d][1])
            if is_wall(cx,cy): continue
            dd=sqdist((cx,cy),g.target)
            if dd<best: best=dd; g.next_dir=d
        if best==1<<30:                      # FIXME: 原版にない救済 (候補ゼロ時)
            for d in (Dir.UP,Dir.LEFT,Dir.DOWN,Dir.RIGHT):
                cx,cy=clamp_tile(tx+DIRVEC[d][0],ty+DIRVEC[d][1])
                if not is_wall(cx,cy): g.next_dir=d; break
    return False
SEAT=[(112,140),(112,140),(96,140),(128,140)]   # 家の中での復活位置
def approach(v,t,step):
    if v<t: return min(v+step,t)
    if v>t: return max(v-step,t)
    return v
def house_move(g,n):
    """家の中・出入りは強制移動。目標を行き過ぎないように詰める"""
    if n<=0: return
    a=g.actor; hx,hy=g.home
    if g.state==GState.HOUSE:
        if a.y<=hy-3: a.dir=Dir.DOWN
        elif a.y>=hy+3: a.dir=Dir.UP
        a.y+=DIRVEC[a.dir][1]*n
    elif g.state==GState.ENTERHOUSE:
        if a.y<hy: a.dir=Dir.DOWN; a.y=min(a.y+n,hy)
        elif a.x!=hx:
            a.dir=Dir.LEFT if a.x>hx else Dir.RIGHT; a.x=approach(a.x,hx,n)
    else:  # LEAVEHOUSE
        if a.x!=DOOR_X:
            a.dir=Dir.LEFT if a.x>DOOR_X else Dir.RIGHT; a.x=approach(a.x,DOOR_X,n)
        elif a.y>DOOR_Y: a.dir=Dir.UP; a.y=max(a.y-n,DOOR_Y)
    a.anim+=n
def ghost_state(g):
    a,new=g.actor,g.state
    if g.state==GState.EYES:
        if abs(a.x-DOOR_X)<=2 and abs(a.y-DOOR_Y)<=2:
            a.x,a.y=DOOR_X,DOOR_Y; new=GState.ENTERHOUSE
    elif g.state==GState.ENTERHOUSE:
        if a.y>=g.home[1] and a.x==g.home[0]: new=GState.LEAVEHOUSE
    elif g.state==GState.HOUSE:
        if after_once(S.game.force_leave,FORCE_LEAVE_TICKS):
            new=GState.LEAVEHOUSE; start(S.game.force_leave)
        elif S.game.global_active:
            if S.game.global_counter==GLOBAL_LIMIT.get(g.type,-1):
                new=GState.LEAVEHOUSE
                if g.type==CLYDE: S.game.global_active=False
        elif g.dot_counter==g.dot_limit: new=GState.LEAVEHOUSE
    elif g.state==GState.LEAVEHOUSE:
        if a.x==DOOR_X and a.y<=DOOR_Y: a.y=DOOR_Y; new=GState.SCATTER
    else:
        new=(GState.FRIGHTENED if before(g.frightened,levelspec(S.game.round)[2])
             else scatter_chase_phase())
    if new!=g.state:                         # 変わるときだけ後始末
        old=g.state
        if old==GState.LEAVEHOUSE: g.next_dir=a.dir=Dir.LEFT
        elif old==GState.ENTERHOUSE: disable(g.frightened)
        elif old in (GState.SCATTER,GState.CHASE): g.next_dir=rev(a.dir)
        g.state=new

# ===================== ルール (第19章) =====================
def pacman_should_move():
    if now(S.game.dot_eaten): return False
    if since(S.game.pill_eaten)<3: return False
    return (S.timing.tick%8)!=0
def input_dir():
    k=S.keys
    return Dir.UP if k.up else Dir.LEFT if k.left else Dir.DOWN if k.down else Dir.RIGHT if k.right else None
def house_counters():
    if S.game.global_active: S.game.global_counter+=1; return
    for t in (PINKY,INKY,CLYDE):
        if S.game.ghost[t].state==GState.HOUSE:
            S.game.ghost[t].dot_counter+=1; return
def dots_eaten(snd):
    g=S.game; g.num_dots+=1
    if g.num_dots==NUM_DOTS: start(g.round_won); snd.stop_all()
    elif g.num_dots in (70,170): start(g.fruit_active)
    snd.play("waka1" if g.num_dots&1 else "waka2")
def update_actors(snd):
    g=S.game; pm=g.pacman
    if pacman_should_move():
        want=input_dir()
        if want is not None and can_move(pm.x,pm.y,want,True): pm.dir=want
        if can_move(pm.x,pm.y,pm.dir,True):
            pm.x,pm.y=move(pm.x,pm.y,pm.dir,True); pm.anim+=1
    tp=tile_of(pm.x,pm.y); cell=S.gfx.vram[tp[1]][tp[0]]
    if cell==DOT:
        S.gfx.vram[tp[1]][tp[0]]=EMPTY
        g.score+=1; start(g.dot_eaten); start(g.force_leave)
        dots_eaten(snd); house_counters()
    elif cell==PILL:
        S.gfx.vram[tp[1]][tp[0]]=EMPTY
        g.score+=5; dots_eaten(snd); start(g.pill_eaten); g.num_ghosts_eaten=0
        for gh in g.ghost: start(gh.frightened)
        snd.play("pill")
    if g.fruit and abs(pm.x-FRUIT_POS[0])<=4 and abs(pm.y-FRUIT_POS[1])<=4:
        g.score+=levelspec(g.round)[1]; g.fruit=0; snd.play("fruit")
    for gh in g.ghost:                       # 衝突は「同じタイルか」
        if tile_of(gh.actor.x,gh.actor.y)!=tp: continue
        if gh.state==GState.FRIGHTENED:
            gh.state=GState.EYES; start(gh.eaten); start(g.ghost_eaten)
            g.num_ghosts_eaten+=1; g.score+=10*(1<<g.num_ghosts_eaten)
            g.freeze|=Freeze.EAT_GHOST; snd.play("eatghost")
        elif gh.state in (GState.CHASE,GState.SCATTER):
            snd.stop_all(); start(g.pacman_eaten); g.freeze|=Freeze.DEAD
            g.lives-=1; g.after_death=True; g.dying=False
            delay=PACMAN_EATEN_TICKS+PACMAN_DEATH_TICKS
            if g.lives>0: start_after(g.ready_started,delay)
            else: start_after(g.game_over,delay)
            break                      # 死んだらこのティックの衝突は終わり
    for gh in g.ghost:
        ghost_state(gh); ghost_target(gh)
        n=ghost_speed(gh); a=gh.actor
        if gh.state in (GState.HOUSE,GState.LEAVEHOUSE,GState.ENTERHOUSE):
            house_move(gh,n); continue
        if gh.state==GState.EYES and abs(a.y-DOOR_Y)<=2 and 2<abs(a.x-DOOR_X)<=16:
            a.dir=Dir.LEFT if a.x>DOOR_X else Dir.RIGHT
            a.x=approach(a.x,DOOR_X,n); a.anim+=n; continue
        if n==0: continue          # 動かないティックでは向きを決めない
        ghost_dir(gh)
        for _ in range(n):
            if not can_move(a.x,a.y,a.dir,False): break
            a.x,a.y=move(a.x,a.y,a.dir,False); a.anim+=1
            mx,my=dist_mid(a.x,a.y)
            if mx==0 and my==0: break        # 中心を跨いだら止めて判断させる
def place_actors():
    g=S.game
    g.pacman=Actor(dir=Dir.LEFT,x=112,y=26*TILE+4); g.ghost=[]
    for t in range(4):
        a=Actor(dir=Dir.LEFT if t==BLINKY else Dir.DOWN,x=HOME_POS[t][0],y=HOME_POS[t][1])
        g.ghost.append(Ghost(type=t,actor=a,home=SEAT[t],next_dir=Dir.LEFT,
            dot_limit=DOT_LIMIT[t],state=GState.SCATTER if t==BLINKY else GState.HOUSE))
    g.num_ghosts_eaten=0; g.fruit=0; disable(g.fruit_active); disable(g.force_leave)
def game_init(snd):
    g=S.game
    g.score=0; g.round=0; g.lives=NUM_LIVES; g.num_dots=0
    g.global_active=False; g.global_counter=0; g.after_death=False; g.dying=False
    g.fruit_history=[]; g.freeze=Freeze.PRELUDE
    clear_screen(); build_playfield(); place_actors()
    put_text(9,0,"HIGH SCORE"); put_text(9,14,"PLAYER ONE",5); snd.play("prelude")
def round_init():
    g=S.game
    assert g.lives >= 0, f"lives={g.lives}"
    if g.after_death:
        g.global_active=True; g.global_counter=0; g.after_death=False
    else:
        build_playfield(); g.num_dots=0; g.fruit_history.append(levelspec(g.round)[0]); g.global_active=False
    place_actors(); g.xorshift=0x12345678; input_enable()
    g.freeze=Freeze.READY; g.dying=False
    put_text(9,14,"          ",5); put_text(11,20,"READY!",9); start(g.force_leave)
def game_tick(snd):
    g=S.game
    if now(g.started):
        start(S.gfx.fadein); start_after(g.ready_started,PRELUDE_TICKS); game_init(snd)
    if now(g.ready_started):
        if g.num_dots==NUM_DOTS: g.round+=1; g.after_death=False   # 勝ちを死亡より優先
        round_init(); start_after(g.round_started,READY_TICKS)
    if now(g.round_started):
        g.freeze&=~Freeze.READY; put_text(11,20,"      ",9); snd.play("siren")
    if now(g.fruit_active): g.fruit=levelspec(g.round)[0]
    elif after_once(g.fruit_active,FRUIT_TICKS): g.fruit=0
    if after_once(g.ghost_eaten,EATGHOST_TICKS): g.freeze&=~Freeze.EAT_GHOST
    if after_once(g.pacman_eaten,PACMAN_EATEN_TICKS):
        g.dying=True; snd.play("death")
    if not g.freeze: update_actors(snd)
    if g.score>g.hiscore: g.hiscore=g.score
    if now(g.round_won): g.freeze|=Freeze.WON; start_after(g.ready_started,ROUNDWON_TICKS)
    if now(g.game_over):
        put_text(9,20,"GAME  OVER",1); input_disable()
        start_after(S.gfx.fadeout,GAMEOVER_TICKS)
        start_after(S.intro.started,GAMEOVER_TICKS+FADE_TICKS)
def intro_tick(snd):
    if now(S.intro.started):
        input_enable(); start(S.gfx.fadein); snd.stop_all()
        clear_screen(); put_text(9,0,"HIGH SCORE"); put_text(6,5,"CHARACTER / NICKNAME",7)
    for i,(nick,name) in enumerate(GHOST_NAME):
        if after_once(S.intro.started,40+i*40):
            put_text(9,8+i*3,'"'+nick+'"',i+1); put_text(9,9+i*3,name,i+1)
    if after(S.intro.started,220):
        put_text(4,24,"PRESS ANY KEY TO START!",7 if (S.timing.tick//24)%2 else 0)
        put_text(5,30,"ARROWS / WASD : MOVE",7)
    if S.keys.enabled and S.keys.anykey and after(S.intro.started,40):
        input_disable(); start(S.gfx.fadeout); start_after(S.game.started,FADE_TICKS)
def gfx_fade():
    f=S.gfx
    if between(f.fadein,0,FADE_TICKS): f.fade=int(255*(1-since(f.fadein)/FADE_TICKS))
    if after_once(f.fadein,FADE_TICKS): f.fade=0
    if between(f.fadeout,0,FADE_TICKS): f.fade=int(255*(since(f.fadeout)/FADE_TICKS))
    if after_once(f.fadeout,FADE_TICKS): f.fade=255
def step_tick(snd):
    """frame の while の中身。描画も入力も知らない (第11章)。"""
    if now(S.intro.started): S.scene=Scene.INTRO
    if now(S.game.started): S.scene=Scene.GAME
    if S.scene==Scene.INTRO: intro_tick(snd)
    else: game_tick(snd)

# ===================== 描画 (第16・17章) =====================
import pygame
class Renderer:
    """表を読むだけ。ゲームのルールを知らない。"""
    def __init__(self):
        pygame.font.init()
        self.font=pygame.font.Font(None,18); self.glyph={}
        self.walls=self._walls()
        self.veil=pygame.Surface((W,H),pygame.SRCALPHA)
    def _walls(self):
        s=pygame.Surface((W,H),pygame.SRCALPHA); col=(33,33,255)
        wall={(x,y) for y,l in enumerate(MAZE) for x,ch in enumerate(l) if ch not in ".P "}
        for x,y in wall:
            cx,cy=x*16+8,(y+3)*16+8
            pygame.draw.circle(s,col,(cx,cy),3)
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                if (x+dx,y+dy) in wall: pygame.draw.line(s,col,(cx,cy),(cx+dx*8,cy+dy*8),3)
        for x,y in wall:
            if MAZE[y][x]=='-':
                cx,cy=x*16+8,(y+3)*16+8
                pygame.draw.line(s,(255,184,255),(cx-8,cy),(cx+8,cy),4)
        return s
    def text(self,surf,x,y,txt,col=7):
        rgb=TEXT_RGB.get(col,(255,255,255))
        for i,ch in enumerate(txt):
            if ch==' ': continue
            key=(ch,rgb)
            if key not in self.glyph: self.glyph[key]=self.font.render(ch,True,rgb)
            surf.blit(self.glyph[key],((x+i)*16,(y)*16))
    def num(self,surf,x,y,v):
        t=str(v) if v else "00"; self.text(surf,x-len(t)+1,y,t,7)
    def pac(self,surf,cx,cy,r,d,ang):
        if ang<0.02: pygame.draw.circle(surf,(255,255,0),(cx,cy),r); return
        base={Dir.RIGHT:0,Dir.DOWN:math.pi/2,Dir.LEFT:math.pi,Dir.UP:-math.pi/2}[d]
        pts=[(cx,cy)]
        for i in range(25):
            a=base+ang+(2*math.pi-2*ang)*i/24
            pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
        pygame.draw.polygon(surf,(255,255,0),pts)
    def ghost(self,surf,cx,cy,col,d,fr=False,flash=False,eyes=False):
        r=14
        if not eyes:
            body=(255,255,255) if flash else (33,33,255) if fr else col
            pygame.draw.circle(surf,body,(cx,cy-3),r)
            pygame.draw.rect(surf,body,(cx-r,cy-3,2*r,r+3))
            for ox in (-9,0,9): pygame.draw.circle(surf,body,(cx+ox,cy+10),5)
        if fr and not eyes:
            c=(255,0,0) if flash else (255,255,255)
            for ox in (-6,6): pygame.draw.rect(surf,c,(cx+ox-2,cy-7,4,4))
            pygame.draw.lines(surf,c,False,[(cx-9,cy+5),(cx-5,cy+2),(cx-1,cy+5),
                                            (cx+3,cy+2),(cx+7,cy+5)],2)
        else:
            dx,dy=DIRVEC[d]
            for ox in (-6,6):
                pygame.draw.ellipse(surf,(255,255,255),(cx+ox-4,cy-9,8,11))
                pygame.draw.circle(surf,(33,33,255),(cx+ox+dx*2,cy-4+dy*2),2)
    def fruit(self,surf,cx,cy,k):
        pygame.draw.circle(surf,FRUIT_RGB[k],(cx,cy+2),9)
        pygame.draw.line(surf,(0,180,0),(cx,cy-6),(cx+3,cy-11),2)
    def draw(self,surf):
        surf.fill((0,0,0)); surf.blit(self.walls,(0,0))
        blink=(S.timing.tick//12)%2==0
        for y in range(TY):
            for x in range(TX):
                v=S.gfx.vram[y][x]
                if v==DOT: pygame.draw.rect(surf,(255,184,151),(x*16+6,y*16+6,4,4))
                elif v==PILL and blink: pygame.draw.circle(surf,(255,184,151),(x*16+8,y*16+8),6)
                ch=S.gfx.tram[y][x]
                if ch!=' ': self.text(surf,x,y,ch,S.gfx.cram[y][x])
        self.text(surf,3,0,"1UP",7); self.num(surf,6,1,S.game.score*10)
        self.num(surf,16,1,S.game.hiscore*10)
        if S.scene==Scene.GAME:
            if S.game.fruit: self.fruit(surf,FRUIT_POS[0]*2,FRUIT_POS[1]*2,S.game.fruit)
            for gh in S.game.ghost:
                fr=gh.state==GState.FRIGHTENED
                left=levelspec(S.game.round)[2]-since(gh.frightened)
                flash=fr and left<120 and (S.timing.tick//8)%2==0
                eyes=gh.state in (GState.EYES,GState.ENTERHOUSE)
                self.ghost(surf,gh.actor.x*2,gh.actor.y*2,GHOST_RGB[gh.type],
                           gh.actor.dir,fr,flash,eyes)
            if not (S.game.freeze&Freeze.EAT_GHOST):
                pm=S.game.pacman
                if S.game.dying:
                    k=(since(S.game.pacman_eaten)-PACMAN_EATEN_TICKS)/PACMAN_DEATH_TICKS
                    ang=max(0.0,min(1.0,k))*math.pi
                else: ang=(math.pi/4)*[0,1,2,1][(pm.anim//2)%4]
                self.pac(surf,pm.x*2,pm.y*2,15,pm.dir,ang)
            for i in range(max(0,S.game.lives-1)):
                self.pac(surf,(2+2*i)*16+8,34*16+8,12,Dir.RIGHT,0.6)
            for i,f in enumerate(S.game.fruit_history[-7:]):
                self.fruit(surf,(26-2*i)*16+8,34*16+8,f)
        else:
            for i in range(4):
                if since(S.intro.started)>40+i*40:
                    self.ghost(surf,6*16+8,(8+i*3)*16+8,GHOST_RGB[i],Dir.RIGHT)
        if S.gfx.fade>0:
            self.veil.fill((0,0,0,S.gfx.fade)); surf.blit(self.veil,(0,0))

# ===================== 音 (第18章の簡略版) =====================
class Sound:
    """3声の Namco 音源エミュレーションではなく、自作の矩形波効果音。"""
    def __init__(self):
        self.ok=False; self.snd={}; self.loop=None
        try: pygame.mixer.init(44100,-16,1,512); self.ok=True
        except Exception: return
        self.snd["waka1"]=self._mk([(520,45,-4)]); self.snd["waka2"]=self._mk([(300,45,6)])
        self.snd["pill"]=self._mk([(180,120,3)])
        self.snd["eatghost"]=self._mk([(300,60,9),(900,90,2)])
        self.snd["fruit"]=self._mk([(700,70,3),(1100,90,-2)])
        self.snd["death"]=self._mk([(700,90,-5),(500,90,-5),(320,140,-4)])
        self.snd["siren"]=self._mk([(330,110,2),(400,110,-2)])
        self.snd["prelude"]=self._mk([(392,110,0),(523,110,0),(659,110,0),(784,180,0),
                                      (659,110,0),(784,240,0)])
    def _mk(self,parts):
        a=array('h')
        for f,ms,sw in parts:
            n=int(44100*ms/1000)
            for i in range(n):
                t=i/44100; ph=(t*f*(1+sw*t))%1.0
                v=1.0 if ph<0.5 else -1.0
                a.append(int(v*0.22*32767*min(1.0,(n-i)/700.0)))
        return pygame.mixer.Sound(buffer=a.tobytes())
    def play(self,name):
        if not self.ok: return
        s=self.snd.get(name)
        if s is None: return
        if name=="siren": self.loop=s.play(loops=-1)
        else: s.play()
    def stop_all(self):
        if self.ok: pygame.mixer.stop(); self.loop=None

# ===================== 入り口 (第1・13・26章) =====================
async def main():
    pygame.init()
    screen=pygame.display.set_mode((W,H),pygame.SCALED|pygame.RESIZABLE)
    pygame.display.set_caption("pacman.py")
    snd=Sound(); r=Renderer(); clock=pygame.time.Clock()
    start(S.intro.started)
    prev=time.perf_counter_ns(); running=True
    KEYMAP={pygame.K_UP:"up",pygame.K_w:"up",pygame.K_DOWN:"down",pygame.K_s:"down",
            pygame.K_LEFT:"left",pygame.K_a:"left",pygame.K_RIGHT:"right",pygame.K_d:"right"}
    while running:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            elif ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: running=False
            elif ev.type in (pygame.KEYDOWN,pygame.KEYUP) and S.keys.enabled:
                down=ev.type==pygame.KEYDOWN; name=KEYMAP.get(ev.key)
                if name: setattr(S.keys,name,down)
                if down: S.keys.anykey=True
        ns=time.perf_counter_ns()
        S.timing.accum+=min(ns-prev,CLAMP_NS); prev=ns
        while S.timing.accum>-TOL_NS:            # 固定ティック (第13章)
            S.timing.accum-=TICK_NS; S.timing.tick+=1; step_tick(snd)
        gfx_fade(); r.draw(screen); pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)                   # ブラウザでは主導権を返す (第26章)
    pygame.quit()

if __name__=="__main__":
    asyncio.run(main())
