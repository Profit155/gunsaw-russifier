# -*- coding: utf-8 -*-
"""Cyrillic for Hemi Head Bd It (Typodermic freeware; user accepted fan-patch risk).
Italic -12deg: unskew -> compose upright -> reskew, otherwise mirrors/flips
break the slant. upem 1000, caps 0..677, x-height 506."""
import os
import math
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'fonts', 'originals', 'hemi-head', 'hemi head bd it.ttf')
OUT = os.path.join(ROOT, 'fonts', 'ru', 'HemiHeadRu.ttf')

T = math.tan(math.radians(12))   # 0.2126

c = Composer(SRC)
R, P = c.rect, c.poly
U, cut, clip, mv, mir, vfl, sc = c.union, c.cut, c.clip, c.move, c.hmirror, c.vflip, c.scale
A = c.adv

def G(ch):
    """Glyph path in upright (deslanted) space."""
    return c.xform(c.G(ch), 1, 0, -T, 1)

def put(ch, path, adv):
    """Re-slant and install."""
    c.put(ch, c.xform(path, 1, 0, T, 1), adv)

def mirc(p):
    b = p.bounds
    return mir(p, (b[0] + b[2]) / 2)

# ---------------- capitals ----------------
for ch, src in [('А','A'),('В','B'),('Е','E'),('К','K'),('М','M'),('Н','H'),('О','O'),
                ('Р','P'),('С','C'),('Т','T'),('Х','X'),('З','three')]:
    c.alias(ch, src)

# У: scaled-up lowercase y, descender lifted to the baseline
y_up = sc(G('y'), 1.05, 0.9)
y_up = mv(y_up, 0, -y_up.bounds[1])
put('У', y_up, int(A('y') * 1.05))

put('И', mirc(G('N')), A('N'))
put('Я', mirc(G('R')), A('R'))
Gm = vfl(G('L'), 338.5)
put('Г', Gm, A('L'))
Pp = vfl(G('U'), 338.5)
put('П', Pp, A('U'))
L_p = vfl(G('V'), 338.5)
put('Л', L_p, A('V'))

plat = clip(G('L'), R(-60, 0, 700, 160))
foot = clip(G('I'), R(-60, 0, 280, 200))
Dd = U(mv(sc(Pp, 0.84, 0.82, 330, 0), 0, 120), sc(plat, 1.3, 1, 300, 0),
       mv(sc(foot, 0.8, 0.8), -10, -140), mv(sc(foot, 0.8, 0.8), 450, -140))
put('Д', Dd, A('U'))

# Ж: arms must be translated clear of the stem (mirc mirrors in place)
kdiag = cut(G('K'), R(-60, -10, 205, 690))
Zh = U(mv(mirc(kdiag), -165), mv(G('I'), 280), mv(kdiag, 290))
b = Zh.bounds
Zh = mv(Zh, -b[0] + 40)
put('Ж', Zh, int(b[2] - b[0] + 110))

tail = mv(clip(G('I'), R(-60, 0, 280, 220)), 480, -150)
put('Ц', U(G('U'), tail), A('U') + 80)
put('Ч', cut(G('H'), R(-60, -10, 200, 300)), A('H'))
Sh = U(G('U'), mv(G('U'), 380))
put('Ш', Sh, A('U') + 380)
put('Щ', U(Sh, mv(tail, 380, 0)), A('U') + 460)

Soft = cut(G('B'), R(190, 330, 780, 700))
put('Ь', Soft, A('B'))
put('Б', U(Soft, sc(Gm, 1.3, 1, 54, 0)), A('B'))
put('Ъ', U(mv(Soft, 150), clip(G('T'), R(-10, 520, 330, 690))), A('B') + 150)
put('Ы', U(Soft, mv(G('I'), 470)), A('B') + 270)
hbar = clip(G('H'), R(200, 260, 500, 420))
E_rev = U(mirc(G('C')), mv(hbar, 120, 0))
put('Э', E_rev, A('C'))
put('Ю', U(G('I'), mv(hbar, -90, 0), mv(G('O'), 250)), A('O') + 250)
put('Ф', U(sc(G('O'), 1.2, 0.75, 340, 330), mv(sc(G('I'), 1, 1.05), 230, 0)), A('O') + 110)
brv = mv(sc(G('v'), 0.55, 0.4), 150, 720)
put('Й', U(mirc(G('N')), brv), A('N'))
put('Ё', U(G('E'), mv(G('period'), 100, 720), mv(G('period'), 330, 720)), A('E'))
put('№', U(G('N'), mv(sc(G('o'), 0.55, 0.55), 660, 290), mv(clip(G('T'), R(130, 520, 660, 690)), 600, -520)), A('N') + 520)

# ---------------- lowercase ----------------
for ch, src in [('а','a'),('е','e'),('о','o'),('р','p'),('с','c'),('у','y'),('х','x')]:
    c.alias(ch, src)

XS, YS = 0.85, 0.75
def low(path):
    return sc(path, XS, YS)

put('и', low(mirc(G('N'))), int(A('N') * XS))
put('й', low(U(mirc(G('N')), brv)), int(A('N') * XS))
put('н', low(G('H')), int(A('H') * XS))
put('п', low(Pp), int(A('U') * XS))
put('т', low(G('T')), int(A('T') * XS))
put('к', low(G('K')), int(A('K') * XS))
put('л', low(L_p), int(A('V') * XS))
put('м', low(G('M')), int(A('M') * XS))
put('в', low(G('B')), int(A('B') * XS))
put('г', low(Gm), int(A('L') * XS))
put('д', low(Dd), int(A('U') * XS))
put('ж', low(Zh), int((Zh.bounds[2] + 110) * XS))
put('з', low(G('three')), int(A('three') * XS))
put('ц', low(U(G('U'), tail)), int((A('U') + 80) * XS))
put('ч', low(cut(G('H'), R(-60, -10, 200, 300))), int(A('H') * XS))
put('ш', low(Sh), int((A('U') + 380) * XS))
put('щ', low(U(Sh, mv(tail, 380, 0))), int((A('U') + 460) * XS))
put('ь', low(Soft), int(A('B') * XS))
# б: upright o-bowl + canonical Liberation tail; put() re-slants the result
from outline_lib import b_tail_from
_b, _badv = c.be_with_tail(b_tail_from(os.path.join(ROOT, 'fonts', 'originals', 'liberation-fonts-ttf-2.1.5', 'LiberationSans-Bold.ttf')), o=G('o'))
put('б', _b, _badv)
put('ъ', low(U(mv(Soft, 150), clip(G('T'), R(-10, 520, 330, 690)))), int((A('B') + 150) * XS))
put('ы', low(U(Soft, mv(G('I'), 470))), int((A('B') + 270) * XS))
put('э', low(E_rev), int(A('C') * XS))
put('ю', low(U(G('I'), mv(hbar, -90, 0), mv(G('O'), 250))), int((A('O') + 250) * XS))
put('я', low(mirc(G('R'))), int(A('R') * XS))
put('ф', low(U(sc(G('O'), 1.2, 0.75, 340, 330), mv(sc(G('I'), 1, 1.05), 230, 0))), int((A('O') + 110) * XS))
put('ё', U(G('e'), mv(G('period'), 100, 540), mv(G('period'), 330, 540)), A('e'))

n = c.save(OUT)
print('saved', OUT, 'mapped:', n)
