# Generate Tests

> **Duration:** ~10 minutes

Reuse the report session to generate tests while its page findings and tool results remain in context:

```csharp
Console.Write("\nWould you like to generate Playwright accessibility tests? (y/n): ");
if (Console.ReadLine()?.Trim().ToLowerInvariant() is "y" or "yes")
{
    Console.Write("Language for tests [TypeScript]: ");
    var language = Console.ReadLine()?.Trim();
    language = string.IsNullOrWhiteSpace(language) ? "TypeScript" : language;

    var testPrompt = $"""
        Based on the accessibility report for {url}, generate a complete Playwright accessibility test file in {language}.
        Cover the findings, including landmarks, heading hierarchy, text alternatives, focus indicators, and form labels.
        Include helpful comments and output only the complete test file.
        """;

    await ResponseStreamer.SendAndPrintAsync(session, testPrompt);
}
```

## Checkpoint

- [ ] Test generation is optional.
- [ ] The same session maintains the report context.
- [ ] The generated test targets actual findings.

Finish with [Run and Review](12-run-review.md).
