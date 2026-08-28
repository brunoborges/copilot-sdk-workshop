using MuseumExhibitStudio;

Console.WriteLine("=== Museum Exhibit Studio ===");
Console.WriteLine("Approved Apollo 11 facts:");

for (var index = 0; index < CuratorPrompts.Apollo11Facts.Count; index++)
{
    Console.WriteLine($"{index + 1}. {CuratorPrompts.Apollo11Facts[index]}");
}

Console.Write("\nUse these facts? [Y/n]: ");
var useDefaults = Console.ReadLine()?.Trim();
var facts = useDefaults?.Equals("n", StringComparison.OrdinalIgnoreCase) == true
    ? ReadFacts()
    : CuratorPrompts.Apollo11Facts;

await using var client = new CopilotCuratorClient();
var studio = new MuseumExhibitService(client);

try
{
    var result = await studio.GenerateAsync(facts, Environment.GetEnvironmentVariable("COPILOT_MODEL"));
    Console.WriteLine($"\n{result.Content}\n");
    PrintValidation(result.Validation);
    return 0;
}
catch (TimeoutException)
{
    Console.Error.WriteLine("The curator did not respond within two minutes. Try again.");
    return 1;
}
catch (Exception exception)
{
    Console.Error.WriteLine($"Could not generate the exhibit: {exception.Message}");
    return 1;
}

static IReadOnlyList<string> ReadFacts()
{
    Console.WriteLine("Enter one approved fact per line. Submit a blank line when finished:");
    var facts = new List<string>();

    while (true)
    {
        var fact = Console.ReadLine();
        if (string.IsNullOrWhiteSpace(fact))
        {
            return facts;
        }

        facts.Add(fact.Trim());
    }
}

static void PrintValidation(ExhibitValidation validation)
{
    Console.WriteLine(validation.Valid
        ? "Structural checks passed."
        : "Structural checks found issues:");

    Console.WriteLine($"- One level-one title: {validation.Title.Present}");
    Console.WriteLine($"- Narrative section: {validation.Narrative.Present}");
    Console.WriteLine(
        $"- Narrative length: {validation.Narrative.WordCount} words " +
        $"(within 100-140: {validation.Narrative.WithinLimit})");
    Console.WriteLine($"- Visitor questions section: {validation.VisitorQuestions.Present}");
    Console.WriteLine(
        $"- Numbered questions: {validation.VisitorQuestions.QuestionCount} " +
        $"(exactly three: {validation.VisitorQuestions.ExactlyThree})");
    Console.WriteLine($"- Every item is a question: {validation.VisitorQuestions.AllItemsAreQuestions}");

    foreach (var error in validation.Errors)
    {
        Console.WriteLine($"  - {error}");
    }

    Console.WriteLine(
        "\nStructural checks do not prove factual grounding. " +
        "Unsupported claims require human review or a separate evaluator.");
}
