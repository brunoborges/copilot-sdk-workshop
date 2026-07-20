# Client and Model Selection

> **Duration:** ~15 minutes

Start the SDK client, verify its connection, and let the user choose a model.

## 1. Start the client

Replace `workshop-app/Program.cs` with:

```csharp
using GitHub.Copilot;

Console.WriteLine("=== Copilot Accessibility Assistant ===\n");

await using var client = new CopilotClient();
await client.StartAsync();

var pingResponse = await client.PingAsync("hello");
Console.WriteLine($"✅ Copilot client responded: {pingResponse.Message}");
```

`CopilotClient` owns the runtime connection. `await using` disposes it cleanly, and `PingAsync` verifies the authenticated connection.

## 2. Add a model picker

Create `workshop-app/Helpers/ModelSelector.cs`:

```csharp
using GitHub.Copilot;

namespace HelloCopilotSDK.Helpers;

public static class ModelSelector
{
    public static async Task<string?> SelectModelAsync(CopilotClient client)
    {
        var models = (await client.ListModelsAsync())?.ToList();
        if (models is null || models.Count == 0)
        {
            Console.WriteLine("⚠️ Could not fetch models. Using the default model.");
            return null;
        }

        for (var i = 0; i < models.Count; i++)
        {
            Console.WriteLine($"{i + 1}. {models[i].Name}");
        }

        Console.Write($"Select a model (1-{models.Count}) [1]: ");
        var valid = int.TryParse(Console.ReadLine(), out var choice) && choice >= 1 && choice <= models.Count;
        return models[(valid ? choice : 1) - 1].Id;
    }
}
```

Add `using HelloCopilotSDK.Helpers;` and call:

```csharp
var selectedModel = await ModelSelector.SelectModelAsync(client);
```

## Checkpoint

- [ ] The client starts and responds to `PingAsync`.
- [ ] The model list is displayed.
- [ ] `selectedModel` contains the selected model ID.

Next, create a streaming session in [Session and Streaming](03-streaming.md).
