# Step 3: Add application-owned knowledge

> **Time:** 15 minutes

## What you'll add

You'll give Copilot a typed local tool that retrieves an exact criterion and remediation from the
application-owned Web Content Accessibility Guidelines (WCAG) catalog.

## Give Copilot a tool your app owns

**Tool calling** lets the model request a capability while it works on an answer. A **local tool**
runs inside your application process. The model decides when to request it, but your code still owns
the data, validation, execution, and result.

In this step, you expose application-owned WCAG guidance as `accessibility_rule_lookup`, register
that tool with the session, and explicitly make it available to the model.

## Bring your own source of truth

The model's general knowledge is not a substitute for data your application owns. This local tool
returns a small, exact result from deterministic code you can test instead of putting the full
catalog in every prompt.

`skip permission` is deliberate here because the tool only reads application-owned data. The
external MCP process in the next step will use a permission boundary instead.

:::language dotnet
## Wire up the C# lookup

### 1. Add the catalog lookup tool

At the top of `workshop-app/Helpers/AccessibilityRuleCatalog.cs`, insert:

```csharp
using System.ComponentModel;
using GitHub.Copilot;
using Microsoft.Extensions.AI;
```

Inside `AccessibilityRuleCatalog`, after the existing `Rules` array, insert:

```csharp
public static AIFunction CreateLookupTool() => CopilotTool.DefineTool(
    ([Description("The accessibility issue or WCAG criterion to look up.")] string query) =>
        Task.FromResult(Lookup(query)),
    toolOptions: new CopilotToolOptions { SkipPermission = true },
    factoryOptions: new AIFunctionFactoryOptions
    {
        Name = "accessibility_rule_lookup",
        Description = "Looks up read-only WCAG guidance maintained by this application."
    });

public static AccessibilityRule Lookup(string query)
{
    var normalizedQuery = query.Trim();
    return Rules.FirstOrDefault(rule =>
               normalizedQuery.Contains(rule.Criterion, StringComparison.OrdinalIgnoreCase) ||
               normalizedQuery.Contains(rule.Title, StringComparison.OrdinalIgnoreCase) ||
               rule.Keywords.Any(keyword =>
                   normalizedQuery.Contains(keyword, StringComparison.OrdinalIgnoreCase)))
           ?? new AccessibilityRule(
               "No exact match",
               "Criterion not found",
               "The issue is not represented in the workshop catalog.",
               "Verify the evidence and consult the complete WCAG reference.",
               []);
}
```

### 2. Show tool activity

In `workshop-app/Helpers/ResponseStreamer.cs`, insert these cases before `SessionIdleEvent`:

```csharp
case ToolExecutionStartEvent tool:
    Console.WriteLine($"\n[tool:start] {tool.Data.ToolName}");
    break;
case ToolExecutionCompleteEvent tool:
    Console.WriteLine($"[tool:done] success={tool.Data.Success}");
    break;
```

### 3. Register and request the tool

Replace the session configuration and send call in `workshop-app/Program.cs`:

```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Streaming = true,
    Tools = [AccessibilityRuleCatalog.CreateLookupTool()],
    AvailableTools = ["accessibility_rule_lookup"]
});

Console.WriteLine("\nCopilot:");
await ResponseStreamer.SendAndPrintAsync(
    session,
    "Use accessibility_rule_lookup to explain how to fix an input with no accessible name.");
```

## Run it

```bash
dotnet run --project workshop-app
```

Look for the tool name and its mapping to 4.1.2:

```text
[tool:start] accessibility_rule_lookup
[tool:done] success=True

WCAG 4.1.2 Name, Role, Value ...
```

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| No tool event appears | Keep the explicit `Use accessibility_rule_lookup` instruction in this learning checkpoint. |
| The compiler cannot find `AIFunction` | Add `using Microsoft.Extensions.AI;` to the catalog file. |
| The result says no exact match | Confirm the prompt contains `accessible name`, a keyword in the starter data. |

</details>

<details>
<summary>Complete Step 3 checkpoint</summary>

Compare your version with
[`checkpoints/dotnet/03-local-tool`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/dotnet/03-local-tool).

