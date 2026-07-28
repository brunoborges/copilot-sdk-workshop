import asyncio

from copilot import CopilotClient
from copilot.session_events import AssistantMessageDeltaData, SessionIdleData


async def main() -> None:
    async with CopilotClient() as client:
        async with await client.create_session(streaming=True) as session:
            done = asyncio.Event()

            def on_event(event) -> None:
                match event.data:
                    case AssistantMessageDeltaData(delta_content=delta) if delta:
                        print(delta, end="", flush=True)
                    case SessionIdleData():
                        done.set()

            session.on(on_event)
            await session.send("Explain accessible names in three short bullet points.")
            await done.wait()


if __name__ == "__main__":
    asyncio.run(main())
