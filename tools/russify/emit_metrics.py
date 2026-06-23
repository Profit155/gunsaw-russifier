# -*- coding: utf-8 -*-
"""Emit <font>.metrics.txt next to each deployed ttf: reference glyph metrics
in font units. Unity's FreeType returns garbage advances for a few glyphs
(e.g. Retro Gaming Ы/Х), so the plugin re-applies these after baking.

Line format:  U+0425=adv,lsb,yMax,width,height   (font units; first line upem=N)
"""
import glob
import os
from fontTools.ttLib import TTFont

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
FONTS = os.path.join(ROOT, 'fonts')

for path in glob.glob(os.path.join(FONTS, '*.ttf')):
    name = os.path.basename(path)
    if name.startswith('_') or name == 'arial.ttf':
        continue
    f = TTFont(path, fontNumber=0)
    cmap = f.getBestCmap()
    hmtx = f['hmtx']
    glyf = f['glyf'] if 'glyf' in f else None
    glyphset = f.getGlyphSet()
    upem = f['head'].unitsPerEm
    lines = ['upem=%d' % upem]
    for cp in sorted(cmap):
        gn = cmap[cp]
        adv, lsb = hmtx[gn]
        xmin = ymin = xmax = ymax = 0
        try:
            from fontTools.pens.boundsPen import BoundsPen
            bp = BoundsPen(glyphset)
            glyphset[gn].draw(bp)
            if bp.bounds:
                xmin, ymin, xmax, ymax = bp.bounds
        except Exception:
            pass
        lines.append('U+%04X=%d,%d,%d,%d,%d' % (cp, adv, lsb, ymax, xmax - xmin, ymax - ymin))
    out = os.path.splitext(path)[0] + '.metrics.txt'
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    print(os.path.basename(out), len(cmap), 'chars')
