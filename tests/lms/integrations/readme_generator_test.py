"""Tests for readme_generator module."""

from __future__ import annotations

from src.lms.integrations.readme_generator import ReadmeGenerator


def test_readme_generator_creation():
    """Test ReadmeGenerator initialization."""
    generator = ReadmeGenerator()
    assert generator is not None
    assert "project_name" in generator.template


def test_generate_tech_badges_empty():
    """Test badge generation with empty tech stack."""
    generator = ReadmeGenerator()
    badges = generator.generate_tech_badges([])
    assert "multiple technologies" in badges


def test_generate_tech_badges_python():
    """Test badge generation with Python."""
    generator = ReadmeGenerator()
    badges = generator.generate_tech_badges(["Python"])
    assert "Python" in badges
    assert "img.shields.io" in badges


def test_generate_tech_badges_multiple():
    """Test badge generation with multiple technologies."""
    generator = ReadmeGenerator()
    badges = generator.generate_tech_badges(["Python", "Docker", "Node.js"])
    assert "Python" in badges
    assert "Docker" in badges
    assert "Node.js" in badges


def test_generate_installation_python():
    """Test installation instructions for Python."""
    generator = ReadmeGenerator()
    instructions = generator.generate_installation_instructions(["Python"])
    assert "pip install" in instructions


def test_generate_installation_nodejs():
    """Test installation instructions for Node.js."""
    generator = ReadmeGenerator()
    instructions = generator.generate_installation_instructions(["Node.js"])
    assert "npm install" in instructions


def test_generate_installation_mixed():
    """Test installation instructions for mixed stack."""
    generator = ReadmeGenerator()
    instructions = generator.generate_installation_instructions(
        ["Python", "Node.js", "Docker"]
    )
    assert "pip install" in instructions
    assert "npm install" in instructions
    assert "docker build" in instructions


def test_generate_readme_content():
    """Test README content generation."""
    generator = ReadmeGenerator()
    content = generator.generate_readme_content(
        "my-project", "A cool project", ["Python"]
    )

    assert "my-project" in content
    assert "A cool project" in content
    assert "Python" in content
    assert "## Installation" in content
    assert "## Technologies" in content


def test_write_readme_success(tmp_path):
    """Test writing README file successfully."""
    generator = ReadmeGenerator()
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    success = generator.write_readme(
        str(project_dir),
        "test-project",
        "Test project description",
        ["Python", "Docker"],
    )

    assert success is True
    readme_file = project_dir / "README.md"
    assert readme_file.exists()

    content = readme_file.read_text()
    assert "test-project" in content
    assert "Test project description" in content
    assert "Python" in content
    assert "Docker" in content


def test_write_readme_invalid_path(tmp_path):
    """Test writing README to non-existent path."""
    generator = ReadmeGenerator()
    invalid_path = tmp_path / "nonexistent" / "project"

    success = generator.write_readme(
        str(invalid_path),
        "test-project",
        "Test description",
        ["Python"],
    )

    assert success is False
