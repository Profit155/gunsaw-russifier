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

    [Fact]
    public void Parse_ValueOnlyPipe_IsIgnored()
    {
        var map = FontMap.Parse("A=|");
        Assert.Equal(0, map.Count);
    }
}
