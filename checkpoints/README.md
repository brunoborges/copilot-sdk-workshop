# Workshop checkpoints

Each language track contains the compiling state after core Steps 1 through 6. The completed
applications are in `samples/<language>/hello-copilot-sdk` and
`samples/<language>/accessibility-report`.

Run the repository-wide deterministic validation from the root:

```bash
bash scripts/validate-workshop.sh
```

It validates all six language registries, lessons, local assets, security boundaries, starters,
six checkpoints per language, and both samples per language. For a single checkpoint, use its
native command: `dotnet build`, `npm ci && npm run build`, `python -m py_compile *.py`,
`go test -mod=readonly ./...`, `cargo test --locked`, or `mvn test`.

The static validation intentionally does not authenticate the Copilot CLI, launch a browser, or
send a Copilot request. Runtime setup is covered by the language-specific interactive preflight.
