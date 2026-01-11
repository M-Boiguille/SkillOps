"""Tests for github_automation module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.lms.integrations.github_automation import GitHubAutomation


def test_github_automation_creation():
    """Test GitHubAutomation initialization."""
    automation = GitHubAutomation("test_token", "test_user")
    assert automation.github_token == "test_token"
    assert automation.github_username == "test_user"
    assert "token test_token" in automation.headers["Authorization"]


def test_init_repository_success(tmp_path):
    """Test successful repository initialization."""
    automation = GitHubAutomation("token", "user")
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    success = automation.init_repository(str(project_dir))
    assert success is True
    assert (project_dir / ".git").exists()


def test_init_repository_already_exists(tmp_path):
    """Test initialization when .git already exists."""
    automation = GitHubAutomation("token", "user")
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()

    success = automation.init_repository(str(project_dir))
    assert success is True


def test_init_repository_invalid_path():
    """Test initialization with invalid path."""
    automation = GitHubAutomation("token", "user")
    success = automation.init_repository("/nonexistent/path")
    assert success is False


def test_create_commit_success(tmp_path):
    """Test successful commit creation."""
    automation = GitHubAutomation("token", "user")
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Initialize repo first
    automation.init_repository(str(project_dir))

    # Create a test file
    test_file = project_dir / "test.txt"
    test_file.write_text("test content")

    # Configure git user
    from subprocess import run

    run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(project_dir),
        capture_output=True,
    )
    run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(project_dir),
        capture_output=True,
    )

    success = automation.create_commit(str(project_dir), "Test commit")
    assert success is True


@patch("src.lms.integrations.github_automation.requests.post")
def test_create_remote_repository_success(mock_post):
    """Test successful remote repository creation."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "html_url": "https://github.com/test_user/test_repo",
        "clone_url": "https://github.com/test_user/test_repo.git",
        "ssh_url": "git@github.com:test_user/test_repo.git",
    }
    mock_post.return_value = mock_response

    automation = GitHubAutomation("token", "test_user")
    result = automation.create_remote_repository("test_repo", "A test repo")

    assert result is not None
    assert result["html_url"] == "https://github.com/test_user/test_repo"
    assert result["clone_url"] == "https://github.com/test_user/test_repo.git"
    mock_post.assert_called_once()


@patch("src.lms.integrations.github_automation.requests.post")
def test_create_remote_repository_failure(mock_post):
    """Test failed remote repository creation."""
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.text = ""
    mock_post.return_value = mock_response

    automation = GitHubAutomation("token", "test_user")
    result = automation.create_remote_repository("test_repo")

    assert result is None


@patch("src.lms.integrations.github_automation.requests.post")
def test_create_remote_repository_with_description(mock_post):
    """Test repository creation with description."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "html_url": "https://github.com/test_user/test_repo",
        "clone_url": "https://github.com/test_user/test_repo.git",
        "ssh_url": "git@github.com:test_user/test_repo.git",
    }
    mock_post.return_value = mock_response

    automation = GitHubAutomation("token", "test_user")
    automation.create_remote_repository("test_repo", "Test repository", private=True)

    # Check that the post request was made with correct payload
    call_args = mock_post.call_args
    payload = call_args[1]["json"]
    assert payload["name"] == "test_repo"
    assert payload["description"] == "Test repository"
    assert payload["private"] is True


def test_get_current_commit_success(tmp_path):
    """Test getting current commit hash."""
    automation = GitHubAutomation("token", "user")
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Initialize repo and create commit
    automation.init_repository(str(project_dir))

    # Configure git user
    from subprocess import run

    run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(project_dir),
        capture_output=True,
    )
    run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(project_dir),
        capture_output=True,
    )

    # Create test file and commit
    test_file = project_dir / "test.txt"
    test_file.write_text("test")

    automation.create_commit(str(project_dir), "Initial commit")

    # Get commit hash
    commit_hash = automation.get_current_commit(str(project_dir))

    assert commit_hash is not None
    assert len(commit_hash) == 40  # SHA-1 hash is 40 chars


def test_get_current_commit_invalid_path():
    """Test getting commit from invalid path."""
    automation = GitHubAutomation("token", "user")
    commit = automation.get_current_commit("/nonexistent/path")
    assert commit is None
