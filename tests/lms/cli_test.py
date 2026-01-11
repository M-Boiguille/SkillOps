"""
Test suite for CLI module.

Based on:
- URD (User Requirements Document) - US-011: Interface CLI Interactive
- Sprint Planning Sprint 1 - Task T011-2: Implémenter menu principal
- ADR: CLI with Inquirer for keyboard navigation

CLI module responsibilities:
1. Display interactive menu with 8 steps + Exit
2. Support keyboard navigation (arrow keys)
3. Show current step indicator (● vs ○)
4. Return selected Step enum
5. Handle user cancellation (Ctrl+C, ESC)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from lms.cli import (
    Step,
    STEP_DISPLAY_NAMES,
    get_current_step_from_state,
    format_menu_choice,
    main_menu,
)
from lms.persistence import StateManager


class TestStepEnum:
    """Test Step enumeration."""

    def test_step_enum_values(self):
        """GIVEN Step enum
        WHEN accessing enum values
        THEN all 8 steps + exit should be defined
        """
        expected_steps = [
            "review",
            "formation",
            "analysis",
            "reinforce",
            "zettelkasten",
            "flashcards",
            "portfolio",
            "reflection",
            "exit",
        ]
        
        actual_steps = [step.value for step in Step]
        assert len(actual_steps) == 9
        for expected in expected_steps:
            assert expected in actual_steps

    def test_step_display_names_complete(self):
        """GIVEN STEP_DISPLAY_NAMES dictionary
        WHEN checking all Step enum values
        THEN each step should have a display name
        """
        for step in Step:
            assert step in STEP_DISPLAY_NAMES
            assert isinstance(STEP_DISPLAY_NAMES[step], str)
            assert len(STEP_DISPLAY_NAMES[step]) > 0

    def test_step_display_names_format(self):
        """GIVEN STEP_DISPLAY_NAMES
        WHEN checking format
        THEN steps should have number, emoji, and name (except Exit)
        """
        # Check that first 8 steps have the pattern "N. emoji Name"
        step_list = [
            Step.REVIEW,
            Step.FORMATION,
            Step.ANALYSIS,
            Step.REINFORCE,
            Step.ZETTELKASTEN,
            Step.FLASHCARDS,
            Step.PORTFOLIO,
            Step.REFLECTION,
        ]
        
        for i, step in enumerate(step_list, start=1):
            display = STEP_DISPLAY_NAMES[step]
            assert display.startswith(f"{i}. ")


class TestGetCurrentStepFromState:
    """Test getting current step from StateManager."""

    def test_get_current_step_with_valid_state(self, tmp_path):
        """GIVEN a StateManager with valid state
        WHEN get_current_step_from_state is called
        THEN it should return the step_id
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        state_manager.current_state = {
            "session_id": "test_session",
            "step_id": "review",
            "timestamp": "2026-01-10T10:00:00Z",
        }
        state_manager.save_state()
        
        result = get_current_step_from_state(state_manager)
        
        assert result == "review"

    def test_get_current_step_with_no_state(self, tmp_path):
        """GIVEN a StateManager with no saved state
        WHEN get_current_step_from_state is called
        THEN it should return None
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        
        result = get_current_step_from_state(state_manager)
        
        assert result is None

    def test_get_current_step_with_none_step_id(self, tmp_path):
        """GIVEN a StateManager with step_id = None
        WHEN get_current_step_from_state is called
        THEN it should return None
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        state_manager.current_state = {
            "session_id": None,
            "step_id": None,
            "timestamp": None,
        }
        state_manager.save_state()
        
        result = get_current_step_from_state(state_manager)
        
        assert result is None


class TestFormatMenuChoice:
    """Test menu choice formatting with indicators."""

    def test_format_menu_choice_current_step(self):
        """GIVEN a step that is the current step
        WHEN format_menu_choice is called
        THEN it should return formatted string with ● indicator
        """
        result = format_menu_choice(Step.REVIEW, "review")
        
        assert "●" in result
        assert "📊 Review Metrics" in result
        assert result.startswith("●")

    def test_format_menu_choice_non_current_step(self):
        """GIVEN a step that is NOT the current step
        WHEN format_menu_choice is called
        THEN it should return formatted string with ○ indicator
        """
        result = format_menu_choice(Step.FORMATION, "review")
        
        assert "○" in result
        assert "⏱️  Formation" in result
        assert result.startswith("○")

    def test_format_menu_choice_no_current_step(self):
        """GIVEN no current step (None)
        WHEN format_menu_choice is called
        THEN it should return formatted string with ○ indicator
        """
        result = format_menu_choice(Step.REINFORCE, None)
        
        assert "○" in result
        assert "💪 Reinforcement" in result

    def test_format_menu_choice_exit_no_indicator(self):
        """GIVEN Exit step
        WHEN format_menu_choice is called
        THEN it should NOT have an indicator
        """
        result = format_menu_choice(Step.EXIT, "review")
        
        assert "●" not in result
        assert "○" not in result
        assert result == "Exit"


