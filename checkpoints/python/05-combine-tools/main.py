import asyncio
import sys
from urllib.parse import urlsplit

from copilot import CopilotClient
from copilot.session_events import AssistantMessageDeltaData, SessionIdleData

from workshop import accessibility_rule_lookup, create_snapshot_reader, permission_for_target


async def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Usage: python main.py <http-or-https-url>")
    target = sys.argv[1]
    if urlsplit(target).scheme not in {"http", "https"}:
        raise ValueError("Enter an absolute HTTP or HTTPS URL.")
    async with CopilotClient() as client:
        async with await client.create_session(
            streaming=True,
            on_permission_request=permission_for_target(target),
            tools=[accessibility_rule_lookup, create_snapshot_reader(".")],
            available_tools=["accessibility_rule_lookup", "read_latest_accessibility_snapshot", "playwright-browser_navigate"],
            mcp_servers={"playwright": {"command": "npx", "args": ["-y", "@playwright/mcp@0.0.78", "--browser=msedge"], "working_directory": ".", "tools": ["browser_navigate"]}},
        ) as session:
            done = asyncio.Event()

            def on_event(event) -> None:
                match event.data:
                    case AssistantMessageDeltaData(delta_content=delta) if delta:
                        print(delta, end="", flush=True)
                    case SessionIdleData():
                        done.set()

            session.on(on_event)
            await session.send(f"Open {target}, read the snapshot, then use accessibility_rule_lookup for one evidence-backed recommendation.")
            await done.wait()


if __name__ == "__main__":
    asyncio.run(main())
