# -*- coding: utf-8 -*-
"""Task 12: вытащить строковые литералы из декомпилированного Assembly-CSharp.
Делит на фразы (с пробелами/пунктуацией — почти наверняка игровой текст)
и одиночные слова/идентификаторы (просеиваются вручную)."""
import io
import re
import os

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, '_decomp', 'game', 'Assembly-CSharp.decompiled.cs')
OUT_P = os.path.join(ROOT, 'docs', 'strings_code_phrases.txt')
OUT_W = os.path.join(ROOT, 'docs', 'strings_code_words.txt')

src = io.open(SRC, encoding='utf-8').read()
lits = re.findall(r'"((?:[^"\\]|\\.)*)"', src)


def unesc(s):
    return (s.replace('\\n', '\n').replace('\\t', '\t')
             .replace('\\"', '"').replace('\\\\', '\\'))


seen, phrases, words = set(), [], []
for lit in lits:
    u = unesc(lit).strip()
    if len(u) < 2 or u in seen:
        continue
    seen.add(u)
    if not re.search(r'[A-Za-z]', u):
        continue
    ident = re.match(r'^[A-Za-z0-9_./\\:#{}\[\]()<>=+-]+$', u) and ' ' not in u
    if not ident and (' ' in u or re.search(r'[.!?,]', u)):
        phrases.append(u)
    else:
        words.append(u)

io.open(OUT_P, 'w', encoding='utf-8').write('\n'.join(phrases))
io.open(OUT_W, 'w', encoding='utf-8').write('\n'.join(words))
print('phrases:', len(phrases))
print('words:', len(words))
print('--- sample phrases ---')
for p in phrases[:30]:
    print(' ', p[:110].replace('\n', ' / '))
