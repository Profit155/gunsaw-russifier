# -*- coding: utf-8 -*-
"""Собирает chatter_dune_enemy.txt и chatter_shelly_enemy.txt.
Оба вида НЕМЫЕ по лору: Dune — тупой жук («Nothing goes on in their head»),
все реплики пустое '...'; Shelly — скорпион без рта («lack a mouth, mute»),
«говорит» пунктуацией-эмоциями и стрёкотом хитина. Переводим ТОЛЬКО токены с
буквами (пунктуация одинакова в любом языке — оставляем игре как есть).
Ключи тянутся ДОСЛОВНО (хвостовые пробелы), перевод матчится по key.strip()."""
import os, io, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "chatter_by_enemy.txt")
TEXTDIR = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text")

# занятые ключи всех прочих chatter-файлов
def load_taken(exclude):
    taken = set()
    for fp in glob.glob(os.path.join(TEXTDIR, "chatter_*.txt")):
        if os.path.basename(fp) == exclude:
            continue
        with io.open(fp, encoding="utf-8") as f:
            for ln in f:
                if ln.startswith("//") or "=" not in ln:
                    continue
                taken.add(ln.split("=", 1)[0].strip())
    return taken

def section(name):
    with io.open(SRC, encoding="utf-8") as f:
        lines = f.read().split("\n")
    started = False; rows = []
    for ln in lines:
        if ln.strip() == name:
            if not started: started = True; continue
        if started and ln.startswith("=== "): break
        if started and ln.startswith("["):
            rb = ln.index("]"); rows.append((ln[1:rb], ln[rb + 2:]))
    return rows

HAS_LETTERS = re.compile(r"[A-Za-z]")

def build(outname, section_name, header, tr):
    out = os.path.join(TEXTDIR, outname)
    taken = load_taken(outname)
    rows = section(section_name)
    bad = [k for k in tr if k in taken]
    lines = list(header)
    emitted = set(); missing = []; dups = []
    cur = None
    for cat, key in rows:
        if cat != cur:
            cur = cat
            lines.append("")
            lines.append("// --- " + cat + " ---")
        sk = key.strip()
        if not HAS_LETTERS.search(key):
            continue  # чистая пунктуация — отдаём игре как есть
        if sk in taken:
            continue
        if sk in tr:
            if sk in emitted:
                dups.append((cat, key)); continue
            emitted.add(sk)
            lines.append(key + "=" + tr[sk])
        else:
            missing.append((cat, key))
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    unused = [k for k in tr if k not in emitted]
    print(f"\n=== {outname} ===")
    print("source rows:", len(rows))
    print("written pairs:", sum(1 for l in lines if "=" in l and not l.startswith("//")))
    print("TAKEN∩TR (must be empty):", bad)
    print("DUP (emitted once):", [k for _, k in dups])
    print("MISSING:", missing)
    print("UNUSED:", unused)

# ---------- Dune ----------
TR_DUNE = {
    "Gh...": "Гх...",
}
HEAD_DUNE = [
    "// Реплики DuneEnemy (вид Dune, шрифт Gelatik) — водяной жук-камуфляж, тупая голодная машина.",
    "// Лор: 'Nothing goes on in their head', не способен к эмпатии, движим лишь голодом (вплоть до каннибализма).",
    "// ПРАКТИЧЕСКИ НЕМОЙ: 5 из 6 реплик — пустое '...' (тупой взгляд), их НЕ трогаем. Переводим только предсмертный хрип.",
]
build("chatter_dune_enemy.txt", "=== DuneEnemy (6 lines) ===", HEAD_DUNE, TR_DUNE)

# ---------- Shelly ----------
TR_SHELLY = {
    # стрёкот/предсмертные щелчки хитина — кириллизуем (как Velvet Хсссс / Icke Граахгг)
    "Krrk...": "Крк...",
    "Krkrkrkrkrkrr...": "Кркркркркркрр...",
    "Ksshhh...": "Кшшш...",
    "Krrrk...": "Кррк...",
    # игривый звуко-ряд chItter/chAtter/chUtter (меняется гласная) + сырный панчлайн cheddar
    "*chitter*": "*цик-цик*",
    "*chatter*": "*цак-цак*",
    "*chutter*": "*цук-цук*",
    "*cheddar*": "*чеддер*",
}
HEAD_SHELLY = [
    "// Реплики ShellyEnemy (вид Shelly, шрифт Chloe) — светящийся скорпион-арахнид, ЖЕНСКИЙ род по лору.",
    "// Лор: нет рта (питается радиацией), поэтому НЕМАЯ; при этом спокойная, умная, с приятным поведением.",
    "// 'Говорит' пунктуацией-эмоциями (?, !!!, ?!?!) и стрёкотом хитина. Пунктуацию НЕ трогаем (универсальна).",
    "// Звуко-ряд *chitter/chatter/chutter* (вокальная игра и-а-у) -> *цик-цак-цук*; *cheddar* (сырная шутка) -> *чеддер*.",
    "// Хвостовые пробелы в ключах Ksshhh... / Krrrk... сохранены дословно.",
]
build("chatter_shelly_enemy.txt", "=== ShellyEnemy (35 lines) ===", HEAD_SHELLY, TR_SHELLY)
