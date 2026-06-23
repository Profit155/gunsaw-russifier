using System;
using System.Collections.Generic;
using System.Globalization;

namespace GunsawRusFonts
{
    public sealed class LayoutRule
    {
        public string Match { get; }
        public float MinFontScale { get; }
        public bool EnableWrap { get; }
        public int MaxLines { get; }
        public LayoutRule(string match, float minFontScale, bool enableWrap, int maxLines)
        {
            Match = match;
            MinFontScale = minFontScale;
            EnableWrap = enableWrap;
            MaxLines = maxLines;
        }
    }

    public sealed class LayoutRules
    {
        private readonly List<LayoutRule> _rules;

        private LayoutRules(List<LayoutRule> rules) { _rules = rules; }

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
                    list.Add(new LayoutRule(match, scale, wrap, maxl));
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
