# -*- coding: utf-8 -*-
"""Переразбивает RU-значения world-табличек по ширине EN-оригинала, чтобы русский
текст не вытекал. Бюджет ширины = самая длинная строка EN у этой таблички.
Правит ТОЛЬКО строки, что превышают бюджет; авторские переносы/пустые строки
(абзацы) сохраняются. Затрагивает лишь ключи, реально присутствующие в world-дампе
(класс TMPro.TextMeshPro) и переполняющие. Пишет ui_game.txt на месте.

Запуск:  python _rewrap_world_signs.py          # dry-run (только показать)
         python _rewrap_world_signs.py --apply  # записать ui_game.txt
"""
import json, os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
UIGAME = os.path.join(ROOT, 'BepInEx', 'Translation', 'ru', 'Text', 'ui_game.txt')
NL = '\\n'   # литерал backslash-n (как в .txt и ключах)

rows = json.load(open(os.path.join(ROOT, 'docs', '_world_text_dump.json'), encoding='utf-8'))
def to_literal(s): return s.replace('\n', NL)
def has_cyr(s): return bool(re.search('[А-Яа-яЁё]', s))

# EN world-таблички -> бюджет ширины (самая длинная строка EN)
budget = {}
for r in rows:
    en = to_literal(r['text'])
    emax = max((len(x) for x in en.split(NL)), default=0)
    budget[en] = max(budget.get(en, 0), emax)

def wrap_line(line, width):
    """Жадный перенос одной строки по словам в строки <= width. Длинные слова не ломаем."""
    words = line.split(' ')
    out, cur = [], ''
    for w in words:
        if cur == '':
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += ' ' + w
        else:
            out.append(cur); cur = w
    if cur != '':
        out.append(cur)
    return out

OVER = 6          # переносим строку только если вылезает хотя бы на столько симв
MIN_WORDS = 3     # ...и если в ней >=3 слова (иначе перенос рвёт фразу из 2 слов уродливо)

def rewrap(ru, width):
    """Переразбить RU: ужимаем только строки, что СУЩЕСТВЕННО шире width и из >=3 слов.
    Пустые строки/короткие лейблы/двусловные хвосты сохраняем как есть."""
    res = []
    for ln in ru.split(NL):
        if len(ln) - width >= OVER and len(ln.strip().split(' ')) >= MIN_WORDS:
            res.extend(wrap_line(ln, width))
        else:
            res.append(ln)
    return NL.join(res)

# читаем ui_game.txt, строим правки
changes = []
out_lines = []
for raw in open(UIGAME, encoding='utf-8'):
    line = raw.rstrip('\n')
    if not line or line.startswith('//') or line.startswith('r:') or '=' not in line:
        out_lines.append(raw); continue
    k, v = line.split('=', 1)
    b = budget.get(k)
    # пропускаем мелкие лейблы (узкий бюджет) и длинные гэг-списки (>12 строк)
    if b and b >= 8 and has_cyr(v) and v.count(NL) <= 12 and any(len(x) - b >= 6 for x in v.split(NL)):
        nv = rewrap(v, b)
        if nv != v:
            changes.append((k, v, nv, b))
            out_lines.append(k + '=' + nv + '\n')
            continue
    out_lines.append(raw)

print(f"переразбито табличек: {len(changes)}\n")
for k, v, nv, b in changes:
    print(f"  [budget {b}] {k!r}")
    print(f"      old: {v!r}")
    print(f"      new: {nv!r}")

if '--apply' in sys.argv:
    with open(UIGAME, 'w', encoding='utf-8', newline='') as f:
        f.writelines(out_lines)
    print(f"\n>>> записано в {UIGAME}")
else:
    print("\n(dry-run; для записи добавь --apply)")
