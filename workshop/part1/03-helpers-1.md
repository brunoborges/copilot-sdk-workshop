# Part 1: Helpers (1/2)

> **Duration:** ~10 minutes

In this step you will add two helpers:

1. `CliChecker.cs` — verifies that the Copilot CLI is installed.
2. `ModelSelector.cs` — lists available models and lets you pick one.

---

## 1. Create the status record

Create `part1/Helpers/CliChecker.cs` and start with the data record:

```csharp
using System.Diagnostics;

namespace HelloCopilotSDK.Helpers;

public record CopilotCliStatus(
    bool IsInstalled,
    string? ErrorMessage);
```

A `record` is a concise way to hold immutable status data.

---

## 2. Check the Copilot CLI installation

Still in `part1/Helpers/CliChecker.cs`, add the `CliChecker` class and check the version:

```csharp
public static class CliChecker
{
    public static async Task<CopilotCliStatus> CheckCopilotCliAsync()
    {
        try
        {
            var version = await RunCommandAsync("copilot", "--version");
            if (string.IsNullOrWhiteSpace(version))
            {
                return new CopilotCliStatus(false, "Copilot CLI is installed but returned no version.");
            }

            return new CopilotCliStatus(true, null);
        }
        catch (System.ComponentModel.Win32Exception ex)
        {
            return new CopilotCliStatus(false, $"Copilot CLI not found: {ex.Message}");
        }
        catch (InvalidOperationException ex)
        {
            return new CopilotCliStatus(false, $"Copilot CLI could not run: {ex.Message}");
        }
    }
```

This confirms only that the CLI can run. The SDK verifies the current credentials when it starts the client and lists models.

---

## 3. Add the command runner

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

        if (process.ExitCode != 0)
        {
            throw new InvalidOperationException(
                string.IsNullOrWhiteSpace(error) ? output : error);
        }

        return output;
    }
```

---

## 4. Create ModelSelector.cs

Create `part1/Helpers/ModelSelector.cs` with the model-listing logic:

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

}
```

`ModelInfo` is provided by the SDK and contains `Id`, `Name`, and billing metadata. Calling `ListModelsAsync` on the started client confirms the configured credentials are usable.

---

## 5. Wire the helpers into Program.cs

Update the top of `part1/Program.cs`:

```csharp
using GitHub.Copilot;
using HelloCopilotSDK.Helpers;
```

Then replace the prerequisite and model-selection `TODO` comments, plus the client initialization, with:

```csharp
// 1. Check prerequisites
Console.WriteLine("🔍 Checking prerequisites...");
var cliStatus = await CliChecker.CheckCopilotCliAsync();

if (!cliStatus.IsInstalled)
{
    Console.WriteLine("❌ " + (cliStatus.ErrorMessage ?? "Copilot CLI is not ready."));
    Console.WriteLine("   Install the CLI: https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli");
    return;
}

Console.WriteLine("   ✅ Copilot CLI installed");

// 2. Start the Copilot client and verify the current credentials through the SDK.
Console.WriteLine("🚀 Starting Copilot client...");
await using var client = new CopilotClient();
string? selectedModel;

try
{
    await client.StartAsync();
    selectedModel = await ModelSelector.SelectModelAsync(client);
}
catch (InvalidOperationException ex)
{
    Console.WriteLine("❌ Copilot authentication could not be verified.");
    Console.WriteLine("   Run: copilot login");
    Console.WriteLine("   Or set a GH_TOKEN environment variable with Copilot Requests scope.");
    Console.WriteLine($"   Details: {ex.Message}");
    return;
}
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

## 6. Build and run

```bash
dotnet build part1
dotnet run --project part1
```

You should see the CLI installation check, a model list, and the chat prompt. If the SDK cannot use your credentials, run `copilot login` and try again. Typing a message will not stream a response yet — that is the next step.

---

## Checkpoint

- [ ] `part1/Helpers/CliChecker.cs` is created.
- [ ] `part1/Helpers/ModelSelector.cs` is created.
- [ ] `part1/Program.cs` uses both helpers.
- [ ] `dotnet run --project part1` shows the model list and reaches the chat prompt.

Next, add streaming and demo prompts in [Part 1: Helpers (2/2)](04-helpers-2.md).
