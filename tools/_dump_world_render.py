# -*- coding: utf-8 -*-
"""Для world-space TMP (TMPro.TextMeshPro) собирает РЕНДЕР-состояние, важное для
перекрытия геометрией: материал (имя/шейдер/renderQueue/_ZTestMode/_ZWrite),
MeshRenderer (sortingLayerID/sortingOrder), и локальный/мировой Z.
Это евиденс к «текст проваливается за трубу»."""
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

def pid(p):
    for a in ('m_PathID', 'path_id'):
        if hasattr(p, a):
            return getattr(p, a)
    if isinstance(p, dict):
        return p.get('m_PathID')
    return None

def matfloats(mat):
    """{имя: значение} из m_SavedProperties.m_Floats — там _ZTestMode/_ZWrite/_Stencil*."""
    out = {}
    try:
        sp = mat.m_SavedProperties
        for kv in sp.m_Floats:
            try:
                k = kv[0].m_Name if hasattr(kv[0], 'm_Name') else kv[0]
                v = kv[1]
            except Exception:
                k, v = kv.first, kv.second
            out[str(k)] = round(float(v), 1)
    except Exception:
        pass
    return out

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
    except Exception:
        continue
    objmap = {o.path_id: o for o in env.objects}
    # MeshRenderer и Transform по GameObject
    mr_by_go, tr_by_go = {}, {}
    for o in env.objects:
        if o.type.name == 'MeshRenderer':
            try:
                r = o.read(); mr_by_go[pid(r.m_GameObject)] = r
            except Exception: pass
        elif o.type.name in ('Transform', 'RectTransform'):
            try:
                t = o.read(); tr_by_go[pid(t.m_GameObject)] = t
            except Exception: pass

    def world_z(go_pid):
        z = 0.0; seen = set()
        cur = go_pid
        while cur in tr_by_go and cur not in seen:
            seen.add(cur)
            t = tr_by_go[cur]
            lp = t.m_LocalPosition
            z += round(getattr(lp, 'z', getattr(lp, 'Z', 0)), 3)
            f = pid(t.m_Father)
            if not f: break
            ft = objmap.get(f)
            if ft is None: break
            try: cur = pid(ft.read().m_GameObject)
            except Exception: break
        return round(z, 2)

    for o in env.objects:
        if o.type.name != 'MonoBehaviour':
            continue
        try:
            mb = o.read(check_read=False)
            ms = mb.m_Script.read()
            cls = (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName
            if cls != 'TMPro.TextMeshPro':
                continue
            key = (ms.m_AssemblyName, cls)
            if key not in cache:
                try: cache[key] = build_tree(gen.get_nodes(*key))
                except Exception: cache[key] = None
            if not cache[key]:
                continue
            data = o.read_typetree(cache[key])
            t = (data.get('m_text') or '').strip()
            if not t:
                continue
            go_pid = pid(mb.m_GameObject)
            # материал: сначала с MeshRenderer (фактический), иначе m_sharedMaterial у TMP
            matname = shader = None; rq = None; zt = zw = None
            mr = mr_by_go.get(go_pid)
            mat_obj = None
            if mr is not None:
                try:
                    mats = mr.m_Materials
                    if mats:
                        mp = pid(mats[0])
                        if mp in objmap: mat_obj = objmap[mp].read()
                except Exception: pass
            if mat_obj is None:
                mp = pid(data.get('m_sharedMaterial'))
                if mp in objmap:
                    try: mat_obj = objmap[mp].read()
                    except Exception: pass
            if mat_obj is not None:
                matname = getattr(mat_obj, 'm_Name', None)
                rq = getattr(mat_obj, 'm_CustomRenderQueue', None)
                fl = matfloats(mat_obj)
                zt = fl.get('_ZTestMode'); zw = fl.get('_ZWrite')
                try:
                    sh = mat_obj.m_Shader
                    sp = pid(sh)
                    if sp in objmap: shader = objmap[sp].read().m_ParsedForm.m_Name
                except Exception: pass
            sl = so = None
            if mr is not None:
                sl = getattr(mr, 'm_SortingLayerID', getattr(mr, 'm_SortingLayer', None))
                so = getattr(mr, 'm_SortingOrder', None)
            rows.append({
                'level': name, 'text': t[:50],
                'mat': matname, 'shader': shader, 'renderQueue': rq,
                'ZTest': zt, 'ZWrite': zw,
                'sortLayer': sl, 'sortOrder': so,
                'wz': world_z(go_pid),
            })
        except Exception:
            pass

out = os.path.join(ROOT, 'docs', '_world_render_dump.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
print(f"{len(rows)} world-TMP ->  {out}\n")
import collections
print('материалы:', collections.Counter(r['mat'] for r in rows).most_common(12))
print('шейдеры  :', collections.Counter(r['shader'] for r in rows).most_common(8))
print('ZTest    :', collections.Counter(r['ZTest'] for r in rows))
print('renderQ  :', collections.Counter(r['renderQueue'] for r in rows))
print('sortOrder:', collections.Counter(r['sortOrder'] for r in rows))
print('sortLayer:', collections.Counter(r['sortLayer'] for r in rows))
