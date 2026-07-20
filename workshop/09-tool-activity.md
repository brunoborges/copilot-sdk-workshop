# Tool Activity

> **Duration:** ~5 minutes

The response helper already receives events for both local and MCP tools. Its generic tool messages should be:

```csharp
case ToolExecutionStartEvent:
    Console.WriteLine("\n🔧 Copilot is using a tool...");
    break;
case ToolExecutionCompleteEvent:
    Console.WriteLine("✅ Tool completed.");
    break;
```

Run the app against the target URL. You should see tool activity while Playwright navigates and inspects the page, followed by the streamed response.

This consistent event model is the key transition: your application observes a C# function and an MCP browser tool in exactly the same way.

Next, create a structured report in [Report Prompt](10-report-prompt.md).
