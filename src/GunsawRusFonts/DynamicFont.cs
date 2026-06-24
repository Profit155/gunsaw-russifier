using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using UnityEngine.TextCore;
using UnityEngine.TextCore.LowLevel;
using TMPro;

namespace GunsawRusFonts
{
    /// <summary>
    /// Builds a dynamic TMP_FontAsset from raw .ttf bytes at runtime via FontEngine,
    /// bypassing UnityEngine.Font (which cannot load custom/OS fonts in a player build).
    ///
    /// TMP's glyph baking (TryAddCharacterInternal) reloads the face on every call via
    /// FontEngine.LoadFontFace(m_SourceFontFile, pointSize). For a runtime-built asset that
    /// Font is null, so baking silently fails. We store a marker Font in m_SourceFontFile
    /// and Harmony-redirect LoadFontFace(Font, ...) to our ttf bytes (see patches below).
    /// </summary>
    internal static class DynamicFont
    {
        internal const int SamplingPointSize = 90;
        private const int AtlasSize = 2048;   // 1024 переполнялся (67+ глифов по ~95px) — вторая страница атласа рисуется ненадёжно
        private const int Padding = 9;

        // marker Font (stored in each asset's m_SourceFontFile) -> ttf file path.
        // Загрузка по ПУТИ (а не из byte[]): face из byte[] не регистрируется в нативном
        // кэше FontEngine, и многопоточный батч-рендер TryAddGlyphsToTexture получает
        // «пустой» face — все глифы выходят с нулевыми rect и метриками.
        private static readonly Dictionary<Font, string> _sources = new Dictionary<Font, string>();

        internal static string GetSourcePath(Font font)
        {
            string path;
            return font != null && _sources.TryGetValue(font, out path) ? path : null;
        }

        public static TMP_FontAsset Build(string ttfPath, string assetName)
        {
            if (FontEngine.InitializeFontEngine() != FontEngineError.Success)
            {
                Plugin.Log.LogError("DynamicFont: InitializeFontEngine failed");
                return null;
            }

            // Marker Font: внутри CreateFontAsset и TryAddCharacters все вызовы
            // LoadFontFace(Font, ...) перенаправляются на наш файл Harmony-патчами ниже.
            var marker = new Font(assetName + "_src");
            marker.hideFlags = HideFlags.DontSave;
            _sources[marker] = ttfPath;

            // Канонический путь TMP: ассет, атлас, материал и пакер делает сам TMP.
            var fa = TMP_FontAsset.CreateFontAsset(marker, SamplingPointSize, Padding,
                GlyphRenderMode.SDFAA, AtlasSize, AtlasSize,
                AtlasPopulationMode.Dynamic, true);
            if (fa == null)
            {
                Plugin.Log.LogError($"DynamicFont: CreateFontAsset failed for '{assetName}'");
                return null;
            }
            fa.name = assetName;
            fa.hideFlags = HideFlags.DontSave;

            fa.ReadFontAssetDefinition(); // инициализация lookup-таблиц до TryAddCharacters
            int baked = PreBakeCyrillic(fa);
            fa.ReadFontAssetDefinition();
            Plugin.Log.LogInfo($"DynamicFont: pre-baked {baked} cyrillic glyphs into '{assetName}'");
            return fa;
        }

        /// <summary>
        /// Unity's FreeType returns garbage advances for a few glyphs of some fonts.
        /// Re-apply reference metrics emitted from the ttf.
        /// </summary>
        public static int ApplyReferenceMetrics(TMP_FontAsset fa, string metricsPath)
        {
            if (fa == null || !System.IO.File.Exists(metricsPath)) return 0;
            float upem = 0;
            int fixedCount = 0;
            foreach (var raw in System.IO.File.ReadAllLines(metricsPath))
            {
                var line = raw.Trim();
                if (line.StartsWith("upem="))
                {
                    upem = float.Parse(line.Substring(5), System.Globalization.CultureInfo.InvariantCulture);
                    continue;
                }
                if (upem <= 0 || !line.StartsWith("U+")) continue;
                int eq = line.IndexOf('=');
                if (eq < 0) continue;
                uint cp;
                if (!uint.TryParse(line.Substring(2, eq - 2), System.Globalization.NumberStyles.HexNumber,
                                   System.Globalization.CultureInfo.InvariantCulture, out cp)) continue;
                var parts = line.Substring(eq + 1).Split(',');
                if (parts.Length < 5) continue;
                TMP_Character ch;
                if (!fa.characterLookupTable.TryGetValue(cp, out ch) || ch.glyph == null) continue;
                float k = SamplingPointSize / upem;
                float adv = float.Parse(parts[0], System.Globalization.CultureInfo.InvariantCulture) * k;
                var m = ch.glyph.metrics;
                if (System.Math.Abs(m.horizontalAdvance - adv) > 0.6f)
                {
                    ch.glyph.metrics = new UnityEngine.TextCore.GlyphMetrics(
                        m.width, m.height, m.horizontalBearingX, m.horizontalBearingY, adv);
                    fixedCount++;
                }
            }
            if (fixedCount > 0)
                Plugin.Log.LogInfo($"DynamicFont: fixed {fixedCount} bad advances in '{fa.name}' from reference metrics");
            return fixedCount;
        }

