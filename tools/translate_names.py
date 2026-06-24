# -*- coding: utf-8 -*-
"""Перевод имён врагов прямо в TextAsset 'NameList' (Gunsaw_Data/resources.assets, path_id 1000).
RandomName(species) (декомпил 13911) режет секцию "[SPECIES]".."[", Split('\n'), берёт случайную строку.
Поэтому правим ВНУТРИ секции построчно, сохраняя заголовок/число строк/'\r\n' 1:1 и НЕ вводя '[' в имя.
Доставка: имя становится кириллическим в characterName -> готовые regex состояний (ui_fixes) подхватывают $1.

Режимы:
  python tools/translate_names.py            # dry-run: проверка покрытия секций из DICTS, без записи
  python tools/translate_names.py --apply    # запись (бэкап оригинала -> .orig, сборка из .orig)
ВАЖНО при --apply: игру ЗАКРЫТЬ (файл блокируется); ассет грузится при старте -> нужен перезапуск.
Идемпотентность: всегда собираем из pristine-бэкапа resources.assets.orig (создаётся при первом --apply).
"""
import os, sys, shutil, re
import UnityPy

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(ROOT, 'Gunsaw_Data')
ASSET = os.path.join(DATA, 'resources.assets')
ORIG = ASSET + '.orig'   # pristine (англ.) бэкап

# Словари перевода по секциям. Расширяем по мере прохода по видам.
DICTS = {
 "EXPERIMENT": {
  "AJ":"Эй-Джей","Acke":"Акке","Addi":"Адди","Albert":"Альберт","Alf":"Альф","Ander":"Андер",
  "Andrew":"Эндрю","Anim":"Аним","Anon":"Анон","Aspy":"Аспи","Basil":"Бэзил","Bean":"Боб",
  "Bee":"Пчёлка","Beta":"Бета","Beverly":"Беверли","Black":"Чёрный","Bobo":"Бобо","Bolt":"Болт",
  "Bon":"Бон","Brook":"Брук","CJ":"Си-Джей","Carlos":"Карлос","Carrot":"Морковка","Cenn":"Сенн",
  "Choi":"Чой","Ciar":"Киар","Clay":"Клэй","Clover":"Клевер","Clyde":"Клайд","Coal":"Уголёк",
  "Coco":"Коко","Cocoa":"Какао","Cole":"Коул","Colt":"Кольт","Coward":"Трус","Craw":"Крав",
  "Crawler":"Ползун","Cri":"Кри","Crieg":"Криг","D":"Ди","Daan":"Дан","Doub":"Даб","Dude":"Чувак",
  "Dusty":"Пыльный","Easel":"Изель","East":"Восток","Eavi":"Иви","Einar":"Эйнар","Elwin":"Элвин",
  "Ember":"Эмбер","Enby":"Энби","Endy":"Энди","Eric":"Эрик","Ewa":"Эва","Exi":"Экси",
  "Exper":"Экспер","Expi":"Экспи","Exun":"Эксан","Felix":"Феликс","Finian":"Финиан","Flint":"Кремень",
  "Fodder":"Пушечное мясо","Fox":"Лис","Franky":"Фрэнки","Fuzzy":"Пушистик","Gabri":"Габри",
  "Glare":"Зыркало","Grey":"Серый","Hernandez":"Эрнандес","Hidden":"Скрытый","Hik":"Хик",
  "Inigo":"Иниго","Inky":"Инки","Iro":"Иро","Irvin":"Ирвин","Jan":"Ян","Joker":"Джокер",
  "Jolly":"Весельчак","Jr.":"Мл.","Kel":"Кел","Koda":"Кода","Koy":"Кой","Lau":"Лау","Link":"Линк",
  "Linus":"Линус","Lonely":"Одиночка","Loni":"Лони","Loser":"Лошара","Louis":"Луи","MK":"Эм-Кей",
  "Mario":"Марио","Matt":"Мэтт","Maverick":"Маверик","Meat":"Мясо","Moon":"Луна","Morty":"Морти",
  "Naia":"Найя","Nathan":"Нейтан","Navii":"Нави","Nemo":"Немо","Nevin":"Невин","Nobody":"Никто",
  "Noke":"Ноке","No Significant Harrassment":"Никаких Значимых Забот","Oli":"Оли","Oliver":"Оливер",
  "Omero":"Омеро","Omori":"Омори","Onyx":"Оникс","Opti":"Опти","Orsi":"Орси","Orson":"Орсон",
  "Ortho":"Орто","Oscar":"Оскар","Otto":"Отто","Paige":"Пейдж","Pal":"Дружок","Pate":"Пейт",
  "Peanut":"Орешек","Peeper":"Гляделкинс","Pelly":"Пелли","Pepper":"Перчик","Peter":"Питер",
  "Peyton":"Пейтон","Phil":"Фил","Philip":"Филип","Pibb":"Пибб","Pion":"Пион","Pip":"Пип",
  "Poltri":"Полтри","Poyo":"Пойо","Prisoner":"Заключённый","Pup":"Щенок","Quilly":"Квилли",
  "Racoon":"Енот","Rigby":"Ригби","Runner":"Бегун","Scarf":"Шарф","Scrungle":"Скрангл",
  "Scuggly":"Скаггли","Sergei":"Сергей","Shrub":"Кустик","Simon":"Саймон","Slime":"Слизняк",
  "Soldier":"Солдат","Solo":"Соло","Soul":"Душа","Spot":"Пятныш","Stephen":"Стивен","Stitch":"Стич",
  "Stoke":"Стоук","Survivor":"Выживший","TJ":"Ти-Джей","Tobia":"Тобиа","Tod":"Тод","Tommy":"Томми",
  "Tory":"Тори","Trash":"Мусор","Trashboat":"Говновоз","Tweaker":"Дёрганый","Tyler":"Тайлер",
  "Useless":"Бесполезный","Vani":"Вани","Walker":"Уокер","Wally":"Уолли","Weak":"Слабак",
  "Weazel":"Ласка","Wess":"Уэсс","Yoinky":"Йоинки",
 },
}

