"""Main entry point for SkillOps LMS CLI application."""

import typer
from lms.cli import main_menu, execute_step

app = typer.Typer(
    name="skillops",
    help="SkillOps - Your Daily Learning Management System",
    add_completion=False,
)


@app.command()
def start():
    """Start the interactive SkillOps LMS menu."""
    while True:
        step = main_menu()
        if step is None:
            break
        execute_step(step)


@app.command()
def version():
    """Display the SkillOps version."""
    typer.echo("SkillOps LMS v0.1.0 (Sprint 1 MVP)")


if __name__ == "__main__":
    app()
