# -*- coding: utf-8 -*-
"""Cyrillic for Acidic (dafont, PD/GPL/OFL). Bold sans eaten by acid splatter.
upem 940, caps ~0..730, x-height ~0..550. Splatter hides all composition seams."""
import os
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'fonts', 'originals', 'acidic', 'Acidic.TTF')
OUT = os.path.join(ROOT, 'fonts', 'ru', 'AcidicRu.ttf')

c = Composer(SRC)
G, R, P = c.G, c.rect, c.poly
U, cut, clip, mv, mir, vfl, sc = c.union, c.cut, c.clip, c.move, c.hmirror, c.vflip, c.scale
A = c.adv

# ---------------- capitals ----------------
for ch, src in [('А','A'),('В','B'),('Е','E'),('К','K'),('М','M'),('Н','H'),('О','O'),
                ('Р','P'),('С','C'),('Т','T'),('Х','X'),('У','Y'),('З','three')]:
    c.alias(ch, src)

c.put('И', mir(G('N'), 318), A('N'))
c.put('Я', mir(G('R'), 337), A('R'))
Gm = vfl(G('L'), 369)
c.put('Г', Gm, A('L'))
Pp = vfl(G('U'), 372)
c.put('П', Pp, A('U'))
L_p = vfl(G('V'), 362)
c.put('Л', L_p, A('V'))

plat = clip(G('L'), R(-20, -10, 580, 170))
foot = clip(G('I'), R(0, 0, 240, 220))
c.put('Д', U(mv(sc(Pp, 0.84, 0.82, 300, 0), 0, 130), sc(plat, 1.25, 1, 290, 0),
             mv(sc(foot, 0.8, 0.8), -30, -150), mv(sc(foot, 0.8, 0.8), 440, -150)), A('U'))

kdiag = cut(G('K'), R(-20, -40, 180, 770))
c.put('Ж', U(mir(kdiag, 250), mv(G('I'), 290), mv(kdiag, 300)), A('K') + 470)

tail = mv(clip(G('I'), R(0, 0, 240, 240)), 440, -170)
c.put('Ц', U(G('U'), tail), A('U') + 80)
c.put('Ч', cut(G('H'), R(-20, -40, 170, 330)), A('H'))
Sh = U(G('U'), mv(G('U'), 360))
c.put('Ш', Sh, A('U') + 360)
c.put('Щ', U(Sh, mv(tail, 360, 0)), A('U') + 440)

Soft = cut(G('B'), R(170, 360, 720, 810))
c.put('Ь', Soft, A('B'))
c.put('Б', U(Soft, Gm), A('B'))
c.put('Ъ', U(mv(Soft, 160), clip(G('T'), R(-15, 560, 280, 770))), A('B') + 160)
c.put('Ы', U(Soft, mv(G('I'), 470)), A('B') + 280)
hbar = clip(G('H'), R(160, 290, 470, 460))
E_rev = U(mir(G('C'), 326), mv(hbar, 100, 0))
c.put('Э', E_rev, A('C'))
c.put('Ю', U(G('I'), mv(hbar, -80, 0), mv(G('O'), 260)), A('O') + 260)
c.put('Ф', U(sc(G('O'), 1.2, 0.75, 370, 330), mv(sc(G('I'), 1, 1.05), 245, 0)), A('O') + 110)
brv = mv(sc(G('v'), 0.55, 0.4), 160, 770)
c.put('Й', U(mir(G('N'), 318), brv), A('N'))
c.put('Ё', U(G('E'), mv(G('period'), 60, 790), mv(G('period'), 300, 790)), A('E'))
c.put('№', U(G('N'), mv(sc(G('o'), 0.55, 0.55), 640, 300), mv(clip(G('T'), R(-11, 570, 576, 770)), 660, -540)), A('N') + 520)

# ---------------- lowercase ----------------
for ch, src in [('а','a'),('е','e'),('о','o'),('р','p'),('с','c'),('у','y'),('х','x')]:
    c.alias(ch, src)

XS, YS = 0.88, 0.74
def low(path):
    return sc(path, XS, YS)

c.put('и', low(mir(G('N'), 318)), int(A('N') * XS))
c.put('й', low(U(mir(G('N'), 318), brv)), int(A('N') * XS))
c.put('н', low(G('H')), int(A('H') * XS))
c.put('п', low(Pp), int(A('U') * XS))
c.put('т', low(G('T')), int(A('T') * XS))
c.put('к', low(G('K')), int(A('K') * XS))
c.put('л', low(L_p), int(A('V') * XS))
c.put('м', low(G('M')), int(A('M') * XS))
c.put('в', low(G('B')), int(A('B') * XS))
c.put('г', low(Gm), int(A('L') * XS))
c.put('д', low(U(mv(sc(Pp, 0.84, 0.82, 300, 0), 0, 130), sc(plat, 1.25, 1, 290, 0),
                 mv(sc(foot, 0.8, 0.8), -30, -150), mv(sc(foot, 0.8, 0.8), 440, -150))), int(A('U') * XS))
c.put('ж', low(U(mir(kdiag, 250), mv(G('I'), 290), mv(kdiag, 300))), int((A('K') + 470) * XS))
c.put('з', low(G('three')), int(A('three') * XS))
c.put('ц', low(U(G('U'), tail)), int((A('U') + 80) * XS))
c.put('ч', low(cut(G('H'), R(-20, -40, 170, 330))), int(A('H') * XS))
c.put('ш', low(Sh), int((A('U') + 360) * XS))
c.put('щ', low(U(Sh, mv(tail, 360, 0))), int((A('U') + 440) * XS))
c.put('ь', low(Soft), int(A('B') * XS))
c.put('б', U(vfl(G('p'), 167), mv(clip(Gm, R(0, 580, 560, 780)), 30, -210)), A('p'))
c.put('ъ', low(U(mv(Soft, 160), clip(G('T'), R(-15, 560, 280, 770)))), int((A('B') + 160) * XS))
c.put('ы', low(U(Soft, mv(G('I'), 470))), int((A('B') + 280) * XS))
c.put('э', low(E_rev), int(A('C') * XS))
c.put('ю', low(U(G('I'), mv(hbar, -80, 0), mv(G('O'), 260))), int((A('O') + 260) * XS))
c.put('я', low(mir(G('R'), 337)), int(A('R') * XS))
c.put('ф', low(U(sc(G('O'), 1.2, 0.75, 370, 330), mv(sc(G('I'), 1, 1.05), 245, 0))), int((A('O') + 110) * XS))
c.put('ё', U(G('e'), mv(G('period'), 60, 600), mv(G('period'), 280, 600)), A('e'))

n = c.save(OUT)
print('saved', OUT, 'mapped:', n)
