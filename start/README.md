# Workshop starter

This is the starting point for Part 1. It includes the .NET 10 console project and the GitHub Copilot SDK package, but no workshop implementation.

Before running it, install and authenticate the GitHub Copilot CLI. The repository automatically uses the WinGet CLI location on Windows and the standard Homebrew locations on macOS. On macOS or Linux with a custom CLI location, point the SDK at the installed CLI for the current shell:

```bash
export COPILOT_CLI_BINARY_PATH="$(command -v copilot)"
```

Then run:

```bash
cd start/HelloCopilotSDK
dotnet run
```

Continue with [Part 1 setup](../workshop/part1/01-setup.md) to build the chat client.