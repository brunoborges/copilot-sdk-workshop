# Copilot SDK Workshop

> **Duration:** ~90 minutes  
> **Stack:** .NET 10, C#, GitHub Copilot SDK, Playwright MCP

Build one application from start to finish. You will begin with a console accessibility assistant, teach it to call a safe local C# tool, then extend the **same project** with Playwright MCP to inspect a live webpage and generate accessibility tests.

## What you'll build

1. Start and verify a `CopilotClient`.
2. Let the user select a model.
3. Create a streaming `CopilotSession`.
4. Add a typed local WCAG lookup tool.
5. Add Playwright MCP browser tools to the same session.
6. Generate an accessibility report and optional tests.

The starter is in [`start/HelloCopilotSDK`](../start/HelloCopilotSDK). The completed references are [`samples/hello-copilot-sdk`](../samples/hello-copilot-sdk) and [`samples/accessibility-report`](../samples/accessibility-report).

Continue to [Setup](01-setup.md).
