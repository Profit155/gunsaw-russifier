# -*- coding: utf-8 -*-
"""Cyrillic for Victor (dafont, PD/GPL/OFL). Ultra-condensed distressed woodtype.
OTF/CFF source -> converted to quadratic by outline_lib. upem 1000, caps ~0..670,
x-height ~0..600 (≈90% of caps, so scaled caps keep stroke weight)."""
import os
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'fonts', 'originals', 'victor', 'Victor.otf')
OUT = os.path.join(ROOT, 'fonts', 'ru', 'VictorRu.ttf')

c = Composer(SRC)
G, R, P = c.G, c.rect, c.poly
U, cut, clip, mv, mir, vfl, sc = c.union, c.cut, c.clip, c.move, c.hmirror, c.vflip, c.scale
A = c.adv

# ---------------- capitals ----------------
for ch, src in [('А','A'),('В','B'),('Е','E'),('К','K'),('М','M'),('Н','H'),('О','O'),
                ('Р','P'),('С','C'),('Т','T'),('Х','X'),('З','three')]:
    c.alias(ch, src)

# У: scaled-up lowercase y (true У shape), descender lifted to the baseline
y_up = sc(G('y'), 1.05, 0.88)
y_up = mv(y_up, 0, -y_up.bounds[1])
c.put('У', y_up, int(A('y') * 1.05))

c.put('И', mir(G('N'), 214), A('N'))
c.put('Я', mir(G('R'), 214), A('R'))
Gm = vfl(G('L'), 330)                              # Г from flipped L
c.put('Г', Gm, A('L'))
Pp = vfl(G('U'), 330)                              # П from flipped U
c.put('П', Pp, A('U'))
L_p = vfl(G('V'), 328)                             # Л from flipped V
c.put('Л', L_p, A('V'))

plat = clip(G('L'), R(0, -10, 400, 130))           # L bottom bar
foot = clip(G('I'), R(27, 0, 173, 170))
c.put('Д', U(mv(sc(Pp, 0.82, 0.82, 215, 0), 0, 110), sc(plat, 1.25, 1, 200, 0),
             mv(sc(foot, 0.8, 0.8), -20, -110), mv(sc(foot, 0.8, 0.8), 300, -110)), A('U'))

kdiag = cut(G('K'), R(0, -50, 150, 750))           # K arms
c.put('Ж', U(mir(kdiag, 200), mv(G('I'), 225), mv(kdiag, 250)), A('K') + 400)

tail = mv(clip(G('I'), R(27, 0, 173, 200)), 290, -110)
c.put('Ц', U(G('U'), tail), A('U') + 60)
c.put('Ч', cut(G('H'), R(0, -30, 150, 290)), A('H'))
Sh = U(G('U'), mv(G('U'), 250))
c.put('Ш', Sh, A('U') + 250)
c.put('Щ', U(Sh, mv(tail, 250, 0)), A('U') + 310)

# Ь family: full-height stem + a BIG o-bowl (B's own bowls are too subtle)
stemB = clip(G('B'), R(-10, -20, 135, 700))
bowl = mv(sc(G('o'), 1.05, 0.72, 211, 0), 30, 0)
Soft = U(stemB, bowl)
c.put('Ь', Soft, A('B'))
c.put('Б', U(Soft, sc(Gm, 1.22, 1, 26, 0)), A('B'))
c.put('Ъ', U(mv(Soft, 120), clip(G('T'), R(0, 540, 200, 700))), A('B') + 120)
c.put('Ы', U(Soft, mv(G('I'), 330)), A('B') + 200)
hbar = clip(G('H'), R(130, 250, 300, 410))         # H crossbar piece
E_rev = U(mir(G('C'), 213), mv(hbar, 60, 0))
c.put('Э', E_rev, A('C'))
c.put('Ю', U(G('I'), mv(hbar, -60, 0), mv(G('O'), 180)), A('O') + 180)
# Ф: split squashed O into halves moved apart so the counters clear the stem
Os = sc(G('O'), 1.1, 0.78, 211, 320)
F_cap = U(mv(clip(Os, R(-60, -60, 211, 760)), -80), mv(clip(Os, R(211, -60, 480, 760)), 80),
          mv(sc(G('I'), 1, 1.05), 113, 0))
