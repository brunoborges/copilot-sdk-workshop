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
LANGUAGES = ("dotnet", "nodejs", "python", "go", "rust", "java")
LESSONS = (
    "00-preflight.md",
    "01-first-session.md",
    "02-streaming.md",
    "03-local-tool.md",
    "04-mcp-safety.md",
    "05-combine-tools.md",
    "06-structured-report.md",
    "07-run-explain.md",
    "08-model-selection.md",
)
CHECKPOINTS = (
    "01-first-session",
    "02-streaming",
    "03-local-tool",
    "04-mcp-safety",
    "05-combine-tools",
    "06-structured-report",
)
OFFICIAL_SDK_URLS = {
    "dotnet": "https://github.com/github/copilot-sdk/tree/main/dotnet",
    "nodejs": "https://github.com/github/copilot-sdk/tree/main/nodejs",
    "python": "https://github.com/github/copilot-sdk/tree/main/python",
    "go": "https://github.com/github/copilot-sdk/tree/main/go",
    "rust": "https://github.com/github/copilot-sdk/tree/main/rust",
    "java": "https://github.com/github/copilot-sdk/tree/main/java",
}
MANIFESTS = {
    "dotnet": "*.csproj",
    "nodejs": "package.json",
    "python": "requirements.txt",
    "go": "go.mod",
    "rust": "Cargo.toml",
    "java": "pom.xml",
}
SOURCE_FILES = {
    "dotnet": "Program.cs",
    "nodejs": "src/workshop.ts",
    "python": "workshop.py",
    "go": "main.go",
    "rust": "src/main.rs",
    "java": "src/main/java/workshop/AccessibilityReport.java",
}
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


class LocalAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute = "href" if tag in {"a", "link"} else "src" if tag in {"script", "img"} else None
        if attribute:
            value = dict(attrs).get(attribute)
            if value:
                self.references.append(value)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_manifest(directory: Path, language: str) -> bool:
    manifest = MANIFESTS[language]
    return bool(list(directory.glob(manifest))) if "*" in manifest else (directory / manifest).exists()


def project_source(directory: Path) -> str:
    source_suffixes = {
        ".cs", ".ts", ".py", ".go", ".rs", ".java"
    }
    return "\n".join(
        read(path) for path in directory.rglob("*")
        if path.is_file() and path.suffix in source_suffixes
    )


def validate_html_assets(html_file: Path) -> None:
    parser = LocalAssetParser()
    parser.feed(read(html_file))
    for reference in parser.references:
        parsed = urlsplit(reference)
        if parsed.scheme or reference.startswith(("#", "?", "//", "data:")):
            continue
        target = (html_file.parent / parsed.path).resolve()
        if parsed.path.endswith("/"):
            target /= "index.html"
        require(target.exists(), f"{html_file.relative_to(ROOT)} links to missing local asset {reference}")


def validate_markdown_links(markdown_file: Path) -> None:
    for target_text in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", read(markdown_file)):
        target_value = target_text.split(maxsplit=1)[0].strip("<>")
        prefixes = (
            "https://github.com/jamesmontemagno/copilot-sdk-workshop/tree/main/",
            "https://github.com/jamesmontemagno/copilot-sdk-workshop/blob/main/",
        )
        prefix = next((candidate for candidate in prefixes if target_value.startswith(candidate)), None)
        if prefix:
            require(
                (ROOT / target_value.removeprefix(prefix)).exists(),
                f"{markdown_file.relative_to(ROOT)} links to missing repository path {target_value}",
            )
            continue
        parsed = urlsplit(target_value)
        if parsed.scheme or target_value.startswith(("#", "mailto:")):
            continue
        require(
            (markdown_file.parent / parsed.path).resolve().exists(),
            f"{markdown_file.relative_to(ROOT)} links to missing file {target_value}",
        )


