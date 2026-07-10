using GitHub.Copilot;

namespace hello_copilot_sdk.Helpers;

public static class ChatHelper
{
    public static async Task SendMessageAndStreamResponse(CopilotSession session, string message)
    {
        var tcs = new TaskCompletionSource();
        var hasStreamedContent = false;

        session.On<SessionEvent>(evt =>
        {
            switch (evt)
            {
                case AssistantMessageDeltaEvent delta:
                    if (!string.IsNullOrEmpty(delta.Data.DeltaContent))
                    {
                        hasStreamedContent = true;
                        Console.Write(delta.Data.DeltaContent);
                    }
                    break;

                case AssistantMessageEvent msg:
                    if (!hasStreamedContent)
                    {
                        Console.Write(msg.Data.Content);
                    }
                    break;

                case SessionIdleEvent:
                    Console.WriteLine();
                    tcs.TrySetResult();
                    break;

                case SessionErrorEvent err:
                    Console.WriteLine($"\n❌ Error: {err.Data.Message}");
                    tcs.TrySetResult();
                    break;
            }
        });

        await session.SendAsync(new MessageOptions { Prompt = message });
        await tcs.Task;
    }
}
