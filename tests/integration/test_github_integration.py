"""Integration tests for GitHubAutomation using the real GitHub API.

These tests are skipped unless the following environment variables are set:
- GITHUB_TOKEN_INTEGRATION
- GITHUB_USERNAME_INTEGRATION

Each test creates a temporary private repository and deletes it afterward.
"""

from __future__ import annotations

import os
import uuid
from typing import Iterator

import pytest
import requests

from src.lms.integrations.github_automation import GitHubAutomation

REQUIRED_ENVS = ["GITHUB_TOKEN_INTEGRATION", "GITHUB_USERNAME_INTEGRATION"]

pytestmark = pytest.mark.skipif(
    any(os.getenv(env) is None for env in REQUIRED_ENVS),
    reason=(
        "Integration credentials not provided; set GITHUB_TOKEN_INTEGRATION "
        "and GITHUB_USERNAME_INTEGRATION"
    ),
)


@pytest.fixture()
def github_creds() -> tuple[str, str]:
    token = os.environ["GITHUB_TOKEN_INTEGRATION"]
    username = os.environ["GITHUB_USERNAME_INTEGRATION"]
    return token, username


def _delete_repo(token: str, username: str, repo_name: str) -> None:
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    # Ignore errors; repo may already be absent
    requests.delete(url, headers=headers, timeout=10)


@pytest.fixture()
def temp_repo_name() -> Iterator[str]:
    repo_name = f"skillops-integration-{uuid.uuid4().hex[:8]}"
    yield repo_name


def test_can_create_repository_and_receive_urls(
    github_creds: tuple[str, str], temp_repo_name: str
) -> None:
    """Creating a repo returns clone/ssh URLs."""
    token, username = github_creds
    automation = GitHubAutomation(token, username)

    repo_info = automation.create_remote_repository(
        temp_repo_name,
        description="SkillOps integration test",
        private=True,
    )

    try:
        assert repo_info is not None
        assert repo_info["html_url"].startswith("https://github.com/")
        assert repo_info["ssh_url"].startswith("git@github.com:")
    finally:
        _delete_repo(token, username, temp_repo_name)


def test_duplicate_repository_returns_none(
    github_creds: tuple[str, str], temp_repo_name: str
) -> None:
    """Creating the same repo twice should gracefully return None on the second attempt."""
    token, username = github_creds
    automation = GitHubAutomation(token, username)

    first = automation.create_remote_repository(temp_repo_name, private=True)
    try:
        assert first is not None
        second = automation.create_remote_repository(temp_repo_name, private=True)
        assert second is None
    finally:
        _delete_repo(token, username, temp_repo_name)


def test_private_flag_is_applied(
    github_creds: tuple[str, str], temp_repo_name: str
) -> None:
    """Repositories created with private=True should be marked private on GitHub."""
    token, username = github_creds
    automation = GitHubAutomation(token, username)

    repo_info = automation.create_remote_repository(
        temp_repo_name,
        description="SkillOps integration privacy check",
        private=True,
    )

    try:
        assert repo_info is not None
        repo_url = f"https://api.github.com/repos/{username}/{temp_repo_name}"
        response = requests.get(
            repo_url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("private") is True
    finally:
        _delete_repo(token, username, temp_repo_name)


def test_authenticated_user_matches_username(github_creds: tuple[str, str]) -> None:
    """Auth headers should resolve to the expected GitHub user."""
    token, username = github_creds
    response = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=10,
    )
    assert response.status_code == 200
    assert response.json().get("login") == username


def test_invalid_token_returns_none(temp_repo_name: str) -> None:
    """Invalid tokens must not create repositories and should return None."""
    invalid_token = "ghp_INVALID_TOKEN_FOR_TESTS"
    automation = GitHubAutomation(invalid_token, "invalid-user")
    result = automation.create_remote_repository(temp_repo_name, private=True)
    assert result is None
