# Step 5: Combine local and MCP tools

> **Time:** 15 minutes

## What you'll orchestrate

You'll use one URL to drive an agent turn that gathers browser evidence with Playwright and gets
remediation guidance from the local WCAG catalog.

## Let the agent choose the right tool

**Agent orchestration** is the model choosing and sequencing capabilities to complete a goal. Your
session exposes two different tools through one interface:

- Playwright discovers facts about the live page.
- The application-owned catalog explains a matching criterion and remediation.

Both tools report through tool-start and tool-completion events. Your application can observe the
work without knowing how either tool is implemented.

## Keep evidence and guidance in their lanes

Each tool has one job. Playwright supplies browser evidence, while the local catalog supplies
the application's source-of-truth guidance. The answer is grounded in those sources instead of
asking the model to infer both.

The flow is now `URL -> Playwright evidence -> WCAG catalog lookup -> grounded response`.

## Put both tools to work

:::language dotnet
### 1. Read and validate a URL

Remove the command-line argument validation from Step 4. After the banner and before creating the
client, insert:

```csharp
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
```
:::
The Step 4 handler receives this validated `targetUri`, so the URL boundary still applies.

:::language dotnet
### 2. Give the agent a three-tool goal

Replace the final prompt:

```csharp
Console.WriteLine($"\nAnalyzing: {targetUri.AbsoluteUri}\n");
await ResponseStreamer.SendAndPrintAsync(
    session,
    $"""
    Use browser_navigate to open {targetUri.AbsoluteUri}, then call read_latest_accessibility_snapshot.
    Identify two high-confidence accessibility issues supported by the snapshot.
    For each issue, call accessibility_rule_lookup and return:
    - the browser evidence;
    - the matching criterion;
    - the catalog's recommended remediation.
    """);
```
:::
The prompt assigns evidence and guidance to their correct sources. It leaves the order of the
catalog lookups to the agent.

:::language nodejs
In `workshop-app/src/report.ts`, keep the scoped tools from Step 4 and replace the final prompt with
an evidence-backed request that navigates, reads the snapshot, and calls
`accessibility_rule_lookup` for each issue.
:::
:::language python
In `workshop-app/report.py`, keep the scoped tools from Step 4 and replace the final prompt with an
evidence-backed request that navigates, reads the snapshot, and calls
`accessibility_rule_lookup` for each issue.
:::
:::language go
In `workshop-app/main.go`, keep the three `AvailableTools` and replace the prompt with the
evidence-backed two-tool goal from the Step 5 checkpoint.
:::
:::language rust
In `workshop-app/src/main.rs`, keep `config.available_tools` scoped to the same three names and
replace the prompt with the evidence-backed two-tool goal.
:::
:::language java
In `workshop-app/src/main/java/workshop/AccessibilityReport.java`, keep
`setAvailableTools` scoped to the same three names and replace the prompt with the evidence-backed
two-tool goal.
:::

## Run it

:::language dotnet
```bash
dotnet run --project workshop-app
```

Paste this URL when prompted:

```text
{{TARGET_APP_URL}}
```
:::
:::language nodejs
```bash
npm --prefix workshop-app start -- "{{TARGET_APP_URL}}"
```
:::
:::language python
```bash
python workshop-app/main.py "{{TARGET_APP_URL}}"
```
:::
:::language go
```bash
go -C workshop-app run . "{{TARGET_APP_URL}}"
```
:::
:::language rust
```bash
cargo run --manifest-path workshop-app/Cargo.toml -- "{{TARGET_APP_URL}}"
```
:::
:::language java
```bash
mvn -f workshop-app/pom.xml exec:java -Dexec.args="{{TARGET_APP_URL}}"
```
:::

You should see activity from both kinds of tool:

```text
[tool:start] playwright-browser_navigate
[tool:start] read_latest_accessibility_snapshot
[tool:start] accessibility_rule_lookup

- Evidence: The text input has no accessible name ...
- WCAG criterion: 4.1.2 Name, Role, Value
- Recommended remediation: Associate a visible <label> ...
```

The exact order and wording can vary. The evidence must come from Playwright, and the criterion
must match the catalog.

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| Only Playwright tools run | Keep the explicit instruction to call `accessibility_rule_lookup` for each issue. |
| The catalog tool runs before browser inspection | This can be valid planning, but reject any final finding that lacks browser evidence. |
| The URL is rejected | Enter an HTTP or HTTPS URL; a missing scheme is automatically changed to `https://`. |

</details>

> **You're ready to shape the report when:** one run names a Playwright tool and
> `accessibility_rule_lookup`, then connects browser evidence to catalog guidance.

## Check your understanding

Which tool should discover an input without an accessible name, and which tool should explain the
associated WCAG criterion?

<details>
<summary>Check your answer</summary>

Playwright finds the input on the live page. The local catalog returns the application's
source-of-truth criterion and remediation.

</details>

:::language dotnet
<details>
<summary>Complete Step 5 checkpoint</summary>

A complete Step 5 project is available at
[`checkpoints/dotnet/05-combine-tools`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/dotnet/05-combine-tools).

```csharp
using GitHub.Copilot;
using HelloCopilotSDK.Helpers;

Console.WriteLine("=== Browser evidence plus application guidance ===\n");

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
await ResponseStreamer.SendAndPrintAsync(
    session,
    $"""
    Use browser_navigate to open {targetUri.AbsoluteUri}, then call read_latest_accessibility_snapshot.
    Identify two high-confidence accessibility issues supported by the snapshot.
    For each issue, call accessibility_rule_lookup and return:
    - the browser evidence;
    - the matching criterion;
    - the catalog's recommended remediation.
    """);
```
</details>
:::

:::language nodejs
Compare your work with
[`checkpoints/nodejs/05-combine-tools`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/nodejs/05-combine-tools).
:::
:::language python
Compare your work with
[`checkpoints/python/05-combine-tools`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/python/05-combine-tools).
:::
:::language go
Compare your work with [`checkpoints/go/05-combine-tools`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/go/05-combine-tools).
:::
:::language rust
Compare your work with [`checkpoints/rust/05-combine-tools`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/rust/05-combine-tools).
:::
:::language java
Compare your work with [`checkpoints/java/05-combine-tools`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/java/05-combine-tools).
:::

Continue to [Step 6: Produce a structured report](06-structured-report.md).
