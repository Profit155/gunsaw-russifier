# -*- coding: utf-8 -*-
"""Собирает BepInEx/Translation/ru/Text/chatter_icke_enemy.txt.
Ключи тянутся ДОСЛОВНО из docs/chatter_by_enemy.txt (с хвостовыми пробелами),
перевод матчится по key.strip(). Уже занятые другими файлами ключи (глобальный
матчинг XUnity) вычисляются динамически и пропускаются. Печатает MISSING/UNUSED/DUP."""
import os, io, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "chatter_by_enemy.txt")
TEXTDIR = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text")
OUT = os.path.join(TEXTDIR, "chatter_icke_enemy.txt")
SECTION = "=== IckeEnemy (197 lines) ==="

# Занятые ключи из всех прочих chatter-файлов (глобальный матчинг) — не дублируем.
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
    "Was' that?": "Чё это было?",
    "Just me?": "Это я, что ли?",
    "Come on, coward!": "Ну давай, ссыкло!",
    "Whatever you are, you'll meet your end.": "Кто б ты ни был, тебе крышка.",
    "Silence down ova' there!": "А ну, тихо там!",
    "Loud as always.": "Шумят, как всегда.",
    "I'm spoiling for a fight.": "Руки чешутся подраться.",
    "Come out, prick!": "Вылазь, козёл!",
    "C'mon! Let's go!": "Давай! Погнали!",
    "This'll be fun...": "Будет весело...",
    "Let's go, hot stuff!": "Ну давай, красавчик!",
    "You think you can hide??": "Думаешь, спрячешься??",
    "Come on out, pansy!": "Вылазь, неженка!",
    "Tch...": "Тц...",
    "I can hear you, y'know!": "Я ж тебя слышу!",
    "Hiding won't work!": "Прятки не помогут!",
    "Pansy...": "Неженка...",
    "You scared? Ha!": "Зассал? Ха!",
    "Haha! You're hiding!": "Хаха! Прячешься!",
    "I can't wait for this...": "Не терпится уже...",
    "I'm made for this... Come on!": "Я для этого создан... Давай!",
    "Don't make me wait!": "Не заставляй меня ждать!",
    "I know what I heard!": "Я точно что-то слышал!",
    "Let's go, tough guy!": "Ну давай, крутыш!",
    "You think you're sly?": "Думаешь, ты хитрый?",
    "Raise your dukes!": "Поднимай кулаки!",
    "I'm gettin' impatient...": "Я уже теряю терпение...",
    "Ha! HIDE!": "Ха! ПРЯЧЬСЯ!",
    "I've got a bad itch for this...": "Аж кулаки зудят...",
    "I've waited... long enough.": "Я ждал... достаточно долго.",
    "Finger's on the trigger...": "Палец на курке...",
    "Just gotta wait...": "Надо только подождать...",
    # --- spot ---
    "Die, prick!": "Сдохни, козёл!",
    "Fight me like a man!": "Дерись как мужик!",
    "I aint scared!": "Да не боюсь я!",
    "Gotcha!": "Попался!",
    "You stand not a chance!": "У тебя ни шанса!",
    "Let's do this!": "Ну, понеслась!",
    "You'll bleed!": "Будешь кровью харкать!",
    "You're dead!": "Ты труп!",
    "Let's go, pansy!": "Ну давай, неженка!",
    "I'll break your legs!": "Ноги переломаю!",
    "I'm stronger, faster, and better!": "Я сильнее, быстрее и круче!",
    "Ha! You? Pathetic!": "Ха! Ты? Жалкий!",
    "I'll tear your throat out!": "Глотку тебе вырву!",
    "You'll regret showing yourself!": "Пожалеешь, что высунулся!",
    "Should've stayed hiding!": "Сидел бы и не высовывался!",
    "Think you're tough??": "Думаешь, ты крутой??",
    "Finally! I've waited long enough!": "Наконец-то! Заждался уже!",
    "I've waited for you!": "Я тебя заждался!",
    "Look who shows their face!": "Гляньте, кто высунулся!",
    "If it isn't you! Ha!": "Кого я вижу! Ха!",
    "Ha! Let's fight, me and you!": "Ха! Давай, ты и я!",
    "I was getting impatient!": "Я уж терпение терял!",
    "Tsk tsk tsk...": "Ай-яй-яй...",
    "There you are!": "Вот ты где!",
    "I bet you're weak!": "Спорим, ты слабак!",
    "You're nothing!": "Ты пустое место!",
    "This'll be easy!": "Это будет легко!",
    "The hell!?": "Какого чёрта!?",
    "Huh?!": "Чё?!",
    "You'll regret this, moron!": "Пожалеешь, придурок!",
    # --- reload ---
    "Crap! Wait!": "Блин! Стой!",
    "Okay, actually give me a second...": "Так, дай-ка мне секунду...",
    "Hey, you! Wait!": "Эй, ты! Подожди!",
    "Where is this god damn...": "Да где эта чёртова...",
    "I don't need help!": "Мне не нужна помощь!",
    "Insurance won't cover this!": "Страховка это не покроет!",
    "This is easy!": "Да это легко!",
    "You call this a fight?!": "И это ты называешь дракой?!",
    "Try harder!": "Старайся лучше!",
    "Weak! Useless!": "Слабак! Никчёмный!",
    "Think you're safe?!": "Думаешь, ты в безопасности?!",
    "I'm not done with you, meat bag!": "Я с тобой ещё не закончил, мешок с мясом!",
    "Stay still, moron!": "Стой смирно, придурок!",
    "Not a challenge!": "Тоже мне, противник!",
    "You're making this look easy!": "С тобой даже слишком легко!",
    "Weak! Haha!": "Слабак! Хаха!",
    "God damn, this gun...": "Да чёрт бы побрал эту пушку...",
    "You're terrible! Ha!": "Ты ужасен! Ха!",
    "You like this!?": "Нравится!?",
    "You're pathetic!": "Ты жалок!",
    "Are you even trying!?": "Ты вообще стараешься!?",
    "I ain't even working a sweat!": "Я даже не вспотел!",
    "C'mon, fight harder!": "Ну давай, дерись активнее!",
    "I'll wipe that look off your face!": "Я сотру эту ухмылку с твоей рожи!",
    "Run, pansy, run!": "Беги, неженка, беги!",
    "Haha! This is fun!": "Хаха! Весело же!",
    "Reloading this!": "Перезаряжаю!",
    "Getting ammo!": "Беру патроны!",
    "Useless gun!": "Бесполезная пушка!",
    "Can't shoot this!": "Не стреляет, зараза!",
    "Bah! Ammo!": "Тьфу! Патроны!",
    "Not fair!": "Так нечестно!",
    # --- allyDeath ---
    "Fool!": "Дурак!",
    "Loser!": "Лох!",
    "NO!!": "НЕТ!!",
    "Formidable.": "Внушает.",
    "Better up there than here!": "На небе ему спокойнее!",
    "You were such a mouse!": "Ну и мышь же ты был!",
    "Didn't like 'em anyway.": "Да он мне и не нравился.",
    "Okay...": "Ну ладно...",
    "PRICK!!!": "КОЗЁЛ!!!",
    "STOP!!!": "ХВАТИТ!!!",
    "Try NOT getting shot next time!": "В следующий раз постарайся НЕ словить пулю!",
    "Out of the way!": "С дороги!",
    "You weren't cut for the work!": "Ты не годился для этого дела!",
    "Are you serious?!": "Ты серьёзно?!",
    "Damn, that's gotta hurt...": "Чёрт, это должно быть больно...",
    "Not worth it, pal!": "Оно того не стоило, дружище!",
    "Shoulda' moved!": "Надо было увернуться!",
    "I won't go as easy!": "Я так легко не сдамся!",
    "You're really pissing me off!": "Ты меня реально бесишь!",
    "Damn! That's tough!": "Чёрт! А он крепкий!",
    "You'll regret this!": "Ты об этом пожалеешь!",
    "Moron! Move!": "Придурок! Шевелись!",
    "MOVE!": "ДВИГАЙ!",
    "You all fight like morons!": "Вы все деретесь как придурки!",
    "That's just pathetic!": "Это просто жалко!",
    "So much for that!": "Вот тебе и всё!",
    "Seriously! What the hell!": "Серьёзно! Какого чёрта!",
    "There's no excuse for that!": "Этому нет оправдания!",
    "Tch!... Watch and learn!": "Тц!... Смотри и учись!",
    "Tch... Useless.": "Тц... Бесполезно.",
    "Meatshield! MOVE!": "Мясной щит! ДВИГАЙ!",
    "You guys need help!?": "Вам, ребята, помощь нужна!?",
    "Have no fear, Icke is here!": "Не бойтесь, Ике тут как тут!",
    # --- death ---
    "OUCH!": "АЙ!",
    "OW!": "ОЙ!",
    "Damnit..": "Чёрт..",
    "Jeepers...": "Ё-моё...",
    "My skull...": "Мой череп...",
    "Headache...": "Башка трещит...",
    "I... Concede...": "Я... Сдаюсь...",
    "Eepy...": "Баиньки...",
    "Enough!...": "Хватит!...",
    "That's... A lotta holes...": "Это... куча дырок...",
    "Kyaahhg!": "Кьяагх!",
    "Fuuuhh...": "Фууух...",
    "Avenge... me!": "Отомстите... за меня!",
    "Noo! Gahh!": "Неет! Гах!",
    "Gahh! Hnnn..": "Гах! Хнн..",
    "You're... strong...": "А ты... силён...",
    "You... got me...": "Ты... достал меня...",
    "You'll... pay...": "Ты... заплатишь...",
    "Don't... forget... me...": "Не забывайте... меня...",
    "It... it hurts...": "Мне... больно...",
    "I'll... gahh...": "Я ещё... гах...",
    "I'm not... hnng...": "Я не... хнн...",
    "How... did you...": "Как... ты смог...",
    "Not... fair...": "Так... нечестно...",
    "Ch... Cheater...": "Ч... Читер...",
    "The... hell?...": "Какого... чёрта?...",
    "I can't... get up...": "Я не могу... встать...",
    "Graahhhggg!": "Граахгг!",
    "Ahhhhggnn!": "Аххгнн!",
    "No! My ribs!": "Нет! Мои рёбра!",
    "I'm... bleeding...": "Я... истекаю кровью...",
    "Tch... typical...": "Тц... как всегда...",
    "Owwh! Ahhg!": "Оуу! Ахг!",
    "I... lost...": "Я... проиграл...",
    "Help... me...": "Помогите... мне...",
    "I can't... feel my legs...": "Я не чувствую... ног...",
}

