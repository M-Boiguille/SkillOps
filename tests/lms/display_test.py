"""
Test suite for DisplayManager class.

Based on:
- Sprint Planning Sprint 1 - Task T011-3: Implémenter affichage Rich
- US-011: Interface CLI Interactive

DisplayManager responsibilities:
1. Display formatted tables for metrics
2. Create and display progress bars
3. Apply conditional colors (green = OK, red = warning)
4. Provide responsive layout
5. Display success/warning/error messages
"""

import pytest
from io import StringIO
from rich.console import Console
from lms.display import DisplayManager


class TestDisplayManagerInit:
    """Test DisplayManager initialization."""

    def test_init_with_default_console(self):
        """
        Given: No console parameter provided
        When: DisplayManager is initialized
        Then: It should create a default Console instance
        """
        display = DisplayManager()
        
        assert display.console is not None
        assert isinstance(display.console, Console)

    def test_init_with_custom_console(self):
        """
        Given: A custom Console instance
        When: DisplayManager is initialized with it
        Then: It should use the provided console
        """
        custom_console = Console(file=StringIO())
        display = DisplayManager(console=custom_console)
        
        assert display.console is custom_console


class TestDisplayMetricsTable:
    """Test metrics table display functionality."""

    def test_display_metrics_table_with_valid_data(self):
        """
        Given: Valid metrics data with streak, avg_time, total_cards
        When: display_metrics_table is called
        Then: Table should be rendered without errors
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        metrics = {
            "streak": 7,
            "avg_time": 2.5,
            "total_cards": 60
        }
        
        display.display_metrics_table(metrics)
        result = output.getvalue()
        
        assert "Learning Metrics" in result
        assert "Streak" in result
        assert "7 days" in result
        assert "Avg Time" in result
        assert "Total Cards" in result
        assert "60" in result

    def test_display_metrics_table_with_formatted_time(self):
        """
        Given: Metrics with avg_time_formatted key
        When: display_metrics_table is called
        Then: Formatted time should be displayed
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        metrics = {
            "streak": 5,
            "avg_time": 2.75,
            "avg_time_formatted": "2h 45min",
            "total_cards": 30
        }
        
        display.display_metrics_table(metrics)
        result = output.getvalue()
        
        assert "2h 45min" in result

    def test_display_metrics_table_with_zero_values(self):
        """
        Given: Metrics with all zero values
        When: display_metrics_table is called
        Then: Table should display zeros without errors
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        metrics = {
            "streak": 0,
            "avg_time": 0.0,
            "total_cards": 0
        }
        
        display.display_metrics_table(metrics)
        result = output.getvalue()
        
        assert "0 days" in result
        assert "0h 00min" in result

    def test_display_metrics_table_with_custom_title(self):
        """
        Given: Metrics and a custom title
        When: display_metrics_table is called with title parameter
        Then: Custom title should be displayed
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        metrics = {
            "streak": 3,
            "avg_time": 1.5,
            "total_cards": 25
        }
        
        display.display_metrics_table(metrics, title="Custom Metrics")
        result = output.getvalue()
        
        assert "Custom Metrics" in result

    def test_display_metrics_table_missing_keys_uses_defaults(self):
        """
        Given: Metrics dictionary with missing keys
        When: display_metrics_table is called
        Then: Default values (0) should be used
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        metrics = {}
        
        display.display_metrics_table(metrics)
        result = output.getvalue()
        
        # Should not crash and should show defaults
        assert "0 days" in result or "0h 00min" in result


class TestConditionalColors:
    """Test conditional color logic for different metric values."""

    def test_streak_color_excellent(self):
        """
        Given: A streak of 7 or more days
        When: _get_streak_color is called
        Then: Should return green color
        """
        display = DisplayManager()
        
        color = display._get_streak_color(7)
        assert "green" in color
        
        color = display._get_streak_color(10)
        assert "green" in color

    def test_streak_color_good(self):
        """
        Given: A streak of 3-6 days
        When: _get_streak_color is called
        Then: Should return yellow color
        """
        display = DisplayManager()
        
        color = display._get_streak_color(3)
        assert "yellow" in color
        
        color = display._get_streak_color(5)
        assert "yellow" in color

    def test_streak_color_low(self):
        """
        Given: A streak of less than 3 days
        When: _get_streak_color is called
        Then: Should return red color
        """
        display = DisplayManager()
        
        color = display._get_streak_color(0)
        assert "red" in color
        
        color = display._get_streak_color(2)
        assert "red" in color

    def test_time_color_great(self):
        """
        Given: Average time of 2.0 hours or more
        When: _get_time_color is called
        Then: Should return green color
        """
        display = DisplayManager()
        
        color = display._get_time_color(2.0)
        assert "green" in color
        
        color = display._get_time_color(3.5)
        assert "green" in color

    def test_time_color_good(self):
        """
        Given: Average time between 1.0 and 2.0 hours
        When: _get_time_color is called
        Then: Should return yellow color
        """
        display = DisplayManager()
        
        color = display._get_time_color(1.0)
        assert "yellow" in color
        
        color = display._get_time_color(1.5)
        assert "yellow" in color

    def test_time_color_low(self):
        """
        Given: Average time less than 1.0 hour
        When: _get_time_color is called
        Then: Should return red color
        """
        display = DisplayManager()
        
        color = display._get_time_color(0.0)
        assert "red" in color
        
        color = display._get_time_color(0.5)
        assert "red" in color

    def test_cards_color_excellent(self):
        """
        Given: Total cards of 50 or more
        When: _get_cards_color is called
        Then: Should return green color
        """
        display = DisplayManager()
        
        color = display._get_cards_color(50)
        assert "green" in color
        
        color = display._get_cards_color(100)
        assert "green" in color

    def test_cards_color_good(self):
        """
        Given: Total cards between 20 and 50
        When: _get_cards_color is called
        Then: Should return yellow color
        """
        display = DisplayManager()
        
        color = display._get_cards_color(20)
        assert "yellow" in color
        
        color = display._get_cards_color(35)
        assert "yellow" in color

    def test_cards_color_low(self):
        """
        Given: Total cards less than 20
        When: _get_cards_color is called
        Then: Should return red color
        """
        display = DisplayManager()
        
        color = display._get_cards_color(0)
        assert "red" in color
        
        color = display._get_cards_color(10)
        assert "red" in color


class TestStatusText:
    """Test status text generation for metrics."""

    def test_streak_status_excellent(self):
        """
        Given: A streak of 7+ days
        When: _get_streak_status is called
        Then: Should return excellent status
        """
        display = DisplayManager()
        
        status = display._get_streak_status(7)
        assert "Excellent" in status

    def test_streak_status_good(self):
        """
        Given: A streak of 3-6 days
        When: _get_streak_status is called
        Then: Should return good status
        """
        display = DisplayManager()
        
        status = display._get_streak_status(3)
        assert "Good" in status

    def test_streak_status_low(self):
        """
        Given: A streak of less than 3 days
        When: _get_streak_status is called
        Then: Should return low status
        """
        display = DisplayManager()
        
        status = display._get_streak_status(0)
        assert "Low" in status

    def test_time_status_messages(self):
        """
        Given: Different average time values
        When: _get_time_status is called
        Then: Should return appropriate status messages
        """
        display = DisplayManager()
        
        status = display._get_time_status(2.5)
        assert "Great" in status or "Good" in status
        
        status = display._get_time_status(1.5)
        assert "Good" in status
        
        status = display._get_time_status(0.5)
        assert "low" in status.lower()

    def test_cards_status_messages(self):
        """
        Given: Different total card values
        When: _get_cards_status is called
        Then: Should return appropriate status messages
        """
        display = DisplayManager()
        
        status = display._get_cards_status(60)
        assert "Excellent" in status
        
        status = display._get_cards_status(30)
        assert "Good" in status
        
        status = display._get_cards_status(10)
        assert "Keep going" in status or "going" in status


class TestProgressBar:
    """Test progress bar functionality."""

    def test_display_progress_bar_creates_progress(self):
        """
        Given: Description and total steps
        When: display_progress_bar is called
        Then: Should return a Progress object
        """
        output = StringIO()
        console = Console(file=output)
        display = DisplayManager(console=console)
        
        progress = display.display_progress_bar("Test Task", total=10)
        
        assert progress is not None

    def test_display_progress_bar_with_current_value(self):
        """
        Given: Description, total, and current progress
        When: display_progress_bar is called
        Then: Progress should be set to current value
        """
        output = StringIO()
        console = Console(file=output)
        display = DisplayManager(console=console)
        
        progress = display.display_progress_bar("Test Task", total=10, current=5)
        
        assert progress is not None

    def test_display_step_progress_renders_correctly(self):
        """
        Given: Current step and total steps
        When: display_step_progress is called
        Then: Progress indicator should be rendered
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        display.display_step_progress(current_step=4, total_steps=8)
        result = output.getvalue()
        
        assert "Step 4/8" in result
        assert "50%" in result

    def test_display_step_progress_with_different_steps(self):
        """
        Given: Different step values
        When: display_step_progress is called
        Then: Should display correct percentages
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        display.display_step_progress(current_step=8, total_steps=8)
        result = output.getvalue()
        
        assert "Step 8/8" in result
        assert "100%" in result


class TestPanelDisplay:
    """Test panel display functionality."""

    def test_display_panel_with_content(self):
        """
        Given: Content text
        When: display_panel is called
        Then: Content should be displayed in a panel
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        display.display_panel("Test content")
        result = output.getvalue()
        
        assert "Test content" in result

    def test_display_panel_with_title(self):
        """
        Given: Content and title
        When: display_panel is called with title
        Then: Title should be displayed
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        display.display_panel("Test content", title="Test Title")
        result = output.getvalue()
        
        assert "Test content" in result
        assert "Test Title" in result


class TestMessageDisplay:
    """Test success, warning, and error message display."""

    def test_display_success_message(self):
        """
        Given: A success message
        When: display_success is called
        Then: Message should be displayed with checkmark
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        display.display_success("Operation successful")
        result = output.getvalue()
        
        assert "Operation successful" in result
        assert "✅" in result

    def test_display_warning_message(self):
        """
        Given: A warning message
        When: display_warning is called
        Then: Message should be displayed with warning icon
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        display.display_warning("This is a warning")
        result = output.getvalue()
        
        assert "This is a warning" in result
        assert "⚠" in result or "warning" in result.lower()

    def test_display_error_message(self):
        """
        Given: An error message
        When: display_error is called
        Then: Message should be displayed with error icon
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        display.display_error("An error occurred")
        result = output.getvalue()
        
        assert "An error occurred" in result
        assert "❌" in result


