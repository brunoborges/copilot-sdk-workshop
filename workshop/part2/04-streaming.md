# Part 2: Streaming

> **Duration:** ~5 minutes

In this step you will add the event handler that streams the report to the console and waits for the model to finish.

---

## 1. Create the completion source

After creating the session, add:

```csharp
// Wait for response using session.idle event
var done = new TaskCompletionSource();
```

`TaskCompletionSource` lets us turn the event-based stream into an `await`-able method.

---

## 2. Add the event loop

Add the event handler:

```csharp
session.On<SessionEvent>(evt =>
{
    switch (evt)
    {
        case AssistantMessageDeltaEvent delta:
            Console.Write(delta.Data.DeltaContent);
            break;
        case SessionIdleEvent:
            done.TrySetResult();
            break;
        case SessionErrorEvent error:
            Console.WriteLine($"\nError: {error.Data.Message}");
            done.TrySetResult();
            break;
    }
});
```

This is the same event pattern you used in Part 1:

- `AssistantMessageDeltaEvent` prints each token as it arrives.
- `SessionIdleEvent` signals completion.
- `SessionErrorEvent` handles failures.

---

## 3. Send the prompt and wait

After the prompt definition, add:

```csharp
await session.SendAsync(new MessageOptions { Prompt = prompt });
await done.Task;

Console.WriteLine("\n\n=== Report Complete ===\n");
```

`MessageOptions` wraps the prompt and any other message settings. `await done.Task` blocks until the model finishes streaming.

---

## 3. Try a first run

Run:

```bash
dotnet run --project part2
```

When prompted, pick a model and enter the target app URL:

```text
https://jamesmontemagno.github.io/copilot-sdk-workshop/target-app/
```

If you are running the Blazor app locally instead, use your localhost URL (for example, `http://localhost:5000`).

You should see Copilot navigate the page and stream a basic accessibility analysis. The output will not be formatted yet — that comes next.

---

## Checkpoint

- [ ] The event handler streams tokens and waits for `SessionIdleEvent`.
- [ ] `session.SendAsync` sends the prompt.
- [ ] The recipe runs and produces output for the Blazor app URL.

Next, craft the structured report prompt in [Part 2: Report Prompt](05-prompt.md).
