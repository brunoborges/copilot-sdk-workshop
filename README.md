# Copilot SDK Workshop

Build an AI-powered accessibility reviewer with .NET, Node.js/TypeScript, Python, Go, Rust, or Maven Java and the GitHub Copilot SDK.

In this self-guided workshop, you'll:

1. Create a Copilot client and conversation session.
2. Stream responses through session events.
3. Expose application-owned Web Content Accessibility Guidelines (WCAG) data as a local tool.
4. Connect Playwright MCP through a scoped permission boundary.
5. Combine browser evidence and catalog guidance in a structured report.
6. Explain the ownership, process, and trust boundaries in the completed application.

Plan on about 90 minutes for the seven core steps. Machine setup happens separately in an untimed
preflight.

## Start the workshop

Open the GitHub Pages URL produced by the repository's **Deploy to GitHub Pages** workflow, then
select **Start workshop**. The site derives its Pages base URL at runtime, so there is no hardcoded
organization or user Pages hostname.

To preview the site from a clone:

```bash
git clone https://github.com/jamesmontemagno/copilot-sdk-workshop.git
cd copilot-sdk-workshop
python3 -m http.server 8000
```

Open <http://localhost:8000/docs/>. Do not open `step.html` with a `file://` URL; browsers block
the Markdown requests used by the lesson viewer.

## Prerequisites

- [.NET 10 SDK](https://learn.microsoft.com/dotnet/core/install/)
- [Node.js 22 or newer](https://nodejs.org/)
- [Python 3.11 or newer](https://www.python.org/downloads/)
- [Go 1.24 or newer](https://go.dev/dl/)
- [Rust 1.94 or newer](https://rustup.rs/)
- [Java 17 or newer](https://adoptium.net/) and [Maven](https://maven.apache.org/install.html)
- [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)
- GitHub Copilot subscription or trial
- Microsoft Edge (the workshop default) or Google Chrome

Preflight walks through installation checks, authentication, OS-specific commands, expected
output, and troubleshooting.

## Repository layout

```text
copilot-sdk-workshop/
|-- docs/                         GitHub Pages site and controlled target page
|-- workshop/                     Preflight, seven core lessons, optional extension
|-- start/dotnet/                 .NET learner starter with WCAG data and permission helper
|-- checkpoints/dotnet/           .NET compiling state after each build step
|-- samples/dotnet/
|   |-- hello-copilot-sdk/        Completed local-tool example in every language
|   `-- accessibility-report/     Completed .NET local + MCP reporter
|-- start/nodejs/                 Node.js/TypeScript learner starter
|-- checkpoints/nodejs/           Node.js/TypeScript checkpoint projects
|-- samples/nodejs/               Completed TypeScript examples
|-- start/python/                 Python 3.11+ learner starter
|-- checkpoints/python/           Python checkpoint projects
|-- samples/python/               Completed Python examples
|-- start/go/                     Go 1.24+ learner starter
|-- checkpoints/go/               Go checkpoint projects
|-- samples/go/                   Completed Go examples
|-- start/rust/                   Rust 1.94+ learner starter
|-- checkpoints/rust/             Rust checkpoint projects
|-- samples/rust/                 Completed Rust examples
|-- start/java/                   Maven Java 17+ learner starter
|-- checkpoints/java/             Maven Java checkpoint projects
|-- samples/java/                 Completed Maven Java examples
|-- src/BlazorApp/                Source counterpart of the deployed target
|-- scripts/                      Deterministic content and build validation
`-- .github/workflows/            Validation and Pages deployment
```

## Validate a change

```bash
bash scripts/validate-workshop.sh
```

The command checks lesson structure, internal links, site behavior hooks, and checkpoint coverage.
It then runs browser-independent language-selection tests and restores, builds, or syntax-checks every
starter, every checkpoint, both samples, and the Blazor target without authenticating Copilot, launching
a browser, or sending a prompt.

Pass a language ID to run one smoke-build target:

```bash
bash scripts/validate-workshop.sh nodejs
```

Pull requests run content validation and all six language smoke builds as separate GitHub Actions
jobs, so a failure identifies the affected SDK track.

Rust checks share one Cargo target directory across all workshop projects, avoiding repeated SDK
dependency compilation.

## Deployment

After validation passes, push to `main`. The
[Pages workflow](.github/workflows/deploy.yml) publishes `docs/` plus the Markdown lessons in
`workshop/`. Build and content validation run separately in the validation workflow.

Enable GitHub Pages in repository settings and choose **GitHub Actions** as the source. The
deployment job reports the canonical workshop URL in its environment.

## References

- [GitHub Copilot SDK for .NET](https://github.com/github/copilot-sdk/tree/main/dotnet)
- [GitHub Copilot SDK for Node.js/TypeScript](https://github.com/github/copilot-sdk/tree/main/nodejs)
- [GitHub Copilot SDK for Python](https://github.com/github/copilot-sdk/tree/main/python)
- [GitHub Copilot SDK for Go](https://github.com/github/copilot-sdk/tree/main/go)
- [GitHub Copilot SDK for Rust](https://github.com/github/copilot-sdk/tree/main/rust)
- [GitHub Copilot SDK for Java](https://github.com/github/copilot-sdk/tree/main/java)
- [Copilot SDK cookbook](https://github.com/github/copilot-sdk/tree/main/cookbook)
- [Copilot SDK API and source](https://github.com/github/copilot-sdk)
- [Install the GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

This workshop is provided as-is for educational purposes.
