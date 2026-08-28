package workshop;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.TimeoutException;

public final class MuseumExhibitStudio {
    private MuseumExhibitStudio() {
    }

    public static void main(String[] args) {
        System.out.println("=== Museum Exhibit Studio ===");
        System.out.println("Approved Apollo 11 facts:");
        for (int index = 0; index < CuratorPrompts.APOLLO_11_FACTS.size(); index++) {
            System.out.printf("%d. %s%n", index + 1, CuratorPrompts.APOLLO_11_FACTS.get(index));
        }

        Scanner input = new Scanner(System.in);
        System.out.print("\nUse these facts? [Y/n]: ");
        String choice = input.hasNextLine() ? input.nextLine().trim() : "";
        List<String> facts = choice.equalsIgnoreCase("n")
                ? readFacts(input)
                : CuratorPrompts.APOLLO_11_FACTS;

        try (var client = new CopilotCuratorClient()) {
            var studio = new MuseumExhibitService(client);
            var result = studio.generate(facts, System.getenv("COPILOT_MODEL"));
            System.out.printf("%n%s%n%n", result.content());
            printValidation(result.validation());
        } catch (Exception exception) {
            if (hasCause(exception, TimeoutException.class)) {
                System.err.println("The curator did not respond within two minutes. Try again.");
            } else {
                System.err.println("Could not generate the exhibit: " + rootMessage(exception));
            }
            System.exit(1);
        }
    }

    private static List<String> readFacts(Scanner input) {
        System.out.println("Enter one approved fact per line. Submit a blank line when finished:");
        List<String> facts = new ArrayList<>();
        while (input.hasNextLine()) {
            String fact = input.nextLine();
            if (fact.isBlank()) {
                break;
            }
            facts.add(fact.trim());
        }
        return facts;
    }

    private static void printValidation(ExhibitValidation validation) {
        System.out.println(validation.valid()
                ? "Structural checks passed."
                : "Structural checks found issues:");
        System.out.println("- One level-one title: " + validation.title().present());
        System.out.println("- Narrative section: " + validation.narrative().present());
        System.out.printf("- Narrative length: %d words (within 100-140: %s)%n",
                validation.narrative().wordCount(), validation.narrative().withinLimit());
        System.out.println("- Visitor questions section: " + validation.visitorQuestions().present());
        System.out.printf("- Numbered questions: %d (exactly three: %s)%n",
                validation.visitorQuestions().questionCount(),
                validation.visitorQuestions().exactlyThree());
        System.out.println("- Every item is a question: "
                + validation.visitorQuestions().allItemsAreQuestions());
        validation.errors().forEach(error -> System.out.println("  - " + error));
        System.out.println("""

                Structural checks do not prove factual grounding. Unsupported claims require \
                human review or a separate evaluator.""");
    }

    private static boolean hasCause(Throwable error, Class<? extends Throwable> type) {
        Throwable current = error;
        while (current != null) {
            if (type.isInstance(current)) {
                return true;
            }
            current = current.getCause();
        }
        return false;
    }

    private static String rootMessage(Throwable error) {
        Throwable current = error;
        while (current.getCause() != null) {
            current = current.getCause();
        }
        return current.getMessage() == null ? current.getClass().getSimpleName() : current.getMessage();
    }
}
