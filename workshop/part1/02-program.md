# Part 1: Program.cs

> **Duration:** ~10 minutes

In this step you will write the main entry point of the chat app. It checks prerequisites, selects a model, starts the Copilot client, creates a session, and runs a simple interactive loop.

---

## 1. Start with a minimal Program.cs

Open `part1/Program.cs` and replace its contents with this tiny runnable skeleton:

```csharp
using GitHub.Copilot;

Console.WriteLine("=====================================");
Console.WriteLine("   🤖 Hello GitHub Copilot SDK (.NET)");
Console.WriteLine("=====================================\n");

// 1. Check prerequisites
Console.WriteLine("🔍 Checking prerequisites...");
// TODO: Add CliChecker helper in the next step.

// 2. Select a model
// TODO: Add ModelSelector helper in the next step.

// 3. Start the Copilot client and create a session
Console.WriteLine("🚀 Starting Copilot client...");
await using var client = new CopilotClient();
await client.StartAsync();

var pingResponse = await client.PingAsync("hello");
Console.WriteLine($"   ✅ Copilot client responded: {pingResponse}\n");

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = null, // We will set this after adding ModelSelector.
    Streaming = true
});

// 4. Interactive chat loop
Console.WriteLine("💬 Interactive Chat Mode");
Console.WriteLine("   Type a message and press Enter.");
Console.WriteLine("   Commands: model | clear | exit\n");

while (true)
{
    Console.Write("You: ");
    var input = Console.ReadLine();

    if (string.IsNullOrWhiteSpace(input))
    {
        continue;
    }

    var command = input.Trim().ToLowerInvariant();

    if (command is "exit" or "quit")
    {
        Console.WriteLine("\n👋 Goodbye!");
        break;
    }

    if (command == "clear")
    {
        Console.Clear();
        Console.WriteLine("💬 Interactive Chat Mode\n");
        continue;
    }

    Console.Write("Copilot: ");
    // TODO: Stream response via ChatHelper.
    Console.WriteLine();
}
```

This file already shows the core SDK pattern:

- `new CopilotClient()` creates the client.
- `client.StartAsync()` connects to Copilot.
- `client.PingAsync("hello")` verifies the connection.
- `client.CreateSessionAsync(...)` creates a conversation session.
- `Streaming = true` enables token-by-token responses.

---

## 2. Build the project

```bash
dotnet build part1
```

The build will succeed, but the app does not do much yet. In the next two steps you will add the helper classes that fill in the `TODO` comments.

---

## Key concepts

### CopilotClient

`CopilotClient` is the top-level object for interacting with the GitHub Copilot SDK. You typically create one per application and reuse it for multiple sessions.

### SessionConfig

`SessionConfig` controls how a session behaves. Important properties include:

| Property | Purpose |
|----------|---------|
| `Model` | The model ID to use (e.g., `claude-sonnet-4.5`, `mai-code-1-flash`). `null` uses the default. |
| `Streaming` | When `true`, responses arrive as `AssistantMessageDeltaEvent` chunks. |
| `McpServers` | Dictionary of MCP servers to attach (used in Part 2). |

### Disposal

Both `CopilotClient` and `CopilotSession` implement `IAsyncDisposable`. The `await using` statements ensure they are cleaned up correctly.

---

## Checkpoint

- [ ] `part1/Program.cs` matches the skeleton above.
- [ ] `dotnet build part1` succeeds.
- [ ] You can explain what `CopilotClient`, `SessionConfig`, and `CopilotSession` do.

Next, add the prerequisite checker and model selector in [Part 1: Helpers (1/2)](03-helpers-1.md).
