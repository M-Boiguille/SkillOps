"""Data export functionality for SkillOps progress and metrics."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.lms.database import init_db
from src.lms.persistence import calculate_streak, get_progress_history

console = Console()


class DataExporter:
    """Export SkillOps progress and metrics to various formats."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize exporter.

        Args:
            storage_path: Path to SkillOps storage directory
        """
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else Path.home() / ".local/share/skillops"
        )
        init_db(self.storage_path)

    def export_to_json(
        self,
        output_path: Optional[Path] = None,
        include_metrics: bool = True,
    ) -> Path:
        """Export all progress data to JSON format.

        Args:
            output_path: Where to save JSON file. Defaults to ./skillops_export.json
            include_metrics: Include metrics data if available

        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = Path.cwd() / "skillops_export.json"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("[cyan]Exporting to JSON...", total=None)

            # Collect all progress data (list of daily entries)
            all_progress = get_progress_history(self.storage_path)

            export_data: Dict[str, Any] = {
                "exported_at": datetime.now().isoformat(),
                "export_format": "json",
                "version": "1.0",
                "data": {
                    "progress": all_progress,
                },
            }

            # Add metrics if available
            if include_metrics:
                total_cards = sum(e.get("cards", 0) for e in all_progress)
                total_time = sum(e.get("time", 0) for e in all_progress)
                avg_time = (total_time / len(all_progress)) if all_progress else 0.0
                export_data["data"]["metrics"] = {
                    "streak": calculate_streak(self.storage_path),
                    "avg_time": avg_time,
                    "total_cards": total_cards,
                }

            progress.update(task, completed=True)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))

        console.print(f"[green]✓[/green] Exported to {output_path}")
        return output_path

    def export_to_csv(
        self,
        output_dir: Optional[Path] = None,
        flatten: bool = True,
    ) -> list[Path]:
        """Export progress data to CSV format.

        Generates a single CSV file with all progress entries:
        - progress_data.csv: One row per day with date, steps, time, cards

        Args:
            output_dir: Directory to save CSV file. Defaults to current directory
            flatten: Unused, kept for API compatibility

        Returns:
            List of paths to exported CSV files
        """
        if output_dir is None:
            output_dir = Path.cwd()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("[cyan]Exporting to CSV...", total=None)

            # Load all progress data
            all_progress = get_progress_history(self.storage_path)

            # Export progress CSV
            csv_path = output_dir / "progress_data.csv"
            self._export_progress_csv(all_progress, csv_path)

            progress.update(task, completed=True)

        console.print(f"[green]✓[/green] Exported to {output_dir}")
        return [csv_path]

    def _export_progress_csv(self, progress_data: list, output_path: Path) -> None:
        """Export progress data to CSV file.

        Args:
            progress_data: List of progress entries
            output_path: Path to save CSV
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV with headers: date, steps, time, cards
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["date", "steps", "time", "cards"],
            )
            writer.writeheader()
            writer.writerows(progress_data)

    def display_export_summary(self) -> None:
        """Display a summary table of exported data."""
        all_progress = get_progress_history(self.storage_path)

        if not all_progress:
            console.print("[yellow]No progress data to display[/yellow]")
            return

        # Create summary table
        table = Table(title="Export Summary")
        table.add_column("Total Entries", style="cyan")
        table.add_column("Date Range", style="magenta")
        table.add_column("Total Steps", style="green")
        table.add_column("Total Time (min)", style="yellow")
        table.add_column("Total Cards", style="blue")

        if all_progress:
            total_steps = sum(e.get("steps", 0) for e in all_progress)
            total_time = sum(e.get("time", 0) for e in all_progress)
            total_cards = sum(e.get("cards", 0) for e in all_progress)
            date_range = (
                f"{all_progress[0].get('date')} to " f"{all_progress[-1].get('date')}"
            )

            table.add_row(
                str(len(all_progress)),
                date_range,
                str(total_steps),
                str(total_time),
                str(total_cards),
            )

        console.print(table)
