import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
await client.start();
try {
  const session = await client.createSession({});
  try {
    await session.sendAndWait({ prompt: "Reply with one sentence confirming this Copilot session is ready." });
  } finally {
    await session.disconnect();
  }
} finally {
  await client.stop();
}
