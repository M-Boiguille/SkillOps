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
    daily_standup_step,
    missions_step,
    read_step,
    reflection_step,
    tutor_step,
    reinforce_step,
)
from src.lms.database import init_db
from src.lms.persistence import get_completed_steps_for_today, mark_step_completed
from src.lms.steps.create import create_step
from src.lms.steps.share import share_step

console = Console()


def _enable_vim_keybindings() -> None:
    """Patch inquirer render to support vim keybindings (j/k)."""
    if not hasattr(ListRender, "process_input"):
        return

    original_process_input = ListRender.process_input
    if getattr(original_process_input, "vim_patched", False):
        return

    def vim_aware_process_input(self, pressed):
        """Process input with vim keybindings support (j=down, k=up)."""
        if pressed == "j":
            pressed = readchar.key.DOWN
        elif pressed == "k":
            pressed = readchar.key.UP
        return original_process_input(self, pressed)

    vim_aware_process_input.vim_patched = True  # type: ignore[attr-defined]
    ListRender.process_input = vim_aware_process_input


_enable_vim_keybindings()


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


# Define the 9 steps of the LMS workflow (+ optional Labs)
STEPS = [
    # Input Mode (Matin)
    Step(1, "Daily Stand-up", "📊"),  # Review
    Step(2, "Read", "📖"),  # Acquisition
    Step(3, "Tutor", "🧠"),  # Analysis (Feynman)
    # Output Mode (Après-midi)
    Step(4, "Reinforce", "💪"),  # Pratique (Interleaving)
    Step(5, "Create", "📝"),  # Zettelkasten/Flashcards gen
    Step(6, "Flashcards", "🗂️"),  # Anki Review
    # Closure Mode (Soir)
    Step(7, "Mission Control", "🚀"),  # Labs/Projets
    Step(8, "Pull Request", "🌐"),  # Portfolio
    Step(9, "Reflection", "🌅"),  # Journaling
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


def save_step_completion(step_number: int):
    """Mark a step as completed for today."""
    # Initialize DB if needed (idempotent)
    init_db()
    mark_step_completed(step_number)


def get_step_choices(mode: str = "full") -> list[str]:
    """Generate the list of step choices for the menu.

    Args:
        mode: Workflow mode - 'learning' (1-3), 'engineering' (4-9), or 'full' (all)

    Returns:
        List of formatted step strings with visual indicators.
    """
    init_db()
    completed_steps = get_completed_steps_for_today()

    # Update steps completion status based on persistence
    for step in STEPS:
        if step.number in completed_steps:
            step.completed = True

    # Filter steps based on mode
    if mode == "learning":
        step_numbers = [1, 2, 3]
    elif mode == "engineering":
        step_numbers = [4, 5, 6, 7, 8, 9]
    else:  # full
        step_numbers = list(range(1, 10))

    choices = []

    if 1 in step_numbers or 2 in step_numbers or 3 in step_numbers:
        choices.append("--- 🧠 INPUT MODE (Acquisition) ---")
        choices.extend(
            [
                str(s)
                for s in STEPS
                if s.number in [1, 2, 3] and s.number in step_numbers
            ]
        )

    if 4 in step_numbers or 5 in step_numbers or 6 in step_numbers:
        choices.append("--- ⚡ OUTPUT MODE (Pratique) ---")
        choices.extend(
            [
                str(s)
                for s in STEPS
                if s.number in [4, 5, 6] and s.number in step_numbers
            ]
        )

    if 7 in step_numbers or 8 in step_numbers or 9 in step_numbers:
        choices.append("--- 🏁 CLOSURE MODE (Intégration) ---")
        choices.extend(
            [
                str(s)
                for s in STEPS
                if s.number in [7, 8, 9] and s.number in step_numbers
            ]
        )

    choices.append("❌ Exit")
    return choices


def main_menu(mode: str = "full") -> Optional[Step]:
    """Display the main interactive menu and return the selected step.

    Args:
        mode: Workflow mode - 'learning' (1-3), 'engineering' (4-9), or 'full' (all)

    Uses Inquirer for keyboard navigation with arrow keys or vim keys (j/k).
    Returns None if user selects Exit.

    The 9-step Learning Workflow:
        1️⃣ Daily Stand-up - Metrics recap + WakaTime stats
        2️⃣ Read - Study technical articles & documentation
        3️⃣ Tutor - Smart note taker with Socratic dialogue
        4️⃣ Reinforce - Practice exercises
        5️⃣ Create - Build projects & write real code
        6️⃣ Flashcards - Space repetition with flashcards
        7️⃣ Mission Control - Solve tickets & incidents
        8️⃣ Pull Request - Submit & share your learnings
        9️⃣ Reflection - Reflect on your daily progress

    Modes:
        • learning: Steps 1-3 (acquisition, morning)
        • engineering: Steps 4-9 (production, afternoon)
        • full: All 9 steps

    Navigation:
        • Arrow Up/Down: Move between steps
        • j/k: Vim-style navigation
        • Enter: Execute selected step
        • Ctrl+C: Exit

    Returns:
        The selected Step object, or None if Exit was chosen.
    """
    display_header()

    choices = get_step_choices(mode=mode)

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
        1: daily_standup_step,  # Daily Stand-up
        2: read_step,  # Read
        3: tutor_step,  # Tutor
        4: reinforce_step,  # Reinforce (NEW)
        5: create_step,  # Create
        6: anki_step,  # Flashcards
        7: missions_step,  # Mission Control
        8: share_step,  # Pull Request
        9: reflection_step,  # Reflection
    }

    # Execute the corresponding step
    step_func = step_map.get(step.number)
    if step_func:
        # Execute step and check for success (True)
        result = step_func()  # type: ignore[operator]

        # If step returns True (success) or None (legacy steps assumed success if no error)
        if result is True or result is None:
            save_step_completion(step.number)
            step.completed = True
    else:
        console.print(f"\n[red]Error: Step {step.number} not implemented[/red]\n")
