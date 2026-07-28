use std::io::{self, Write};
use std::sync::Arc;

use async_trait::async_trait;
use github_copilot_sdk::tool::{schema_for, JsonSchema, ToolHandler};
use github_copilot_sdk::types::{MessageOptions, SessionConfig, Tool, ToolInvocation};
use github_copilot_sdk::{Client, ClientOptions, Error, ToolResult};
use serde::Deserialize;

#[derive(Deserialize, JsonSchema)]
struct LookupParams {
    /// The accessibility issue or WCAG criterion to look up.
    query: String,
}

struct AccessibilityRuleLookup;

#[async_trait]
impl ToolHandler for AccessibilityRuleLookup {
    async fn call(&self, invocation: ToolInvocation) -> Result<ToolResult, Error> {
        let params: LookupParams = serde_json::from_value(invocation.arguments)?;
        let result = if params.query.to_lowercase().contains("4.1.2") {
            r#"{"criterion":"4.1.2","title":"Name, Role, Value","recommendation":"Associate each input with a visible label."}"#
        } else {
            r#"{"criterion":"No exact match","recommendation":"Verify the evidence and consult the WCAG reference."}"#
        };
        Ok(ToolResult::Text(result.to_owned()))
    }
}

#[tokio::main]
async fn main() -> Result<(), github_copilot_sdk::Error> {
    let lookup = Tool::new("accessibility_rule_lookup")
        .with_description("Looks up read-only WCAG guidance maintained by this application.")
        .with_parameters(schema_for::<LookupParams>())
        .with_skip_permission(true)
        .with_handler(Arc::new(AccessibilityRuleLookup));

    let client = Client::start(ClientOptions::default()).await?;
    let mut config = SessionConfig::default();
    config.streaming = Some(true);
    config.tools = Some(vec![lookup]);
    config.available_tools = Some(vec!["accessibility_rule_lookup".to_owned()]);
    let session = client.create_session(config).await?;

    let mut events = session.subscribe();
    tokio::spawn(async move {
        while let Ok(event) = events.recv().await {
            if event.event_type == "assistant.message_delta" {
                if let Some(delta) = event.data.get("deltaContent").and_then(|value| value.as_str()) {
                    print!("{delta}");
                    io::stdout().flush().ok();
                }
            }
        }
    });

    session
        .send_and_wait(MessageOptions::new(
            "Use accessibility_rule_lookup to explain WCAG 4.1.2.",
        ))
        .await?;
    println!();
    session.disconnect().await?;
    client.stop().await?;
    Ok(())
}
