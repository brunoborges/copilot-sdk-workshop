import { approveAll, CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
await client.start();
try {
  const session = await client.createSession({ onPermissionRequest: approveAll });
  try {
    const response = await session.sendAndWait({ prompt: "Reply with one sentence confirming this Copilot session is ready." });
    console.log(response?.data && "content" in response.data ? response.data.content : response);
  } finally {
    await session.disconnect();
  }
} finally {
  await client.stop();
}
