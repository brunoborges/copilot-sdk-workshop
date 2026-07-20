# Local Tool Calling

> **Duration:** ~15 minutes

Expose the starter's in-memory WCAG catalog as a safe, typed tool Copilot can invoke.

Replace `workshop-app/Helpers/AccessibilityRuleCatalog.cs` with:

```csharp
using System.ComponentModel;
using GitHub.Copilot;
using Microsoft.Extensions.AI;

namespace HelloCopilotSDK.Helpers;

public static class AccessibilityRuleCatalog
{
    public static AIFunction CreateLookupTool() => CopilotTool.DefineTool(
        ([Description("The accessibility issue or WCAG criterion to look up.")] string query) => Task.FromResult(new
        {
            Query = query,
            Guidance = "Use semantic HTML, meaningful text alternatives, visible keyboard focus, sufficient contrast, and programmatic labels."
        }),
        toolOptions: new CopilotToolOptions { SkipPermission = true },
        factoryOptions: new AIFunctionFactoryOptions
        {
            Name = "accessibility_rule_lookup",
            Description = "Looks up read-only WCAG accessibility guidance from this application's rule catalog."
        });
}
```

Update the session configuration:

```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true,
    Tools = [AccessibilityRuleCatalog.CreateLookupTool()]
});
```

Add these cases to `ResponseStreamer` before `SessionIdleEvent`:

```csharp
case ToolExecutionStartEvent:
    Console.WriteLine("\n🔧 Copilot is using a tool...");
    break;
case ToolExecutionCompleteEvent:
    Console.WriteLine("✅ Tool completed.");
    break;
```

Run the app and ask: `Use accessibility_rule_lookup to explain how to fix an input without a label.`

## Checkpoint

- [ ] `CopilotTool.DefineTool` registers a typed C# callback.
- [ ] The tool is in `SessionConfig.Tools`.
- [ ] Tool start and completion appear in the terminal.

Next, make the assistant interactive in [Interactive Assistant](05-interactive.md).
