from unittest.mock import Mock

import pytest
import requests
from fastapi.testclient import TestClient

import main
from core import token_manager


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """No test may read/write real credentials or call a live provider."""
    for key in token_manager.TokenManager._keys:
        monkeypatch.delenv(key, raising=False)
    manager = token_manager.TokenManager(tmp_path / ".env")
    monkeypatch.setattr(token_manager, "_manager", manager)

    def no_network(*args, **kwargs):
        raise AssertionError("External network access is forbidden in tests")

    monkeypatch.setattr(requests.sessions.Session, "request", no_network)
    return manager


@pytest.fixture
def client():
    with TestClient(main.app) as client:
        yield client


@pytest.fixture
def github_api(monkeypatch, isolated_config):
    isolated_config.set_github_token("fake-github-token")
    api = Mock()
    api.__enter__ = Mock(return_value=api)
    api.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(main, "GitHubAPI", Mock(return_value=api))
    return api
