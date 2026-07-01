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

## 2. Create the console project

From the repository root, run:

```bash
dotnet new console -n accessibility-report -o part2
cd part2
```

This creates a standard .NET 10 console project with `accessibility-report.csproj` and `Program.cs` inside the `part2/` folder.

---

## 3. Add the GitHub Copilot SDK package

```bash
dotnet add package GitHub.Copilot.SDK --version 1.0.5
```

> [!NOTE]
> The SDK is evolving quickly. If you want the latest version, omit `--version 1.0.5`. The samples in this repo pin the version for reproducibility.

---

## 4. Update the project file

Open `part2/accessibility-report.csproj` and make sure it looks like this:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RootNamespace>accessibility_report</RootNamespace>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="GitHub.Copilot.SDK" Version="1.0.5" />
  </ItemGroup>

</Project>
```

---

## 5. Choose a target webpage

The accessibility report needs a webpage to analyze. We have included a small Blazor app with intentional accessibility issues.

### Option A: Use the deployed target app (recommended)

If this repository is deployed to GitHub Pages, the target app is available at:

```text
https://YOUR_ORG.github.io/copilot-sdk-workshop/target-app/
```

> [!NOTE]
> Replace `YOUR_ORG` with the actual GitHub organization or username.

### Option B: Run the Blazor app locally

In a **new terminal**, run:

```bash
dotnet run --project src/BlazorApp
```

After a few seconds you will see a URL such as `http://localhost:5000` or `https://localhost:5001`. Open it in a browser to confirm the app loads, then keep the terminal open.

> [!NOTE]
> If port 5000 is in use, the app will pick another port. Note the exact URL shown in the terminal.

---

## Checkpoint

- [ ] `node --version` and `npx --version` work.
- [ ] `part2/accessibility-report.csproj` exists and targets `net10.0`.
- [ ] `GitHub.Copilot.SDK` package is added.
- [ ] You have a target app URL (deployed or localhost).

Next, create the Copilot client and attach the Playwright MCP server in [Part 2: Client & MCP](02-client.md).
