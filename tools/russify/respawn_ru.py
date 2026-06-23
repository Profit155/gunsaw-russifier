# -*- coding: utf-8 -*-
"""Cyrillic for respawn-pro (dafont, PD/GPL/OFL).
Grid: W=877, caps H=1462, x-height 877, stroke S=292, chamfer 146.
H stems x[0,292],[585,877]; H midbar y[585,877]; cap topbar y[1170,1462]."""
import os
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'fonts', 'originals', 'respawn_pro', 'respawn-pro.ttf')
OUT = os.path.join(ROOT, 'fonts', 'ru', 'RespawnProRu.ttf')

W, H, X, S, C = 877, 1462, 877, 292, 146
MID = 438.5  # glyph horizontal center

c = Composer(SRC)
G, R, P = c.G, c.rect, c.poly
U, cut, clip, mv, mir, vfl, sc = c.union, c.cut, c.clip, c.move, c.hmirror, c.vflip, c.scale

ADV = c.adv('H')  # 1026

# ---------------- capitals ----------------
for ch, src in [('А','A'),('В','B'),('Е','E'),('К','K'),('М','M'),('Н','H'),('О','O'),
                ('Р','P'),('С','C'),('Т','T'),('Х','X'),('У','Y'),('З','three')]:
    c.alias(ch, src)

c.put('И', mir(G('N'), MID), ADV)
c.put('Я', mir(G('R'), MID), ADV)
c.put('Г', clip(G('E'), U(R(0,0,S,H), R(0,H-S,W,H))), ADV)
c.put('П', U(clip(G('H'), R(0,0,S,H)), clip(G('H'), R(W-S,0,W,H)),
             clip(G('E'), R(0,H-S,W,H))), ADV)
# Л: right stem + top bar + slanted left leg with constant horizontal thickness
L_path = U(R(W-S,0,W,H), R(S,H-S,W,H),
           P((0,0),(S,0),(585,H-S+1),(S+1,H-S+1)))
c.put('Л', L_path, ADV)
# Д: П-body on a platform with feet below the baseline
P_body = U(clip(G('H'), R(0,0,S,H)), clip(G('H'), R(W-S,0,W,H)), R(0,H-S,W,H))
c.put('Д', U(P_body, R(0,0,W,S), R(0,-C,C,0), R(W-C,-C,W,0)), ADV)

kdiag = cut(G('K'), R(0,0,S,H))                     # x[292,877]
Zh = U(mir(kdiag, MID), R(585,0,877,H), mv(kdiag, 585))
c.put('Ж', Zh, 1612)
c.put('Ц', U(G('U'), R(W,-C,W+C,S)), ADV+C)
c.put('Ч', cut(G('H'), R(0,0,S,877)), ADV)
c.put('Ш', U(G('U'), mv(G('U'), 585)), 1612)
c.put('Щ', U(G('U'), mv(G('U'), 585), R(1462,-C,1462+C,S)), 1612+C)

Soft = cut(G('B'), R(S,877,W,H))                    # Ь
c.put('Ь', Soft, ADV)
c.put('Б', U(Soft, R(0,H-S,W,H)), ADV)
c.put('Ъ', U(mv(Soft, 219), R(0,H-S,219+S,H)), ADV+219)
c.put('Ы', U(Soft, R(W+C,0,W+C+S,H)), W+C+S+149)
E_rev = U(mir(G('C'), MID), R(219,585,585,877))
c.put('Э', E_rev, ADV)
c.put('Ю', U(R(0,0,S,H), R(S,585,438,877), mv(G('O'), 438)), 438+ADV)
# Ф: wide — centre stem + ring with counters on both sides of the stem
c.put('Ф', U(R(438,0,731,H), cut(R(0,S,1170,H-S),
             U(R(S,585,438,877), R(731,585,877,877)))), 1320)
