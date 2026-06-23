# -*- coding: utf-8 -*-
"""Дамп ВСЕХ world-space TMP-текстов (класс TMPro.TextMeshPro, НЕ ...UGUI) по всем
уровням Gunsaw_Data/levelN. Для каждого: уровень, имя GameObject, размер бокса
(RectTransform m_SizeDelta), кегль/autosize/wrap/overflow, и сам текст (EN).
Это «коробочки на уровнях», в которые не влезает русский."""
import os, json, glob, re
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(ROOT, 'Gunsaw_Data')

gen = TypeTreeGenerator('2021.1.23f1')
gen.load_local_game(ROOT)

def build_tree(nodes):
    return [{'m_Level': n.m_Level, 'm_Type': n.m_Type, 'm_Name': n.m_Name,
             'm_MetaFlag': n.m_MetaFlag, 'm_Version': getattr(n, 'm_Version', 1),
             'm_ByteSize': getattr(n, 'm_ByteSize', -1),
             'm_TypeFlags': getattr(n, 'm_TypeFlags', 0)} for n in nodes]

def pid(pptr):
    for a in ('m_PathID', 'path_id'):
        if hasattr(pptr, a):
            return getattr(pptr, a)
    return None

OVERFLOW = {0: 'Overflow', 1: 'Ellipsis', 2: 'Masking', 3: 'Truncate',
            4: 'ScrollRect', 5: 'Page', 6: 'Linked'}

cache = {}
rows = []
levels = sorted(glob.glob(os.path.join(DATA, 'level*')),
                key=lambda p: int(re.search(r'level(\d+)$', p).group(1)) if re.search(r'level(\d+)$', p) else 999)
for lvl in levels:
    if not re.search(r'level\d+$', lvl):
        continue
    name = os.path.basename(lvl)
    try:
        env = UnityPy.load(lvl)
    except Exception as e:
        print('skip', name, e); continue
    objmap = {o.path_id: o for o in env.objects}
    # индекс RectTransform по GameObject path_id (для размеров бокса)
    rt_by_go = {}
    for o in env.objects:
        if o.type.name in ('RectTransform',):
            try:
                t = o.read()
                rt_by_go[pid(t.m_GameObject)] = t
            except Exception:
                pass
    for o in env.objects:
        if o.type.name != 'MonoBehaviour':
            continue
        try:
            mb = o.read(check_read=False)
            ms = mb.m_Script.read()
            cls = (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName
            if cls != 'TMPro.TextMeshPro':      # ТОЛЬКО мировой 3D-текст
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
            t = (data.get('m_text') or '').strip()
            if not t:
                continue
            go_pid = pid(mb.m_GameObject)
            go = objmap.get(go_pid)
            goname = go.read().m_Name if go else '?'
            rt = rt_by_go.get(go_pid)
            sd = getattr(rt, 'm_SizeDelta', None) if rt else None
            w = round(getattr(sd, 'x', 0), 1) if sd else None
            h = round(getattr(sd, 'y', 0), 1) if sd else None
            rows.append({
                'level': name,
                'go': goname,
                'w': w, 'h': h,
                'fontSize': round(data.get('m_fontSize', 0), 1),
                'autoSize': bool(data.get('m_enableAutoSizing', False)),
                'fsMin': round(data.get('m_fontSizeMin', 0), 1),
                'fsMax': round(data.get('m_fontSizeMax', 0), 1),
                'wrap': bool(data.get('m_enableWordWrapping', False)),
                'overflow': OVERFLOW.get(data.get('m_overflowMode', 0), str(data.get('m_overflowMode', 0))),
                'text': t,
            })
        except Exception:
            pass

out = os.path.join(ROOT, 'docs', '_world_text_dump.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
print(f"world-space TextMeshPro объектов: {len(rows)}  ->  {out}")
# сводка по уровням
from collections import Counter
c = Counter(r['level'] for r in rows)
for k in sorted(c, key=lambda x: int(re.search(r'\d+', x).group())):
    print(f"  {k}: {c[k]}")
