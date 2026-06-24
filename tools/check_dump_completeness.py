# -*- coding: utf-8 -*-
"""Проверка полноты дампов: сравнивает строковые литералы декомпила с объединённым дампом."""
import io, re, glob

dump = set()
for ln in io.open('docs/strings_assets.txt', encoding='utf-8'):
    ln = ln.rstrip('\n')
    if '\t' in ln:
        dump.add(ln.rsplit('\t', 1)[0])
for fp in ('docs/strings_code_phrases.txt', 'docs/strings_code_words.txt'):
    for ln in io.open(fp, encoding='utf-8'):
        dump.add(ln.rstrip('\n'))
print('строк в дампах (сырых):', len(dump))

src = io.open('_decomp/game/Assembly-CSharp.decompiled.cs', encoding='utf-8', errors='replace').read()
# строковые литералы C#: "..." с учётом экранирования
lits = re.findall(r'"((?:[^"\\]|\\.)*)"', src)


def humanish(s):
    if not re.search(r'[A-Za-z]', s):
        return False
    if s.startswith(('Sounds/', 'Spawnables/', 'Assets/', '/', '#', 'http')):
        return False
    if ' ' not in s and len(s) < 12 and re.match(r'^[A-Za-z0-9_./<>+-]+$', s):
        return False  # одиночный идентификатор/путь
    if len(s) < 3:
        return False
    return True


lits = sorted({s for s in lits if humanish(s)})
print('человекочитаемых литералов в коде:', len(lits))


def norm(s):
    return s.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t').strip()


dn = set(norm(d) for d in dump)
missing = [s for s in lits if norm(s) not in dn]
print('НЕ найдено в дампах:', len(missing))
print()
print('=== примеры пропущенного (первые 50) ===')
for s in missing[:50]:
    print('  ', repr(s[:90]))

# записываем значимые пропущенные строки кода (без чистых символов) для добавления в перевод
keep = [s for s in missing if re.search(r'[A-Za-z]', s) and len(s.strip()) > 3]
io.open('docs/strings_code_runtime.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(keep) + '\n')
print('\nзаписано docs/strings_code_runtime.txt:', len(keep), 'строк')
