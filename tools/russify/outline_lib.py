# -*- coding: utf-8 -*-
"""Shared helpers for building cyrillic glyphs in outline fonts by composing
pieces of existing latin glyphs (skia-pathops booleans + affine transforms)."""
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from pathops import Path, PathOp, op


def _otf_to_ttf(font):
    """Convert CFF outlines to quadratic glyf in place (standard otf2ttf recipe)."""
    from fontTools.pens.cu2quPen import Cu2QuPen
    glyph_order = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()
    glyf = newTable('glyf')
    glyf.glyphOrder = glyph_order
    glyf.glyphs = {}
    for name in glyph_order:
        pen = TTGlyphPen(glyph_set)
        glyph_set[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
        glyf.glyphs[name] = pen.glyph()
    font['glyf'] = glyf
    font['loca'] = newTable('loca')
    maxp = newTable('maxp')
    maxp.tableVersion = 0x00010000
    maxp.numGlyphs = len(glyph_order)
    for attr in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs',
                 'maxInstructionDefs', 'maxStackElements', 'maxSizeOfInstructions',
                 'maxComponentElements', 'maxComponentDepth', 'maxPoints',
                 'maxContours', 'maxCompositePoints', 'maxCompositeContours'):
        setattr(maxp, attr, 0)
    maxp.maxZones = 1
    font['maxp'] = maxp
    font['head'].glyphDataFormat = 0
    font['post'].formatType = 2.0
    font['post'].extraNames = []
    font['post'].mapping = {}
    font['post'].glyphOrder = glyph_order
    for tag in ('CFF ', 'VORG'):
        if tag in font:
            del font[tag]
    font.sfntVersion = '\x00\x01\x00\x00'
    # recalc glyph bounds so hmtx/bbox stay sane
    for name in glyph_order:
        glyf.glyphs[name].recalcBounds(glyf)


