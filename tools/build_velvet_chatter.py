# -*- coding: utf-8 -*-
"""Собирает BepInEx/Translation/ru/Text/chatter_velvet_enemy.txt.
Ключи тянутся ДОСЛОВНО из docs/chatter_by_enemy.txt (с хвостовыми пробелами),
перевод матчится по key.strip(). Дедуп ключа внутри файла (Hissssss! есть в
reload и allyDeath). Печатает MISSING/UNUSED/DUP для контроля."""
import os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "chatter_by_enemy.txt")
OUT = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text", "chatter_velvet_enemy.txt")
SECTION = "=== VelvetEnemy (137 lines) ==="

# Ключи уже заданы базой/др. врагами (глобальный матчинг) — не дублируем.
COVERED = {
    "Prey...", "You've made your last mistake!", "Let's dance!", "Useless!",
    "That's not enough!", "I need... help...",
    "CRAP!", "OUUCH!!", "AAAAHHH!!", "GRAAHHH!!", "MY LIMBS!!!",
}

TR = {
    # --- alert ---
    "I hear them... Writhing...": "Слышу их... как они извиваются...",
    "I know you're here...": "Я знаю, ты здесь...",
    "I can hear yoooou~": "Я тебя слышууу~",
    "Something's in my web...": "Кто-то попался в мою паутину...",
    "Come out... Don't be shy...": "Выходи... не стесняйся...",
    "Don't worry... You're safe here...": "Не бойся... здесь ты в безопасности...",
    "Come to meeee~": "Иди ко мнееее~",
    "Ehehe... Stop hiding...": "Эхехе... хватит прятаться...",
    "Hide and seek?~": "Прячешься?~",
    "I'll play your game...": "Сыграю в твою игру...",
    "I can... help you.": "Я могу... тебе помочь.",
    "Don't be scared... I don't bite...": "Не пугайся... я не кусаюсь...",
    "Ehehe... Come out...": "Эхехе... выходи...",
    "Make this simple...": "Не усложняй...",
    "Where are youuuuu?~": "Ну где же тыыы?~",
    "Don't make this pointless...": "Не тяни понапрасну...",
    "I can smell you...": "Я тебя чую...",
    "You're close...": "Ты совсем рядом...",
    "You're just what I need...": "Ты именно то, что мне нужно...",
    "It's only a matter of time...": "Это лишь вопрос времени...",
    "Don't be scared... I'm here, for you...": "Не бойся... я здесь, ради тебя...",
    # --- spot ---
    "You'll be put to good use...": "Ты мне славно пригодишься...",
    "I'll have my fun with you...": "Я с тобой позабавлюсь...",
    "Perfect...": "Идеально...",
    "Oh~? Who's this?": "Ой~? А это кто тут?",
    "Oh! You're here~": "О! А вот и ты~",
    "It's you...!": "Это ты...!",
    "Let's have FUN!": "Повеселимся!",
    "Ehuhuhu!": "Эхухуху!",
    "You've made, a bad choice.": "Ты сделал, плохой выбор.",
    "Let's play a game, little one...": "Давай поиграем, деточка...",
    "Come to me!": "Иди ко мне!",
    "Aren't you cute?": "Какой же ты милашка?",
    "You look... delicious!": "Выглядишь... аппетитно!",
    "Perfect!...": "Идеально!...",
    "Took you long enough...": "Долго же ты...",
    "There you are...": "Вот ты где...",
    "I've waited for you~": "Я тебя заждалась~",
    "Aren't you just precious?": "Ну разве ты не прелесть?",
    "Make this easy, morsel...": "Не усложняй, кусочек...",
    "All for me~": "Всё мне одной~",
    "You're mine! Mine!": "Ты мой! Мой!",
    "You'll feed my children nicely...": "Ты славно накормишь моих деток...",
    "I'll strip you to the bone!": "Обглодаю тебя до косточек!",
    "You'll do nicely~": "Ты прекрасно подойдёшь~",
    "I want to watch you struggle...": "Хочу смотреть, как ты бьёшься...",
    "Don't resist me, morsel...~": "Не сопротивляйся, кусочек...~",
    # --- reload ---
    "You won't last~": "Долго не протянешь~",
    "It's futile to resist~": "Сопротивляться бесполезно~",
    "Be still for me...": "Замри для меня...",
    "Take this slow, darling~": "Давай помедленнее, дорогуша~",
    "Useless... weapon!": "Никудышное... оружие!",
    "Hissssss!": "Хсссссс!",
    "Damned weapon!": "Проклятое оружие!",
    "You're tough prey...": "А ты добыча не из лёгких...",
    "Playing hard to get?~": "Строишь недотрогу?~",
    "Grrrrr... Work!": "Гррр... работай!",
    "This... damn gun!": "Эта... чёртова пушка!",
    "How do I... There!": "Как это... ага, вот так!",
    "I'll get you! Just... there!": "Я тебя достану! Только... вот так!",
    "You're not going anywhere, morsel!": "Ты никуда не денешься, кусочек!",
    "I hate this thing!": "Ненавижу эту штуку!",
    "Reload... Now...": "Перезарядка... живо...",
    "Reload this...": "Перезарядить это...",
    "Jammed! Again!": "Заклинило! Опять!",
    "I'm not done with you yet!": "Я с тобой ещё не закончила!",
    "Your turn!~": "Твой черёд~",
    "Crumble before me!": "Рассыпься передо мной!",
    "Bleed...": "Истекай кровью...",
    "More...": "Ещё...",
    # --- allyDeath ---
    "Don't worry... You'll be put to good use..": "Не волнуйся... ты славно пригодишься..",
    "Nothing will be wasted!": "Ничего не пропадёт даром!",
    "You like making this hard, dont you?~": "Любишь всё усложнять, да?~",
    "How fun!~": "Как весело!~",
    "Stop struggling...": "Перестань вырываться...",
    "Useless...": "Бесполезно...",
    "All for nothing!": "Всё впустую!",
    "More for me!~": "Мне же больше достанется!~",
    "How regrettable...": "Какая жалость...",
    "There goes, another...": "Вот и, ещё один...",
    "You're good at this!...": "А ты хорош в этом!...",
    "I'm hungry! Die already!": "Я голодна! Да умри уже!",
    "Kill them! Bring them to me!": "Убейте его! Несите ко мне!",
    "Go! Get them!": "Вперёд! Взять его!",
    "Impressive, morsel!": "Впечатляет, кусочек!",
    "Prove yourself to me!~": "Докажи мне, чего ты стоишь!~",
    "You'll suffer for that!": "Ты за это поплатишься!",
    "Need... more...": "Нужно... ещё...",
    "My turn!~": "Мой черёд~",
    "Not... enough...": "Этого... мало...",
    "Inadequate...": "Не годится...",
    "Won't go down without a fight?~": "Без боя не сдаёшься?~",
    "Such a struggle...~": "Сколько в тебе борьбы...~",
    "I'll enjoy peeling your muscle from the bone!": "С удовольствием обдеру твоё мясо с костей!",
    "That won't stop me!": "Это меня не остановит!",
    "Limb from limb!~": "Разорву на кусочки!~",
    # --- death ---
    "My... children...": "Мои... детки...",
    "So hungry...": "Так голодна...",
    "But you...": "Но ты...",
    "Finish... me...": "Добей... меня...",
    "Strong... prey...": "Сильная... добыча...",
    "Not enough...": "Всё... мало...",
    "You... monster...": "Ты... чудовище...",
    "How.... did you?...": "Как... ты смог?...",
    "I... Impressive...": "А ты... впечатляешь...",
    "Such a... waste...": "Какая... потеря...",
    "You... won't... last...": "Ты... долго... не протянешь...",
    "Help me... Help...": "Помогите мне... помогите...",
    "I'm... not... done...": "Я... ещё... не закончила...",
    "I was... too weak...": "Я была... слишком слаба...",
    "No... Not... now...": "Нет... только... не сейчас...",
    "So... strong...": "Такой... сильный...",
    "Hisssss!...": "Хссссс!...",
    "Hisssssss...": "Хсссссс...",
    "Hissss!": "Хсссс!",
    "Hisshshhhh!": "Хсшшшшш!",
    "Auuhh!": "Ауухх!",
    "Auuhhg!": "Ауухг!",
    "Ahhhn!": "Аххн!",
    "Gahhhn!": "Гаххн!",
    # --- ouch ---
    "HHHIIIISSSSSSS!!!": "ХХХИИИСССССС!!!",
    "Nahhhggghhh! You'll PAY!": "Нагхх! ТЫ ЗАПЛАТИШЬ!",
    "YOU'LL PAY! YOU'LL DIE!": "ТЫ ЗАПЛАТИШЬ! ТЫ СДОХНЕШЬ!",
    "HHHHISSSSSS!!! DIIEEEEE!": "ХХХИСССССС!!! СДОХНИИИИ!",
    "Kahahahahahah! HIIISSSSS!": "Кахахахахахах! ХИИИСССС!",
}

