# -*- coding: utf-8 -*-
"""Сверяет пул строк ErrorDetector (из docs/strings_assets.txt) с переведёнными
ключами во всех ru/Text/*.txt. Печатает, что переведено и что НЕТ."""
import os, re, glob

ROOT = os.path.join(os.path.dirname(__file__), '..')
ASSETS = os.path.join(ROOT, 'docs', 'strings_assets.txt')
TXTDIR = os.path.join(ROOT, 'BepInEx', 'Translation', 'ru', 'Text')

# 1. строки ErrorDetector
ed = []
with open(ASSETS, encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.search(r'\t(\[[^\]]*\])\s*$', line)
        if not m:
            continue
        tag = m.group(1)
        if 'ErrorDetector' not in tag:
            continue
        text = line[:m.start()]
        ed.append((text, tag))

# 2. все ключи переводов (левая часть до первого '='), по файлам
keys = {}   # key -> file
for p in glob.glob(os.path.join(TXTDIR, '*.txt')):
    fn = os.path.basename(p)
    with open(p, encoding='utf-8') as f:
        for line in f:
            s = line.rstrip('\n')
            if not s or s.lstrip().startswith('//') or '=' not in s:
                continue
            k = s.split('=', 1)[0]
            keys.setdefault(k, fn)

print("=== ErrorDetector: ПЕРЕВЕДЕНО ===")
done = miss = 0
missing = []
for text, tag in ed:
    if text in keys:
        done += 1
    else:
        miss += 1
        missing.append((text, tag))

print(f"переведено: {done}, НЕ переведено: {miss}\n")
print("=== НЕ ПЕРЕВЕДЕНО ===")
for text, tag in missing:
    chat = ' (есть в chatter!)' if 'Chatter' in tag else ''
    print(f"  {text!r}{chat}")
