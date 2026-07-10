using GitHub.Copilot;

// Create and start client
await using var client = new CopilotClient();
await client.StartAsync();

Console.WriteLine("=== Accessibility Report Generator ===");
Console.WriteLine();

// Pick a model
var models = await client.ListModelsAsync();
if (models is null || !models.Any())
{
    Console.WriteLine("⚠️ Could not fetch models. Using default model.");
}

string? selectedModel = null;
if (models is not null && models.Any())
{
    var modelList = models.ToList();
    Console.WriteLine("\n🤖 Select a model:");
    for (var i = 0; i < modelList.Count; i++)
    {
        var model = modelList[i];
        Console.WriteLine($"   {i + 1}. {model.Name} (multiplier: {model.Billing?.Multiplier ?? 1}x)");
    }

    Console.Write($"\nEnter choice (1-{modelList.Count}) [default: 1]: ");
    var input = Console.ReadLine()?.Trim();

    if (string.IsNullOrWhiteSpace(input) || !int.TryParse(input, out var choice))
    {
        choice = 1;
    }

    if (choice < 1 || choice > modelList.Count)
    {
        choice = 1;
    }

    selectedModel = modelList[choice - 1].Id;
    Console.WriteLine($"✅ Selected: {modelList[choice - 1].Name}\n");
}

Console.Write("Enter URL to analyze: ");
var url = Console.ReadLine()?.Trim();

if (string.IsNullOrWhiteSpace(url))
{
    Console.WriteLine("No URL provided. Exiting.");
    return;
}

// Ensure URL has a scheme
if (!url.StartsWith("http://") && !url.StartsWith("https://"))
{
    url = "https://" + url;
}

Console.WriteLine($"\nAnalyzing: {url}");
Console.WriteLine("Please wait...\n");

// Create a session with Playwright MCP server
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = selectedModel,
    Streaming = true,
    OnPermissionRequest = PermissionHandler.ApproveAll,
    McpServers = new Dictionary<string, McpServerConfig>()
    {
        ["playwright"] = new McpStdioServerConfig
        {
            Command = "npx",
            Args = ["@playwright/mcp@0.0.77", "--browser=msedge"],
            Tools = ["*"]
        }
    },
});

// Wait for response using session.idle event
var done = new TaskCompletionSource();

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

var prompt = $"""
    Use the Playwright MCP server to analyze the accessibility of this webpage: {url}

    Please:
    1. Navigate to the URL using playwright-browser_navigate
    2. Take an accessibility snapshot using playwright-browser_snapshot
    3. Analyze the snapshot and provide a detailed accessibility report

    Format the report EXACTLY like this structure with emoji indicators:

    📊 Accessibility Report: [Page Title] (domain.com)

    ✅ What's Working Well
    | Category | Status | Details |
    |----------|--------|---------|
    | Language | ✅ Pass | lang="en-US" properly set |
    | Page Title | ✅ Pass | "[Title]" is descriptive |
    | Heading Hierarchy | ✅ Pass | Single H1, proper H2/H3 structure |
    | Images | ✅ Pass | All X images have alt text |

    ⚠️ Issues Found
    | Severity | Issue | WCAG Criterion | Recommendation |
    |----------|-------|----------------|----------------|
    | 🔴 High | No <main> landmark | 1.3.1, 2.4.1 | Wrap main content in <main> element |
    | 🟡 Medium | Focus outlines disabled | 2.4.7 | Ensure visible :focus styles exist |

    📋 Stats Summary
    - Total Links: X
    - Total Headings: X
    - Focusable Elements: X
    - Landmarks Found: banner ✅, navigation ✅, main ❌, footer ✅

    ⚙️ Priority Recommendations

    Use ✅ for pass, 🔴 for high severity issues, 🟡 for medium severity, ❌ for missing items.
    Include actual findings from the page analysis - don't just copy the example.
    """;

await session.SendAsync(new MessageOptions { Prompt = prompt });
await done.Task;

Console.WriteLine("\n\n=== Report Complete ===\n");

// Prompt user for test generation
Console.Write("Would you like to generate Playwright accessibility tests? (y/n): ");
var generateTests = Console.ReadLine()?.Trim().ToLowerInvariant();

if (generateTests == "y" || generateTests == "yes")
{
    // Reset for next interaction
    done = new TaskCompletionSource();

    var detectLanguagePrompt = $"""
        Analyze the current working directory to detect the primary programming language used in this project.
        Respond with ONLY the detected language name and a brief explanation.
        If no project is detected, suggest "TypeScript" as the default for Playwright tests.
        """;

    Console.WriteLine("\nDetecting project language...\n");
    await session.SendAsync(new MessageOptions { Prompt = detectLanguagePrompt });
    await done.Task;

    Console.Write("\n\nConfirm language for tests (or enter a different one): ");
    var language = Console.ReadLine()?.Trim();

    if (string.IsNullOrWhiteSpace(language))
    {
        language = "TypeScript";
    }

    // Reset for test generation
    done = new TaskCompletionSource();

    var testGenerationPrompt = $"""
        Based on the accessibility report you just generated for {url}, create Playwright accessibility tests in {language}.

        The tests should:
        1. Verify all the accessibility checks from the report
        2. Test for the issues that were found (to ensure they get fixed)
        3. Include tests for landmarks, heading hierarchy, alt text, focus indicators, and more
        4. Use Playwright's accessibility testing features
        5. Include helpful comments explaining each test

        Output the complete test file that can be saved and run.
        """;

    Console.WriteLine("\nGenerating accessibility tests...\n");
    await session.SendAsync(new MessageOptions { Prompt = testGenerationPrompt });
    await done.Task;

    Console.WriteLine("\n\n=== Tests Generated ===");
}
