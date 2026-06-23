# -*- coding: utf-8 -*-
"""Достать отображаемые названия видов: значения speciesName (то, что игрок
видит в "Species: X") + afterSwapTip из всех ассетов."""
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

species = {}   # speciesName -> set(goName)
cache = {}
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
            full = (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName
            key = (ms.m_AssemblyName, full)
            if key not in cache:
                try:
                    cache[key] = build_tree(gen.get_nodes(*key))
                except Exception:
                    cache[key] = None
            if cache[key] is None:
                continue
            data = obj.read_typetree(cache[key])
            if not isinstance(data, dict) or 'speciesName' not in data:
                continue
            sp = (data.get('speciesName') or '').strip()
            if not sp:
                continue
            try:
                go = mb.m_GameObject.read().m_Name
            except Exception:
                go = '?'
            species.setdefault(sp, set()).add(go)
        except Exception:
            continue

print('=== speciesName (как видит игрок) ===')
for sp in sorted(species):
    print('  %-18s  prefabs: %s' % (sp, ', '.join(sorted(species[sp]))))
print('итого видов:', len(species))
