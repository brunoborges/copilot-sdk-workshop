# Step 2: Stream a response

> **Time:** 10 minutes

## What you'll see

Response text will arrive while the session is still working, and the application will know when
the turn has finished.

## How streaming changes the experience

**Streaming** does not change the answer. It changes when your application receives it. Instead of
waiting for one completed message, the session emits events throughout the turn:

- `AssistantMessageDeltaEvent` contains each new piece of response text.
- `AssistantMessageEvent` contains the completed message.
- `SessionIdleEvent` means the turn and any tool work have finished.
- `SessionErrorEvent` reports a failed turn.

## Why progressive output feels better

Seeing text arrive makes the application feel more responsive. Later, the same event stream will
show activity from local and MCP tools.

The session flow is now `response deltas -> final message -> idle`.

## Let the response roll in

### 1. Add the streaming helper

Create `workshop-app/Helpers/ResponseStreamer.cs`:

:::language dotnet
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
:::
The final-message case handles a runtime that completes without sending deltas. An error completes
the task with an exception instead of looking like a successful turn.

### 2. Use the helper

In `Program.cs`, add `using HelloCopilotSDK.Helpers;`, then replace the session and response code
with:

:::language dotnet
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
:::
## Run it

:::language dotnet
```bash
dotnet run --project workshop-app
```
:::
The bullets should start appearing before the process exits:

```text
Connected to the Copilot runtime: ...

Copilot:
- Gives a control a programmatic identity.
- Helps screen-reader users understand its purpose.
- Connects visible labels to form controls.
```

:::language dotnet
<details>
<summary>Troubleshooting this run</summary>

| Symptom | Fix |
|---|---|
| Text appears only at the end | Confirm `Streaming = true` is in this session's `SessionConfig`. |
| The application exits before text appears | Confirm the helper awaits `completed.Task` after `SendAsync`. |
| Text is printed twice | Keep the `when !receivedDelta` guard on `AssistantMessageEvent`. |

</details>
:::

> **You're ready to add tools when:** response text appears before the full answer is complete.

## Check your understanding

When would `SendAndWaitAsync` be a better choice than event streaming?

<details>
<summary>Check your answer</summary>

Use `SendAndWaitAsync` for background work or simple request/response code that does not need
progressive output or intermediate events.

</details>

:::language dotnet
<details>
<summary>Complete Step 2 checkpoint</summary>

The completed Step 2 project is in
[`checkpoints/dotnet/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/dotnet/02-streaming).

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
:::

Continue to [Step 3: Add application-owned knowledge](03-local-tool.md).

:::language nodejs
Use `session.on("assistant.message_delta", ...)` and `session.on("session.idle", ...)` to stream
output; the shared `streamResponse` helper is in `src/workshop.ts`.
:::
:::language python
Use `AssistantMessageDeltaData` and `SessionIdleData` event payloads with `asyncio.Event`; the
matching helper is in `workshop.py`.
:::
:::language go
Subscribe with `session.On(func(event copilot.SessionEvent) { ... })`, print `AssistantMessageDeltaData`, and complete on `SessionIdleData`; run `go run .`. Deltas arrive before the final answer; if output is doubled, print either deltas or the completed message. See [`checkpoints/go/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/go/02-streaming).
:::
:::language rust
Use `session.subscribe()` and handle assistant delta and idle events in the async event loop; run `cargo run`. Progressive text proves streaming is active; ensure the subscription stays alive until idle. See [`checkpoints/rust/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/rust/02-streaming).
:::
:::language java
Register `session.on(...)` handlers for assistant message events and wait for the idle completion; run `mvn exec:java`. Output should appear progressively. If it prints only once, confirm `setStreaming(true)` is in `SessionConfig`. See [`checkpoints/java/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/java/02-streaming).
:::
