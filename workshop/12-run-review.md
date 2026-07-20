# Run and Review

> **Duration:** ~10 minutes

Run the completed application:

```bash
dotnet run --project workshop-app
```

Analyze the deployed target app:

```text
https://jamesmontemagno.github.io/copilot-sdk-workshop/target-app/
```

The target intentionally includes missing image text alternatives, an absent `main` landmark, heading problems, low contrast text, and an unlabeled input. Compare the report with the source in [`src/BlazorApp`](../src/BlazorApp), fix one issue, and run the report again.

## What you built

You used one continuous SDK workflow from start to finish:

1. Start `CopilotClient`.
2. Select a model and create `CopilotSession`.
3. Stream events and wait for completion.
4. Add a local typed C# tool.
5. Add external Playwright MCP tools.
6. Turn real browser findings into a report and tests.

The completed references are [`samples/hello-copilot-sdk`](../samples/hello-copilot-sdk) and [`samples/accessibility-report`](../samples/accessibility-report).

Congratulations! 🎉
