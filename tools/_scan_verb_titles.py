# -*- coding: utf-8 -*-
"""Ищет НАЗВАНИЯ/ЗАГОЛОВКИ (короткие пары EN=RU), переведённые ГЛАГОЛОМ.
Помечает RU, начинающиеся/оканчивающиеся инфинитивом (-ть/-ться/-ти/-чь) или
повелит. формой — кандидаты на «должно быть существительным». Решение по EN — вручную."""
import os, re, glob

ROOT = os.path.join(os.path.dirname(__file__), '..')
TXTDIR = os.path.join(ROOT, 'BepInEx', 'Translation', 'ru', 'Text')
FILES = ['ui_game.txt', 'ui_editor.txt', 'ui_pause.txt', 'ui_settings.txt',
         '_test_menu.txt', 'ui_fixes.txt']

INF = re.compile(r'(ть|ться|ти|чь)$')          # инфинитив
IMP = re.compile(r'(й|йте|и|ите)$')            # грубо: повелит.

def ru_is_verbish(ru):
    w = ru.strip().split()
    if not w:
        return False
    first, last = w[0].lower().strip('.,!?:'), w[-1].lower().strip('.,!?:')
    return bool(INF.search(first) or INF.search(last))

rows = []
for fn in FILES:
    p = os.path.join(TXTDIR, fn)
    if not os.path.exists(p):
        continue
    with open(p, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            s = line.rstrip('\n')
            if not s or s.lstrip().startswith('//') or '=' not in s:
                continue
            k, v = s.split('=', 1)
            if k.lstrip().startswith('r:'):
                continue
            # короткие «заголовки»: без \n, EN <= 32, есть кириллица в RU
            if '\\n' in k or len(k) > 32:
                continue
            if not re.search(r'[А-Яа-яЁё]', v):
                continue
            if ru_is_verbish(v):
                rows.append((fn, i, k, v))

print(f"кандидатов (RU выглядит как глагол): {len(rows)}\n")
for fn, i, k, v in rows:
    print(f"[{fn}:{i}]  {k!r}  =>  {v!r}")
