# Part 2: Generate Tests

> **Duration:** ~10 minutes

In this step you will add an optional flow that generates Playwright accessibility tests based on the report.

---

## 1. Ask whether to generate tests

After the report completes, add the yes/no prompt:

```csharp
// Prompt user for test generation
Console.Write("Would you like to generate Playwright accessibility tests? (y/n): ");
var generateTests = Console.ReadLine()?.Trim().ToLowerInvariant();
```

---

## 2. Detect the project language

Inside the `if` block, reset the completion source and ask Copilot to detect the language:

```csharp
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
```

---

## 3. Confirm the language

Add the language confirmation prompt:

```csharp
    Console.Write("\n\nConfirm language for tests (or enter a different one): ");
    var language = Console.ReadLine()?.Trim();

    if (string.IsNullOrWhiteSpace(language))
    {
        language = "TypeScript";
    }
```

---

## 4. Generate the tests

Reset the completion source again and ask for the test file:

```csharp
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
```

### What is happening here

1. The app asks the user if they want tests.
2. If yes, it resets the `TaskCompletionSource` so the event loop can wait for a new response.
3. It asks Copilot to detect the project's primary language.
4. It asks the user to confirm or override the language.
5. It resets the completion source again and asks Copilot to generate Playwright tests in that language.

---

## 2. Run and generate tests

```bash
dotnet run --project part2
```

Pick a model, enter the target app URL, then type `y` when asked about test generation. You should see a language suggestion followed by a complete Playwright test file.

---

## 3. Save the tests (optional)

The generated tests are printed to the console. You can copy them into a file such as `tests/accessibility.spec.ts` and run them with Playwright.

---

## Checkpoint

- [ ] The test-generation flow is added after the report.
- [ ] The `done` completion source is reset before each new SDK call.
- [ ] Running with `y` produces a Playwright test file.

Next, run the full workflow and review the results in [Part 2: Run & Review](07-run.md).
