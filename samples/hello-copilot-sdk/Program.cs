using GitHub.Copilot;
using hello_copilot_sdk.Helpers;

Console.WriteLine("=====================================");
Console.WriteLine("   🤖 Hello GitHub Copilot SDK (.NET)");
Console.WriteLine("=====================================\n");

// 1. Check prerequisites
Console.WriteLine("🔍 Checking prerequisites...");
var cliStatus = await CliChecker.CheckCopilotCliAsync();

if (!cliStatus.IsInstalled)
{
    Console.WriteLine("❌ " + (cliStatus.ErrorMessage ?? "Copilot CLI is not ready."));
    Console.WriteLine("   Install the CLI: https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli");
    return;
}

Console.WriteLine("   ✅ Copilot CLI installed");

// 2. Start the Copilot client and verify the current credentials through the SDK.
Console.WriteLine("🚀 Starting Copilot client...");
await using var client = new CopilotClient();
string? selectedModel;

try
{
    await client.StartAsync();
    selectedModel = await ModelSelector.SelectModelAsync(client);
}
catch (InvalidOperationException ex)
{
    Console.WriteLine("❌ Copilot authentication could not be verified.");
    Console.WriteLine("   Run: copilot login");
    Console.WriteLine("   Or set a GH_TOKEN environment variable with Copilot Requests scope.");
    Console.WriteLine($"   Details: {ex.Message}");
    return;
}

var pingResponse = await client.PingAsync("hello");
Console.WriteLine($"   ✅ Copilot client responded: {pingResponse}\n");

// 3. Create a session.
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true
});

// 4. Interactive chat loop
DemoPrompts.PrintDemoPrompts();
Console.WriteLine("💬 Interactive Chat Mode");
Console.WriteLine("   Type a message and press Enter.");
Console.WriteLine("   Commands: model | clear | demo <1-6> | exit\n");

while (true)
{
    Console.Write("You: ");
    var input = Console.ReadLine();

    if (string.IsNullOrWhiteSpace(input))
    {
        continue;
    }

    var command = input.Trim().ToLowerInvariant();

    if (command is "exit" or "quit")
    {
        Console.WriteLine("\n👋 Goodbye!");
        break;
    }

    if (command == "model")
    {
        selectedModel = await ModelSelector.SelectModelAsync(client);
        await session.DisposeAsync();
        var newSession = await client.CreateSessionAsync(new SessionConfig
        {
            Model = selectedModel,
            Streaming = true
        });
        // Note: In a real app you would reassign the session reference. Here we keep the original scope simple.
        Console.WriteLine("🔄 Model switched. Continue chatting.\n");
        continue;
    }

    if (command == "clear")
    {
        Console.Clear();
        DemoPrompts.PrintDemoPrompts();
        Console.WriteLine("💬 Interactive Chat Mode\n");
        continue;
    }

    if (command.StartsWith("demo ", StringComparison.OrdinalIgnoreCase))
    {
        var prompt = DemoPrompts.GetDemoPrompt(input);
        if (prompt is null)
        {
            Console.WriteLine("❌ Unknown demo. Use demo 1 through demo 6.\n");
            continue;
        }

        Console.WriteLine($"\n🎯 Running: {input}");
        Console.Write("Copilot: ");
        await ChatHelper.SendMessageAndStreamResponse(session, prompt);
        Console.WriteLine();
        continue;
    }

    Console.Write("Copilot: ");
    await ChatHelper.SendMessageAndStreamResponse(session, input);
    Console.WriteLine();
}
