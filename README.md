<div align="center">

# 🎮 Gunsaw — Русификатор

**Полный русский перевод демки [Gunsaw](https://orsonik.itch.io/gunsaw-demo): интерфейс, сюжет и реплики врагов — каждый своим шрифтом.**

[![Версия](https://img.shields.io/github/v/release/Profit155/gunsaw-russifier?label=версия&color=2ea44f)](https://github.com/Profit155/gunsaw-russifier/releases/latest)
[![Скачиваний](https://img.shields.io/github/downloads/Profit155/gunsaw-russifier/total?label=скачиваний&color=blue)](https://github.com/Profit155/gunsaw-russifier/releases)
![Платформа](https://img.shields.io/badge/платформа-Windows-555)
![Язык](https://img.shields.io/badge/перевод-100%25-2ea44f)

<br>

<img src="assets/media/01-menu.jpg" width="80%" alt="Главное меню Gunsaw на русском">

</div>

---

## ✨ Что это

Это **русификатор** бесплатной демо-игры **Gunsaw** — фанатский перевод всего текста плюс
кириллические шрифты, нарисованные специально под игру. Ставится по принципу
**«скачал и распаковал»**: ничего настраивать руками не нужно, отдельный софт ставить не надо.

> Перевод неофициальный и не связан с автором игры. Оригинал — [Gunsaw Demo by Orsoniks](https://orsonik.itch.io/gunsaw-demo).

---

## ✅ Что переведено

Переведено **всё, на 100%**:

- 🖱️ **Меню и весь интерфейс**
- ⚙️ **Настройки** — Звук, Видео, Геймплей, Персонаж, Управление
- 📖 **Сюжет, диалоги, советы и подсказки**
- 💬 **Реплики врагов** — у каждого вида свой шрифт и своя манера речи
- 🏷️ **Имена врагов и названия оружия**

---

## 📸 Как выглядит

<div align="center">
<table>
  <tr>
    <td width="50%"><img src="assets/media/02-settings.jpg" width="100%" alt="Настройки на русском"><br><sub>⚙️ Настройки — переведён весь UI</sub></td>
    <td width="50%"><img src="assets/media/03-gameplay.jpg" width="100%" alt="Геймплей с русским текстом"><br><sub>🎯 Текст прямо в бою</sub></td>
  </tr>
  <tr>
    <td width="50%"><img src="assets/media/05-dialogue.png" width="100%" alt="Реплика врага на русском"><br><sub>💬 Реплики врагов</sub></td>
    <td width="50%"><img src="assets/media/04-disclaimer.jpg" width="100%" alt="Дисклеймер и совет дня на русском"><br><sub>📖 Длинные тексты и советы</sub></td>
  </tr>
</table>
</div>

---

## 🎬 Реплики врагов — каждый своим шрифтом

Это не просто перевод реплик: **у каждого вида врага свой шрифт и характер речи**.
Кириллические начертания подобраны под оригинальные — Роза говорит «граффити»-шрифтом,
робот — пиксельным, и так далее.

<div align="center">
<table>
  <tr>
    <td width="50%">
      <img src="assets/media/roza.gif" width="100%" alt="Роза: реплика и взрыв бочки">
      <br><sub>🌹 <b>Роза</b> (шрифт Chloe): ящик → реплика → бочка → 💥</sub>
    </td>
    <td width="50%">
      <img src="assets/media/expie.gif" width="100%" alt="Эксперимент: устранение и реплики">
      <br><sub>🧪 <b>Эксперимент</b>: устранение и болтовня на фоне текста уровня</sub>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="assets/media/abomination.gif" width="100%" alt="Абоминация">
      <br><sub>🧟 <b>Абоминация</b></sub>
    </td>
    <td width="50%">
      <img src="assets/media/action.gif" width="100%" alt="Геймплей: диалоги, бодисвап, смерть">
      <br><sub>⚔️ <b>Геймплей</b>: диалоги, смена тел (бодисвап) и смерть</sub>
    </td>
  </tr>
</table>
</div>

---

## ⬇️ Установка за 3 шага

1. **Скачай** последний `Gunsaw-Russifier-vX.X.X.zip` со страницы [**Releases**](https://github.com/Profit155/gunsaw-russifier/releases/latest).
2. **Распакуй** архив прямо в папку с игрой (туда, где лежит `Gunsaw.exe`), соглашаясь на замену файлов.
3. **Запусти** `Gunsaw.exe` — игра уже на русском.

> 💡 **Совет:** перед установкой сделай резервную копию `Gunsaw_Data/resources.assets` —
> мод заменяет этот файл (в нём русские имена врагов), а бэкап позволит легко вернуть всё назад.
>
> ⏳ Первый запуск может занять до минуты — это инициализируется загрузчик модов. Так и должно быть.

Ничего больше ставить не нужно — всё необходимое уже лежит в архиве.

---

## ❓ Если что-то не так

| Проблема | Что делать |
|---|---|
| Игра по-прежнему на английском | Проверь, что распаковал **в корень игры**: рядом с `Gunsaw.exe` должны появиться `winhttp.dll` и папка `BepInEx`. Запускай именно `Gunsaw.exe`. |
| Долгий чёрный экран при первом запуске | Это нормально — загрузчик модов инициализируется. Подожди до минуты. |
| Антивирус ругается на `winhttp.dll` | Ложное срабатывание: это загрузчик модов (BepInEx). Добавь файл/папку в исключения. |
| Вместо русских букв — квадратики | Убедись, что папка `fonts/` тоже распакована в корень игры. |
| Хочу вернуть как было | См. раздел **Удаление** ниже. |

---

## 🐞 Нашли проблему?

Опечатка, кривая вёрстка, непереведённая строка или просто баг — **пишите, принимаем любые сообщения**,
даже самые мелкие. Откройте [**Issue**](https://github.com/Profit155/gunsaw-russifier/issues/new)
и опишите, что заметили (по возможности — со скриншотом).

---

## 🧹 Удаление

Из папки игры удалите:

- файл `winhttp.dll`
- папки `BepInEx` и `fonts`

Затем восстановите `Gunsaw_Data/resources.assets` из резервной копии (или проверьте целостность файлов игры).

---

## 🙏 Благодарности

- **Оригинальная игра** — [Gunsaw Demo](https://orsonik.itch.io/gunsaw-demo) от **Orsoniks**.
- Сборка переводов работает на [BepInEx](https://github.com/BepInEx/BepInEx) и [XUnity.AutoTranslator](https://github.com/bbepis/XUnity.AutoTranslator).

---

<details>
<summary>🛠️ <b>Для разработчиков</b> (сборка, структура проекта, инструменты)</summary>

<br>

### Состав репозитория

- **`src/GunsawRusFonts/`** — BepInEx-плагин: рантайм-сборка кириллических TMP-шрифтов
  из `.ttf` (фолбэк к игровым шрифтам, без перепаковки ассетов) + точечная подгонка
  вёрстки русских строк (`LayoutService`).
- **`translations/ru/Text/`** — переводы для XUnity AutoTranslator: UI (`ui_*.txt`),
  реплики врагов (`chatter_*.txt`), регэкспы и пре/постпроцессоры.
- **`fonts/`** — русифицированные `.ttf` + метрики, карта шрифтов `font_map.txt`
  (игровой шрифт → ttf-фолбэк) и правила вёрстки `layout_rules.txt`.
- **`tools/`** — Python-тулчейн: извлечение строк из ассетов, сборка переводов,
  имена врагов, чаттер, генерация метрик шрифтов.
- **`docs/`** — спеки и данные workflow перевода.

### Сборка плагина

```sh
dotnet build src/GunsawRusFonts/GunsawRusFonts.csproj -c Release
```

### Установка на чистую игру вручную

Нужны **BepInEx** + **XUnity.AutoTranslator**. Затем:

- `GunsawRusFonts.dll` → `BepInEx/plugins/GunsawRusFonts/`
- `fonts/` → в корень игры (рядом с `Gunsaw.exe`) — плагин читает `<gameroot>/fonts/`
- `translations/ru/Text/*.txt` → `BepInEx/Translation/ru/Text/`
- XUnity: `Language=ru`, `Endpoint=` пуст (офлайн — только эти переводы);
  см. `translations/config/AutoTranslatorConfig.ini`

</details>
