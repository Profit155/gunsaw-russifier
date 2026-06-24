using System.IO;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;

namespace GunsawRusFonts
{
    [BepInPlugin("gunsaw.rusfonts", "Gunsaw RUS Fonts & Layout", "0.2.0")]
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

            BindTuningConfig();

            var harmony = new Harmony("gunsaw.rusfonts");
            harmony.PatchAll();
            PatchFallbackOutlineFix(harmony);
            LayoutService.Hook();
            EnableMatchMaterialPresets();
            Log.LogInfo("GunsawRusFonts initialized");
        }

        // Вес грани/обводки кириллицы в контурных шрифтах (PixelOperatorOutline = баннер главы).
        // Вынесено в конфиг, чтобы подбирать под ширину английской латиницы без пересборки DLL.
        private void BindTuningConfig()
        {
            var dilate = Config.Bind("Banner", "FaceDilate", 0.33f,
                "Вес белой грани кириллицы в контурных шрифтах (напр. баннер главы). " +
                "Оригинал = 0.67 (на нашем атласе выглядит жирно), 0 = тонко. " +
                "Подбери под ширину английской латиницы. Разумный диапазон 0..0.67.");
            FallbackMaterialOutlineFix.FaceDilateCap = dilate.Value;

            var outline = Config.Bind("Banner", "OutlineWidth", 0.28f,
                "Толщина чёрной обводки кириллицы в контурных шрифтах. 0 = без обводки, больше = толще кант.");
            FallbackMaterialOutlineFix.OutlineCap = outline.Value;

            Log.LogInfo($"tuning: Banner.FaceDilate={dilate.Value}, Banner.OutlineWidth={outline.Value}");
        }

        private static FontMap LoadFontMap(string path)
        {
            try { return File.Exists(path) ? FontMap.Parse(File.ReadAllText(path)) : FontMap.Parse(""); }
            catch (System.Exception e) { Log.LogError($"font_map load error: {e}"); return FontMap.Parse(""); }
        }

        // Без этого глифы из фолбэка рисуются дефолтным материалом RU-шрифта:
        // теряются цвет заливки и обводка оригинала (чёрные реплики становились
        // оранжевыми — белая заливка × вершинный цвет). С Match Material Presets
        // TMP клонирует материал оригинала и лишь подменяет в нём атлас фолбэка.
        // Гасим разливающуюся чёрную обводку на клон-материалах RU-фолбэка.
        // Сигнатуру резолвим рефлексией (зависит от версии TMP) и патчим изолированно.
        private static void PatchFallbackOutlineFix(Harmony harmony)
        {
            try
            {
                var m = HarmonyLib.AccessTools.Method(typeof(TMPro.TMP_MaterialManager),
                    "GetFallbackMaterial", new[] { typeof(UnityEngine.Material), typeof(UnityEngine.Material) });
                if (m == null) { Log.LogWarning("outline-fix: GetFallbackMaterial(Material,Material) not found"); return; }
                harmony.Patch(m, postfix: new HarmonyMethod(
                    typeof(FallbackMaterialOutlineFix).GetMethod("Postfix",
                        System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)));
                Log.LogInfo("outline-fix: patched TMP_MaterialManager.GetFallbackMaterial");
            }
            catch (System.Exception e) { Log.LogError($"outline-fix patch failed: {e.Message}"); }
        }

        private static void EnableMatchMaterialPresets()
        {
            try
            {
                var settings = TMPro.TMP_Settings.instance;
                var fi = typeof(TMPro.TMP_Settings).GetField("m_matchMaterialPreset",
                    System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                if (settings != null && fi != null)
                {
                    fi.SetValue(settings, true);
                    Log.LogInfo("TMP_Settings.matchMaterialPreset = true");
                }
                else
                {
                    Log.LogWarning("matchMaterialPreset: settings or field not found");
                }
            }
            catch (System.Exception e) { Log.LogError($"matchMaterialPreset: {e.Message}"); }
        }

        private static LayoutRules LoadLayoutRules(string path)
        {
            try { return File.Exists(path) ? LayoutRules.Parse(File.ReadAllText(path)) : LayoutRules.Parse(""); }
            catch (System.Exception e) { Log.LogError($"layout_rules load error: {e}"); return LayoutRules.Parse(""); }
        }
    }

    // Каждому включающемуся TMP-тексту цепляем кириллический фолбэк его шрифта.
    // Вёрстку правит LayoutService по событию изменения текста (только кириллица).
    [HarmonyPatch(typeof(TMPro.TextMeshProUGUI), "OnEnable")]
    internal static class TmpUguiEnableHook
    {
        static void Postfix(TMPro.TextMeshProUGUI __instance)
        {
            try { FontService.Attach(__instance.font); } catch { }
        }
    }

    [HarmonyPatch(typeof(TMPro.TextMeshPro), "OnEnable")]
    internal static class TmpWorldEnableHook
    {
        static void Postfix(TMPro.TextMeshPro __instance)
        {
            try { FontService.Attach(__instance.font); } catch { }
        }
    }

    // Разведка legacy-текстов (Task 8d): использует ли игра PerfectDOSVGA437 и пр.
    [HarmonyPatch(typeof(UnityEngine.UI.Text), "OnEnable")]
    internal static class LegacyTextHook
    {
        private static readonly System.Collections.Generic.HashSet<string> _seen =
            new System.Collections.Generic.HashSet<string>();

        static void Postfix(UnityEngine.UI.Text __instance)
        {
            try
            {
                string f = __instance.font != null ? __instance.font.name : "(null)";
                if (_seen.Add(f))
                    Plugin.Log.LogInfo($"LegacyText: font '{f}' first seen on '{__instance.gameObject.name}'");
            }
            catch { }
        }
    }
}
