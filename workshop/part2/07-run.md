# Part 2: Run & Review

> **Duration:** ~10 minutes

In this final step you will run the complete accessibility report recipe against the Blazor target app, review the findings, and explore ways to extend the project.

---

## 1. Make sure you have a target URL

Use the deployed target app:

```text
https://YOUR_ORG.github.io/copilot-sdk-workshop/target-app/
```

Or, if you prefer to run locally, restart the Blazor app in a separate terminal:

```bash
dotnet run --project src/BlazorApp
```

Note the localhost URL.

---

## 2. Run the accessibility report

In another terminal, run:

```bash
dotnet run --project part2
```

When prompted, pick a model and enter the target app URL. For example:

```text
https://YOUR_ORG.github.io/copilot-sdk-workshop/target-app/
```

Or, if running locally:

```text
http://localhost:5000
```

Wait for the report to stream. Then decide whether to generate tests.

---

## 3. Review the seeded accessibility issues

The Blazor app intentionally contains several issues. Your report should surface some of these:

| Issue | WCAG Criterion | Where to look |
|-------|----------------|---------------|
| Missing `alt` text on images | 1.1.1 Non-text Content | `Home.razor` image tag |
| Missing `<main>` landmark | 1.3.1 Info and Relationships, 2.4.1 Bypass Blocks | `MainLayout.razor` |
| Poor heading hierarchy | 1.3.1 Info and Relationships | `Home.razor` headings |
| Low-contrast text | 1.4.3 Contrast (Minimum) | `app.css` muted text class |
| Missing form label | 3.3.2 Labels or Instructions | `Home.razor` input |

Compare the report's findings with the source code in `src/BlazorApp`. This is a great way to see how automated accessibility analysis maps back to real code.

---

## 4. Fix one issue and re-run

Try fixing one issue in the Blazor app, then re-run the report. For example:

1. Open `src/BlazorApp/Components/Pages/Home.razor`.
2. Add `alt` text to the image.
3. Save and restart the Blazor app.
4. Re-run the accessibility report.

You should see the image-related finding change from ❌ to ✅.

---

## 5. Experiment with other URLs

Once the recipe works against the Blazor app, try analyzing other sites:

```text
https://github.com
https://docs.github.com
```

Keep in mind that public sites may block automated browsers or require more time to analyze.

---

## 6. Ideas for extension

- **Output to a file:** Save the report as Markdown or HTML instead of printing to the console.
- **Batch mode:** Accept the URL from command-line arguments so the tool can run in CI.
- **Custom rules:** Add project-specific accessibility checks to the prompt.
- **Multi-page crawl:** Ask Copilot to follow links and report on multiple pages.

---

## Checkpoint

- [ ] The Blazor app is running.
- [ ] The accessibility report runs and produces a formatted report.
- [ ] You can correlate findings with code in `src/BlazorApp`.
- [ ] You fixed at least one issue and re-ran the report.

Congratulations — you have completed the Copilot SDK Workshop! 🎉

If you want to try the first workshop, head back to [Hello GitHub Copilot SDK](../part1/00-overview.md).
