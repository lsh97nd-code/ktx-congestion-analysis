"""Responses API regressions with an in-memory client; never call OpenAI."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from backend import config
from backend.services import openai_service as service


@pytest.mark.parametrize("status", ["incomplete", "failed", "cancelled", "queued", "in_progress"])
def test_partial_answers_are_not_returned_as_success(monkeypatch, status):
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(status=status, output_text="partial answer")
    monkeypatch.setattr(service, "get_openai_client", lambda: client)
    monkeypatch.setattr(service, "get_openai_model", lambda: "test-model")
    with pytest.raises(RuntimeError, match="완료되지"):
        service.generate_ai_response("question", "instructions")


def test_completed_answer_preserves_request_contract(monkeypatch):
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(status="completed", output_text=" answer ")
    monkeypatch.setattr(service, "get_openai_client", lambda: client)
    monkeypatch.setattr(service, "get_openai_model", lambda: "test-model")
    assert service.generate_ai_response(" question ", " instructions ") == "answer"
    client.responses.create.assert_called_once_with(model="test-model", instructions="instructions", input="question", store=False)


@pytest.mark.parametrize("text", [None, "", "   "])
def test_completed_response_requires_text(monkeypatch, text):
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(status="completed", output_text=text)
    monkeypatch.setattr(service, "get_openai_client", lambda: client)
    monkeypatch.setattr(service, "get_openai_model", lambda: "test-model")
    with pytest.raises(RuntimeError, match="텍스트"):
        service.generate_ai_response("question", "instructions")


def test_environment_loader_does_not_search_parent_directories(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("KTX_TEST_ENV=parent-secret\n", encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    monkeypatch.setattr(config, "ENV_FILE", project / ".env")
    monkeypatch.delenv("KTX_TEST_ENV", raising=False)
    config.load_environment()
    import os
    assert "KTX_TEST_ENV" not in os.environ
    (project / ".env").write_text("KTX_TEST_ENV=local\n", encoding="utf-8")
    monkeypatch.setenv("KTX_TEST_ENV", "deployment")
    config.load_environment()
    assert os.environ["KTX_TEST_ENV"] == "deployment"
