"""Offline API tests for streaming council failures."""

import json
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend import council, main, storage


FAILURE_MESSAGE = "All models failed to respond. Please try again."


def _sse_events(response):
    return [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]


@pytest.mark.asyncio
async def test_non_streaming_council_uses_shared_stage1_failure_message(monkeypatch):
    stage1 = AsyncMock(return_value=[])
    stage2 = AsyncMock()
    stage3 = AsyncMock()
    monkeypatch.setattr(council, "stage1_collect_responses", stage1)
    monkeypatch.setattr(council, "stage2_collect_rankings", stage2)
    monkeypatch.setattr(council, "stage3_synthesize_final", stage3)

    result = await council.run_full_council("offline question")

    assert result == (
        [],
        [],
        {"model": "error", "response": FAILURE_MESSAGE},
        {},
    )
    stage2.assert_not_awaited()
    stage3.assert_not_awaited()


def test_stream_stops_and_saves_error_when_stage1_has_no_responses(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(storage, "DATA_DIR", str(tmp_path / "conversations"))

    stage1 = AsyncMock(return_value=[])
    stage2 = AsyncMock()
    stage3 = AsyncMock()
    title = AsyncMock(return_value="Offline title")
    monkeypatch.setattr(main, "stage1_collect_responses", stage1)
    monkeypatch.setattr(main, "stage2_collect_rankings", stage2)
    monkeypatch.setattr(main, "stage3_synthesize_final", stage3)
    monkeypatch.setattr(main, "generate_conversation_title", title)

    with TestClient(main.app) as client:
        created = client.post("/api/conversations", json={}).json()
        response = client.post(
            f"/api/conversations/{created['id']}/message/stream",
            json={"content": "offline question"},
        )

    assert response.status_code == 200
    events = _sse_events(response)
    assert [event["type"] for event in events] == [
        "stage1_start",
        "stage1_complete",
        "title_complete",
        "error",
    ]
    assert events[-1] == {"type": "error", "message": FAILURE_MESSAGE}
    assert all(event["type"] not in {"stage2_start", "stage3_start"} for event in events)
    stage1.assert_awaited_once_with("offline question")
    stage2.assert_not_awaited()
    stage3.assert_not_awaited()

    saved = storage.get_conversation(created["id"])
    assert saved["messages"] == [
        {"role": "user", "content": "offline question"},
        {
            "role": "assistant",
            "stage1": [],
            "stage2": [],
            "stage3": {"model": "error", "response": FAILURE_MESSAGE},
        },
    ]
