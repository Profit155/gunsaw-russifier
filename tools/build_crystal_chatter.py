# -*- coding: utf-8 -*-
"""Собирает BepInEx/Translation/ru/Text/chatter_crystal_enemy.txt.
Ключи тянутся ДОСЛОВНО из docs/chatter_by_enemy.txt (с хвостовыми пробелами),
перевод матчится по key.strip(). Печатает MISSING/UNUSED для контроля."""
import os, sys, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "chatter_by_enemy.txt")
OUT = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text", "chatter_crystal_enemy.txt")

# Ключи уже заданы базой/др. врагами (глобальный матчинг) — не дублируем.
COVERED = {
    "You're done for!", "I'll crush you!", "This won't stop me!",
    "CRAP!", "OUUCH!!", "AAAAHHH!!", "GRAAHHH!!", "MY LIMBS!!!",
}

TR = {
    # --- alert ---
    "Alright, who did it?!": "Так, кто это сделал?!",
    "Who needs being set straight?": "Кому тут мозги вправить?",
    "Don't make me cranky!": "Не доводи меня!",
    "Dont try me! I'm armed!": "Не лезь ко мне! Я вооружена!",
    "I don't like the sound of this.": "Не нравятся мне эти звуки.",
    "Don't push me...": "Не нарывайся...",
    "This can't get worse.": "Хуже уже не будет.",
    "I'm not dealing with this.": "Не буду я с этим возиться.",
    "Another issue? Really?": "Опять проблемы? Серьёзно?",
    "Who's gonna show up now?!": "И кто там ещё припёрся?!",
    "There goes my peace and quiet...": "Ну вот, и покою конец...",
    "I'll handle this!...": "Я разберусь!...",
    "Someone dropped something.": "Кто-то что-то уронил.",
    "I don't like this.": "Мне это не нравится.",
    "Like that'll scare me!": "Будто меня это напугает!",
    "Bah, whatever!...": "Ай, да пофиг!...",
    "Hmph!...": "Хмф!...",
    "Guhh... More noise!": "Гхх... опять шум!",
    "More trouble...": "Опять заморочки...",
    "Gah... more things to deal with.": "Гах... опять куча дел.",
    "What's that!? Trouble...": "Что там!? Заморочки...",
    "Nehh... Not my problem.": "Не-е... не моя проблема.",
    "Who's asking to get knocked?": "Кто напрашивается на тумаки?",
    "Ghhn... loud noises.": "Гхн... шумно как.",
    "Grrrrrhh... Not today...": "Грррх... только не сегодня...",
    "You won't get me this time...": "В этот раз не возьмёшь...",
    "Grrrrrh...": "Грррх...",
    "Okay... now, where...": "Так... ну и где...",
    # --- spot ---
    "Hey! Meanie!": "Эй, вредина!",
    "Okay, here we go!": "Так, понеслась!",
    "I'm not afraid of you!": "Я тебя не боюсь!",
    "Looks like I found trouble!": "Кажись, вот и неприятности!",
    "I'll crush you like a brick!": "Раздавлю тебя, как кирпич!",
    "Found you! Now, c'mere!": "Нашла! А ну иди сюда!",
    "You! Come here!": "Ты! Иди сюда!",
    "I'll shut you down!": "Я тебя уделаю!",
    "You and me, here and now :33": "Ты и я, здесь и сейчас :33",
    "GET OVER HERE!": "А НУ ИДИ СЮДА!",
    "You're getting knocked!": "Сейчас получишь!",
    "You're in aboslute trouble!": "Ты влип по полной!",
    "You're not getting past me, idiot!": "Мимо меня не пройдёшь, придурок!",
    "I found the problem!": "Нашла проблему!",
    "There you are! C'mere!": "Вот ты где! А ну сюда!",
    "I found something tough!": "Нашла что-то крепкое!",
    "Okay, this won't be easy!": "Так, легко не будет!",
    "You're in TROUBLE!": "Ну ты ВЛИП!",
    "Bring it, tough guy!": "Ну давай, крутой!",
    "Im stopping you HERE AND NOW!": "Я тебя остановлю ПРЯМО ЗДЕСЬ И СЕЙЧАС!",
    "Think you're tough? I'll fold you!": "Думаешь, ты крутой? Я тебя сложу!",
    "I'll fold you like a folding chair!": "Сложу тебя, как раскладной стул!",
    "Found the meanie!": "Нашла вредину!",
    "You'll pay for what you've done!": "Ты заплатишь за то, что натворил!",
    "HEY! GET EM!": "ЭЙ! ХВАТАЙ ЕГО!",
    "Oh, YOU'VE DONE IT NOW!": "Ну ВСЁ, ДОИГРАЛСЯ!",
    "Hey! Jerk! SURRENDER!": "Эй! Придурок! СДАВАЙСЯ!",
    # --- reload ---
    "Stupid, stupid gun!": "Тупая, тупая пушка!",
    "Just you wait! You're done for!": "Ну погоди! Тебе конец!",
    "Someone help me!": "Кто-нибудь, помогите!",
    "Reload... reload...": "Перезарядка... перезарядка...",
    "You think you scare me!?": "Думаешь, я тебя боюсь?!",
    "Hold them back! I've got this...": "Сдержите его! Я сейчас...",
    "C'mon... gun... work!": "Ну же... пушка... работай!",
    "Bullets... go in here!": "Патроны... суём вот сюда!",
    "I'll toss you like a handbag!": "Зашвырну тебя, как сумочку!",
    "This is a problem!": "Так, это проблема!",
    "Not good... Uh oh....": "Плохо дело... ой-ёй....",
    "No! My bullets! Grrhhh!": "Нет! Мои патроны! Гррх!",
    "Grrrrrrh... stupid!": "Гррррх... тупица!",
    "Grrrrrrrhh... work!": "Гррррх... работай!",
    "Why don't these things go faster!": "Ну чего так медленно-то!",
    "Surrender while you can, idiot!": "Сдавайся, пока можешь, придурок!",
    "Meanie!": "Вредина!",
    "You're not getting away!": "Не уйдёшь!",
    "Stay there! Away from me!": "Стой там! Не подходи!",
    "Get back, idiot!": "Назад, придурок!",
    "Get off! Grrrh": "Отвали! Гррх",
    # --- allyDeath ---
    "I'm afraid of you!": "Я тебя боюсь!",
    "Nevermind.": "Неважно.",
    "Hey- HEY! NO!": "Эй- ЭЙ! НЕТ!",
    "GET BACK UP! PLEASE!": "ВСТАВАЙ! ПРОШУ!",
    "GRRRRRRH! YOU'LL PAY!": "ГРРРРХ! ТЫ ЗАПЛАТИШЬ!",
    "No!... NO! NO!": "Нет!... НЕТ! НЕТ!",
    "WHAT THE HELL?!": "ДА КАКОГО ЧЁРТА?!",
    "TAKE ME INSTEAD!": "ЗАБЕРИ ЛУЧШЕ МЕНЯ!",
    "No- NO! MY DAMN FRIEND!": "Нет- НЕТ! ДРУЖИЩЕ МОЙ!",
    "HOW COULD YOU! YOU!...": "КАК ТЫ МОГ! ТЫ!...",
    "I'll CRUSH YOU! GRRNNHH!": "Я ТЕБЯ РАЗДАВЛЮ! ГРРНХ!",
    "YOU'VE DONE IT NOW!": "ТЕПЕРЬ ТЫ ДОПРЫГАЛСЯ!",
    "HOW COULD YOU!": "КАК ТЫ МОГ!",
    "I- HATE THIS! NO!": "Я- НЕНАВИЖУ ЭТО! НЕТ!",
    "NO! PLEASE!": "НЕТ! ПРОШУ!",
    "No... WHY!": "Нет... ЗА ЧТО!",
    "WHY ARE YOU DOING THIS!?": "ЗАЧЕМ ТЫ ЭТО ДЕЛАЕШЬ?!",
    "Hey! HEY! GET UP!": "Эй! ЭЙ! ВСТАВАЙ!",
    "Hey- No! You meanie!": "Эй- Нет! Вредина ты!",
    "I'LL KILL YOU!": "Я ТЕБЯ УБЬЮ!",
    "YOU- GRRRRRRH!": "ТЫ- ГРРРРХ!",
    "FFFFFFFFFFUHHH!": "Ф-Ф-Ф-Ф-Ф-УХХ!",
    "No no no no NO!": "Нет нет нет нет НЕТ!",
    "I can't handle this!": "Я этого не вынесу!",
    "This isn't WORKING!": "Так НИЧЕГО НЕ ВЫХОДИТ!",
    # --- death ---
    "Guhhhghhh!": "Гухх-гхх!",
    "Gaahhhhnnn!... No...": "Га-аххннн!... Нет...",
    "Grrrhssh.... Ahhg...": "Гррхщщ.... Ахг...",
    "You... idiot...": "Ты... придурок...",
    "You.... gahhh...": "Ты.... гахх...",
    "I've... failed... again...": "Опять... я всё... провалила...",
    "Why... me?...": "За что... мне?...",
    "Wh.... Whoops...": "Ой... упс...",
    "I've... fallen...": "Я... упала...",
    "Can't... get... up...": "Не могу... встать...",
    "I'm not- done with you...": "Я с тобой... не закончила...",
    "But I'm... not...": "Но я же... не...",
    "I was... never...": "Я так... и не...",
    "Hrrnnhhg!... Help...": "Хррнхг!... Помогите...",
    "N-No... you...": "Н-нет... ты...",
    "Meanie...": "Вредина...",
    "G...Get... away...": "У... уходите...",
    "Too... much...": "Это... слишком...",
    "It... It hurts...": "Это... Это больно...",
    "Forgive me...": "Простите... меня...",
    "Grrnnhhhgg!": "Грннхг!",
    "Gaaahhhhh!": "Га-а-аххх!",
    # --- ouch ---
    "MUSHROOM!": "ГРИБОЧЕК!",
    "WHAT THE HELL! GAAAHHHHH!": "ДА КАКОГО ЧЁРТА! ГА-А-АХХХ!",
    "THAT HURTS! ALOT! LIKE! OH MY GOD!": "БОЛЬНО! ОЧЕНЬ! ПРЯМ! О БОЖЕ МОЙ!",
    "MY CARDIOVASCULAR SYSTEM!!": "МОЯ СЕРДЕЧНО-СОСУДИСТАЯ СИСТЕМА!!",
    "HOLY CRYSTALS!": "СВЯТЫЕ КРИСТАЛЛЫ!",
}

