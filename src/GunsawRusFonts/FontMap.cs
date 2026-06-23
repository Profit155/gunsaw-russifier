using System;
using System.Collections.Generic;
using System.IO;

namespace GunsawRusFonts
{
    public sealed class FontEntry
    {
        public string Ttf { get; }
        public string Face { get; }
        public FontEntry(string ttf, string face) { Ttf = ttf; Face = face; }
    }

    public sealed class FontMap
    {
        private readonly Dictionary<string, FontEntry> _map;

        private FontMap(Dictionary<string, FontEntry> map) { _map = map; }

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
                    d[key] = new FontEntry(ttf, face);
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
