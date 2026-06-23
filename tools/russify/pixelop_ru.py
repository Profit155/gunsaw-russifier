# -*- coding: utf-8 -*-
"""Builds PixelOperatorRu.ttf: Pixel Operator (CC0) + hand-made cyrillic glyphs.

Pixel grid: 1 px = 100 units, caps rows 0..8, x-height rows 0..6, descender to -3.
Each ART glyph is (top_row, [row strings col0..]), '#' = filled pixel, col0 = x=100 (1px LSB).
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

SRC = os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'originals', 'pixel-operator', 'PixelOperator.ttf')
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'ru', 'PixelOperatorRu.ttf')
PX = 100
LSB = 1  # left bearing in px


# ---------- extraction of existing glyphs as pixel cell sets ----------

def glyph_cells(font, gname):
    """Rasterize an axis-aligned pixel glyph into a set of (col,row) cells."""
    glyf = font['glyf']
    g = glyf[gname]
    if g.numberOfContours <= 0:
        return set()
    coords, ends, _ = g.getCoordinates(glyf)
    polys, start = [], 0
    for e in ends:
        polys.append([tuple(coords[i]) for i in range(start, e + 1)])
        start = e + 1
    cells = set()
    for col in range(-2, 16):
        for row in range(-4, 14):
            x, y = col * PX + 50, row * PX + 50
            cnt = 0
            for poly in polys:
                inside, j = False, len(poly) - 1
                for i in range(len(poly)):
                    xi, yi = poly[i]
                    xj, yj = poly[j]
                    if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                        inside = not inside
                    j = i
                if inside:
                    cnt += 1
            if cnt % 2:
                cells.add((col, row))
    return cells


def mirror(cells):
    if not cells:
        return cells
    lo = min(c for c, _ in cells)
    hi = max(c for c, _ in cells)
    return {(lo + hi - c, r) for c, r in cells}


def art_cells(top, rows):
    cells = set()
    for i, line in enumerate(rows):
        r = top - i
        for c, ch in enumerate(line):
            if ch == '#':
                cells.add((c + LSB, r))
    return cells


def add_art(base_cells, top, rows):
    return base_cells | art_cells(top, rows)


# ---------- cyrillic definitions ----------
# value: ('copy', 'X') | ('mirror', 'X') | ('art', top, [rows]) | ('copy+art', 'X', top, [rows])

DEFS = {
    # capitals
    'А': ('copy', 'A'),
    'Б': ('art', 8, ["#####", "#....", "#....", "#....", "####.", "#...#", "#...#", "#...#", "####."]),
    'В': ('copy', 'B'),
    'Г': ('art', 8, ["#####", "#....", "#....", "#....", "#....", "#....", "#....", "#....", "#...."]),
    'Д': ('art', 8, [".####", ".#..#", ".#..#", ".#..#", ".#..#", ".#..#", "#...#", "#####", "#...#"]),
    'Е': ('copy', 'E'),
    'Ё': ('copy+art', 'E', 10, [".#.#."]),
    'Ж': ('art', 8, ["#..#..#", "#..#..#", ".#.#.#.", ".#.#.#.", "..###..", ".#.#.#.", ".#.#.#.", "#..#..#", "#..#..#"]),
    'З': ('copy', 'three'),
    'И': ('art', 8, ["#...#", "#...#", "#..##", "#.#.#", "##..#", "#...#", "#...#", "#...#", "#...#"]),
    'Й': ('art', 10, ["#...#", ".###.", "#...#", "#...#", "#..##", "#.#.#", "##..#", "#...#", "#...#", "#...#", "#...#"]),
    'К': ('copy', 'K'),
    'Л': ('art', 8, [".####", ".#..#", ".#..#", ".#..#", ".#..#", ".#..#", ".#..#", "#...#", "#...#"]),
    'М': ('copy', 'M'),
    'Н': ('copy', 'H'),
    'О': ('copy', 'O'),
    'П': ('art', 8, ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#"]),
    'Р': ('copy', 'P'),
    'С': ('copy', 'C'),
    'Т': ('copy', 'T'),
    'У': ('art', 8, ["#...#", "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", ".#...", "#...."]),
    'Ф': ('art', 8, ["..#..", ".###.", "#.#.#", "#.#.#", "#.#.#", ".###.", "..#..", "..#..", "..#.."]),
    'Х': ('copy', 'X'),
    'Ц': ('art', 8, ["#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "######", ".....#"]),
    'Ч': ('art', 8, ["#...#", "#...#", "#...#", "#...#", ".####", "....#", "....#", "....#", "....#"]),
    'Ш': ('art', 8, ["#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#######"]),
    'Щ': ('art', 8, ["#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "########", ".......#"]),
    'Ъ': ('art', 8, ["##...", ".#...", ".#...", ".#...", ".###.", ".#..#", ".#..#", ".#..#", ".###."]),
    'Ы': ('art', 8, ["#.....#", "#.....#", "#.....#", "#.....#", "####..#", "#...#.#", "#...#.#", "#...#.#", "####..#"]),
    'Ь': ('art', 8, ["#....", "#....", "#....", "#....", "####.", "#...#", "#...#", "#...#", "####."]),
    'Э': ('art', 8, [".###.", "#...#", "....#", "....#", ".####", "....#", "....#", "#...#", ".###."]),
    'Ю': ('art', 8, ["#....###.", "#...#...#", "#...#...#", "#...#...#", "#####...#", "#...#...#", "#...#...#", "#...#...#", "#....###."]),
    'Я': ('mirror', 'R'),
    # lowercase
    'а': ('copy', 'a'),
    'б': ('art', 8, ["..###", ".#...", "#....", "####.", "#...#", "#...#", "#...#", "#...#", ".###."]),
    'в': ('art', 6, ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."]),
    'г': ('art', 6, ["#####", "#....", "#....", "#....", "#....", "#....", "#...."]),
    'д': ('art', 6, [".####", ".#..#", ".#..#", ".#..#", "#...#", "#####", "#...#"]),
    'е': ('copy', 'e'),
    'ё': ('copy+art', 'e', 8, [".#.#."]),
    'ж': ('art', 6, ["#..#..#", "#..#..#", ".#.#.#.", "..###..", ".#.#.#.", "#..#..#", "#..#..#"]),
    'з': ('art', 6, [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."]),
    'и': ('art', 6, ["#...#", "#...#", "#..##", "#.#.#", "##..#", "#...#", "#...#"]),
    'й': ('art', 8, ["#...#", ".###.", "#...#", "#...#", "#..##", "#.#.#", "##..#", "#...#", "#...#"]),
    'к': ('art', 6, ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"]),
    'л': ('art', 6, [".####", ".#..#", ".#..#", ".#..#", ".#..#", "#...#", "#...#"]),
    'м': ('art', 6, ["#.....#", "##...##", "#.#.#.#", "#..#..#", "#.....#", "#.....#", "#.....#"]),
    'н': ('art', 6, ["#...#", "#...#", "#####", "#...#", "#...#", "#...#", "#...#"]),
    'о': ('copy', 'o'),
    'п': ('art', 6, ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#"]),
    'р': ('copy', 'p'),
    'с': ('copy', 'c'),
    'т': ('art', 6, ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."]),
    'у': ('copy', 'y'),
    'ф': ('art', 8, ["..#..", "..#..", ".###.", "#.#.#", "#.#.#", "#.#.#", ".###.", "..#..", "..#..", "..#..", "..#.."]),
    'х': ('copy', 'x'),
    'ц': ('art', 6, ["#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "#...#.", "######", ".....#"]),
    'ч': ('art', 6, ["#...#", "#...#", ".####", "....#", "....#", "....#", "....#"]),
    'ш': ('art', 6, ["#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#######"]),
    'щ': ('art', 6, ["#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "#..#..#.", "########", ".......#"]),
    'ъ': ('art', 6, ["##...", ".#...", ".###.", ".#..#", ".#..#", ".#..#", ".###."]),
    'ы': ('art', 6, ["#.....#", "#.....#", "####..#", "#...#.#", "#...#.#", "#...#.#", "####..#"]),
    'ь': ('art', 6, ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."]),
    'э': ('art', 6, [".###.", "#...#", "....#", ".####", "....#", "#...#", ".###."]),
    'ю': ('art', 6, ["#....##.", "#...#..#", "#...#..#", "#####..#", "#...#..#", "#...#..#", "#....##."]),
    'я': ('art', 6, [".####", "#...#", "#...#", ".####", ".#..#", "#...#", "#...#"]),
    '№': ('art', 8, ["#...#..##.", "#...#.#..#", "#...#.#..#", "#..##..##.", "#.#.#.....", "##..#.####", "#...#.....", "#...#.....", "#...#....."]),
}


# ---------- glyph building ----------

def cells_to_glyph(cells):
    """Merge cells into per-row run rectangles and emit a TT glyph."""
    pen = TTGlyphPen(None)
    rows = {}
    for c, r in cells:
        rows.setdefault(r, []).append(c)
    for r, cols in rows.items():
        cols.sort()
        run_start = prev = cols[0]
        runs = []
        for c in cols[1:]:
            if c == prev + 1:
                prev = c
            else:
                runs.append((run_start, prev))
                run_start = prev = c
        runs.append((run_start, prev))
        for c0, c1 in runs:
            x0, x1 = c0 * PX, (c1 + 1) * PX
            y0, y1 = r * PX, (r + 1) * PX
            pen.moveTo((x0, y0))
            pen.lineTo((x0, y1))
            pen.lineTo((x1, y1))
            pen.lineTo((x1, y0))
            pen.closePath()
    return pen.glyph()


def build():
    font = TTFont(SRC)
    cmap = font.getBestCmap()
    glyf = font['glyf']
    hmtx = font['hmtx']
    order = font.getGlyphOrder()

    def src_name(ch_or_name):
        if len(ch_or_name) == 1:
            return cmap[ord(ch_or_name)]
        return ch_or_name  # raw glyph name like 'three'

    new_maps = {}
    for ch, spec in DEFS.items():
        kind = spec[0]
        if kind == 'copy':
            cells = glyph_cells(font, src_name(spec[1]))
        elif kind == 'mirror':
            cells = mirror(glyph_cells(font, src_name(spec[1])))
        elif kind == 'art':
            cells = art_cells(spec[1], spec[2])
        elif kind == 'copy+art':
            cells = add_art(glyph_cells(font, src_name(spec[1])), spec[2], spec[3])
        else:
            raise ValueError(kind)
        gname = 'uni%04X' % ord(ch)
        glyph = cells_to_glyph(cells)
        glyph.recalcBounds(glyf)
        existed = gname in glyf.glyphs
        glyf[gname] = glyph
        adv = (max(c for c, _ in cells) + 2) * PX
        hmtx[gname] = (adv, min(c for c, _ in cells) * PX)
        if not existed and gname not in order:
            order.append(gname)
        new_maps[ord(ch)] = gname

    font.setGlyphOrder(order)
    if hasattr(glyf, 'glyphOrder'):
        glyf.glyphOrder = order
    for table in font['cmap'].tables:
        if table.isUnicode():
            table.cmap.update(new_maps)

    # rename so the family is distinguishable from the original
    for rec in font['name'].names:
        if rec.nameID in (1, 3, 4, 6, 16):
            s = rec.toUnicode().replace('Pixel Operator', 'Pixel Operator Ru').replace('PixelOperator', 'PixelOperatorRu')
            font['name'].setName(s, rec.nameID, rec.platformID, rec.platEncID, rec.langID)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # appended glyphs lose advances unless hhea.numberOfHMetrics covers them
    font['hhea'].numberOfHMetrics = len(order)
    font.save(OUT)
    print('saved', OUT, 'glyphs added:', len(new_maps))


if __name__ == '__main__':
    build()
