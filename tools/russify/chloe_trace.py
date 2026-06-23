# -*- coding: utf-8 -*-
"""Rebuild 'chloe font v1' as a TTF by tracing its SDF atlas.

The game ships only the TMP SDF atlas (no source ttf). chloe_glyphs.json is a
runtime dump of the TMP glyph table (rects + metrics). The SDF alpha channel is
a continuous distance field, so upscale x8 + threshold 128 gives smooth shapes
for potrace.
"""
import json
import os
import numpy as np
import potrace
from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
META = os.path.join(ROOT, 'chloe_glyphs.json')
ATLAS = os.path.join(ROOT, 'fonts', 'ru', '_chloe_atlas_alpha.png')
OUT = os.path.join(ROOT, 'fonts', 'ru', '_chloe_traced.ttf')

UPM = 1000
SS = 8  # supersampling factor

meta = json.load(open(META, encoding='utf-8'))
atlas = Image.open(ATLAS)
AW, AH = atlas.size
pt = meta['pointSize']
K = UPM / pt              # font units per atlas pixel

glyphs = {'.notdef': TTGlyphPen(None).glyph()}
cmap = {}
metrics = {'.notdef': (int(meta['chars'][0]['adv'] * K), 0)}

for chd in meta['chars']:
    u = chd['u']
    name = 'uni%04X' % u
    w, h = chd['w'], chd['h']
    pen = TTGlyphPen(None)
    if w > 0 and h > 0:
        # atlas rect y origin is bottom-left; PIL is top-left
        box = (chd['x'], AH - (chd['y'] + h), chd['x'] + w, AH - chd['y'])
        crop = atlas.crop(box).resize((w * SS, h * SS), Image.BILINEAR)
        bits = np.array(crop) <= 128   # potracer traces ZERO pixels as foreground
        bmp = potrace.Bitmap(bits)
        path = bmp.trace(turdsize=8, alphamax=1.0, opttolerance=0.3)
        # pixel(尺SS) -> glyph units: x = bx + px/SS*K ; y = (by - gh) + (h - py/SS)*K
        bx, by, gh = chd['bx'], chd['by'], chd['gh']
        sx = K / SS
        ox = bx * K
        oy = (by - gh) * K

        def XY(p):
            return (ox + p.x * sx, oy + (h * SS - p.y) * sx)

        qpen = Cu2QuPen(pen, max_err=2.0, reverse_direction=False)
        for curve in path:
            qpen.moveTo(XY(curve.start_point))
            for seg in curve:
                if seg.is_corner:
                    qpen.lineTo(XY(seg.c))
                    qpen.lineTo(XY(seg.end_point))
                else:
                    qpen.curveTo(XY(seg.c1), XY(seg.c2), XY(seg.end_point))
            qpen.closePath()
    glyphs[name] = pen.glyph()
    cmap[u] = name
    metrics[name] = (int(round(chd['adv'] * K)), int(round(chd['bx'] * K)))

order = ['.notdef'] + [n for n in glyphs if n != '.notdef']
fb = FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(order)
fb.setupCharacterMap(cmap)
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics(metrics)
asc = int(round(meta['ascent'] * K))
dsc = int(round(meta['descent'] * K))
fb.setupHorizontalHeader(ascent=asc, descent=dsc)
fb.setupNameTable({'familyName': 'Chloe Trace', 'styleName': 'Regular',
                   'fullName': 'Chloe Trace', 'psName': 'ChloeTrace'})
fb.setupOS2(sTypoAscender=asc, sTypoDescender=dsc, usWinAscent=max(asc, 0),
            usWinDescent=abs(min(dsc, 0)))
fb.setupPost()
fb.save(OUT)
print('saved', OUT, 'glyphs:', len(order) - 1, 'pointSize:', pt)
