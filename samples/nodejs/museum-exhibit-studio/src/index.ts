import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { apollo11Facts } from "./prompts.js";
import { createCopilotCuratorClient, MuseumExhibitService } from "./service.js";
import type { ExhibitValidation } from "./validator.js";

const terminal = createInterface({ input, output });

try {
  console.log("=== Museum Exhibit Studio ===");
  console.log("Approved Apollo 11 facts:");
  apollo11Facts.forEach((fact, index) => console.log(`${index + 1}. ${fact}`));

  const answer = (await terminal.question("\nUse these facts? [Y/n]: ")).trim();
  const facts = answer.toLocaleLowerCase() === "n" ? await readFacts() : apollo11Facts;
  const studio = new MuseumExhibitService(createCopilotCuratorClient());
  const result = await studio.generate(facts, process.env.COPILOT_MODEL);

  console.log(`\n${result.content}\n`);
  printValidation(result.validation);
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(message.toLocaleLowerCase().includes("timeout")
    ? "The curator did not respond within two minutes. Try again."
    : `Could not generate the exhibit: ${message}`);
  process.exitCode = 1;
} finally {
  terminal.close();
}

async function readFacts(): Promise<string[]> {
  console.log("Enter one approved fact per line. Submit a blank line when finished:");
  const facts: string[] = [];
  while (true) {
    const fact = (await terminal.question("")).trim();
    if (!fact) return facts;
    facts.push(fact);
  }
}

function printValidation(validation: ExhibitValidation): void {
  console.log(validation.valid ? "Structural checks passed." : "Structural checks found issues:");
  console.log(`- One level-one title: ${validation.title.present}`);
  console.log(`- Narrative section: ${validation.narrative.present}`);
  console.log(`- Narrative length: ${validation.narrative.wordCount} words (within 100-140: ${validation.narrative.withinLimit})`);
  console.log(`- Visitor questions section: ${validation.visitorQuestions.present}`);
  console.log(`- Numbered questions: ${validation.visitorQuestions.questionCount} (exactly three: ${validation.visitorQuestions.exactlyThree})`);
  console.log(`- Every item is a question: ${validation.visitorQuestions.allItemsAreQuestions}`);
  validation.errors.forEach((error) => console.log(`  - ${error}`));
  console.log("\nStructural checks do not prove factual grounding. Unsupported claims require human review or a separate evaluator.");
}
