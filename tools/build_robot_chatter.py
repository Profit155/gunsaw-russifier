# -*- coding: utf-8 -*-
"""Собирает BepInEx/Translation/ru/Text/chatter_robot_enemy.txt (вид G4A / RobotEnemy).
Голос — машинный охранный лог КАПСОМ. Ключи тянутся ДОСЛОВНО, перевод по key.strip().
Занятые ключи (глобальный матчинг) вычисляются динамически. Чистая пунктуация
('...') не переводится. Дедуп внутри файла: OUCH (death+ouch), CEASE (spot+ouch)."""
import os, io, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "chatter_by_enemy.txt")
TEXTDIR = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text")
OUT = os.path.join(TEXTDIR, "chatter_robot_enemy.txt")
SECTION = "=== RobotEnemy (70 lines) ==="
HAS_LETTERS = re.compile(r"[A-Za-z]")

TAKEN = set()
for fp in glob.glob(os.path.join(TEXTDIR, "chatter_*.txt")):
    if os.path.basename(fp) == os.path.basename(OUT):
        continue
    with io.open(fp, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("//") or "=" not in ln:
                continue
            TAKEN.add(ln.split("=", 1)[0].strip())

TR = {
    # --- alert ---
    "AUDIO ANOMALY": "АУДИО-АНОМАЛИЯ",
    "INVESTIGATING": "ВЕДУ ПРОВЕРКУ",
    "COMBAT READY": "К БОЮ ГОТОВ",
    "READY": "ГОТОВ",
    "COME OUT": "ВЫХОДИ",
    "I HEAR YOU": "СЛЫШУ ТЕБЯ",
    "ANOMALY": "АНОМАЛИЯ",
    "AUDIO ABNORMALITY": "АУДИО-ОТКЛОНЕНИЕ",
    "POSSIBLE BREAK-IN": "ВОЗМОЖНО ПРОНИКНОВЕНИЕ",
    "PROBLEM": "ПРОБЛЕМА",
    "POSSIBLE ISSUE": "ВОЗМОЖНАЯ НЕПОЛАДКА",
    "WHAT WAS THAT": "ЧТО ЭТО БЫЛО",
    # --- spot ---
    "ANOMALY DETECTED": "АНОМАЛИЯ ОБНАРУЖЕНА",
    "VISUAL ANOMALY": "ВИЗУАЛЬНАЯ АНОМАЛИЯ",
    "VISUAL ABNORMALITY": "ВИЗУАЛЬНОЕ ОТКЛОНЕНИЕ",
    "PERPETRATOR": "НАРУШИТЕЛЬ",
    "ENEMY": "ВРАГ",
    "COMBAT": "БОЙ",
    "FIGHT": "АТАКА",
    "STOP": "СТОЯТЬ",
    "PUT YOUR PAWS UP": "ЛАПЫ ВВЕРХ",
    "CEASE": "ПРЕКРАТИТЬ",
    "END": "КОНЕЦ",
    "CONSIDERABLE PROBLEM": "СЕРЬЁЗНАЯ ПРОБЛЕМА",
    # --- reload ---
    "RELOADING": "ПЕРЕЗАРЯДКА",
    "REFRESHING": "ОБНОВЛЕНИЕ",
    "COVER ME": "ПРИКРОЙТЕ",
    "CALLING FOR BACKUP": "ВЫЗЫВАЮ ПОДКРЕПЛЕНИЕ",
    "CODE 4": "КОД 4",
    "STOP FIGHTING": "ПРЕКРАТИ СОПРОТИВЛЕНИЕ",
    "AMMO WASTED": "ПАТРОНЫ ВПУСТУЮ",
    "DOWN THE DRAIN": "НАСМАРКУ",
    "DIE": "УМРИ",
    "I CANNOT FULFILL MY DUTY": "НЕ МОГУ ВЫПОЛНИТЬ СВОЙ ДОЛГ",
    "TOUGH": "КРЕПИСЬ",
    "I AM RELOADING": "Я ПЕРЕЗАРЯЖАЮСЬ",
    # --- allyDeath ---
    "ALLY DOWN": "СОЮЗНИК ПАЛ",
    "TEAMMATE DOWN": "НАПАРНИК ВЫБЫЛ",
    "WE ARE LOSING": "МЫ ПРОИГРЫВАЕМ",
    "NEED BACKUP": "НУЖНО ПОДКРЕПЛЕНИЕ",
    "UNFAIR": "НЕЧЕСТНО",
    "MEAN": "ПОДЛО",
    "DO NOT": "НЕ НАДО",
    "YOU MONSTER": "ТЫ ЧУДОВИЩЕ",
    "HOW COULD YOU": "КАК ТЫ МОГ",
    "SQUADMATE DOWN": "БОЕЦ ОТРЯДА ВЫБЫЛ",
    "PUSH": "НАСТУПАТЬ",
    "WEAKLING": "СЛАБАК",
    # --- death ---
    "*BUZZ*": "*БЗЗЗ*",
    "CRITICAL ERROR": "КРИТИЧЕСКАЯ ОШИБКА",
    "SHUTTING DOWN": "ОТКЛЮЧЕНИЕ",
    "MAJOR TRAUMA DETECTED": "ОБНАРУЖЕНА ТЯЖЁЛАЯ ТРАВМА",
    "CIRCUITRY DAMAGED": "СХЕМЫ ПОВРЕЖДЕНЫ",
    "I AM DEAD": "Я МЁРТВ",
    "*SPARKS*": "*ИСКРЫ*",
    "OUCH": "ОЙ",
    "CONNECTION SEVERED": "СВЯЗЬ ОБОРВАНА",
    "SEVERE DAMAGE": "ТЯЖЁЛЫЕ ПОВРЕЖДЕНИЯ",
    "ENDING COMBAT": "ЗАВЕРШЕНИЕ БОЯ",
    # --- ouch ---
    "CRITICAL": "КРИТИЧНО",
    "CRITICAL HIT": "КРИТИЧЕСКОЕ ПОПАДАНИЕ",
    "I AM DISFIGURED": "Я ИЗУРОДОВАН",
    "REPAIR NEEDED": "ТРЕБУЕТСЯ РЕМОНТ",
    "CORE DAMAGED": "ЯДРО ПОВРЕЖДЕНО",
    "THAT HURT": "БОЛЬНО",
    "CRAP": "ЧЁРТ",
    "LIMB LOST": "ПОТЕРЯ КОНЕЧНОСТИ",
}

CAT_TITLE = {
    "alert": "alert: скан, засёк аудио-аномалию",
    "spot": "spot: визуальный контакт, охранные команды",
    "reload": "reload: перезарядка + команды/подколки",
    "allyDeath": "allyDeath: союзник пал — глюк детской эмоции у дефектного юнита",
    "death": "death: отключается (пустое '...' оставлено игре как есть)",
    "ouch": "ouch: потеря конечности (OUCH/CEASE уже выше — дедуп)",
}

with io.open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

started = False
rows = []
for ln in lines:
    if ln.strip() == SECTION:
        if not started:
            started = True
            continue
    if started and ln.startswith("=== "):
        break
    if started and ln.startswith("["):
        rb = ln.index("]")
        rows.append((ln[1:rb], ln[rb + 2:]))

bad = [k for k in TR if k in TAKEN]

out = []
out.append("// Реплики RobotEnemy (вид G4A / Robot, шрифт Retro Gaming) — охранный робот-силовик линейки G4A.")
out.append("// Лор (BodyScript): 'Pile of steel / Missing soul' — груда стали без души. КАПС = машинный дисплей/лог.")
out.append("// Голос: сухой техно-лог терминала; у дефектных юнитов прорывается детская эмоция (UNFAIR/MEAN/YOU MONSTER).")
out.append("// Пунктуацию ('...') НЕ трогаем (универсальна). Звуко-эффекты в звёздочках выводятся текстом — переводим (*БЗЗЗ*/*ИСКРЫ*).")
out.append("// PUT YOUR PAWS UP->ЛАПЫ ВВЕРХ (в оригинале именно paws — враги пушистые). Дедуп: OUCH (death+ouch), CEASE (spot+ouch).")

emitted = set()
missing, dups = [], []
cur = None
for cat, key in rows:
    if cat != cur:
        cur = cat
        out.append("")
        out.append("// --- " + CAT_TITLE.get(cat, cat) + " ---")
    sk = key.strip()
    if not HAS_LETTERS.search(key):
        continue  # чистая пунктуация — игре как есть
    if sk in TAKEN:
        continue
    if sk in TR:
        if sk in emitted:
            dups.append((cat, key))
            continue
        emitted.add(sk)
        out.append(key + "=" + TR[sk])
    else:
        missing.append((cat, key))

with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")

unused = [k for k in TR if k not in emitted]
print("source rows:", len(rows))
print("written pairs:", sum(1 for l in out if "=" in l and not l.startswith("//")))
print("TAKEN∩TR (must be empty):", bad)
print("DUP keys (emitted once):", [k for _, k in dups])
print("MISSING:", missing)
print("UNUSED:", unused)
print("OUT:", OUT)
