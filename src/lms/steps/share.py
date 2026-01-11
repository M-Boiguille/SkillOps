"""Share step for GitHub portfolio automation."""

from __future__ import annotations

import os
from typing import Optional

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)

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
    repositories to GitHub. Shows progress bars for long operations.

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

        # Filter to only new projects
        new_projects = [p for p in projects if detector.is_new_project(p)]

        if not new_projects:
            console.print("[dim]All projects already have remotes[/dim]")
            return True

        shared_count = 0

        # Progress bar for overall task
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task_id = progress.add_task(
                "[cyan]Sharing projects to GitHub...", total=len(new_projects)
            )

            for project_path in new_projects:
                progress.update(
                    task_id, description=f"[cyan]Processing: {project_path.name}[/cyan]"
                )

                try:
                    # Get project metadata
                    metadata = detector.get_project_metadata(project_path)

                    # Generate README
                    progress.update(
                        task_id,
                        description=f"[cyan]{project_path.name}: Generating README...[/cyan]",
                    )
                    readme_success = generator.write_readme(
                        project_path,
                        metadata["name"],
                        metadata["description"],
                        metadata["tech_stack"],
                    )

                    if not readme_success:
                        console.print("  [yellow]✗ Failed to generate README[/yellow]")
                        progress.advance(task_id)
                        continue

                    # Initialize git repository
                    progress.update(
                        task_id,
                        description=f"[cyan]{project_path.name}: Initializing git...[/cyan]",
                    )
                    if not automation.init_repository(project_path):
                        console.print("  [yellow]✗ Failed to initialize git[/yellow]")
                        progress.advance(task_id)
                        continue

                    # Create commit
                    progress.update(
                        task_id,
                        description=f"[cyan]{project_path.name}: Creating commit...[/cyan]",
                    )
                    if not automation.create_commit(project_path, "Initial commit"):
                        console.print("  [yellow]✗ Failed to create commit[/yellow]")
                        progress.advance(task_id)
                        continue

                    # Create GitHub repository
                    progress.update(
                        task_id,
                        description=f"[cyan]{project_path.name}: Creating GitHub repo...[/cyan]",
                    )
                    repo_info = automation.create_remote_repository(
                        metadata["name"],
                        metadata["description"],
                        private=False,
                    )

                    if not repo_info:
                        console.print(
                            "  [yellow]✗ Failed to create GitHub repository[/yellow]"
                        )
                        progress.advance(task_id)
                        continue

                    # Push to GitHub
                    progress.update(
                        task_id,
                        description=f"[cyan]{project_path.name}: Pushing to GitHub...[/cyan]",
                    )
                    if not automation.push_to_github(
                        project_path, repo_info["clone_url"]
                    ):
                        console.print("  [yellow]✗ Failed to push to GitHub[/yellow]")
                        progress.advance(task_id)
                        continue

                    # Get commit hash
                    commit_hash = automation.get_current_commit(project_path)

                    console.print(
                        f"[green]✓ {project_path.name}[/green]: {repo_info['html_url']}"
                    )

                    if commit_hash:
                        console.print(f"  [dim]Commit: {commit_hash[:7]}[/dim]")

                    shared_count += 1

                except (ValueError, OSError) as e:
                    console.print(f"  [yellow]✗ Error: {e}[/yellow]")

                finally:
                    progress.advance(task_id)

        console.print(
            f"[green]✓ Successfully shared {shared_count}/{len(new_projects)} projects[/green]"
        )
        return True

    except (ValueError, OSError) as e:
        console.print(f"[red]Error: {e}[/red]")
        return False
