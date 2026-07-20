# Interactive Assistant

> **Duration:** ~10 minutes

Finish the local-tool assistant. This is the foundation you will extend with browser tools.

Use the completed shape from [`samples/hello-copilot-sdk`](../samples/hello-copilot-sdk): keep one `CopilotClient`, create a session through a `CreateSessionAsync` helper, and add a loop that supports `model`, `clear`, `help`, and `exit`.

The session factory should centralize the configuration:

```csharp
static Task<CopilotSession> CreateSessionAsync(CopilotClient client, string? model) =>
    client.CreateSessionAsync(new SessionConfig
    {
        Model = model,
        Streaming = true,
        Tools = [AccessibilityRuleCatalog.CreateLookupTool()]
    });
```

When handling `model`, select a new model, create a replacement session through this helper, then dispose the old session. This preserves the local tool after every model change.

Try:

```text
What should I do about missing alt text?
Why does a page need a main landmark?
How can I make keyboard focus easier to see?
```

## Checkpoint

- [ ] The assistant accepts multiple questions.
- [ ] A model switch recreates the session and retains the local tool.
- [ ] Local tool calls are visible while answers stream.

Next, add browser prerequisites in [Browser Setup](06-browser-setup.md).
