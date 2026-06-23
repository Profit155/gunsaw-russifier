# -*- coding: utf-8 -*-
"""Находит в Gunsaw_Data/level8 объект с текстом Bee Movie: GameObject, путь в
иерархии (через скан Transform по m_GameObject) и приблизительную мировую позицию."""
import os, sys
import UnityPy

ROOT = os.path.join(os.path.dirname(__file__), '..')
LEVEL = os.path.join(ROOT, 'Gunsaw_Data', 'level8')
NEEDLE = b'known laws of aviation'

env = UnityPy.load(LEVEL)
objmap = {o.path_id: o for o in env.objects}

def pid(pptr):
    for a in ('m_PathID', 'path_id'):
        if hasattr(pptr, a):
            return getattr(pptr, a)
    return None

def vec(v):
    for ax in (('x', 'y', 'z'), ('X', 'Y', 'Z')):
        if all(hasattr(v, a) for a in ax):
            return [round(getattr(v, a), 1) for a in ax]
    if isinstance(v, dict):
        return [round(v.get(a, v.get(a.upper(), 0)), 1) for a in ('x', 'y', 'z')]
    return [0.0, 0.0, 0.0]

# индекс: GameObject path_id -> Transform-объект
tr_by_go = {}
for o in env.objects:
    if o.type.name in ('Transform', 'RectTransform'):
        try:
            t = o.read()
            tr_by_go[pid(t.m_GameObject)] = o
        except Exception:
            pass

# 1. MonoBehaviour с текстом
mb_obj = next((o for o in env.objects if o.type.name == 'MonoBehaviour'
               and NEEDLE in (o.get_raw_data() or b'')), None)
if not mb_obj:
    print('НЕ НАЙДЕНО'); sys.exit(1)
mb = mb_obj.read(check_read=False)
go_pid = pid(mb.m_GameObject)
go = objmap[go_pid].read()
print('GameObject:', repr(go.m_Name))
try:
    ms = mb.m_Script.read()
    print('Script:', (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName)
except Exception:
    pass

# полный текст (длина) — для подтверждения
raw = mb_obj.get_raw_data()
idx = raw.find(NEEDLE)
print('Текст начинается с offset', idx, '| размер объекта (байт):', len(raw))

# 2. путь вверх + позиция
names, pos = [], [0.0, 0.0, 0.0]
cur_go = go_pid
local0 = None
seen = set()
while cur_go in tr_by_go and cur_go not in seen:
    seen.add(cur_go)
    t = tr_by_go[cur_go].read()
    lp = vec(t.m_LocalPosition)
    if local0 is None:
        local0 = lp
    for i in range(3):
        pos[i] += lp[i]
    gname = objmap[cur_go].read().m_Name if cur_go in objmap else '?'
    names.append(gname)
    fpid = pid(t.m_Father)
    if not fpid:
        break
    # m_Father -> Transform; его GameObject = следующий уровень
    ft = objmap.get(fpid)
    if ft is None:
        break
    cur_go = pid(ft.read().m_GameObject)

print('Локальная позиция Text(TMP):', local0)
print('Прибл. мировая позиция:', [round(p, 1) for p in pos])
print('Иерархия (объект -> корень):')
print('  ' + '  ->  '.join(repr(n) for n in names))
