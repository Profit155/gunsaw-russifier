# -*- coding: utf-8 -*-
"""Собирает корпус для QA-ревью перевода: все осмысленные EN=RU пары из НЕ-chatter
файлов перевода. Исключает: комментарии, идентичные (EN==RU, намеренно англ.),
чистые имена видов/персонажей/уровней. Печатает JSON в docs/_review_corpus.json."""
import os, json, re, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
TXT = os.path.join(ROOT, 'BepInEx', 'Translation', 'ru', 'Text')

FILES = ['ui_game.txt', 'ui_editor.txt', 'ui_pause.txt',
         'ui_settings.txt', '_test_menu.txt', 'ui_fixes.txt']

# Чистые имена (исключаем как «имена»). EN и RU формы.
NAMES = set("""
Experiment Orange Milky Leapy Chompy Roza Voyager Baron Chik Crystal Velvet Icke
Shelly Dune Albino Abomination Robot Carver Avelyn Angler G4-A G4A
Эксперимент Оранж Орандж Милки Липи Чомпи Роза Вояджер Барон Чик Кристалл Вельвет
Велвет Ике Шелли Дюн Альбинос Абоминация Робот Карвер Эвелин Англер
""".split())

def is_pure_name(k, v):
    kk, vv = k.strip(), v.strip()
    # одиночное имя по любую сторону
    if vv in NAMES or kk in NAMES:
        return True
    # список имён через \n (напр. "Experiment\nOrange\n...")
    parts = [p.strip() for p in re.split(r'\\n', vv) if p.strip()]
    if parts and all(p in NAMES for p in parts):
        return True
    return False

rows = []
stats = {'total': 0, 'comment': 0, 'identity': 0, 'name': 0, 'kept': 0}
for fn in FILES:
    p = os.path.join(TXT, fn)
    if not os.path.exists(p):
        continue
    with open(p, encoding='utf-8') as f:
        for i, raw in enumerate(f, 1):
            line = raw.rstrip('\n')
            s = line.strip()
            if not s:
                continue
            if s.startswith('//') or s.startswith('#'):
                stats['comment'] += 1
                continue
            if '=' not in line:
                continue
            stats['total'] += 1
            k, v = line.split('=', 1)
            if k == v:
                stats['identity'] += 1
                continue
            if is_pure_name(k, v):
                stats['name'] += 1
                continue
            is_regex = k.lstrip().startswith('r:')
            stats['kept'] += 1
            rows.append({
                'file': fn, 'line': i,
                'en': k, 'ru': v,
                'en_len': len(k), 'ru_len': len(v),
                'is_regex': is_regex,
                'kind': 'long' if len(k) > 120 else ('regex' if is_regex else 'short'),
            })

out = os.path.join(ROOT, 'docs', '_review_corpus.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

by_kind = {}
for r in rows:
    by_kind[r['kind']] = by_kind.get(r['kind'], 0) + 1
sys.stderr.write(f"[corpus] kept={stats['kept']} (long={by_kind.get('long',0)} "
                 f"short={by_kind.get('short',0)} regex={by_kind.get('regex',0)}) | "
                 f"excluded: identity={stats['identity']} name={stats['name']} "
                 f"comment={stats['comment']} | total_eq_lines={stats['total']}\n")
