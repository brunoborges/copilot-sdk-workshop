# Step 7: Run and explain the application

> **Time:** 10 minutes

## What you'll be ready to explain

You'll run the complete application and explain its state, tool boundaries, permission boundary,
and report limitations.

## See the whole agent system

:::language dotnet
The finished application is an agent host. Its session coordinates a model, an application-owned
function, and a browser running in another process:

```text
Console application
  |
  +-- CopilotClient -------- runtime connection
       |
       `-- CopilotSession --- one conversation and its context
            |
            +-- accessibility_rule_lookup
            |     same process, application-owned data
            |
            `-- Playwright MCP
                  separate process, scoped permission handler
                       |
                       `-- Browser target
```
:::

:::language nodejs
The completed report is in [`samples/nodejs/accessibility-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/samples/nodejs/accessibility-report).
:::
:::language python
The completed report is in [`samples/python/accessibility-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/samples/python/accessibility-report).
:::

## Take the design beyond this workshop

Understanding these boundaries lets you reuse the design in another application instead of only
reproducing the workshop code. A database lookup, deployment service, or issue tracker may use
different tools, but the same ownership and trust questions apply.

:::language dotnet
The complete flow is
`URL -> Playwright inspection -> C# WCAG lookup -> structured accessibility report`.
:::

## Take a victory lap

There is no code to change. Keep the Step 6 checkpoint in place so this run tests the application
you built.

## Run it

:::language dotnet
```bash
dotnet run --project workshop-app
```
:::
Use the workshop target:

```text
{{TARGET_APP_URL}}
```

Watch for all five stages:

1. The client connects and creates one session.
2. Playwright navigates to the exact target and creates an accessibility snapshot.
3. The narrow local reader returns that current-run snapshot.
4. The local catalog is called for browser-supported findings.
5. The response follows the report contract and states its limits.

The controlled target intentionally includes browser-observable issues: a missing text alternative,
no `main` landmark, an illogical heading sequence, and a textbox without an accessible name.
Compare the report with the
[published target HTML](https://github.com/jamesmontemagno/copilot-sdk-workshop/blob/main/docs/target-app/index.html);
do not accept a finding that is absent from both the snapshot and source.

<details>
<summary>Troubleshooting the complete run</summary>

| Symptom | Fix |
|---|---|
| A known issue is omitted | Agent output can vary. Rerun once, but require evidence rather than forcing a predetermined answer. |
| A reported issue is not in the page | Reject it as ungrounded; the prompt requires specific browser evidence. |
| A tool is denied | Check that `browser_navigate` uses the exact entered target. |
| The reader finds no snapshot | Keep the prompt order: navigate before calling `read_latest_accessibility_snapshot`. |

</details>

> **You have completed the core workshop when:** the report is grounded, the tool names are visible,
> and you can answer the architecture questions below without reading the code.

## Check your understanding

1. What state belongs to the session?
2. Why is the WCAG catalog local?
3. Why is Playwright external?
4. Where are permissions enforced?
5. What changes when another MCP server is added?

<details>
<summary>Compare your explanation</summary>

1. The session owns one conversation's messages, model response, and tool results.
2. The application owns the catalog data and deterministic lookup, so the function stays local.
3. Playwright is a reusable browser capability with its own Node.js process and dependencies.
4. The MCP tool allowlist exposes only navigation, and `WorkshopPermissionHandler` approves only
   the exact target. The trusted local reader accepts no path and reads only a new generated
   snapshot; the catalog is also read-only. Those application-owned tools skip permission.
5. Add the server configuration, expose only needed tools, define its trust policy, and keep
   observing its calls through the same session event stream.

</details>

## Keep exploring

Try [Optional: Select a model](08-model-selection.md) if your application needs explicit control
over model choice. Otherwise, the core workshop is complete.

:::language dotnet
Complete references:

- [Step 6 checkpoint](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/dotnet/06-structured-report)
- [Finished accessibility reporter](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/samples/dotnet/accessibility-report)
- [GitHub Copilot SDK for .NET](https://github.com/github/copilot-sdk/tree/main/dotnet)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
:::
:::language go
Run the completed reporter with `go -C samples/go/accessibility-report run . "{{TARGET_APP_URL}}"`. Explain that `Client` owns the Copilot CLI lifecycle, the `Session` owns one conversation, and the permission handler gates external navigation. The expected report is evidence-bound; if the CLI is missing, install it rather than granting broader permissions. Review [`samples/go/accessibility-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/samples/go/accessibility-report) and [`checkpoints/go/06-structured-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/go/06-structured-report).
:::
:::language rust
Run `cargo run --manifest-path samples/rust/accessibility-report/Cargo.toml -- "{{TARGET_APP_URL}}"`. Explain that `Client` manages the runtime, `Session` dispatches events, typed tools are app-owned, and the permission handler trusts only exact navigation. If it cannot start, install and authenticate the Copilot CLI. Review [`samples/rust/accessibility-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/samples/rust/accessibility-report) and [`checkpoints/rust/06-structured-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/rust/06-structured-report).
:::
:::language java
Run `mvn -f samples/java/accessibility-report/pom.xml exec:java -Dexec.args="{{TARGET_APP_URL}}"`. Explain that Maven compiles the Java 17 application, `CopilotClient` manages the runtime, tools remain scoped, and the permission callback accepts only the canonical URL. If the runtime is unavailable, install the Copilot CLI; do not replace Maven with JBang or Gradle. Review [`samples/java/accessibility-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/samples/java/accessibility-report) and [`checkpoints/java/06-structured-report`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/java/06-structured-report).
:::
