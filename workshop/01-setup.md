# Setup

> **Duration:** ~10 minutes

Clone the workshop, open it in VS Code, install the prerequisites, and copy the single project you will use for the entire workshop.

## 1. Clone the workshop and open it in VS Code

```bash
git clone https://github.com/jamesmontemagno/copilot-sdk-workshop.git
cd copilot-sdk-workshop
code .
```

If the `code` command is not available, open Visual Studio Code and select **File > Open Folder** to choose the cloned `copilot-sdk-workshop` folder.

## 2. Install and authenticate the Copilot CLI

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

## 3. Copy the starter

From the repository root:

```powershell
Copy-Item -Recurse start/HelloCopilotSDK workshop-app
```

On macOS or Linux:

```bash
cp -R start/HelloCopilotSDK workshop-app
```

Use `workshop-app` for every remaining step. It contains the .NET 10 project, Copilot SDK package, local accessibility-rule data, and example scenarios.

## 4. Build

```bash
dotnet build workshop-app
```

## Checkpoint

- [ ] The `copilot-sdk-workshop` folder is open in Visual Studio Code.
- [ ] `copilot login` completed.
- [ ] `workshop-app/HelloCopilotSDK.csproj` exists.
- [ ] The project builds.

Next, start Copilot in [Client and Model Selection](02-client.md).
