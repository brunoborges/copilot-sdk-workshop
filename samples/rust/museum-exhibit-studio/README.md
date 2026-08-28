# Museum Exhibit Studio

This Rust sample uses the GitHub Copilot SDK as a focused, non-software-engineering
agent harness. A museum educator can accept the Apollo 11 fixture or enter another
approved fact set, generate visitor-facing exhibit copy, and inspect deterministic
structural checks.

## Run the sample

From the repository root:

```bash
cargo run --manifest-path samples/rust/museum-exhibit-studio/Cargo.toml
```

Set `COPILOT_MODEL` to select a model. Otherwise, the Copilot runtime chooses its
default. The sample requires an authenticated GitHub Copilot CLI.

Run the mocked tests without contacting a model:

```bash
cargo test --locked --manifest-path samples/rust/museum-exhibit-studio/Cargo.toml
```

## What the sample teaches

`SYSTEM_MESSAGE` is the complete durable agent definition. Approved facts remain
in the separate user task prompt because they are task data, not reusable policy.
The session replaces the built-in system message, identifies itself as
`museum-exhibit-studio`, and exposes no tools.

The application limits input to 20 facts of at most 500 characters each, applies
a 120-second generation timeout, rejects an empty response, and disconnects the
session and stops the client on success or failure. Its validator checks for one
level-one title, the required sections, a 100–140-word narrative, exactly three
numbered questions ending in `?`, and prohibited software vocabulary.

The validator cannot prove semantic factual grounding. Generated claims still
require human review or a separate evaluator.
