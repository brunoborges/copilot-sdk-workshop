# Part 1: Helpers (1/2)

> **Duration:** ~10 minutes

In this step you will add two helpers:

1. `CliChecker.cs` — verifies the Copilot CLI is installed and the user is authenticated.
2. `ModelSelector.cs` — lists available models and lets you pick one.

---

## 1. Create the status record

Create `part1/Helpers/CliChecker.cs` and start with the data record:

```csharp
using System.Diagnostics;

namespace HelloCopilotSDK.Helpers;

public record CopilotStatus(
    bool IsInstalled,
    bool IsTokenSet,
    bool IsAuthenticated,
    string? ErrorMessage);
```

A `record` is a concise way to hold immutable status data.

---

## 2. Add the ready check

Still in `part1/Helpers/CliChecker.cs`, add the `CliChecker` class:

```csharp
public static class CliChecker
{
    public static bool IsReady(CopilotStatus status)
        => status.IsInstalled && (status.IsTokenSet || status.IsAuthenticated);
}
```

`IsReady` returns `true` when the CLI is installed **and** the user has either a token or an authenticated CLI session.

---

## 3. Check the Copilot CLI version

Add the first async method to `CliChecker`:

```csharp
    public static async Task<CopilotStatus> CheckCopilotStatusAsync()
    {
        var isTokenSet = !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("GH_TOKEN"));

        try
        {
            var version = await RunCommandAsync("copilot", "--version");
            if (string.IsNullOrWhiteSpace(version))
            {
                return new CopilotStatus(false, isTokenSet, false, "Copilot CLI is installed but returned no version.");
            }
        }
        catch (Exception ex)
        {
            return new CopilotStatus(false, isTokenSet, false, $"Copilot CLI not found: {ex.Message}");
        }

        // Auth check will go here in the next chunk.
        return new CopilotStatus(true, isTokenSet, false, null);
    }
```

Run `dotnet build part1` now to make sure the file compiles.

---

## 4. Check authentication

Replace the placeholder return with the auth check:

```csharp
        try
        {
            var authOutput = await RunCommandAsync("copilot", "auth status");
            var isAuthenticated = authOutput.Contains("Logged in", StringComparison.OrdinalIgnoreCase)
                               || authOutput.Contains("Authenticated", StringComparison.OrdinalIgnoreCase);

            if (!isAuthenticated && !isTokenSet)
            {
                return new CopilotStatus(true, false, false, "Not authenticated. Run 'copilot auth login' or set GH_TOKEN.");
            }

            return new CopilotStatus(true, isTokenSet, isAuthenticated, null);
        }
        catch (Exception ex)
        {
            return new CopilotStatus(true, isTokenSet, false, $"Could not verify auth status: {ex.Message}");
        }
```

---

## 5. Add the command runner

Add the private helper that runs shell commands:

```csharp
    private static async Task<string> RunCommandAsync(string command, string arguments)
    {
        var psi = new ProcessStartInfo
        {
            FileName = command,
            Arguments = arguments,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using var process = Process.Start(psi)
            ?? throw new InvalidOperationException($"Could not start process: {command}");

        await process.WaitForExitAsync();
        var output = await process.StandardOutput.ReadToEndAsync();
        var error = await process.StandardError.ReadToEndAsync();

        if (process.ExitCode != 0 && string.IsNullOrWhiteSpace(output))
        {
            throw new InvalidOperationException(error);
        }

        return output + error;
    }
```

---

## 6. Create ModelSelector.cs

Create `part1/Helpers/ModelSelector.cs` with the model-listing logic:

```csharp
using GitHub.Copilot;

namespace HelloCopilotSDK.Helpers;

public static class ModelSelector
{
    public static async Task<string?> SelectModelAsync()
    {
        var models = await GetModelsFromSdkAsync();

        if (models is null || models.Count == 0)
        {
            Console.WriteLine("⚠️ Could not fetch models. Using default model.");
            return null;
        }

        Console.WriteLine("\n🤖 Select a model:");
        for (var i = 0; i < models.Count; i++)
        {
            var model = models[i];
            Console.WriteLine($"   {i + 1}. {model.Name} (multiplier: {model.Billing?.Multiplier ?? 1}x)");
        }

        Console.Write($"\nEnter choice (1-{models.Count}) [default: 1]: ");
        var input = Console.ReadLine()?.Trim();

        if (string.IsNullOrWhiteSpace(input) || !int.TryParse(input, out var choice))
        {
            choice = 1;
        }

        if (choice < 1 || choice > models.Count)
        {
            choice = 1;
        }

        var selected = models[choice - 1];
        Console.WriteLine($"✅ Selected: {selected.Name}\n");
        return selected.Id;
    }

    private static async Task<List<ModelInfo>?> GetModelsFromSdkAsync()
    {
        using var client = new CopilotClient();
        await client.StartAsync();
        var models = await client.ListModelsAsync();
        await client.StopAsync();
        return models?.ToList();
    }
}
```

`ModelInfo` is provided by the SDK and contains `Id`, `Name`, and `PricingMultiplier`.

---

## 7. Wire the helpers into Program.cs

Update the top of `part1/Program.cs`:

```csharp
using GitHub.Copilot;
using HelloCopilotSDK.Helpers;
```

Then replace the prerequisite `TODO` with:

```csharp
// 1. Check prerequisites
Console.WriteLine("🔍 Checking prerequisites...");
var copilotStatus = await CliChecker.CheckCopilotStatusAsync();

if (!CliChecker.IsReady(copilotStatus))
{
    Console.WriteLine("❌ " + (copilotStatus.ErrorMessage ?? "Copilot is not ready."));
    Console.WriteLine("   Install the CLI: https://github.com/cli/cli#installation");
    Console.WriteLine("   Then run: copilot auth login");
    Console.WriteLine("   Or set a GH_TOKEN environment variable with Copilot Requests scope.");
    return;
}

Console.WriteLine("   ✅ Copilot CLI installed");
Console.WriteLine(copilotStatus.IsTokenSet ? "   ✅ GH_TOKEN set" : "   ✅ Authenticated with Copilot CLI");
```

Replace the model-selection `TODO` with:

```csharp
// 2. Select a model
var selectedModel = await ModelSelector.SelectModelAsync();
```

> [!NOTE]
> The `//` comment markers above are plain C# comments, not part of the syntax highlighting. They will appear normally in your editor.

Finally, update the `SessionConfig`:

```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true
});
```

---

## 4. Build and run

```bash
dotnet build part1
dotnet run --project part1
```

You should see the prerequisite check, a model list, and the chat prompt. Typing a message will not stream a response yet — that is the next step.

---

## Checkpoint

- [ ] `part1/Helpers/CliChecker.cs` is created.
- [ ] `part1/Helpers/ModelSelector.cs` is created.
- [ ] `part1/Program.cs` uses both helpers.
- [ ] `dotnet run --project part1` shows the model list and reaches the chat prompt.

Next, add streaming and demo prompts in [Part 1: Helpers (2/2)](04-helpers-2.md).