def validate_language_directives(markdown_file: Path) -> None:
    active_language: str | None = None
    blocks: set[str] = set()
    for line_number, line in enumerate(read(markdown_file).splitlines(), start=1):
        opening = re.fullmatch(r":::language ([a-z0-9]+)", line)
        if opening:
            require(active_language is None, f"{markdown_file.relative_to(ROOT)}:{line_number} nests a language directive")
            active_language = opening.group(1)
            require(active_language in LANGUAGES, f"{markdown_file.relative_to(ROOT)}:{line_number} uses unknown language {active_language}")
            blocks.add(active_language)
        elif line == ":::":
            require(active_language is not None, f"{markdown_file.relative_to(ROOT)}:{line_number} closes no language directive")
            active_language = None
        elif line.startswith(":::"):
            require(False, f"{markdown_file.relative_to(ROOT)}:{line_number} has invalid language directive syntax")
    require(active_language is None, f"{markdown_file.relative_to(ROOT)} has an unclosed language directive")
    require(blocks == set(LANGUAGES), f"{markdown_file.relative_to(ROOT)} must contain exactly one or more blocks for all six languages")


def validate_language_registry() -> None:
    registry = read(DOCS / "language-registry.js")
    ids = re.findall(r"\bid: '([a-z0-9]+)'", registry)
    require(ids == list(LANGUAGES), "docs/language-registry.js must be the ordered six-language registry")
    for language, url in OFFICIAL_SDK_URLS.items():
        require(url in registry, f"Language registry has no official {language} SDK link")
    require("Object.freeze" in registry and "getLanguage" in registry, "Language registry must expose immutable language lookup")


def validate_layout() -> None:
    for language in LANGUAGES:
        for directory in [ROOT / "start" / language, ROOT / "samples" / language / "hello-copilot-sdk", ROOT / "samples" / language / "accessibility-report"]:
            require(directory.is_dir(), f"Missing {language} project directory {directory.relative_to(ROOT)}")
            require(has_manifest(directory, language), f"Missing {language} manifest in {directory.relative_to(ROOT)}")
        for checkpoint in CHECKPOINTS:
            directory = ROOT / "checkpoints" / language / checkpoint
            require(directory.is_dir(), f"Missing {language} checkpoint {checkpoint}")
            require(has_manifest(directory, language), f"Missing {language} manifest in {directory.relative_to(ROOT)}")
            require((directory / SOURCE_FILES[language]).exists(), f"Missing {language} source in {directory.relative_to(ROOT)}")
    for language in ("nodejs", "rust"):
        for directory in [ROOT / "start" / language, *(ROOT / "samples" / language / sample for sample in ("hello-copilot-sdk", "accessibility-report")), *(ROOT / "checkpoints" / language / checkpoint for checkpoint in CHECKPOINTS)]:
            lock = "package-lock.json" if language == "nodejs" else "Cargo.lock"
            require((directory / lock).exists(), f"Missing deterministic {language} lock file in {directory.relative_to(ROOT)}")


def validate_security_invariants() -> None:
    required_tools = ("accessibility_rule_lookup", "read_latest_accessibility_snapshot", "playwright-browser_navigate")
    for language in LANGUAGES:
        directories = [
            ROOT / "checkpoints" / language / checkpoint
            for checkpoint in CHECKPOINTS[3:]
        ] + [ROOT / "samples" / language / "accessibility-report"]
        for directory in directories:
            source = project_source(directory)
            for tool in required_tools:
                require(tool in source, f"{directory.relative_to(ROOT)} is missing canonical tool {tool}")
            require("browser_snapshot" not in source, f"{directory.relative_to(ROOT)} exposes browser_snapshot")
            require("browser_navigate" in source, f"{directory.relative_to(ROOT)} does not expose browser_navigate")
            require("read_latest_accessibility_snapshot" in source, f"{directory.relative_to(ROOT)} has no scoped snapshot reader")
            require(re.search(r"snapshot.*bytes", source, re.IGNORECASE) is not None,
                    f"{directory.relative_to(ROOT)} snapshot reader lacks a bounded no-path reader")
            exact_url_markers = {
                "dotnet": "UriComponents.PathAndQuery | UriComponents.Fragment",
                "nodejs": "function sameUrl",
                "python": "def _same_url",
                "go": "func sameURL",
                "rust": "fn same_url",
                "java": "boolean sameUrl",
            }
            require(exact_url_markers[language] in source, f"{directory.relative_to(ROOT)} does not compare target URL components exactly")


