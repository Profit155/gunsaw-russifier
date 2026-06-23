# -*- coding: utf-8 -*-
"""Реплики Chatter по врагам: ручной парс сырых байтов (шесть string[]
идут первыми полями после заголовка MonoBehaviour) + имя GameObject."""
import io
import os
import re
import struct

import UnityPy

ROOT = r'C:\Users\User\Downloads\gunsaw-demo-win'
DATA = os.path.join(ROOT, 'Gunsaw_Data')
OUT = os.path.join(ROOT, 'docs', 'chatter_by_enemy.txt')

CATS = ['alert', 'spot', 'reload', 'allyDeath', 'death', 'ouch']


def align4(i):
    return (i + 3) & ~3


def read_str(buf, i):
    ln = struct.unpack_from('<i', buf, i)[0]
    if ln < 0 or i + 4 + ln > len(buf):
        raise ValueError('bad string len %d at %d' % (ln, i))
    s = buf[i + 4:i + 4 + ln].decode('utf-8', 'replace')
    return s, align4(i + 4 + ln)


def parse_chatter(buf):
    i = 12 + 4 + 12  # m_GameObject PPtr, m_Enabled+pad, m_Script PPtr
    _, i = read_str(buf, i)  # m_Name (обычно пустое в билде)
    fields = {}
    for cat in CATS:
        n = struct.unpack_from('<i', buf, i)[0]
        i += 4
        if n < 0 or n > 5000:
            raise ValueError('bad array count %d' % n)
        arr = []
        for _ in range(n):
            s, i = read_str(buf, i)
            arr.append(s)
        fields[cat] = arr
    return fields


def get_transform(go):
    for comp in go.m_Components:
        ptr = getattr(comp, 'component', comp)
        try:
            c = ptr.read()
        except Exception:
            continue
        if type(c).__name__ in ('Transform', 'RectTransform'):
            return c
    return None


def root_name(go):
    """Имя корневого GameObject прифаба (Chatter висит на Head)."""
    t = get_transform(go)
    guard = 0
    last = go
    while t is not None and guard < 64:
        guard += 1
        try:
            t2 = t.m_Father.read()
        except Exception:
            break
        t = t2
    if t is not None:
        try:
            last = t.m_GameObject.read()
        except Exception:
            pass
    return last.m_Name


files = ['globalgamemanagers.assets', 'resources.assets']
files += [f for f in os.listdir(DATA) if re.match(r'^level\d+$', f)]
files += [f for f in os.listdir(DATA) if re.match(r'^sharedassets\d+\.assets$', f)]

groups = {}  # (goName, fingerprint) -> fields
for fname in files:
    path = os.path.join(DATA, fname)
    if not os.path.exists(path):
        continue
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        try:
            mb = obj.read(check_read=False)
            ms = mb.m_Script.read()
            if ms.m_ClassName != 'Chatter':
                continue
            go = mb.m_GameObject.read()
            name = root_name(go)
        except Exception:
            continue
        try:
            fields = parse_chatter(obj.get_raw_data())
        except Exception as e:
            print('parse fail on', name, 'in', fname, ':', e)
            continue
        fp = hash(tuple(tuple(fields[c]) for c in CATS))
        groups[(name, fp)] = fields

with io.open(OUT, 'w', encoding='utf-8') as fh:
    for (name, _), fields in sorted(groups.items()):
        total = sum(len(v) for v in fields.values())
        fh.write('=== %s (%d lines) ===\n' % (name, total))
        for cat in CATS:
            for s in fields[cat]:
                fh.write('[%s] %s\n' % (cat, s.replace('\n', '\\n')))
        fh.write('\n')

print('groups:')
for (name, _), fields in sorted(groups.items()):
    print('  %-28s %d lines' % (name, sum(len(v) for v in fields.values())))
print('->', OUT)
