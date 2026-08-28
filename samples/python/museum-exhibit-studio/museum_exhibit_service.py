from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from curator_prompts import SYSTEM_MESSAGE, build_exhibit_prompt
from exhibit_validator import ExhibitValidation, validate_exhibit

GENERATION_TIMEOUT_SECONDS = 120.0


@dataclass(frozen=True)
class GeneratedExhibit:
    content: str
    validation: ExhibitValidation


def create_session_configuration(model: str | None = None) -> dict[str, Any]:
    return {
        "client_name": "museum-exhibit-studio",
        "model": model.strip() if model and model.strip() else None,
        "available_tools": [],
        "streaming": False,
        "system_message": {"mode": "replace", "content": SYSTEM_MESSAGE},
    }


class MuseumExhibitService:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def generate(
        self, approved_facts: list[str] | tuple[str, ...], model: str | None = None
    ) -> GeneratedExhibit:
        prompt = build_exhibit_prompt(approved_facts)
        session = None
        try:
            await self._client.start()
            session = await self._client.create_session(
                **create_session_configuration(model)
            )
            response = await session.send_and_wait(
                prompt, timeout=GENERATION_TIMEOUT_SECONDS
            )
            content = getattr(getattr(response, "data", None), "content", None)
            if not content or not content.strip():
                raise RuntimeError("The curator returned no exhibit content.")
            return GeneratedExhibit(content, validate_exhibit(content))
        finally:
            try:
                if session is not None:
                    await session.disconnect()
            finally:
                await self._client.stop()
