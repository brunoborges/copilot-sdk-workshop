using System.ComponentModel;
using GitHub.Copilot;
using Microsoft.Extensions.AI;

namespace HelloCopilotSDK.Helpers;

public static class AccessibilityRuleCatalog
{
    private static readonly AccessibilityRule[] Rules =
    [
        new("1.1.1", "Non-text Content", "An informative image has no useful text alternative.", "Add concise, meaningful alt text. Use alt=\"\" only for decorative images."),
        new("1.3.1", "Info and Relationships", "A page lacks a main landmark or uses headings that do not describe its structure.", "Use semantic landmarks such as <main> and preserve a logical heading hierarchy."),
        new("1.4.3", "Contrast (Minimum)", "Text does not have enough contrast against its background.", "Provide at least 4.5:1 contrast for normal text and 3:1 for large text."),
        new("2.4.7", "Focus Visible", "Keyboard focus cannot be seen clearly.", "Keep a visible, high-contrast focus indicator for every interactive element."),
        new("3.3.2", "Labels or Instructions", "A form input has no programmatic label or clear instruction.", "Associate a visible <label> with the input using matching for and id values.")
    ];

    public static AIFunction CreateLookupTool() => CopilotTool.DefineTool(
        ([Description("The accessibility issue or WCAG criterion to look up.")] string query) =>
            Task.FromResult(Lookup(query)),
        toolOptions: new CopilotToolOptions { SkipPermission = true },
        factoryOptions: new AIFunctionFactoryOptions
        {
            Name = "accessibility_rule_lookup",
            Description = "Looks up read-only WCAG accessibility guidance from this application's rule catalog."
        });

    private static AccessibilityRule Lookup(string query)
    {
        var normalizedQuery = query.ToLowerInvariant();
        return Rules.FirstOrDefault(rule =>
                   normalizedQuery.Contains(rule.Criterion, StringComparison.OrdinalIgnoreCase) ||
                   normalizedQuery.Contains(rule.Title, StringComparison.OrdinalIgnoreCase) ||
                   rule.Keywords.Any(keyword => normalizedQuery.Contains(keyword, StringComparison.OrdinalIgnoreCase)))
               ?? new AccessibilityRule("No exact match", "General accessibility guidance", "The issue is not in the small workshop catalog.", "Inspect semantic HTML, labels, keyboard access, text alternatives, and contrast.");
    }

    private sealed record AccessibilityRule(string Criterion, string Title, string WhenItApplies, string Recommendation)
    {
        public string[] Keywords => Title switch
        {
            "Non-text Content" => ["image", "alt", "photo"],
            "Info and Relationships" => ["main", "landmark", "heading", "structure"],
            "Contrast (Minimum)" => ["contrast", "color", "colour"],
            "Focus Visible" => ["focus", "keyboard", "outline"],
            "Labels or Instructions" => ["label", "input", "form"],
            _ => []
        };
    }
}