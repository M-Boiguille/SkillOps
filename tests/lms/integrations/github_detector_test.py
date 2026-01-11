"""Tests for github_detector module."""

from __future__ import annotations

import pytest

from src.lms.integrations.github_detector import LabProjectDetector


def test_lab_project_detector_creation(tmp_path):
    """Test LabProjectDetector initialization with valid path."""
    detector = LabProjectDetector(str(tmp_path))
    assert detector.labs_path == tmp_path


def test_lab_project_detector_invalid_path():
    """Test LabProjectDetector raises error for non-existent path."""
    with pytest.raises(ValueError, match="Labs path does not exist"):
        LabProjectDetector("/nonexistent/path/12345")


def test_lab_project_detector_not_directory(tmp_path):
    """Test LabProjectDetector raises error if path is not a directory."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")

    with pytest.raises(ValueError, match="Labs path is not a directory"):
        LabProjectDetector(str(file_path))


def test_scan_empty_labs_directory(tmp_path):
    """Test scanning empty labs directory."""
    detector = LabProjectDetector(str(tmp_path))
    projects = detector.scan_labs_directory()
    assert projects == []


def test_scan_labs_directory_with_projects(tmp_path):
    """Test scanning labs directory with projects."""
    (tmp_path / "project1").mkdir()
    (tmp_path / "project2").mkdir()
    (tmp_path / ".hidden").mkdir()

    detector = LabProjectDetector(str(tmp_path))
    projects = detector.scan_labs_directory()

    assert len(projects) == 2
    assert (tmp_path / "project1") in projects
    assert (tmp_path / "project2") in projects
    assert (tmp_path / ".hidden") not in projects


def test_is_new_project_no_git(tmp_path):
    """Test project detection for directory without .git."""
    project = tmp_path / "project"
    project.mkdir()

    detector = LabProjectDetector(str(tmp_path))
    assert detector.is_new_project(project) is True


def test_get_project_metadata_basic(tmp_path):
    """Test extracting metadata from project."""
    project = tmp_path / "my_project"
    project.mkdir()

    detector = LabProjectDetector(str(tmp_path))
    metadata = detector.get_project_metadata(project)

    assert metadata["name"] == "my_project"
    assert metadata["path"] == str(project)
    assert metadata["tech_stack"] == []
    assert "Lab project" in metadata["description"]


def test_get_project_metadata_with_tech_stack(tmp_path):
    """Test metadata extraction with technology detection."""
    project = tmp_path / "full_project"
    project.mkdir()
    (project / "package.json").touch()
    (project / "requirements.txt").touch()
    (project / "Dockerfile").touch()

    detector = LabProjectDetector(str(tmp_path))
    metadata = detector.get_project_metadata(project)

    assert "Node.js" in metadata["tech_stack"]
    assert "Python" in metadata["tech_stack"]
    assert "Docker" in metadata["tech_stack"]
