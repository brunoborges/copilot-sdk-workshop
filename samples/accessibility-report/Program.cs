using AccessibilityReport.Helpers;
using GitHub.Copilot;

Console.WriteLine("=== Accessibility Report Generator ===\n");

await using var client = new CopilotClient();
await client.StartAsync();
var selectedModel = await ModelSelector.SelectModelAsync(client);

Console.Write("Enter URL to analyze: ");
var url = Console.ReadLine()?.Trim();

if (string.IsNullOrWhiteSpace(url))
{
    Console.WriteLine("No URL provided. Exiting.");
    return;
}

if (!url.StartsWith("http://") && !url.StartsWith("https://"))
{
    url = "https://" + url;
}

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true,
    OnPermissionRequest = PermissionHandler.ApproveAll,
    Tools = [AccessibilityRuleCatalog.CreateLookupTool()],
    McpServers = new Dictionary<string, McpServerConfig>
    {
        ["playwright"] = new McpStdioServerConfig
        {
            Command = "npx",
            Args = ["@playwright/mcp@0.0.78", "--browser=msedge"],
            Tools = ["*"]
        }
    }
});

Console.WriteLine($"\nAnalyzing: {url}\n");
await ResponseStreamer.SendAndPrintAsync(session, Prompts.CreateReportPrompt(url));

Console.Write("\nWould you like to generate Playwright accessibility tests? (y/n): ");
if (Console.ReadLine()?.Trim().ToLowerInvariant() is "y" or "yes")
{
    Console.Write("Language for tests [TypeScript]: ");
    var language = Console.ReadLine()?.Trim();
    language = string.IsNullOrWhiteSpace(language) ? "TypeScript" : language;

    Console.WriteLine("\nGenerating tests...\n");
    await ResponseStreamer.SendAndPrintAsync(session, Prompts.CreateTestPrompt(url, language));
}
