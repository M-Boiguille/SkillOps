"""README generation for GitHub portfolio projects."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


class ReadmeGenerator:
    """Generate README.md files for lab projects."""

    def __init__(self):
        self.template = """# {project_name}

> {description}

## Overview

This is a lab project demonstrating {tech_stack_text}.

## Technologies

{tech_badges}

## Installation

{installation_instructions}

## Usage

```bash
# Add your usage instructions here
```

## Project Structure

```
{project_name}/
├── src/              # Source code
├── tests/            # Test files
├── README.md         # This file
└── .gitignore        # Git ignore rules
```

## Contributing

This is a personal lab project. Feel free to fork and adapt as needed.

## License

MIT License - See LICENSE file for details
"""

    def generate_tech_badges(self, tech_stack: list[str]) -> str:
        """Generate markdown badges for technologies.

        Args:
            tech_stack: List of technology names.

        Returns:
            Markdown text with badges.
        """
        if not tech_stack:
            return "- Project uses multiple technologies"

        badge_map = {
            "Python": (
                "![Python](https://img.shields.io/badge/python-3670A0?"
                "style=flat-square&logo=python&logoColor=ffdd54)"
            ),
            "Node.js": (
                "![Node.js](https://img.shields.io/badge/node.js-339933?"
                "style=flat-square&logo=node.js&logoColor=white)"
            ),
            "Go": (
                "![Go](https://img.shields.io/badge/go-00ADD8?"
                "style=flat-square&logo=go&logoColor=white)"
            ),
            "Docker": (
                "![Docker](https://img.shields.io/badge/docker-2496ED?"
                "style=flat-square&logo=docker&logoColor=white)"
            ),
            "Make": (
                "![Make](https://img.shields.io/badge/make-427819?" "style=flat-square)"
            ),
            "Docker Compose": (
                "![Docker Compose](https://img.shields.io/badge/"
                "docker--compose-2496ED?style=flat-square&logo=docker"
                "&logoColor=white)"
            ),
            "Terraform": (
                "![Terraform](https://img.shields.io/badge/terraform-7B42BC?"
                "style=flat-square&logo=terraform&logoColor=white)"
            ),
        }

        badges = []
        for tech in tech_stack:
            if tech in badge_map:
                badges.append(badge_map[tech])

        return "\n".join(f"- {badge}" for badge in badges) if badges else ""

    def generate_installation_instructions(self, tech_stack: list[str]) -> str:
        """Generate installation instructions based on tech stack.

        Args:
            tech_stack: List of technology names.

        Returns:
            Markdown text with installation instructions.
        """
        instructions = []

        if "Node.js" in tech_stack:
            instructions.append("```bash\nnpm install\n```")

        if "Python" in tech_stack:
            instructions.append("```bash\npip install -r requirements.txt\n```")

        if "Docker" in tech_stack:
            instructions.append("```bash\ndocker build -t project-name .\n```")

        if not instructions:
            instructions.append("```bash\n# Installation instructions\n```")

        return "\n\n".join(instructions)

    def generate_readme_content(
        self,
        project_name: str,
        description: str,
        tech_stack: list[str],
    ) -> str:
        """Generate complete README content.

        Args:
            project_name: Name of the project.
            description: Project description.
            tech_stack: List of technologies used.

        Returns:
            Complete README markdown content.
        """
        tech_stack_text = (
            ", ".join(tech_stack) if tech_stack else "various technologies"
        )
        tech_badges = self.generate_tech_badges(tech_stack)
        installation = self.generate_installation_instructions(tech_stack)

        content = self.template.format(
            project_name=project_name,
            description=description,
            tech_stack_text=tech_stack_text,
            tech_badges=tech_badges,
            installation_instructions=installation,
            project_name_lower=project_name.lower(),
        )

        return content

    def write_readme(
        self,
        project_path: str | Path,
        project_name: str,
        description: str,
        tech_stack: list[str],
    ) -> bool:
        """Write README file to project directory.

        Args:
            project_path: Path to project directory.
            project_name: Name of the project.
            description: Project description.
            tech_stack: List of technologies used.

        Returns:
            True if successful, False otherwise.
        """
        try:
            project_path = Path(project_path).expanduser().absolute()
            if not project_path.is_dir():
                console.print(f"[red]Project path not found: {project_path}[/red]")
                return False

            content = self.generate_readme_content(
                project_name, description, tech_stack
            )

            readme_path = project_path / "README.md"
            readme_path.write_text(content)

            return True
        except OSError as e:
            console.print(f"[red]Error writing README: {e}[/red]")
            return False
