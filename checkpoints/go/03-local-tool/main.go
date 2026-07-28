package main

import (
	"context"
	"fmt"
	"strings"

	copilot "github.com/github/copilot-sdk/go"
)

type lookupParams struct {
	Query string `json:"query" jsonschema:"The accessibility issue or WCAG criterion to look up."`
}

func accessibilityRuleLookup(params lookupParams, _ copilot.ToolInvocation) (any, error) {
	query := strings.ToLower(params.Query)
	if strings.Contains(query, "4.1.2") || strings.Contains(query, "accessible name") {
		return map[string]string{
			"criterion":      "4.1.2",
			"title":          "Name, Role, Value",
			"recommendation": "Associate each input with a visible label.",
		}, nil
	}
	return map[string]string{
		"criterion":      "No exact match",
		"recommendation": "Verify the evidence and consult the WCAG reference.",
	}, nil
}

func streamResponse(session *copilot.Session, prompt string) error {
	unsubscribe := session.On(func(event copilot.SessionEvent) {
		if delta, ok := event.Data.(*copilot.AssistantMessageDeltaData); ok {
			fmt.Print(delta.DeltaContent)
		}
	})
	defer unsubscribe()

	_, err := session.SendAndWait(context.Background(), copilot.MessageOptions{Prompt: prompt})
	fmt.Println()
	return err
}

func main() {
	lookup := copilot.DefineTool(
		"accessibility_rule_lookup",
		"Looks up read-only WCAG guidance maintained by this application.",
		accessibilityRuleLookup,
	)
	lookup.SkipPermission = true

	client := copilot.NewClient(&copilot.ClientOptions{LogLevel: "error"})
	if err := client.Start(context.Background()); err != nil {
		panic(err)
	}
	defer client.Stop()

	session, err := client.CreateSession(context.Background(), &copilot.SessionConfig{
		Streaming:      copilot.Bool(true),
		Tools:          []copilot.Tool{lookup},
		AvailableTools: []string{"accessibility_rule_lookup"},
	})
	if err != nil {
		panic(err)
	}
	defer session.Disconnect()

	if err := streamResponse(session, "Use accessibility_rule_lookup to explain WCAG 4.1.2."); err != nil {
		panic(err)
	}
}
