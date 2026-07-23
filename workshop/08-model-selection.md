# Optional: Select a model

> **Time:** 10 minutes  
> **Prerequisite:** Complete the seven core steps first.

## What you'll customize

After this extension, the application will list models available to the signed-in user and use the
selected model for the report session.

## How model selection works

The Copilot runtime can expose more than one model. `ListModelsAsync` returns the models available
for the current account, while `SessionConfig.Model` selects one for a new session.

## Swap models without changing the architecture

Model choice can affect latency, capability, and billing. It does not change your local tools, MCP
configuration, or permission policy, so it is easier to understand after the core architecture.

> **Where it fits:** Model selection configures `CopilotSession`; it does not replace the client or
> either tool boundary.

## Add a model picker

Create `workshop-app/Helpers/ModelSelector.cs`:

```csharp
using GitHub.Copilot;

namespace HelloCopilotSDK.Helpers;

public static class ModelSelector
{
    public static async Task<string?> SelectAsync(CopilotClient client)
    {
        var models = (await client.ListModelsAsync())?.ToList();
        if (models is null || models.Count is 0)
        {
            Console.WriteLine("No model list was returned; using the account default.");
            return null;
        }

        Console.WriteLine("Available models:");
        for (var index = 0; index < models.Count; index++)
        {
            Console.WriteLine($"{index + 1}. {models[index].Name}");
        }

        Console.Write($"Choose 1-{models.Count} [1]: ");
        var valid = int.TryParse(Console.ReadLine(), out var choice) &&
                    choice >= 1 &&
                    choice <= models.Count;
        var selected = models[(valid ? choice : 1) - 1];

        Console.WriteLine($"Using {selected.Name}\n");
        return selected.Id;
    }
}
```

After `PingAsync` in `Program.cs`, insert:

```csharp
var selectedModel = await ModelSelector.SelectAsync(client);
```

Then add `Model = selectedModel` to `SessionConfig`:

```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true,
    // Keep the existing permission, local-tool, and MCP configuration.
});
```

Do not remove the rest of the Step 6 session configuration.

## Run it

```bash
dotnet run --project workshop-app
```

Choose a model, enter the workshop target URL, and confirm the same scoped tools still run.

<details>
<summary>Troubleshooting this extension</summary>

| Symptom | Fix |
|---|---|
| No models are listed | The helper deliberately falls back to the account default; verify authentication if this is unexpected. |
| A number is outside the range | The helper safely uses the first model. |
| Tools disappear | Add only `Model = selectedModel`; retain `Tools`, `McpServers`, and `OnPermissionRequest`. |

</details>

> **You are ready to finish when:** the selected model is named and the report still uses both
> scoped tool types.

## Check your understanding

Why was model selection moved out of Step 1?

<details>
<summary>Check your answer</summary>

It is configuration rather than a core agent concept. Deferring it gives learners a useful Copilot
response sooner and keeps the first lesson focused on client and session responsibilities.

</details>

Return to [Step 7: Run and explain the application](07-run-explain.md).
