from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
from github import GithubException

from core.github_api import GitHubAPI
from core.gitee_api import GiteeAPI


@pytest.fixture
def github(monkeypatch):
    client = Mock()
    client.get_repo.return_value.owner.login = "alice"
    monkeypatch.setattr("core.github_api.Github", Mock(return_value=client))
    api = GitHubAPI("fake-token")
    api._user = Mock(login="alice")
    return api


@pytest.mark.parametrize("name", ["sample", "alice/sample"])
def test_archive_accepts_both_name_formats(github, name):
    assert github.archive_repo(name)
    github.client.get_repo.assert_called_once_with("alice/sample")
    github.client.get_repo.return_value.edit.assert_called_once_with(archived=True)


def test_management_rejects_another_account(github):
    with pytest.raises(ValueError, match="当前账户"):
        github.delete_repo("someone-else/sample")
    github.client.get_repo.assert_not_called()


def test_list_only_requests_owned_repositories(github):
    github.user.get_repos.return_value = []
    assert github.list_repos(visibility="private") == []
    github.user.get_repos.assert_called_once_with(
        affiliation="owner", visibility="private", sort="updated"
    )


def test_collaborations_exclude_organization_membership(github):
    github.user.get_repos.return_value = []
    assert github.list_collaborator_repos() == []
    github.user.get_repos.assert_called_once_with(
        affiliation="collaborator", sort="updated"
    )


def test_profile_permission_failure_does_not_create_repository(github):
    github.client.get_repo.side_effect = GithubException(403, {"message": "denied"})
    assert github.update_profile_readme("hello") is False
    github.user.create_repo.assert_not_called()


@pytest.mark.parametrize("status", [403, 404, 409])
def test_profile_update_failure_does_not_attempt_duplicate_creation(github, status):
    repo = github.client.get_repo.return_value
    repo.get_readme.return_value = SimpleNamespace(path="readme.md", sha="old-sha")
    repo.update_file.side_effect = GithubException(status, {"message": "failed"})
    assert github.update_profile_readme("hello") is False
    assert repo.update_file.call_args.kwargs["path"] == "readme.md"
    repo.create_file.assert_not_called()


def response(status, data=None):
    result = Mock(status_code=status)
    result.json.return_value = data
    return result


def test_gitee_invalid_token_raises_instead_of_empty_account():
    with GiteeAPI("secret-token") as api:
        api.session.request = Mock(return_value=response(401))
        with pytest.raises(requests.HTTPError, match="Token 无效"):
            api.get_user_info()


def test_gitee_failed_second_page_is_not_returned_as_complete_list():
    with GiteeAPI("secret-token") as api:
        api.session.request = Mock(
            side_effect=[response(200, [{}] * 100), response(503)]
        )
        with pytest.raises(requests.HTTPError):
            api.list_repos()
        assert api.session.request.call_count == 2


def test_gitee_stops_at_last_page_and_reuses_bounded_session():
    with GiteeAPI("secret-token") as api:
        api.session.request = Mock(
            return_value=response(200, [{"name": "last", "full_name": "alice/last"}])
        )
        assert len(api.list_repos()) == 1
        api.session.request.assert_called_once()
        assert api.session.request.call_args.kwargs["timeout"] == (5, 20)


def test_gitee_errors_never_include_token_url():
    with GiteeAPI("secret-token") as api:
        api.session.request = Mock(
            side_effect=requests.ConnectionError(
                "https://gitee.com?access_token=secret-token"
            )
        )
        with pytest.raises(requests.RequestException) as exc:
            api.get_user_info()
        assert "secret-token" not in str(exc.value)


def test_gitee_mutations_put_token_in_body():
    with GiteeAPI("secret-token") as api:
        api.session.request = Mock(return_value=response(204))
        assert api.delete_repo("alice", "sample") is True
        args = api.session.request.call_args.kwargs
        assert args["data"] == {"access_token": "secret-token"}
        assert "params" not in args
        assert args["timeout"] == (5, 20)


def test_management_rejects_repository_transferred_to_another_owner(github):
    github.client.get_repo.return_value.owner.login = "new-owner"
    with pytest.raises(ValueError, match="已转移"):
        github.delete_repo("alice/old-name")
    github.client.get_repo.return_value.delete.assert_not_called()
