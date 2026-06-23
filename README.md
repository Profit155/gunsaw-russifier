# Gunsaw Russifier

Русификатор демо-игры **Gunsaw** (бесплатная демо, на хиатусе): кириллические шрифты,
перевод интерфейса и реплик, плюс инструменты перевода.

## Состав

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

## Сборка плагина

```
dotnet build src/GunsawRusFonts/GunsawRusFonts.csproj -c Release
```

## Установка (на чистую игру)

Нужны **BepInEx** + **XUnity.AutoTranslator**. Затем:

- `GunsawRusFonts.dll` → `BepInEx/plugins/GunsawRusFonts/`
- `fonts/` → в корень игры (рядом с `Gunsaw.exe`) — плагин читает `<gameroot>/fonts/`
- `translations/ru/Text/*.txt` → `BepInEx/Translation/ru/Text/`
- XUnity: `Language=ru`, `Endpoint=` пуст (офлайн — только эти переводы);
  см. `translations/config/AutoTranslatorConfig.ini`

Готовый мод-пакет «скачал и распаковал» — в разделе **Releases**.
