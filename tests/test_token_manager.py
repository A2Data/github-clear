from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest
from dotenv import dotenv_values

from core.token_manager import TokenManager


def test_environment_tokens_work_without_env_file(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "container-github-token")
    monkeypatch.setenv("GITEE_TOKEN", "container-gitee-token")
    manager = TokenManager(tmp_path / "missing.env")
    assert manager.is_github_configured()
    assert manager.is_gitee_configured()
    assert manager.get_github_token() == "container-github-token"


def test_quoted_values_comments_and_environment_precedence(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        "GITHUB_TOKEN=\"file-token-value\" # comment\nGITEE_TOKEN='gitee-file-token'\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GITHUB_TOKEN", "environment-token")
    manager = TokenManager(env)
    assert manager.get_github_token() == "environment-token"
    assert manager.get_gitee_token() == "gitee-file-token"


def test_failed_write_does_not_replace_live_token(isolated_config, monkeypatch):
    isolated_config.set_github_token("old-token")
    monkeypatch.setattr(
        "core.token_manager.set_key", Mock(side_effect=OSError("read-only"))
    )
    with pytest.raises(OSError):
        isolated_config.set_github_token("new-token")
    assert isolated_config.get_github_token() == "old-token"


def test_concurrent_saves_preserve_both_tokens_and_other_settings(isolated_config):
    isolated_config._env_path.write_text(
        "# custom config\nOTHER=value\n", encoding="utf-8"
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        github = pool.submit(isolated_config.set_github_token, "new-github-token")
        gitee = pool.submit(isolated_config.set_gitee_token, "new-gitee-token")
        github.result()
        gitee.result()
    values = dotenv_values(isolated_config._env_path)
    assert values["GITHUB_TOKEN"] == "new-github-token"
    assert values["GITEE_TOKEN"] == "new-gitee-token"
    assert values["OTHER"] == "value"
    assert "# custom config" in isolated_config._env_path.read_text()
    restarted = TokenManager(isolated_config._env_path)
    assert restarted.get_github_token() == "new-github-token"
