# -*- coding: utf-8 -*-
"""Cyrillic for the traced chloe font (game-custom handwriting, rebuilt from the
SDF atlas by chloe_trace.py). Soft marker handwriting: same friendly recipes as
Gelatik — cursive forms и=u, д=g, З/з from B/b sans stem, mirrors keep the hand."""
import os
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'fonts', 'ru', '_chloe_traced.ttf')
OUT = os.path.join(ROOT, 'fonts', 'ru', 'ChloeRu.ttf')

c = Composer(SRC)
G, R, P = c.G, c.rect, c.poly
U, cut, clip, mv, mir, vfl, sc = c.union, c.cut, c.clip, c.move, c.hmirror, c.vflip, c.scale
A = c.adv

def mirc(p):
    b = p.bounds
    return mir(p, (b[0] + b[2]) / 2)

BL = 100  # wobbly hand baseline sits around y=100

# ---------------- capitals ----------------
for ch, src in [('А','A'),('В','B'),('Е','E'),('К','K'),('М','M'),('Н','H'),('О','O'),
                ('Р','P'),('С','C'),('Т','T'),('Х','X'),('У','Y'),('З','3')]:
    c.alias(ch, src)

c.put('И', mirc(G('N')), A('N'))
c.put('Я', mirc(G('R')), A('R'))
Gm = vfl(G('L'), 360)
c.put('Г', Gm, A('L'))
Pp = vfl(G('U'), 370)
c.put('П', Pp, A('U'))
L_p = vfl(G('V'), 370)
c.put('Л', L_p, A('V'))

plat = sc(clip(G('L'), R(40, 90, 300, 250)), 1.5, 1, 170, 0)
foot = G('.')
Dd = U(mv(sc(Pp, 0.85, 0.8, 215, BL), 0, 120), plat,
       mv(foot, -30, -120), mv(foot, 230, -120))
c.put('Д', Dd, A('V'))

kdiag = cut(G('K'), R(0, 80, 160, 700))
Zh = U(mv(mirc(kdiag), -190), mv(G('I'), 130), mv(kdiag, 160))
b = Zh.bounds
Zh = mv(Zh, -b[0] + 50)
c.put('Ж', Zh, int(b[2] - b[0] + 110))

tail = mv(clip(G('I'), R(40, 300, 290, 660)), 250, -290)
c.put('Ц', U(G('U'), tail), A('U') + 70)
c.put('Ч', cut(G('H'), R(0, 80, 160, 350)), A('H'))
Sh = U(G('U'), mv(G('U'), 235))
c.put('Ш', Sh, A('U') + 235)
c.put('Щ', U(Sh, mv(tail, 235, 0)), A('U') + 305)

Soft = cut(G('B'), R(165, 330, 460, 700))
c.put('Ь', Soft, A('B'))
c.put('Б', U(Soft, Gm), A('B'))
c.put('Ъ', U(mv(Soft, 130), clip(G('T'), R(40, 540, 230, 700))), A('B') + 130)
c.put('Ы', U(Soft, mv(G('I'), 380)), A('B') + 290)
hbar = clip(G('H'), R(150, 330, 340, 440))
# Э: bar fitted from the bowl centre to the right wall (a floating cube reads badly)
Cm = mirc(G('C'))
cb = Cm.bounds
cy = (cb[1] + cb[3]) / 2
E_rev = U(Cm, c.fit(clip(G('T'), R(55, 540, 300, 660)),
                    (cb[0] + cb[2]) / 2 - 40, cy - 55, cb[2] - 28, cy + 55))
c.put('Э', E_rev, A('C'))
c.put('Ю', U(G('I'), mv(hbar, -90, 20), mv(G('O'), 230)), A('O') + 230)
# Ф: split squashed O into halves moved apart so the counters clear the stem
Os = sc(G('O'), 1.0, 0.72, 280, 340)
F_cap = U(mv(clip(Os, R(-60, 0, 280, 720)), -55), mv(clip(Os, R(280, 0, 620, 720)), 55),
          mv(sc(G('I'), 1, 1.05), 90, 0))
F_cap = mv(F_cap, -F_cap.bounds[0] + 40)
c.put('Ф', F_cap, A('O') + 150)
brv = mv(sc(G('v'), 0.5, 0.4), 120, 640)
c.put('Й', U(mirc(G('N')), brv), A('N'))
c.put('Ё', U(G('E'), mv(G('.'), 50, 560), mv(G('.'), 180, 560)), A('E'))
c.put('№', U(G('N'), mv(sc(G('o'), 0.55, 0.55), 430, 290), mv(G('.'), 500, 0)), A('N') + 300)

# ---------------- lowercase ----------------
for ch, src in [('а','a'),('е','e'),('о','o'),('р','p'),('с','c'),('у','y'),('х','x'),
                ('и','u'),('д','g')]:
    c.alias(ch, src)

XS, YS = 0.88, 0.79
def low(path):
    return sc(path, XS, YS, 0, BL)

c.put('й', U(G('u'), mv(sc(G('v'), 0.45, 0.4), 110, 480)), A('u'))
c.put('п', vfl(G('u'), 307), A('u'))
c.put('н', low(G('H')), int(A('H') * XS))
c.put('к', low(G('K')), int(A('K') * XS))
c.put('л', vfl(G('v'), 317), A('v'))
c.put('м', low(G('M')), int(A('M') * XS))
c.put('т', low(G('T')), int(A('T') * XS))
c.put('в', low(G('B')), int(A('B') * XS))
c.put('г', low(Gm), int(A('L') * XS))
c.put('ж', low(Zh), int((Zh.bounds[2] + 110) * XS))
c.put('з', low(G('3')), int(A('3') * XS))
c.put('ц', U(G('u'), mv(clip(G('l') if 0x6C in c.cmap else G('I'), R(40, 300, 290, 660)), 260, -290)), A('u') + 70)
c.put('ч', low(cut(G('H'), R(0, 80, 160, 350))), int(A('H') * XS))
sh_l = U(G('u'), mv(G('u'), 280))
c.put('ш', sh_l, A('u') + 280)
c.put('щ', U(sh_l, mv(clip(G('I'), R(40, 300, 290, 660)), 540, -290)), A('u') + 350)
c.put('ь', low(Soft), int(A('B') * XS))
c.put('ъ', low(U(mv(Soft, 130), clip(G('T'), R(40, 540, 230, 700)))), int((A('B') + 130) * XS))
c.put('ы', low(U(Soft, mv(G('I'), 380))), int((A('B') + 290) * XS))
c.put('э', low(E_rev), int(A('C') * XS))
c.put('ю', U(sc(G('I'), 1, 0.79, 0, BL), mv(sc(hbar, 1, 0.79, 0, BL), -90, 10), mv(G('o'), 200)), A('o') + 200)
c.put('я', low(mirc(G('R'))), int(A('R') * XS))
c.put('ф', low(F_cap), int((A('O') + 150) * XS))
# б: o-bowl + canonical tail transplanted from Liberation Sans Bold
from outline_lib import b_tail_from
_b, _badv = c.be_with_tail(b_tail_from(os.path.join(ROOT, 'fonts', 'originals', 'liberation-fonts-ttf-2.1.5', 'LiberationSans-Bold.ttf')))
c.put('б', _b, _badv)
c.put('ё', U(G('e'), mv(G('.'), 40, 480), mv(G('.'), 170, 480)), A('e'))

n = c.save(OUT, family_suffix=' Ru')
print('saved', OUT, 'mapped:', n)
