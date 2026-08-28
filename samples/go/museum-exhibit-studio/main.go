package main

import (
	"bufio"
	"context"
	"errors"
	"fmt"
	"os"
	"strings"
)

func main() {
	if err := runCLI(bufio.NewReader(os.Stdin)); err != nil {
		fmt.Fprintln(os.Stderr, "Could not generate the exhibit:", err)
		os.Exit(1)
	}
}

func runCLI(input *bufio.Reader) error {
	fmt.Println("=== Museum Exhibit Studio ===")
	fmt.Println("Approved Apollo 11 facts:")
	for index, fact := range apollo11Facts {
		fmt.Printf("%d. %s\n", index+1, fact)
	}

	fmt.Print("\nUse these facts? [Y/n]: ")
	answer, _ := input.ReadString('\n')
	facts := append([]string(nil), apollo11Facts...)
	if strings.EqualFold(strings.TrimSpace(answer), "n") {
		facts = readFacts(input)
	}

	result, err := (museumExhibitService{client: newCopilotCuratorClient()}).Generate(
		context.Background(),
		facts,
		os.Getenv("COPILOT_MODEL"),
	)
	if err != nil {
		if errorsIsDeadline(err) {
			return fmt.Errorf("the curator did not respond within two minutes; try again")
		}
		return err
	}
	fmt.Printf("\n%s\n\n", result.Content)
	printValidation(result.Validation)
	return nil
}

func errorsIsDeadline(err error) bool {
	return errors.Is(err, context.DeadlineExceeded)
}

func readFacts(input *bufio.Reader) []string {
	fmt.Println("Enter one approved fact per line. Submit a blank line when finished:")
	var facts []string
	for {
		fact, err := input.ReadString('\n')
		fact = strings.TrimSpace(fact)
		if fact == "" || err != nil {
			return facts
		}
		facts = append(facts, fact)
	}
}

func printValidation(validation ExhibitValidation) {
	if validation.Valid() {
		fmt.Println("Structural checks passed.")
	} else {
		fmt.Println("Structural checks found issues:")
	}
	fmt.Printf("- One level-one title: %t\n", validation.Title.Present())
	fmt.Printf("- Narrative section: %t\n", validation.Narrative.Present)
	fmt.Printf("- Narrative length: %d words (within 100-140: %t)\n", validation.Narrative.WordCount, validation.Narrative.WithinLimit())
	fmt.Printf("- Visitor questions section: %t\n", validation.VisitorQuestions.Present)
	fmt.Printf("- Numbered questions: %d (exactly three: %t)\n", validation.VisitorQuestions.QuestionCount, validation.VisitorQuestions.ExactlyThree())
	fmt.Printf("- Every item is a question: %t\n", validation.VisitorQuestions.AllItemsAreQuestions)
	for _, message := range validation.Errors {
		fmt.Println("  -", message)
	}
	fmt.Println("\nStructural checks do not prove factual grounding. Unsupported claims require human review or a separate evaluator.")
}