def validate_site_behavior() -> None:
    index = read(DOCS / "index.html")
    step = read(DOCS / "workshop" / "step.html")
    navigation = read(DOCS / "language-navigation.js")
    require(index.count('class="primary-action"') == 1, "Homepage must have exactly one primary action")
    require('option value="" selected' in index, "Homepage must not choose a default language")
    require('id="languagePicker"' in index and "homepage.js" in index, "Homepage is missing language selection behavior")
    require("language-navigation.js" in index and "language-navigation.js" in step, "Homepage and lessons must share language navigation")
    require("resolveLanguage" in navigation and "lessonUrl" in navigation and "firstLessonUrl" in navigation, "Language navigation must preserve URL propagation")
    require("localStorage" in read(DOCS / "homepage.js") and "localStorage" in step, "Homepage and lessons must persist language selection")
    require("Choose a workshop language" in step and "if (!language)" in step, "Lessons must not load without a valid language")
    require("preprocessLanguageDirectives" in step, "Lesson viewer must filter language directives")
    for hook in ("event.key === 'Escape'", "trapNavigationFocus", "toggleAttribute('inert'", "initializeTabs", 'id="lessonStatus"', 'id="progressTrack"'):
        require(hook in step, f"Lesson viewer is missing behavior hook: {hook}")
    for html_file in (DOCS / "index.html", DOCS / "workshop" / "step.html", DOCS / "target-app" / "index.html"):
        validate_html_assets(html_file)


def validate_documentation() -> None:
    for markdown in [ROOT / "README.md", ROOT / "start" / "README.md", ROOT / "checkpoints" / "README.md", *WORKSHOP.glob("*.md")]:
        validate_markdown_links(markdown)
    published = "\n".join(read(path) for path in [ROOT / "README.md", *WORKSHOP.glob("*.md"), *DOCS.rglob("*.html")])
    for forbidden in ("jamesmontemagno.github.io", "codemillmatt.github.io", "](../start/", "](../samples/"):
        require(forbidden not in published, f"Published content contains forbidden pattern: {forbidden}")
    for url in OFFICIAL_SDK_URLS.values():
        require(url in read(ROOT / "README.md"), f"README is missing official SDK link {url}")
    require("https://github.com/github/copilot-sdk/tree/main/cookbook" in read(ROOT / "README.md"), "README is missing the official cookbook link")


def validate_workflows() -> None:
    required_setup = (
        ("actions/setup-dotnet@v4", "dotnet-version: 10.0.x"),
        ("actions/setup-node@v4", "node-version: 22"),
        ("actions/setup-python@v5", 'python-version: "3.11"'),
        ("actions/setup-go@v5", 'go-version: "1.24.x"'),
        ("dtolnay/rust-toolchain@stable", 'toolchain: "1.94.0"'),
        ("actions/setup-java@v4", 'java-version: "17"'),
        ("mvn --version", "bash scripts/validate-workshop.sh"),
    )
    for workflow_name in ("validate.yml", "deploy.yml"):
        workflow = read(ROOT / ".github" / "workflows" / workflow_name)
        for expected in required_setup:
            for value in expected:
                require(value in workflow, f"{workflow_name} is missing required validation setup: {value}")


validate_language_registry()
for lesson in LESSONS:
    lesson_path = WORKSHOP / lesson
    require(lesson_path.exists(), f"Missing lesson {lesson}")
    if lesson_path.exists():
        validate_language_directives(lesson_path)
        for section in ("## Run it", "## Check your understanding"):
            if lesson.startswith("0") and lesson != "00-preflight.md":
                require(section in read(lesson_path), f"{lesson} is missing required section: {section}")
validate_layout()
validate_security_invariants()
validate_site_behavior()
validate_documentation()
validate_workflows()

if errors:
    print("Workshop validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"Workshop content validation passed: {len(LANGUAGES)} languages, {len(LESSONS)} lessons, {len(CHECKPOINTS)} checkpoints per language, and local site assets.")
