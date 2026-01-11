"""GitHub automation for repository creation and management."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console

console = Console()


class GitHubAutomation:
    """Handle GitHub repository creation and git operations."""

    def __init__(self, github_token: str, github_username: str):
        self.github_token = github_token
        self.github_username = github_username
        self.github_api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def init_repository(self, project_path: str | Path) -> bool:
        """Initialize git repository in project directory.

        Args:
            project_path: Path to project directory.

        Returns:
            True if successful, False otherwise.
        """
        try:
            project_path = Path(project_path).expanduser().absolute()
            if not project_path.is_dir():
                console.print(f"[red]Project directory not found: {project_path}[/red]")
                return False

            git_dir = project_path / ".git"
            if git_dir.exists():
                return True

            result = subprocess.run(
                ["git", "init"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.returncode == 0
        except (subprocess.SubprocessError, OSError) as e:
            console.print(f"[red]Error initializing repository: {e}[/red]")
            return False

    def create_commit(
        self,
        project_path: str | Path,
        message: str = "Initial commit",
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
    ) -> bool:
        """Create a git commit with all changes.

        Args:
            project_path: Path to project directory.
            message: Commit message.
            author_name: Author name for commit.
            author_email: Author email for commit.

        Returns:
            True if successful, False otherwise.
        """
        try:
            project_path = Path(project_path).expanduser().absolute()

            # Add all files
            result = subprocess.run(
                ["git", "add", "."],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return False

            # Create commit
            commit_cmd = ["git", "commit", "-m", message]

            if author_name and author_email:
                commit_cmd.extend(["--author", f"{author_name} <{author_email}>"])

            result = subprocess.run(
                commit_cmd,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.returncode == 0
        except (subprocess.SubprocessError, OSError) as e:
            console.print(f"[red]Error creating commit: {e}[/red]")
            return False

    def create_remote_repository(
        self,
        repo_name: str,
        description: str = "",
        private: bool = False,
    ) -> Optional[dict]:
        """Create a new repository on GitHub.

        Args:
            repo_name: Name of repository.
            description: Repository description.
            private: Whether repository should be private.

        Returns:
            Repository info dict with 'html_url' and 'clone_url' if successful,
            None otherwise.
        """
        try:
            payload = {
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": False,
            }

            response = requests.post(
                f"{self.github_api_base}/user/repos",
                json=payload,
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 201:
                data = response.json()
                return {
                    "html_url": data["html_url"],
                    "clone_url": data["clone_url"],
                    "ssh_url": data["ssh_url"],
                }

            console.print(
                f"[red]Failed to create repository: {response.status_code}[/red]"
            )
            if response.text:
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        console.print(f"[red]{error_data['message']}[/red]")
                except json.JSONDecodeError:
                    pass

            return None
        except requests.RequestException as e:
            console.print(f"[red]Error creating repository: {e}[/red]")
            return None

    def push_to_github(
        self,
        project_path: str | Path,
        repo_url: str,
        branch: str = "main",
    ) -> bool:
        """Push repository to GitHub.

        Args:
            project_path: Path to project directory.
            repo_url: HTTPS URL of GitHub repository.
            branch: Branch name (default: main).

        Returns:
            True if successful, False otherwise.
        """
        try:
            project_path = Path(project_path).expanduser().absolute()

            # Add remote
            result = subprocess.run(
                ["git", "remote", "add", "origin", repo_url],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                # Remote might already exist, try to update it
                subprocess.run(
                    ["git", "remote", "set-url", "origin", repo_url],
                    cwd=str(project_path),
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            # Push to GitHub
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            return result.returncode == 0
        except (subprocess.SubprocessError, OSError) as e:
            console.print(f"[red]Error pushing to GitHub: {e}[/red]")
            return False

    def get_current_commit(self, project_path: str | Path) -> Optional[str]:
        """Get current commit hash.

        Args:
            project_path: Path to project directory.

        Returns:
            Commit hash if successful, None otherwise.
        """
        try:
            project_path = Path(project_path).expanduser().absolute()

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.SubprocessError, OSError):
            return None
