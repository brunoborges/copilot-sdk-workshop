# Report Prompt

> **Duration:** ~10 minutes

Replace the basic prompt with a structured report request:

```csharp
var prompt = $"""
    Use the Playwright MCP server to analyze the accessibility of this webpage: {url}

    1. Navigate to the URL and take an accessibility snapshot.
    2. Inspect page structure, headings, landmarks, images, links, and form controls.
    3. Use accessibility_rule_lookup when you need project-specific WCAG guidance.

    Format the report as:
    # Accessibility Report
    ## What's working well
    ## Issues found
    | Severity | Issue | WCAG criterion | Recommendation |
    |----------|-------|----------------|----------------|
    ## Statistics
    Include counts for headings, links, landmarks, images, and form controls.
    ## Priority actions

    Use actual findings from the page. Mark high severity with 🔴, medium with 🟡, and passing checks with ✅.
    """;
```

The prompt asks for browser evidence, a predictable output shape, and local guidance only when it adds value.

Next, add test generation in [Generate Tests](11-generate-tests.md).
