# Part 1: Run

> **Duration:** ~10 minutes

Your Hello Copilot SDK app is complete. In this step you will run it, try the demo prompts, and experiment with the commands.

---

## 1. Run the app

```bash
dotnet run --project part1
```

You should see output similar to:

```text
=====================================
   🤖 Hello GitHub Copilot SDK (.NET)
=====================================

🔍 Checking prerequisites...
   ✅ Copilot CLI installed
   ✅ Authenticated with Copilot CLI

🤖 Select a model:
   1. Claude 3.5 Sonnet (multiplier: 1x)
   2. GPT-4o (multiplier: 1x)
   ...

Enter choice (1-N) [default: 1]: 1
✅ Selected: Claude 3.5 Sonnet

🚀 Starting Copilot client...
   ✅ Copilot client responded: pong: hello

📚 Demo Prompts
   demo 1: Code Review
   demo 2: Algorithm Help
   ...

💬 Interactive Chat Mode
   Type a message and press Enter.
   Commands: model | clear | demo <1-6> | exit

You:
```

---

## 2. Try a demo prompt

Type:

```text
demo 1
```

Copilot should stream a code review of the vulnerable SQL method.

---

## 3. Ask your own question

Type any question, for example:

```text
Explain async/await in C# like I'm new to the language.
```

---

## 4. Try the commands

| Command | What it does |
|---------|--------------|
| `model` | Re-run model selection and create a new session. |
| `clear` | Clear the console and reprint the header. |
| `demo 1` ... `demo 6` | Run a built-in demo prompt. |
| `exit` or `quit` | Close the app. |

---

## 5. Experiment

Try these ideas:

- Switch models mid-conversation with `model`.
- Ask Copilot to refactor one of the demo prompts.
- Add a new demo prompt to `DemoPrompts.cs` and rebuild.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Copilot CLI not found" | Install the CLI with `winget install GitHub.Copilot`, `brew install copilot-cli`, or `npm install -g @github/copilot`. |
| "Not authenticated" | Run `copilot auth login` or set `GH_TOKEN`. |
| Empty model list | Check your network and Copilot subscription; the SDK needs to reach GitHub's model endpoint. |
| Responses are slow | Streaming makes latency feel lower, but large prompts still take time. |

---

## Checkpoint

- [ ] `dotnet run --project part1` starts the app.
- [ ] A demo prompt produces a streamed response.
- [ ] You can switch models and exit cleanly.

Part 1 is complete! 🎉

When you are ready, try the second workshop: [Accessibility Report with Copilot SDK](../part2/00-overview.md).
