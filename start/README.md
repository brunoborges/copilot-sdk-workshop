# Workshop starter

This folder is the starting point for the workshop. It contains:

- a .NET 10 console project with `GitHub.Copilot.SDK` 1.0.7;
- the application-owned WCAG rule data used in Step 3;
- a prebuilt scoped permission handler and snapshot reader introduced in Step 4.

The starter intentionally does not contain a Copilot client, session, streaming helper, local tool
wrapper, or MCP configuration. Learners add those pieces in small, runnable steps.

Copy this folder to `workshop-app` from the repository root:

```powershell
# Windows
Copy-Item -Recurse start/HelloCopilotSDK workshop-app
```

```bash
# macOS or Linux
cp -R start/HelloCopilotSDK workshop-app
```

Keep `workshop-app` for the full workshop. Return to
[Start the workshop](../README.md#start-the-workshop) to open the interactive lesson viewer.