CAT_TITLE = {
    "alert": "alert: заметил/звереет, выманивает прячущегося труса (понты-задира)",
    "spot": "spot: засёк игрока (мачизм, оскорбления)",
    "reload": "reload: возится с пушкой + сыплет понты",
    "allyDeath": "allyDeath: союзник пал — не горюет, хамит трупу, звереет, гонит своих в бой",
    "death": "death: предсмертные (боль, понты до конца, обвиняет в читерстве, мужской род)",
    "ouch": "ouch: потеря конечности (полностью покрыто базой)",
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

# защита: пересечение TAKEN и TR = двойной перевод занятого ключа
bad = [k for k in TR if k in TAKEN]

out = []
out.append("// Реплики IckeEnemy (вид Icke, шрифт Gelatik) — агрессивный кролик-мужик, гопник-боксёр-задира. МУЖСКОЙ РОД.")
out.append("// Лор: powerful kicking legs, weak upper body (bandaged); injuries ENRAGE him (adrenaline); low intelligence,")
out.append("//   overestimates himself, acts before thinking; selfish bully, 'Asshole. Leporidae.' Понты, мачизм, trash-talk.")
out.append("// Лексикон: coward->ссыкло, prick->козёл, pansy->неженка, tough guy->крутыш, moron->придурок, meat bag->мешок с мясом.")
out.append("// Покрыто базой/др. (не дублируем): I heard something..., Huh?, God..., Come on!, Come and get it!, Come to me и die!,")
out.append("//   I'll find you!, HEY!, No you're not!, Show me what you got!, Enemy!, You're over!, This ends here!, Show me a good fight!,")
out.append("//   Bring it, tough guy!, Reloading!, I'm out!, Give me a moment!, I need a moment!, CRAP!, This thing's jammed!,")
out.append("//   That's not enough!, I hate this thing!, Man down!, Dude!, This isn't over!, Hngh...., + 5 воплей ouch (база).")
out.append("// Хвостовые пробелы в ключах сохранены дословно. Без em-dash. Имя в кричалке транслитерировано -> Ике (рифма-задор).")

emitted = set()
missing, dups = [], []
cur = None
for cat, key in rows:
    if cat != cur:
        cur = cat
        out.append("")
        out.append("// --- " + CAT_TITLE.get(cat, cat) + " ---")
    sk = key.strip()
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
print("TAKEN keys total:", len(TAKEN))
print("TAKEN∩TR (must be empty):", bad)
print("DUP keys (emitted once):", [k for _, k in dups])
print("MISSING:")
for c, k in missing: print("   [%s] %r" % (c, k))
print("UNUSED:")
for k in unused: print("   %r" % k)
print("OUT:", OUT)
