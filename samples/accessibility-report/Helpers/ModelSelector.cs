using GitHub.Copilot;

namespace AccessibilityReport.Helpers;

public static class ModelSelector
{
    public static async Task<string?> SelectModelAsync(CopilotClient client)
    {
        var models = (await client.ListModelsAsync())?.ToList();
        if (models is null || models.Count == 0)
        {
            Console.WriteLine("⚠️ Could not fetch models. Using the default model.");
            return null;
        }

        Console.WriteLine("🤖 Select a model:");
        for (var i = 0; i < models.Count; i++)
        {
            Console.WriteLine($"   {i + 1}. {models[i].Name}");
        }

        Console.Write($"Enter choice (1-{models.Count}) [default: 1]: ");
        var isValidChoice = int.TryParse(Console.ReadLine()?.Trim(), out var choice) && choice >= 1 && choice <= models.Count;
        var selected = models[(isValidChoice ? choice : 1) - 1];
        Console.WriteLine($"✅ Selected: {selected.Name}");
        return selected.Id;
    }
}