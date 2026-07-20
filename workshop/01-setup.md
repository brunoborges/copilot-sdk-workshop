# Setup

> **Duration:** ~10 minutes

Install the prerequisites and copy the single project you will use for the entire workshop.

## 1. Install and authenticate the Copilot CLI

```powershell
# Windows
winget install GitHub.Copilot
```

```bash
# macOS and Linux with Homebrew
brew install copilot-cli

# Any platform with Node.js 22+
npm install -g @github/copilot
```

Then authenticate:

```bash
copilot login
```

The repository detects the WinGet location on Windows and standard Homebrew locations on macOS. For a custom macOS or Linux install:

```bash
export COPILOT_CLI_BINARY_PATH="$(command -v copilot)"
```

In PowerShell:

```powershell
$env:COPILOT_CLI_BINARY_PATH = (Get-Command copilot).Source
```

## 2. Copy the starter

From the repository root:

```powershell
Copy-Item -Recurse start/HelloCopilotSDK workshop-app
```

On macOS or Linux:

```bash
cp -R start/HelloCopilotSDK workshop-app
```

Use `workshop-app` for every remaining step. It contains the .NET 10 project, Copilot SDK package, local accessibility-rule data, and example scenarios.

## 3. Build

```bash
dotnet build workshop-app
```

## Checkpoint

- [ ] `copilot login` completed.
- [ ] `workshop-app/HelloCopilotSDK.csproj` exists.
- [ ] The project builds.

Next, start Copilot in [Client and Model Selection](02-client.md).
