from __future__ import annotations

import asyncio
import os
import sys

from copilot import CopilotClient

from curator_prompts import APOLLO_11_FACTS
from exhibit_validator import ExhibitValidation
from museum_exhibit_service import MuseumExhibitService

GROUNDING_DISCLAIMER = (
    "Structural checks do not prove factual grounding. "
    "Unsupported claims require human review or a separate evaluator."
)


def read_facts() -> list[str]:
    print("Enter one approved fact per line. Submit a blank line when finished:")
    facts: list[str] = []
    while fact := input().strip():
        facts.append(fact)
    return facts


def print_validation(validation: ExhibitValidation) -> None:
    print(
        "Structural checks passed."
        if validation.valid
        else "Structural checks found issues:"
    )
    print(f"- One level-one title: {validation.title.present}")
    print(f"- Narrative section: {validation.narrative.present}")
    print(
        f"- Narrative length: {validation.narrative.word_count} words "
        f"(within 100-140: {validation.narrative.within_limit})"
    )
    print(f"- Visitor questions section: {validation.visitor_questions.present}")
    print(
        f"- Numbered questions: {validation.visitor_questions.question_count} "
        f"(exactly three: {validation.visitor_questions.exactly_three})"
    )
    print(
        "- Every item is a question: "
        f"{validation.visitor_questions.all_items_are_questions}"
    )
    for error in validation.errors:
        print(f"  - {error}")
    print(f"\n{GROUNDING_DISCLAIMER}")


async def main() -> int:
    print("=== Museum Exhibit Studio ===")
    print("Approved Apollo 11 facts:")
    for index, fact in enumerate(APOLLO_11_FACTS, start=1):
        print(f"{index}. {fact}")

    use_defaults = input("\nUse these facts? [Y/n]: ").strip()
    facts = read_facts() if use_defaults.casefold() == "n" else list(APOLLO_11_FACTS)
    studio = MuseumExhibitService(CopilotClient())
    try:
        result = await studio.generate(facts, os.getenv("COPILOT_MODEL"))
        print(f"\n{result.content}\n")
        print_validation(result.validation)
        return 0
    except TimeoutError:
        print("The curator did not respond within two minutes. Try again.", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Could not generate the exhibit: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
