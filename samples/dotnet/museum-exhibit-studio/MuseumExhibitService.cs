using GitHub.Copilot;

namespace MuseumExhibitStudio;

public sealed record GeneratedExhibit(string Content, ExhibitValidation Validation);

public sealed class MuseumExhibitService(ICuratorClient client)
{
    public static readonly TimeSpan GenerationTimeout = TimeSpan.FromMinutes(2);

    public async Task<GeneratedExhibit> GenerateAsync(
        IEnumerable<string> approvedFacts,
        string? model = null,
        CancellationToken cancellationToken = default)
    {
        var prompt = CuratorPrompts.BuildExhibitPrompt(approvedFacts);

        await client.StartAsync(cancellationToken);
        try
        {
            await using var session = await client.CreateSessionAsync(
                CreateSessionConfiguration(model),
                cancellationToken);
            var content = await session.SendAndWaitAsync(
                prompt,
                GenerationTimeout,
                cancellationToken);

            if (string.IsNullOrWhiteSpace(content))
            {
                throw new InvalidOperationException("The curator returned no exhibit content.");
            }

            return new GeneratedExhibit(content, ExhibitValidator.Validate(content));
        }
        finally
        {
            await client.StopAsync();
        }
    }

    public static SessionConfig CreateSessionConfiguration(string? model = null) => new()
    {
        ClientName = "museum-exhibit-studio",
        Model = string.IsNullOrWhiteSpace(model) ? null : model,
        AvailableTools = [],
        Streaming = false,
        SystemMessage = new SystemMessageConfig
        {
            Mode = SystemMessageMode.Replace,
            Content = CuratorPrompts.SystemMessage
        }
    };
}
