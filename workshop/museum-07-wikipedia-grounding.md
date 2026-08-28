# Optional: Add Wikipedia grounding

> **Time:** 15 minutes  
> **Goal:** Design a reviewed research stage without weakening the tool-free core.

## Keep research separate

Do not quietly give the curator open-ended browsing. Add research as a visible stage before
generation, with only read-only Wikipedia search and article retrieval tools.

The flow should:

1. Mark each supplied fact as `supported`, `contradicted`, `not found`, or `not checked`.
2. Show proposed additions with article title and URL.
3. Require explicit approval before an addition enters the exhibit prompt.
4. Generate from the original facts plus approved additions.
5. Display consulted sources separately from the exhibit.

Choose one server implementation for your environment, discover its effective tool names, and
allowlist only search and article retrieval. Do not assume package names imply stable tool names.

## Treat retrieved text as untrusted

Ignore instructions embedded in article content. Bound result count and article size, apply startup
and call timeouts, and never invent citations. If research fails, continue with the original facts
and state that external validation was not completed.

:::language dotnet
Add an MCP server configuration and permission handler beside the session setup in
`MuseumExhibitService.cs`.
:::
:::language nodejs
Add the MCP server configuration and permission handler in `src/service.ts`.
:::
:::language python
Add the MCP server configuration and permission handler in `museum_exhibit_service.py`.
:::
:::language go
Add the MCP server configuration and permission handler in `service.go`.
:::
:::language rust
Add the MCP server configuration and permission handler in `src/lib.rs`.
:::
:::language java
Add the MCP server configuration and permission handler in `MuseumExhibitService.java`.
:::

## Run it

Test the extension with a mock MCP server, not live Wikipedia. Cover supported, contradicted, timeout,
and user-rejected addition paths. Re-run the base suite to prove the original tool-free mode remains
available.

:::language dotnet
```bash
dotnet test museum-workshop-app/tests/museum-exhibit-studio.Tests.csproj
```
:::
:::language nodejs
```bash
npm --prefix museum-workshop-app test
```
:::
:::language python
```bash
PYTHONPATH=museum-workshop-app museum-workshop-app/.venv/bin/python -m unittest discover -s museum-workshop-app/tests
```
:::
:::language go
```bash
go -C museum-workshop-app test ./...
```
:::
:::language rust
```bash
cargo test --manifest-path museum-workshop-app/Cargo.toml --locked
```
:::
:::language java
```bash
mvn -f museum-workshop-app/pom.xml test
```
:::

## Check your understanding

1. Why must proposed facts require explicit approval?
2. How does the permission handler constrain the research surface?
3. What should the app report when Wikipedia is unavailable?
