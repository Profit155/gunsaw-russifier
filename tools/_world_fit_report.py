# -*- coding: utf-8 -*-
"""Построчное сравнение world-табличек EN↔RU: где русская строка шире английской
(переполнение). Нормализуем переносы: в ассете m_text реальный \\n, в .txt — литерал."""
import json, os, re

ROOT = os.path.join(os.path.dirname(__file__), '..')
rows = json.load(open(os.path.join(ROOT, 'docs', '_world_text_dump.json'), encoding='utf-8'))

tx = {}
TD = os.path.join(ROOT, 'BepInEx', 'Translation', 'ru', 'Text')
for fn in os.listdir(TD):
    if not fn.endswith('.txt'):
        continue
    for line in open(os.path.join(TD, fn), encoding='utf-8'):
        s = line.rstrip('\n')
        if not s or s.lstrip().startswith('//') or s.lstrip().startswith('r:') or '=' not in s:
            continue
        k, v = s.split('=', 1)
        tx[k] = v

def has_cyr(s): return bool(re.search('[А-Яа-яЁё]', s))
NL = '\\n'                               # литерал backslash-n, как в ключах .txt
def to_literal(s): return s.replace('\n', NL)   # реальный перевод строки -> литерал
def lines(s): return s.split(NL)
def maxline(s): return max((len(x) for x in lines(s)), default=0)

seen = set()
res = []
for r in rows:
    en = to_literal(r['text'])
    if en in seen:
        continue
    seen.add(en)
    ru = tx.get(en)
    if not ru or not has_cyr(ru):
        continue
    emax, rmax = maxline(en), maxline(ru)
    if rmax - emax >= 4:                 # переполнение хотя бы на 4 симв по самой длинной строке
        res.append((rmax - emax, emax, rmax, r['level'], en, ru))

res.sort(reverse=True)
print(f"переполняющих уникальных world-табличек: {len(res)}\n")
for over, emax, rmax, lvl, en, ru in res:
    print(f"[{lvl}] +{over}  (EN max {emax} -> RU max {rmax})")
    el, rl = lines(en), lines(ru)
    for i in range(max(len(el), len(rl))):
        e = el[i] if i < len(el) else ''
        rr = rl[i] if i < len(rl) else ''
        mark = '  <<' if len(rr) > emax else ''
        print(f"    EN[{len(e):>2}] {e!r:42}  RU[{len(rr):>2}] {rr!r}{mark}")
    print()
