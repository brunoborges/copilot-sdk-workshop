namespace hello_copilot_sdk.Helpers;

public static class DemoPrompts
{
    private static readonly Dictionary<string, string> DemoLookup = new(StringComparer.OrdinalIgnoreCase)
    {
        ["1"] = "Review this C# method for potential SQL injection vulnerabilities:\n\npublic List<User> GetUsers(string name)\n{\n    using var conn = new SqlConnection(_connectionString);\n    var cmd = new SqlCommand(\"SELECT * FROM Users WHERE Name = '\" + name + \"'\", conn);\n    conn.Open();\n    var reader = cmd.ExecuteReader();\n    // ...\n}",
        ["2"] = "Explain how to implement a binary search tree in C# with insert and search operations.",
        ["3"] = "Find the bug in this async method and suggest a fix:\n\npublic async Task<string> FetchDataAsync()\n{\n    var client = new HttpClient();\n    var response = client.GetAsync(\"https://example.com/data\");\n    return await response.Result.Content.ReadAsStringAsync();\n}",
        ["4"] = "Describe the repository pattern and when it makes sense to use it in a .NET application.",
        ["5"] = "Design a REST API for a simple task-management system. Include endpoints, HTTP methods, and example request/response payloads.",
        ["6"] = "Suggest performance optimizations for a .NET 10 minimal API that queries a SQL database and returns JSON."
    };

    public static void PrintDemoPrompts()
    {
        Console.WriteLine("\n📚 Demo Prompts");
        Console.WriteLine("   demo 1: Code Review");
        Console.WriteLine("   demo 2: Algorithm Help");
        Console.WriteLine("   demo 3: Bug Finding");
        Console.WriteLine("   demo 4: Design Pattern");
        Console.WriteLine("   demo 5: API Design");
        Console.WriteLine("   demo 6: Performance");
        Console.WriteLine();
    }

    public static string? GetDemoPrompt(string input)
    {
        var parts = input.Split(' ', 2);
        if (parts.Length >= 2 && DemoLookup.TryGetValue(parts[1].Trim(), out var prompt))
        {
            return prompt;
        }

        return null;
    }
}
