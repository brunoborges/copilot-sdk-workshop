use std::io::{self, Write};

use museum_exhibit_studio::{
    APOLLO_11_FACTS, CopilotCuratorClient, ExhibitValidation, generate_exhibit,
};

fn read_facts() -> io::Result<Vec<String>> {
    println!("Enter one approved fact per line. Submit a blank line when finished:");
    let mut facts = Vec::new();
    loop {
        let mut fact = String::new();
        io::stdin().read_line(&mut fact)?;
        let fact = fact.trim();
        if fact.is_empty() {
            return Ok(facts);
        }
        facts.push(fact.to_owned());
    }
}

fn print_validation(validation: &ExhibitValidation) {
    println!(
        "{}",
        if validation.is_valid() {
            "Structural checks passed."
        } else {
            "Structural checks found issues:"
        }
    );
    println!("- One level-one title: {}", validation.title.is_present());
    println!("- Narrative section: {}", validation.narrative.present);
    println!(
        "- Narrative length: {} words (within 100-140: {})",
        validation.narrative.word_count,
        validation.narrative.is_within_limit()
    );
    println!(
        "- Visitor questions section: {}",
        validation.visitor_questions.present
    );
    println!(
        "- Numbered questions: {} (exactly three: {})",
        validation.visitor_questions.question_count,
        validation.visitor_questions.has_exactly_three()
    );
    println!(
        "- Every item is a question: {}",
        validation.visitor_questions.all_items_are_questions
    );
    for error in &validation.errors {
        println!("  - {error}");
    }
    println!(
        "\nStructural checks do not prove factual grounding. Unsupported claims require human review or a separate evaluator."
    );
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    println!("=== Museum Exhibit Studio ===");
    println!("Approved Apollo 11 facts:");
    for (index, fact) in APOLLO_11_FACTS.iter().enumerate() {
        println!("{}. {fact}", index + 1);
    }

    print!("\nUse these facts? [Y/n]: ");
    io::stdout().flush()?;
    let mut choice = String::new();
    io::stdin().read_line(&mut choice)?;
    let facts = if choice.trim().eq_ignore_ascii_case("n") {
        read_facts()?
    } else {
        APOLLO_11_FACTS.map(str::to_owned).to_vec()
    };

    let model = std::env::var("COPILOT_MODEL").ok();
    let mut client = CopilotCuratorClient::new();
    match generate_exhibit(&mut client, &facts, model.as_deref()).await {
        Ok(result) => {
            println!("\n{}\n", result.content);
            print_validation(&result.validation);
            Ok(())
        }
        Err(error) => {
            eprintln!("Could not generate the exhibit: {error}");
            Err(error)
        }
    }
}