F_cap = mv(F_cap, -F_cap.bounds[0] + 20)
c.put('Ф', F_cap, A('O') + 160)
brv = mv(sc(G('v'), 0.5, 0.35), 105, 700)
c.put('Й', U(mir(G('N'), 214), brv), A('N'))
c.put('Ё', U(G('E'), mv(G('period'), 60, 700), mv(G('period'), 210, 700)), A('E'))
c.put('№', U(G('N'), mv(sc(G('o'), 0.55, 0.55), 420, 280), mv(clip(G('T'), R(21, 560, 345, 700)), 420, -480)), A('N') + 320)

# ---------------- lowercase ----------------
for ch, src in [('а','a'),('е','e'),('о','o'),('с','c'),('у','y'),('х','x')]:
    c.alias(ch, src)
# р: mirrored q (q has an open counter, the original p is nearly solid)
c.put('р', mir(G('q'), 197), A('q'))

XS, YS = 0.97, 0.89
def low(path):
    return sc(path, XS, YS)

c.put('и', low(mir(G('N'), 214)), int(A('N') * XS))
c.put('й', low(U(mir(G('N'), 214), brv)), int(A('N') * XS))
c.put('н', low(G('H')), int(A('H') * XS))
c.put('п', low(Pp), int(A('U') * XS))
c.put('т', low(G('T')), int(A('T') * XS))
c.put('к', low(G('K')), int(A('K') * XS))
c.put('л', low(L_p), int(A('V') * XS))
c.put('м', low(G('M')), int(A('M') * XS))
c.put('в', low(G('B')), int(A('B') * XS))
c.put('г', low(Gm), int(A('L') * XS))
c.put('д', low(U(mv(sc(Pp, 0.82, 0.82, 215, 0), 0, 110), sc(plat, 1.25, 1, 200, 0),
                 mv(sc(foot, 0.8, 0.8), -20, -110), mv(sc(foot, 0.8, 0.8), 300, -110))), int(A('U') * XS))
c.put('ж', low(U(mir(kdiag, 200), mv(G('I'), 225), mv(kdiag, 250))), int((A('K') + 400) * XS))
c.put('з', low(G('three')), int(A('three') * XS))
c.put('ц', low(U(G('U'), tail)), int((A('U') + 60) * XS))
c.put('ч', low(cut(G('H'), R(0, -30, 150, 290))), int(A('H') * XS))
c.put('ш', low(Sh), int((A('U') + 250) * XS))
c.put('щ', low(U(Sh, mv(tail, 250, 0))), int((A('U') + 310) * XS))
c.put('ь', low(Soft), int(A('B') * XS))
# б: o-bowl + canonical tail transplanted from Liberation Sans Bold (a touch smaller)
from outline_lib import b_tail_from
_b, _badv = c.be_with_tail(b_tail_from(os.path.join(ROOT, 'fonts', 'originals', 'liberation-fonts-ttf-2.1.5', 'LiberationSans-Bold.ttf')))
c.put('б', sc(_b, 0.94, 0.94), int(_badv * 0.94))
c.put('ъ', low(U(mv(Soft, 120), clip(G('T'), R(0, 540, 200, 700)))), int((A('B') + 120) * XS))
c.put('ы', low(U(Soft, mv(G('I'), 330))), int((A('B') + 200) * XS))
c.put('э', low(E_rev), int(A('C') * XS))
c.put('ю', low(U(G('I'), mv(hbar, -60, 0), mv(G('O'), 180))), int((A('O') + 180) * XS))
c.put('я', low(mir(G('R'), 214)), int(A('R') * XS))
c.put('ф', low(F_cap), int((A('O') + 160) * XS))
c.put('ё', U(G('e'), mv(G('period'), 60, 640), mv(G('period'), 210, 640)), A('e'))

n = c.save(OUT)
print('saved', OUT, 'mapped:', n)
