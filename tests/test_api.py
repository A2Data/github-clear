import asyncio
from threading import Event
from unittest.mock import Mock

import httpx
import pytest
import requests
from github import GithubException

import main


@pytest.mark.parametrize(
    "path", ["/", "/dashboard", "/repositories", "/profile", "/settings", "/guide", "/health"]
)
def test_pages_render_without_credentials(client, path):
    assert client.get(path).status_code == 200


def test_configured_pages_render(client, github_api):
    github_api.get_user_info.return_value = {
        "login": "alice",
        "name": "Alice",
        "avatar_url": "",
        "html_url": "https://github.com/alice",
        "bio": "",
        "public_repos": 0,
        "followers": 0,
        "following": 0,
    }
    for path in ("/dashboard", "/repositories", "/profile", "/settings"):
        response = client.get(path)
        assert response.status_code == 200
    dashboard = client.get("/dashboard").text
    assert 'id="stat-public">0</div>' in dashboard
    assert dashboard.index("/static/js/app.js") < dashboard.index("loadDashboardStats")


@pytest.mark.parametrize(
    "repos",
    [
        [],
        "alice/repo",
        None,
        [123],
        ["../repo"],
        ["alice/repo/extra"],
        [" "],
        ["a/.."],
        ["a?<b"],
        ["repo"] * 1001,
    ],
)
@pytest.mark.parametrize("action", ["delete", "archive", "leave"])
def test_invalid_batches_never_call_provider(client, github_api, repos, action):
    assert (
        client.post(f"/api/repos/github/{action}", json={"repos": repos}).status_code
        == 422
    )
    getattr(github_api, f"{action}_repo").assert_not_called()


def test_batch_deduplicates_and_continues_after_network_failure(client, github_api):
    github_api.delete_repo.side_effect = [
        (True, ""),
        requests.Timeout("private URL"),
        (True, ""),
    ]
    response = client.post(
        "/api/repos/github/delete",
        json={"repos": [" alice/a ", "alice/a", "alice/b", "alice/c"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == 2
    assert data["total"] == 3
    assert data["results"] == {"alice/a": True, "alice/b": False, "alice/c": True}
    assert "alice/b:" in data["errors"][0]
    assert "private URL" not in response.text
    assert github_api.delete_repo.call_count == 3
    github_api.__exit__.assert_called_once()


def test_gitee_batch_isolates_failure(client, monkeypatch, isolated_config):
    isolated_config.set_gitee_token("fake-gitee-token")
    api = Mock()
    api.__enter__ = Mock(return_value=api)
    api.__exit__ = Mock(return_value=False)
    api.delete_repo.side_effect = [requests.Timeout(), True]
    monkeypatch.setattr(main, "GiteeAPI", Mock(return_value=api))
    response = client.post(
        "/api/repos/gitee/delete", json={"repos": ["alice/a", "alice/b"]}
    )
    assert response.json()["results"] == {"alice/a": False, "alice/b": True}


@pytest.mark.parametrize("path", ["/api/repos/github", "/api/repos/gitee"])
def test_listing_requires_token(client, path):
    assert client.get(path).status_code == 401
    assert client.get(path, params={"sort": "invalid"}).status_code == 422


def test_dashboard_reports_upstream_error(client, github_api):
    github_api.list_repos.side_effect = GithubException(403, {"message": "rate limit"})
    assert client.get("/api/dashboard/stats").status_code == 403


def test_invalid_gitee_token_is_failure(client, monkeypatch):
    response = requests.Response()
    response.status_code = 401
    monkeypatch.setattr(
        requests.sessions.Session, "request", Mock(return_value=response)
    )
    result = client.post(
        "/api/settings/test-token", json={"platform": "gitee", "token": "fake-token"}
    )
    assert result.status_code == 401
    assert "success" not in result.json()


@pytest.mark.parametrize(
    "payload",
    [
        {"platform": "unknown", "token": "abc"},
        {"platform": "github", "token": "   "},
        {"platform": "github", "token": "abc\nGITEE_TOKEN=injected"},
        {"platform": "github", "token": 123},
    ],
)
def test_invalid_settings_do_not_write(client, isolated_config, payload):
    assert client.post("/api/settings/token", json=payload).status_code == 422
    assert not isolated_config._env_path.exists()


def test_trophy_url_survives_partial_settings_save(client, isolated_config):
    isolated_config._save_values({"TROPHIES_URL": "https://trophy.example"})
    result = client.post(
        "/api/settings/stats-url", json={"stats_url": "stats.example", "streak_url": ""}
    )
    assert result.status_code == 200
    assert isolated_config._get("STATS_URL") == "https://stats.example"
    assert isolated_config._get("TROPHIES_URL") == "https://trophy.example"


def test_profile_header_style_reaches_generator(client):
    response = client.post(
        "/api/profile/generate", json={"username": "alice", "header_style": "capsule"}
    )
    assert response.status_code == 200
    assert "capsule-render" in response.json()["content"]


def test_slow_repository_request_does_not_block_health(github_api):
    started, release = Event(), Event()

    def slow_list(**kwargs):
        started.set()
        release.wait(timeout=3)
        return []

    github_api.list_repos.side_effect = slow_list

    async def scenario():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=main.app), base_url="http://test"
        ) as client:
            slow = asyncio.create_task(client.get("/api/repos/github"))
            try:
                for _ in range(100):
                    if started.is_set():
                        break
                    await asyncio.sleep(0.01)
                assert started.is_set()
                assert not slow.done(), "Blocking API work ran on the event loop"
                response = await asyncio.wait_for(client.get("/health"), timeout=0.5)
                assert response.json() == {"status": "ok"}
                assert not slow.done()
            finally:
                release.set()
                await slow

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "url",
    [
        "https://",
        "ftp://stats.example",
        "javascript:alert(1)",
        "https://stats.example:99999",
        "https://stats.example\nOTHER=value",
    ],
)
def test_invalid_stats_urls_do_not_write(client, isolated_config, url):
    assert (
        client.post("/api/settings/stats-url", json={"stats_url": url}).status_code
        == 422
    )
    assert not isolated_config._env_path.exists()
