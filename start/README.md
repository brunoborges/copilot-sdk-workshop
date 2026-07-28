# Workshop starter

Each language track has its own workshop starting point. Every track contains:

- a .NET 10 console project with `GitHub.Copilot.SDK` 1.0.7;
- the application-owned Web Content Accessibility Guidelines (WCAG) rule data used in Step 3;
- a prebuilt scoped permission handler and snapshot reader introduced in Step 4.

The Copilot client, session, streaming helper, local tool wrapper, and MCP configuration are not
here yet. You'll add them in small steps and run the application after each one.

Copy the track you selected to `workshop-app` from the repository root:

```powershell
# Windows
Copy-Item -Recurse start/dotnet workshop-app
```

```bash
# macOS or Linux
cp -R start/dotnet workshop-app
```

For Node.js/TypeScript use `start/nodejs`, then run `npm install` and `npm run build`.
For Python 3.11+ use `start/python`, create a virtual environment, then run
`python -m pip install -r requirements.txt`.

Keep using `workshop-app` throughout the workshop. Return to
[Start the workshop](../README.md#start-the-workshop) to open the interactive lesson viewer.
