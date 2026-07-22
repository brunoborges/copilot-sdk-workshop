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
REQUIRED_SECTIONS = [
    "## Outcome",
    "## What this means",
    "## Why it matters",
    "## Make the change",
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
            "https://github.com/codemillmatt/copilot-sdk-workshop/tree/main/",
            "https://github.com/codemillmatt/copilot-sdk-workshop/blob/main/",
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


for lesson_name in LESSONS:
    lesson_path = WORKSHOP / lesson_name
    require(lesson_path.exists(), f"Missing lesson {lesson_name}")
    if lesson_path.exists():
        validate_markdown_links(lesson_path)

for supporting_markdown in [ROOT / "README.md", ROOT / "start" / "README.md", ROOT / "checkpoints" / "README.md"]:
    validate_markdown_links(supporting_markdown)

start_readme = (ROOT / "start" / "README.md").read_text(encoding="utf-8")
require(
    "](../workshop/" not in start_readme,
    "Starter README links to raw lesson Markdown instead of the interactive viewer",
)

for lesson_name in CORE_LESSONS:
    lesson_path = WORKSHOP / lesson_name
    if not lesson_path.exists():
        continue
    lesson_text = lesson_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        require(section in lesson_text, f"{lesson_name} is missing required section: {section}")
    require(
        "You are ready to continue when:" in lesson_text
        or "You have completed the core workshop when:" in lesson_text,
        f"{lesson_name} is missing a readiness statement",
    )

for checkpoint in CHECKPOINTS:
    project = ROOT / "checkpoints" / checkpoint / "HelloCopilotSDK.csproj"
    program = ROOT / "checkpoints" / checkpoint / "Program.cs"
    require(project.exists(), f"Missing compiling project for checkpoint {checkpoint}")
    require(program.exists(), f"Missing complete Program.cs for checkpoint {checkpoint}")

mcp_projects = [
    ROOT / "samples" / "accessibility-report",
    *(ROOT / "checkpoints" / checkpoint for checkpoint in CHECKPOINTS[3:]),
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
    ROOT / "start" / "HelloCopilotSDK" / "Helpers" / "WorkshopPermissionHandler.cs",
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
    "](../src/",
]:
    require(forbidden not in published_text, f"Published content contains forbidden link pattern: {forbidden}")

require(not re.search(r"^\s*-\s+\[[ xX]\]", published_text, re.MULTILINE), "Lessons contain task-list checkboxes")

step_shell = (DOCS / "workshop" / "step.html").read_text(encoding="utf-8")
for lesson_name in LESSONS:
    require(lesson_name in step_shell, f"Lesson viewer does not register {lesson_name}")
for behavior_hook in [
    "copy-code-button",
    "aria-current=\"step\"",
    "event.key === 'Escape'",
    "trapNavigationFocus",
    "initializeTabs",
    "document.title =",
    'id="lessonStatus"',
    "aria-busy",
    "stateLabel",
]:
    require(behavior_hook in step_shell, f"Lesson viewer is missing behavior hook: {behavior_hook}")
require(
    'id="markdownContent" aria-live=' not in step_shell,
    "The full rendered lesson must not be an aria-live region",
)

homepage = (DOCS / "index.html").read_text(encoding="utf-8")
require(homepage.count('class="primary-action"') == 1, "Homepage must have exactly one primary action")
require("GitHub Copilot SDK" in homepage, "Homepage does not define the SDK")
require("Playwright inspection" in homepage, "Homepage does not show the application flow")

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
