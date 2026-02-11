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
        step = Step(1, "Daily Stand-up", "📊", completed=True)

        assert step.number == 1
        assert step.name == "Daily Stand-up"
        assert step.emoji == "📊"
        assert step.completed is True

    def test_step_str_completed(self):
        """
        Given: A completed step
        When: Converting to string
        Then: String contains filled circle (●)
        """
        step = Step(1, "Daily Stand-up", "📊", completed=True)
        result = str(step)

        assert "●" in result
        assert "Daily Stand-up" in result
        assert "📊" in result

    def test_step_str_not_completed(self):
        """
        Given: An incomplete step
        When: Converting to string
        Then: String contains empty circle (○)
        """
        step = Step(2, "Flashcards", "🗂️", completed=False)
        result = str(step)

        assert "○" in result
        assert "Flashcards" in result
        assert "🗂️" in result


class TestStepChoices:
    """Tests for step choice generation."""

    @patch("src.lms.cli.get_completed_steps_for_today")
    @patch("src.lms.cli.init_db")
    @patch("src.lms.cli.inquirer")
    def test_get_step_choices_length(self, mock_inquirer, mock_init, mock_get_steps):
        """
        Given: The predefined STEPS list
        When: Getting step choices with separators
        Then: Returns 9 steps + 3 separators + Exit option = 13 choices
        """
        mock_get_steps.return_value = []
        _ = mock_inquirer
        _ = mock_init
        choices = get_step_choices()

        assert len(choices) == 13
        assert "❌ Exit" in choices

    @patch("src.lms.cli.get_completed_steps_for_today")
    @patch("src.lms.cli.init_db")
    @patch("src.lms.cli.inquirer")
    def test_get_step_choices_format(self, mock_inquirer, mock_init, mock_get_steps):
        """
        Given: The predefined STEPS list
        When: Getting step choices
        Then: Each choice contains emoji and step name
        """
        mock_get_steps.return_value = []
        _ = mock_inquirer
        _ = mock_init
        choices = get_step_choices()

        # Check first step format
        # Index 0 is separator, 1 is step 1
        assert "📊" in choices[1]
        assert "Daily Stand-up" in choices[1]

        # Check separators
        assert any("---" in c for c in choices)


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

    @patch("src.lms.cli.get_completed_steps_for_today")
    @patch("src.lms.cli.init_db")
    @patch("src.lms.cli.inquirer")
    @patch("src.lms.cli.console.print")
    def test_main_menu_returns_none_on_exit(
        self, mock_print, mock_inquirer, mock_init, mock_get_steps
    ):
        """
        Given: User selects Exit option
        When: Displaying main menu
        Then: Returns None
        """
        mock_get_steps.return_value = []
        _ = mock_print
        _ = mock_init
        mock_inquirer.prompt.return_value = {"step": "❌ Exit"}

        result = main_menu()

        assert result is None
        mock_inquirer.prompt.assert_called_once()

    @patch("src.lms.cli.get_completed_steps_for_today")
    @patch("src.lms.cli.init_db")
    @patch("src.lms.cli.inquirer")
    def test_main_menu_returns_step_on_selection(
        self, mock_inquirer, mock_init, mock_get_steps
    ):
        """
        Given: User selects step 1 (Review)
        When: Displaying main menu
        Then: Returns the corresponding Step object
        """
        mock_get_steps.return_value = []
        _ = mock_init
        mock_inquirer.prompt.return_value = {"step": "📊 1. Daily Stand-up ○"}

        result = main_menu()

        assert result is not None
        assert result.number == 1
        assert result.name == "Daily Stand-up"
        assert result.emoji == "📊"

    @patch("src.lms.cli.get_completed_steps_for_today")
    @patch("src.lms.cli.init_db")
    @patch("src.lms.cli.inquirer")
    @patch("src.lms.cli.console.print")
    def test_main_menu_handles_keyboard_interrupt(
        self, mock_print, mock_inquirer, mock_init, mock_get_steps
    ):
        """
        Given: User presses Ctrl+C
        When: Displaying main menu
        Then: Returns None and displays goodbye message
        """
        mock_get_steps.return_value = []
        _ = mock_print
        _ = mock_init
        mock_inquirer.prompt.side_effect = KeyboardInterrupt()

        result = main_menu()

        assert result is None

    @patch("src.lms.cli.get_completed_steps_for_today")
    @patch("src.lms.cli.init_db")
    @patch("src.lms.cli.inquirer")
    @patch("src.lms.cli.console.print")
    def test_main_menu_handles_none_answer(
        self, mock_print, mock_inquirer, mock_init, mock_get_steps
    ):
        """
        Given: Prompt returns None (Ctrl+D or similar)
        When: Displaying main menu
        Then: Returns None
        """
        mock_get_steps.return_value = []
        _ = mock_print
        _ = mock_init
        mock_inquirer.prompt.return_value = None

        result = main_menu()

        assert result is None

    @patch("src.lms.cli.get_completed_steps_for_today")
    @patch("src.lms.cli.init_db")
    @patch("src.lms.cli.inquirer")
    def test_main_menu_multiple_steps(self, mock_inquirer, mock_init, mock_get_steps):
        """
        Given: User selects different steps
        When: Calling main_menu multiple times
        Then: Returns correct Step for each selection
        """
        mock_get_steps.return_value = []
        _ = mock_init
        # Test step 2 (Read)
        mock_inquirer.prompt.return_value = {"step": "📖 2. Read ○"}
        result = main_menu()
        assert result is not None
        assert result.number == 2
        assert result.name == "Read"

        # Test step 8 (Pull Request)
        mock_inquirer.prompt.return_value = {"step": "🌐 8. Pull Request ○"}
        result = main_menu()
        assert result is not None
        assert result.number == 8
        assert result.name == "Pull Request"


