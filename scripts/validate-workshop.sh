#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 scripts/validate_workshop.py
node docs/tests/markdown-language-preprocessor.test.js

mapfile -t dotnet_projects < <(find start/dotnet samples/dotnet checkpoints/dotnet -name '*.csproj' -print | sort)
dotnet_projects+=("src/BlazorApp/BlazorApp.csproj")
for project in "${dotnet_projects[@]}"; do
    echo "Restoring and building $project"
    dotnet restore "$project" --nologo --verbosity quiet
    dotnet build "$project" --no-restore --nologo --verbosity quiet
done

for project in start/nodejs samples/nodejs/* checkpoints/nodejs/*; do
    echo "Installing and type-checking $project"
    (cd "$project" && npm ci --ignore-scripts --no-audit --fund=false && npm run build)
done

for project in start/python samples/python/* checkpoints/python/*; do
    echo "Syntax-checking $project"
    python3 -m py_compile "$project"/*.py
done

for project in start/go samples/go/* checkpoints/go/*; do
    echo "Resolving and testing $project"
    (cd "$project" && go mod download && go build ./... && go test ./...)
done

for project in start/rust samples/rust/* checkpoints/rust/*; do
    echo "Fetching and testing $project"
    (cd "$project" && cargo fetch --locked && cargo check --locked && cargo test --locked)
done

for project in start/java samples/java/* checkpoints/java/*; do
    echo "Resolving and testing $project"
    (cd "$project" && mvn --batch-mode --no-transfer-progress dependency:go-offline)
    (cd "$project" && mvn --batch-mode --no-transfer-progress --offline test)
done