CAT_TITLE = {
    "alert": "alert: насторожилась / заманивает (медовая приманка-ложь)",
    "spot": "spot: засекла игрока (вкусняшка-обращения)",
    "reload": "reload: возится с оружием",
    "allyDeath": "allyDeath: смерть союзника — НЕ горюет, радуется лишней «еде», натравливает своих",
    "death": "death: предсмертные (детки/голод/уважение к сильной добыче, женский род)",
    "ouch": "ouch: потеря конечности (садистская ярость + хохот)",
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

# защита: пересечение COVERED и TR = двойной перевод
bad = [k for k in TR if k in COVERED]

out = []
out.append("// Реплики VelvetEnemy (вид Velvet, шрифт Chloe) — ласковая «мамочка»-паучиха-каннибал. ЖЕНСКИЙ РОД.")
out.append("// Спокойная садистка: медовый сюсюкающий тон-приманка, под ним паутина/трапеза/«накормлю деток».")
out.append("// Лор: feminine spider, motherly voice to lure prey to horrible deaths, sadistic cannibal, calm & intelligent in combat.")
out.append("// Покрыто базой/др. (не дублируем): Prey!, You've made your last mistake!, Let's dance!, Useless!, That's not enough!, I need... help...; + 5 воплей база.")
out.append("// Хвостовые пробелы в ключах сохранены дословно. morsel->кусочек, prey->добыча, ~ сохранён (певучий хвостик). Без em-dash.")
out.append("")

emitted = set()
missing, dups = [], []
cur = None
for cat, key in rows:
    if cat != cur:
        cur = cat
        out.append("")
        out.append("// --- " + CAT_TITLE.get(cat, cat) + " ---")
    sk = key.strip()
    if sk in COVERED:
        continue
    if sk in TR:
        if sk in emitted:
            dups.append((cat, key))   # дубль ключа в файле — пишем один раз
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
print("COVERED∩TR (must be empty):", bad)
print("DUP keys (emitted once):", [k for _, k in dups])
print("MISSING:")
for c, k in missing: print("   [%s] %r" % (c, k))
print("UNUSED:")
for k in unused: print("   %r" % k)
print("OUT:", OUT)
