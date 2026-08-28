# Ground the exhibit in approved facts

> **Time:** 20 minutes  
> **Goal:** Add a bounded prompt builder and execute its boundary tests.

The builder accepts 1-20 nonblank facts, trims whitespace, and rejects facts over 500 characters.
It never truncates source material. The returned prompt requests exactly:

```text
# <an engaging exhibit title>
## Narrative
<100-140 words, excluding the title and questions>
## Visitor questions
1. <question>
2. <question>
3. <question>
```

Validation belongs before client startup: invalid educator input must not consume an SDK session.

:::language dotnet
Add this method inside `CuratorPrompts` in `museum-workshop-app/CuratorPrompts.cs`:

```csharp
public static string BuildExhibitPrompt(IEnumerable<string> approvedFacts)
{
    ArgumentNullException.ThrowIfNull(approvedFacts);

    var facts = approvedFacts
        .Select(fact => fact?.Trim())
        .Where(fact => !string.IsNullOrWhiteSpace(fact))
        .Cast<string>()
        .ToArray();

    if (facts.Length == 0)
        throw new ArgumentException("Provide at least one approved fact.", nameof(approvedFacts));
    if (facts.Length > MaximumFactCount)
        throw new ArgumentException(
            $"Provide no more than {MaximumFactCount} approved facts.", nameof(approvedFacts));
    if (facts.Any(fact => fact.Length > MaximumFactLength))
        throw new ArgumentException(
            $"Each approved fact must be {MaximumFactLength} characters or fewer.",
            nameof(approvedFacts));

    var factList = string.Join(Environment.NewLine, facts.Select(fact => $"- {fact}"));
    return $"""
        Create visitor-facing exhibit text about Apollo 11 using only these supplied facts:

        {factList}

        Return exactly this structure:

        # <an engaging exhibit title>
        ## Narrative
        <100-140 words, excluding the title and questions>
        ## Visitor questions
        1. <question>
        2. <question>
        3. <question>

        Write exactly three distinct visitor reflection questions. Do not add a preface,
        conclusion, software discussion, or facts not supplied above. Do not inspect the
        filesystem or use tools.
        """;
}
```

Create `museum-workshop-app/tests/GlobalUsings.cs` containing `global using Xunit;`, then create
`museum-workshop-app/tests/CuratorPromptsTests.cs`:

```csharp
using MuseumExhibitStudio;

namespace MuseumExhibitStudio.Tests;

public sealed class CuratorPromptsTests
{
    [Fact]
    public void PromptIncludesContractAndFacts()
    {
        var prompt = CuratorPrompts.BuildExhibitPrompt(CuratorPrompts.Apollo11Facts);
        Assert.All(CuratorPrompts.Apollo11Facts, fact => Assert.Contains(fact, prompt));
        Assert.Contains("# <an engaging exhibit title>", prompt);
        Assert.Contains("## Narrative", prompt);
        Assert.Contains("## Visitor questions", prompt);
    }

    [Fact]
    public void RejectsBoundaryViolations()
    {
        Assert.Throws<ArgumentException>(() => CuratorPrompts.BuildExhibitPrompt([]));
        Assert.Throws<ArgumentException>(() => CuratorPrompts.BuildExhibitPrompt(
            Enumerable.Repeat("fact", CuratorPrompts.MaximumFactCount + 1)));
        Assert.Throws<ArgumentException>(() => CuratorPrompts.BuildExhibitPrompt(
            [new string('a', CuratorPrompts.MaximumFactLength + 1)]));
    }
}
```
:::

:::language nodejs
Append this function to `museum-workshop-app/src/prompts.ts`:

```typescript
export function buildExhibitPrompt(approvedFacts: Iterable<string>): string {
  const facts = [...approvedFacts].map((fact) => fact.trim()).filter(Boolean);
  if (facts.length === 0) throw new Error("Provide at least one approved fact.");
  if (facts.length > maximumFactCount) {
    throw new Error(`Provide no more than ${maximumFactCount} approved facts.`);
  }
  if (facts.some((fact) => fact.length > maximumFactLength)) {
    throw new Error(`Each approved fact must be ${maximumFactLength} characters or fewer.`);
  }

  return `Create visitor-facing exhibit text about Apollo 11 using only these supplied facts:

