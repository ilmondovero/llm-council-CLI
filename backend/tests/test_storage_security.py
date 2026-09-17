"""Offline regression tests for conversation ID path safety."""

import uuid
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from backend import storage
from backend.main import app


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", "/api/conversations/..%5C..%5Cleak"),
        ("post", "/api/conversations/..%5C..%5Cleak/message"),
        ("post", "/api/conversations/..%5C..%5Cleak/message/stream"),
    ],
)
def test_invalid_conversation_ids_return_404_without_filesystem_access(
    monkeypatch, tmp_path, method, url
):
    data_dir = tmp_path / "conversations"
    path_lookup = Mock(side_effect=AssertionError("invalid ID reached path lookup"))
    monkeypatch.setattr(storage, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(storage, "get_conversation_path", path_lookup)

    with TestClient(app) as client:
        if method == "get":
            response = client.get(url)
        else:
            response = client.post(url, json={"content": "must not be saved"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found"}
    path_lookup.assert_not_called()
    assert not data_dir.exists()
    assert list(tmp_path.iterdir()) == []


def test_storage_rejects_invalid_id_before_creating_data_directory(
    monkeypatch, tmp_path
):
    data_dir = tmp_path / "conversations"
    monkeypatch.setattr(storage, "DATA_DIR", str(data_dir))

    with pytest.raises(ValueError, match="Invalid conversation ID"):
        storage.create_conversation(r"..\..\leak")

    assert not data_dir.exists()


def test_valid_uuid_round_trips_in_temporary_storage(monkeypatch, tmp_path):
    data_dir = tmp_path / "conversations"
    monkeypatch.setattr(storage, "DATA_DIR", str(data_dir))
    conversation_id = str(uuid.uuid4())

    created = storage.create_conversation(conversation_id)

    assert created["id"] == conversation_id
    assert storage.get_conversation(conversation_id) == created
    assert (data_dir / f"{conversation_id}.json").is_file()
