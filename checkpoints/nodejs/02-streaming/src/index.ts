import { CopilotClient } from "@github/copilot-sdk";
import { streamResponse } from "./workshop.js";

const client = new CopilotClient();
await client.start();
try {
  const session = await client.createSession({ streaming: true });
  try {
    await streamResponse(session, "Describe why streaming improves an interactive assistant in one sentence.");
  } finally {
    await session.disconnect();
  }
} finally {
  await client.stop();
}
