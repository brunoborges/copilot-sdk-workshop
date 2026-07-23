# Step 6: Produce a structured report

> **Time:** 10 minutes

## What you'll produce

After this step, the application will produce a concise report that separates page evidence,
criterion mapping, remediation, and the limits of the review.

## Separate evidence from interpretation

An agent response contains both **evidence** and **interpretation**. Evidence is what Playwright
actually observed, such as an input with no accessible name. Interpretation is the criterion
mapping and remediation built from that evidence and the catalog result.

Output constraints tell the agent what to include, what to omit, and how to represent uncertainty.
They improve consistency without turning a prompt into a claim that the review is exhaustive.

## Be useful without overstating the result

Accessibility conformance cannot be established by one automated snapshot. The report should make
useful, high-confidence findings without invented statistics, decorative severity labels, or a
broad claim that the page passes or fails WCAG.

> **Where it fits:** The agent now transforms `browser evidence + catalog result` into a bounded,
> repeatable report.

## Give the report a contract

### 1. Add the report contract

Create `workshop-app/Helpers/Prompts.cs`:

```csharp
namespace HelloCopilotSDK.Helpers;

public static class Prompts
{
    public static string CreateReportPrompt(Uri targetUri) => $"""
        Prepare an evidence-based accessibility review of {targetUri.AbsoluteUri}.

        1. Use browser_navigate to open that exact URL.
        2. Call read_latest_accessibility_snapshot to inspect its accessibility tree.
        3. Identify three to five high-confidence issues supported by the snapshot.
        4. Call accessibility_rule_lookup for each issue before recommending a fix.

        Return only this structure:

        # Accessibility review
        ## Finding 1: <short name>
        - Evidence: <specific element or page structure observed in the browser>
        - WCAG criterion: <criterion and title returned by the catalog>
        - Recommended remediation: <specific implementation change>

        Repeat the finding section as needed.

        ## Review limits
        State that this is a focused review of browser-observable evidence, not a full WCAG conformance audit.

        Do not invent evidence, report unsupported statistics, or claim the page is WCAG compliant.
        """;
}
```

### 2. Use the contract

Replace the final send call in `Program.cs`:

```csharp
Console.WriteLine($"\nAnalyzing: {targetUri.AbsoluteUri}\n");
await ResponseStreamer.SendAndPrintAsync(session, Prompts.CreateReportPrompt(targetUri));
```

## Run it

```bash
dotnet run --project workshop-app
```

Use:

```text
{{TARGET_APP_URL}}
```

The report should follow this shape:

```text
# Accessibility review
## Finding 1: Input has no accessible name
- Evidence: The snapshot contains a textbox with no accessible name.
- WCAG criterion: 4.1.2 Name, Role, Value
- Recommended remediation: Associate a visible label using matching for and id values.

## Review limits
This focused review uses browser-observable evidence and is not a full WCAG conformance audit.
```

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| The output contains unsupported counts | Confirm the prompt says not to report unsupported statistics. |
| A finding has no concrete element or structure | Treat it as ungrounded; keep the evidence requirement in the report contract. |
| The response claims WCAG compliance | Keep the required **Review limits** section and explicit prohibition. |

</details>

> **You are ready to continue when:** each finding contains specific browser evidence, a catalog
> criterion, a remediation, and the report ends with its limits.

## Check your understanding

In the report, which content is direct evidence and which content is model interpretation?

<details>
<summary>Check your answer</summary>

The element or page structure returned by Playwright is evidence. Choosing the relevant criterion
and phrasing a remediation are interpretations grounded by that evidence and the catalog result.

</details>

<details>
<summary>Complete Step 6 checkpoint</summary>

The full, compiling reference is
[`checkpoints/06-structured-report`](https://github.com/codemillmatt/copilot-sdk-workshop/tree/main/checkpoints/06-structured-report).
The completed application is also in
[`samples/accessibility-report`](https://github.com/codemillmatt/copilot-sdk-workshop/tree/main/samples/accessibility-report).

```csharp
using GitHub.Copilot;
using HelloCopilotSDK.Helpers;

Console.WriteLine("=== Accessibility Report Generator ===\n");

Console.Write("Enter URL to analyze: ");
var urlInput = Console.ReadLine()?.Trim();

if (string.IsNullOrWhiteSpace(urlInput))
{
    Console.Error.WriteLine("Enter a URL to analyze.");
    return;
}

if (!urlInput.Contains("://", StringComparison.Ordinal))
{
    urlInput = $"https://{urlInput}";
}

if (!Uri.TryCreate(urlInput, UriKind.Absolute, out var targetUri) ||
    targetUri.Scheme is not ("http" or "https"))
{
    Console.Error.WriteLine("Enter an absolute HTTP or HTTPS URL.");
    return;
}

await using var client = new CopilotClient();
await client.StartAsync();

var ping = await client.PingAsync("workshop");
Console.WriteLine($"\nConnected to the Copilot runtime: {ping.Message}\n");

var workingDirectory = Directory.GetCurrentDirectory();

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Streaming = true,
    OnPermissionRequest = WorkshopPermissionHandler.CreateForTarget(targetUri),
    Tools =
    [
        AccessibilityRuleCatalog.CreateLookupTool(),
        PlaywrightSnapshotReader.CreateTool(workingDirectory)
    ],
    AvailableTools =
    [
        "accessibility_rule_lookup",
        "read_latest_accessibility_snapshot",
        "playwright-browser_navigate"
    ],
    McpServers = new Dictionary<string, McpServerConfig>
    {
        ["playwright"] = new McpStdioServerConfig
        {
            Command = "npx",
            Args = ["-y", "@playwright/mcp@0.0.78", "--browser=msedge"],
            WorkingDirectory = workingDirectory,
            Tools = ["browser_navigate"]
        }
    }
});

Console.WriteLine($"Analyzing: {targetUri.AbsoluteUri}\n");
await ResponseStreamer.SendAndPrintAsync(session, Prompts.CreateReportPrompt(targetUri));
```

</details>

Continue to [Step 7: Run and explain the application](07-run-explain.md).