${facts.map((fact) => `- ${fact}`).join("\n")}

Return exactly this structure:

# <an engaging exhibit title>
## Narrative
<100-140 words, excluding the title and questions>
## Visitor questions
1. <question>
2. <question>
3. <question>

Write exactly three distinct visitor reflection questions. Do not add a preface,
conclusion, software discussion, or facts not supplied above. Do not inspect the
filesystem or use tools.`;
}
```

Create `museum-workshop-app/tests/prompts.test.ts`:

```typescript
import assert from "node:assert/strict";
import test from "node:test";
import {
  apollo11Facts, buildExhibitPrompt, maximumFactCount, maximumFactLength,
} from "../src/prompts.js";

test("builds the exact shape from approved facts", () => {
  const prompt = buildExhibitPrompt(apollo11Facts);
  apollo11Facts.forEach((fact) => assert.ok(prompt.includes(fact)));
  assert.ok(prompt.includes("# <an engaging exhibit title>\n## Narrative"));
  assert.ok(prompt.includes("## Visitor questions\n1. <question>"));
});

test("rejects input outside the bounds", () => {
  assert.throws(() => buildExhibitPrompt([]), /at least one/);
  assert.throws(() => buildExhibitPrompt(Array(maximumFactCount + 1).fill("fact")), /20/);
  assert.throws(() => buildExhibitPrompt(["a".repeat(maximumFactLength + 1)]), /500/);
});
```
:::

:::language python
Add `from collections.abc import Iterable` at the top of
`museum-workshop-app/curator_prompts.py`, then append:

```python
def build_exhibit_prompt(approved_facts: Iterable[str]) -> str:
    facts = tuple(fact.strip() for fact in approved_facts if fact and fact.strip())
    if not facts:
        raise ValueError("Provide at least one approved fact.")
    if len(facts) > MAXIMUM_FACT_COUNT:
        raise ValueError(f"Provide no more than {MAXIMUM_FACT_COUNT} approved facts.")
    if any(len(fact) > MAXIMUM_FACT_LENGTH for fact in facts):
        raise ValueError(
            f"Each approved fact must be {MAXIMUM_FACT_LENGTH} characters or fewer."
        )

    fact_list = "\n".join(f"- {fact}" for fact in facts)
    return f"""Create visitor-facing exhibit text about Apollo 11 using only these supplied facts:

{fact_list}

Return exactly this structure:

# <an engaging exhibit title>
## Narrative
<100-140 words, excluding the title and questions>
## Visitor questions
1. <question>
2. <question>
3. <question>

Write exactly three distinct visitor reflection questions. Do not add a preface,
conclusion, software discussion, or facts not supplied above. Do not inspect the
filesystem or use tools."""
```

Create `museum-workshop-app/tests/test_curator_prompts.py`:

```python
import unittest
from curator_prompts import (
    APOLLO_11_FACTS, MAXIMUM_FACT_COUNT, MAXIMUM_FACT_LENGTH, build_exhibit_prompt,
)

class CuratorPromptsTests(unittest.TestCase):
    def test_shape_and_bounds(self) -> None:
        prompt = build_exhibit_prompt(APOLLO_11_FACTS)
        self.assertIn("# <an engaging exhibit title>\n## Narrative", prompt)
        self.assertIn("## Visitor questions\n1. <question>", prompt)
        with self.assertRaises(ValueError):
            build_exhibit_prompt([])
        with self.assertRaises(ValueError):
            build_exhibit_prompt(["fact"] * (MAXIMUM_FACT_COUNT + 1))
        with self.assertRaises(ValueError):
            build_exhibit_prompt(["a" * (MAXIMUM_FACT_LENGTH + 1)])

if __name__ == "__main__":
    unittest.main()
```
:::

:::language go
Add this import block after `package main` in `museum-workshop-app/prompts.go`, then append the
function:

