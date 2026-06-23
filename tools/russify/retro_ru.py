# -*- coding: utf-8 -*-
"""RetroGamingRu: original Retro Gaming (native cyrillic) + composed №.
Dashes/ellipsis are added afterwards by punct_fix.py."""
import os
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'fonts', 'originals', 'retro_gaming', 'Retro Gaming.ttf')
OUT = os.path.join(ROOT, 'fonts', 'ru', 'RetroGamingRu.ttf')

c = Composer(SRC)
N = c.G('N')
nb = N.bounds
o = c.G('o')
ob = o.bounds
nw, nh = nb[2] - nb[0], nb[3] - nb[1]
so = c.fit(o, nb[2] + 0.18 * nw, nb[1] + 0.45 * nh,
           nb[2] + 0.18 * nw + 0.62 * (ob[2] - ob[0]), nb[3])
sb = so.bounds
bar = c.fit(c.G('-'), sb[0], nb[1] + 0.10 * nh, sb[2], nb[1] + 0.28 * nh)
c.put('№', c.union(N, so, bar), int(sb[2] + 0.1 * nw))
n = c.save(OUT)
print('saved', OUT, 'added:', n)
