using System.Collections.Generic;
using TMPro;

namespace GunsawRusFonts
{
    /// <summary>
    /// Точечная подгонка кегля для русских строк, которые не влезают в свой прямоугольник.
    ///
    /// Почему НЕ глобальный TMP enableAutoSizing: тексты Ui сидят в layout-группах Unity,
    /// и динамический autosize входит с ними в обратную связь (autosize меняет кегль →
    /// layout пересчитывает прямоугольник → autosize ужимает дальше) — текст «схлопывается»
    /// с каждым событием. Поэтому по умолчанию мы НЕ трогаем ничего: русский влезает в
    /// большинство родных прямоугольников. Для конкретных проблемных объектов задаём в
    /// layout_rules.txt ФИКСИРОВАННЫЙ масштаб кегля (одноразовая правка fontSize, без autosize).
    ///
    /// Формат правила: подстрокаИмени|scale|enableWrap|maxLines
    ///   scale 0..1 — доля исходного кегля (0.8 = 80%); 0 или ≥1 — не масштабировать.
    /// </summary>
    internal static class LayoutService
    {
        private static bool _hooked;

        // instanceID -> исходный (дизайнерский) кегль; нужен как guard от само-зацикливания
        // нашей же правки (set fontSize → новое TEXT_CHANGED). Объекты UI пересоздаются,
        // так что записи устаревают — периодически чистим, чтобы словарь не рос бесконечно.
        private static readonly Dictionary<int, float> _origSize = new Dictionary<int, float>();

        public static void Hook()
        {
            if (_hooked) return;
            _hooked = true;
            TMPro_EventManager.TEXT_CHANGED_EVENT.Add(OnTextChanged);
        }

        private static void OnTextChanged(UnityEngine.Object obj)
        {
            var text = obj as TMP_Text;
            if (text == null) return;
            try { Apply(text); } catch { }
        }

        private static void Apply(TMP_Text text)
        {
            var rule = Plugin.LayoutRules.Match(text.gameObject.name);
            if (rule == null) return;                       // нет правила — не трогаем
            float scale = rule.MinFontScale;
            if (scale <= 0f || scale >= 1f)                 // масштабирование не задано
            {
                ApplyWrap(text, rule);
                return;
            }
            if (!HasCyrillic(text.text)) return;            // латиницу не трогаем

            int id = text.GetInstanceID();
            if (!_origSize.TryGetValue(id, out float orig))
            {
                if (_origSize.Count > 4096) _origSize.Clear(); // защита от роста на пересоздаваемых объектах
                orig = text.fontSize;
                if (orig <= 0f) return;
                _origSize[id] = orig;
            }

            ApplyWrap(text, rule);
            float target = orig * scale;
            if (System.Math.Abs(text.fontSize - target) > 0.05f)
            {
                if (text.enableAutoSizing) text.enableAutoSizing = false;
                text.fontSize = target;                     // фиксированный кегль, без autosize
            }
        }

        private static void ApplyWrap(TMP_Text text, LayoutRule rule)
        {
            if (rule.EnableWrap && !text.enableWordWrapping) text.enableWordWrapping = true;
            if (rule.MaxLines > 0 && text.maxVisibleLines != rule.MaxLines) text.maxVisibleLines = rule.MaxLines;
        }

        private static bool HasCyrillic(string s)
        {
            if (string.IsNullOrEmpty(s)) return false;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if ((c >= 'Ѐ' && c <= 'ӿ') || c == '№') return true; // кириллица, №
            }
            return false;
        }
    }
}
