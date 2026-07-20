# URL Input

> **Duration:** ~5 minutes

Replace the general question loop with one URL-driven report run:

```csharp
Console.Write("Enter URL to analyze: ");
var url = Console.ReadLine()?.Trim();

if (string.IsNullOrWhiteSpace(url))
{
    Console.WriteLine("No URL provided. Exiting.");
    return;
}

if (!url.StartsWith("http://") && !url.StartsWith("https://"))
{
    url = "https://" + url;
}

Console.WriteLine($"\nAnalyzing: {url}\n");
```

Then create a basic browser prompt:

```csharp
var prompt = $"""
    Use the Playwright MCP server to analyze the accessibility of {url}.
    Navigate to the page, take an accessibility snapshot, and report the issues you find.
    Use accessibility_rule_lookup when project-specific WCAG guidance is useful.
    """;

await ResponseStreamer.SendAndPrintAsync(session, prompt);
```

## Checkpoint

- [ ] Empty URLs exit safely.
- [ ] Missing URL schemes are added.
- [ ] The same response helper streams the browser report.

Next, improve tool visibility in [Tool Activity](09-tool-activity.md).