</details>
:::

:::language nodejs
## Wire up the TypeScript lookup

### 1. Inspect the prebuilt typed tool

Open `workshop-app/src/workshop.ts`. The starter already imports the catalog and defines this local
tool:

```typescript
export const accessibilityRuleLookup = defineTool("accessibility_rule_lookup", {
  description: "Looks up read-only WCAG guidance maintained by this application.",
  parameters: z.object({
    query: z.string().describe("The accessibility issue or WCAG criterion to look up."),
  }),
  skipPermission: true,
  handler: async ({ query }) => {
    const normalized = query.trim().toLowerCase();
    return accessibilityRules.find((rule) =>
      normalized.includes(rule.criterion.toLowerCase()) ||
      normalized.includes(rule.title.toLowerCase()) ||
      rule.keywords.some((keyword) => normalized.includes(keyword))
    ) ?? noMatch;
  },
});
```

The Zod schema gives the model a typed `query` argument. The handler searches
`accessibilityRules`, which remains application-owned.

### 2. Register and request the tool

In `workshop-app/src/index.ts`, import the tool with the streaming helper:

```typescript
import { accessibilityRuleLookup, streamResponse } from "./workshop.js";
```

Replace the session creation and send call:

```typescript
const session = await client.createSession({
  streaming: true,
  tools: [accessibilityRuleLookup],
  availableTools: ["accessibility_rule_lookup"],
});
try {
  await streamResponse(
    session,
    "Use accessibility_rule_lookup to explain WCAG 4.1.2.",
  );
} finally {
  await session.disconnect();
}
```

`streamResponse` already prints tool start and completion events as well as response text.

## Run it

```bash
npm --prefix workshop-app start
```

Look for `[tool:start] accessibility_rule_lookup` and guidance for WCAG 4.1.2.

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| TypeScript cannot resolve `zod` | Run `npm install` in `workshop-app`. |
| The tool is not called | Keep its name in both `tools` and `availableTools`, and keep the explicit instruction in the prompt. |
| The lookup returns no match | Ask about `4.1.2` or `accessible name`, both represented in the catalog. |

</details>

<details>
<summary>Complete Step 3 checkpoint</summary>

Compare your version with
[`checkpoints/nodejs/03-local-tool`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/nodejs/03-local-tool).

</details>
:::

:::language python
## Wire up the Python lookup

### 1. Inspect the prebuilt typed tool

Open `workshop-app/workshop.py`. The starter already defines the parameter model and local tool:

```python
class LookupParams(BaseModel):
    query: str = Field(
        description="The accessibility issue or WCAG criterion to look up."
    )


@define_tool(
    name="accessibility_rule_lookup",
    description="Looks up read-only WCAG guidance maintained by this application.",
    skip_permission=True,
)
def accessibility_rule_lookup(params: LookupParams) -> dict[str, object]:
    query = params.query.strip().lower()
    rule = next(
        (
            item
            for item in ACCESSIBILITY_RULES
            if item.criterion.lower() in query
            or item.title.lower() in query
            or any(keyword in query for keyword in item.keywords)
        ),
        None,
    )
    return rule.__dict__ if rule else {
        "criterion": "No exact match",
        "recommendation": "Verify the evidence and consult the complete WCAG reference.",
    }
```

Pydantic describes the model-visible argument while the handler searches
`ACCESSIBILITY_RULES`, which remains application-owned.

### 2. Register and request the tool

In `workshop-app/main.py`, import the tool:

```python
from workshop import accessibility_rule_lookup
```

Replace the session creation and send call:

```python
async with await client.create_session(
    streaming=True,
    tools=[accessibility_rule_lookup],
    available_tools=["accessibility_rule_lookup"],
) as session:
    # Keep the Step 2 event handler and completion code here.
    session.on(on_event)
    await session.send(
        "Use accessibility_rule_lookup to explain WCAG 4.1.2."
    )
    await done.wait()
    if error is not None:
        raise error
```

Keep the event handler from Step 2 in the session block; only the session options, import, and
prompt change.

## Run it

```bash
python workshop-app/main.py
```

