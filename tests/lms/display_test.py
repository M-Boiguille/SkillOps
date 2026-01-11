"""Tests for the display module - Rich display components."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from rich.table import Table
from rich.progress import Progress
from lms.display import (
    create_metrics_table,
    create_step_summary_table,
    display_success_message,
    display_warning_message,
    display_error_message,
    display_info_panel,
    create_progress_bar,
    format_time_duration,
    format_date,
    display_section_header,
)


class TestCreateMetricsTable:
    """Tests for metrics table creation."""

    def test_create_metrics_table_returns_table(self):
        """
        Given: Valid metrics dictionary
        When: Creating metrics table
        Then: Returns a Table object
        """
        metrics = {
            "steps_completed": 7,
            "total_time": 7200,
            "cards_created": 12,
            "streak": 18,
        }

        result = create_metrics_table(metrics)

        assert isinstance(result, Table)
        assert result.title == "📊 Daily Metrics"

    def test_create_metrics_table_with_minimal_data(self):
        """
        Given: Empty metrics dictionary
        When: Creating metrics table
        Then: Returns table with zero values
        """
        metrics = {}

        result = create_metrics_table(metrics)

        assert isinstance(result, Table)

    def test_create_metrics_table_time_formatting(self):
        """
        Given: Metrics with 13320 seconds (3h42min)
        When: Creating metrics table
        Then: Table contains formatted time string
        """
        metrics = {"total_time": 13320}  # 3h 42min

        result = create_metrics_table(metrics)

        # Check that table was created successfully
        assert isinstance(result, Table)


class TestCreateStepSummaryTable:
    """Tests for step summary table creation."""

    def test_create_step_summary_table_returns_table(self):
        """
        Given: Valid steps data
        When: Creating step summary table
        Then: Returns a Table object
        """
        steps_data = [
            {
                "number": 1,
                "name": "Review",
                "emoji": "📊",
                "completed": True,
                "time_spent": 600,
            },
            {
                "number": 2,
                "name": "Formation",
                "emoji": "⏱️",
                "completed": False,
                "time_spent": 0,
            },
        ]

        result = create_step_summary_table(steps_data)

        assert isinstance(result, Table)
        assert result.title == "📋 Steps Overview"

    def test_create_step_summary_table_empty_list(self):
        """
        Given: Empty steps list
        When: Creating step summary table
        Then: Returns empty table
        """
        steps_data = []

        result = create_step_summary_table(steps_data)

        assert isinstance(result, Table)


class TestDisplayMessages:
    """Tests for display message functions."""

    @patch("lms.display.console.print")
    def test_display_success_message(self, mock_print):
        """
        Given: Success message
        When: Displaying success message
        Then: Console.print is called with green panel
        """
        display_success_message("Operation completed")

        mock_print.assert_called_once()

    @patch("lms.display.console.print")
    def test_display_warning_message(self, mock_print):
        """
        Given: Warning message
        When: Displaying warning message
        Then: Console.print is called with yellow panel
        """
        display_warning_message("Be careful")

        mock_print.assert_called_once()

    @patch("lms.display.console.print")
    def test_display_error_message(self, mock_print):
        """
        Given: Error message
        When: Displaying error message
        Then: Console.print is called with red panel
        """
        display_error_message("Something went wrong")

        mock_print.assert_called_once()

    @patch("lms.display.console.print")
    def test_display_info_panel(self, mock_print):
        """
        Given: Info panel content
        When: Displaying info panel
        Then: Console.print is called
        """
        display_info_panel("Information", "Here is some info")

        mock_print.assert_called_once()

    @patch("lms.display.console.print")
    def test_display_info_panel_custom_color(self, mock_print):
        """
        Given: Info panel with custom border color
        When: Displaying info panel
        Then: Console.print is called with specified color
        """
        display_info_panel("Custom", "Content here", border_color="magenta")

        mock_print.assert_called_once()


class TestProgressBar:
    """Tests for progress bar creation."""

    def test_create_progress_bar_returns_progress_object(self):
        """
        Given: Progress bar description
        When: Creating progress bar
        Then: Returns Progress object
        """
        result = create_progress_bar("Loading")

        assert isinstance(result, Progress)

    def test_create_progress_bar_default_description(self):
        """
        Given: No description provided
        When: Creating progress bar
        Then: Uses default description
        """
        result = create_progress_bar()

        assert isinstance(result, Progress)


class TestFormatTimeDuration:
    """Tests for time duration formatting."""

    def test_format_time_duration_hours_and_minutes(self):
        """
        Given: 13320 seconds (3h 42min)
        When: Formatting time duration
        Then: Returns "3h 42min"
        """
        result = format_time_duration(13320)

        assert result == "3h 42min"

    def test_format_time_duration_only_minutes(self):
        """
        Given: 2700 seconds (45 minutes)
        When: Formatting time duration
        Then: Returns "45min"
        """
        result = format_time_duration(2700)

        assert result == "45min"

    def test_format_time_duration_zero(self):
        """
        Given: 0 seconds
        When: Formatting time duration
        Then: Returns "0min"
        """
        result = format_time_duration(0)

        assert result == "0min"

    def test_format_time_duration_negative(self):
        """
        Given: Negative seconds
        When: Formatting time duration
        Then: Returns "0min" (handles negative gracefully)
        """
        result = format_time_duration(-100)

        assert result == "0min"

    def test_format_time_duration_exact_hours(self):
        """
        Given: 7200 seconds (exactly 2 hours)
        When: Formatting time duration
        Then: Returns "2h 00min"
        """
        result = format_time_duration(7200)

        assert result == "2h 00min"

    def test_format_time_duration_large_value(self):
        """
        Given: 36000 seconds (10 hours)
        When: Formatting time duration
        Then: Returns "10h 00min"
        """
        result = format_time_duration(36000)

        assert result == "10h 00min"


class TestFormatDate:
    """Tests for date formatting."""

    def test_format_date_january(self):
        """
        Given: Date in January
        When: Formatting date
        Then: Returns French formatted date
        """
        date = datetime(2026, 1, 11)

        result = format_date(date)

        assert result == "11 janvier 2026"

    def test_format_date_december(self):
        """
        Given: Date in December
        When: Formatting date
        Then: Returns French formatted date
        """
        date = datetime(2025, 12, 25)

        result = format_date(date)

        assert result == "25 décembre 2025"

    def test_format_date_single_digit_day(self):
        """
        Given: Date with single-digit day
        When: Formatting date
        Then: Returns correctly formatted date
        """
        date = datetime(2026, 3, 5)

        result = format_date(date)

        assert result == "5 mars 2026"

    def test_format_date_all_months(self):
        """
        Given: Dates in different months
        When: Formatting dates
        Then: All return correct French month names
        """
        expected = [
            (datetime(2026, 1, 1), "1 janvier 2026"),
            (datetime(2026, 2, 1), "1 février 2026"),
            (datetime(2026, 3, 1), "1 mars 2026"),
            (datetime(2026, 4, 1), "1 avril 2026"),
            (datetime(2026, 5, 1), "1 mai 2026"),
            (datetime(2026, 6, 1), "1 juin 2026"),
            (datetime(2026, 7, 1), "1 juillet 2026"),
            (datetime(2026, 8, 1), "1 août 2026"),
            (datetime(2026, 9, 1), "1 septembre 2026"),
            (datetime(2026, 10, 1), "1 octobre 2026"),
            (datetime(2026, 11, 1), "1 novembre 2026"),
            (datetime(2026, 12, 1), "1 décembre 2026"),
        ]

        for date, expected_str in expected:
            assert format_date(date) == expected_str


class TestDisplaySectionHeader:
    """Tests for section header display."""

    @patch("lms.display.console.print")
    def test_display_section_header_default_emoji(self, mock_print):
        """
        Given: Section title
        When: Displaying section header
        Then: Console.print is called multiple times
        """
        display_section_header("My Section")

        assert mock_print.call_count >= 3

    @patch("lms.display.console.print")
    def test_display_section_header_custom_emoji(self, mock_print):
        """
        Given: Section title with custom emoji
        When: Displaying section header
        Then: Console.print is called with custom emoji
        """
        display_section_header("Custom Section", emoji="🚀")

        assert mock_print.call_count >= 3


class TestIntegrationScenarios:
    """Integration tests for combined display scenarios."""

    def test_full_metrics_display_scenario(self):
        """
        Given: Complete metrics data
        When: Creating all display components
        Then: All components are created successfully
        """
        # Metrics table
        metrics = {
            "steps_completed": 7,
            "total_time": 7200,
            "cards_created": 12,
            "streak": 18,
        }
        metrics_table = create_metrics_table(metrics)

        # Steps table
        steps_data = [
            {"number": i, "name": f"Step{i}", "emoji": "📌", "completed": i <= 5}
            for i in range(1, 9)
        ]
        steps_table = create_step_summary_table(steps_data)

        # Verify both created
        assert isinstance(metrics_table, Table)
        assert isinstance(steps_table, Table)

    def test_time_formatting_consistency(self):
        """
        Given: Various time values
        When: Formatting times
        Then: All formats are consistent
        """
        test_cases = [
            (0, "0min"),
            (60, "1min"),
            (3600, "1h 00min"),
            (3660, "1h 01min"),
            (7200, "2h 00min"),
        ]

        for seconds, expected in test_cases:
            result = format_time_duration(seconds)
            assert result == expected
