# Workshop starter

This is the starting point for the workshop. It includes the .NET 10 console project, the GitHub Copilot SDK package, and small accessibility-rule and prompt scaffolding. You will write the SDK initialization, model picker, streaming handler, local tool registration, and Playwright MCP integration during the workshop.

Before running it, install and authenticate the GitHub Copilot CLI. The repository automatically uses the WinGet CLI location on Windows and the standard Homebrew locations on macOS. On macOS or Linux with a custom CLI location, point the SDK at the installed CLI for the current shell:

```bash
export COPILOT_CLI_BINARY_PATH="$(command -v copilot)"
```

Copy this folder to `workshop-app` at the repository root. In PowerShell:

```powershell
Copy-Item -Recurse start/HelloCopilotSDK workshop-app
```

On macOS or Linux:

```bash
cp -R start/HelloCopilotSDK workshop-app
```

Keep `workshop-app` for the entire flow. Later steps add the Playwright MCP server and evolve it into a browser-backed accessibility reporter.

Continue with [Setup](../workshop/01-setup.md).