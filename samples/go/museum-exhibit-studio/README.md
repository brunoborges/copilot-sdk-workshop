# Museum Exhibit Studio

This Go sample uses the GitHub Copilot SDK as a focused, non-software-engineering agent harness. A
museum educator can accept the Apollo 11 fixture or enter another approved fact set, generate
visitor-facing exhibit copy, and inspect deterministic structural checks.

## Run the sample

From this directory:

```bash
go run .
```

Set `COPILOT_MODEL` to select a model; otherwise the runtime chooses its default. An authenticated
GitHub Copilot CLI is required.

Tests use fakes and never contact a model:

```bash
go test -mod=readonly ./...
```

## What the sample teaches

The complete curator system message replaces the SDK default, while approved facts remain in the
separate task prompt. The session exposes no tools, bounds facts to 20 entries of 500 characters,
and limits generation to 120 seconds. Every path disconnects an established session and stops the
client. A deterministic validator checks one H1, required sections, a 100-140-word narrative, three
numbered questions ending in `?`, and prohibited software terms.

Prompt guidance is not an authorization boundary, and structural validation cannot prove factual
grounding. Generated claims still require human review or a separate evaluator.
