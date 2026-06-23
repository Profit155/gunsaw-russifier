# -*- coding: utf-8 -*-
"""Собирает перевод объектов редактора уровней (docs/wf_editor_out/*.json) -> ui_editor.txt."""
import os, io, glob, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTDIR = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text")
OUT = os.path.join(TEXTDIR, "ui_editor.txt")

# уже переведённое (для проверки коллизий)
TAKEN = set()
for fp in glob.glob(os.path.join(TEXTDIR, "*.txt")):
    if os.path.basename(fp) == os.path.basename(OUT):
        continue
    for ln in io.open(fp, encoding="utf-8"):
        if ln.startswith("//") or "=" not in ln:
            continue
        TAKEN.add(ln.split("=", 1)[0].strip())

records = []
for fp in sorted(glob.glob(os.path.join(ROOT, "docs", "wf_editor_out", "out_*.json"))):
    records += json.load(io.open(fp, encoding="utf-8"))

seen = set()
pairs, dup, collide, emdash = [], [], [], []
for r in records:
    key = r.get("key", "")
    ru = (r.get("ru") or "").strip()
    if not key or not ru:
        continue
    if key in seen:
        dup.append(key); continue
    seen.add(key)
    if key.strip() in TAKEN:
        collide.append(key); continue
    if "—" in ru:
        emdash.append((key, ru))
    pairs.append((key, ru))

lines = ["// Объекты и описания редактора уровней Gunsaw (workflow Opus). Стиль: функциональный, без em-dash."]
lines.append("")
for key, ru in pairs:
    lines.append(key + "=" + ru)
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

print("записей прочитано:", len(records))
print("пар записано:", len(pairs), "->", OUT)
print("проверки: dup=%d collide=%d em-dash=%d" % (len(dup), len(collide), len(emdash)))
if emdash:
    for k, ru in emdash[:20]:
        print("   em-dash:", repr(ru[:70]))
