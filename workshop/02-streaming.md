# Step 2: Stream a response

> **Time:** 10 minutes

## What you'll see

You'll configure a streaming-enabled session and make completion visible. The .NET, Node.js,
Python, Go, and Rust checkpoints print response text while the session is still working. The Java
checkpoint uses the same streaming configuration but waits for the completed response.

## How streaming changes the experience

**Streaming** does not change the answer. It changes when an application that subscribes to the
event stream receives it. Instead of waiting for one completed message, the session emits events
throughout the turn:

- Assistant message delta events contain each new piece of response text.
- The completed assistant message event contains the full message.
- A session idle event means the turn and any tool work have finished.
- A session error event reports a failed turn.

## Why progressive output feels better

Seeing text arrive makes the application feel more responsive. Later, the same event stream will
show activity from local and MCP tools.

The session flow is now `response deltas -> final message -> idle`.

## Let the response roll in

:::language dotnet
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
:::
The final-message case handles a runtime that completes without sending deltas. An error completes
the task with an exception instead of looking like a successful turn.

:::language dotnet
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
:::
:::language nodejs
Use `session.on(callback)` in `workshop-app/src/workshop.ts`, inspect each event's `type`, print
assistant deltas, keep a final-message fallback, reject session errors, and resolve on idle. Call
that `streamResponse` helper from `src/index.ts`.
:::
:::language python
In `workshop-app/main.py`, handle `AssistantMessageDeltaData`, `AssistantMessageData`,
`SessionErrorData`, and `SessionIdleData` with an `asyncio.Event`, then wait for completion after
`session.send`.
:::
:::language go
In `workshop-app/main.go`, subscribe with `session.On`, print `AssistantMessageDeltaData`, keep an
`AssistantMessageData` fallback, and use `SendAndWait` to propagate completion errors.
:::
:::language rust
In `workshop-app/src/main.rs`, call `session.subscribe()` and use `tokio::select!` to print
assistant deltas while waiting for both send completion and the session idle event.
:::
:::language java
In `workshop-app/src/main/java/workshop/AccessibilityReport.java`, set streaming on
`SessionConfig`, call `sendAndWait`, and print the completed response returned by the Java
checkpoint.
:::

## Run it

:::language dotnet
```bash
dotnet run --project workshop-app
```
:::
:::language nodejs
```bash
npm --prefix workshop-app start
```
:::
:::language python
```bash
python workshop-app/main.py
```
:::
:::language go
```bash
go -C workshop-app run .
```
:::
:::language rust
```bash
cargo run --manifest-path workshop-app/Cargo.toml
```
:::
:::language java
```bash
mvn -f workshop-app/pom.xml exec:java
```
:::
The response should print before the process exits:

:::language dotnet
```text
Connected to the Copilot runtime: ...

Copilot:
- Gives a control a programmatic identity.
- Helps screen-reader users understand its purpose.
- Connects visible labels to form controls.
```
:::

:::language dotnet
The bullets should start appearing progressively.
:::
:::language nodejs
The one-sentence response should start appearing progressively through the event callback.
:::
:::language python
The bullets should start appearing progressively through the event callback.
:::
:::language go
The bullets should start appearing progressively through the event callback.
:::
:::language rust
The bullets should start appearing progressively through the event subscription.
:::
:::language java
The Java checkpoint uses a streaming-enabled session with `sendAndWait`, so it prints the completed
response when the turn finishes.
:::

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

> **You're ready to add tools when:** the configured response path prints an answer and completes
> the turn without hiding session errors.

## Check your understanding

When would a completed-response send be a better choice than event streaming?

<details>
<summary>Check your answer</summary>

Use a completed-response send for background work or simple request/response code that does not
need progressive output or intermediate events.

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

:::language nodejs
Compare your work with
[`checkpoints/nodejs/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/nodejs/02-streaming).
:::
:::language python
Compare your work with
[`checkpoints/python/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/python/02-streaming).
:::
:::language go
Compare your work with [`checkpoints/go/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/go/02-streaming).
:::
:::language rust
Compare your work with [`checkpoints/rust/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/rust/02-streaming).
:::
:::language java
Compare your work with
[`checkpoints/java/02-streaming`](https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/checkpoints/java/02-streaming).
:::

Continue to [Step 3: Add application-owned knowledge](03-local-tool.md).
