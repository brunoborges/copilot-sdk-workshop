#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 scripts/validate_workshop.py

projects=(
    "start/HelloCopilotSDK/HelloCopilotSDK.csproj"
    "samples/hello-copilot-sdk/hello-copilot-sdk.csproj"
    "samples/accessibility-report/accessibility-report.csproj"
    "src/BlazorApp/BlazorApp.csproj"
)

while IFS= read -r project; do
    projects+=("$project")
done < <(find checkpoints -mindepth 2 -maxdepth 2 -name '*.csproj' -print | sort)

for project in "${projects[@]}"; do
    echo "Building $project"
    dotnet build "$project" --nologo --verbosity quiet
done
