# Адаптивный русификатор Gunsaw — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Рантайм-русификатор Gunsaw на BepInEx: XUnity.AutoTranslator переводит текст по ручному словарю, наш плагин `GunsawRusFonts` добавляет кириллицу в стиле оригинальных шрифтов и чинит адаптивную вёрстку.

**Architecture:** Гибрид. XUnity.AutoTranslator (готовый, офлайн) отвечает за перехват и подмену текста. Наш тонкий BepInEx-плагин на Harmony подключает кириллические fallback-шрифты к игровым `TMP_FontAsset` и применяет правила вёрстки. Чистая логика (парсинг конфигов) изолирована от Unity и покрыта юнит-тестами; Unity-зависимые части проверяются в реальной игре по логам и скриншотам.

**Tech Stack:** Unity 2021.1.23f1 (Mono), BepInEx 5.4.x (x64), XUnity.AutoTranslator-BepInEx 5.4.x, C# (netstandard2.0), HarmonyLib, TextMeshPro 3.0, xUnit (.NET 10), Python 3.13 (скрипт дампа строк).

**Корень проекта:** `C:\Users\User\Downloads\gunsaw-demo-win` (он же папка игры). Обозначается ниже как `<ROOT>`.

---

## Карта файлов

| Файл | Ответственность |
|---|---|
| `src/GunsawRusFonts/GunsawRusFonts.csproj` | Проект плагина (netstandard2.0), ссылки на Unity/BepInEx DLL |
| `src/GunsawRusFonts/Plugin.cs` | Точка входа BepInEx, загрузка конфигов, инициализация Harmony |
| `src/GunsawRusFonts/FontMap.cs` | Модель + парсер `font_map.txt` (чистая логика, тестируется) |
| `src/GunsawRusFonts/LayoutRules.cs` | Модель + парсер `layout_rules.txt` (чистая логика, тестируется) |
| `src/GunsawRusFonts/Win32Fonts.cs` | P/Invoke `AddFontResourceEx` для регистрации `.ttf` в процессе |
| `src/GunsawRusFonts/FontLoader.cs` | Загрузка `.ttf` → `TMP_FontAsset` (динамический OS-font), кэш |
| `src/GunsawRusFonts/FontService.cs` | Harmony-патч: подключение кириллического fallback к игровым FontAsset |
| `src/GunsawRusFonts/LayoutService.cs` | Harmony-патч: применение правил адаптивной вёрстки |
| `tests/GunsawRusFonts.Tests/GunsawRusFonts.Tests.csproj` | Юнит-тесты чистой логики |
| `tests/GunsawRusFonts.Tests/FontMapTests.cs` | Тесты парсера font_map |
| `tests/GunsawRusFonts.Tests/LayoutRulesTests.cs` | Тесты парсера layout_rules |
| `assets/fonts/*.ttf` | Кириллические шрифты |
| `assets/fonts/font_map.txt` | Карта «игровой FontAsset → кир. ttf\|faceName» |
| `assets/fonts/layout_rules.txt` | Точечные правила вёрстки |
| `tools/dump_strings.py` | Статический дамп строк из ассетов/DLL |
| `dist/` | Собранный мод для распространения |
| `docs/font_triage.md` | Таблица триажа шрифтов (заполняется в Task 8) |
| `docs/glossary.md` | Глоссарий терминов (заполняется в Task 13) |

**Установка мода (куда деплоится сборка):** `<ROOT>/BepInEx/plugins/GunsawRusFonts/GunsawRusFonts.dll`, шрифты — в `<ROOT>/fonts/`.

---

## Task 1: Каркас проекта

**Files:**
- Create: `<ROOT>/.gitignore`
- Create: `<ROOT>/src/GunsawRusFonts/GunsawRusFonts.csproj`
- Create: `<ROOT>/tests/GunsawRusFonts.Tests/GunsawRusFonts.Tests.csproj`

- [ ] **Step 1: Инициализировать git и .gitignore**

В `<ROOT>` создать `.gitignore`:

```
bin/
obj/
dist/
# Файлы игры не версионируем — это сторонний билд
/Gunsaw.exe
/Gunsaw_Data/
/MonoBleedingEdge/
/UnityCrashHandler64.exe
/UnityPlayer.dll
/BepInEx/
```

Затем:

```bash
cd "<ROOT>" && git init && git add .gitignore docs && git commit -m "chore: init russifier project"
```

- [ ] **Step 2: Создать проект плагина**

`src/GunsawRusFonts/GunsawRusFonts.csproj` (пути к DLL — абсолютные, к папке Managed игры):

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <AssemblyName>GunsawRusFonts</AssemblyName>
    <LangVersion>latest</LangVersion>
    <AllowUnsafeBlocks>false</AllowUnsafeBlocks>
    <EnableDefaultCompileItems>true</EnableDefaultCompileItems>
    <ManagedDir>$(MSBuildThisFileDirectory)..\..\Gunsaw_Data\Managed</ManagedDir>
    <BepInExCore>$(MSBuildThisFileDirectory)..\..\BepInEx\core</BepInExCore>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="UnityEngine"><HintPath>$(ManagedDir)\UnityEngine.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="UnityEngine.CoreModule"><HintPath>$(ManagedDir)\UnityEngine.CoreModule.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="UnityEngine.TextRenderingModule"><HintPath>$(ManagedDir)\UnityEngine.TextRenderingModule.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="UnityEngine.TextCoreModule"><HintPath>$(ManagedDir)\UnityEngine.TextCoreModule.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="UnityEngine.UIModule"><HintPath>$(ManagedDir)\UnityEngine.UIModule.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="Unity.TextMeshPro"><HintPath>$(ManagedDir)\Unity.TextMeshPro.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="BepInEx"><HintPath>$(BepInExCore)\BepInEx.dll</HintPath><Private>false</Private></Reference>
    <Reference Include="0Harmony"><HintPath>$(BepInExCore)\0Harmony.dll</HintPath><Private>false</Private></Reference>
  </ItemGroup>
</Project>
```

> Примечание: `BepInEx/core/*.dll` появятся после Task 2. До этого проект не соберётся целиком — это ожидаемо, сборку плагина запускаем начиная с Task 6.

- [ ] **Step 3: Создать тестовый проект**

`tests/GunsawRusFonts.Tests/GunsawRusFonts.Tests.csproj` — линкует исходники чистой логики напрямую (без Unity-зависимостей):

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>disable</Nullable>
    <IsPackable>false</IsPackable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="**/*.cs" />
    <Compile Include="..\..\src\GunsawRusFonts\FontMap.cs" />
    <Compile Include="..\..\src\GunsawRusFonts\LayoutRules.cs" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.1" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
  </ItemGroup>
