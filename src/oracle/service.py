"""Runs a question through the ORACLE pipeline and returns the answer plus metrics."""
from __future__ import annotations

import time
import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from oracle.observability import start_request

APP_NAME = "oracle"
_session_service = InMemorySessionService()
_runner: Runner | None = None


def _get_runner() -> Runner:
    global _runner
    if _runner is None:
        from oracle.agents.pipeline import root_agent

        _runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=_session_service)
    return _runner


async def ask(question: str, user_id: str = "local", session_id: str | None = None) -> dict:
    session_id = session_id or uuid.uuid4().hex
    await _session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    metrics = start_request()
    message = types.Content(role="user", parts=[types.Part(text=question)])
    started = time.perf_counter()
    final = ""
    async for event in _get_runner().run_async(
        user_id=user_id, session_id=session_id, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text.strip():
                final = text  # the last final response comes from the critic
    latency_ms = (time.perf_counter() - started) * 1000
    return {"answer": final, "session_id": session_id, "metrics": metrics.to_dict(latency_ms)}
