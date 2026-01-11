"""Interactive CLI for SkillOps Learning Management System.

This module implements the main menu interface using Inquirer for keyboard navigation.
Provides visual indicators for current step and supports navigation through 8 learning steps.
"""

from enum import Enum
from typing import Optional
import inquirer
from lms.persistence import StateManager


class Step(str, Enum):
    """Enumeration of the 8 learning steps in the daily workflow."""
    
    REVIEW = "review"
    FORMATION = "formation"
    ANALYSIS = "analysis"
    REINFORCE = "reinforce"
    ZETTELKASTEN = "zettelkasten"
    FLASHCARDS = "flashcards"
    PORTFOLIO = "portfolio"
    REFLECTION = "reflection"
    EXIT = "exit"


# Map Step enum to display names with emojis
STEP_DISPLAY_NAMES = {
    Step.REVIEW: "1. 📊 Review Metrics",
    Step.FORMATION: "2. ⏱️  Formation (WakaTime)",
    Step.ANALYSIS: "3. 🧠 Analysis with AI",
    Step.REINFORCE: "4. 💪 Reinforcement",
    Step.ZETTELKASTEN: "5. 📝 Zettelkasten Notes",
    Step.FLASHCARDS: "6. 🃏 Flashcards Generation",
    Step.PORTFOLIO: "7. 🔧 Portfolio Automation",
    Step.REFLECTION: "8. 🌅 Reflection",
    Step.EXIT: "Exit",
}


def get_current_step_from_state(state_manager: StateManager) -> Optional[str]:
    """Get current step ID from state manager.
    
    Args:
        state_manager: StateManager instance to query current state
        
    Returns:
        Current step_id from state or None if no valid state
    """
    state_manager.load_state()
    current_state = state_manager.get_current_state()
    
    if current_state and isinstance(current_state, dict):
        return current_state.get("step_id")
    return None


def format_menu_choice(step: Step, current_step_id: Optional[str]) -> str:
    """Format menu choice with current step indicator.
    
    Args:
        step: Step enum value to format
        current_step_id: Current step ID from state (or None)
        
    Returns:
        Formatted string with indicator (● for current, ○ for others)
    """
    display_name = STEP_DISPLAY_NAMES[step]
    
    # Exit option doesn't get an indicator
    if step == Step.EXIT:
        return display_name
    
    # Add indicator based on whether this is the current step
    indicator = "●" if step.value == current_step_id else "○"
    return f"{indicator} {display_name}"


def main_menu(state_manager: Optional[StateManager] = None) -> Step:
    """Display interactive main menu and return selected step.
    
    Shows all 8 learning steps plus Exit option with keyboard navigation.
    Current step is indicated with ● (filled circle), others with ○ (empty circle).
    
    Args:
        state_manager: Optional StateManager to load current step indicator.
                      If None, creates a default StateManager.
    
    Returns:
        Selected Step enum value
        
    Example:
        >>> step = main_menu()
        >>> if step == Step.REVIEW:
        ...     # Execute review metrics step
    """
    if state_manager is None:
        state_manager = StateManager()
    
    # Get current step from state
    current_step_id = get_current_step_from_state(state_manager)
    
    # Build choices list with all 8 steps + Exit
    steps_order = [
        Step.REVIEW,
        Step.FORMATION,
        Step.ANALYSIS,
        Step.REINFORCE,
        Step.ZETTELKASTEN,
        Step.FLASHCARDS,
        Step.PORTFOLIO,
        Step.REFLECTION,
        Step.EXIT,
    ]
    
    # Format each choice with indicator
    choices = [format_menu_choice(step, current_step_id) for step in steps_order]
    
    # Create Inquirer list prompt
    questions = [
        inquirer.List(
            "step",
            message="Select a step to execute",
            choices=choices,
        ),
    ]
    
    # Show menu and get answer
    answers = inquirer.prompt(questions)
    
    # Handle Ctrl+C or ESC (returns None)
    if answers is None:
        return Step.EXIT
    
    # Parse selected choice back to Step enum
    selected_display = answers["step"]
    
    # Remove indicator prefix if present
    for step in steps_order:
        formatted = format_menu_choice(step, current_step_id)
        if formatted == selected_display:
            return step
    
    # Fallback (should not happen)
    return Step.EXIT