The response should use the catalog's WCAG 4.1.2 title and recommendation.

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| Python cannot import `pydantic` | Activate the preflight virtual environment and reinstall `requirements.txt`. |
| The tool is not called | Keep it in both `tools` and `available_tools`, and keep the explicit instruction in the prompt. |
| The lookup returns no match | Ask about `4.1.2` or `accessible name`, both represented in the catalog. |

</details>

<details>
<summary>Complete Step 3 checkpoint</summary>

Compare your version with
[`checkpoints/python/03-local-tool`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/python/03-local-tool).

</details>
:::

:::language go
## Wire up the Go lookup

### 1. Add the typed lookup

Add `strings` to the imports in `workshop-app/main.go`, then add these declarations before
`streamResponse`:

```go
type lookupParams struct {
	Query string `json:"query" jsonschema:"The accessibility issue or WCAG criterion to look up."`
}

func accessibilityRuleLookup(params lookupParams, _ copilot.ToolInvocation) (any, error) {
	query := strings.ToLower(params.Query)
	if strings.Contains(query, "4.1.2") || strings.Contains(query, "accessible name") {
		return map[string]string{
			"criterion":      "4.1.2",
			"title":          "Name, Role, Value",
			"recommendation": "Associate each input with a visible label.",
		}, nil
	}
	return map[string]string{
		"criterion":      "No exact match",
		"recommendation": "Verify the evidence and consult the WCAG reference.",
	}, nil
}
```

### 2. Define and register the tool

At the start of `main`, create the tool:

```go
lookup := copilot.DefineTool(
	"accessibility_rule_lookup",
	"Looks up read-only WCAG guidance maintained by this application.",
	accessibilityRuleLookup,
)
lookup.SkipPermission = true
```

Replace the session configuration and final send:

```go
session, err := client.CreateSession(context.Background(), &copilot.SessionConfig{
	Streaming:      copilot.Bool(true),
	Tools:          []copilot.Tool{lookup},
	AvailableTools: []string{"accessibility_rule_lookup"},
})
if err != nil {
	panic(err)
}
defer session.Disconnect()

if err := streamResponse(
	session,
	"Use accessibility_rule_lookup to explain WCAG 4.1.2.",
); err != nil {
	panic(err)
}
```

## Run it

```bash
go -C workshop-app run .
```

The streamed response should use the lookup result for WCAG 4.1.2.

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| `strings` is undefined | Add the standard-library `strings` import. |
| The model cannot see the tool | Keep the tool in `Tools` and its exact name in `AvailableTools`. |
| The lookup returns no match | Ask about `4.1.2` or `accessible name`. |

</details>

<details>
<summary>Complete Step 3 checkpoint</summary>

Compare your version with
[`checkpoints/go/03-local-tool`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/go/03-local-tool).

</details>
:::

:::language rust
## Wire up the Rust lookup

### 1. Add the typed handler

Add these imports near the top of `workshop-app/src/main.rs`:

```rust
use std::sync::Arc;

use async_trait::async_trait;
use github_copilot_sdk::tool::{JsonSchema, ToolHandler, schema_for};
use github_copilot_sdk::types::{SessionConfig, Tool, ToolInvocation};
use github_copilot_sdk::{Client, ClientOptions, Error, ToolResult};
use serde::Deserialize;
```

Replace the narrower Step 2 SDK imports, then add the typed handler before `stream_response`:

```rust
#[derive(Deserialize, JsonSchema)]
struct LookupParams {
    /// The accessibility issue or WCAG criterion to look up.
    query: String,
}

struct AccessibilityRuleLookup;

#[async_trait]
impl ToolHandler for AccessibilityRuleLookup {
    async fn call(&self, invocation: ToolInvocation) -> Result<ToolResult, Error> {
        let params: LookupParams = serde_json::from_value(invocation.arguments)?;
        let result = if params.query.to_lowercase().contains("4.1.2") {
            r#"{"criterion":"4.1.2","title":"Name, Role, Value","recommendation":"Associate each input with a visible label."}"#
        } else {
            r#"{"criterion":"No exact match","recommendation":"Verify the evidence and consult the WCAG reference."}"#
        };
        Ok(ToolResult::Text(result.to_owned()))
    }
}
```

