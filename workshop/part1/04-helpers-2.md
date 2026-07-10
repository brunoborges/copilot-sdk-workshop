# Part 1: Helpers (2/2)

> **Duration:** ~10 minutes

In this step you will add the final two helpers:

1. `ChatHelper.cs` — streams a response from a `CopilotSession`.
2. `DemoPrompts.cs` — provides built-in prompts so users can quickly test the app.

---

## 1. Create ChatHelper.cs with the event handler

Create `part1/Helpers/ChatHelper.cs` and start with the `using` and class shell:

```csharp
using GitHub.Copilot;

namespace HelloCopilotSDK.Helpers;

public static class ChatHelper
{
    public static async Task SendMessageAndStreamResponse(CopilotSession session, string message)
    {
        var tcs = new TaskCompletionSource();
        var hasStreamedContent = false;

        // Event handler added in the next chunk.

        await session.SendAsync(new MessageOptions { Prompt = message });
        await tcs.Task;
    }
}
```

---

## 2. Add the streaming event handler

Inside `SendMessageAndStreamResponse`, add the handler before `session.SendAsync`:

```csharp
        session.On<SessionEvent>(evt =>
        {
            switch (evt)
            {
                case AssistantMessageDeltaEvent delta:
                    if (!string.IsNullOrEmpty(delta.Data.DeltaContent))
                    {
                        hasStreamedContent = true;
                        Console.Write(delta.Data.DeltaContent);
                    }
                    break;

                case AssistantMessageEvent msg:
                    if (!hasStreamedContent)
                    {
                        Console.Write(msg.Data.Content);
                    }
                    break;

                case SessionIdleEvent:
                    Console.WriteLine();
                    tcs.TrySetResult();
                    break;

                case SessionErrorEvent err:
                    Console.WriteLine($"\n❌ Error: {err.Data.Message}");
                    tcs.TrySetResult();
                    break;
            }
        });
```

### How streaming works

When `Streaming = true`, the SDK raises events as the model generates tokens:

| Event | Meaning |
|-------|---------|
| `AssistantMessageDeltaEvent` | A new chunk of text has arrived. Print it immediately. |
| `AssistantMessageEvent` | A complete non-streaming message (fallback). |
| `SessionIdleEvent` | The model has finished responding. |
| `SessionErrorEvent` | Something went wrong. |

The SDK emits a complete `AssistantMessageEvent` after a streamed response. `hasStreamedContent` prevents that completed message from repeating deltas already printed to the console, while still displaying a response when no streaming content arrives.

`TaskCompletionSource` lets us turn the event-based stream into an `await`-able method.

---

## 3. Create DemoPrompts.cs with the lookup

Create `part1/Helpers/DemoPrompts.cs` and add the dictionary of demo prompts:

```csharp
namespace HelloCopilotSDK.Helpers;

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
}
```

---

## 4. Add the prompt printer

Add these methods to `DemoPrompts`:

```csharp
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
```

---

## 5. Update `part1/Program.cs` to use the helpers

Add the `using`:

```csharp
using HelloCopilotSDK.Helpers;
```

Replace the session declaration and chat-loop body with the full version:

```csharp
var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true
});

try
{
// 4. Interactive chat loop
DemoPrompts.PrintDemoPrompts();
Console.WriteLine("💬 Interactive Chat Mode");
Console.WriteLine("   Type a message and press Enter.");
Console.WriteLine("   Commands: model | clear | demo <1-6> | exit\n");

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

    if (command == "model")
    {
        selectedModel = await ModelSelector.SelectModelAsync(client);
        var replacementSession = await client.CreateSessionAsync(new SessionConfig
        {
            Model = selectedModel,
            Streaming = true
        });
        var previousSession = session;
        session = replacementSession;
        await previousSession.DisposeAsync();
        Console.WriteLine("🔄 Model switched. Continue chatting.\n");
        continue;
    }

    if (command == "clear")
    {
        Console.Clear();
        DemoPrompts.PrintDemoPrompts();
        Console.WriteLine("💬 Interactive Chat Mode\n");
        continue;
    }

    if (command.StartsWith("demo ", StringComparison.OrdinalIgnoreCase))
    {
        var prompt = DemoPrompts.GetDemoPrompt(input);
        if (prompt is null)
        {
            Console.WriteLine("❌ Unknown demo. Use demo 1 through demo 6.\n");
            continue;
        }

        Console.WriteLine($"\n🎯 Running: {input}");
        Console.Write("Copilot: ");
        await ChatHelper.SendMessageAndStreamResponse(session, prompt);
        Console.WriteLine();
        continue;
    }

    Console.Write("Copilot: ");
    await ChatHelper.SendMessageAndStreamResponse(session, input);
    Console.WriteLine();
}
}
finally
{
    await session.DisposeAsync();
}
```

> [!NOTE]
> The `model` command creates a replacement session before switching the active reference and disposing the previous session. This keeps later demo prompts and free-form messages streaming from the newly selected model. The `finally` block disposes whichever session is active when the app exits.

---

## 4. Build

```bash
dotnet build part1
```

Fix any compiler errors before moving on.

---

## Checkpoint

- [ ] `part1/Helpers/ChatHelper.cs` is created.
- [ ] `part1/Helpers/DemoPrompts.cs` is created.
- [ ] `part1/Program.cs` calls `ChatHelper.SendMessageAndStreamResponse`.
- [ ] `dotnet build part1` succeeds.

Next, run the finished app in [Part 1: Run](05-run.md).
