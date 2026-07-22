# Step 1: Create your first Copilot session

> **Time:** 10 minutes

## Outcome

After this step, the console application will connect to the Copilot runtime, create one
conversation, send a prompt, and print a complete response.

## What this means

The **GitHub Copilot SDK** is the .NET API your application uses to run Copilot as an agent.
The **Copilot runtime** performs the agent work: it receives prompts, calls models, and manages
tools. Your C# code reaches that runtime through `CopilotClient`.

A `CopilotSession` is one continuing agent conversation. It holds the messages and tool results
that form that conversation's context. Reuse one client for the application, and create a session
for each independent conversation.

## Why it matters

This separation lets your application own connection lifetime independently from conversation
state. It also gives you the smallest useful success before adding streaming or tools.

> **Where it fits:** Your console app now contains `CopilotClient -> CopilotSession -> model response`.

## Make the change

Open `workshop-app/Program.cs` and **replace the entire file**:

```csharp
using GitHub.Copilot;

Console.WriteLine("=== First Copilot session ===\n");

await using var client = new CopilotClient();
await client.StartAsync();

var ping = await client.PingAsync("workshop");
Console.WriteLine($"Connected to the Copilot runtime: {ping.Message}");

await using var session = await client.CreateSessionAsync(new SessionConfig());
var response = await session.SendAndWaitAsync(
    "In one sentence, explain why an accessible name matters for a form input.");

if (response is null)
{
    throw new InvalidOperationException("Copilot completed without an assistant message.");
}

Console.WriteLine($"\nCopilot: {response.Data.Content}");
```

`PingAsync` is a connection check. `SendAndWaitAsync` sends the prompt and returns after the
session becomes idle, which is ideal when you only need the completed answer.

## Run it

```bash
dotnet run --project workshop-app
```

Your wording will vary, but the shape should be:

```text
=== First Copilot session ===

Connected to the Copilot runtime: ...

Copilot: An accessible name lets assistive technology identify the input's purpose.
```

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| Authentication or authorization error | Run `copilot login` again, then rerun the project. |
| Runtime executable not found | Set `COPILOT_CLI_BINARY_PATH` using the preflight instructions. |
| The request times out | Check network access to GitHub Copilot and retry; the code deliberately surfaces the failure. |

</details>

> **You are ready to continue when:** the terminal prints one complete Copilot response.

## Check your understanding

Which object should usually live for the application lifetime, and which object owns one
conversation's context?

<details>
<summary>Check your answer</summary>

Reuse `CopilotClient` for the runtime connection. A `CopilotSession` owns one conversation's
messages and tool context.

</details>

<details>
<summary>Complete Step 1 checkpoint</summary>

The full, compiling reference is
[`checkpoints/01-first-session`](https://github.com/codemillmatt/copilot-sdk-workshop/tree/main/checkpoints/01-first-session).

```csharp
using GitHub.Copilot;

Console.WriteLine("=== First Copilot session ===\n");

await using var client = new CopilotClient();
await client.StartAsync();

var ping = await client.PingAsync("workshop");
Console.WriteLine($"Connected to the Copilot runtime: {ping.Message}");

await using var session = await client.CreateSessionAsync(new SessionConfig());
var response = await session.SendAndWaitAsync(
    "In one sentence, explain why an accessible name matters for a form input.");

if (response is null)
{
    throw new InvalidOperationException("Copilot completed without an assistant message.");
}

Console.WriteLine($"\nCopilot: {response.Data.Content}");
```

</details>

Continue to [Step 2: Stream a response](02-streaming.md).
