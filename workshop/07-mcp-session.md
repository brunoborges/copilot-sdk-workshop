# MCP Session

> **Duration:** ~10 minutes

Keep the earlier session factory and add Playwright MCP beside the local tool:

```csharp
static Task<CopilotSession> CreateSessionAsync(CopilotClient client, string? model) =>
    client.CreateSessionAsync(new SessionConfig
    {
        Model = model,
        Streaming = true,
        OnPermissionRequest = PermissionHandler.ApproveAll,
        Tools = [AccessibilityRuleCatalog.CreateLookupTool()],
        McpServers = new Dictionary<string, McpServerConfig>
        {
            ["playwright"] = new McpStdioServerConfig
            {
                Command = "npx",
                Args = ["@playwright/mcp@0.0.78", "--browser=msedge"],
                Tools = ["*"]
            }
        }
    });
```

`Tools` remains the application-owned C# callback. `McpServers` supplies tools implemented in another process. Both appear in the same session event stream.

> [!IMPORTANT]
> `PermissionHandler.ApproveAll` is convenient for this known workshop setup. Production applications should approve only the necessary operations.

## Checkpoint

- [ ] The local WCAG tool remains registered.
- [ ] Playwright MCP is added through `McpStdioServerConfig`.
- [ ] The browser argument matches your machine.

Next, turn the assistant into a reporter in [URL Input](08-url-input.md).
