using System;
using System.IO;
using System.Linq;
using System.Reflection;

class P
{
    static string managed = @"C:\Users\User\Downloads\gunsaw-demo-win\Gunsaw_Data\Managed";

    static string Sig(MethodInfo m) =>
        (m.IsPublic ? "public " : m.IsAssembly ? "internal " : m.IsPrivate ? "private " : "protected ") +
        m.ReturnType.Name + " " + m.Name + "(" +
        string.Join(", ", m.GetParameters().Select(p =>
            (p.IsOut ? "out " : p.ParameterType.IsByRef ? "ref " : "") +
            p.ParameterType.Name.TrimEnd('&') + " " + p.Name)) + ")";

    static void Main()
    {
        var resolver = new PathAssemblyResolver(Directory.GetFiles(managed, "*.dll"));
        using var mlc = new MetadataLoadContext(resolver);
        var tmp = mlc.LoadFromAssemblyPath(Path.Combine(managed, "Unity.TextMeshPro.dll"));
        var tc = mlc.LoadFromAssemblyPath(Path.Combine(managed, "UnityEngine.TextCoreModule.dll"));

        var fa = tmp.GetType("TMPro.TMP_FontAsset");

        Console.WriteLine("=== TMP_FontAsset: methods matching Load/Face ===");
        foreach (var m in fa.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static)
                            .Where(m => m.Name.Contains("Load") || m.Name.Contains("Face")))
            Console.WriteLine("  " + Sig(m));

        Console.WriteLine("=== TMP_FontAsset: fields matching Source/Missing/AtlasTexture/Face ===");
        foreach (var f in fa.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
                            .Where(f => f.Name.Contains("Source") || f.Name.Contains("Missing") ||
                                        f.Name.Contains("AtlasTexture") || f.Name.Contains("FaceIndex")))
            Console.WriteLine("  " + f.FieldType.Name + " " + f.Name);

        var fe = tc.GetType("UnityEngine.TextCore.LowLevel.FontEngine");
        Console.WriteLine("=== FontEngine: LoadFontFace overloads / ResetAtlasTexture / TryAddGlyphToTexture ===");
        foreach (var m in fe.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static)
                            .Where(m => m.Name == "LoadFontFace" || m.Name.Contains("ResetAtlas") || m.Name == "TryAddGlyphToTexture"))
            Console.WriteLine("  " + Sig(m));

        Console.WriteLine("=== FaceInfo.pointSize type ===");
        var fi = tc.GetType("UnityEngine.TextCore.FaceInfo");
        var ps = fi.GetProperty("pointSize");
        Console.WriteLine("  pointSize : " + ps.PropertyType.Name);
    }
}
