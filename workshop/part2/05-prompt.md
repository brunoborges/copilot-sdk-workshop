# Part 2: Report Prompt

> **Duration:** ~10 minutes

In this step you will replace the basic prompt with a structured prompt that asks Copilot to return a WCAG-aligned accessibility report with emoji indicators, tables, and a stats summary.

---

## 1. Replace the prompt

Replace the `prompt` variable with the structured report prompt:

```csharp
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
```

### Why this works

Large language models follow structure and examples. By giving Copilot:

- A clear task list (`1.`, `2.`, `3.`),
- An exact output template,
- Emoji conventions,
- Markdown table headers,

you make the output consistent and easy to read.

---

## 2. Run again

```bash
dotnet run --project part2
```

Pick a model and enter the target app URL. This time the output should be a formatted report with tables and emoji indicators.

---

## 3. Inspect the findings

Look for issues such as:

- Missing `alt` text on images.
- Missing or incorrect heading hierarchy.
- Missing `<main>` landmark.
- Low-contrast text.
- Missing form labels.

These are the kinds of issues intentionally seeded in the Blazor target app.

---

## Checkpoint

- [ ] The prompt includes the structured report template.
- [ ] Running the recipe produces a formatted report.
- [ ] The report surfaces real accessibility findings from the Blazor app.

Next, add optional Playwright test generation in [Part 2: Generate Tests](06-tests.md).