        // Bake ALL cyrillic in one batch via the public TryAddCharacters API. The per-character
        // path (TryAddCharacterInternal) reloads the FreeType face for every letter and after
        // ~44 calls starts returning true with empty (0,0,0,0) glyph rects — invisible letters.
        // The batch path loads the face once and packs all glyphs in a single native call.
        private static int PreBakeCyrillic(TMP_FontAsset fa)
        {
            var sb = new System.Text.StringBuilder();
            foreach (uint cp in CyrillicCodepoints()) sb.Append((char)cp);
            string wanted = sb.ToString();
            string missing;
            fa.TryAddCharacters(wanted, out missing);
            if (!string.IsNullOrEmpty(missing))
                Plugin.Log.LogWarning($"DynamicFont: '{fa.name}' could not bake: {missing}");
            return wanted.Length - (missing == null ? 0 : missing.Length);
        }

        private static IEnumerable<uint> CyrillicCodepoints()
        {
            yield return 0x0401; // Ё
            yield return 0x0451; // ё
            for (uint c = 0x0410; c <= 0x044F; c++) yield return c; // А-я
            yield return 0x2116; // №
            // Казахские буквы для пасхалки Эксперимента «Ойбай, шошып кеттім ғой...».
            // Пекутся только в те шрифты, чей ttf их содержит (LiberationSans, RetroGaming);
            // в остальных TryAddCharacters их молча пропустит. См. font_map: Experiment = LiberationSans SDF.
            yield return 0x0456; // і (kaz)
            yield return 0x0493; // ғ (kaz)
        }

        private static void SetPrivate(object obj, string field, object value)
        {
            var fi = obj.GetType().GetField(field, BindingFlags.Instance | BindingFlags.NonPublic);
            if (fi == null) { Plugin.Log.LogWarning($"DynamicFont: field '{field}' not found"); return; }
            fi.SetValue(obj, value);
        }
    }

    // FontEngine.LoadFontFace(Font, ...) cannot load a runtime-created Font. When the Font is
    // one of our markers, load the registered ttf FILE instead; otherwise run the original.
    [HarmonyPatch(typeof(FontEngine), "LoadFontFace", new[] { typeof(Font) })]
    internal static class LoadFontFacePatch_Font
    {
        static bool Prefix(Font font, ref FontEngineError __result)
        {
            var path = DynamicFont.GetSourcePath(font);
            if (path == null) return true;
            __result = FontEngine.LoadFontFace(path, DynamicFont.SamplingPointSize);
            return false;
        }
    }

    [HarmonyPatch(typeof(FontEngine), "LoadFontFace", new[] { typeof(Font), typeof(int) })]
    internal static class LoadFontFacePatch_FontSize
    {
        static bool Prefix(Font font, int pointSize, ref FontEngineError __result)
        {
            var path = DynamicFont.GetSourcePath(font);
            if (path == null) return true;
            __result = FontEngine.LoadFontFace(path, pointSize);
            return false;
        }
    }

    [HarmonyPatch(typeof(FontEngine), "LoadFontFace", new[] { typeof(Font), typeof(int), typeof(int) })]
    internal static class LoadFontFacePatch_FontSizeIndex
    {
        static bool Prefix(Font font, int pointSize, int faceIndex, ref FontEngineError __result)
        {
            var path = DynamicFont.GetSourcePath(font);
            if (path == null) return true;
            __result = FontEngine.LoadFontFace(path, pointSize, faceIndex);
            return false;
        }
    }

    // matchMaterialPreset клонирует материал оригинала (бордовая грань через вершинный цвет +
    // чёрный outline) и подставляет наш RU-атлас. Outline оригинала рассчитан на его атлас
    // (gradientScale ~11, толстые штрихи); на нашем RU-атласе (gradientScale ~10) та же обводка
    // разливается и заливает кириллицу целиком в чёрный. Грань (white × вершинный бордовый) верна —
    // гасим ТОЛЬКО обводку у клонов, где target == один из наших ru.material.
    // Патчится вручную из Plugin.Awake (сигнатура может зависеть от версии TMP) — в try/catch.
    internal static class FallbackMaterialOutlineFix
    {
        // Обводка оригинала (outW=1) на RU-атласе разливается в сплошной чёрный.
        // Полностью гасить — теряется тонкий кант, который есть у латиницы. Поэтому
        // ОГРАНИЧИВАЕМ ширину небольшим значением: остаётся тонкий чёрный кант, без заливки.
        // Значение подобрано визуально (кант как у латиницы, без заливки штриха).
        // Переопределяется из конфига (секция Banner, ключ OutlineWidth).
        internal static float OutlineCap = 0.28f;

        // Грань оригинала тоже раздута: у PixelOperatorOutline _FaceDilate=0.67 (рассчитан на
        // атлас gradientScale=31). На нашем рантайм-атласе (gradientScale=Padding=9) тот же
        // дилейт раздувает белую грань — баннер главы выходил «жирным белым». Занижаем грань
        // (только вниз — тонкие/нераздутые материалы не трогаем). Подбирается под ширину
        // английской латиницы; переопределяется из конфига (секция Banner, ключ FaceDilate).
        internal static float FaceDilateCap = 0.33f;

        internal static void Postfix(Material targetMaterial, Material __result)
        {
            if (__result == null || targetMaterial == null) return;
            if (!FontService.RuMaterialIds.Contains(targetMaterial.GetInstanceID())) return;
            if (__result.HasProperty("_OutlineWidth"))
            {
                float w = __result.GetFloat("_OutlineWidth");
                if (w > OutlineCap) __result.SetFloat("_OutlineWidth", OutlineCap);
            }
            if (__result.HasProperty("_FaceDilate"))
            {
                float d = __result.GetFloat("_FaceDilate");
                if (d > FaceDilateCap) __result.SetFloat("_FaceDilate", FaceDilateCap);
            }
        }
    }
}
