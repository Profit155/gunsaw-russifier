# -*- coding: utf-8 -*-
"""Собирает BepInEx/Translation/ru/Text/ui_pause.txt — цитаты на экране паузы (GameManager~raw).
Голос: саркастично-ленивый «голос разработчика», местами ломает 4-ю стену (мета-шутки про
сломанный селектор цитат, лор, спам про гарантию). Ключи тянутся ДОСЛОВНО из дампа, перевод
матчится по key.strip(). Вычитает уже занятые ключи и дедупит. Печатает MISSING/UNUSED/DUP."""
import os, io, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "strings_assets.txt")
TEXTDIR = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text")
OUT = os.path.join(TEXTDIR, "ui_pause.txt")
TAG = "GameManager~raw"
HAS_LETTER = re.compile(r"[A-Za-z]")

TAKEN = set()
for fp in glob.glob(os.path.join(TEXTDIR, "*.txt")):
    if os.path.basename(fp) == os.path.basename(OUT):
        continue
    for ln in io.open(fp, encoding="utf-8"):
        if ln.startswith("//") or "=" not in ln:
            continue
        TAKEN.add(ln.split("=", 1)[0].strip())

TR = {
    "And so, time has halted...": "Итак, время замерло...",
    "Believe it or not, paused.": "Веришь или нет, но это пауза.",
    "Breathe in, breathe out.": "Вдох, выдох.",
    "Come on.": "Ну давай.",
    "Could've gone better.": "Бывало и лучше.",
    "Dead already?": "Уже помер?",
    "Escape has been pressed": "Нажат Escape",
    "Get back to work!": "Живо за работу!",
    "Get me a soda.": "Принеси мне газировки.",
    "Get yourself a snack.": "Сходи перекуси.",
    "Go back to playing!": "Возвращайся в игру!",
    "Going back?": "Уже уходишь?",
    "Happy killings!": "Приятных убийств!",
    "Here lie your options": "Здесь покоятся твои опции",
    "How's your day going?": "Как проходит денёк?",
    "Hurry up.": "Поторопись.",
    "I could go for a hot pocket.": "Сейчас бы навернуть горячего чебурека.",
    "I've got time": "У меня есть время",
    "if you're seeing this, i broke the settings quote selector": "если ты это видишь, значит я сломал селектор цитат в настройках",
    "Keep this snowball rollin'.": "Пусть снежный ком катится дальше.",
    "Killing your time?": "Убиваешь время?",
    "Let's do this.": "Погнали.",
    "Let's not idle too long.": "Не будем долго прохлаждаться.",
    "Let's wait": "Подождём",
    "Lunch time?": "Обеденный перерыв?",
    "Nice day, isn't it?": "Хороший денёк, не правда ли?",
    "Oh, come on.": "Да ладно тебе.",
    "Pause menu": "Меню паузы",
    "Personally, not too bad!": "Лично мне вполне неплохо!",
    "Shoot 'em!": "Перестреляй их!",
    "Should've seen your face!": "Видел бы ты своё лицо!",
    "Still alive?": "Ещё живой?",
    "Take a breather.": "Передохни.",
    "Taking a break?": "Решил передохнуть?",
    "That was painful to watch.": "Больно было смотреть.",
    "The clock stopped ticking.": "Часы перестали тикать.",
    "Tick, tock, tick, tock...": "Тик-так, тик-так...",
    "Time is stopped": "Время остановлено",
    "timeScale is zero": "timeScale равен нулю",
    "Tired yet?": "Уже устал?",
    "Too loud?": "Слишком громко?",
    "Too scared?": "Очканул?",
    "Took you long enough.": "Долго же ты.",
    "Try giving THIS a lore explanaton.": "А ВОТ ЭТОМУ попробуй придумать лор.",
    "we have been trying to reach you about your car's extended warranty": "мы пытались связаться с вами по поводу продления гарантии на ваш автомобиль",
    "Working a sweat?": "Аж вспотел?",
    "Writing these is fun": "Писать их весело",
    "You got blood on my suit.": "Ты заляпал мой костюм кровью.",
    "You think you're done?": "Думаешь, ты закончил?",
    "You're not the first one to suck.": "Ты не первый, кто лажает.",
    "Bad!": "Плохо!",
    "Bruh.": "Бро.",
    "Cheater!": "Читер!",
    "Coward.": "Трус.",
    "Dissapointing.": "Разочаровываешь.",
    "Hello!": "Привет!",
    "hi": "здаров",
    "Lazy!!!": "Лентяй!!!",
    "Paused": "Пауза",
    "Waiting.": "Ожидание.",
    # "m%" — формат-строка процента, не переводим (оставляем игре как есть)
}

# собрать ключи дословно из дампа (tag содержит GameManager~raw, без Chatter)
rows = []
for ln in io.open(SRC, encoding="utf-8"):
    ln = ln.rstrip("\n")
    if "\t" not in ln:
        continue
    key, tag = ln.rsplit("\t", 1)
    comps = set(tag.strip("[]").split(","))
    if TAG not in comps or "Chatter~raw" in comps:
        continue
    rows.append(key)

out = [
    "// UI: цитаты на экране паузы (GameManager). Голос саркастично-ленивого «разработчика»,",
    "// местами ломает 4-ю стену (мета-шутки про селектор цитат / лор / спам-гарантию).",
    "// 'm%' (формат процента) и чистые ID не трогаем. Опечатки оригинала (explanaton/Dissapointing) исправлены в RU.",
    "",
]
emitted, missing, dups = set(), [], []
for key in rows:
    sk = key.strip()
    if not HAS_LETTER.search(key):
        continue
    if sk in TAKEN:
        continue
    if sk in TR:
        if sk in emitted:
            dups.append(key)
            continue
        emitted.add(sk)
        out.append(key + "=" + TR[sk])
    else:
        missing.append(key)

io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
unused = [k for k in TR if k not in emitted]
print("source rows:", len(rows))
print("written pairs:", sum(1 for l in out if "=" in l and not l.startswith("//")))
print("DUP:", dups)
print("MISSING:", missing)
print("UNUSED:", unused)
print("OUT:", OUT)
