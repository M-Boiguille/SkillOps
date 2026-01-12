"""CLI module for SkillOps LMS - Interactive menu system.

This module provides the main interactive CLI menu using Inquirer for keyboard
navigation and Rich for visual display.
"""

from typing import Optional
import inquirer
from inquirer.render.console import List as ListRender
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import readchar

from src.lms.steps import (
    anki_step,
    formation_step,
    read_step,
    reflection_step,
    reinforce_step,
    review_step,
)
from src.lms.steps.create import create_step
from src.lms.steps.labs import labs_step
from src.lms.steps.share import share_step

console = Console()


# Patch inquirer to support vim keybindings (j/k)
original_process_input = ListRender.process_input


def vim_aware_process_input(self, pressed):
    """Process input with vim keybindings support (j=down, k=up)."""
    if pressed == "j":
        pressed = readchar.key.DOWN
    elif pressed == "k":
        pressed = readchar.key.UP
    return original_process_input(self, pressed)


ListRender.process_input = vim_aware_process_input


class Step:
    """Represents a step in the LMS workflow."""

    def __init__(self, number: int, name: str, emoji: str, completed: bool = False):
        self.number = number
        self.name = name
        self.emoji = emoji
        self.completed = completed

    def __str__(self) -> str:
        status = "●" if self.completed else "○"
        return f"{self.emoji} {self.number}. {self.name} {status}"


# Define the 8 steps of the LMS workflow (+ optional Labs)
STEPS = [
    Step(1, "Review", "📊"),
    Step(2, "Formation", "⏱️"),
    Step(3, "Anki", "🗂️"),
    Step(4, "Create", "📝"),
    Step(5, "Read", "📖"),
    Step(6, "Reinforce", "💪"),
    Step(7, "Share", "🌐"),
    Step(8, "Reflection", "🌅"),
    Step(9, "Labs", "🎯"),
]


def display_header() -> None:
    """Display the SkillOps header with Rich formatting."""
    header_text = Text("SkillOps LMS", style="bold cyan", justify="center")
    subtitle = Text(
        "Your Daily Learning Management System", style="dim", justify="center"
    )

    panel = Panel(
        f"{header_text}\n{subtitle}",
        title="Welcome",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def get_step_choices() -> list[str]:
    """Generate the list of step choices for the menu.

    Returns:
        List of formatted step strings with visual indicators.
    """
    choices = [str(step) for step in STEPS]
    choices.append("❌ Exit")
    return choices


def main_menu() -> Optional[Step]:
    """Display the main interactive menu and return the selected step.

    Uses Inquirer for keyboard navigation with arrow keys or vim keys (j/k).
    Returns None if user selects Exit.

    Navigation:
        - Arrow Up/Down or j/k to navigate
        - Enter to select
        - Ctrl+C to quit

    Returns:
        The selected Step object, or None if Exit was chosen.
    """
    display_header()

    choices = get_step_choices()

    questions = [
        inquirer.List(
            "step",
            message="Select a step (↑↓ or j/k to navigate, Enter to select)",
            choices=choices,
            carousel=True,
        )
    ]

    try:
        answers = inquirer.prompt(questions)

        if answers is None or answers["step"] == "❌ Exit":
            console.print("\n[yellow]Goodbye! Keep learning! 🚀[/yellow]\n")
            return None

        # Extract step number from selection
        selected_text = answers["step"]
        step_number = int(selected_text.split(".")[0].split()[-1])

        # Find and return the corresponding Step object
        for step in STEPS:
            if step.number == step_number:
                return step

        return None

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Goodbye! 👋[/yellow]\n")
        return None


def execute_step(step: Step) -> None:
    """Execute a specific step with its implementation.

    Args:
        step: The Step object to execute.
    """
    # Map step numbers to their implementations
    step_map = {
        1: review_step,  # Review
        2: formation_step,  # Formation
        3: anki_step,  # Anki
        4: create_step,  # Create
        5: read_step,  # Read
        6: reinforce_step,  # Reinforce
        7: share_step,  # Share
        8: reflection_step,  # Reflection
        9: labs_step,  # Labs - AI Missions
    }

    # Execute the corresponding step
    step_func = step_map.get(step.number)
    if step_func:
        step_func()  # type: ignore[operator]
    else:
        console.print(f"\n[red]Error: Step {step.number} not implemented[/red]\n")