# Догружаем секции из tools/names_data/<section>.json (генерит gen_names.py).
# Файлы с ведущим '_' — служебные (не словари секций).
import json, glob
_DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'names_data')
for _jp in glob.glob(os.path.join(_DATADIR, '*.json')):
    _bn = os.path.basename(_jp)
    if _bn.startswith('_'):
        continue
    _sec = os.path.splitext(_bn)[0].upper()
    with open(_jp, encoding='utf-8') as _f:
        DICTS[_sec] = {**DICTS.get(_sec, {}), **json.load(_f)}

# Дополнения — НОВЫЕ имена, которых нет в англ. оригинале: _additions.json {"SEC":[names]}.
ADDITIONS = {}
_ap = os.path.join(_DATADIR, '_additions.json')
if os.path.exists(_ap):
    with open(_ap, encoding='utf-8') as _f:
        ADDITIONS = json.load(_f)

def load_text(path):
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name == 'TextAsset':
            d = obj.read()
            if getattr(d, 'm_Name', None) == 'NameList':
                t = d.m_Script
                if isinstance(t, (bytes, bytearray)):
                    t = t.decode('utf-8', 'replace')
                return env, obj, d, t
    raise SystemExit("NameList не найден в " + path)

def translate_section(text, species, mapping):
    """Возвращает (new_text, missing[], translated_count). Правит только секцию [species]."""
    start = text.rfind('[' + species + ']')
    if start < 0:
        raise SystemExit("Секция [%s] не найдена" % species)
    end = text.find('[', start + 1)
    if end < 0:
        end = len(text)
    seg = text[start:end]
    out_lines, missing, n = [], [], 0
    for ln in seg.split('\n'):
        cr = ln.endswith('\r')
        core = ln[:-1] if cr else ln
        key = core.strip()
        if key == '' or key.startswith('['):
            out_lines.append(ln)            # заголовок/пустая — как есть
            continue
        if key in mapping:
            ru = mapping[key]
            if '[' in ru:
                raise SystemExit("Символ '[' в переводе '%s' сломает RandomName" % ru)
            out_lines.append(ru + ('\r' if cr else ''))
            n += 1
        else:
            missing.append(key)
            out_lines.append(ln)
    new_seg = '\n'.join(out_lines)
    return text[:start] + new_seg + text[end:], missing, n

