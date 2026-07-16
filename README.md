# Copilot SDK Workshop

A hands-on workshop for the GitHub Copilot SDK (.NET). Build two real projects:

1. **Hello Copilot SDK** — an interactive console chat client.
2. **Accessibility Report** — a single-file recipe that uses the Copilot SDK + Playwright MCP server to analyze a live webpage.

The workshops are published as a GitHub Pages site. Each workshop has its own landing page and step-by-step walkthroughs.

---

## Live site

After you enable GitHub Pages, the site will be available at:

```text
https://jamesmontemagno.github.io/copilot-sdk-workshop/
```

No step-viewer URL configuration is required before deployment. The Part 1 and Part 2 viewers derive the site root from the current URL, so walkthrough content resolves correctly for both a repository GitHub Pages site and a local preview served from the repository root.

The Blazor target app for Part 2 is deployed automatically at:

```text
https://jamesmontemagno.github.io/copilot-sdk-workshop/target-app/
```

---

## Prerequisites

- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0)
- [Node.js 22+](https://nodejs.org/) (for the Playwright MCP server)
- A supported browser for Part 2: [Microsoft Edge](https://www.microsoft.com/edge/download) (the default) or [Google Chrome](https://www.google.com/chrome/) installed locally
- [Visual Studio Code](https://code.visualstudio.com/)
- [GitHub Copilot](https://github.com/features/copilot) subscription or trial
- [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli) installed; run `copilot login` before using a sample

Install the CLI using your platform's package manager:

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

The SDK can download its bundled runtime during the build. This workshop instead uses the locally installed CLI when available, avoiding that download. Windows installs made with WinGet and Homebrew installs on macOS are detected automatically. On macOS or Linux with a custom CLI location, set the CLI location before restoring, building, or running:

```bash
export COPILOT_CLI_BINARY_PATH="$(command -v copilot)"
```

In PowerShell, use:

```powershell
$env:COPILOT_CLI_BINARY_PATH = (Get-Command copilot).Source
```

---

## Quick start

### Workshop starter

The baseline project is available in [`start/HelloCopilotSDK`](start/HelloCopilotSDK). It contains the project setup and an SDK connectivity check, ready for Part 1.

### Part 1: Hello Copilot SDK

```bash
copilot login
cd samples/hello-copilot-sdk
dotnet run
```

### Part 2: Accessibility Report

1. Open the deployed target app (or run it locally):

   ```bash
   dotnet run --project src/BlazorApp
   ```

2. In another terminal, run the report:

   ```bash
   dotnet run --project samples/accessibility-report
   ```

3. Enter the target app URL when prompted.

---

## Local preview of the workshop site

Because the step viewers fetch markdown from the repository, the easiest way to preview locally is to serve the repository root and open `docs/index.html`:

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .
```

Then open `http://localhost:8000/docs/index.html`.

---

## Repository layout

```
copilot-sdk-workshop/
├── docs/                         # GitHub Pages static site
│   ├── index.html                # Workshop hub
│   ├── part1/                    # Part 1 landing + step viewer
│   ├── part2/                    # Part 2 landing + step viewer
│   └── target-app/               # Deployed Blazor target app
├── workshop/
│   ├── part1/                    # Part 1 walkthroughs
│   └── part2/                    # Part 2 walkthroughs
├── samples/
│   ├── hello-copilot-sdk/        # Part 1 final code
│   └── accessibility-report/     # Part 2 final code
├── src/BlazorApp/                # Source for the target app
├── .github/workflows/deploy.yml  # GitHub Pages deployment
└── README.md
```

---

## Deployment

Push to the `main` branch. The [GitHub Actions workflow](.github/workflows/deploy.yml) will deploy the `docs/` and `workshop/` folders to GitHub Pages.

Make sure GitHub Pages is enabled in the repository settings and set to deploy from GitHub Actions.

---

## Resources

- [GitHub Copilot SDK for .NET](https://github.com/github/copilot-sdk/tree/main/dotnet)
- [Awesome Copilot cookbook](https://github.com/github/awesome-copilot/tree/main/cookbook/copilot-sdk/dotnet)
- [Playwright MCP server](https://www.npmjs.com/package/@playwright/mcp)
- [Site format inspired by Mona Mayhem](https://github.com/copilot-dev-days/mona-mayhem)

---

## License

This workshop is provided as-is for educational purposes.
