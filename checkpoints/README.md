# Workshop checkpoints

Each directory is the complete, compiling state of `workshop-app` after the matching core step.
The first three projects link unchanged starter helpers so the checkpoint shows only the code introduced
so far; later checkpoints contain every source file directly.

Build all checkpoints from the repository root:

```bash
for project in checkpoints/*/*.csproj; do dotnet build "$project"; done
```

The final application is also available in
[`samples/accessibility-report`](../samples/accessibility-report).
