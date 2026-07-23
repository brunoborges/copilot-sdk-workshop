# Preflight: prepare your machine

> **Untimed preparation**  
> Complete this page before starting the 90-minute workshop.

## What you'll have ready

You will have the repository, authenticated Copilot CLI, .NET project, Node.js runtime, and
Playwright MCP package ready before the first lesson.

## What you need

| Requirement | Why the workshop needs it | Verify |
|---|---|---|
| [.NET 10 SDK](https://learn.microsoft.com/dotnet/core/install/) | Builds and runs the C# console application | `dotnet --version` |
| [Node.js 22 or newer](https://nodejs.org/) | Runs the Playwright MCP server | `node --version` |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli) | Provides the Copilot runtime used by the SDK | `copilot --version` |
| [GitHub Copilot access](https://github.com/features/copilot) | Authorizes Copilot requests | `copilot login` |
| Microsoft Edge (default) or Google Chrome | Lets Playwright inspect the target page | Open the browser once before the workshop |

Expected version output looks like this:

```text
$ dotnet --version
10.0.x
$ node --version
v22.x.x
$ copilot --version
GitHub Copilot CLI ...
```

## 1. Clone the repository

```bash
git clone https://github.com/codemillmatt/copilot-sdk-workshop.git
cd copilot-sdk-workshop
code .
```

If `code` is unavailable, open the cloned `copilot-sdk-workshop` folder from your editor's
**Open Folder** command.

## 2. Authenticate Copilot

Install the CLI with the method from the
[official setup guide](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli), then run:

```bash
copilot login
```

The repository detects common WinGet and Homebrew locations. If `dotnet build` later says it
cannot find the Copilot CLI, set its path for the current terminal:

<div class="workshop-tabs" data-tabs>
  <div role="tablist" aria-label="Set the Copilot CLI path">
    <button type="button" role="tab" aria-selected="true" data-tab="cli-windows">Windows</button>
    <button type="button" role="tab" aria-selected="false" data-tab="cli-unix">macOS or Linux</button>
  </div>
  <div role="tabpanel" data-panel="cli-windows">
    <pre><code class="language-powershell">$env:COPILOT_CLI_BINARY_PATH = (Get-Command copilot).Source</code></pre>
  </div>
  <div role="tabpanel" data-panel="cli-unix" hidden>
    <pre><code class="language-bash">export COPILOT_CLI_BINARY_PATH="$(command -v copilot)"</code></pre>
  </div>
</div>

## 3. Warm up Playwright MCP

This command downloads the pinned package once and prints its options without starting a server:

```bash
npx -y @playwright/mcp@0.0.78 --help
```

The workshop uses a pinned version so every learner receives the same tool names and behavior.
The code uses Microsoft Edge with `--browser=msedge`. If you prepared Google Chrome instead, use
`--browser=chrome` when that argument appears in Step 4.

## 4. Copy and build the starter

<div class="workshop-tabs" data-tabs>
  <div role="tablist" aria-label="Copy the workshop starter">
    <button type="button" role="tab" aria-selected="true" data-tab="copy-windows">Windows</button>
    <button type="button" role="tab" aria-selected="false" data-tab="copy-unix">macOS or Linux</button>
  </div>
  <div role="tabpanel" data-panel="copy-windows">
    <pre><code class="language-powershell">Copy-Item -Recurse start/HelloCopilotSDK workshop-app
dotnet build workshop-app</code></pre>
  </div>
  <div role="tabpanel" data-panel="copy-unix" hidden>
    <pre><code class="language-bash">cp -R start/HelloCopilotSDK workshop-app
dotnet build workshop-app</code></pre>
  </div>
</div>

The final lines should be:

```text
Build succeeded.
    0 Warning(s)
    0 Error(s)
```

Open the controlled target page once so you know it is reachable:

```text
{{TARGET_APP_URL}}
```

<details>
<summary>Troubleshooting preflight</summary>

| Symptom | Fix |
|---|---|
| `copilot` is not recognized | Restart the terminal after installation, or set `COPILOT_CLI_BINARY_PATH` with the command above. |
| Copilot asks you to authenticate | Run `copilot login`, finish the browser flow, then retry. |
| NuGet restore cannot reach the package source | Check proxy or package-source settings, then run `dotnet restore workshop-app`. |
| `npx` is not recognized | Install Node.js 22 or newer and restart the terminal. |
| The browser cannot start later | Install Edge or Chrome, or follow the [Playwright MCP browser configuration](https://github.com/microsoft/playwright-mcp#configuration). |

</details>

> **You are ready to continue when:** `dotnet build workshop-app` succeeds, `copilot login`
> is complete, and the target page opens.

Continue to [Step 1: Create your first Copilot session](01-first-session.md).
