# -*- coding: utf-8 -*-
"""Дамп РОВНО поля WeaponPreset.name (отображаемое имя оружия, stats.name) по всем ассетам.
Выводит: name<TAB>m_Name(имя ассета)<TAB>magSize. Так видно, какие строки реально
показываются на наведении ("<name>, N rounds") и в HUD оружия, без мусора m_Name."""
import os, re
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(ROOT, 'Gunsaw_Data')
UNITY_VER = '2021.1.23f1'

gen = TypeTreeGenerator(UNITY_VER)
gen.load_local_game(ROOT)

def build_tree(nodes):
    return [{
        'm_Level': n.m_Level, 'm_Type': n.m_Type, 'm_Name': n.m_Name,
        'm_MetaFlag': n.m_MetaFlag, 'm_Version': getattr(n, 'm_Version', 1),
        'm_ByteSize': getattr(n, 'm_ByteSize', -1), 'm_TypeFlags': getattr(n, 'm_TypeFlags', 0),
    } for n in nodes]

def script_cls(obj):
    try:
        mb = obj.read(check_read=False)
        sc = mb.m_Script
        if sc:
            ms = sc.read()
            return ms.m_AssemblyName, (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName
    except Exception:
        pass
    return None, None

files = ['globalgamemanagers.assets', 'resources.assets']
files += [f for f in os.listdir(DATA) if re.match(r'^level\d+$', f)]
files += [f for f in os.listdir(DATA) if re.match(r'^sharedassets\d+\.assets$', f)]

tree_cache = {}
rows = {}  # name -> (m_Name, magSize)
for fname in files:
    path = os.path.join(DATA, fname)
    if not os.path.exists(path):
        continue
    try:
        env = UnityPy.load(path)
    except Exception:
        continue
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        asm, cls = script_cls(obj)
        if cls != 'WeaponPreset':
            continue
        key = (asm, cls)
        if key not in tree_cache:
            try:
                tree_cache[key] = build_tree(gen.get_nodes(asm, cls))
            except Exception:
                tree_cache[key] = None
        if tree_cache[key] is None:
            continue
        try:
            data = obj.read_typetree(tree_cache[key])
        except Exception:
            continue
        nm = (data.get('name') or '').strip()
        mnm = (data.get('m_Name') or '').strip()
        mag = data.get('magSize')
        if nm:
            rows[nm] = (mnm, mag)

print("ВСЕГО WeaponPreset с непустым name:", len(rows))
print("%-26s %-18s %s" % ("name (показывается)", "m_Name(ассет)", "magSize"))
for nm in sorted(rows, key=lambda s: (0 if ' ' in s else 1, s.lower())):
    mnm, mag = rows[nm]
    print("%-26s %-18s %s" % (nm, mnm, mag))
