# -*- coding: utf-8 -*-
"""Cyrillic for Gelatik (dafont, PD/GPL/OFL). Hand-drawn angular marker font.
upem 1000, caps ~750, x-height ~500, hand-wobble baseline (yMin ~ -100..-160).
Hand style is forgiving: mirrors/flips/scales keep the hand-drawn feel, and
cursive letterforms allow и=u, г=r, д=g, э=mirror(e), З=mirror(S)."""
import os
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'fonts', 'originals', 'gelatik', 'Gelatik-Regular.ttf')
OUT = os.path.join(ROOT, 'fonts', 'ru', 'GelatikRu.ttf')

c = Composer(SRC)
G, R, P = c.G, c.rect, c.poly
U, cut, clip, mv, mir, vfl, sc = c.union, c.cut, c.clip, c.move, c.hmirror, c.vflip, c.scale
A = c.adv

# ---------------- capitals ----------------
for ch, src in [('А','A'),('В','B'),('Е','E'),('К','K'),('М','M'),('Н','H'),('О','O'),
                ('Р','P'),('С','C'),('Т','T'),('Х','X'),('У','Y')]:
    c.alias(ch, src)

c.put('И', mir(G('N'), 405), A('N'))
c.put('Я', mir(G('R'), 353), A('R'))
Gm = vfl(G('L'), 305)
c.put('Г', Gm, A('L'))
c.put('П', vfl(G('U'), 300), A('U'))
# З: B without its stem = two right-bulging bowls with a middle pinch
Z_p = cut(G('B'), R(0, -200, 178, 800))
c.put('З', Z_p, A('B'))

# Л: flipped V — a clean hand-drawn Λ, no leftovers from A's crossbar
L_p = vfl(G('V'), 310)
c.put('Л', L_p, A('V'))
# Д: narrowed Л body on the L bottom bar (already on the baseline) + stem feet
plat = sc(clip(G('L'), R(40, -130, 650, 160)), 1.25, 1, 345, 0)
foot = clip(G('l'), R(43, 500, 191, 737))
c.put('Д', U(mv(sc(L_p, 0.85, 0.8, 390, 0), 0, 160), plat,
             mv(foot, -40, -790), mv(foot, 470, -790)), A('V'))

kdiag = cut(G('K'), R(0, -200, 180, 800))
c.put('Ж', U(mir(kdiag, 340), mv(G('I'), 344), mv(kdiag, 330)), 1030)

tail = mv(clip(G('I'), R(42, 400, 171, 737)), 530, -640)
c.put('Ц', U(G('U'), tail), A('U') + 60)
c.put('Ч', cut(G('H'), R(40, -140, 230, 250)), A('H'))
Sh = U(G('U'), mv(G('U'), 450))
c.put('Ш', Sh, A('U') + 450)
c.put('Щ', U(Sh, mv(tail, 440, 0)), A('U') + 500)

Soft = cut(G('B'), R(180, 330, 700, 800))          # B without top bowl
c.put('Ь', Soft, A('B'))
c.put('Б', U(Soft, Gm), A('B'))                    # Ь + Г share the stem
c.put('Ъ', U(mv(Soft, 150), mv(clip(G('T'), R(45, 540, 330, 750)), 0, 0)), A('B') + 150)
c.put('Ы', U(Soft, mv(G('I'), 640)), A('B') + 230)
E_rev = U(mir(G('C'), 415), mv(clip(G('H'), R(220, 230, 560, 420)), 60, 0))
c.put('Э', E_rev, A('C'))
c.put('Ю', U(G('I'), mv(clip(G('H'), R(220, 230, 560, 420)), -60, 0), mv(G('O'), 270)), A('O') + 270)
c.put('Ф', U(sc(G('O'), 0.9, 0.78, 385, 290), G('I') and mv(G('I'), 300)), A('O'))
brv = mv(sc(G('v'), 0.5, 0.45), 230, 850)
c.put('Й', U(mir(G('N'), 405), brv), A('N'))
c.put('Ё', U(G('E'), mv(G('.'), 110, 950), mv(G('.'), 360, 950)), A('E'))
c.put('№', U(G('N'), mv(sc(G('o'), 0.55, 0.55), 800, 280), mv(G('.'), 870, 60)), 1300)

# ---------------- lowercase ----------------
for ch, src in [('а','a'),('е','e'),('о','o'),('р','p'),('с','c'),('у','y'),('х','x'),
                ('и','u'),('д','g')]:
    c.alias(ch, src)
c.put('г', sc(Gm, 0.85, 0.7), int(A('L') * 0.85))   # proper Г shape, not r

XS, YS = 0.82, 0.68   # caps -> x-height scale for hand-drawn forms
c.put('й', U(G('u'), mv(sc(G('v'), 0.45, 0.4), 160, 600)), A('u'))
c.put('п', vfl(G('u'), 187), A('u'))
c.put('н', sc(G('H'), XS, YS), int(A('H') * XS))
c.put('к', sc(G('K'), XS, YS), int(A('K') * XS))
c.put('л', vfl(G('v'), 216), A('v'))               # flipped v
c.put('м', sc(G('M'), XS, YS), int(A('M') * XS))
c.put('т', sc(G('T'), XS, YS), int(A('T') * XS))
c.put('в', sc(G('B'), XS, YS), int(A('B') * XS))
c.put('ж', sc(U(mir(kdiag, 340), mv(G('I'), 344), mv(kdiag, 330)), XS, YS), int(1030 * XS))
c.put('з', sc(Z_p, XS, YS), int(A('B') * XS))
c.put('ч', sc(cut(G('H'), R(40, -140, 230, 250)), XS, YS), int(A('H') * XS))
sh_l = U(G('u'), mv(G('u'), 380))
c.put('ш', sh_l, A('u') + 380)
tail_l = mv(clip(G('l'), R(43, 350, 191, 737)), 500, -560)
c.put('щ', U(sh_l, mv(tail_l, 370, 0)), A('u') + 430)
c.put('ь', sc(Soft, XS, YS), int(A('B') * XS))
c.put('ъ', sc(U(mv(Soft, 150), clip(G('T'), R(45, 540, 330, 750))), XS, YS), int((A('B') + 150) * XS))
c.put('ы', sc(U(Soft, mv(G('I'), 640)), XS, YS), int((A('B') + 230) * XS))
c.put('э', sc(E_rev, XS, YS), int(A('C') * XS))
c.put('ю', U(G('l'), mv(clip(G('H'), R(220, 230, 560, 420)), -150, -120), mv(G('o'), 250)), A('o') + 250)
c.put('я', sc(mir(G('R'), 353), XS, YS), int(A('R') * XS))
c.put('ф', U(G('o'), mv(G('l'), 270, -110)), A('o'))
c.put('ц', U(G('u'), tail_l), A('u') + 60)
# б: bowl + flag tilted ~15° to the right (rotated l-stem piece)
flag = c.xform(clip(G('l'), R(43, 300, 191, 737)), 0.966, -0.259, 0.259, 0.966)
c.put('б', U(G('o'), mv(flag, 290, 60)), A('o'))
c.put('ё', U(G('e'), mv(G('.'), 100, 700), mv(G('.'), 330, 700)), A('e'))

n = c.save(OUT)
print('saved', OUT, 'mapped:', n)
