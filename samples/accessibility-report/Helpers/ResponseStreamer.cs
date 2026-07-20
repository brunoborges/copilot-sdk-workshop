using GitHub.Copilot;

namespace AccessibilityReport.Helpers;

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
                case ToolExecutionStartEvent:
                    Console.WriteLine("\n🔧 Copilot is using a tool...");
                    break;
                case ToolExecutionCompleteEvent:
                    Console.WriteLine("✅ Tool completed.");
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