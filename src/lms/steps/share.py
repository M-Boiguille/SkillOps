"""Share step for GitHub portfolio automation."""

from __future__ import annotations

import os
from typing import Optional

from rich.console import Console

from src.lms.integrations.github_automation import GitHubAutomation
from src.lms.integrations.github_detector import LabProjectDetector
from src.lms.integrations.readme_generator import ReadmeGenerator

console = Console()


def share_step(
    labs_path: Optional[str] = None,
    github_token: Optional[str] = None,
    github_username: Optional[str] = None,
) -> bool:
    """Share lab projects to GitHub with automatic README generation.

    Detects new projects without remotes, generates READMEs, and pushes
    repositories to GitHub.

    Args:
        labs_path: Path to labs directory. Defaults to ~/labs
        github_token: GitHub personal access token. Defaults to GITHUB_TOKEN env var
        github_username: GitHub username. Defaults to GITHUB_USERNAME env var

    Returns:
        True if successful, False otherwise.
    """
    # Get configuration from environment or parameters
    if github_token is None:
        github_token = os.getenv("GITHUB_TOKEN")
    if github_username is None:
        github_username = os.getenv("GITHUB_USERNAME")
    if labs_path is None:
        labs_path = os.getenv("LABS_PATH")

    # Validate required configuration
    if not github_token:
        console.print(
            "[red]Error: GITHUB_TOKEN not set. Set via env var or parameter.[/red]"
        )
        return False

    if not github_username:
        console.print(
            "[red]Error: GITHUB_USERNAME not set. Set via env var or parameter.[/red]"
        )
        return False

    try:
        # Initialize detectors and generators
        detector = LabProjectDetector(labs_path)
        generator = ReadmeGenerator()
        automation = GitHubAutomation(github_token, github_username)

        # Scan for new projects
        projects = detector.scan_labs_directory()
        console.print(f"[cyan]Found {len(projects)} projects[/cyan]")

        shared_count = 0
        for project_path in projects:
            if not detector.is_new_project(project_path):
                console.print(f"[dim]{project_path.name}: Already has remote[/dim]")
                continue

            console.print(f"[cyan]Processing: {project_path.name}[/cyan]")

            # Get project metadata
            metadata = detector.get_project_metadata(project_path)

            # Generate README
            readme_success = generator.write_readme(
                project_path,
                metadata["name"],
                metadata["description"],
                metadata["tech_stack"],
            )

            if not readme_success:
                msg = "[yellow]Failed to generate README[/yellow]"
                console.print(msg)
                continue

            # Initialize git repository
            if not automation.init_repository(project_path):
                msg = "[yellow]Failed to initialize git[/yellow]"
                console.print(msg)
                continue

            # Create commit
            if not automation.create_commit(project_path, "Initial commit"):
                msg = "[yellow]Failed to create commit[/yellow]"
                console.print(msg)
                continue

            # Create GitHub repository
            repo_info = automation.create_remote_repository(
                metadata["name"],
                metadata["description"],
                private=False,
            )

            if not repo_info:
                msg = "[yellow]Failed to create GitHub repository[/yellow]"
                console.print(msg)
                continue

            # Push to GitHub
            if not automation.push_to_github(project_path, repo_info["clone_url"]):
                msg = "[yellow]Failed to push to GitHub[/yellow]"
                console.print(msg)
                continue

            # Get commit hash
            commit_hash = automation.get_current_commit(project_path)

            console.print(
                f"[green]✓ {project_path.name}[/green]: " f"{repo_info['html_url']}"
            )

            if commit_hash:
                console.print(f"  [dim]Commit: {commit_hash[:7]}[/dim]")

            shared_count += 1

        console.print(f"[green]Shared {shared_count}/{len(projects)} projects[/green]")
        return True

    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        return False
