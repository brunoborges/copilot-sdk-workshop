# Accessibility Report with Copilot SDK

> **Duration:** ~45 minutes  
> **Level:** Intermediate  
> **Stack:** .NET 10, C#, GitHub Copilot SDK, Playwright MCP

Welcome! In this workshop you will build a single-file .NET recipe that uses the GitHub Copilot SDK and the Playwright MCP server to analyze a live webpage and generate a WCAG-aligned accessibility report.

You will also learn how to prompt the model to generate Playwright accessibility tests based on the findings.

---

## What you'll build

An interactive console tool that:

1. Asks for a URL.
2. Starts a `CopilotClient` and creates a streaming `CopilotSession`.
3. Attaches the Playwright MCP server so Copilot can drive a real browser.
4. Navigates to the page, captures an accessibility snapshot, and produces a structured report.
5. Optionally generates Playwright accessibility tests in the language of your choice.

---

## What you'll learn

- How to attach an MCP server (Playwright) to a `CopilotSession`.
- How to handle SDK events such as `AssistantMessageDeltaEvent`, `SessionIdleEvent`, and `SessionErrorEvent`.
- How to prompt Copilot to drive a browser and return structured output.
- How to engineer prompts that produce consistent, WCAG-aligned reports.

---

## Prerequisites

Before you start, make sure you have:

- [ ] [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) installed.
- [ ] [Node.js 22+](https://nodejs.org/) installed (needed for the Playwright MCP server).
- [ ] [Google Chrome](https://www.google.com/chrome/) installed (the Playwright MCP configuration launches the locally installed Chrome browser).
- [ ] [Visual Studio Code](https://code.visualstudio.com/) installed.
- [ ] A [GitHub Copilot](https://github.com/features/copilot) subscription or trial.
- [ ] The [GitHub Copilot CLI](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line) installed and authenticated.

> [!TIP]
> You can authenticate the Copilot CLI interactively with `copilot auth login`, or set a `GH_TOKEN` environment variable with the **Copilot Requests** scope.

---

## Target app

This workshop analyzes a live Blazor target app. The easiest option is to use the already-deployed app:

**Deployed target app**:  
`https://jamesmontemagno.github.io/copilot-sdk-workshop/target-app/`

If you prefer, you can also run the target app locally:

```bash
dotnet run --project src/BlazorApp --urls http://localhost:5000
```

---

## Repository layout

```
copilot-sdk-workshop/
├── docs/                         # GitHub Pages site
│   └── target-app/               # Deployed Blazor target app
├── workshop/
│   ├── part1/                    # Hello Copilot SDK workshop
│   └── part2/                    # This workshop
├── part1/                        # Your Part 1 project
└── part2/                        # Your Part 2 project
```

You will create the `part2/` project folder as you work through the steps. The `samples/accessibility-report/` folder contains the finished code if you need a reference.

---

## How to use this workshop

Each step has:

- A short explanation of the concept.
- A code block you can copy and paste.
- A command to run.
- Checkboxes you can tick off as you go.

Use the **Prev** / **Next** buttons or the sidebar to move between steps. Code blocks have a **Copy** button in the top-right corner.

Ready? Start with [Setup](01-setup.md).