c.put('Й', U(mir(G('N'), MID), R(C,H+C,731,H+S), R(C,H+S,S,H+S+73), R(585,H+S,731,H+S+73)), ADV)
c.put('Ё', U(G('E'), R(C,H+C,365,H+S+73), R(512,H+C,731,H+S+73)), ADV)
c.put('№', U(G('N'), mv(sc(G('O'), .5, .5), 1023, 731), R(1023,439,1462,585)), 1612+146)

# ---------------- lowercase ----------------
for ch, src in [('а','a'),('е','e'),('о','o'),('р','p'),('с','c'),('у','y'),('х','x'),('п','n')]:
    c.alias(ch, src)

n_l = clip(G('n'), R(0,0,S,X))
n_r = clip(G('n'), R(X-S,0,W,X))
n_bar = clip(G('n'), R(0,X-S,W,X))
c.put('н', U(n_l, n_r, mv(n_bar, 0, -S)), ADV)
c.put('т', U(n_bar, R(S,0,585,X-S)), ADV)
i_diag = P((S,0),(S,438),(585,X),(585,X-438))
c.put('и', U(n_l, n_r, i_diag), ADV)
c.put('й', U(n_l, n_r, i_diag, R(C,X+C,731,X+S), R(C,X+S,S,X+S+73), R(585,X+S,731,X+S+73)), ADV)
c.put('к', sc(G('K'), 1, X/H), ADV)
c.put('л', sc(L_path, 1, X/H), ADV)
c.put('в', sc(G('B'), 1, X/H), ADV)
c.put('м', U(R(0,0,S,X), R(878,0,1170,X),
             P((S,X),(S,X-410),(585,S),(585,S+410)),
             P((1170-S,X),(1170-S,X-410),(585,S),(585,S+410))), 1320)
# б: o-bowl + canonical tail transplanted from Liberation Sans Bold
from outline_lib import b_tail_from
import os as _os
_LIB = _os.path.join(ROOT, 'fonts', 'originals', 'liberation-fonts-ttf-2.1.5', 'LiberationSans-Bold.ttf')
_b, _badv = c.be_with_tail(b_tail_from(_LIB))
c.put('б', _b, _badv)
c.put('д', U(G('n'), R(0,0,W,S), R(0,-C,C,0), R(W-C,-C,W,0)), ADV)
c.put('г', clip(G('n'), U(R(0,0,S,X), R(0,X-S,W,X))), ADV)
c.put('ж', sc(Zh, 1, X/H), 1612)
c.put('з', sc(G('three'), 1, X/H), ADV)
c.put('ц', U(G('u'), R(W,-C,W+C,S)), ADV+C)
c.put('ч', U(R(0,X-438,S,X), R(0,293,W,585), R(X-S,0,W,X)), ADV)
c.put('ш', U(G('u'), mv(G('u'), 585)), 1612)
c.put('щ', U(G('u'), mv(G('u'), 585), R(1462,-C,1462+C,S)), 1612+C)
# ь: full-height bowl reads as 'b'; draw a low bowl with a lighter (219u) stroke
soft_l = U(R(0,0,S,X), cut(R(0,0,731,585), R(S,219,512,366)))
c.put('ь', soft_l, ADV)
c.put('ъ', U(mv(soft_l, 219), R(0,X-C,219+S,X)), ADV+219)
c.put('ы', U(soft_l, R(W+C,0,W+C+S,X)), W+C+S+149)
c.put('э', sc(E_rev, 1, X/H), ADV)
c.put('ю', U(R(0,0,S,X), R(S,293,438,585), mv(G('o'), 438)), 438+ADV)
c.put('я', sc(mir(G('R'), MID), 1, X/H), ADV)
# ф: wide — centre stem + ring with counters on both sides of the stem
c.put('ф', U(R(438,-S,731,X+S), cut(R(0,0,1170,X),
             U(R(S,S,438,585), R(731,S,877,585)))), 1320)
c.put('ё', U(G('e'), R(C,X+C,365,X+S+73), R(512,X+C,731,X+S+73)), ADV)

n = c.save(OUT)
print('saved', OUT, 'mapped:', n)
