# -*- coding: utf-8 -*-
"""Сопоставить КОРНЕВОЙ префаб врага -> speciesName, поднявшись по трансформам от Body."""
import os, re, UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

ROOT = r'C:\Users\User\Downloads\gunsaw-demo-win'
DATA = os.path.join(ROOT, 'Gunsaw_Data')
gen = TypeTreeGenerator('2021.1.23f1'); gen.load_local_game(ROOT)

def build_tree(nodes):
    return [{'m_Level': n.m_Level,'m_Type': n.m_Type,'m_Name': n.m_Name,
             'm_MetaFlag': n.m_MetaFlag,'m_Version': getattr(n,'m_Version',1),
             'm_ByteSize': getattr(n,'m_ByteSize',-1),'m_TypeFlags': getattr(n,'m_TypeFlags',0)} for n in nodes]

files = ['globalgamemanagers.assets','resources.assets']
files += [f for f in os.listdir(DATA) if re.match(r'^level\d+$', f)]
files += [f for f in os.listdir(DATA) if re.match(r'^sharedassets\d+\.assets$', f)]

cache = {}

def go_transform(go):
    for comp in getattr(go, 'm_Components', []) or []:
        try:
            c = comp.read()
            if c.object_reader.type.name in ('Transform', 'RectTransform'):
                return c
        except Exception:
            continue
    return None

def root_name(go):
    """Поднимаемся по m_Father до корня, возвращаем имя корневого GameObject."""
    seen = 0
    name = getattr(go, 'm_Name', '(?)')
    tr = go_transform(go)
    while tr is not None and seen < 64:
        seen += 1
        father = getattr(tr, 'm_Father', None)
        if father is None or getattr(father, 'path_id', 0) == 0:
            break
        try:
            tr = father.read()
            pgo = tr.m_GameObject.read()
            name = pgo.m_Name
        except Exception:
            break
    return name

rows = {}   # root prefab name -> set speciesName
for fname in files:
    path = os.path.join(DATA, fname)
    if not os.path.exists(path): continue
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour': continue
        try:
            mb = obj.read(check_read=False); ms = mb.m_Script.read()
            cls = (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName
            if cls != 'BodyScript': continue
            key = (ms.m_AssemblyName, cls)
            if key not in cache:
                try: cache[key] = build_tree(gen.get_nodes(*key))
                except Exception: cache[key] = None
            if cache[key] is None: continue
            data = obj.read_typetree(cache[key])
            sp = (data.get('speciesName') or '').strip() or '(empty)'
            go = mb.m_GameObject.read()
            rn = root_name(go)
            rows.setdefault(rn, set()).add(sp)
        except Exception:
            continue

print('=== Корневой префаб -> speciesName ===')
for go in sorted(rows):
    print('  %-24s %s' % (go, ', '.join(sorted(rows[go]))))
print('итого корней:', len(rows))
