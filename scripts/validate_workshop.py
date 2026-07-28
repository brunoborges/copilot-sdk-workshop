#!/usr/bin/env python3

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "workshop"
DOCS = ROOT / "docs"
DOTNET = "dotnet"
START_PROJECT = ROOT / "start" / DOTNET / "HelloCopilotSDK.csproj"
CHECKPOINT_ROOT = ROOT / "checkpoints" / DOTNET
SAMPLE_ROOT = ROOT / "samples" / DOTNET

LESSONS = [
    "00-preflight.md",
    "01-first-session.md",
    "02-streaming.md",
    "03-local-tool.md",
    "04-mcp-safety.md",
    "05-combine-tools.md",
    "06-structured-report.md",
    "07-run-explain.md",
    "08-model-selection.md",
]
CORE_LESSONS = LESSONS[1:8]
CHECKPOINTS = [
    "01-first-session",
    "02-streaming",
    "03-local-tool",
    "04-mcp-safety",
    "05-combine-tools",
    "06-structured-report",
]
LESSON_HEADINGS = {
    "00-preflight.md": ["## What you'll have ready"],
    "01-first-session.md": [
        "## What you'll build",
        "## Meet the GitHub Copilot SDK and runtime",
        "## Why clients and sessions stay separate",
        "## Fire up your first Copilot session",
    ],
    "02-streaming.md": [
        "## What you'll see",
        "## How streaming changes the experience",
        "## Why progressive output feels better",
        "## Let the response roll in",
    ],
    "03-local-tool.md": [
        "## What you'll add",
        "## Give Copilot a tool your app owns",
        "## Bring your own source of truth",
        "## Wire up the WCAG lookup",
    ],
    "04-mcp-safety.md": [
        "## What you'll connect",
        "## Meet MCP and its trust boundary",
        "## Reuse browser automation without giving it free rein",
        "## Put Playwright behind guardrails",
    ],
    "05-combine-tools.md": [
        "## What you'll orchestrate",
        "## Let the agent choose the right tool",
        "## Keep evidence and guidance in their lanes",
        "## Put both tools to work",
    ],
    "06-structured-report.md": [
        "## What you'll produce",
        "## Separate evidence from interpretation",
        "## Be useful without overstating the result",
        "## Give the report a contract",
    ],
    "07-run-explain.md": [
        "## What you'll be ready to explain",
        "## See the whole agent system",
        "## Take the design beyond this workshop",
        "## Take a victory lap",
    ],
    "08-model-selection.md": [
        "## What you'll customize",
        "## How model selection works",
        "## Swap models without changing the architecture",
        "## Add a model picker",
    ],
}
LESSON_READINESS = {
    "00-preflight.md": "**Start Step 1 when:**",
    "01-first-session.md": "**You're ready for streaming when:**",
    "02-streaming.md": "**You're ready to add tools when:**",
    "03-local-tool.md": "**You're ready for Playwright when:**",
    "04-mcp-safety.md": "**You're ready to combine tools when:**",
    "05-combine-tools.md": "**You're ready to shape the report when:**",
    "06-structured-report.md": "**You're ready for the final run when:**",
    "07-run-explain.md": "**You have completed the core workshop when:**",
    "08-model-selection.md": "**The extension is complete when:**",
}
CORE_REQUIRED_SECTIONS = [
    "## Run it",
    "## Check your understanding",
]

errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


class LocalAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute_name = "href" if tag in {"a", "link"} else "src" if tag in {"script", "img"} else None
        if attribute_name is None:
            return

        attributes = dict(attrs)
        value = attributes.get(attribute_name)
        if value:
            self.references.append(value)


def validate_html_assets(html_file: Path) -> None:
    parser = LocalAssetParser()
    parser.feed(html_file.read_text(encoding="utf-8"))

    for reference in parser.references:
        parsed = urlsplit(reference)
        if parsed.scheme or reference.startswith(("#", "?", "//", "data:")):
            continue

        target = (html_file.parent / parsed.path).resolve()
        if parsed.path.endswith("/"):
            target /= "index.html"
        require(target.exists(), f"{html_file.relative_to(ROOT)} links to missing local asset {reference}")