class TestExecuteStep:
    """Tests for step execution."""

    @patch("src.lms.cli.save_step_completion")
    @patch("src.lms.cli.daily_standup_step")
    def test_execute_step_calls_review(self, mock_standup, mock_save):
        """
        Given: Step 1 (Daily Stand-up)
        When: Executing the step
        Then: Calls daily_standup_step function
        """
        mock_standup.return_value = True
        step = Step(1, "Daily Stand-up", "📊")

        execute_step(step)

        mock_standup.assert_called_once()
        mock_save.assert_called_once_with(1)

    @patch("src.lms.cli.save_step_completion")
    @patch("src.lms.cli.read_step")
    def test_execute_step_calls_read(self, mock_read, mock_save):
        """
        Given: Step 2 (Read)
        When: Executing the step
        Then: Calls read_step function
        """
        mock_read.return_value = True
        step = Step(2, "Read", "📖")

        execute_step(step)

        mock_read.assert_called_once()
        mock_save.assert_called_once_with(2)

    @patch("src.lms.cli.save_step_completion")
    @patch("src.lms.cli.reinforce_step")
    def test_execute_step_calls_reinforce(self, mock_reinforce, mock_save):
        """
        Given: Step 4 (Reinforce)
        When: Executing the step
        Then: Calls reinforce_step function
        """
        mock_reinforce.return_value = True
        step = Step(4, "Reinforce", "💪")

        execute_step(step)

        mock_reinforce.assert_called_once()
        mock_save.assert_called_once_with(4)


class TestStepsConstants:
    """Tests for the STEPS constant."""

    def test_steps_has_eight_items(self):
        """
        Given: The STEPS constant
        When: Checking length
        Then: Contains exactly 9 steps (1-8 core + Labs)
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
            "Daily Stand-up",
            "Read",
            "Tutor",
            "Reinforce",
            "Create",
            "Flashcards",
            "Mission Control",
            "Pull Request",
            "Reflection",
        ]

        for i, step in enumerate(STEPS):
            assert step.name == expected_names[i]
