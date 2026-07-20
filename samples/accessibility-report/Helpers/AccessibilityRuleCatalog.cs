using System.ComponentModel;
using GitHub.Copilot;
using Microsoft.Extensions.AI;

namespace AccessibilityReport.Helpers;

public static class AccessibilityRuleCatalog
{
    public static AIFunction CreateLookupTool() => CopilotTool.DefineTool(
        ([Description("The accessibility issue or WCAG criterion to look up.")] string query) => Task.FromResult(new
        {
            Query = query,
            Guidance = "Use semantic HTML, meaningful text alternatives, visible keyboard focus, sufficient contrast, and programmatic labels."
        }),
        toolOptions: new CopilotToolOptions { SkipPermission = true },
        factoryOptions: new AIFunctionFactoryOptions
        {
            Name = "accessibility_rule_lookup",
            Description = "Looks up read-only WCAG guidance maintained by this application."
        });
}