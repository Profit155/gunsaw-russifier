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
