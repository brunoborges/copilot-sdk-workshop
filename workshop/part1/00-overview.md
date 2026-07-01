# Hello GitHub Copilot SDK (.NET)

> **Duration:** ~45 minutes  
> **Level:** Intermediate  
> **Stack:** .NET 10, C#, GitHub Copilot SDK

Welcome! In this workshop you will build an interactive console chat client using the GitHub Copilot SDK for .NET.

---

## What you'll build

A console app that:

1. Checks that the GitHub Copilot CLI is installed and authenticated.
2. Lists available Copilot models and lets you pick one.
3. Starts a `CopilotClient` and creates a streaming `CopilotSession`.
4. Provides an interactive chat loop with demo prompts.

---

## What you'll learn

- How to start a `CopilotClient` and create a streaming `CopilotSession`.
- How to handle SDK events such as `AssistantMessageDeltaEvent`, `SessionIdleEvent`, and `SessionErrorEvent`.
- How to list and select models.
- How to structure a small but complete Copilot SDK application.

---

## Prerequisites

Before you start, make sure you have:

- [ ] [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) installed.
- [ ] [Visual Studio Code](https://code.visualstudio.com/) installed.
- [ ] A [GitHub Copilot](https://github.com/features/copilot) subscription or trial.
- [ ] The [GitHub Copilot CLI](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line) installed and authenticated.

> [!TIP]
> You can authenticate the Copilot CLI interactively with `copilot auth login`, or set a `GH_TOKEN` environment variable with the **Copilot Requests** scope.

---

## Repository layout

```
copilot-sdk-workshop/
├── docs/                         # GitHub Pages site
├── workshop/
│   ├── part1/                    # This workshop
│   └── part2/                    # Accessibility Report workshop
├── part1/                        # Your Part 1 project
├── part2/                        # Your Part 2 project
└── src/BlazorApp/                # Target app for Part 2
```

You will create the `part1/` project folder as you work through the steps. The `samples/hello-copilot-sdk/` folder contains the finished code if you need a reference.

---

## How to use this workshop

Each step has:

- A short explanation of the concept.
- A code block you can copy and paste.
- A command to run.
- Checkboxes you can tick off as you go.

Use the **Prev** / **Next** buttons or the sidebar to move between steps. Code blocks have a **Copy** button in the top-right corner.

Ready? Start with [Setup](01-setup.md).