```go
import (
	"fmt"
	"strings"
)

func buildExhibitPrompt(approvedFacts []string) (string, error) {
	facts := make([]string, 0, len(approvedFacts))
	for _, fact := range approvedFacts {
		if fact = strings.TrimSpace(fact); fact != "" {
			facts = append(facts, fact)
		}
	}
	if len(facts) == 0 {
		return "", fmt.Errorf("provide at least one approved fact")
	}
	if len(facts) > maximumFactCount {
		return "", fmt.Errorf("provide no more than %d approved facts", maximumFactCount)
	}
	for _, fact := range facts {
		if len([]rune(fact)) > maximumFactLength {
			return "", fmt.Errorf(
				"each approved fact must be %d characters or fewer", maximumFactLength)
		}
	}

	var factList strings.Builder
	for _, fact := range facts {
		fmt.Fprintf(&factList, "- %s\n", fact)
	}
	return fmt.Sprintf(`Create visitor-facing exhibit text about Apollo 11 using only these supplied facts:

%s
Return exactly this structure:

# <an engaging exhibit title>
## Narrative
<100-140 words, excluding the title and questions>
## Visitor questions
1. <question>
2. <question>
3. <question>

Write exactly three distinct visitor reflection questions. Do not add a preface,
conclusion, software discussion, or facts not supplied above. Do not inspect the
filesystem or use tools.`, factList.String()), nil
}
```

Create `museum-workshop-app/prompts_test.go`:

```go
package main

import (
	"strings"
	"testing"
)

func TestBuildExhibitPromptBounds(t *testing.T) {
	prompt, err := buildExhibitPrompt(apollo11Facts)
	if err != nil || !strings.Contains(prompt, "## Visitor questions\n1. <question>") {
		t.Fatalf("prompt = %q, error = %v", prompt, err)
	}
	if _, err = buildExhibitPrompt(nil); err == nil {
		t.Fatal("empty facts must fail")
	}
	tooManyFacts := make([]string, maximumFactCount+1)
	for index := range tooManyFacts {
		tooManyFacts[index] = "fact"
	}
	if _, err = buildExhibitPrompt(tooManyFacts); err == nil {
		t.Fatal("21 facts must fail")
	}
	if _, err = buildExhibitPrompt([]string{strings.Repeat("a", 501)}); err == nil {
		t.Fatal("501-character fact must fail")
	}
}
```
:::

:::language rust
Add `use std::fmt;` with the other imports in `museum-workshop-app/src/lib.rs`, then append:

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PromptError(String);

impl fmt::Display for PromptError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.0)
    }
}

impl Error for PromptError {}

