"""Data import functionality for SkillOps progress and metrics."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.lms.persistence import ProgressManager

console = Console()


class DataImporter:
    """Import SkillOps progress and metrics from exported files."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize importer.

        Args:
            storage_path: Path to SkillOps storage directory
        """
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else Path.home() / ".local/share/skillops"
        )
        self.progress_manager = ProgressManager(self.storage_path)

    def import_from_json(
        self,
        json_file: Path,
        merge: bool = False,
        backup: bool = True,
    ) -> bool:
        """Import progress data from JSON export.

        Args:
            json_file: Path to JSON export file
            merge: Merge with existing data instead of replacing
            backup: Create backup of current data before import

        Returns:
            True if successful, False otherwise
        """
        if not json_file.exists():
            console.print(f"[red]✗[/red] File not found: {json_file}")
            return False

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task("[cyan]Importing from JSON...", total=None)

                # Load JSON data
                import_data = json.loads(json_file.read_text())
                progress_list = import_data.get("data", {}).get("progress", [])

                # Create backup if requested
                if backup:
                    self._create_backup()

                # Import progress data
                if merge:
                    # Load existing progress
                    current = self.progress_manager.load_progress()
                    # Merge: add new entries, replace existing ones by date
                    import_dates = {e["date"] for e in progress_list}

                    # Keep existing entries not in import
                    merged = [e for e in current if e["date"] not in import_dates]
                    # Add all import entries
                    merged.extend(progress_list)
                    # Sort by date
                    merged.sort(key=lambda e: e["date"])

                    # Save merged data
                    for entry in merged:
                        self.progress_manager.save_daily_progress(
                            entry, merge_strategy="replace"
                        )
                else:
                    # Replace: clear and import fresh
                    for entry in progress_list:
                        self.progress_manager.save_daily_progress(
                            entry, merge_strategy="replace"
                        )

                # Import metrics if available
                metrics = import_data.get("data", {}).get("metrics", {})
                if metrics:
                    metrics_file = self.storage_path / "metrics.json"
                    metrics_file.parent.mkdir(parents=True, exist_ok=True)
                    metrics_file.write_text(json.dumps(metrics, indent=2))

                progress.update(task, completed=True)

            console.print("[green]✓[/green] Successfully imported JSON data")
            return True

        except Exception as e:
            console.print(f"[red]✗ Import failed:[/red] {str(e)}")
            return False

    def import_from_csv(
        self,
        csv_file: Path,
        merge: bool = False,
        backup: bool = True,
    ) -> bool:
        """Import progress data from CSV export.

        Expected CSV format:
        - progress_data.csv: date, steps, time, cards

        Args:
            csv_file: Path to progress_data.csv
            merge: Merge with existing data
            backup: Create backup before import

        Returns:
            True if successful
        """
        if not csv_file.exists():
            console.print(f"[red]✗[/red] File not found: {csv_file}")
            return False

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task("[cyan]Importing from CSV...", total=None)

                # Create backup if requested
                if backup:
                    self._create_backup()

                # Import progress data from CSV
                self._import_progress_csv(csv_file, merge)

                progress.update(task, completed=True)

            console.print("[green]✓[/green] Successfully imported CSV data")
            return True

        except Exception as e:
            console.print(f"[red]✗ Import failed:[/red] {str(e)}")
            return False

    def _import_progress_csv(self, csv_file: Path, merge: bool) -> None:
        """Import progress entries from CSV.

        Args:
            csv_file: Path to CSV file with date, steps, time, cards
            merge: Whether to merge with existing data
        """
        import csv

        progress_list = []

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    entry = {
                        "date": row.get("date", ""),
                        "steps": int(row.get("steps", 0)),
                        "time": int(row.get("time", 0)),
                        "cards": int(row.get("cards", 0)),
                    }
                    if entry["date"]:  # Only add if date is valid
                        progress_list.append(entry)
                except ValueError:
                    console.print(
                        f"[yellow]Warning:[/yellow] Skipping invalid row: {row}"
                    )

        if merge:
            # Load existing progress
            current = self.progress_manager.load_progress()

            # Keep existing entries not in import
            merged = [
                e
                for e in current
                if e["date"] not in {e["date"] for e in progress_list}
            ]
            # Add all import entries
            merged.extend(progress_list)
            # Sort by date
            merged.sort(key=lambda e: e["date"])

            # Save merged data
            for entry in merged:
                self.progress_manager.save_daily_progress(
                    entry, merge_strategy="replace"
                )
        else:
            # Replace: save each entry
            for entry in progress_list:
                self.progress_manager.save_daily_progress(
                    entry, merge_strategy="replace"
                )

    def _create_backup(self) -> Path:
        """Create backup of current progress data.

        Returns:
            Path to backup file
        """
        backup_dir = self.storage_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"progress_backup_{timestamp}.json"

        progress_data = self.progress_manager.load_progress()
        backup_file.write_text(json.dumps(progress_data, indent=2))

        console.print(f"[dim]Created backup: {backup_file}[/dim]")
        return backup_file

    def validate_import(self, file_path: Path) -> bool:
        """Validate import file before importing.

        Args:
            file_path: Path to import file

        Returns:
            True if valid
        """
        if not file_path.exists():
            console.print(f"[red]✗ File not found:[/red] {file_path}")
            return False

        if file_path.suffix == ".json":
            try:
                data = json.loads(file_path.read_text())
                return "data" in data and "exported_at" in data
            except json.JSONDecodeError:
                console.print("[red]✗ Invalid JSON format[/red]")
                return False

        elif file_path.suffix == ".csv":
            # Basic CSV validation
            try:
                import csv

                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or []
                    return "date" in headers
            except Exception:
                return False

        return True
