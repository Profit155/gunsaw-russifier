using System.Collections.Generic;
using System.IO;
using TMPro;

namespace GunsawRusFonts
{
    /// <summary>
    /// Attaches cyrillic fallback fonts (built at runtime from ttf files in /fonts)
    /// to the game's TMP font assets, driven by font_map.txt. Latin glyphs keep
    /// rendering from the original asset; cyrillic comes from our matching ttf.
    /// </summary>
    internal static class FontService
    {
        private static readonly Dictionary<string, TMP_FontAsset> _byFile =
            new Dictionary<string, TMP_FontAsset>(System.StringComparer.OrdinalIgnoreCase);
        private static readonly HashSet<int> _seen = new HashSet<int>();

        // Дефолт-материалы RU-фолбэков. matchMaterialPreset клонирует материал оригинала
        // и подставляет наш атлас как target == ru.material — по этому ID узнаём «наш» клон,
        // чтобы погасить разливающуюся чёрную обводку (см. FallbackMaterialOutlineFix).
        internal static readonly HashSet<int> RuMaterialIds = new HashSet<int>();

        public static void Attach(TMP_FontAsset fa)
        {
            if (fa == null) return;
            int id = fa.GetInstanceID();
            if (!_seen.Add(id)) return;

            var entry = Plugin.FontMap.Resolve(fa.name);
            if (entry == null)
            {
                Plugin.Log.LogWarning($"FontService: no font_map entry for '{fa.name}'");
                return;
            }
            var ru = GetOrBuild(entry.Ttf);
            if (ru == null || ru == fa) return;

            if (fa.fallbackFontAssetTable == null)
                fa.fallbackFontAssetTable = new List<TMP_FontAsset>();
            fa.fallbackFontAssetTable.Insert(0, ru);
            Plugin.Log.LogInfo($"FontService: '{fa.name}' += fallback '{ru.name}'");
        }

        private static TMP_FontAsset GetOrBuild(string ttfFile)
        {
            if (_byFile.TryGetValue(ttfFile, out var cached)) return cached;
            TMP_FontAsset built = null;
            var path = Path.Combine(Plugin.FontsDir, ttfFile);
            if (File.Exists(path))
            {
                built = DynamicFont.Build(path,
                                          "RU_" + Path.GetFileNameWithoutExtension(ttfFile));
                // Страховка: если FreeType отдал мусорные advance, правим по эталону из ttf.
                DynamicFont.ApplyReferenceMetrics(built, Path.ChangeExtension(path, ".metrics.txt"));
                if (built != null && built.material != null)
                    RuMaterialIds.Add(built.material.GetInstanceID());
            }
            else
            {
                Plugin.Log.LogError($"FontService: ttf not found: {path}");
            }
            _byFile[ttfFile] = built; // кэшируем и null, чтобы не молотить диск
            return built;
        }
    }
}
