"""Tests for share step."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.lms.steps.share import share_step


@patch("src.lms.steps.share.GitHubAutomation")
@patch("src.lms.steps.share.ReadmeGenerator")
@patch("src.lms.steps.share.LabProjectDetector")
def test_share_step_no_projects(mock_detector, mock_generator, mock_automation):
    """Test share step with no projects found."""
    mock_detector_instance = MagicMock()
    mock_detector_instance.scan_labs_directory.return_value = []
    mock_detector.return_value = mock_detector_instance

    success = share_step(
        labs_path="/tmp/labs",
        github_token="test_token",
        github_username="test_user",
    )

    assert success is True


@patch.dict("os.environ", {})
def test_share_step_missing_github_token():
    """Test share step fails without GitHub token."""
    success = share_step(
        labs_path="/tmp/labs",
        github_username="test_user",
    )

    assert success is False


@patch.dict("os.environ", {})
def test_share_step_missing_github_username():
    """Test share step fails without GitHub username."""
    success = share_step(
        labs_path="/tmp/labs",
        github_token="test_token",
    )

    assert success is False


@patch("src.lms.steps.share.GitHubAutomation")
@patch("src.lms.steps.share.ReadmeGenerator")
@patch("src.lms.steps.share.LabProjectDetector")
def test_share_step_with_new_project(mock_detector, mock_generator, mock_automation):
    """Test share step successfully processes new project."""
    # Setup detector
    project_path = Path("/tmp/labs/test_project")
    mock_detector_instance = MagicMock()
    mock_detector_instance.scan_labs_directory.return_value = [project_path]
    mock_detector_instance.is_new_project.return_value = True
    mock_detector_instance.get_project_metadata.return_value = {
        "name": "test_project",
        "description": "Test project",
        "tech_stack": ["Python"],
    }
    mock_detector.return_value = mock_detector_instance

    # Setup generator
    mock_generator_instance = MagicMock()
    mock_generator_instance.write_readme.return_value = True
    mock_generator.return_value = mock_generator_instance

    # Setup automation
    mock_automation_instance = MagicMock()
    mock_automation_instance.repository_exists.return_value = False
    mock_automation_instance.init_repository.return_value = True
    mock_automation_instance.create_commit.return_value = True
    mock_automation_instance.create_remote_repository.return_value = {
        "html_url": "https://github.com/test_user/test_project",
        "clone_url": "https://github.com/test_user/test_project.git",
    }
    mock_automation_instance.push_to_github.return_value = True
    mock_automation_instance.get_current_commit.return_value = "abc123def456"
    mock_automation.return_value = mock_automation_instance

    success = share_step(
        labs_path="/tmp/labs",
        github_token="test_token",
        github_username="test_user",
    )

    assert success is True
    mock_generator_instance.write_readme.assert_called_once()
    mock_automation_instance.init_repository.assert_called_once()
    mock_automation_instance.push_to_github.assert_called_once()


@patch("src.lms.steps.share.GitHubAutomation")
@patch("src.lms.steps.share.ReadmeGenerator")
@patch("src.lms.steps.share.LabProjectDetector")
def test_share_step_skips_existing_project(
    mock_detector, mock_generator, mock_automation
):
    """Test share step skips projects with existing remotes."""
    project_path = Path("/tmp/labs/test_project")
    mock_detector_instance = MagicMock()
    mock_detector_instance.scan_labs_directory.return_value = [project_path]
    mock_detector_instance.is_new_project.return_value = False
    mock_detector.return_value = mock_detector_instance

    success = share_step(
        labs_path="/tmp/labs",
        github_token="test_token",
        github_username="test_user",
    )

    # Should return True because no errors occurred
    assert success is True


@patch("src.lms.steps.share.GitHubAutomation")
@patch("src.lms.steps.share.ReadmeGenerator")
@patch("src.lms.steps.share.LabProjectDetector")
def test_share_step_skips_existing_remote(
    mock_detector, mock_generator, mock_automation
):
    """Share step should be idempotent when repository already exists."""
    project_path = Path("/tmp/labs/test_project")
    mock_detector_instance = MagicMock()
    mock_detector_instance.scan_labs_directory.return_value = [project_path]
    mock_detector_instance.is_new_project.return_value = True
    mock_detector_instance.get_project_metadata.return_value = {
        "name": "test_project",
        "description": "Test",
        "tech_stack": [],
    }
    mock_detector.return_value = mock_detector_instance

    mock_generator_instance = MagicMock()
    mock_generator_instance.write_readme.return_value = True
    mock_generator.return_value = mock_generator_instance

    mock_automation_instance = MagicMock()
    mock_automation_instance.repository_exists.return_value = True
    mock_automation.return_value = mock_automation_instance

    success = share_step(
        labs_path="/tmp/labs",
        github_token="test_token",
        github_username="test_user",
    )

    assert success is True
    mock_automation_instance.create_remote_repository.assert_not_called()
    mock_automation_instance.push_to_github.assert_not_called()


@patch("src.lms.steps.share.GitHubAutomation")
@patch("src.lms.steps.share.ReadmeGenerator")
@patch("src.lms.steps.share.LabProjectDetector")
def test_share_step_handles_readme_failure(
    mock_detector, mock_generator, mock_automation
):
    """Test share step handles README generation failure."""
    project_path = Path("/tmp/labs/test_project")
    mock_detector_instance = MagicMock()
    mock_detector_instance.scan_labs_directory.return_value = [project_path]
    mock_detector_instance.is_new_project.return_value = True
    mock_detector_instance.get_project_metadata.return_value = {
        "name": "test_project",
        "description": "Test",
        "tech_stack": [],
    }
    mock_detector.return_value = mock_detector_instance

    # Generator fails
    mock_generator_instance = MagicMock()
    mock_generator_instance.write_readme.return_value = False
    mock_generator.return_value = mock_generator_instance

    success = share_step(
        labs_path="/tmp/labs",
        github_token="test_token",
        github_username="test_user",
    )

    # Should return True because no critical error (just skipped project)
    assert success is True


@patch("src.lms.steps.share.LabProjectDetector")
def test_share_step_handles_detector_error(mock_detector):
    """Test share step handles detector initialization error."""
    mock_detector.side_effect = ValueError("Invalid path")

    success = share_step(
        labs_path="/invalid/path",
        github_token="test_token",
        github_username="test_user",
    )

    assert success is False


@patch.dict(
    "os.environ",
    {
        "GITHUB_TOKEN": "env_token",
        "GITHUB_USERNAME": "env_user",
        "LABS_PATH": "/env/labs",
    },
)
@patch("src.lms.steps.share.GitHubAutomation")
@patch("src.lms.steps.share.ReadmeGenerator")
@patch("src.lms.steps.share.LabProjectDetector")
def test_share_step_uses_env_variables(mock_detector, mock_generator, mock_automation):
    """Test share step uses environment variables."""
    mock_detector_instance = MagicMock()
    mock_detector_instance.scan_labs_directory.return_value = []
    mock_detector.return_value = mock_detector_instance

    share_step()  # Call without parameters

    # Verify environment variables were used
    mock_detector.assert_called_once_with("/env/labs")
