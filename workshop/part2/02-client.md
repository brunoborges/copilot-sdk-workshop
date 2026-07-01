# Part 2: Client & MCP

> **Duration:** ~10 minutes

In this step you will add the Copilot client startup code, let the user pick a model, and configure the Playwright MCP server so Copilot can drive a real browser.

---

## 1. Add the using

Open `part2/Program.cs` and add at the very top:

```csharp
using GitHub.Copilot;
```

---

## 2. Start the Copilot client

Add the client startup code:

```csharp
// Create and start client
await using var client = new CopilotClient();
await client.StartAsync();

Console.WriteLine("=== Accessibility Report Generator ===");
Console.WriteLine();
```

This is the same pattern you used in Part 1.

---

## 3. Pick a model

Add a small model picker so the user can choose which Copilot model to use:

```csharp
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
```

> **💡 Tip**
> Smaller models such as `mai-code-1-flash` or `claude-sonnet-4.5` are usually faster and cheaper for this task. You can pick any model Copilot exposes.

---

## 4. Create a session config

Add the `SessionConfig` with the Playwright MCP server:

```csharp
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
            Args = ["@playwright/mcp@latest"],
            Tools = ["*"]
        }
    },
};
```

### What this does

| Piece | Purpose |
|-------|---------|
| `Model = selectedModel` | Uses the model the user just picked. |
| `Streaming = true` | Streams the report to the console as it is generated. |
| `OnPermissionRequest = PermissionHandler.ApproveAll` | Auto-approves MCP tool permission requests. |
| `McpServers["playwright"]` | Registers the Playwright MCP server as a stdio process. |
| `Command = "npx"` | Launches the MCP server through npx. |
| `Args = ["@playwright/mcp@latest"]` | Runs the latest Playwright MCP package. |
| `Tools = ["*"]` | Allows the session to use all Playwright tools. |

> [!IMPORTANT]
> `PermissionHandler.ApproveAll` is convenient for a workshop, but in production you should review permission requests carefully.

---

## 5. Create the session

Add the session creation line right after the config:

```csharp
await using var session = await client.CreateSessionAsync(sessionConfig);
```

---

## 6. Checkpoint file so far

Your `part2/Program.cs` should look like this:

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
            Args = ["@playwright/mcp@latest"],
            Tools = ["*"]
        }
    },
};

await using var session = await client.CreateSessionAsync(sessionConfig);
```

---

## Checkpoint

- [ ] `using GitHub.Copilot;` is at the top of `part2/Program.cs`.
- [ ] `CopilotClient` is started with `await using`.
- [ ] The user can pick a model from the list.
- [ ] `SessionConfig` includes the Playwright MCP server configuration.

Next, prompt the user for a URL in [Part 2: URL Input](03-url.md).
