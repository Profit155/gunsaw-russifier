# -*- coding: utf-8 -*-
"""Собирает промежуточные результаты перевода в финальные файлы.
- translate -> BepInEx/Translation/ru/Text/ui_game.txt (секции по тегу-источнику)
- doubtful  -> docs/translation_review.txt (на проверку человеком)
- skip      -> только счётчики
Проверяет: коллизии с уже переведённым (TAKEN), дубли ключей, em-dash в переводе."""
import os, io, glob, json, re
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTDIR = os.path.join(ROOT, "BepInEx", "Translation", "ru", "Text")
OUT = os.path.join(TEXTDIR, "ui_game.txt")
REVIEW = os.path.join(ROOT, "docs", "translation_review.txt")

# key -> tag из батчей
key2tag = {}
for fp in glob.glob(os.path.join(ROOT, "docs", "wf_batches", "*.tsv")):
    for ln in io.open(fp, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if "\t" not in ln:
            continue
        k, t = ln.rsplit("\t", 1)
        key2tag[k] = t

# уже переведённое
TAKEN = set()
for fp in glob.glob(os.path.join(TEXTDIR, "*.txt")):
    if os.path.basename(fp) == os.path.basename(OUT):
        continue
    for ln in io.open(fp, encoding="utf-8"):
        if ln.startswith("//") or "=" not in ln:
            continue
        TAKEN.add(ln.split("=", 1)[0].strip())

# читаем все out-файлы
records = []
bad_json = []
for fp in sorted(glob.glob(os.path.join(ROOT, "docs", "wf_out", "out_*.json"))):
    try:
        data = json.load(io.open(fp, encoding="utf-8"))
        for r in data:
            records.append(r)
    except Exception as e:
        bad_json.append((os.path.basename(fp), str(e)))

# doubtful разводим по правилам: треки и отладку оставляем (skip),
# остальное с непустым переводом — принимаем в перевод (отдельная секция).
TRACK_TAGS = {"MusicClip", "NewMusicManager"}
DEBUG_TAGS = {"ErrorDetector~raw"}
# ники/теги авторов — оставляем английскими (решение пользователя)
NAME_SKIP = {"Blood by Awez", "Orsoniks", "Pistol adwewe", "Canndc", "TheRealon3"}
# ручные правки перевода (убрать em-dash и т.п.)
RU_OVERRIDE = {
    "0% no blood spawns, 100% is almost all particles create splats.\\nDefault 90%":
        "При 0% кровь не появляется, при 100% почти все частицы оставляют брызги.\\nПо умолчанию 90%",
    "Downdrops": "Даундропс",  # название миссии — транслит (было оставлено англ. в doubtful)
    # Leapy(Agile and fragile) и Milky(Dexterous and frail) оба давали "Ловкий и хрупкий" -> юзер
    # видел "одинаковое описание у Липи/Милки". Дифференцируем свап-описание Милки:
    "Dexterous and frail": "Проворный и хлипкий",
    # swapText по запасу смен (swapAmount): 2->ALPHA(голубой, полный запас), 1->LAST(белый), 0->OUT(красный).
    # "Alpha" = состояние "обе смены доступны / полный запас", НЕ имя и НЕ "первая".
    # Было "СМЕНИТЬ АЛЬФУ"(неверно)->"ПЕРВАЯ СМЕНА"(слабо). Решение юзера: передать "полный запас".
    "SWAP ALPHA": "ПОЛНЫЙ ЗАПАС",
}

# глобальные правки имён видов (решение пользователя): транслитерация ближе к ориг. произношению
NAME_FIX = [("Ориндж", "Оранж"), ("Велвет", "Вельвет")]
def fix_name(ru):
    for a, b in NAME_FIX:
        ru = ru.replace(a, b)
    return ru

def tagset(key):
    return set(key2tag.get(key, "").strip("[]").split(","))

translate, doubtful, skip = [], [], []
extra = []  # доразобранное из doubtful -> в перевод
emdash, collide, dup = [], [], []
seen = set()
for r in records:
    key = r.get("key", "")
    v = r.get("verdict", "")
    ru = (r.get("ru") or "").strip()
    note = (r.get("note") or "").strip()
    if key in seen:
        dup.append(key)
        continue
    seen.add(key)
    if key.strip() in TAKEN:
        collide.append(key)
        continue
    ru = fix_name(RU_OVERRIDE.get(key, ru))
    if v == "translate":
        if "—" in ru:
            emdash.append((key, ru))
        translate.append((key, ru))
    elif v == "doubtful":
        comps = tagset(key)
        if comps & TRACK_TAGS:          # музыкальные треки — оставляем английскими
            skip.append(key)
        elif comps & DEBUG_TAGS:        # отладочные сообщения — не показываются игроку
            skip.append(key)
        elif key in NAME_SKIP:          # ники/теги авторов — оставляем английскими
            skip.append(key)
        elif not ru:                    # нечего добавить
            doubtful.append((key, ru, note))
        else:                           # видимый текст с переводом — принимаем
            if "—" in ru:
                emdash.append((key, ru))
            extra.append((key, ru))
    else:
        skip.append(key)

# группировка translate по семантике тега
GROUP = {
    "MainMenuManager": "Описания и статы видов", "BodyScript": "Описания и статы видов",
    "MissionSelect": "Миссии и брифинги", "SceneLoader~raw": "Подсказки загрузки",
    "WeaponPreset": "Оружие", "GameManager~raw": "Прочее (рантайм)",
    "code_phrase": "Редактор уровней / служебный UI", "code_runtime": "HUD / рантайм-строки",
}
def group_of(key):
    tag = key2tag.get(key, "")
    comps = tag.strip("[]").split(",")
    for c in comps:
        if c in GROUP:
            return GROUP[c]
    return "Основной UI"

bygrp = defaultdict(list)
for key, ru in translate:
    bygrp[group_of(key)].append((key, ru))
for key, ru in extra:
    bygrp["Доразобранное (бывш. сомнительное)"].append((key, ru))

def to_regex(key, ru):
    r"""Надёжный regex-формат для ключей, которые XUnity не возьмёт как обычные:
    - начинающиеся с '//' (XUnity счёл бы комментарием);
    - содержащие '=' внутри (теги <color="red">, <voffset=3.5em>) — XUnity делит пару
      по первому '=' и обрезает ключ.
    Каждый пробельный промежуток (включая литерал \n) -> \s+ (XUnity нормализует пробелы/
    переносы при IgnoreWhitespaceInDialogue, поэтому буквальный \n не матчится). Кавычки -> '.'
    (иначе ломают разделитель r:"..."). Метасимволы экранируются, строка якорится ^\s*...\s*$."""
    key = re.sub(r'^(?:\\n|[ \t])+', '', key)
    key = re.sub(r'(?:\\n|[ \t])+$', '', key)
    out = []
    for p in re.split(r'((?:\\n|[ \t])+)', key):
        if p == '':
            continue
        if re.fullmatch(r'(?:\\n|[ \t])+', p):
            out.append(r'\s+')
        else:
            out.append(re.escape(p).replace('"', '.'))
    return 'r:"^\\s*' + ''.join(out) + '\\s*$"=' + ru

def _trim(s):
    return re.sub(r'(?:\\n|[ \t])+$', '', re.sub(r'^(?:\\n|[ \t])+', '', s))

def segment_pairs(eng, rus):
    r"""ПОДТВЕРЖДЕНО В ИГРЕ: XUnity при HandleRichText переводит ТЕКСТ-ФРАГМЕНТЫ между rich-text
    тегами по ОТДЕЛЬНОСТИ (полную tagged-строку — будь то плейн или regex — он не матчит, т.к.
    декомпозирует и/или нормализует теги). Значение фрагмента — ЧИСТЫЙ текст без тегов; формат
    (теги, \n) XUnity переприменяет сам. Бьём англ. и рус. по тегам и выравниваем непустые фрагменты."""
    e = [_trim(x) for x in re.split(r'<[^>]*>', eng)]
    r = [_trim(x) for x in re.split(r'<[^>]*>', rus)]
    if len(e) != len(r):
        return None
    return [(a, b) for a, b in zip(e, r) if a and re.search(r'[A-Za-z]', a)]

def detag(s):
    return re.sub(r'[ \t]{2,}', ' ', re.sub(r'<[^>]*>', '', s))

lines = ["// Авто-перевод текста игры. Сомнительное вынесено в docs/translation_review.txt.",
         "// Ключи-главы (ведущий //) -> regex. Tagged-строки (<color=...>) РАЗБИТЫ на текст-фрагменты",
         "// между тегами (XUnity переводит их по отдельности; полную строку не матчит — проверено в игре).", ""]
regex_lines = []
emitted = set()  # дедуп ФИНАЛЬНЫХ ключей (фрагменты разных строк могут совпасть, напр. 'Lowered health regeneration')
for grp in sorted(bygrp):
    body = []
    for key, ru in bygrp[grp]:
        if key.startswith("//"):
            continue  # главы обрабатываются вручную в ui_fixes (XUnity Multiline ломает якорный \s+;
                      # матчим по уникальному слову 2-й строки, '//' в значении -> через zero-width)
        if "<" in key:                                             # rich-text -> фрагменты
            segs = segment_pairs(key, ru)
            items = segs if segs is not None else [(detag(key), detag(ru))]  # fallback: де-тег обоих
        elif "=" in key:                                           # '=' без тега (редко)
            items = [(detag(key), ru)]
        else:
            items = [(key, ru)]                                    # чистый ключ
        for fk, fv in items:
            if not fk or fk in emitted:
                continue
            emitted.add(fk)
            body.append(fk + "=" + fv)
    if body:
        lines.append("// === %s ===" % grp)
        lines.extend(body)
        lines.append("")
if regex_lines:
    lines.append("// === Regex-ключи (ведущий // или '=' в теге; \\s+ для нормализации пробелов) ===")
    lines.extend(regex_lines)
    lines.append("")
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

# review-файл
rv = ["# Сомнительные строки на проверку (verdict=doubtful). Формат: ТЕГ | КЛЮЧ | предложенный RU | причина", ""]
for key, ru, note in doubtful:
    rv.append("[%s]\n  KEY: %r\n  RU : %s\n  ??? %s\n" % (key2tag.get(key, "?"), key, ru, note))
io.open(REVIEW, "w", encoding="utf-8", newline="\n").write("\n".join(rv) + "\n")

print("out-файлов прочитано:", len(glob.glob(os.path.join(ROOT, 'docs', 'wf_out', 'out_*.json'))))
print("записей всего:", len(records))
print("  translate (явные):", len(translate))
print("  extra (доразобрано из doubtful):", len(extra))
print("  => в ui_game.txt:", len(translate) + len(extra), "-> ", OUT)
print("  doubtful (осталось на проверку):", len(doubtful), "-> ", REVIEW)
print("  skip (вкл. треки/отладку):", len(skip))
print("проверки: dup=%d collide(с TAKEN)=%d em-dash=%d bad_json=%d" % (len(dup), len(collide), len(emdash), len(bad_json)))
if emdash:
    print("  em-dash в переводах (исправить):")
    for k, ru in emdash[:20]:
        print("    %r" % ru)
if bad_json:
    print("  битый JSON:", bad_json)
# счётчик skip по тегам (что отсеяно)
sc = Counter(key2tag.get(k, "?") for k in skip)
print("skip по тегам (топ):")
for t, n in sc.most_common(12):
    print("   %4d %s" % (n, t))
