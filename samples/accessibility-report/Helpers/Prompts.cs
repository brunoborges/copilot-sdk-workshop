namespace AccessibilityReport.Helpers;

public static class Prompts
{
    public static string CreateReportPrompt(string url) => $"""
        Use the Playwright MCP server to analyze the accessibility of {url}.
        Navigate to the page, take an accessibility snapshot, and return a report with:
        - a short summary;
        - findings grouped by severity;
        - WCAG criteria and practical fixes;
        - a statistics summary for headings, links, landmarks, and form controls.

        Use accessibility_rule_lookup for project-specific WCAG guidance when it is useful.
        Include actual findings from the page, not examples.
        """;

    public static string CreateTestPrompt(string url, string language) => $"""
        Based on the accessibility report for {url}, generate a complete Playwright accessibility test file in {language}.
        Cover the findings, including landmarks, heading hierarchy, text alternatives, focus indicators, and form labels. Include helpful comments.
        """;
}