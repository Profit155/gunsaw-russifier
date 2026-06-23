# -*- coding: utf-8 -*-
"""Сканирует docs/wf_out/out_*.json на verdict=='doubtful', сверяет с доставленными
ключами переводов (ru/Text/*.txt). Печатает: что доставлено, что НЕТ (дырки)."""
import os, re, glob, json

ROOT = os.path.join(os.path.dirname(__file__), '..')
WFOUT = os.path.join(ROOT, 'docs', 'wf_out')
TXTDIR = os.path.join(ROOT, 'BepInEx', 'Translation', 'ru', 'Text')

# 1. собрать все doubtful (рекурсивный обход json)
doubtful = []
def walk(node, src):
    if isinstance(node, dict):
        if str(node.get('verdict', '')).lower() == 'doubtful':
            doubtful.append({'key': node.get('key', ''), 'ru': node.get('ru', ''),
                             'note': node.get('note', ''), 'src': src})
        for v in node.values():
            walk(v, src)
    elif isinstance(node, list):
        for v in node:
            walk(v, src)

for p in sorted(glob.glob(os.path.join(WFOUT, 'out_*.json'))):
    try:
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print("!! не распарсил", os.path.basename(p), e); continue
    walk(data, os.path.basename(p))

# 2. доставленные ключи (плейн, левая часть до первого '=') + сырьё regex-значений
plain_keys = set()
regex_lines = []
for p in glob.glob(os.path.join(TXTDIR, '*.txt')):
    with open(p, encoding='utf-8') as f:
        for line in f:
            s = line.rstrip('\n')
            if not s or s.lstrip().startswith('//') or '=' not in s:
                continue
            k = s.split('=', 1)[0]
            if k.lstrip().startswith('r:'):
                regex_lines.append(s)
            else:
                plain_keys.add(k)

def delivered(key):
    if key in plain_keys:
        return 'plain'
    # грубая проверка: встречается ли ключ как подстрока в каком-то regex-правиле
    for rl in regex_lines:
        core = re.sub(r'[\^\$\\]', '', rl.split('=', 1)[0])
        words = [w for w in re.findall(r'[A-Za-z]{4,}', key)]
        if words and all(w in rl for w in words[:3]):
            return 'regex?'
    return None

deliv, gaps = [], []
for d in doubtful:
    st = delivered(d['key'])
    (deliv if st else gaps).append({**d, 'how': st})

print(f"ВСЕГО doubtful: {len(doubtful)} | доставлено: {len(deliv)} | ДЫРКИ: {len(gaps)}\n")
print("================= ДЫРКИ (не доставлено) =================")
for g in sorted(gaps, key=lambda x: x['src']):
    k = g['key'].replace('\\n', '⏎')
    ru = g['ru'].replace('\\n', '⏎')
    print(f"[{g['src']}] {k!r}")
    if ru:
        print(f"      draft RU: {ru!r}")
    if g['note']:
        print(f"      note: {g['note']}")
