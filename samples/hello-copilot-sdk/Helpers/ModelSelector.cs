using GitHub.Copilot;

namespace hello_copilot_sdk.Helpers;

public static class ModelSelector
{
    public static async Task<string?> SelectModelAsync(CopilotClient client)
    {
        var models = (await client.ListModelsAsync())?.ToList();

        if (models is null || models.Count == 0)
        {
            Console.WriteLine("⚠️ Could not fetch models. Using default model.");
            return null;
        }

        Console.WriteLine("\n🤖 Select a model:");
        for (var i = 0; i < models.Count; i++)
        {
            var model = models[i];
            Console.WriteLine($"   {i + 1}. {model.Name} (multiplier: {model.Billing?.Multiplier ?? 1}x)");
        }

        Console.Write($"\nEnter choice (1-{models.Count}) [default: 1]: ");
        var input = Console.ReadLine()?.Trim();

        if (string.IsNullOrWhiteSpace(input) || !int.TryParse(input, out var choice))
        {
            choice = 1;
        }

        if (choice < 1 || choice > models.Count)
        {
            choice = 1;
        }

        var selected = models[choice - 1];
        Console.WriteLine($"✅ Selected: {selected.Name}\n");
        return selected.Id;
    }

}
