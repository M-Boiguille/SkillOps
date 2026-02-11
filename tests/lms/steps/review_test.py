"""Tests for the Review step."""

from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.lms.steps.review import (
    get_yesterday_date,
    format_step_data_for_display,
    review_step,
)


class TestGetYesterdayDate:
    """Tests for get_yesterday_date function."""

    def test_get_yesterday_date_format(self):
        """
        Given: Current date
        When: Getting yesterday's date
        Then: Returns date in YYYY-MM-DD format
        """
        result = get_yesterday_date()

        # Check format
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"

        # Verify it's actually yesterday
        expected = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert result == expected


class TestFormatStepDataForDisplay:
    """Tests for format_step_data_for_display function."""

    def test_format_step_data_all_completed(self):
        """
        Given: Progress data with all steps completed
        When: Formatting for display
        Then: Returns 8 steps with completed=True
        """
        progress_data = {"steps_list": list(range(1, 10))}

        result = format_step_data_for_display(progress_data)

        assert len(result) == 9
        for step in result:
            assert step["completed"] is True
            assert step["time_spent"] == 0

    def test_format_step_data_none_completed(self):
        """
        Given: Progress data with no steps completed
        When: Formatting for display
        Then: Returns 8 steps with completed=False
        """
        progress_data = {"steps_list": []}

        result = format_step_data_for_display(progress_data)

        assert len(result) == 9
        for step in result:
            assert step["completed"] is False
            assert step["time_spent"] == 0

    def test_format_step_data_partial_completion(self):
        """
        Given: Progress data with some steps completed
        When: Formatting for display
        Then: Returns correct completion status for each step
        """
        progress_data = {"steps_list": [1, 3]}

        result = format_step_data_for_display(progress_data)

        assert result[0]["completed"] is True  # step1
        assert result[0]["time_spent"] == 0
        assert result[1]["completed"] is False  # step2 (not in data)
        assert result[2]["completed"] is True  # step3
        assert result[4]["completed"] is False  # step5 (Create)

    def test_format_step_data_has_correct_names_and_emojis(self):
        """
        Given: Progress data
        When: Formatting for display
        Then: Each step has correct name and emoji
        """
        progress_data = {"steps_list": []}

        result = format_step_data_for_display(progress_data)

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
        expected_emojis = ["📊", "📖", "🧠", "💪", "📝", "🗂️", "🚀", "🌐", "🌅"]

        for i, step in enumerate(result):
            assert step["name"] == expected_names[i]
            assert step["emoji"] == expected_emojis[i]
            assert step["number"] == i + 1


class TestReviewStep:
    """Tests for the main review_step function."""

    @patch("src.lms.steps.review.console.print")
    @patch("src.lms.steps.review.get_daily_summary")
    @patch("src.lms.steps.review.display_section_header")
    def test_review_step_no_data(self, mock_header, mock_get_summary, mock_print):
        """
        Given: No progress data for yesterday
        When: Running review step
        Then: Displays message about no data
        """
        mock_get_summary.return_value = {}

        review_step()

        mock_header.assert_called_once()
        # Should print "no data" message
        assert any(
            "No data" in str(call) or "no data" in str(call).lower()
            for call in mock_print.call_args_list
        )

    @patch("src.lms.steps.review.console.print")
    @patch("src.lms.steps.review.calculate_streak")
    @patch("src.lms.steps.review.get_daily_summary")
    @patch("src.lms.steps.review.display_section_header")
    @patch("src.lms.steps.review.create_metrics_table")
    @patch("src.lms.steps.review.create_step_summary_table")
    def test_review_step_with_data(
        self,
        mock_steps_table,
        mock_metrics_table,
        mock_header,
        mock_get_summary,
        mock_calculate_streak,
        mock_print,
    ):
        """
        Given: Valid progress data for yesterday
        When: Running review step
        Then: Displays metrics and steps tables
        """
        yesterday_date = get_yesterday_date()

        progress_data = {
            "date": yesterday_date,
            "steps_completed": 2,
            "steps_list": [1, 2],
            "total_time_minutes": 25,
            "cards_created": 5,
        }

        mock_get_summary.return_value = progress_data
        mock_calculate_streak.return_value = 5

        mock_metrics_table.return_value = MagicMock()
        mock_steps_table.return_value = MagicMock()

        review_step()

        mock_header.assert_called_once()
        mock_metrics_table.assert_called_once()
        mock_steps_table.assert_called_once()

    @patch("src.lms.steps.review.console.print")
    @patch("src.lms.steps.review.calculate_streak")
    @patch("src.lms.steps.review.get_daily_summary")
    @patch("src.lms.steps.review.display_section_header")
    @patch("src.lms.steps.review.create_metrics_table")
    @patch("src.lms.steps.review.create_step_summary_table")
    def test_review_step_excellent_performance(
        self,
        mock_steps_table,
        mock_metrics_table,
        mock_header,
        mock_get_summary,
        mock_calculate_streak,
        mock_print,
    ):
        """
        Given: Progress data with 7+ steps completed
        When: Running review step
        Then: Displays excellent performance message
        """
        yesterday_date = get_yesterday_date()

        progress_data = {
            "date": yesterday_date,
            "steps_completed": 8,
            "steps_list": list(range(1, 9)),
            "total_time_minutes": 120,
            "cards_created": 12,
        }

        mock_get_summary.return_value = progress_data
        mock_calculate_streak.return_value = 10

        mock_metrics_table.return_value = MagicMock()
        mock_steps_table.return_value = MagicMock()

        review_step()

        # Should contain "Excellent" message
        print_calls_str = str(mock_print.call_args_list)
        assert "Excellent" in print_calls_str or "excellent" in print_calls_str.lower()