def validate_markdown_links(markdown_file: Path) -> None:
    text = markdown_file.read_text(encoding="utf-8")
    for target_text in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        target_value = target_text.split(maxsplit=1)[0].strip("<>")
        local_github_prefixes = [
            "https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/",
            "https://github.com/jamesmontemagno/copilot-sdk-workshop/blob/main/",
        ]
        matching_prefix = next(
            (prefix for prefix in local_github_prefixes if target_value.startswith(prefix)),
            None,
        )
        if matching_prefix:
            repository_target = ROOT / target_value.removeprefix(matching_prefix)
            require(
                repository_target.exists(),
                f"{markdown_file.relative_to(ROOT)} links to missing repository path {target_value}",
            )
            continue

        parsed = urlsplit(target_value)
        if parsed.scheme or target_value.startswith(("#", "mailto:")):
            continue

        target = (markdown_file.parent / parsed.path).resolve()
        require(target.exists(), f"{markdown_file.relative_to(ROOT)} links to missing file {target_value}")


def validate_language_directives(markdown_file: Path) -> None:
    active_language: str | None = None
    has_dotnet_block = False
    lines = markdown_file.read_text(encoding="utf-8").splitlines()
    language_specific = re.compile(
        r"\bdotnet\b|\bC#\b|start/dotnet|checkpoints/dotnet|samples/dotnet|"
        r"CopilotClient|CopilotSession|SessionConfig|AIFunction|McpServerConfig|PermissionDecision",
        re.IGNORECASE,
    )

    for line_number, line in enumerate(lines, start=1):
        language_match = re.fullmatch(r":::language\s+(\S+)\s*", line)
        if language_match:
            require(
                active_language is None,
                f"{markdown_file.relative_to(ROOT)}:{line_number} nests a language directive",
            )
            active_language = language_match.group(1)
            require(
                active_language == DOTNET,
                f"{markdown_file.relative_to(ROOT)}:{line_number} uses unknown language {active_language}",
            )
            has_dotnet_block = has_dotnet_block or active_language == DOTNET
            continue

        if re.fullmatch(r":::\s*", line):
            require(
                active_language is not None,
                f"{markdown_file.relative_to(ROOT)}:{line_number} closes no language directive",
            )
            active_language = None
            continue

        if line.startswith(":::"):
            require(
                False,
                f"{markdown_file.relative_to(ROOT)}:{line_number} has invalid language directive syntax",
            )

        if active_language is None and language_specific.search(line):
            require(
                False,
                f"{markdown_file.relative_to(ROOT)}:{line_number} exposes .NET-specific content outside a language block",
            )

    require(
        active_language is None,
        f"{markdown_file.relative_to(ROOT)} has an unclosed language directive",
    )
    require(
        has_dotnet_block,
        f"{markdown_file.relative_to(ROOT)} has no .NET language block",
    )


for lesson_name in LESSONS:
    lesson_path = WORKSHOP / lesson_name
    require(lesson_path.exists(), f"Missing lesson {lesson_name}")
    if lesson_path.exists():
        validate_markdown_links(lesson_path)
        validate_language_directives(lesson_path)
        lesson_text = lesson_path.read_text(encoding="utf-8")
        for heading in LESSON_HEADINGS[lesson_name]:
            require(heading in lesson_text, f"{lesson_name} is missing tailored heading: {heading}")
        require(
            LESSON_READINESS[lesson_name] in lesson_text,
            f"{lesson_name} is missing its readiness statement",
        )
        for generic_heading in [
            "## Outcome",
            "## What this means",
            "## Why it matters",
            "## Make the change",
        ]:
            require(
                generic_heading not in lesson_text,
                f"{lesson_name} still uses generic heading: {generic_heading}",
            )

for supporting_markdown in [ROOT / "README.md", ROOT / "start" / "README.md", ROOT / "checkpoints" / "README.md"]:
    validate_markdown_links(supporting_markdown)

start_readme = (ROOT / "start" / "README.md").read_text(encoding="utf-8")
require(
    "](../workshop/" not in start_readme,
    "Starter README links to raw lesson Markdown instead of the interactive viewer",
)

wcag_definition = "Web Content Accessibility Guidelines (WCAG)"
for entry_point in [
    ROOT / "README.md",
    ROOT / "start" / "README.md",
    WORKSHOP / "03-local-tool.md",
    DOCS / "index.html",
]:
    require(
        wcag_definition in entry_point.read_text(encoding="utf-8"),
        f"{entry_point.relative_to(ROOT)} uses WCAG without defining the acronym",
    )

for lesson_name in CORE_LESSONS:
    lesson_path = WORKSHOP / lesson_name
    if not lesson_path.exists():
        continue
    lesson_text = lesson_path.read_text(encoding="utf-8")
    for section in CORE_REQUIRED_SECTIONS:
        require(section in lesson_text, f"{lesson_name} is missing required section: {section}")

for checkpoint in CHECKPOINTS:
    project = CHECKPOINT_ROOT / checkpoint / "HelloCopilotSDK.csproj"
    program = CHECKPOINT_ROOT / checkpoint / "Program.cs"
    require(project.exists(), f"Missing compiling project for checkpoint {checkpoint}")
    require(program.exists(), f"Missing complete Program.cs for checkpoint {checkpoint}")

