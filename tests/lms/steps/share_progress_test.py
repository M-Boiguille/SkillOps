"""Tests for progress tracking in share_step."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.lms.steps.share import share_step


class TestShareStepProgressTracking:
    """Test progress bar and feedback during share operations."""

    def test_share_step_shows_progress_with_multiple_projects(self) -> None:
        """Test that progress is tracked across multiple projects."""
        with patch(
            "src.lms.steps.share.LabProjectDetector"
        ) as mock_detector_class, patch(
            "src.lms.steps.share.ReadmeGenerator"
        ) as mock_generator_class, patch(
            "src.lms.steps.share.GitHubAutomation"
        ) as mock_automation_class, patch(
            "src.lms.steps.share.Progress"
        ) as mock_progress_class:
            # Setup mocks
            mock_detector = MagicMock()
            mock_generator = MagicMock()
            mock_automation = MagicMock()
            mock_progress = MagicMock()

            mock_detector_class.return_value = mock_detector
            mock_generator_class.return_value = mock_generator
            mock_automation_class.return_value = mock_automation
            mock_progress_class.return_value.__enter__.return_value = mock_progress

            # Create 3 test projects
            projects = [MagicMock(spec=Path) for _ in range(3)]
            projects[0].name = "project1"
            projects[1].name = "project2"
            projects[2].name = "project3"

            mock_detector.scan_labs_directory.return_value = projects
            mock_detector.is_new_project.return_value = True

            mock_detector.get_project_metadata.return_value = {
                "name": "test-project",
                "description": "Test project",
                "tech_stack": ["Python"],
            }

            mock_generator.write_readme.return_value = True
            mock_automation.init_repository.return_value = True
            mock_automation.create_commit.return_value = True
            mock_automation.create_remote_repository.return_value = {
                "html_url": "https://github.com/user/test",
                "clone_url": "https://github.com/user/test.git",
            }
            mock_automation.push_to_github.return_value = True
            mock_automation.get_current_commit.return_value = "abc1234"

            # Mock progress bar methods
            mock_progress.add_task.return_value = 0
            mock_progress.update.return_value = None
            mock_progress.advance.return_value = None

            # Call function with test environment
            with patch.dict(
                "os.environ",
                {
                    "GITHUB_TOKEN": "test_token",
                    "GITHUB_USERNAME": "testuser",
                    "LABS_PATH": "/labs",
                },
            ):
                result = share_step()

            assert result is True
            # Verify progress bar was created
            assert mock_progress.add_task.called
            # Verify progress updates were made for each project
            assert mock_progress.update.call_count > 0
            # Verify progress advances were made
            assert mock_progress.advance.call_count > 0

    def test_share_step_progress_with_failed_operations(self) -> None:
        """Test progress continues despite failed operations."""
        with patch(
            "src.lms.steps.share.LabProjectDetector"
        ) as mock_detector_class, patch(
            "src.lms.steps.share.ReadmeGenerator"
        ) as mock_generator_class, patch(
            "src.lms.steps.share.GitHubAutomation"
        ) as mock_automation_class, patch(
            "src.lms.steps.share.Progress"
        ) as mock_progress_class:
            # Setup mocks
            mock_detector = MagicMock()
            mock_generator = MagicMock()
            mock_automation = MagicMock()
            mock_progress = MagicMock()

            mock_detector_class.return_value = mock_detector
            mock_generator_class.return_value = mock_generator
            mock_automation_class.return_value = mock_automation
            mock_progress_class.return_value.__enter__.return_value = mock_progress

            # Create 2 projects: first succeeds, second fails
            projects = [MagicMock(spec=Path), MagicMock(spec=Path)]
            projects[0].name = "success"
            projects[1].name = "fail"

            mock_detector.scan_labs_directory.return_value = projects
            mock_detector.is_new_project.return_value = True

            # First project succeeds
            metadata_responses = [
                {"name": "success", "description": "Works", "tech_stack": ["Python"]},
                {"name": "fail", "description": "Fails", "tech_stack": ["Python"]},
            ]
            mock_detector.get_project_metadata.side_effect = metadata_responses

            # First succeeds, second readme fails
            mock_generator.write_readme.side_effect = [True, False]

            mock_automation.init_repository.return_value = True
            mock_automation.create_commit.return_value = True
            mock_automation.create_remote_repository.return_value = {
                "html_url": "https://github.com/user/test",
                "clone_url": "https://github.com/user/test.git",
            }
            mock_automation.push_to_github.return_value = True
            mock_automation.get_current_commit.return_value = "abc1234"

            # Mock progress bar methods
            mock_progress.add_task.return_value = 0
            mock_progress.update.return_value = None
            mock_progress.advance.return_value = None

            # Call function
            with patch.dict(
                "os.environ",
                {
                    "GITHUB_TOKEN": "test_token",
                    "GITHUB_USERNAME": "testuser",
                    "LABS_PATH": "/labs",
                },
            ):
                result = share_step()

            # Should continue processing despite failure
            assert result is True
            # Should advance progress for each project (at least 2 times)
            assert mock_progress.advance.call_count >= 2

    def test_share_step_progress_with_no_new_projects(self) -> None:
        """Test progress handling when no new projects found."""
        with patch(
            "src.lms.steps.share.LabProjectDetector"
        ) as mock_detector_class, patch(
            "src.lms.steps.share.ReadmeGenerator"
        ) as mock_generator_class, patch(
            "src.lms.steps.share.GitHubAutomation"
        ) as mock_automation_class:
            # Setup mocks
            mock_detector = MagicMock()
            mock_generator = MagicMock()
            mock_automation = MagicMock()

            mock_detector_class.return_value = mock_detector
            mock_generator_class.return_value = mock_generator
            mock_automation_class.return_value = mock_automation

            # All projects already have remotes
            projects = [MagicMock(spec=Path)]
            projects[0].name = "existing"

            mock_detector.scan_labs_directory.return_value = projects
            mock_detector.is_new_project.return_value = False

            # Call function
            with patch.dict(
                "os.environ",
                {
                    "GITHUB_TOKEN": "test_token",
                    "GITHUB_USERNAME": "testuser",
                    "LABS_PATH": "/labs",
                },
            ):
                result = share_step()

            assert result is True
