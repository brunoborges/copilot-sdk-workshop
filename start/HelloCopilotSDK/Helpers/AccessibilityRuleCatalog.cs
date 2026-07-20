namespace HelloCopilotSDK.Helpers;

public static class AccessibilityRuleCatalog
{
    public static readonly AccessibilityRule[] Rules =
    [
        new("1.1.1", "Non-text Content", "Add concise alt text to informative images."),
        new("1.3.1", "Info and Relationships", "Use semantic landmarks and a logical heading hierarchy."),
        new("1.4.3", "Contrast (Minimum)", "Maintain sufficient text and background contrast."),
        new("2.4.7", "Focus Visible", "Keep keyboard focus visible."),
        new("3.3.2", "Labels or Instructions", "Associate every form input with a label.")
    ];
}

public sealed record AccessibilityRule(string Criterion, string Title, string Recommendation);