def add_names(text, species, names):
    """Дописывает НОВЫЕ имена в конец секции [species] (перед след. '[' или в конец)."""
    s = text.find('[' + species + ']')
    if s < 0:
        print("ОШИБКА: секция [%s] для дополнений не найдена" % species)
        return text, 0
    e = text.find('[', s + 1)
    if e < 0:
        e = len(text)
    for n in names:
        if '[' in n:
            raise SystemExit("Символ '[' в добавляемом имени %r" % n)
    ins = ''.join(n + '\r\n' for n in names)
    return text[:e] + ins + text[e:], len(names)

def main():
    apply = '--apply' in sys.argv
    if apply and not os.path.exists(ORIG):
        shutil.copy2(ASSET, ORIG)
        print("Создан pristine-бэкап:", os.path.basename(ORIG))
    src = ORIG if os.path.exists(ORIG) else ASSET  # источник истины — англ. оригинал (идемпотентно)

    env, obj, d, text = load_text(src)
    print("Источник:", os.path.basename(src), "| длина:", len(text))

    new_text = text
    total_missing = {}
    for species, mapping in DICTS.items():
        new_text, missing, n = translate_section(new_text, species, mapping)
        # лишние ключи в словаре, которых нет в секции
        seg_start = text.rfind('[' + species + ']'); seg_end = text.find('[', seg_start+1)
        seg_keys = set(x.strip().rstrip('\r').strip() for x in text[seg_start:(seg_end if seg_end>0 else len(text))].split('\n'))
        extra = [k for k in mapping if k not in seg_keys]
        print("[%s] переведено %d, не найдено в ассете (MISSING): %d, лишних в словаре (EXTRA): %d"
              % (species, n, len(missing), len(extra)))
        if missing:
            print("   MISSING:", missing)
            total_missing[species] = missing
        if extra:
            print("   EXTRA:", extra)

    if total_missing:
        print("\nНЕ ПИШУ: есть непокрытые имена в ассете. Добавь их в словарь.")
        return

    # дополнения (новые имена)
    for species, names in ADDITIONS.items():
        new_text, k = add_names(new_text, species, names)
        if k:
            print("[%s] добавлено новых имён: %d (%s)" % (species, k, ", ".join(names)))

    if not apply:
        print("\nDRY-RUN ок: все имена секций покрыты. Запуск с --apply запишет в resources.assets.")
        return

    # запись
    d.m_Script = new_text
    d.save()
    try:
        blob = env.file.save()
    except Exception:
        blob = env.file.save(packer="original")
    tmp = ASSET + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(blob)
    os.replace(tmp, ASSET)
    print("\nЗАПИСАНО в", os.path.basename(ASSET))

    # верификация
    _, _, _, check = load_text(ASSET)
    for species, mapping in DICTS.items():
        s = check.rfind('[' + species + ']'); e = check.find('[', s+1)
        seg = check[s:(e if e>0 else len(check))]
        sample = [v for v in mapping.values()][:3]
        ok = all(v in seg for v in sample)
        print("Верификация [%s]: примеры %s -> %s" % (species, sample, "НАЙДЕНЫ" if ok else "НЕ найдены"))
    for species, names in ADDITIONS.items():
        s = check.find('[' + species + ']'); e = check.find('[', s+1)
        seg = check[s:(e if e>0 else len(check))]
        ok = all((n + '\r') in seg for n in names)
        print("Верификация дополнений [%s]: %s" % (species, "НАЙДЕНЫ" if ok else "НЕ найдены"))

if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        if isinstance(e.code, str):
            print("ОШИБКА:", e.code)
        raise