</Project>
```

- [ ] **Step 4: Проверить, что тестовый проект восстанавливается**

Run: `cd "<ROOT>/tests/GunsawRusFonts.Tests" && dotnet restore`
Expected: восстановление без ошибок (компиляция упадёт позже — файлов `FontMap.cs`/`LayoutRules.cs` ещё нет; это нормально, создадим в Task 4–5).

- [ ] **Step 5: Commit**

```bash
cd "<ROOT>" && git add src tests && git commit -m "chore: scaffold plugin and test projects"
```

---

## Task 2: Установка BepInEx 5 и smoke-тест запуска

**Files:**
- Create: `<ROOT>/BepInEx/` (распакованный дистрибутив)

- [ ] **Step 1: Скачать BepInEx 5 (x64, Mono)**

Скачать последний релиз ветки 5.4.x `BepInEx_win_x64_5.4.*.zip` со страницы релизов: https://github.com/BepInEx/BepInEx/releases (НЕ BepInEx 6 / не IL2CPP — игра на Mono).

- [ ] **Step 2: Распаковать в корень игры**

Распаковать так, чтобы `winhttp.dll`, `doorstop_config.ini` и папка `BepInEx/` оказались рядом с `Gunsaw.exe` в `<ROOT>`.

- [ ] **Step 3: Первый запуск для генерации структуры**

Запустить игру:

```bash
cd "<ROOT>" && ./Gunsaw.exe
```

Дать игре дойти до меню, затем закрыть.

- [ ] **Step 4: Проверить, что BepInEx загрузился**

Проверить, что появились `<ROOT>/BepInEx/core/*.dll` (включая `BepInEx.dll`, `0Harmony.dll`) и `<ROOT>/BepInEx/LogOutput.log`.

Run: `cat "<ROOT>/BepInEx/LogOutput.log" | head -20`
Expected: строки вида `BepInEx 5.4.x` и `Chainloader started` без фатальных ошибок.

- [ ] **Step 5: Commit (фиксируем только факт настройки в README-заметке, не сам BepInEx)**

```bash
cd "<ROOT>" && git add docs && git commit -m "docs: note BepInEx 5 installed and verified" --allow-empty
```

---

## Task 3: Установка XUnity.AutoTranslator (офлайн-режим) и smoke перехвата

**Files:**
- Create: `<ROOT>/BepInEx/plugins/XUnity.AutoTranslator/`
- Modify: `<ROOT>/BepInEx/config/AutoTranslatorConfig.ini`

- [ ] **Step 1: Скачать XUnity.AutoTranslator для BepInEx 5**

Скачать `XUnity.AutoTranslator-BepInEx-5.4.*.zip` (последний релиз) со страницы: https://github.com/bbepis/XUnity.AutoTranslator/releases

- [ ] **Step 2: Распаковать в корень игры**

Распаковать в `<ROOT>` так, чтобы плагин оказался в `<ROOT>/BepInEx/plugins/XUnity.AutoTranslator/`.

- [ ] **Step 3: Запустить игру один раз для генерации конфига**

```bash
cd "<ROOT>" && ./Gunsaw.exe
```

Пройти по меню (чтобы AT увидел текст), закрыть.

- [ ] **Step 4: Настроить офлайн-режим**

Открыть `<ROOT>/BepInEx/config/AutoTranslatorConfig.ini` и выставить:

```ini
[Service]
Endpoint=
FallbackEndpoint=

[General]
Language=ru
FromLanguage=en

[Behaviour]
EnableUIResizing=true
OverrideFont=
OverrideFontTextMeshPro=
FallbackFontTextMeshPro=
```

`Endpoint=` пустой → никакого онлайн-перевода, только дамп и словарь.

- [ ] **Step 5: Проверить дамп строк**

Запустить игру, пройти меню, закрыть. Проверить, что появился файл словаря с собранными строками:

Run: `ls -la "<ROOT>/BepInEx/Translation/ru/Text/" && head -30 "<ROOT>/BepInEx/Translation/ru/Text/_AutoGeneratedTranslations.txt"`
Expected: файл существует, содержит строки игры в формате `Оригинал=` (правая часть пустая = не переведено).

- [ ] **Step 6: Commit**

```bash
cd "<ROOT>" && git add docs && git commit -m "docs: note XUnity.AutoTranslator installed in offline mode" --allow-empty
```

---

## Task 4: FontMap — парсер карты шрифтов (TDD, чистая логика)

**Files:**
- Create: `<ROOT>/src/GunsawRusFonts/FontMap.cs`
- Test: `<ROOT>/tests/GunsawRusFonts.Tests/FontMapTests.cs`

Формат `font_map.txt`: `ИмяИгровогоFontAsset=ttfФайл|FaceName` (FaceName опционален; по умолчанию — имя файла без расширения). Комментарии — строки, начинающиеся с `#`.

- [ ] **Step 1: Написать падающие тесты**

`tests/GunsawRusFonts.Tests/FontMapTests.cs`:

```csharp
using GunsawRusFonts;
using Xunit;

public class FontMapTests
{
    [Fact]
    public void Parse_BasicEntry_ResolvesTtfAndFace()
    {
        var map = FontMap.Parse("chloe font v1 SDF=chloe-cyr.ttf|Chloe Cyrillic");
        var e = map.Resolve("chloe font v1 SDF");
        Assert.NotNull(e);
        Assert.Equal("chloe-cyr.ttf", e.Ttf);
        Assert.Equal("Chloe Cyrillic", e.Face);
    }

    [Fact]
    public void Parse_NoFace_DefaultsToFileNameWithoutExtension()
    {
        var map = FontMap.Parse("Acidic=acidic-cyr.ttf");
        var e = map.Resolve("Acidic");
        Assert.Equal("acidic-cyr.ttf", e.Ttf);
        Assert.Equal("acidic-cyr", e.Face);
    }

    [Fact]
    public void Parse_IgnoresCommentsAndBlankLines()
    {
        var map = FontMap.Parse("# comment\n\n  \nAcidic=acidic-cyr.ttf\n");
        Assert.Equal(1, map.Count);
    }

    [Fact]
    public void Parse_TrimsWhitespace()
    {
        var map = FontMap.Parse("  Acidic  =  acidic-cyr.ttf  |  Acidic Cyr  ");
        var e = map.Resolve("Acidic");
        Assert.Equal("acidic-cyr.ttf", e.Ttf);
        Assert.Equal("Acidic Cyr", e.Face);
    }

    [Fact]
    public void Resolve_Miss_ReturnsNull()
    {
        var map = FontMap.Parse("Acidic=acidic-cyr.ttf");
        Assert.Null(map.Resolve("Unknown"));
        Assert.Null(map.Resolve(null));
    }

    [Fact]
    public void Parse_DuplicateKey_LastWins()
    {
        var map = FontMap.Parse("A=one.ttf\nA=two.ttf");
        Assert.Equal("two.ttf", map.Resolve("A").Ttf);
    }
}
```

- [ ] **Step 2: Запустить тесты — убедиться, что падают**

Run: `cd "<ROOT>/tests/GunsawRusFonts.Tests" && dotnet test`
Expected: FAIL — компиляция падает, тип `FontMap` не найден.

- [ ] **Step 3: Реализовать FontMap**

`src/GunsawRusFonts/FontMap.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.IO;

namespace GunsawRusFonts
{
    public sealed class FontEntry
    {
        public string Ttf;
        public string Face;
    }

    public sealed class FontMap
    {
        private readonly Dictionary<string, FontEntry> _map;

        public FontMap(Dictionary<string, FontEntry> map) { _map = map; }

        public int Count => _map.Count;

        public static FontMap Parse(string content)
        {
            var d = new Dictionary<string, FontEntry>(StringComparer.Ordinal);
            if (content != null)
            {
                foreach (var raw in content.Split('\n'))
                {
                    var line = raw.Trim();
                    if (line.Length == 0 || line[0] == '#') continue;
                    int eq = line.IndexOf('=');
                    if (eq <= 0) continue;
                    var key = line.Substring(0, eq).Trim();
                    var val = line.Substring(eq + 1).Trim();
                    if (key.Length == 0 || val.Length == 0) continue;

                    string ttf, face;
                    int bar = val.IndexOf('|');
                    if (bar >= 0)
                    {
                        ttf = val.Substring(0, bar).Trim();
                        face = val.Substring(bar + 1).Trim();
                    }
                    else
                    {
                        ttf = val;
                        face = Path.GetFileNameWithoutExtension(val);
                    }
                    if (ttf.Length == 0) continue;
                    d[key] = new FontEntry { Ttf = ttf, Face = face };
                }
            }
            return new FontMap(d);
        }

        public FontEntry Resolve(string fontAssetName)
        {
            if (fontAssetName == null) return null;
            return _map.TryGetValue(fontAssetName.Trim(), out var e) ? e : null;
        }
    }
}
```

- [ ] **Step 4: Запустить тесты — убедиться, что проходят**

Run: `cd "<ROOT>/tests/GunsawRusFonts.Tests" && dotnet test`
Expected: PASS, 6 тестов.

- [ ] **Step 5: Commit**

```bash
cd "<ROOT>" && git add src/GunsawRusFonts/FontMap.cs tests && git commit -m "feat: font map parser with tests"
```

---

## Task 5: LayoutRules — парсер правил вёрстки (TDD, чистая логика)

**Files:**
- Create: `<ROOT>/src/GunsawRusFonts/LayoutRules.cs`
- Test: `<ROOT>/tests/GunsawRusFonts.Tests/LayoutRulesTests.cs`

Формат `layout_rules.txt`: `подстрокаИмениОбъекта|minFontScale|enableWrap|maxLines`. `minFontScale` — float (доля от исходного кегля, нижняя граница автосайза), `enableWrap` — bool, `maxLines` — int (0 = без лимита). Первое правило, чья подстрока содержится в имени объекта, выигрывает.

- [ ] **Step 1: Написать падающие тесты**

`tests/GunsawRusFonts.Tests/LayoutRulesTests.cs`:

```csharp
using GunsawRusFonts;
using Xunit;

public class LayoutRulesTests
{
    [Fact]
    public void Parse_BasicRule_ParsesAllFields()
    {
        var rules = LayoutRules.Parse("PlayButton|0.6|true|1");
        var r = rules.Match("MainMenu/PlayButton");
        Assert.NotNull(r);
        Assert.Equal(0.6f, r.MinFontScale, 3);
        Assert.True(r.EnableWrap);
        Assert.Equal(1, r.MaxLines);
    }

    [Fact]
    public void Match_FirstMatchingSubstringWins()
    {
        var rules = LayoutRules.Parse("Button|0.5|false|0\nPlayButton|0.6|true|1");
        var r = rules.Match("PlayButton");
        Assert.Equal(0.5f, r.MinFontScale, 3); // первое по порядку
    }

    [Fact]
    public void Match_CaseInsensitive()
    {
        var rules = LayoutRules.Parse("dialogue|0.8|true|0");
        Assert.NotNull(rules.Match("EnemyDialogueBox"));
    }

    [Fact]
    public void Match_NoMatch_ReturnsNull()
    {
        var rules = LayoutRules.Parse("PlayButton|0.6|true|1");
        Assert.Null(rules.Match("SomethingElse"));
        Assert.Null(rules.Match(null));
    }

    [Fact]
    public void Parse_IgnoresCommentsBlanksAndMalformed()
    {
        var rules = LayoutRules.Parse("# c\n\nPlayButton|0.6|true|1\nbroken|notafloat|true|1\nonlyone");
        Assert.Equal(1, rules.Count);
    }

    [Fact]
    public void Parse_InvariantDecimalPoint()
    {
        var rules = LayoutRules.Parse("X|0.75|false|2");
        Assert.Equal(0.75f, rules.Match("X").MinFontScale, 3);
    }
}
```

- [ ] **Step 2: Запустить тесты — убедиться, что падают**

Run: `cd "<ROOT>/tests/GunsawRusFonts.Tests" && dotnet test`
Expected: FAIL — тип `LayoutRules` не найден.

- [ ] **Step 3: Реализовать LayoutRules**

`src/GunsawRusFonts/LayoutRules.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;

namespace GunsawRusFonts
{
    public sealed class LayoutRule
    {
        public string Match;
        public float MinFontScale;
        public bool EnableWrap;
        public int MaxLines;
    }

    public sealed class LayoutRules
    {
        private readonly List<LayoutRule> _rules;

        public LayoutRules(List<LayoutRule> rules) { _rules = rules; }

        public int Count => _rules.Count;

        public static LayoutRules Parse(string content)
        {
            var list = new List<LayoutRule>();
            if (content != null)
            {
                foreach (var raw in content.Split('\n'))
                {
                    var line = raw.Trim();
                    if (line.Length == 0 || line[0] == '#') continue;
                    var p = line.Split('|');
                    if (p.Length < 4) continue;
                    if (!float.TryParse(p[1].Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out var scale))
                        continue;
                    bool.TryParse(p[2].Trim(), out var wrap);
                    int.TryParse(p[3].Trim(), out var maxl);
                    var match = p[0].Trim();
                    if (match.Length == 0) continue;
                    list.Add(new LayoutRule { Match = match, MinFontScale = scale, EnableWrap = wrap, MaxLines = maxl });
                }
            }
            return new LayoutRules(list);
        }

        public LayoutRule Match(string objectName)
        {
            if (objectName == null) return null;
            foreach (var r in _rules)
                if (objectName.IndexOf(r.Match, StringComparison.OrdinalIgnoreCase) >= 0)
                    return r;
            return null;
        }
    }
}
```

- [ ] **Step 4: Запустить тесты — убедиться, что проходят**

Run: `cd "<ROOT>/tests/GunsawRusFonts.Tests" && dotnet test`
Expected: PASS, 12 тестов суммарно (6 FontMap + 6 LayoutRules).

- [ ] **Step 5: Commit**

```bash
cd "<ROOT>" && git add src/GunsawRusFonts/LayoutRules.cs tests && git commit -m "feat: layout rules parser with tests"
```

---

## Task 6: Plugin skeleton — точка входа, загрузка конфигов, лог

**Files:**
- Create: `<ROOT>/src/GunsawRusFonts/Plugin.cs`
- Create: `<ROOT>/assets/fonts/font_map.txt` (пока пустой/комментарий)
- Create: `<ROOT>/assets/fonts/layout_rules.txt` (пока пустой/комментарий)

- [ ] **Step 1: Создать стартовые конфиги**

`assets/fonts/font_map.txt`:

```
# Формат: ИмяИгровогоFontAsset=ttfФайл|FaceName
# Заполняется в Task 8 после триажа шрифтов.
```

`assets/fonts/layout_rules.txt`:

```
# Формат: подстрокаИмениОбъекта|minFontScale|enableWrap|maxLines
# Заполняется по результатам ранней проверки (Task 11).
```

- [ ] **Step 2: Реализовать Plugin.cs**

`src/GunsawRusFonts/Plugin.cs`:

```csharp
using System.IO;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;

namespace GunsawRusFonts
{
    [BepInPlugin("gunsaw.rusfonts", "Gunsaw RUS Fonts & Layout", "0.1.0")]
    public class Plugin : BaseUnityPlugin
    {
        internal static ManualLogSource Log;
        internal static FontMap FontMap;
        internal static LayoutRules LayoutRules;
        internal static string FontsDir;

        private void Awake()
        {
            Log = Logger;
            FontsDir = Path.Combine(Paths.GameRootPath, "fonts");

            FontMap = LoadFontMap(Path.Combine(FontsDir, "font_map.txt"));
            LayoutRules = LoadLayoutRules(Path.Combine(FontsDir, "layout_rules.txt"));
            Log.LogInfo($"font_map: {FontMap.Count} entries; layout_rules: {LayoutRules.Count} rules; dir={FontsDir}");

            new Harmony("gunsaw.rusfonts").PatchAll();
            Log.LogInfo("GunsawRusFonts initialized");
        }

        private static FontMap LoadFontMap(string path)
        {
            try { return File.Exists(path) ? FontMap.Parse(File.ReadAllText(path)) : FontMap.Parse(""); }
            catch (System.Exception e) { Log.LogError($"font_map load error: {e}"); return FontMap.Parse(""); }
        }

        private static LayoutRules LoadLayoutRules(string path)
        {
            try { return File.Exists(path) ? LayoutRules.Parse(File.ReadAllText(path)) : LayoutRules.Parse(""); }
            catch (System.Exception e) { Log.LogError($"layout_rules load error: {e}"); return LayoutRules.Parse(""); }
        }
    }
}
```

- [ ] **Step 3: Собрать плагин**

Run: `cd "<ROOT>/src/GunsawRusFonts" && dotnet build -c Release`
Expected: BUILD SUCCEEDED, артефакт `bin/Release/netstandard2.0/GunsawRusFonts.dll`.

- [ ] **Step 4: Задеплоить в игру и проверить загрузку**

```bash
mkdir -p "<ROOT>/BepInEx/plugins/GunsawRusFonts"
cp "<ROOT>/src/GunsawRusFonts/bin/Release/netstandard2.0/GunsawRusFonts.dll" "<ROOT>/BepInEx/plugins/GunsawRusFonts/"
cp -r "<ROOT>/assets/fonts" "<ROOT>/fonts"
cd "<ROOT>" && ./Gunsaw.exe
```

Дойти до меню, закрыть. Проверить лог:

Run: `grep -i "GunsawRusFonts\|font_map" "<ROOT>/BepInEx/LogOutput.log"`
Expected: строки `font_map: 0 entries; layout_rules: 0 rules` и `GunsawRusFonts initialized` без исключений.

- [ ] **Step 5: Commit**

```bash
cd "<ROOT>" && git add src/GunsawRusFonts/Plugin.cs assets && git commit -m "feat: BepInEx plugin entrypoint with config loading"
```

---

## Task 7: SPIKE — загрузка одного кириллического шрифта в рантайме

Цель: доказать рабочий путь загрузки `.ttf` → `TMP_FontAsset` (динамический OS-font) и отображение кириллицы в игре. Если путь не сработает — переключиться на AssetBundle (см. конец задачи).

**Files:**
- Create: `<ROOT>/src/GunsawRusFonts/Win32Fonts.cs`
- Create: `<ROOT>/src/GunsawRusFonts/FontLoader.cs`
- Modify: `<ROOT>/src/GunsawRusFonts/Plugin.cs` (временный smoke-вызов)
- Create: `<ROOT>/fonts/_spike.ttf` (любой кириллический шрифт, напр. DejaVu Sans или PT Sans)

- [ ] **Step 1: Положить тестовый кириллический шрифт**

Скопировать любой свободный шрифт с кириллицей в `<ROOT>/fonts/_spike.ttf` (например, DejaVuSans.ttf или PTSans-Regular.ttf). Запомнить его face name (family), напр. `DejaVu Sans`.

- [ ] **Step 2: Реализовать Win32Fonts.cs**

`src/GunsawRusFonts/Win32Fonts.cs`:

```csharp
using System;
using System.Runtime.InteropServices;

namespace GunsawRusFonts
{
    internal static class Win32Fonts
    {
        [DllImport("gdi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern int AddFontResourceEx(string lpszFilename, uint fl, IntPtr pdv);

        private const uint FR_PRIVATE = 0x10;

        /// <summary>Регистрирует .ttf в текущем процессе. Возвращает true при успехе.</summary>
        public static bool Register(string ttfPath)
        {
            try { return AddFontResourceEx(ttfPath, FR_PRIVATE, IntPtr.Zero) > 0; }
            catch (Exception e) { Plugin.Log.LogError($"AddFontResourceEx failed: {e}"); return false; }
        }
    }
}
```

- [ ] **Step 3: Реализовать FontLoader.cs**

`src/GunsawRusFonts/FontLoader.cs`:

```csharp
using System.Collections.Generic;
using System.IO;
using TMPro;
using UnityEngine;
using UnityEngine.TextCore.LowLevel;

namespace GunsawRusFonts
{
    internal static class FontLoader
    {
        private static readonly Dictionary<string, TMP_FontAsset> _cache = new Dictionary<string, TMP_FontAsset>();

        /// <summary>Грузит .ttf как динамический TMP_FontAsset. ttfFileName — имя файла в fonts/, faceName — family.</summary>
        public static TMP_FontAsset Load(string ttfFileName, string faceName)
        {
            if (_cache.TryGetValue(ttfFileName, out var cached)) return cached;

            var path = Path.Combine(Plugin.FontsDir, ttfFileName);
            if (!File.Exists(path))
            {
                Plugin.Log.LogWarning($"TTF not found: {path}");
                _cache[ttfFileName] = null;
                return null;
            }

            try
            {
                Win32Fonts.Register(path);
                var osFont = Font.CreateDynamicFontFromOSFont(faceName, 90);
                var tmp = TMP_FontAsset.CreateFontAsset(osFont, 90, 9, GlyphRenderMode.SDFAA, 1024, 1024,
                    AtlasPopulationMode.Dynamic);
                tmp.name = "CYR_" + faceName;
                _cache[ttfFileName] = tmp;
                Plugin.Log.LogInfo($"Loaded TMP font '{tmp.name}' from {ttfFileName} (face '{faceName}')");
                return tmp;
            }
            catch (System.Exception e)
            {
                Plugin.Log.LogError($"FontLoader failed for {ttfFileName}: {e}");
                _cache[ttfFileName] = null;
                return null;
            }
        }
    }
}
```

- [ ] **Step 4: Временный smoke-вызов в Plugin.Awake**

В конец `Awake()` добавить (после `PatchAll`) — временно, удалим в Task 9:

```csharp
            // SPIKE: проверить загрузку одного шрифта (удалить в Task 9)
            var spike = FontLoader.Load("_spike.ttf", "DejaVu Sans");
            Log.LogInfo($"SPIKE font load result: {(spike != null ? "OK glyphs=" + spike.characterTable.Count : "NULL")}");
```

- [ ] **Step 5: Собрать, задеплоить, запустить**

```bash
cd "<ROOT>/src/GunsawRusFonts" && dotnet build -c Release \
&& cp bin/Release/netstandard2.0/GunsawRusFonts.dll "<ROOT>/BepInEx/plugins/GunsawRusFonts/" \
&& cd "<ROOT>" && ./Gunsaw.exe
```

Дойти до меню, закрыть.

- [ ] **Step 6: Проверить результат spike**

Run: `grep -i "SPIKE\|Loaded TMP font\|FontLoader failed" "<ROOT>/BepInEx/LogOutput.log"`
Expected (успех пути 1): `SPIKE font load result: OK glyphs=...` без `FontLoader failed`.

**Если NULL/ошибка** (`CreateDynamicFontFromOSFont` вернул пустой или исключение):
- Записать в `docs/font_triage.md` факт провала пути 1.
- Переключиться на **путь 2 (AssetBundle)**: установить Unity 2021.1.23f1, создать TMP FontAsset из кириллического `.ttf` через Font Asset Creator, упаковать в AssetBundle `cyrfonts.bundle`, и заменить тело `FontLoader.Load` на загрузку из бандла (`AssetBundle.LoadFromFile` → `LoadAsset<TMP_FontAsset>(faceName)`). Остальной план (FontService/LayoutService) не меняется — меняется только реализация `FontLoader.Load`.

- [ ] **Step 7: Commit**

```bash
cd "<ROOT>" && git add src/GunsawRusFonts/Win32Fonts.cs src/GunsawRusFonts/FontLoader.cs src/GunsawRusFonts/Plugin.cs && git commit -m "feat: runtime ttf loader (spike validated)"
```

---

## Task 8: Триаж шрифтов и заполнение font_map

**Files:**
- Create: `<ROOT>/docs/font_triage.md`
- Modify: `<ROOT>/assets/fonts/font_map.txt`
- Create: `<ROOT>/assets/fonts/*.ttf` (подобранные кириллические шрифты)

Игровые шрифты (из разведки): `Gelatik-Regular`, `chloe font v1`, `Acidic`, `conthrax-sb`, `hemi head bd it`, `respawn-pro`, `PixelOperator`, `PixelOperatorOutline`, `Retro Gaming`, `Victor`, `Sansation_Regular`, `LiberationSans`.

- [ ] **Step 1: Зафиксировать точные имена FontAsset из игры**

Run: `grep -iE "SDF|Atlas" "<ROOT>/BepInEx/LogOutput.log"` — и/или прогнать `tools/dump_strings.py` (Task 12) по `resources.assets`, чтобы выписать точные имена `*.name` каждого FontAsset (важно: `Resolve` сравнивает строго).

- [ ] **Step 2: Для каждого шрифта пройти 4-ступенчатый триаж (§4 спеки)**

Создать `docs/font_triage.md` с таблицей-колонками: `FontAsset | кириллица в оригинале? | готовая кир. версия? | решение | источник .ttf | faceName`. Ступени по порядку: (1) кириллица в оригинале → (2) готовая кир. версия → (3) подбор стилевого аналога → (4) ручная дорисовка для ключевых.

Заведомо вероятные:
- `LiberationSans` — кириллица есть в оригинале → взять полный LiberationSans.ttf.
- `PixelOperator` / `PixelOperatorOutline` — кириллица есть в оригинале (PixelOperator поддерживает кириллицу) → взять оригинальный .ttf.
- `conthrax-sb` — проверить наличие официальной кириллической версии.
- `chloe font v1`, `Acidic`, `hemi head bd it`, `respawn-pro`, `Retro Gaming`, `Victor`, `Gelatik`, `Sansation` — вероятно подбор стилевого аналога (для реплик врагов — показать заказчику варианты на выбор).

- [ ] **Step 3: Положить подобранные .ttf и заполнить font_map.txt**

Скопировать выбранные `.ttf` в `<ROOT>/assets/fonts/` и `<ROOT>/fonts/`. Заполнить `assets/fonts/font_map.txt`, например:

```
LiberationSans SDF=LiberationSans.ttf|Liberation Sans
PixelOperator=PixelOperator.ttf|PixelOperator
chloe font v1 SDF=chloe-cyr.ttf|Chloe Cyrillic
Acidic=acidic-cyr.ttf|Acidic Cyrillic
```

> По ключевым шрифтам (реплики врагов, заголовки) — показать заказчику пары «латиница оригинала / кир. кандидат» и утвердить выбор перед фиксацией.

- [ ] **Step 4: Commit**

```bash
cd "<ROOT>" && git add docs/font_triage.md assets/fonts && git commit -m "feat: font triage and cyrillic font map"
```

---

## Task 9: FontService — подключение кириллического fallback к игровым FontAsset

**Files:**
- Create: `<ROOT>/src/GunsawRusFonts/FontService.cs`
- Modify: `<ROOT>/src/GunsawRusFonts/Plugin.cs` (убрать spike-вызов из Task 7; задать нейтральный fallback)

- [ ] **Step 1: Убрать временный spike-код из Plugin.Awake**

Удалить добавленные в Task 7 строки `// SPIKE: ...`. Добавить опциональный нейтральный fallback: в `font_map.txt` зарезервировать ключ `*` для нейтрального шрифта (читается отдельно). В `Plugin` добавить:

```csharp
        internal static FontEntry NeutralFallback;
```

и в конце `Awake` (до `PatchAll`):

```csharp
            NeutralFallback = FontMap.Resolve("*"); // строка вида: *=neutral-cyr.ttf|Neutral Cyr
```

- [ ] **Step 2: Реализовать FontService.cs**

`src/GunsawRusFonts/FontService.cs` (патчим оба конкретных типа — UGUI и world-text; имена методов TMP — `OnEnable`):

```csharp
using System;
using System.Collections.Generic;
using HarmonyLib;
using TMPro;

namespace GunsawRusFonts
{
    internal static class FontService
    {
        private static readonly HashSet<int> _patchedFonts = new HashSet<int>();

        public static void EnsureCyrillic(TMP_Text instance)
        {
            try
            {
                var fa = instance != null ? instance.font : null;
                if (fa == null) return;
                int id = fa.GetInstanceID();
                if (_patchedFonts.Contains(id)) return;
                _patchedFonts.Add(id);

                var entry = Plugin.FontMap.Resolve(fa.name) ?? Plugin.NeutralFallback;
                if (entry == null) return;

                var cyr = FontLoader.Load(entry.Ttf, entry.Face);
                if (cyr == null) return;

                if (fa.fallbackFontAssetTable == null)
                    fa.fallbackFontAssetTable = new List<TMP_FontAsset>();
                if (!fa.fallbackFontAssetTable.Contains(cyr))
                {
                    fa.fallbackFontAssetTable.Add(cyr);
                    Plugin.Log.LogInfo($"Cyrillic fallback '{entry.Ttf}' -> font '{fa.name}'");
                }
            }
            catch (Exception e) { Plugin.Log.LogError($"FontService error: {e}"); }
        }
    }

    [HarmonyPatch(typeof(TextMeshProUGUI), "OnEnable")]
    internal static class FontService_UGUI
    {
        static void Postfix(TextMeshProUGUI __instance) => FontService.EnsureCyrillic(__instance);
    }

    [HarmonyPatch(typeof(TextMeshPro), "OnEnable")]
    internal static class FontService_World
    {
        static void Postfix(TextMeshPro __instance) => FontService.EnsureCyrillic(__instance);
    }
}
```

- [ ] **Step 3: Собрать, задеплоить, запустить**

```bash
cd "<ROOT>/src/GunsawRusFonts" && dotnet build -c Release \
&& cp bin/Release/netstandard2.0/GunsawRusFonts.dll "<ROOT>/BepInEx/plugins/GunsawRusFonts/" \
&& cp -r "<ROOT>/assets/fonts/." "<ROOT>/fonts/" \
&& cd "<ROOT>" && ./Gunsaw.exe
```

Пройти меню (где видны разные шрифты), закрыть.

- [ ] **Step 4: Проверить подключение fallback в логе**

Run: `grep -i "Cyrillic fallback" "<ROOT>/BepInEx/LogOutput.log"`
Expected: строки подключения для встреченных FontAsset (`LiberationSans SDF`, `PixelOperator`, и т.д.) без `FontService error`.

- [ ] **Step 5: Commit**

```bash
cd "<ROOT>" && git add src/GunsawRusFonts/FontService.cs src/GunsawRusFonts/Plugin.cs && git commit -m "feat: attach cyrillic fallback to game fonts"
```

---

## Task 10: LayoutService — адаптивная вёрстка

**Files:**
- Create: `<ROOT>/src/GunsawRusFonts/LayoutService.cs`

Политика: мягкий глобальный автосайз для всех TMP-текстов (нижняя граница 75% кегля) + переопределение точечными правилами из `layout_rules.txt`.

- [ ] **Step 1: Реализовать LayoutService.cs**

`src/GunsawRusFonts/LayoutService.cs`:

```csharp
using System;
using System.Collections.Generic;
using HarmonyLib;
using TMPro;

namespace GunsawRusFonts
{
    internal static class LayoutService
    {
        private static readonly HashSet<int> _done = new HashSet<int>();
        private const float DefaultMinScale = 0.75f;

        public static void Apply(TMP_Text t)
        {
            try
            {
                if (t == null) return;
                int id = t.GetInstanceID();
                if (_done.Contains(id)) return;
                _done.Add(id);

                string objName = t.gameObject != null ? t.gameObject.name : null;
                var rule = Plugin.LayoutRules.Match(objName);

                float baseSize = t.fontSize;
                float minScale = rule != null ? rule.MinFontScale : DefaultMinScale;
                bool wrap = rule != null ? rule.EnableWrap : t.enableWordWrapping;

                t.enableAutoSizing = true;
                t.fontSizeMax = baseSize;
                t.fontSizeMin = baseSize * minScale;
                t.enableWordWrapping = wrap;

                if (rule != null && rule.MaxLines > 0)
                    t.maxVisibleLines = rule.MaxLines;
            }
            catch (Exception e) { Plugin.Log.LogError($"LayoutService error: {e}"); }
        }
    }

    [HarmonyPatch(typeof(TextMeshProUGUI), "OnEnable")]
    internal static class LayoutService_UGUI
    {
        static void Postfix(TextMeshProUGUI __instance) => LayoutService.Apply(__instance);
    }

    [HarmonyPatch(typeof(TextMeshPro), "OnEnable")]
    internal static class LayoutService_World
    {
        static void Postfix(TextMeshPro __instance) => LayoutService.Apply(__instance);
    }
}
```

> Примечание: коэффициент `DefaultMinScale` и точечные правила калибруются по скриншотам в Task 11. Здесь задаются безопасные стартовые значения.

- [ ] **Step 2: Собрать, задеплоить, запустить, проверить отсутствие ошибок**

```bash
cd "<ROOT>/src/GunsawRusFonts" && dotnet build -c Release \
&& cp bin/Release/netstandard2.0/GunsawRusFonts.dll "<ROOT>/BepInEx/plugins/GunsawRusFonts/" \
&& cd "<ROOT>" && ./Gunsaw.exe
```

Run: `grep -i "LayoutService error" "<ROOT>/BepInEx/LogOutput.log"`
Expected: пусто (ошибок нет). Меню визуально не сломано.

- [ ] **Step 3: Commit**

```bash
cd "<ROOT>" && git add src/GunsawRusFonts/LayoutService.cs && git commit -m "feat: adaptive layout service"
```

---

## Task 11: Ранняя проверка — мини-перевод меню + скриншоты

Цель: на 10–20 реальных русских строках убедиться, что кириллица рисуется в нужных стилях и вёрстка не ломается, ДО полного перевода.

**Files:**
- Modify: `<ROOT>/BepInEx/Translation/ru/Text/_AutoGeneratedTranslations.txt`
- Modify: `<ROOT>/assets/fonts/layout_rules.txt` (по итогам)
- Create: `<ROOT>/docs/early-check-screenshots/` (скриншоты до/после)

- [ ] **Step 1: Перевести мини-набор строк меню**

В `_AutoGeneratedTranslations.txt` заполнить правую часть для ~10–20 строк главного меню/настроек, например:

```
Play=Играть
Settings=Настройки
Quit=Выход
Deathmatch=Бой насмерть
Char select=Выбор персонажа
```

(Точные оригиналы взять из уже сдампленного файла.)

- [ ] **Step 2: Запустить и сделать скриншоты ключевых экранов**

```bash
cd "<ROOT>" && ./Gunsaw.exe
```

Снять скриншоты главного меню, настроек, экрана выбора персонажа, любой сцены с репликами врагов. Сохранить в `docs/early-check-screenshots/`.

- [ ] **Step 3: Визуальная сверка**

Проверить по скриншотам:
- кириллица каждого встреченного стилевого шрифта отображается (нет `□`/квадратов);
- стиль кириллицы близок к латинице оригинала (особенно реплики врагов);
- длинные строки не обрезаются и не вылезают за кнопки/плашки.

Записать проблемы списком.

- [ ] **Step 4: Откалибровать (шрифты и/или правила вёрстки)**

- Если стиль кириллицы у ключевого шрифта не устраивает → вернуться в Task 8, заменить `.ttf`-аналог, показать заказчику варианты.
- Если где-то обрезка/наезд → добавить точечное правило в `assets/fonts/layout_rules.txt`, напр.:

```
PlayButton|0.6|true|1
DialogueBox|0.8|true|0
```

Повторять Step 2–4, пока ключевые экраны не будут чистыми.

- [ ] **Step 5: Commit**

```bash
cd "<ROOT>" && git add assets/fonts/layout_rules.txt docs/early-check-screenshots && git commit -m "test: early visual check of fonts and layout on menu"
```

---

## Task 12: Полный дамп строк

**Files:**
- Create: `<ROOT>/tools/dump_strings.py`
- Create: `<ROOT>/docs/string-inventory.md`

- [ ] **Step 1: Написать статический дамп строк из ассетов/DLL**

`tools/dump_strings.py`:

```python
import re, sys, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "Gunsaw_Data")

def ascii_strings(data, n=4):
    return [m.group().decode('ascii') for m in re.finditer(rb'[\x20-\x7e]{%d,}' % n, data)]

def utf16_strings(data, n=4):
    out = []
    for m in re.finditer((rb'(?:[\x20-\x7e]\x00){%d,}' % n), data):
        out.append(m.group().decode('utf-16-le'))
    return out

def looks_like_ui(s):
    s = s.strip()
    if len(s) < 2 or len(s) > 120: return False
    if not re.search(r'[A-Za-z]', s): return False
    # отсечь системные/типовые
    if re.search(r'(System\.|Unity|UnityEngine|get_|set_|\.dll|mscorlib|<[A-Za-z]|::|/)', s): return False
    return True

def main():
    files = glob.glob(os.path.join(DATA, 'level*')) \
        + glob.glob(os.path.join(DATA, 'sharedassets*.assets')) \
        + [os.path.join(DATA, 'resources.assets')] \
        + [os.path.join(DATA, 'Managed', 'Assembly-CSharp.dll')]
    seen = set()
    for f in files:
        if not os.path.exists(f): continue
        data = open(f, 'rb').read()
        for s in ascii_strings(data) + utf16_strings(data):
            t = s.strip()
            if looks_like_ui(t) and t not in seen:
                seen.add(t)
    for s in sorted(seen):
        print(s)

if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Прогнать и сохранить инвентарь**

Run: `cd "<ROOT>" && python tools/dump_strings.py > docs/string-inventory.md`
Expected: файл с черновым списком строк-кандидатов (будет с шумом — это нормально, человек отфильтрует).

- [ ] **Step 3: Дополнить рантайм-дампом AT**

Пройти всю демо-игру с модом (все уровни/экраны/диалоги), чтобы AT дособрал в `_AutoGeneratedTranslations.txt` всё, что показывается. Свести с инвентарём — получить полный список строк к переводу. Зафиксировать число строк в `docs/string-inventory.md`.

- [ ] **Step 4: Commit**

```bash
cd "<ROOT>" && git add tools/dump_strings.py docs/string-inventory.md && git commit -m "feat: static string dumper and full string inventory"
```

---

## Task 13: Глоссарий и перевод по экранам

**Files:**
- Create: `<ROOT>/docs/glossary.md`
- Modify: `<ROOT>/BepInEx/Translation/ru/Text/_AutoGeneratedTranslations.txt`

- [ ] **Step 1: Собрать глоссарий терминов с нуля**

В `docs/glossary.md` выписать повторяющиеся термины (название игры, режимы, оружие, имена, UI-команды) с предложенным переводом/транслитом/латиницей. Спорные — на утверждение заказчику.

- [ ] **Step 2: Перевести по смысловым зонам**

Заполнять `_AutoGeneratedTranslations.txt` пакетами: меню → настройки → HUD → реплики врагов → туториал. Соблюдать глоссарий, плейсхолдеры (`{0}`, `{player}`) и теги (`<b>`, `<color>`) не трогать.

- [ ] **Step 3: Прогон и выверка**

Запустить игру, пройти по зонам, проверить подстановку и отсутствие непереведённых мест (AT дампит непереведённое — проверить пустые правые части). Внести правки заказчика. Итерировать.

- [ ] **Step 4: Commit**

```bash
cd "<ROOT>" && git add docs/glossary.md "BepInEx/Translation/ru/Text/_AutoGeneratedTranslations.txt" && git commit -m "feat: glossary and full russian translation"
```

> Примечание: `_AutoGeneratedTranslations.txt` — это поставляемый артефакт перевода, поэтому версионируем его (исключение из .gitignore-правила про `BepInEx/`: добавить `!BepInEx/Translation/` в `.gitignore`).

---

## Task 14: Сборка дистрибутива, README, тест отката

**Files:**
- Create: `<ROOT>/dist/` (готовый мод)
- Create: `<ROOT>/dist/README.txt`
- Create: `<ROOT>/tools/build_dist.ps1`

- [ ] **Step 1: Скрипт сборки дистрибутива**

`tools/build_dist.ps1` собирает в `dist/Gunsaw-RUS/` структуру для распространения:

```powershell
$root = Split-Path $PSScriptRoot -Parent
$out  = Join-Path $root "dist\Gunsaw-RUS"
Remove-Item -Recurse -Force $out -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $out | Out-Null

# плагин
dotnet build (Join-Path $root "src\GunsawRusFonts\GunsawRusFonts.csproj") -c Release
$dll = Join-Path $root "src\GunsawRusFonts\bin\Release\netstandard2.0\GunsawRusFonts.dll"
New-Item -ItemType Directory -Force (Join-Path $out "BepInEx\plugins\GunsawRusFonts") | Out-Null
Copy-Item $dll (Join-Path $out "BepInEx\plugins\GunsawRusFonts\")

# шрифты + конфиги
Copy-Item -Recurse (Join-Path $root "assets\fonts") (Join-Path $out "fonts")
# словарь
New-Item -ItemType Directory -Force (Join-Path $out "BepInEx\Translation\ru\Text") | Out-Null
Copy-Item (Join-Path $root "BepInEx\Translation\ru\Text\_AutoGeneratedTranslations.txt") (Join-Path $out "BepInEx\Translation\ru\Text\")
# конфиг AT
Copy-Item (Join-Path $root "BepInEx\config\AutoTranslatorConfig.ini") (Join-Path $out "BepInEx\config\")

Write-Host "Built dist at $out"
```

> Сам BepInEx и XUnity.AutoTranslator поставляются отдельной инструкцией в README (или докладываются в dist вручную — это сторонние дистрибутивы).

- [ ] **Step 2: README для игрока**

`dist/README.txt`:

```
Русификатор Gunsaw
==================
Установка:
1. Установите BepInEx 5 (x64) — распакуйте в папку игры.
2. Установите XUnity.AutoTranslator (BepInEx 5) — распакуйте в папку игры.
3. Распакуйте содержимое этой папки (Gunsaw-RUS) в корень игры с заменой.
4. Запустите игру.

Отключение: удалите папку BepInEx (или uninstall BepInEx). Оригинальные файлы игры не изменяются.
```

- [ ] **Step 3: Собрать дистрибутив**

Run: `cd "<ROOT>" && pwsh tools/build_dist.ps1`
Expected: `dist/Gunsaw-RUS/` со структурой `BepInEx/plugins/...`, `fonts/`, `BepInEx/Translation/...`.

- [ ] **Step 4: Тест отката**

Временно переименовать `<ROOT>/BepInEx` → `<ROOT>/BepInEx_off`, запустить игру:

```bash
cd "<ROOT>" && mv BepInEx BepInEx_off && ./Gunsaw.exe
```

Expected: игра запускается в исходном (английском) виде без артефактов. Вернуть: `mv BepInEx_off BepInEx`.

- [ ] **Step 5: Commit**

```bash
cd "<ROOT>" && git add tools/build_dist.ps1 dist/README.txt && git commit -m "feat: dist build script and player readme"
```

---

## Self-Review (выполнено при написании плана)

**Покрытие спеки:**
- §3 Архитектура (AT + наш плагин) → Tasks 3, 6, 9, 10 ✓
- §4 Шрифты: fallback-подход → Task 9; метод загрузки/spike → Task 7; триаж → Task 8 ✓
- §5 Адаптивная вёрстка → Task 10 (+ калибровка в Task 11) ✓
- §6 Перевод/словарь/глоссарий → Tasks 11 (мини), 12 (дамп), 13 (полный) ✓
- §7 Поставка/откат/тесты → Task 14; устойчивость (try/catch) → Tasks 9, 10 ✓
- §9 Порядок (ранняя проверка) → Tasks 7→8→9→10→**11 (ранняя проверка)**→12→13→14 ✓

**Согласованность типов:** `FontMap.Parse/Resolve`, `FontEntry{Ttf,Face}`, `LayoutRules.Parse/Match`, `LayoutRule{Match,MinFontScale,EnableWrap,MaxLines}`, `FontLoader.Load(ttf,face)`, `FontService.EnsureCyrillic`, `LayoutService.Apply` — имена согласованы между задачами ✓

**Плейсхолдеры:** нет TBD/«добавить обработку ошибок» без кода; все шаги с кодом содержат код. Открытые места (выбор конкретных `.ttf`, коэффициенты вёрстки) вынесены в задачи с явной процедурой калибровки, а не оставлены как «доделать» ✓

**Известный риск:** загрузка `.ttf` в рантайме (Task 7) — при провале пути 1 переключение на AssetBundle (путь 2) описано; интерфейс `FontLoader.Load` при этом не меняется, остальные задачи не затрагиваются ✓