pub fn build_exhibit_prompt<I, S>(approved_facts: I) -> Result<String, PromptError>
where
    I: IntoIterator<Item = S>,
    S: AsRef<str>,
{
    let facts: Vec<String> = approved_facts.into_iter()
        .map(|fact| fact.as_ref().trim().to_owned())
        .filter(|fact| !fact.is_empty()).collect();
    if facts.is_empty() {
        return Err(PromptError("Provide at least one approved fact.".to_owned()));
    }
    if facts.len() > MAXIMUM_FACT_COUNT {
        return Err(PromptError(format!(
            "Provide no more than {MAXIMUM_FACT_COUNT} approved facts.")));
    }
    if facts.iter().any(|fact| fact.chars().count() > MAXIMUM_FACT_LENGTH) {
        return Err(PromptError(format!(
            "Each approved fact must be {MAXIMUM_FACT_LENGTH} characters or fewer.")));
    }

    let fact_list = facts.iter().map(|fact| format!("- {fact}"))
        .collect::<Vec<_>>().join("\n");
    Ok(format!(r#"Create visitor-facing exhibit text about Apollo 11 using only these supplied facts:

{fact_list}

Return exactly this structure:

# <an engaging exhibit title>
## Narrative
<100-140 words, excluding the title and questions>
## Visitor questions
1. <question>
2. <question>
3. <question>

Write exactly three distinct visitor reflection questions. Do not add a preface,
conclusion, software discussion, or facts not supplied above. Do not inspect the
filesystem or use tools."#))
}
```

Create `museum-workshop-app/tests/prompt.rs`:

```rust
use museum_exhibit_studio::{
    APOLLO_11_FACTS, MAXIMUM_FACT_COUNT, MAXIMUM_FACT_LENGTH, build_exhibit_prompt,
};

#[test]
fn prompt_shape_and_bounds() {
    let prompt = build_exhibit_prompt(APOLLO_11_FACTS).unwrap();
    assert!(prompt.contains("# <an engaging exhibit title>\n## Narrative"));
    assert!(prompt.contains("## Visitor questions\n1. <question>"));
    assert!(build_exhibit_prompt(Vec::<String>::new()).is_err());
    assert!(build_exhibit_prompt(vec!["fact"; MAXIMUM_FACT_COUNT + 1]).is_err());
    assert!(build_exhibit_prompt([&"a".repeat(MAXIMUM_FACT_LENGTH + 1)]).is_err());
}
```
:::

:::language java
Add `ArrayList` and `Objects` imports to `CuratorPrompts.java`, then append this method inside
`CuratorPrompts`:

```java
public static String buildExhibitPrompt(Iterable<String> approvedFacts) {
    Objects.requireNonNull(approvedFacts, "approvedFacts");
    List<String> facts = new ArrayList<>();
    for (String fact : approvedFacts) {
        if (fact != null && !fact.isBlank()) {
            facts.add(fact.trim());
        }
    }
    if (facts.isEmpty()) {
        throw new IllegalArgumentException("Provide at least one approved fact.");
    }
    if (facts.size() > MAXIMUM_FACT_COUNT) {
        throw new IllegalArgumentException(
                "Provide no more than " + MAXIMUM_FACT_COUNT + " approved facts.");
    }
    if (facts.stream().anyMatch(fact -> fact.length() > MAXIMUM_FACT_LENGTH)) {
        throw new IllegalArgumentException(
                "Each approved fact must be " + MAXIMUM_FACT_LENGTH + " characters or fewer.");
    }

    String factList = facts.stream().map(fact -> "- " + fact)
            .reduce((left, right) -> left + System.lineSeparator() + right).orElseThrow();
    return """
            Create visitor-facing exhibit text about Apollo 11 using only these supplied facts:

            %s

            Return exactly this structure:

            # <an engaging exhibit title>
            ## Narrative
            <100-140 words, excluding the title and questions>
            ## Visitor questions
            1. <question>
            2. <question>
            3. <question>

            Write exactly three distinct visitor reflection questions. Do not add a preface,
            conclusion, software discussion, or facts not supplied above. Do not inspect the
            filesystem or use tools.
            """.formatted(factList);
}
```

Create `museum-workshop-app/src/test/java/workshop/CuratorPromptsTest.java`:

```java
package workshop;

import static org.junit.jupiter.api.Assertions.*;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.Test;

class CuratorPromptsTest {
    @Test void buildsShapeAndRejectsBounds() {
        String prompt = CuratorPrompts.buildExhibitPrompt(CuratorPrompts.APOLLO_11_FACTS);
        assertTrue(prompt.contains("# <an engaging exhibit title>\n## Narrative"));
        assertTrue(prompt.contains("## Visitor questions\n1. <question>"));
        assertThrows(IllegalArgumentException.class,
                () -> CuratorPrompts.buildExhibitPrompt(Collections.emptyList()));
        assertThrows(IllegalArgumentException.class,
                () -> CuratorPrompts.buildExhibitPrompt(
                        Collections.nCopies(CuratorPrompts.MAXIMUM_FACT_COUNT + 1, "fact")));
        assertThrows(IllegalArgumentException.class,
                () -> CuratorPrompts.buildExhibitPrompt(List.of("a".repeat(501))));
    }
}
```
:::

## Run it

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
PYTHONPATH=museum-workshop-app museum-workshop-app/.venv/bin/python -m unittest discover -s museum-workshop-app/tests -p test_curator_prompts.py
```
:::
:::language go
```bash
go -C museum-workshop-app test -run BuildExhibitPrompt ./...
```
:::
:::language rust
```bash
cargo test --manifest-path museum-workshop-app/Cargo.toml --locked --test prompt
```
:::
:::language java
```bash
mvn -f museum-workshop-app/pom.xml -Dtest=CuratorPromptsTest test
```
:::

Pass condition: the valid shape passes, while zero facts, 21 facts, and a 501-character fact fail.
Keep the `PYTHONPATH=museum-workshop-app` prefix so the test runner can import the application
modules while using the isolated environment.

## Check your understanding

1. Why are blank facts removed but overlong facts rejected?
2. Why must prompt validation happen before SDK startup?
3. Which exact Markdown requirements are repeated in the user prompt?
