# -*- coding: utf-8 -*-
"""Сборка словаря секции имён из вывода воркфлоу перевода.
Читает JSON результата (result.base[] = [{eng,ru,category,flag,note}]), применяет ручные
OVERRIDES, пишет tools/names_data/<section>.json (eng->ru) и docs/names_<section>_review.tsv.
Запуск: python tools/gen_names_from_workflow.py <output.json> <SECTION>
"""
import os, sys, json, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATADIR = os.path.join(ROOT, 'tools', 'names_data')
DOCDIR = os.path.join(ROOT, 'docs')
os.makedirs(DATADIR, exist_ok=True)

# Ручные правки поверх перевода агента (по секциям).
OVERRIDES = {
  "BASE": {
    "Etho": "Этхо",   # 'Это' читается как рус. "это"
    "Rote": "Роут",   # 'Рот' читается как рус. "рот"
    "Glee": "Гли",    # 'Глее' неблагозвучно
    "West": "Вэст",   # как имя (Kanye West), не направление
    "North": "Норт",  # как имя, консистентно с West->Вэст
    "Musk": "Маск",   # шутка Elon Musk (Elon->Илон в пуле)
    "Saw": "Сав",     # кличка-клип названия вида (Gunsawians/Sawians), не инструмент
    "Ally": "Союзник", # прикол: враг по имени "Союзник" (а не имя Элли)
  },
  "ORANGE": {
    "Heavy": "Пулемётчик",  # канон офиц. рус-дубляжа TF2 (класс Heavy = Пулемётчик), не «Толстяк»
    "Cheeks": "Щёки",       # щёки лица; разводит коллизию с Buttcheeks→Булки
    "Yapper": "Воздухан",   # пустозвон-болтун, мемное; вместо «Балабол»
    "Orange": "Апельсин",   # цвет/еда как кличка вида ORANGE
    "Coinflip": "Монетка",  # вместо «Подкидыш» (читалось как «подкинули в детстве»)
  },
  "MILKY": {
    "Five Pebbles": "Пять Галек",  # рус-вики Rain World
    "Strelok": "Меченый",          # STALKER (Меченый), освобождает «Стрелок» для Slinger
    "Slinger": "Стрелок",          # gun-slinger → Стрелок (Strelok ушёл в Меченый)
    "Artificer": "Техник",         # рус-вики Rain World (не «Ремесленник»)
    "Watcher": "Созерцатель",      # рус-вики Rain World (не «Наблюдатель»)
    "Coach": "Тренер",             # рус-дубляж L4D2
    "Hitman": "Хитман",            # транслит (вместо «Ликвидатор»)
    "Poland": "Поланд",            # транслит-позывной (вместо «Полония»)
    "Church": "Церковь",           # клерикальный смысл (Deacon оставлен отсылкой Дикон)
    "Shorty": "Обрез",             # обрез-дробовик (оружейный смысл)
    "Codename 7": "Позывной 7",    # Bond 007; «7» сохраняет кивок
    "White": "Белый",              # самоотсылка: вид Milky — белый
  },
  "LEAPY": {
    "Hopper": "Кузнечик",   # развод коллизии с Jumper→Прыгун + grasshopper по виду
    "Green": "Зелёный",     # самоотсылка: вид Leapy — зелёный (как White→Белый у Milky)
    "Roller": "Роллер",     # роллер-движенец (Каток=асфальтоукладчик, мимо)
    "Tiger": "Тигр",        # боевое прозвище по смыслу (не «Тайгер»)
  },
  "CHOMPY": {
    "Happy": "Счастливчик",  # развод коллизии с Jolly→Весельчак (канон)
    "Regy": "Реги",          # развод коллизии с Reggie→Реджи (вариант написания)
    # Darwin/Darvin оба → Дарвин намеренно (дев продублировал отсылку на рыбку из Гамбола)
  },
  "VOYAGER": {
    "Bastard": "Ублюдок",  # надменный кот «не самый хороший котик» — по описанию вида
    "Shadow": "Тень",      # по смыслу (в тон мрак-кластеру), не «Шэдоу»
    "Night": "Ночь",       # по смыслу, не «Найт»
    "Scratch": "Коготок",  # ласк.-хищное (vs Claw→Коготь), не обрубок «Царап»
    # Ghost оставлен «Гоуст» (англо-позывной CoD), Bishop — канон «Бишоп»
  },
}

def main():
    out_path, section = sys.argv[1], sys.argv[2].upper()
    raw = json.load(io.open(out_path, encoding='utf-8'))
    base = raw.get('result', raw).get('base', [])
    ov = OVERRIDES.get(section, {})
    mapping, review = {}, []
    for it in base:
        eng = it['eng'].strip()
        ru = ov.get(eng, it['ru']).strip()
        if '[' in ru:
            raise SystemExit("'[' в переводе %r" % ru)
        mapping[eng] = ru
        review.append((eng, ru, it.get('category',''), 'FLAG' if it.get('flag') else '',
                       ('OVR ' if eng in ov else '') + (it.get('note','') or '')))
    # запись словаря
    jpath = os.path.join(DATADIR, section.lower() + '.json')
    io.open(jpath, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(mapping, ensure_ascii=False, indent=0))
    # запись ревью-файла
    tsv = os.path.join(DOCDIR, 'names_%s_review.tsv' % section.lower())
    with io.open(tsv, 'w', encoding='utf-8', newline='\n') as f:
        f.write("ENG\tRU\tCATEGORY\tFLAG\tNOTE\n")
        for r in review:
            f.write("\t".join(r) + "\n")
    print("Секция %s: %d имён -> %s" % (section, len(mapping), os.path.relpath(jpath, ROOT)))
    print("Ревью: %s" % os.path.relpath(tsv, ROOT))
    print("FLAG'нутых (спорных):", sum(1 for r in review if r[3]=='FLAG'))

if __name__ == '__main__':
    main()
