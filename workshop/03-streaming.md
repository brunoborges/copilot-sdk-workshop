# Session and Streaming

> **Duration:** ~15 minutes

Create a session and stream its events to the console.

## 1. Create a response helper

Create `workshop-app/Helpers/ResponseStreamer.cs`:

```csharp
using GitHub.Copilot;

namespace HelloCopilotSDK.Helpers;

public static class ResponseStreamer
{
    public static async Task SendAndPrintAsync(CopilotSession session, string prompt)
    {
        var done = new TaskCompletionSource();
        var streamed = false;

        using var subscription = session.On<SessionEvent>(evt =>
        {
            switch (evt)
            {
                case AssistantMessageDeltaEvent delta when !string.IsNullOrEmpty(delta.Data.DeltaContent):
                    streamed = true;
                    Console.Write(delta.Data.DeltaContent);
                    break;
                case AssistantMessageEvent message when !streamed:
                    Console.Write(message.Data.Content);
                    break;
                case SessionIdleEvent:
                    Console.WriteLine();
                    done.TrySetResult();
                    break;
                case SessionErrorEvent error:
                    Console.WriteLine($"\n❌ Error: {error.Data.Message}");
                    done.TrySetResult();
                    break;
            }
        });

        await session.SendAsync(new MessageOptions { Prompt = prompt });
        await done.Task;
    }
}
```

## 2. Create and use the session

After selecting the model in `Program.cs`, add:

```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true
});

Console.Write("Ask an accessibility question: ");
var prompt = Console.ReadLine();
if (!string.IsNullOrWhiteSpace(prompt))
{
    await ResponseStreamer.SendAndPrintAsync(session, prompt);
}
```

## Checkpoint

- [ ] `SessionConfig` selects the model and enables streaming.
- [ ] Response text arrives incrementally.
- [ ] The helper awaits `SessionIdleEvent`.

Next, add a local tool in [Local Tool Calling](04-local-tools.md).
