import asyncio

from copilot import CopilotClient


async def main() -> None:
    async with CopilotClient() as client:
        async with await client.create_session() as session:
            await session.send("In one sentence, explain why an accessible name matters for a form input.")


if __name__ == "__main__":
    asyncio.run(main())