mcp_projects = [
    SAMPLE_ROOT / "accessibility-report",
    *(CHECKPOINT_ROOT / checkpoint for checkpoint in CHECKPOINTS[3:]),
]
for project_directory in mcp_projects:
    program_text = (project_directory / "Program.cs").read_text(encoding="utf-8")
    require(
        "browser_snapshot" not in program_text,
        f"{project_directory.relative_to(ROOT)} exposes the file-capable browser_snapshot tool",
    )
    require(
        "PlaywrightSnapshotReader.CreateTool(workingDirectory)" in program_text,
        f"{project_directory.relative_to(ROOT)} is missing the scoped snapshot reader",
    )
    require(
        (project_directory / "Helpers" / "PlaywrightSnapshotReader.cs").exists(),
        f"{project_directory.relative_to(ROOT)} is missing PlaywrightSnapshotReader.cs",
    )

permission_helpers = [
    START_PROJECT.parent / "Helpers" / "WorkshopPermissionHandler.cs",
    *(project / "Helpers" / "WorkshopPermissionHandler.cs" for project in mcp_projects),
]
for helper in permission_helpers:
    helper_text = helper.read_text(encoding="utf-8")
    require(
        "UriComponents.Fragment" in helper_text and "StringComparison.Ordinal)" in helper_text,
        f"{helper.relative_to(ROOT)} does not compare the complete target URL exactly",
    )

published_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in [ROOT / "README.md", *WORKSHOP.glob("*.md"), *DOCS.rglob("*.html")]
)
for forbidden in [
    "jamesmontemagno.github.io",
    "codemillmatt.github.io",
    "](../start/",
    "](../samples/",
    "start/HelloCopilotSDK",
    "checkpoints/01-first-session",
    "samples/accessibility-report",
    "](../src/",
]:
    require(forbidden not in published_text, f"Published content contains forbidden link pattern: {forbidden}")

require(not re.search(r"^\s*-\s+\[[ xX]\]", published_text, re.MULTILINE), "Lessons contain task-list checkboxes")

step_shell = (DOCS / "workshop" / "step.html").read_text(encoding="utf-8")
for lesson_name in LESSONS:
    require(lesson_name in step_shell, f"Lesson viewer does not register {lesson_name}")
for behavior_hook in [
    'class="header"',
    'class="flyout-panel"',
    'class="flyout-link',
    "🤖 Workshop Steps",
    "🏠 Hub",
    "copy-code-button",
    "aria-current=\"step\"",
    "event.key === 'Escape'",
    "trapNavigationFocus",
    "toggleAttribute('inert'",
    "initializeTabs",
    "document.title =",
    'id="lessonStatus"',
    'id="progressTrack"',
    "aria-busy",
]:
    require(behavior_hook in step_shell, f"Lesson viewer is missing behavior hook: {behavior_hook}")
require(
    'id="markdownContent" aria-live=' not in step_shell,
    "The full rendered lesson must not be an aria-live region",
)
require(
    'id="architectureFlow"' not in step_shell,
    "Lesson viewer duplicates the step navigation with an architecture strip",
)

homepage = (DOCS / "index.html").read_text(encoding="utf-8")
require(homepage.count('class="primary-action"') == 1, "Homepage must have exactly one primary action")
require("GitHub Copilot SDK" in homepage, "Homepage does not define the SDK")
require("Playwright inspection" in homepage, "Homepage does not show the application flow")
for homepage_hook in [
    'class="hero-layout"',
    'class="terminal-preview"',
    "🤖",
    "🎯 Target App",
]:
    require(homepage_hook in homepage, f"Homepage is missing hybrid UX hook: {homepage_hook}")

for stylesheet_name in ["styles.css", "step.css"]:
    stylesheet = (DOCS / stylesheet_name).read_text(encoding="utf-8")
    for theme_token in [
        "--neon-cyan: #00f5ff",
        "--neon-magenta: #ff00ff",
        "--neon-purple: #b366ff",
    ]:
        require(
            theme_token in stylesheet,
            f"{stylesheet_name} is missing upstream theme token: {theme_token}",
        )

for html_file in [DOCS / "index.html", DOCS / "workshop" / "step.html", DOCS / "target-app" / "index.html"]:
    validate_html_assets(html_file)

if errors:
    print("Workshop validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(
    f"Workshop content validation passed: {len(LESSONS)} lessons, "
    f"{len(CHECKPOINTS)} compiling checkpoints, and all local site assets resolved."
)
