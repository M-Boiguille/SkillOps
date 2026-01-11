"""Rich display formatting for SkillOps CLI.

This module provides Rich-based display functionality including:
- Formatted tables for metrics
- Progress bars
- Conditional colors (green = OK, red = warning)
- Responsive layouts
"""

from typing import Dict, Optional, List, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout


class DisplayManager:
    """Manage Rich-based CLI display with tables, colors, and progress bars."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize DisplayManager with Rich console.

        Args:
            console: Optional Rich Console instance (default: creates new Console)
        """
        self.console = console if console else Console()

    def display_metrics_table(
        self, 
        metrics: Dict[str, Any],
        title: str = "📊 Learning Metrics"
    ) -> None:
        """Display metrics in a formatted Rich table with conditional colors.

        Given: A dictionary of metrics (streak, avg_time, total_cards)
        When: display_metrics_table is called
        Then: A formatted table with conditional colors is displayed

        Args:
            metrics: Dict with streak, avg_time, total_cards keys
            title: Table title (default: "📊 Learning Metrics")
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", justify="left")
        table.add_column("Value", justify="right")
        table.add_column("Status", justify="center")

        # Streak with conditional color
        streak = metrics.get("streak", 0)
        streak_color = self._get_streak_color(streak)
        streak_status = self._get_streak_status(streak)
        table.add_row(
            "🔥 Streak",
            f"{streak} days",
            Text(streak_status, style=streak_color)
        )

        # Average time with conditional color
        avg_time = metrics.get("avg_time", 0.0)
        avg_time_color = self._get_time_color(avg_time)
        avg_time_status = self._get_time_status(avg_time)
        
        # Format time display
        if "avg_time_formatted" in metrics:
            time_display = metrics["avg_time_formatted"]
        else:
            hours = int(avg_time)
            minutes = int((avg_time - hours) * 60)
            time_display = f"{hours}h {minutes:02d}min"
        
        table.add_row(
            "⏱️  Avg Time",
            time_display,
            Text(avg_time_status, style=avg_time_color)
        )

        # Total cards with conditional color
        total_cards = metrics.get("total_cards", 0)
        cards_color = self._get_cards_color(total_cards)
        cards_status = self._get_cards_status(total_cards)
        table.add_row(
            "📝 Total Cards",
            str(total_cards),
            Text(cards_status, style=cards_color)
        )

        self.console.print(table)

    def display_progress_bar(
        self,
        description: str,
        total: int,
        current: int = 0,
        show_percentage: bool = True
    ) -> Progress:
        """Create and display a progress bar.

        Given: A description, total steps, and current progress
        When: display_progress_bar is called
        Then: A Rich progress bar is created and displayed

        Args:
            description: Text description of the progress
            total: Total number of steps
            current: Current step (default: 0)
            show_percentage: Whether to show percentage (default: True)

        Returns:
            Progress object that can be updated
        """
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%") if show_percentage else TextColumn(""),
            TimeRemainingColumn(),
            console=self.console
        )
        
        task_id = progress.add_task(description, total=total)
        if current > 0:
            progress.update(task_id, completed=current)
        
        return progress

    def display_step_progress(self, current_step: int, total_steps: int = 8) -> None:
        """Display step progress in the learning routine.

        Given: Current step and total steps
        When: display_step_progress is called
        Then: A visual progress indicator is displayed

        Args:
            current_step: Current step number (1-based)
            total_steps: Total number of steps (default: 8)
        """
        percentage = (current_step / total_steps) * 100
        filled = int(percentage / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        status = Text()
        status.append(f"Step {current_step}/{total_steps} ", style="bold")
        status.append(f"[{bar}] ", style="cyan")
        status.append(f"{percentage:.0f}%", style="bold green" if percentage >= 50 else "bold yellow")
        
        self.console.print(status)

    def display_panel(
        self,
        content: str,
        title: str = "",
        style: str = "cyan",
        border_style: str = "blue"
    ) -> None:
        """Display content in a Rich panel.

        Given: Content and styling options
        When: display_panel is called
        Then: Content is displayed in a formatted panel

        Args:
            content: Text content to display
            title: Panel title (default: "")
            style: Content style (default: "cyan")
            border_style: Border style (default: "blue")
        """
        panel = Panel(
            content,
            title=title,
            style=style,
            border_style=border_style
        )
        self.console.print(panel)

    def display_success(self, message: str) -> None:
        """Display a success message in green.

        Given: A success message
        When: display_success is called
        Then: Message is displayed in green with checkmark

        Args:
            message: Success message to display
        """
        self.console.print(f"✅ {message}", style="bold green")

    def display_warning(self, message: str) -> None:
        """Display a warning message in yellow/red.

        Given: A warning message
        When: display_warning is called
        Then: Message is displayed in yellow with warning icon

        Args:
            message: Warning message to display
        """
        self.console.print(f"⚠️  {message}", style="bold yellow")

    def display_error(self, message: str) -> None:
        """Display an error message in red.

        Given: An error message
        When: display_error is called
        Then: Message is displayed in red with error icon

        Args:
            message: Error message to display
        """
        self.console.print(f"❌ {message}", style="bold red")

    def _get_streak_color(self, streak: int) -> str:
        """Get color for streak based on value.

        Args:
            streak: Number of consecutive days

        Returns:
            Color string for Rich
        """
        if streak >= 7:
            return "bold green"
        elif streak >= 3:
            return "yellow"
        else:
            return "red"

    def _get_streak_status(self, streak: int) -> str:
        """Get status text for streak.

        Args:
            streak: Number of consecutive days

        Returns:
            Status text
        """
        if streak >= 7:
            return "🔥 Excellent!"
        elif streak >= 3:
            return "✓ Good"
        else:
            return "⚠ Low"

    def _get_time_color(self, avg_time: float) -> str:
        """Get color for average time based on value.

        Args:
            avg_time: Average time in hours

        Returns:
            Color string for Rich
        """
        if avg_time >= 2.0:
            return "bold green"
        elif avg_time >= 1.0:
            return "yellow"
        else:
            return "red"

    def _get_time_status(self, avg_time: float) -> str:
        """Get status text for average time.

        Args:
            avg_time: Average time in hours

        Returns:
            Status text
        """
        if avg_time >= 2.0:
            return "✓ Great!"
        elif avg_time >= 1.0:
            return "✓ Good"
        else:
            return "⚠ Too low"

    def _get_cards_color(self, total_cards: int) -> str:
        """Get color for total cards based on value.

        Args:
            total_cards: Total number of cards

        Returns:
            Color string for Rich
        """
        if total_cards >= 50:
            return "bold green"
        elif total_cards >= 20:
            return "yellow"
        else:
            return "red"

    def _get_cards_status(self, total_cards: int) -> str:
        """Get status text for total cards.

        Args:
            total_cards: Total number of cards

        Returns:
            Status text
        """
        if total_cards >= 50:
            return "✓ Excellent!"
        elif total_cards >= 20:
            return "✓ Good"
        else:
            return "⚠ Keep going"
