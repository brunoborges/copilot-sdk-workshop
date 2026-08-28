# Museum Exhibit Studio

This Python sample uses the GitHub Copilot SDK as a focused, non-software-engineering
agent harness. A museum educator can accept the Apollo 11 fixture or enter another
approved fact set, then generate visitor-facing copy and inspect deterministic checks.

## Run the sample

From this directory, create an environment and install the pinned dependency:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Set `COPILOT_MODEL` to select a model; otherwise the runtime chooses its default. An
authenticated GitHub Copilot CLI is required.

Run the mocked tests without contacting a model:

```bash
python -m unittest discover -s tests -v
```

## What the sample teaches

`SYSTEM_MESSAGE` is the complete durable curator definition and uses replace mode.
Approved facts remain in the separate user prompt because they are task data. Hard
controls expose no tools, bound facts to 20 items of 500 characters each, enforce a
120-second timeout, and disconnect the session and stop the client on every outcome.
The validator checks one H1, required sections, a 100-140-word narrative, exactly
three numbered questions ending in `?`, and prohibited software vocabulary.

Prompt guidance and structural validation are not authorization or grounding
boundaries. Generated claims still require human review or a separate evaluator.

## Manual check

1. Run with the default Apollo 11 facts.
2. Confirm one title, a 100-140-word narrative, and three questions.
3. Inspect the validation summary and grounding disclaimer.
4. Review the prose for claims absent from the approved facts.
5. Confirm no tool events or permission requests appear.
