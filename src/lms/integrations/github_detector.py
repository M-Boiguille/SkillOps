"""GitHub portfolio automation utilities."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class LabProjectDetector:
    """Detect and analyze lab projects in a directory."""

    def __init__(self, labs_path: Optional[str] = None):
        if not labs_path:
            labs_path = str(Path.home() / "labs")
        self.labs_path = Path(labs_path).expanduser().absolute()
        if not self.labs_path.exists():
            raise ValueError(f"Labs path does not exist: {self.labs_path}")
        if not self.labs_path.is_dir():
            raise ValueError(f"Labs path is not a directory: {self.labs_path}")

    def scan_labs_directory(self) -> list[Path]:
        """Scan labs directory for projects (subdirectories with code).

        Returns:
            List of project directories.
        """
        projects = []
        for item in self.labs_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                projects.append(item)
        return sorted(projects)

    def is_new_project(self, project_path: Path) -> bool:
        """Check if project is new (no git remote configured).

        Args:
            project_path: Path to project directory.

        Returns:
            True if project has no remote, False otherwise.
        """
        if not (project_path / ".git").exists():
            return True

        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return not result.stdout.strip()
        except (subprocess.SubprocessError, OSError):
            return True

    def get_project_metadata(self, project_path: Path) -> dict:
        """Extract metadata from a project.

        Args:
            project_path: Path to project directory.

        Returns:
            Dictionary with name, tech_stack, description.
        """
        name = project_path.name
        description = f"Lab project: {name}"

        # Detect tech stack from common files
        tech_stack = []
        if (project_path / "package.json").exists():
            tech_stack.append("Node.js")
        if (project_path / "requirements.txt").exists() or (
            project_path / "setup.py"
        ).exists():
            tech_stack.append("Python")
        if (project_path / "Dockerfile").exists():
            tech_stack.append("Docker")
        if (project_path / "Makefile").exists():
            tech_stack.append("Make")
        if (project_path / "docker-compose.yml").exists() or (
            project_path / "docker-compose.yaml"
        ).exists():
            tech_stack.append("Docker Compose")
        if (project_path / "terraform").exists() or (project_path / "*.tf").exists():
            tech_stack.append("Terraform")

        return {
            "name": name,
            "path": str(project_path),
            "tech_stack": tech_stack,
            "description": description,
        }
