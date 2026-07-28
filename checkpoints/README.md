# Workshop checkpoints

Each language track directory captures the complete, compiling state of `workshop-app` after the
matching core step. .NET, Node.js/TypeScript, Python, Go, Rust, and Maven Java all provide
checkpoints 01 through 06.

From the repository root, build every checkpoint with:

```bash
for project in checkpoints/dotnet/*/*.csproj; do dotnet build "$project"; done
```

You can also find the finished application in
[`samples/dotnet/accessibility-report`](../samples/dotnet/accessibility-report).
Equivalent completed projects are in `samples/nodejs/accessibility-report` and
`samples/python/accessibility-report`, `samples/go/accessibility-report`,
`samples/rust/accessibility-report`, and `samples/java/accessibility-report`.

```bash
for project in checkpoints/go/*; do (cd "$project" && go build ./...); done
for project in checkpoints/rust/*; do (cd "$project" && cargo check --locked); done
for project in checkpoints/java/*; do (cd "$project" && mvn compile); done
```
