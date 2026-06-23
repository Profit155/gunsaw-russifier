# -*- coding: utf-8 -*-
"""Add missing russian-text punctuation (- – — … « ») and digits to built RU fonts.

Run AFTER the per-font build scripts (their output is the input here).
- dashes: stretched hyphen, or a clip of cyrillic Т's top bar if no hyphen
- ellipsis: three periods
- guillemets: doubled '<' chevrons, or chevrons from rotated 'v'
- digits (Gelatik has none): transplanted from Neucha (OFL, angular handwriting)
"""
import math
import os
from outline_lib import Composer

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
RU = os.path.join(ROOT, 'fonts', 'ru')
NEUCHA = os.path.join(ROOT, 'fonts', 'candidates', 'Neucha.ttf')

FONTS = ['PixelOperatorRu.ttf', 'RespawnProRu.ttf', 'GelatikRu.ttf', 'AcidicRu.ttf',
         'VictorRu.ttf', 'HemiHeadRu.ttf', 'ChloeRu.ttf', 'RetroGamingRu.ttf',
         'SansationRu.ttf']


def fix(path):
    c = Composer(path)
    added = []
    have = lambda ch: ord(ch) in c.cmap or ord(ch) in getattr(c, '_pending', {})

    ob = c.G('о').bounds                      # cyrillic о — always present in RU fonts
    o_h = ob[3] - ob[1]
    Tb = c.G('Т').bounds                      # cyrillic Т
    T_h = Tb[3] - Tb[1]

    # --- dash source ---
    if have('-'):
        dash = c.G('-')
        dadv = c.adv('-')
    else:
        bar = c.clip(c.G('Т'), c.rect(Tb[0] - 60, Tb[3] - 0.30 * T_h, Tb[2] + 60, Tb[3] + 60))
        ymid = (ob[1] + ob[3]) / 2
        dash = c.fit(bar, 0, ymid - 0.10 * o_h, 0.55 * o_h, ymid + 0.10 * o_h)
        dadv = int(0.75 * o_h)
        c.put('-', dash, dadv)
        added.append('-')
    db = dash.bounds
    dw = db[2] - db[0]
    for ch, k in (('–', 1.8), ('—', 2.6)):
        if not have(ch):
            c.put(ch, c.fit(dash, db[0], db[1], db[0] + k * dw, db[3]), int(dadv * k))
            added.append(ch)

    # --- ellipsis ---
    if not have('…') and have('.'):
        dot = c.G('.')
        da = c.adv('.')
        c.put('…', c.union(dot, c.move(dot, da), c.move(dot, 2 * da)), int(da * 3))
        added.append('…')

    # --- guillemets: doubled chevrons ---
    if not have('«') or not have('»'):
        if have('<'):
            chev = c.G('<')
        else:
            v = c.G('v')                       # rotate v by -90° -> '<' (opens right)
            a = math.radians(-90)
            chev = c.xform(v, math.cos(a), math.sin(a), -math.sin(a), math.cos(a))
        cb = chev.bounds
        chev = c.fit(chev, 0, ob[1] + 0.12 * o_h, 0.42 * o_h, ob[3] - 0.12 * o_h)
        cw = chev.bounds[2] - chev.bounds[0]
        left = c.union(chev, c.move(chev, 0.75 * cw))
        lb = left.bounds
        right = c.hmirror(left, (lb[0] + lb[2]) / 2)
        adv = int(lb[2] + 0.25 * o_h)
        if not have('«'):
            c.put('«', left, adv)
            added.append('«')
        if not have('»'):
            c.put('»', right, adv)
            added.append('»')

    # --- № (N + small o + underline) ---
    if not have('№') and have('N'):
        N = c.G('N')
        nb = N.bounds
        nw, nh = nb[2] - nb[0], nb[3] - nb[1]
        o_g = c.G('o')
        ob2 = o_g.bounds
        so = c.fit(o_g, nb[2] + 0.18 * nw, nb[1] + 0.45 * nh,
                   nb[2] + 0.18 * nw + 0.62 * (ob2[2] - ob2[0]), nb[3])
        sb = so.bounds
        bar_src = c.G('-') if have('-') else c.clip(c.G('Т'), c.rect(Tb[0] - 60, Tb[3] - 0.30 * T_h, Tb[2] + 60, Tb[3] + 60))
        nbar = c.fit(bar_src, sb[0], nb[1] + 0.10 * nh, sb[2], nb[1] + 0.26 * nh)
        c.put('№', c.union(N, so, nbar), int(sb[2] + 0.1 * nw))
        added.append('№')

    # --- digits (transplant from Neucha if absent) ---
    if not have('0'):
        donor = Composer(NEUCHA)
        cap_h = T_h
        for d in '0123456789':
            g = donor.G(d)
            gb = g.bounds
            scale = cap_h / (gb[3] - gb[1])
            fitted = c.fit(g, 0, Tb[1], (gb[2] - gb[0]) * scale, Tb[3])
            c.put(d, fitted, int((gb[2] - gb[0]) * scale + 0.18 * cap_h))
        added.append('0-9')

    if added:
        c.save(path, family_suffix='')
        return ' '.join(added)
    return None


for fn in FONTS:
    p = os.path.join(RU, fn)
    if not os.path.exists(p):
        print('skip', fn)
        continue
    res = fix(p)
    print(fn, '+', res) if res else print(fn, 'ok')
