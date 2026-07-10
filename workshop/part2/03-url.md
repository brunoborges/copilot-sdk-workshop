# Part 2: URL Input

> **Duration:** ~5 minutes

In this step you will prompt the user for a URL, ensure it has a scheme, and prepare the analysis prompt.

---

## 1. Prompt for the URL

After the header, add the input prompt:

```csharp
Console.Write("Enter URL to analyze: ");
var url = Console.ReadLine()?.Trim();
```

---

## 2. Validate the URL

Add the validation block:

```csharp
if (string.IsNullOrWhiteSpace(url))
{
    Console.WriteLine("No URL provided. Exiting.");
    return;
}

// Ensure URL has a scheme
if (!url.StartsWith("http://") && !url.StartsWith("https://"))
{
    url = "https://" + url;
}

Console.WriteLine($"\nAnalyzing: {url}");
Console.WriteLine("Please wait...\n");
```

This small validation step makes the tool friendlier: users can type `example.com` instead of `https://example.com`.

---

## 3. Prepare the analysis instruction

For now, add a placeholder prompt after the URL block:

```csharp
var prompt = $"""
    Use the Playwright MCP server to analyze the accessibility of this webpage: {url}

    Please:
    1. Navigate to the URL using playwright-browser_navigate
    2. Take an accessibility snapshot using playwright-browser_snapshot
    3. Analyze the snapshot and provide a detailed accessibility report
    """;
```

You will expand this prompt in [Part 2: Report Prompt](05-prompt.md) to produce the formatted report.

---

## 4. Checkpoint file so far

```csharp
using GitHub.Copilot;

// Create and start client
await using var client = new CopilotClient();
await client.StartAsync();

Console.WriteLine("=== Accessibility Report Generator ===");
Console.WriteLine();

// Pick a model
var models = await client.ListModelsAsync();
if (models is null || !models.Any())
{
    Console.WriteLine("⚠️ Could not fetch models. Using default model.");
}

string? selectedModel = null;
if (models is not null && models.Any())
{
    var modelList = models.ToList();
    Console.WriteLine("\n🤖 Select a model:");
    for (var i = 0; i < modelList.Count; i++)
    {
        var model = modelList[i];
        Console.WriteLine($"   {i + 1}. {model.Name} (multiplier: {model.Billing?.Multiplier ?? 1}x)");
    }

    Console.Write($"\nEnter choice (1-{modelList.Count}) [default: 1]: ");
    var input = Console.ReadLine()?.Trim();

    if (string.IsNullOrWhiteSpace(input) || !int.TryParse(input, out var choice))
    {
        choice = 1;
    }

    if (choice < 1 || choice > modelList.Count)
    {
        choice = 1;
    }

    selectedModel = modelList[choice - 1].Id;
    Console.WriteLine($"✅ Selected: {modelList[choice - 1].Name}\n");
}

Console.Write("Enter URL to analyze: ");
var url = Console.ReadLine()?.Trim();

if (string.IsNullOrWhiteSpace(url))
{
    Console.WriteLine("No URL provided. Exiting.");
    return;
}

// Ensure URL has a scheme
if (!url.StartsWith("http://") && !url.StartsWith("https://"))
{
    url = "https://" + url;
}

Console.WriteLine($"\nAnalyzing: {url}");
Console.WriteLine("Please wait...\n");

// Create a session with Playwright MCP server
var sessionConfig = new SessionConfig
{
    Model = selectedModel,
    Streaming = true,
    OnPermissionRequest = PermissionHandler.ApproveAll,
    McpServers = new Dictionary<string, McpServerConfig>()
    {
        ["playwright"] = new McpStdioServerConfig
        {
            Command = "npx",
            Args = ["@playwright/mcp@0.0.78", "--browser=msedge"],
            Tools = ["*"]
        }
    },
};

await using var session = await client.CreateSessionAsync(sessionConfig);

var prompt = $"""
    Use the Playwright MCP server to analyze the accessibility of this webpage: {url}

    Please:
    1. Navigate to the URL using playwright-browser_navigate
    2. Take an accessibility snapshot using playwright-browser_snapshot
    3. Analyze the snapshot and provide a detailed accessibility report
    """;
```

---

## Checkpoint

- [ ] The app prompts for a URL.
[ ] `https://` is added when no scheme is present.
- [ ] A basic analysis prompt is defined.

Next, add streaming event handling in [Part 2: Streaming](04-streaming.md).
