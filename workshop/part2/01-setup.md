# Part 2: Setup

> **Duration:** ~10 minutes

In this step you will set up the second project: a .NET 10 console app that uses the GitHub Copilot SDK plus the Playwright MCP server to generate an accessibility report for a live webpage.

You will also start a small Blazor target app that contains intentional accessibility issues for the report to find.

---

## 1. Verify Node.js and npx

The Playwright MCP server is launched through `npx`. Verify both are available:

```bash
node --version
npx --version
```

Node.js 22 or later is recommended.

---

## 2. Choose a browser

This workshop uses `@playwright/mcp@0.0.77`. By default, its code uses `--browser=msedge` to launch the locally installed [Microsoft Edge](https://www.microsoft.com/edge/download) browser. Edge is included with current Windows installations.

Choose the option that matches the browser runtime available on your machine:

| Browser | Argument | Requirement |
|---------|----------|-------------|
| Microsoft Edge (default) | `--browser=msedge` | Install Microsoft Edge. |
| Google Chrome | `--browser=chrome` | Install Google Chrome. |
| Firefox | `--browser=firefox` | Playwright downloads its managed Firefox runtime automatically on first use. |
| WebKit | `--browser=webkit` | Playwright downloads its managed WebKit runtime automatically on first use. WebKit is supported on macOS and Linux, not Windows. |

To use a different option, replace `--browser=msedge` with the matching argument wherever it appears in the Part 2 code snippets or the completed sample.

> [!IMPORTANT]
> Edge and Chrome use locally installed browser channels. Running `npx playwright install` downloads Playwright runtimes, but does not install Edge or Chrome.

---

## 3. Create the console project

From the repository root, run:

```bash
dotnet new console -n AccessibilityReport -o part2
cd part2
```

This creates a standard .NET 10 console project with `AccessibilityReport.csproj` and `Program.cs` inside the `part2/` folder.

---

## 4. Add the GitHub Copilot SDK package

```bash
dotnet add package GitHub.Copilot.SDK --version 1.0.5
```

> [!NOTE]
> The SDK is evolving quickly. If you want the latest version, omit `--version 1.0.5`. The samples in this repo pin the version for reproducibility.

---

## 5. Update the project file

Open `part2/AccessibilityReport.csproj` and make sure it looks like this:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RootNamespace>AccessibilityReport</RootNamespace>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="GitHub.Copilot.SDK" Version="1.0.5" />
  </ItemGroup>

</Project>
```

---

## 6. Choose a target webpage

The accessibility report needs a webpage to analyze. We have included a small Blazor app with intentional accessibility issues.

### Use the deployed target app (recommended)

The target app is already deployed to GitHub Pages:

```text
https://jamesmontemagno.github.io/copilot-sdk-workshop/target-app/
```

Use this URL in the steps that follow.

### Run the Blazor app locally (optional)

If you prefer to run the target app yourself, open a **new terminal** and run:

```bash
dotnet run --project src/BlazorApp
```

After a few seconds you will see a URL such as `http://localhost:5000` or `https://localhost:5001`. Open it in a browser to confirm the app loads, then keep the terminal open.

> [!NOTE]
> If port 5000 is in use, the app will pick another port. Note the exact URL shown in the terminal.

---

## Checkpoint

- [ ] `node --version` and `npx --version` work.
- [ ] A browser option from the table is available.
- [ ] `part2/AccessibilityReport.csproj` exists and targets `net10.0`.
- [ ] `GitHub.Copilot.SDK` package is added.
- [ ] You have a target app URL (deployed or localhost).

Next, create the Copilot client and attach the Playwright MCP server in [Part 2: Client & MCP](02-client.md).