class TestResponsiveLayout:
    """Test responsive layout functionality."""

    def test_metrics_table_adapts_to_console_width(self):
        """
        Given: Different console widths
        When: display_metrics_table is called
        Then: Table should adapt to console width
        """
        # Test with narrow console
        narrow_output = StringIO()
        narrow_console = Console(file=narrow_output, force_terminal=True, width=60)
        display_narrow = DisplayManager(console=narrow_console)
        
        metrics = {
            "streak": 5,
            "avg_time": 2.0,
            "total_cards": 30
        }
        
        display_narrow.display_metrics_table(metrics)
        narrow_result = narrow_output.getvalue()
        
        # Test with wide console
        wide_output = StringIO()
        wide_console = Console(file=wide_output, force_terminal=True, width=120)
        display_wide = DisplayManager(console=wide_console)
        
        display_wide.display_metrics_table(metrics)
        wide_result = wide_output.getvalue()
        
        # Both should contain the same content
        assert "Streak" in narrow_result
        assert "Streak" in wide_result


class TestIntegrationWithMetrics:
    """Test integration with MetricsManager."""

    def test_display_metrics_from_metrics_manager_format(self):
        """
        Given: Metrics in MetricsManager.get_metrics_summary() format
        When: display_metrics_table is called
        Then: All metrics should be displayed correctly
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        # Format from MetricsManager.get_metrics_summary()
        metrics = {
            "streak": 15,
            "avg_time": 3.5,
            "total_cards": 120,
            "avg_time_formatted": "3h 30min"
        }
        
        display.display_metrics_table(metrics)
        result = output.getvalue()
        
        assert "15 days" in result
        assert "3h 30min" in result
        assert "120" in result

    def test_display_handles_edge_case_values(self):
        """
        Given: Edge case metric values (very high, very low)
        When: display_metrics_table is called
        Then: Should display without errors
        """
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        display = DisplayManager(console=console)
        
        # Very high values
        metrics = {
            "streak": 365,
            "avg_time": 10.0,
            "total_cards": 1000
        }
        
        display.display_metrics_table(metrics)
        result = output.getvalue()
        
        assert "365 days" in result
        assert "1000" in result