CAT_TITLE = {
    "alert": "alert: насторожилась (ещё не видит игрока)",
    "spot": "spot: засекла игрока",
    "reload": "reload: возится с оружием / огрызается",
    "allyDeath": "allyDeath: смерть союзника — маска цундэрэ слетает",
    "death": "death: предсмертные (мягкое нутро наружу, женский род)",
    "ouch": "ouch: потеря конечности (комично-абсурдные)",
}

# --- читаем ПЕРВУЮ секцию CrystalEnemy дословно ---
with io.open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

started = False
rows = []  # (cat, verbatim_key)
for ln in lines:
    if ln.strip() == "=== CrystalEnemy (136 lines) ===":
        if not started:
            started = True
            continue
    if started and ln.startswith("=== "):
        break
    if started and ln.startswith("["):
        rb = ln.index("]")
        cat = ln[1:rb]
        key = ln[rb + 2:]  # после "] "
        rows.append((cat, key))

used = set()
missing = []
out = []
out.append("// Реплики CrystalEnemy (вид Crystal, шрифт Gelatik) — цундэрэ: ворчливая туповатая задира-ящерка,")
out.append("// крутая снаружи (реслинг-понты, «вредина», :33), мягкая внутри. ЖЕНСКИЙ РОД.")
out.append("// Лор: кристаллочешуйчатая рогатая ящерица, неуклюжа с оружием, длинный липкий язык; маска слетает на смерть союзника.")
out.append("// Покрыто базой/др. (не дублируем): You're done for!, I'll crush you! (Orange); This won't stop me! (Chik); CRAP!/OUUCH!!/AAAAHHH!!/GRAAHHH!!/MY LIMBS!!! (база).")
out.append("// Хвостовые пробелы в ключах сохранены дословно. \"meanie\" -> \"вредина\" единым словом во всех категориях.")
out.append("")

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
        used.add(sk)
        out.append(key + "=" + TR[sk])
    else:
        missing.append((cat, key))

with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")

unused = [k for k in TR if k not in used]
print("rows in source:", len(rows))
print("written pairs:", sum(1 for l in out if "=" in l and not l.startswith("//")))
print("MISSING (in source, no translation):")
for c, k in missing:
    print("   [%s] %r" % (c, k))
print("UNUSED (translation never matched a source key):")
for k in unused:
    print("   %r" % k)
print("OUT:", OUT)
