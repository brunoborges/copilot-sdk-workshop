# Step 2: Stream a response

> **Time:** 10 minutes

## Outcome

After this step, response text will appear incrementally while the session is working, and the
application will know exactly when processing finishes.

## What this means

**Streaming** does not change the answer. It changes when your application receives it.
Instead of waiting for one completed message, the session emits events throughout the turn:

- `AssistantMessageDeltaEvent` contains each new piece of response text.
- `AssistantMessageEvent` contains the completed message.
- `SessionIdleEvent` means the turn and any tool work have finished.
- `SessionErrorEvent` reports a failed turn.

## Why it matters

Progressive output feels faster to a person using the application. The event stream will also
become the single place where you observe local and MCP tool activity later.

> **Where it fits:** The session now emits `response deltas -> final message -> idle`.

## Make the change

### 1. Add the streaming helper

Create `workshop-app/Helpers/ResponseStreamer.cs`:

```csharp
using GitHub.Copilot;

namespace HelloCopilotSDK.Helpers;

public static class ResponseStreamer
{
    public static async Task SendAndPrintAsync(CopilotSession session, string prompt)
    {
        var completed = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var receivedDelta = false;

        using var subscription = session.On<SessionEvent>(sessionEvent =>
        {
            switch (sessionEvent)
            {
                case AssistantMessageDeltaEvent delta when !string.IsNullOrEmpty(delta.Data.DeltaContent):
                    receivedDelta = true;
                    Console.Write(delta.Data.DeltaContent);
                    break;
                case AssistantMessageEvent message when !receivedDelta:
                    Console.Write(message.Data.Content);
                    break;
                case SessionIdleEvent:
                    Console.WriteLine();
                    completed.TrySetResult();
                    break;
                case SessionErrorEvent error:
                    completed.TrySetException(new InvalidOperationException(error.Data.Message));
                    break;
            }
        });

        await session.SendAsync(new MessageOptions { Prompt = prompt });
        await completed.Task;
    }
}
```

The final-message case is a fallback for runtimes that complete without sending deltas. Errors
complete the task with an exception rather than looking like success.

### 2. Use the helper

In `Program.cs`, add `using HelloCopilotSDK.Helpers;`, then replace the session and response code
with:

```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Streaming = true
});

Console.WriteLine("\nCopilot:");
await ResponseStreamer.SendAndPrintAsync(
    session,
    "Explain accessible names in three short bullet points.");
```

## Run it

```bash
dotnet run --project workshop-app
```

The bullets should appear progressively before the process exits:

```text
Connected to the Copilot runtime: ...

Copilot:
- Gives a control a programmatic identity.
- Helps screen-reader users understand its purpose.
- Connects visible labels to form controls.
```

<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| Text appears only at the end | Confirm `Streaming = true` is in this session's `SessionConfig`. |
| The application exits before text appears | Confirm the helper awaits `completed.Task` after `SendAsync`. |
| Text is printed twice | Keep the `when !receivedDelta` guard on `AssistantMessageEvent`. |

</details>

> **You are ready to continue when:** response text appears before the full answer is complete.

## Check your understanding

When would `SendAndWaitAsync` be a better choice than event streaming?

<details>
<summary>Check your answer</summary>

Use `SendAndWaitAsync` for background work or simple request/response code where progressive output
and intermediate events do not improve the experience.

</details>

<details>
<summary>Complete Step 2 checkpoint</summary>

The full, compiling reference is
[`checkpoints/02-streaming`](https://github.com/codemillmatt/copilot-sdk-workshop/tree/main/checkpoints/02-streaming).

```csharp
using GitHub.Copilot;
using HelloCopilotSDK.Helpers;

Console.WriteLine("=== Streaming from Copilot ===\n");

await using var client = new CopilotClient();
await client.StartAsync();

var ping = await client.PingAsync("workshop");
Console.WriteLine($"Connected to the Copilot runtime: {ping.Message}\n");

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Streaming = true
});

Console.WriteLine("Copilot:");
await ResponseStreamer.SendAndPrintAsync(
    session,
    "Explain accessible names in three short bullet points.");
```

</details>

Continue to [Step 3: Add application-owned knowledge](03-local-tool.md).
