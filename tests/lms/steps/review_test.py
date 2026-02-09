"""Tests for the Review step."""

from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.lms.steps.review import (
    get_yesterday_date,
    format_step_data_for_display,
    calculate_metrics_from_progress,
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
        progress_data = {
            "steps": {
                f"step{i}": {"completed": True, "time_spent": 300} for i in range(1, 9)
            }
        }

        result = format_step_data_for_display(progress_data)

        assert len(result) == 8
        for step in result:
            assert step["completed"] is True
            assert step["time_spent"] == 300

    def test_format_step_data_none_completed(self):
        """
        Given: Progress data with no steps completed
        When: Formatting for display
        Then: Returns 8 steps with completed=False
        """
        progress_data = {"steps": {}}

        result = format_step_data_for_display(progress_data)

        assert len(result) == 8
        for step in result:
            assert step["completed"] is False
            assert step["time_spent"] == 0

    def test_format_step_data_partial_completion(self):
        """
        Given: Progress data with some steps completed
        When: Formatting for display
        Then: Returns correct completion status for each step
        """
        progress_data = {
            "steps": {
                "step1": {"completed": True, "time_spent": 600},
                "step3": {"completed": True, "time_spent": 900},
                "step5": {"completed": False, "time_spent": 0},
            }
        }

        result = format_step_data_for_display(progress_data)

        assert result[0]["completed"] is True  # step1
        assert result[0]["time_spent"] == 600
        assert result[1]["completed"] is False  # step2 (not in data)
        assert result[2]["completed"] is True  # step3
        assert result[4]["completed"] is False  # step5

    def test_format_step_data_has_correct_names_and_emojis(self):
        """
        Given: Progress data
        When: Formatting for display
        Then: Each step has correct name and emoji
        """
        progress_data = {"steps": {}}

        result = format_step_data_for_display(progress_data)

        expected_names = [
            "Daily Stand-up",
            "Flashcards",
            "Create",
            "Read",
            "Tutor",
            "Mission Control",
            "Pull Request",
            "Reflection",
        ]
        expected_emojis = ["📊", "🗂️", "📝", "📖", "🧑‍🏫", "💪", "🌐", "🌅"]

        for i, step in enumerate(result):
            assert step["name"] == expected_names[i]
            assert step["emoji"] == expected_emojis[i]
            assert step["number"] == i + 1


class TestCalculateMetricsFromProgress:
    """Tests for calculate_metrics_from_progress function."""

    def test_calculate_metrics_all_steps_completed(self):
        """
        Given: Progress with all 8 steps completed
        When: Calculating metrics
        Then: Returns steps_completed=8
        """
        progress_data = {
            "date": "2026-01-10",
            "steps": {
                f"step{i}": {"completed": True, "time_spent": 600} for i in range(1, 9)
            },
            "cards_created": 12,
        }
        all_progress_data = [progress_data]

        result = calculate_metrics_from_progress(progress_data, all_progress_data)

        assert result["steps_completed"] == 8
        assert result["total_time"] == 4800  # 8 * 600
        assert result["cards_created"] == 12

    def test_calculate_metrics_no_steps_completed(self):
        """
        Given: Progress with no steps completed
        When: Calculating metrics
        Then: Returns steps_completed=0
        """
        progress_data = {
            "date": "2026-01-10",
            "steps": {},
            "cards_created": 0,
        }
        all_progress_data = [progress_data]

        result = calculate_metrics_from_progress(progress_data, all_progress_data)

        assert result["steps_completed"] == 0
        assert result["total_time"] == 0
        assert result["cards_created"] == 0

    def test_calculate_metrics_partial_completion(self):
        """
        Given: Progress with 5 steps completed
        When: Calculating metrics
        Then: Returns correct counts and totals
        """
        progress_data = {
            "date": "2026-01-10",
            "steps": {
                "step1": {"completed": True, "time_spent": 300},
                "step2": {"completed": True, "time_spent": 450},
                "step3": {"completed": False, "time_spent": 0},
                "step4": {"completed": True, "time_spent": 600},
                "step5": {"completed": True, "time_spent": 200},
                "step6": {"completed": True, "time_spent": 350},
            },
            "cards_created": 8,
        }
        all_progress_data = [progress_data]

        result = calculate_metrics_from_progress(progress_data, all_progress_data)

        assert result["steps_completed"] == 5
        assert result["total_time"] == 1900  # 300+450+600+200+350
        assert result["cards_created"] == 8


class TestReviewStep:
    """Tests for the main review_step function."""

    @patch("src.lms.steps.review.console.print")
    @patch("src.lms.steps.review.ProgressManager")
    @patch("src.lms.steps.review.display_section_header")
    def test_review_step_no_data(
        self, mock_header, mock_progress_manager_class, mock_print
    ):
        """
        Given: No progress data for yesterday
        When: Running review step
        Then: Displays message about no data
        """
        mock_manager = MagicMock()
        mock_manager.load_progress.return_value = {}
        mock_manager.get_progress_by_date.return_value = None
        mock_progress_manager_class.return_value = mock_manager

        review_step()

        mock_header.assert_called_once()
        # Should print "no data" message
        assert any(
            "No data" in str(call) or "no data" in str(call).lower()
            for call in mock_print.call_args_list
        )

    @patch("src.lms.steps.review.console.print")
    @patch("src.lms.steps.review.ProgressManager")
    @patch("src.lms.steps.review.display_section_header")
    @patch("src.lms.steps.review.create_metrics_table")
    @patch("src.lms.steps.review.create_step_summary_table")
    def test_review_step_with_data(
        self,
        mock_steps_table,
        mock_metrics_table,
        mock_header,
        mock_progress_manager_class,
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
            "steps": {
                "step1": {"completed": True, "time_spent": 600},
                "step2": {"completed": True, "time_spent": 900},
            },
            "cards_created": 5,
        }

        mock_manager = MagicMock()
        mock_manager.load_progress.return_value = [progress_data]
        mock_manager.get_progress_by_date.return_value = progress_data
        mock_progress_manager_class.return_value = mock_manager

        mock_metrics_table.return_value = MagicMock()
        mock_steps_table.return_value = MagicMock()

        review_step()

        mock_header.assert_called_once()
        mock_metrics_table.assert_called_once()
        mock_steps_table.assert_called_once()

    @patch("src.lms.steps.review.console.print")
    @patch("src.lms.steps.review.ProgressManager")
    @patch("src.lms.steps.review.display_section_header")
    @patch("src.lms.steps.review.create_metrics_table")
    @patch("src.lms.steps.review.create_step_summary_table")
    def test_review_step_excellent_performance(
        self,
        mock_steps_table,
        mock_metrics_table,
        mock_header,
        mock_progress_manager_class,
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
            "steps": {
                f"step{i}": {"completed": True, "time_spent": 300} for i in range(1, 8)
            },
            "cards_created": 12,
        }

        mock_manager = MagicMock()
        mock_manager.load_progress.return_value = [progress_data]
        mock_manager.get_progress_by_date.return_value = progress_data
        mock_progress_manager_class.return_value = mock_manager

        mock_metrics_table.return_value = MagicMock()
        mock_steps_table.return_value = MagicMock()

        review_step()

        # Should contain "Excellent" message
        print_calls_str = str(mock_print.call_args_list)
        assert "Excellent" in print_calls_str or "excellent" in print_calls_str.lower()

    @patch("src.lms.steps.review.console.print")
    @patch("src.lms.steps.review.ProgressManager")
    @patch("src.lms.steps.review.display_section_header")
    @patch("src.lms.steps.review.create_metrics_table")
    @patch("src.lms.steps.review.create_step_summary_table")
    def test_review_step_custom_storage_path(
        self,
        mock_steps_table,
        mock_metrics_table,
        mock_header,
        mock_progress_manager_class,
        mock_print,
        tmp_path,
    ):
        """
        Given: Custom storage path
        When: Running review step with custom path
        Then: Uses the provided storage path
        """
        custom_storage = tmp_path / "custom_storage"
        yesterday_date = get_yesterday_date()

        progress_data = {
            "date": yesterday_date,
            "steps": {
                "step1": {"completed": True, "time_spent": 300},
            },
            "cards_created": 5,
        }

        mock_manager = MagicMock()
        mock_manager.load_progress.return_value = [progress_data]
        mock_manager.get_progress_by_date.return_value = progress_data
        mock_progress_manager_class.return_value = mock_manager

        mock_metrics_table.return_value = MagicMock()
        mock_steps_table.return_value = MagicMock()

        review_step(storage_path=custom_storage)

        # Verify ProgressManager was initialized with custom path
        call_args = mock_progress_manager_class.call_args
        assert custom_storage / "progress.json" == call_args[0][0]
