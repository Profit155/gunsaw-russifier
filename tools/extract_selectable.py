# -*- coding: utf-8 -*-
"""Достать список SelectableCharacter: name + краткое начало lore/gameplay
описаний — то, что игрок видит на экране выбора персонажа."""
import os
import re

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

ROOT = r'C:\Users\User\Downloads\gunsaw-demo-win'
DATA = os.path.join(ROOT, 'Gunsaw_Data')
gen = TypeTreeGenerator('2021.1.23f1')
gen.load_local_game(ROOT)


def build_tree(nodes):
    return [
        {
            'm_Level': n.m_Level, 'm_Type': n.m_Type, 'm_Name': n.m_Name,
            'm_MetaFlag': n.m_MetaFlag, 'm_Version': getattr(n, 'm_Version', 1),
            'm_ByteSize': getattr(n, 'm_ByteSize', -1),
            'm_TypeFlags': getattr(n, 'm_TypeFlags', 0),
        }
        for n in nodes
    ]


files = ['globalgamemanagers.assets', 'resources.assets']
files += [f for f in os.listdir(DATA) if re.match(r'^level\d+$', f)]
files += [f for f in os.listdir(DATA) if re.match(r'^sharedassets\d+\.assets$', f)]

cache = {}
seen = set()
rows = []
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
            key = (ms.m_AssemblyName, (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName)
            if key not in cache:
                try:
                    cache[key] = build_tree(gen.get_nodes(*key))
                except Exception:
                    cache[key] = None
            if cache[key] is None:
                continue
            data = obj.read_typetree(cache[key])
            if not isinstance(data, dict) or 'characters' not in data:
                continue
            chars = data.get('characters')
            if not isinstance(chars, list):
                continue
            for c in chars:
                if not isinstance(c, dict):
                    continue
                nm = (c.get('name') or '').strip()
                if not nm or nm in seen:
                    continue
                seen.add(nm)
                lore = (c.get('loreDescription') or '').replace('\n', ' ').strip()
                rows.append((nm, lore[:70]))
        except Exception:
            continue

print('=== SelectableCharacter (экран выбора) ===')
for nm, lore in rows:
    print('  %-16s %s' % (nm, lore))
print('итого:', len(rows))
