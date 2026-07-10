# Part 1: Setup

> **Duration:** ~10 minutes

In this step you will create a new .NET 10 console project, add the GitHub Copilot SDK package, and verify that your environment is ready.

---

## 1. Create the project

Open VS Code and a terminal (`Ctrl + `` `), then run:

```bash
dotnet new console -n HelloCopilotSDK -o part1
cd part1
```

This creates a minimal console app with `Program.cs` and `HelloCopilotSDK.csproj` inside the `part1/` folder.

---

## 2. Add the GitHub Copilot SDK package

```bash
dotnet add package GitHub.Copilot.SDK --version 1.0.5
```

> [!NOTE]
> The SDK is evolving quickly. If you want the latest version, omit `--version 1.0.5`. The samples in this repo pin the version for reproducibility.

---

## 3. Update the project file

Open `HelloCopilotSDK.csproj` (inside the `part1/` folder) and make sure it looks like this:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RootNamespace>HelloCopilotSDK</RootNamespace>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="GitHub.Copilot.SDK" Version="1.0.5" />
  </ItemGroup>

</Project>
```

`ImplicitUsings` and `Nullable` keep the code concise and safe.

---

## 4. Verify the Copilot CLI

Run:

```bash
copilot --version
```

You should see a version number. Then sign in:

```bash
copilot login
```

Alternatively, set a `GH_TOKEN` environment variable with the **Copilot Requests** scope.

The Copilot CLI does not provide a standalone authentication-status command. The app verifies that your credentials work when it starts the SDK client and loads the available models.

---

## 5. Create the Helpers folder

Later steps will add helper classes. Create the folder now:

```bash
mkdir Helpers
```

---

## Checkpoint

- [ ] `dotnet --version` reports .NET 10.x.
- [ ] `copilot --version` works.
- [ ] `copilot login` completes, or `GH_TOKEN` is set.
- [ ] The project builds: `dotnet build part1` succeeds.

Next, you'll write the main program in [Part 1: Program.cs](02-program.md).