class Composer:
    def __init__(self, src_path):
        self.font = TTFont(src_path, fontNumber=0)
        if 'CFF ' in self.font:
            _otf_to_ttf(self.font)
        self.cmap = self.font.getBestCmap()
        self.glyf = self.font['glyf']
        self.hmtx = self.font['hmtx']

    # ---- path sources ----

    def G(self, ch_or_name):
        """Path of an existing glyph (by char or raw glyph name); decomposes components."""
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        name = self.cmap[ord(ch_or_name)] if len(ch_or_name) == 1 else ch_or_name
        glyphset = self.font.getGlyphSet()
        rec = DecomposingRecordingPen(glyphset)
        glyphset[name].draw(rec)
        p = Path()
        rec.replay(p.getPen())
        return p

    def adv(self, ch_or_name):
        name = self.cmap[ord(ch_or_name)] if len(ch_or_name) == 1 else ch_or_name
        return self.hmtx[name][0]

    # ---- geometry ----

    @staticmethod
    def rect(x0, y0, x1, y1):
        p = Path()
        pen = p.getPen()
        pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0))
        pen.closePath()
        return p

    @staticmethod
    def poly(*pts):
        p = Path()
        pen = p.getPen()
        pen.moveTo(pts[0])
        for pt in pts[1:]:
            pen.lineTo(pt)
        pen.closePath()
        return p

    @staticmethod
    def xform(path, xx=1, xy=0, yx=0, yy=1, dx=0, dy=0):
        out = Path()
        path.draw(TransformPen(out.getPen(), (xx, xy, yx, yy, dx, dy)))
        return out

    @classmethod
    def move(cls, path, dx, dy=0):
        return cls.xform(path, dx=dx, dy=dy)

    @classmethod
    def hmirror(cls, path, about):
        """Mirror horizontally about vertical line x=about."""
        return cls.xform(path, xx=-1, dx=2 * about)

    @classmethod
    def vflip(cls, path, about):
        """Flip vertically about horizontal line y=about."""
        return cls.xform(path, yy=-1, dy=2 * about)

    @classmethod
    def scale(cls, path, sx, sy, ox=0, oy=0):
        return cls.xform(path, xx=sx, yy=sy, dx=ox * (1 - sx), dy=oy * (1 - sy))

    @staticmethod
    def union(*paths):
        out = paths[0]
        for p in paths[1:]:
            out = op(out, p, PathOp.UNION)
        return out

    @staticmethod
    def cut(a, b):
        return op(a, b, PathOp.DIFFERENCE)

    @staticmethod
    def clip(a, b):
        return op(a, b, PathOp.INTERSECTION)

    def fit(self, path, x0, y0, x1, y1):
        """Scale+move path so its bbox becomes (x0,y0)-(x1,y1)."""
        b = path.bounds
        p = self.xform(path, (x1 - x0) / (b[2] - b[0]), 0, 0, (y1 - y0) / (b[3] - b[1]))
        b2 = p.bounds
        return self.move(p, x0 - b2[0], y0 - b2[1])

    def be_glyph(self, bar_src, bar_zone):
        """б = digit 6 + horizontal flag terminal at the tail tip."""
        six = self.G('6')
        b = six.bounds
        w, h = b[2] - b[0], b[3] - b[1]
        bar = self.clip(self.G(bar_src), self.rect(*bar_zone))
        flag = self.fit(bar, b[0] + 0.45 * w, b[3] - 0.16 * h, b[2] + 0.30 * w, b[3])
        return self.union(six, flag), int(self.adv('6') + 0.25 * w)

    def be_with_tail(self, tail, o=None):
        """б = this font's o-bowl + a transplanted canonical б tail (see b_tail_from)."""
        o = o if o is not None else self.G('o')
        bo = o.bounds
        wo, ho = bo[2] - bo[0], bo[3] - bo[1]
        t = self.fit(tail, bo[0] - 0.02 * wo, bo[1] + 0.62 * ho,
                     bo[2] + 0.10 * wo, bo[1] + 1.62 * ho)
        return self.union(o, t), int(self.adv('o') + 0.1 * wo)

    # ---- output ----

    def put(self, ch, path, advance, lsb=None):
        """Install path as the glyph for character ch."""
        gname = 'uni%04X' % ord(ch)
        pen = TTGlyphPen(None)
        path.draw(pen)
        glyph = pen.glyph()
        glyph.recalcBounds(self.glyf)
        existed = gname in self.glyf.glyphs
        self.glyf[gname] = glyph
        self.hmtx[gname] = (int(advance), int(glyph.xMin if lsb is None else lsb))
        if not existed:
            order = self.font.getGlyphOrder()
            if gname not in order:
                order.append(gname)
        self._pending = getattr(self, '_pending', {})
        self._pending[ord(ch)] = gname

    def alias(self, ch, src_ch_or_name):
        """Map ch to an existing glyph without copying outlines."""
        name = self.cmap[ord(src_ch_or_name)] if len(src_ch_or_name) == 1 else src_ch_or_name
        self._pending = getattr(self, '_pending', {})
        self._pending[ord(ch)] = name

    def save(self, out_path, family_suffix=' Ru'):
        for table in self.font['cmap'].tables:
            if table.isUnicode():
                table.cmap.update(self._pending)
        name = self.font['name']
        for rec in name.names:
            if rec.nameID in (1, 3, 4, 6, 16):
                s = rec.toUnicode()
                if family_suffix.strip() and family_suffix.strip() not in s:
                    if rec.nameID == 6:
                        s = s + family_suffix.replace(' ', '')
                    else:
                        s = s + family_suffix
                name.setName(s, rec.nameID, rec.platformID, rec.platEncID, rec.langID)
        import os
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # fontTools never GROWS hhea.numberOfHMetrics, so appended glyphs lose their
        # advances (FreeType then reads garbage). Force full metrics; compile may
        # safely shrink trailing equal-advance entries back.
        self.font['hhea'].numberOfHMetrics = len(self.font.getGlyphOrder())
        self.font.save(out_path)
        return len(self._pending)


def b_tail_from(lib_path):
    """Extract the tail of 'б' (everything above the bowl) from a cyrillic font."""
    c = Composer(lib_path)
    be = c.G('б')
    bb = be.bounds
    h = bb[3] - bb[1]
    return c.clip(be, c.rect(bb[0] - 50, bb[1] + 0.52 * h, bb[2] + 50, bb[3] + 50))
