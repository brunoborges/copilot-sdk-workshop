use std::io::{self, Write};

use github_copilot_sdk::types::{MessageOptions, SessionConfig};
use github_copilot_sdk::{Client, ClientOptions};

#[tokio::main]
async fn main() -> Result<(), github_copilot_sdk::Error> {
    let client = Client::start(ClientOptions::default()).await?;
    let mut config = SessionConfig::default();
    config.streaming = Some(true);
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
            "Explain accessible names in three short bullet points.",
        ))
        .await?;
    println!();
    session.disconnect().await?;
    client.stop().await?;
    Ok(())
}