### 2. Define and register the tool

At the start of `main`, create the tool and add it to the session configuration:

```rust
let lookup = Tool::new("accessibility_rule_lookup")
    .with_description("Looks up read-only WCAG guidance maintained by this application.")
    .with_parameters(schema_for::<LookupParams>())
    .with_skip_permission(true)
    .with_handler(Arc::new(AccessibilityRuleLookup));

let client = Client::start(ClientOptions::default()).await?;
let mut config = SessionConfig::default();
config.streaming = Some(true);
config.tools = Some(vec![lookup]);
config.available_tools = Some(vec!["accessibility_rule_lookup".to_owned()]);
let session = client.create_session(config).await?;

stream_response!(
    session,
    "Use accessibility_rule_lookup to explain WCAG 4.1.2.".to_owned()
);
```

Keep the Step 2 disconnect and client shutdown after the macro call.

## Run it

```bash
cargo run --manifest-path workshop-app/Cargo.toml
```

The streamed response should use the lookup result for WCAG 4.1.2.

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| A trait or derive is unresolved | Keep the `async_trait`, `serde`, schema, and tool imports shown above. |
| The model cannot see the tool | Set both `config.tools` and `config.available_tools`. |
| The lookup returns no match | Ask explicitly about `4.1.2`. |

</details>

<details>
<summary>Complete Step 3 checkpoint</summary>

Compare your version with
[`checkpoints/rust/03-local-tool`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/rust/03-local-tool).

</details>
:::

:::language java
## Wire up the Java lookup

### 1. Add the typed lookup

Add these imports to
`workshop-app/src/main/java/workshop/AccessibilityReport.java`:

```java
import com.github.copilot.rpc.ToolDefinition;
import com.github.copilot.tool.Param;

import java.util.List;
```

Add this method before the class's closing brace:

```java
private static String lookupRule(String query) {
    if (query.toLowerCase(java.util.Locale.ROOT).contains("4.1.2")) {
        return """
                {"criterion":"4.1.2","title":"Name, Role, Value","recommendation":"Associate each input with a visible label."}""";
    }
    return """
            {"criterion":"No exact match","recommendation":"Verify the evidence and consult the WCAG reference."}""";
}
```

### 2. Define and register the tool

At the start of `main`, define the tool and session configuration:

```java
var lookup = ToolDefinition.from(
        "accessibility_rule_lookup",
        "Looks up read-only WCAG guidance maintained by this application.",
        Param.of(String.class, "query",
                "The accessibility issue or WCAG criterion to look up."),
        AccessibilityReport::lookupRule).skipPermission(true);
var config = new SessionConfig()
        .setStreaming(true)
        .setTools(List.of(lookup))
        .setAvailableTools(List.of("accessibility_rule_lookup"));
```

Replace session creation and the prompt inside the client block:

```java
var session = client.createSession(config).get();
var response = session.sendAndWait(new MessageOptions()
        .setPrompt("Use accessibility_rule_lookup to explain WCAG 4.1.2."))
        .get();
System.out.println(response);
```

## Run it

```bash
mvn -f workshop-app/pom.xml exec:java
```

The response should use the lookup result for WCAG 4.1.2.

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| `ToolDefinition` or `Param` is unresolved | Add the two Copilot tool imports shown above. |
| The model cannot see the tool | Keep `setTools` and `setAvailableTools` on the same session configuration. |
| The lookup returns no match | Ask explicitly about `4.1.2`. |

</details>

<details>
<summary>Complete Step 3 checkpoint</summary>

Compare your version with
[`checkpoints/java/03-local-tool`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/java/03-local-tool).

</details>
:::

> **You're ready for Playwright when:** the answer uses criterion 4.1.2 from the application catalog.

## Check your understanding

Should calculating an order total from application-owned line items be a local tool or an MCP
server?

<details>
<summary>Check your answer</summary>

Usually a local tool. The application owns the line items and the deterministic calculation, so an
in-process function is easier to test and does not cross a process boundary.

</details>

Continue to [Step 4: Connect an external tool safely](04-mcp-safety.md).
