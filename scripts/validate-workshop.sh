#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

target="${1:-all}"

validate_content() {
    python3 scripts/validate_workshop.py
    node docs/tests/markdown-language-preprocessor.test.js
}

validate_dotnet() {
    mapfile -t projects < <(find start/dotnet samples/dotnet checkpoints/dotnet -name '*.csproj' -print | sort)
    projects+=("src/BlazorApp/BlazorApp.csproj")
    for project in "${projects[@]}"; do
        echo "Restoring and building $project"
        dotnet restore "$project" --nologo --verbosity quiet
        dotnet build "$project" --no-restore --nologo --verbosity quiet
    done
}

validate_nodejs() {
    for project in start/nodejs samples/nodejs/* checkpoints/nodejs/*; do
        echo "Installing and type-checking $project"
        (cd "$project" && npm ci --ignore-scripts --no-audit --fund=false && npm run build)
    done
}

validate_python() {
    for project in start/python samples/python/* checkpoints/python/*; do
        echo "Installing and smoke-checking $project"
        (
            cd "$project"
            python3 -m pip install --disable-pip-version-check --no-input --requirement requirements.txt
            python3 -m py_compile *.py
            python3 -c "import importlib, pathlib; [importlib.import_module(path.stem) for path in pathlib.Path('.').glob('*.py')]; from copilot import CopilotClient"
        )
    done
}

validate_go() {
    for project in start/go samples/go/* checkpoints/go/*; do
        echo "Resolving and testing $project"
        (cd "$project" && go mod download && go mod verify && go build -mod=readonly ./... && go test -mod=readonly ./...)
    done
}

validate_rust() {
    export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$repo_root/.cargo-target}"
    for project in start/rust samples/rust/* checkpoints/rust/*; do
        echo "Checking $project"
        (cd "$project" && cargo check --locked)
    done
}

validate_java() {
    for project in start/java samples/java/* checkpoints/java/*; do
        echo "Resolving and testing $project"
        (cd "$project" && mvn --batch-mode --no-transfer-progress dependency:go-offline)
        (cd "$project" && mvn --batch-mode --no-transfer-progress --offline test)
    done
}

case "$target" in
    content)
        validate_content
        ;;
    dotnet|nodejs|python|go|rust|java)
        "validate_${target}"
        ;;
    all)
        validate_content
        validate_dotnet
        validate_nodejs
        validate_python
        validate_go
        validate_rust
        validate_java
        ;;
    *)
        echo "Unknown validation target: $target" >&2
        echo "Expected one of: all, content, dotnet, nodejs, python, go, rust, java" >&2
        exit 2
        ;;
esac
