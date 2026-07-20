using GitHub.Copilot;
using HelloCopilotSDK.Helpers;

Console.WriteLine("===============================================");
Console.WriteLine("   ♿ Copilot Accessibility Rule Assistant");
Console.WriteLine("===============================================\n");

await using var client = new CopilotClient();
await client.StartAsync();

var pingResponse = await client.PingAsync("hello");
Console.WriteLine($"✅ Copilot client responded: {pingResponse.Message}");

var selectedModel = await ModelSelector.SelectModelAsync(client);
var session = await CreateSessionAsync(client, selectedModel);

try
{
    PrintHelp();

    while (true)
    {
        Console.Write("You: ");
        var input = Console.ReadLine()?.Trim();

        if (string.IsNullOrWhiteSpace(input))
        {
            continue;
        }

        if (input is "exit" or "quit")
        {
            Console.WriteLine("\n👋 Goodbye!");
            break;
        }

        if (input == "help")
        {
            PrintHelp();
            continue;
        }

        if (input == "clear")
        {
            Console.Clear();
            PrintHelp();
            continue;
        }

        if (input == "model")
        {
            selectedModel = await ModelSelector.SelectModelAsync(client);
            var replacementSession = await CreateSessionAsync(client, selectedModel);
            await session.DisposeAsync();
            session = replacementSession;
            Console.WriteLine("🔄 Model switched. The accessibility tool is still available.\n");
            continue;
        }

        var prompt = input.StartsWith("rule ", StringComparison.OrdinalIgnoreCase)
            ? $"Use the accessibility_rule_lookup tool to answer this question: {input[5..]}"
            : input;

        Console.Write("Copilot: ");
        await ResponseStreamer.SendAndPrintAsync(session, prompt);
    }
}
finally
{
    await session.DisposeAsync();
}

static Task<CopilotSession> CreateSessionAsync(CopilotClient client, string? model) =>
    client.CreateSessionAsync(new SessionConfig
    {
        Model = model,
        Streaming = true,
        Tools = [AccessibilityRuleCatalog.CreateLookupTool()]
    });

static void PrintHelp()
{
    Console.WriteLine("\nAsk an accessibility question in plain language.");
    Console.WriteLine("Examples:");
    Console.WriteLine("  rule What WCAG rule applies when an image has no alt text?");
    Console.WriteLine("  rule How do I fix an input without a label?");
    Console.WriteLine("  rule Why does a page need a main landmark?");
    Console.WriteLine("Commands: model | clear | help | exit\n");
}
