# Browser Setup

> **Duration:** ~10 minutes

The same application will now call Playwright MCP to inspect a live webpage.

## 1. Verify Node.js and npx

```bash
node --version
npx --version
```

Node.js 22 or later is recommended.

## 2. Choose a browser

| Browser | MCP argument |
|---------|--------------|
| Microsoft Edge | `--browser=msedge` |
| Google Chrome | `--browser=chrome` |
| Firefox | `--browser=firefox` |
| WebKit (macOS/Linux) | `--browser=webkit` |

## 3. Start the target app

Use the deployed app:

```text
https://jamesmontemagno.github.io/copilot-sdk-workshop/target-app/
```

Or start it locally in another terminal:

```bash
dotnet run --project src/BlazorApp --urls http://localhost:5000
```

## Checkpoint

- [ ] `node` and `npx` are available.
- [ ] You chose a supported browser.
- [ ] You have a target app URL.

Next, attach Playwright MCP in [MCP Session](07-mcp-session.md).
