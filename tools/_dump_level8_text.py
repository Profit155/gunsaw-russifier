# -*- coding: utf-8 -*-
"""Дамп всех TMP m_text из Gunsaw_Data/level8 — чтобы опознать миссию/главу
(инфо-таблички, баннер главы, название). Тайптри из Managed DLL."""
import os, re
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

ROOT = os.path.join(os.path.dirname(__file__), '..')
LEVEL = os.path.join(ROOT, 'Gunsaw_Data', 'level8')

gen = TypeTreeGenerator('2021.1.23f1')
gen.load_local_game(ROOT)

def build_tree(nodes):
    return [{'m_Level': n.m_Level, 'm_Type': n.m_Type, 'm_Name': n.m_Name,
             'm_MetaFlag': n.m_MetaFlag, 'm_Version': getattr(n, 'm_Version', 1),
             'm_ByteSize': getattr(n, 'm_ByteSize', -1),
             'm_TypeFlags': getattr(n, 'm_TypeFlags', 0)} for n in nodes]

env = UnityPy.load(LEVEL)
cache = {}
texts = []
for o in env.objects:
    if o.type.name != 'MonoBehaviour':
        continue
    try:
        mb = o.read(check_read=False)
        ms = mb.m_Script.read()
        cls = (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName
        if 'TextMeshPro' not in cls:
            continue
        key = (ms.m_AssemblyName, cls)
        if key not in cache:
            try:
                cache[key] = build_tree(gen.get_nodes(*key))
            except Exception:
                cache[key] = None
        if not cache[key]:
            continue
        data = o.read_typetree(cache[key])
        t = data.get('m_text', '')
        if t and t.strip():
            texts.append(t.strip())
    except Exception:
        pass

# короткие отдельно (заголовки/баннеры/названия), длинные усечём
short = sorted(set(t for t in texts if len(t) <= 60))
longs = [t for t in texts if len(t) > 60]
print("=== Короткие TMP-строки level8 (заголовки/таблички/баннеры) ===")
for s in short:
    print('  ', repr(s))
print(f"\n=== Длинные TMP-строки level8 ({len(longs)} шт, первые 80 симв) ===")
for s in longs:
    print('  ', repr(s[:80]))
