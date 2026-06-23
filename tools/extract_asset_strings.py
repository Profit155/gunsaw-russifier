# -*- coding: utf-8 -*-
"""Task 12: дамп всех строковых полей из сцен и ассетов игры (UnityPy).
MonoBehaviour'ы читаются по тайптри, сгенерированным из Managed DLL,
так что достаются и m_text TMP-компонентов, и массивы реплик в скриптах."""
import io
import os
import re
import sys
import traceback

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(ROOT, 'Gunsaw_Data')
OUT = os.path.join(ROOT, 'docs', 'strings_assets.txt')

UNITY_VER = '2021.1.23f1'

gen = TypeTreeGenerator(UNITY_VER)
gen.load_local_game(ROOT)  # подхватывает Gunsaw_Data/Managed/*.dll


def build_tree(nodes):
    """Узлы генератора — чужой для UnityPy класс; конвертируем в list[dict],
    дерево UnityPy соберёт сам."""
    return [
        {
            'm_Level': n.m_Level,
            'm_Type': n.m_Type,
            'm_Name': n.m_Name,
            'm_MetaFlag': n.m_MetaFlag,
            'm_Version': getattr(n, 'm_Version', 1),
            'm_ByteSize': getattr(n, 'm_ByteSize', -1),
            'm_TypeFlags': getattr(n, 'm_TypeFlags', 0),
        }
        for n in nodes
    ]

# (строка) -> set(классов, где встретилась)
found = {}


def walk(value, cls):
    if isinstance(value, str):
        s = value.strip()
        if len(s) >= 2 and re.search(r'[A-Za-z]', s):
            found.setdefault(s, set()).add(cls)
    elif isinstance(value, dict):
        for v in value.values():
            walk(v, cls)
    elif isinstance(value, (list, tuple)):
        for v in value:
            walk(v, cls)


def raw_strings(data, cls):
    """Fallback для объектов, чьё тайптри не совпало: ищем в сырых байтах
    строки Unity-формата (int32 длина + UTF-8, выравнивание по 4)."""
    i, n = 0, len(data)
    while i + 4 <= n:
        ln = int.from_bytes(data[i:i + 4], 'little')
        if 2 <= ln <= 4096 and i + 4 + ln <= n:
            try:
                s = data[i + 4:i + 4 + ln].decode('utf-8')
            except UnicodeDecodeError:
                s = None
            if s and all(c in '\n\t' or ord(c) >= 32 for c in s):
                walk(s, cls + '~raw')
                i = (i + 4 + ln + 3) & ~3
                continue
        i += 4


def script_info(obj):
    try:
        mb = obj.read(check_read=False)
        script = mb.m_Script
        if script:
            ms = script.read()
            return ms.m_AssemblyName, (ms.m_Namespace + '.' if ms.m_Namespace else '') + ms.m_ClassName
    except Exception:
        pass
    return None, None


files = ['globalgamemanagers.assets', 'resources.assets']
files += [f for f in os.listdir(DATA) if re.match(r'^level\d+$', f)]
files += [f for f in os.listdir(DATA) if re.match(r'^sharedassets\d+\.assets$', f)]

tree_cache = {}
stats = {'mb': 0, 'ok': 0, 'fail': 0, 'ta': 0}

for fname in files:
    path = os.path.join(DATA, fname)
    if not os.path.exists(path):
        continue
    try:
        env = UnityPy.load(path)
    except Exception:
        print('load fail:', fname)
        continue
    for obj in env.objects:
        try:
            tname = obj.type.name
            if tname == 'TextAsset':
                ta = obj.read()
                walk(str(ta.m_Script), 'TextAsset:' + ta.m_Name)
                stats['ta'] += 1
            elif tname == 'MonoBehaviour':
                stats['mb'] += 1
                asm, cls = script_info(obj)
                if not cls:
                    continue
                key = (asm, cls)
                if key not in tree_cache:
                    try:
                        tree_cache[key] = build_tree(gen.get_nodes(asm, cls))
                    except Exception:
                        tree_cache[key] = None
                nodes = tree_cache[key]
                if nodes is None:
                    stats['fail'] += 1
                    raw_strings(obj.get_raw_data(), cls)
                    continue
                try:
                    data = obj.read_typetree(nodes)
                except Exception:
                    stats['fail'] += 1
                    raw_strings(obj.get_raw_data(), cls)
                    continue
                walk(data, cls)
                stats['ok'] += 1
        except Exception:
            stats['fail'] += 1

print('MonoBehaviours:', stats['mb'], 'parsed:', stats['ok'],
      'failed:', stats['fail'], 'TextAssets:', stats['ta'])

# отсортировать: сначала фразы с пробелами, потом одиночные слова
entries = sorted(found.items(), key=lambda kv: (0 if ' ' in kv[0] else 1, kv[0].lower()))
with io.open(OUT, 'w', encoding='utf-8') as fh:
    for s, classes in entries:
        flat = s.replace('\\', '\\\\').replace('\n', '\\n')
        fh.write('%s\t[%s]\n' % (flat, ','.join(sorted(classes))))
print('strings:', len(entries), '->', OUT)