class TestMainMenu:
    """Test main_menu function."""

    @patch("lms.cli.inquirer.prompt")
    def test_main_menu_returns_selected_step(self, mock_prompt, tmp_path):
        """GIVEN user selects a step
        WHEN main_menu is called
        THEN it should return the selected Step enum
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        
        # Simulate user selecting Review (with indicator)
        mock_prompt.return_value = {"step": "○ 1. 📊 Review Metrics"}
        
        result = main_menu(state_manager)
        
        assert result == Step.REVIEW

    @patch("lms.cli.inquirer.prompt")
    def test_main_menu_with_current_step_indicator(self, mock_prompt, tmp_path):
        """GIVEN current step is 'formation'
        WHEN main_menu displays choices
        THEN formation should have ● indicator
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        state_manager.current_state = {
            "session_id": "test",
            "step_id": "formation",
            "timestamp": "2026-01-10T10:00:00Z",
        }
        state_manager.save_state()
        
        # User selects formation (current step)
        mock_prompt.return_value = {"step": "● 2. ⏱️  Formation (WakaTime)"}
        
        result = main_menu(state_manager)
        
        assert result == Step.FORMATION

    @patch("lms.cli.inquirer.prompt")
    def test_main_menu_handles_exit_selection(self, mock_prompt, tmp_path):
        """GIVEN user selects Exit
        WHEN main_menu is called
        THEN it should return Step.EXIT
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        
        mock_prompt.return_value = {"step": "Exit"}
        
        result = main_menu(state_manager)
        
        assert result == Step.EXIT

    @patch("lms.cli.inquirer.prompt")
    def test_main_menu_handles_cancellation(self, mock_prompt, tmp_path):
        """GIVEN user cancels (Ctrl+C or ESC)
        WHEN main_menu is called
        THEN inquirer returns None and function should return Step.EXIT
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        
        # inquirer.prompt returns None on cancellation
        mock_prompt.return_value = None
        
        result = main_menu(state_manager)
        
        assert result == Step.EXIT

    @patch("lms.cli.inquirer.prompt")
    def test_main_menu_uses_default_state_manager(self, mock_prompt):
        """GIVEN no StateManager is provided
        WHEN main_menu is called
        THEN it should create a default StateManager
        """
        mock_prompt.return_value = {"step": "Exit"}
        
        result = main_menu()
        
        assert result == Step.EXIT
        assert mock_prompt.called

    @patch("lms.cli.inquirer.prompt")
    def test_main_menu_shows_all_8_steps_plus_exit(self, mock_prompt, tmp_path):
        """GIVEN main_menu is called
        WHEN inquirer.prompt is invoked
        THEN it should display 9 choices (8 steps + Exit)
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        
        mock_prompt.return_value = {"step": "Exit"}
        
        main_menu(state_manager)
        
        # Check that prompt was called with a list of questions
        assert mock_prompt.called
        call_args = mock_prompt.call_args[0][0]
        assert len(call_args) == 1
        
        # Check that the question has 9 choices
        question = call_args[0]
        assert len(question.choices) == 9

    @patch("lms.cli.inquirer.prompt")
    def test_main_menu_all_steps_selectable(self, mock_prompt, tmp_path):
        """GIVEN all 8 steps + Exit
        WHEN user selects each one
        THEN each should map to correct Step enum
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        
        test_cases = [
            ("○ 1. 📊 Review Metrics", Step.REVIEW),
            ("○ 2. ⏱️  Formation (WakaTime)", Step.FORMATION),
            ("○ 3. 🧠 Analysis with AI", Step.ANALYSIS),
            ("○ 4. 💪 Reinforcement", Step.REINFORCE),
            ("○ 5. 📝 Zettelkasten Notes", Step.ZETTELKASTEN),
            ("○ 6. 🃏 Flashcards Generation", Step.FLASHCARDS),
            ("○ 7. 🔧 Portfolio Automation", Step.PORTFOLIO),
            ("○ 8. 🌅 Reflection", Step.REFLECTION),
            ("Exit", Step.EXIT),
        ]
        
        for choice_text, expected_step in test_cases:
            mock_prompt.return_value = {"step": choice_text}
            result = main_menu(state_manager)
            assert result == expected_step, f"Failed for {choice_text}"


class TestIntegrationWithStateManager:
    """Test CLI integration with StateManager."""

    @patch("lms.cli.inquirer.prompt")
    def test_cli_loads_state_correctly(self, mock_prompt, tmp_path):
        """GIVEN a saved state with step_id='reinforce'
        WHEN main_menu loads state
        THEN the reinforce choice should have ● indicator
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        state_manager.current_state = {
            "session_id": "session_123",
            "step_id": "reinforce",
            "timestamp": "2026-01-10T15:30:00Z",
        }
        state_manager.save_state()
        
        # Capture what was passed to inquirer
        mock_prompt.return_value = {"step": "Exit"}
        
        main_menu(state_manager)
        
        # Verify prompt was called
        assert mock_prompt.called
        call_args = mock_prompt.call_args[0][0]
        question = call_args[0]
        choices = question.choices
        
        # Find the reinforce choice and verify it has ● indicator
        reinforce_choice = [c for c in choices if "Reinforcement" in c][0]
        assert reinforce_choice.startswith("●")

    @patch("lms.cli.inquirer.prompt")
    def test_cli_with_empty_state(self, mock_prompt, tmp_path):
        """GIVEN an empty state file
        WHEN main_menu is called
        THEN all choices should have ○ indicator (except Exit)
        """
        state_file = tmp_path / "state.yaml"
        state_manager = StateManager(state_file)
        
        mock_prompt.return_value = {"step": "Exit"}
        
        main_menu(state_manager)
        
        call_args = mock_prompt.call_args[0][0]
        question = call_args[0]
        choices = question.choices
        
        # All non-Exit choices should have ○
        for choice in choices[:-1]:  # Exclude Exit
            assert choice.startswith("○")
