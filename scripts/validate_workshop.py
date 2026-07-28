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
ENTRYPOINTS = {
    "dotnet": "Program.cs",
    "nodejs": "src/index.ts",
    "python": "main.py",
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


def executable_source(directory: Path, language: str) -> str:
    """Read the launched entrypoint and any directly launched report module, not dormant helpers."""
    entrypoint = directory / ENTRYPOINTS[language]
    text = read(entrypoint)
    if language == "nodejs" and re.search(r'import\s+["\']\./report\.js["\']', text):
        text += "\n" + read(directory / "src" / "report.ts") + "\n" + read(directory / "src" / "workshop.ts")
    if language == "python" and re.search(r"from\s+report\s+import\s+main", text):
        text += "\n" + read(directory / "report.py") + "\n" + read(directory / "workshop.py")
    if language == "dotnet" and "Prompts.CreateReportPrompt" in text:
        text += "\n" + read(directory / "Helpers" / "Prompts.cs")
    return text


def contains_any(text: str, markers: tuple[str, ...]) -> bool:
    folded = text.casefold()
    return any(marker.casefold() in folded for marker in markers)


LANGUAGE_APIS = {
    "dotnet": {
        "client": ("new CopilotClient",),
        "session": ("CreateSessionAsync",),
        "send": ("SendAndWaitAsync", "ResponseStreamer.SendAndPrintAsync"),
        "stream": ("Streaming = true",),
        "tool": ("CreateLookupTool",),
    },
    "nodejs": {
        "client": ("new CopilotClient",),
        "session": ("createSession",),
        "send": ("sendAndWait", "streamResponse"),
        "stream": ("streaming: true",),
        "tool": ("accessibilityRuleLookup", "tools: ["),
    },
    "python": {
        "client": ("CopilotClient",),
        "session": ("create_session",),
        "send": ("session.send",),
        "stream": ("streaming=True",),
        "tool": ("accessibility_rule_lookup", "tools=["),
    },
    "go": {
        "client": ("copilot.NewClient",),
        "session": ("CreateSession",),
        "send": ("SendAndWait",),
        "stream": ("Streaming: copilot.Bool(true)",),
        "tool": ('DefineTool("accessibility_rule_lookup"',),
    },
    "rust": {
        "client": ("Client::start",),
        "session": ("create_session",),
        "send": ("send_and_wait", "$session.send("),
        "stream": ("config.streaming = Some(true)",),
        "tool": ('Tool::new("accessibility_rule_lookup")',),
    },
    "java": {
        "client": ("new CopilotClient",),
        "session": ("createSession",),
        "send": ("sendAndWait",),
        "stream": ("setStreaming(true)",),
        "tool": ('ToolDefinition.from(', '"accessibility_rule_lookup"'),
    },
}


def contains_all(text: str, markers: tuple[str, ...]) -> bool:
    folded = text.casefold()
    return all(marker.casefold() in folded for marker in markers)


def runtime_source(directory: Path, language: str, text: str) -> str:
    """Include the directly imported Node response helper for runtime-flow validation."""
    if language == "nodejs" and re.search(r'from\s+["\']\./workshop\.js["\']', text):
        return text + "\n" + read(directory / "src" / "workshop.ts")
    return text


def validate_runtime_flow(language: str, stage: str, text: str, label: Path) -> None:
    """Require a visible response and a completion/error path, not just a send call."""
    streaming = stage != "01-first-session"

    if language == "dotnet":
        markers = (
            ("SendAndWaitAsync", 'Console.WriteLine($"\\nCopilot: {response.Data.Content}")', "await")
            if not streaming
            else ("await ResponseStreamer.SendAndPrintAsync",)
        )
        require(contains_all(text, markers),
                f"{label} does not print a completed Copilot response")
    elif language == "nodejs":
        markers = (
            ("const response = await session.sendAndWait", "console.log(response")
            if not streaming
            else ("await streamResponse(", "session.on(", "process.stdout.write", "session.error", "session.idle")
        )
        require(contains_all(text, markers),
                f"{label} does not print and complete the Copilot response")
    elif language == "python":
        markers = (
            ("AssistantMessageData", "print(content)", "SessionErrorData", "SessionIdleData",
             "await done.wait()", "if error is not None", "done.set()")
            if not streaming
            else ("AssistantMessageDeltaData", "print(delta", "SessionErrorData", "SessionIdleData",
                  "await done.wait()", "if error is not None", "done.set()")
        )
        require(contains_all(text, markers),
                f"{label} does not store and propagate session errors after printing output")
    elif language == "go":
        if streaming:
            event_output = contains_all(text, ("session.On(", "AssistantMessageDeltaData", "fmt.Print"))
            blocking_output = contains_all(text, ("AssistantMessageData", "fmt.Println(message.Content)"))
            require(event_output or blocking_output,
                    f"{label} does not print streamed or final assistant output")
        else:
            require(contains_all(text, ("AssistantMessageData", "fmt.Println(message.Content)")),
                    f"{label} does not print the final assistant response")
        require(contains_all(text, ("SendAndWait",)) and
                ("return err" in text or "if err != nil" in text),
                f"{label} does not wait for or propagate the send result")
    elif language == "rust":
        markers = (
            ("send_and_wait", 'message.data.get("content")', "println!")
            if not streaming
            else ("$session.send(", "session.subscribe", "assistant.message_delta", "assistant.message",
                  "session.error", "session.idle", "tokio::select!", "print!")
        )
        require(contains_all(text, markers),
                f"{label} does not subscribe, print, and await completion or errors")
    elif language == "java":
        require(contains_all(text, ("sendAndWait", "System.out.println(response)", ".get()")),
                f"{label} does not print a completed assistant response")


LATER_CAPABILITIES = {
    "stream": ("streaming", "Streaming", "setStreaming"),
    "local": ("accessibility_rule_lookup",),
    "mcp": ("mcpServers", "mcp_servers", "MCPServers", "McpStdioServerConfig", "McpServerConfig"),
    "browser": ("browser_navigate", "playwright-browser_navigate"),
    "snapshot": ("read_latest_accessibility_snapshot",),
    "permission": ("permissionForTarget", "permission_for_target", "OnPermissionRequest", "with_permission_handler", "setOnPermissionRequest"),
    "report": ("Review limits", "review limits", "reportPrompt", "report_prompt"),
}


def validate_executable_stage(language: str, stage: str, directory: Path) -> str:
    text = executable_source(directory, language)
    apis = LANGUAGE_APIS[language]
    label = directory.relative_to(ROOT)
    require("CHECKPOINT_STAGE" not in text and "checkpointStage" not in text,
            f"{label} relies on a cosmetic checkpoint label instead of executable behavior")

    if stage == "starter":
        for capability in ("client", "session", "stream", "local", "mcp", "browser", "snapshot", "permission", "report"):
            markers = apis.get(capability, ()) + LATER_CAPABILITIES.get(capability, ())
            require(not contains_any(text, markers),
                    f"{label} starter wires {capability} instead of remaining a scaffold")
        return text

    for capability in ("client", "session", "send"):
        require(contains_any(text, apis[capability]),
                f"{label} executable entrypoint does not create, use, and send through a Copilot session")

    required_capabilities = {
        "01-first-session": (),
        "02-streaming": ("stream",),
        "03-local-tool": ("stream", "local"),
        "04-mcp-safety": ("stream", "local", "mcp", "browser", "snapshot", "permission"),
        "05-combine-tools": ("stream", "local", "mcp", "browser", "snapshot", "permission"),
        "06-structured-report": ("stream", "local", "mcp", "browser", "snapshot", "permission", "report"),
    }[stage]
    for capability in required_capabilities:
        markers = apis.get(capability, ()) + LATER_CAPABILITIES.get(capability, ())
        require(contains_any(text, markers),
                f"{label} executable entrypoint does not wire {capability} for {stage}")

    validate_runtime_flow(language, stage, runtime_source(directory, language, text), label)
    if stage == "04-mcp-safety":
        require("evidence-backed" not in text and "Review limits" not in text,
                f"{label} combines report behavior before Step 5 or Step 6")
    if stage == "05-combine-tools":
        combined_marker = {
            "dotnet": "For each issue, call accessibility_rule_lookup",
            "nodejs": "evidence-backed",
            "python": "evidence-backed",
            "go": "evidence-backed",
            "rust": "evidence-backed",
            "java": "evidence-backed",
        }[language]
        require(combined_marker in text and "Review limits" not in text,
                f"{label} does not combine browser evidence with local guidance before Step 6")
    if stage == "06-structured-report":
        require("Review limits" in text,
                f"{label} executable entrypoint does not request the structured report limits")

    forbidden_capabilities = {
        "01-first-session": ("stream", "local", "mcp", "browser", "snapshot", "permission", "report"),
        "02-streaming": ("local", "mcp", "browser", "snapshot", "permission", "report"),
        "03-local-tool": ("mcp", "browser", "snapshot", "permission", "report"),
    }.get(stage, ())
    for capability in forbidden_capabilities:
        markers = apis.get(capability, ()) + LATER_CAPABILITIES.get(capability, ())
        require(not contains_any(text, markers),
                f"{label} executable entrypoint wires later-stage {capability} capability")

    if language == "nodejs" and stage in {"04-mcp-safety", "05-combine-tools"}:
        require('["http:", "https:"].includes(target.protocol)' in text,
                f"{label} accepts a non-HTTP(S) URL")
    return text


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
            require((directory / ENTRYPOINTS[language]).exists(),
                    f"Missing {language} executable entrypoint in {directory.relative_to(ROOT)}")
        for checkpoint in CHECKPOINTS:
            directory = ROOT / "checkpoints" / language / checkpoint
            require(directory.is_dir(), f"Missing {language} checkpoint {checkpoint}")
            require(has_manifest(directory, language), f"Missing {language} manifest in {directory.relative_to(ROOT)}")
            require((directory / SOURCE_FILES[language]).exists(), f"Missing {language} source in {directory.relative_to(ROOT)}")
            require((directory / ENTRYPOINTS[language]).exists(),
                    f"Missing {language} executable entrypoint in {directory.relative_to(ROOT)}")
    for language in ("nodejs", "go", "rust"):
        for directory in [ROOT / "start" / language, *(ROOT / "samples" / language / sample for sample in ("hello-copilot-sdk", "accessibility-report")), *(ROOT / "checkpoints" / language / checkpoint for checkpoint in CHECKPOINTS)]:
            lock = {"nodejs": "package-lock.json", "go": "go.sum", "rust": "Cargo.lock"}[language]
            require((directory / lock).exists(), f"Missing deterministic {language} lock file in {directory.relative_to(ROOT)}")


def validate_python_dependencies() -> None:
    directories = [
        ROOT / "start" / "python",
        *(ROOT / "samples" / "python" / sample for sample in ("hello-copilot-sdk", "accessibility-report")),
        *(ROOT / "checkpoints" / "python" / checkpoint for checkpoint in CHECKPOINTS),
    ]
    for directory in directories:
        requirements = [
            line.strip() for line in read(directory / "requirements.txt").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        require(requirements, f"{directory.relative_to(ROOT)} has no pinned Python dependencies")
        for requirement in requirements:
            require("==" in requirement and not requirement.startswith(("-", "git+", "http:")),
                    f"{directory.relative_to(ROOT)} has an unpinned Python dependency: {requirement}")
        require(any(requirement.startswith("github-copilot-sdk==") for requirement in requirements),
                f"{directory.relative_to(ROOT)} does not pin github-copilot-sdk")


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


def validate_checkpoint_progression() -> None:
    for language in LANGUAGES:
        executable_hashes: set[str] = set()
        starter = ROOT / "start" / language
        require((starter / ENTRYPOINTS[language]).exists(),
                f"Missing {language} starter executable {ENTRYPOINTS[language]}")
        validate_executable_stage(language, "starter", starter)
        for checkpoint in CHECKPOINTS:
            directory = ROOT / "checkpoints" / language / checkpoint
            text = validate_executable_stage(language, checkpoint, directory)
            executable_hashes.add(text)
            if language == "nodejs":
                package = read(directory / "package.json")
                require('"start": "tsx src/index.ts"' in package, f"{directory.relative_to(ROOT)} start script bypasses its checkpoint entrypoint")
                require("Continue with Step 1" not in text, f"{directory.relative_to(ROOT)} has a placeholder entrypoint")
            if language == "python":
                if checkpoint == "06-structured-report":
                    report = read(directory / "report.py")
                    require("case SessionErrorData(message=message): raise" not in report,
                            f"{directory.relative_to(ROOT)} raises from an event callback instead of completing the wait")
                    require("error: RuntimeError | None = None" in report and "done.set()" in report,
                            f"{directory.relative_to(ROOT)} does not propagate session errors to the awaited flow")
                    require('if __name__ == "__main__":' in report,
                            f"{directory.relative_to(ROOT)} runs interactive code when imported")
                else:
                    require(not (directory / "report.py").exists(),
                            f"{directory.relative_to(ROOT)} includes a misleading completed reporter before Step 6")
            if language == "java":
                pom = read(directory / "pom.xml")
                require("<mainClass>workshop.AccessibilityReport</mainClass>" in pom,
                        f"{directory.relative_to(ROOT)} does not configure mvn exec:java")
        require(
            len(executable_hashes) == len(CHECKPOINTS),
            f"{language} checkpoints have identical executable behavior; each checkpoint must demonstrate its named stage",
        )

    for language, stage, directory in (
        ("nodejs", "01-first-session", ROOT / "samples" / "nodejs" / "hello-copilot-sdk"),
        ("go", "06-structured-report", ROOT / "samples" / "go" / "accessibility-report"),
        ("rust", "06-structured-report", ROOT / "samples" / "rust" / "accessibility-report"),
        ("java", "06-structured-report", ROOT / "samples" / "java" / "accessibility-report"),
    ):
        text = executable_source(directory, language)
        validate_runtime_flow(language, stage, runtime_source(directory, language, text), directory.relative_to(ROOT))
    for directory in (
        ROOT / "samples" / "python" / "hello-copilot-sdk",
        ROOT / "samples" / "python" / "accessibility-report",
    ):
        validate_runtime_flow(
            "python",
            "06-structured-report",
            read(directory / "report.py"),
            directory.relative_to(ROOT),
        )

    node_report_package = read(ROOT / "samples" / "nodejs" / "accessibility-report" / "package.json")
    require('"start": "tsx src/report.ts"' in node_report_package,
            "Node accessibility-report npm start must execute src/report.ts")
    for directory in [ROOT / "start" / "nodejs", *(ROOT / "checkpoints" / "nodejs" / checkpoint for checkpoint in CHECKPOINTS), *(ROOT / "samples" / "nodejs" / sample for sample in ("hello-copilot-sdk", "accessibility-report"))]:
        source = read(directory / "src" / "workshop.ts")
        require("const existingSnapshots = safeSnapshotNames(outputDirectory)" in source,
                f"{directory.relative_to(ROOT)} captures snapshot baseline lazily")
        require("const baseline = await existingSnapshots" in source,
                f"{directory.relative_to(ROOT)} does not await the construction-time snapshot baseline")
    for directory in [ROOT / "start" / "python", *(ROOT / "checkpoints" / "python" / checkpoint for checkpoint in CHECKPOINTS), *(ROOT / "samples" / "python" / sample for sample in ("hello-copilot-sdk", "accessibility-report"))]:
        report_path = directory / "report.py"
        if report_path.exists():
            require('if __name__ == "__main__":' in read(report_path),
                    f"{directory.relative_to(ROOT)} report entrypoint cannot be imported safely")
    for directory in [ROOT / "start" / "java", *(ROOT / "checkpoints" / "java" / checkpoint for checkpoint in CHECKPOINTS), *(ROOT / "samples" / "java" / sample for sample in ("hello-copilot-sdk", "accessibility-report"))]:
        require("<mainClass>workshop.AccessibilityReport</mainClass>" in read(directory / "pom.xml"),
                f"{directory.relative_to(ROOT)} does not configure the Maven executable entrypoint")


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
    all_markdown = "\n".join(read(path) for path in [ROOT / "README.md", ROOT / "start" / "README.md", ROOT / "checkpoints" / "README.md", *WORKSHOP.glob("*.md")])
    require("go run ./samples/" not in all_markdown and "go run samples/" not in all_markdown,
            "Documentation runs Go modules from the repository root instead of their module directory")
    starters = read(ROOT / "start" / "README.md")
    require("cd workshop-app && go build -mod=readonly ./..." in starters,
            "Starter documentation must build Go modules with the lock enforced")
    checkpoints = read(ROOT / "checkpoints" / "README.md")
    require("go test -mod=readonly ./..." in checkpoints,
            "Checkpoint documentation must test Go modules with the lock enforced")
    require("python -m pip install -r requirements.txt" in starters,
            "Starter documentation must install the pinned Python requirements")
    require("python report.py" not in all_markdown,
            "Documentation must invoke Python checkpoint main.py rather than an unwired report.py")
    for lesson in ("01-first-session.md", "05-combine-tools.md", "06-structured-report.md"):
        require("python main.py" in read(WORKSHOP / lesson),
                f"{lesson} must run the Python checkpoint through main.py")


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
validate_python_dependencies()
validate_security_invariants()
validate_checkpoint_progression()
validate_site_behavior()
validate_documentation()
validate_workflows()

if errors:
    print("Workshop validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"Workshop content validation passed: {len(LANGUAGES)} languages, {len(LESSONS)} lessons, {len(CHECKPOINTS)} checkpoints per language, and local site assets.")
