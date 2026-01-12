"""Tests for the CLI module - main menu and step navigation."""

from unittest.mock import patch
from src.lms.cli import (
    Step,
    STEPS,
    main_menu,
    execute_step,
    get_step_choices,
    display_header,
)


class TestStep:
    """Tests for the Step class."""

    def test_step_initialization(self):
        """
        Given: Step parameters
        When: Creating a new Step instance
        Then: All attributes are set correctly
        """
        step = Step(1, "Review", "📊", completed=True)

        assert step.number == 1
        assert step.name == "Review"
        assert step.emoji == "📊"
        assert step.completed is True

    def test_step_str_completed(self):
        """
        Given: A completed step
        When: Converting to string
        Then: String contains filled circle (●)
        """
        step = Step(1, "Review", "📊", completed=True)
        result = str(step)

        assert "●" in result
        assert "Review" in result
        assert "📊" in result

    def test_step_str_not_completed(self):
        """
        Given: An incomplete step
        When: Converting to string
        Then: String contains empty circle (○)
        """
        step = Step(2, "Formation", "⏱️", completed=False)
        result = str(step)

        assert "○" in result
        assert "Formation" in result
        assert "⏱️" in result


class TestStepChoices:
    """Tests for step choice generation."""

    def test_get_step_choices_length(self):
        """
        Given: The predefined STEPS list
        When: Getting step choices
        Then: Returns 9 steps + Exit option = 10 choices
        """
        choices = get_step_choices()

        assert len(choices) == 10
        assert "❌ Exit" in choices

    def test_get_step_choices_format(self):
        """
        Given: The predefined STEPS list
        When: Getting step choices
        Then: Each choice contains emoji and step name
        """
        choices = get_step_choices()

        # Check first step format
        assert "📊" in choices[0]
        assert "Review" in choices[0]

        # Check last step format (before Exit)
        assert "9. Labs" in choices[8]
        assert "Labs" in choices[8]


class TestDisplayHeader:
    """Tests for header display."""

    @patch("src.lms.cli.console.print")
    def test_display_header_calls_print(self, mock_print):
        """
        Given: Console is available
        When: Displaying header
        Then: Console.print is called
        """
        display_header()

        assert mock_print.call_count >= 2


class TestMainMenu:
    """Tests for the main menu interaction."""

    @patch("src.lms.cli.inquirer.prompt")
    @patch("src.lms.cli.console.print")
    def test_main_menu_returns_none_on_exit(self, mock_print, mock_prompt):
        """
        Given: User selects Exit option
        When: Displaying main menu
        Then: Returns None
        """
        mock_prompt.return_value = {"step": "❌ Exit"}

        result = main_menu()

        assert result is None
        mock_prompt.assert_called_once()

    @patch("src.lms.cli.inquirer.prompt")
    def test_main_menu_returns_step_on_selection(self, mock_prompt):
        """
        Given: User selects step 1 (Review)
        When: Displaying main menu
        Then: Returns the corresponding Step object
        """
        mock_prompt.return_value = {"step": "📊 1. Review ○"}

        result = main_menu()

        assert result is not None
        assert result.number == 1
        assert result.name == "Review"
        assert result.emoji == "📊"

    @patch("src.lms.cli.inquirer.prompt")
    @patch("src.lms.cli.console.print")
    def test_main_menu_handles_keyboard_interrupt(self, mock_print, mock_prompt):
        """
        Given: User presses Ctrl+C
        When: Displaying main menu
        Then: Returns None and displays goodbye message
        """
        mock_prompt.side_effect = KeyboardInterrupt()

        result = main_menu()

        assert result is None

    @patch("src.lms.cli.inquirer.prompt")
    @patch("src.lms.cli.console.print")
    def test_main_menu_handles_none_answer(self, mock_print, mock_prompt):
        """
        Given: Prompt returns None (Ctrl+D or similar)
        When: Displaying main menu
        Then: Returns None
        """
        mock_prompt.return_value = None

        result = main_menu()

        assert result is None

    @patch("src.lms.cli.inquirer.prompt")
    def test_main_menu_multiple_steps(self, mock_prompt):
        """
        Given: User selects different steps
        When: Calling main_menu multiple times
        Then: Returns correct Step for each selection
        """
        # Test step 3 (Anki)
        mock_prompt.return_value = {"step": "🗂️ 3. Anki ○"}
        result = main_menu()
        assert result.number == 3
        assert result.name == "Anki"

        # Test step 8 (Reflection)
        mock_prompt.return_value = {"step": "🌅 8. Reflection ○"}
        result = main_menu()
        assert result.number == 8
        assert result.name == "Reflection"


class TestExecuteStep:
    """Tests for step execution."""

    @patch("src.lms.cli.review_step")
    def test_execute_step_calls_review(self, mock_review):
        """
        Given: Step 1 (Review)
        When: Executing the step
        Then: Calls review_step function
        """
        step = Step(1, "Review", "📊")

        execute_step(step)

        mock_review.assert_called_once()

    @patch("src.lms.cli.formation_step")
    def test_execute_step_calls_formation(self, mock_formation):
        """
        Given: Step 2 (Formation)
        When: Executing the step
        Then: Calls formation_step function
        """
        step = Step(2, "Formation", "⏱️")

        execute_step(step)

        mock_formation.assert_called_once()

    @patch("src.lms.cli.reinforce_step")
    def test_execute_step_calls_reinforce(self, mock_reinforce):
        """
        Given: Step 6 (Reinforce)
        When: Executing the step
        Then: Calls reinforce_step function
        """
        step = Step(6, "Reinforce", "💪")

        execute_step(step)

        mock_reinforce.assert_called_once()


class TestStepsConstants:
    """Tests for the STEPS constant."""

    def test_steps_has_eight_items(self):
        """
        Given: The STEPS constant
        When: Checking length
        Then: Contains exactly 9 steps (1-8 core + 9 Labs)
        """
        assert len(STEPS) == 9

    def test_steps_sequential_numbers(self):
        """
        Given: The STEPS constant
        When: Checking step numbers
        Then: Numbers are sequential from 1 to 8
        """
        for i, step in enumerate(STEPS, start=1):
            assert step.number == i

    def test_steps_all_have_emojis(self):
        """
        Given: The STEPS constant
        When: Checking each step
        Then: All steps have emojis defined
        """
        for step in STEPS:
            assert step.emoji
            assert len(step.emoji) > 0

    def test_steps_all_have_names(self):
        """
        Given: The STEPS constant
        When: Checking each step
        Then: All steps have names defined
        """
        expected_names = [
            "Review",
            "Formation",
            "Anki",
            "Create",
            "Read",
            "Reinforce",
            "Share",
            "Reflection",
            "Labs",
        ]

        for i, step in enumerate(STEPS):
            assert step.name == expected_names[i]
