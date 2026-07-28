# Workshop checkpoints

Each language track directory captures the complete, compiling state of `workshop-app` after the
matching core step. .NET, Node.js/TypeScript, and Python all provide checkpoints 01 through 06.

From the repository root, build every checkpoint with:

```bash
for project in checkpoints/dotnet/*/*.csproj; do dotnet build "$project"; done
```

You can also find the finished application in
[`samples/dotnet/accessibility-report`](../samples/dotnet/accessibility-report).
Equivalent completed projects are in `samples/nodejs/accessibility-report` and
`samples/python/accessibility-report`.
