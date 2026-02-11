"""Data import functionality for SkillOps progress and metrics."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.lms.database import get_connection, init_db
from src.lms.persistence import calculate_streak, get_progress_history

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
        init_db(self.storage_path)

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

                if merge:
                    for entry in progress_list:
                        self._clear_progress_for_date(entry.get("date"))
                        self._insert_progress_entry(entry)
                else:
                    self._clear_all_progress()
                    for entry in progress_list:
                        self._insert_progress_entry(entry)

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
            for entry in progress_list:
                date_value = entry.get("date")
                if isinstance(date_value, str) and date_value:
                    self._clear_progress_for_date(date_value)
                self._insert_progress_entry(entry)
        else:
            self._clear_all_progress()
            for entry in progress_list:
                self._insert_progress_entry(entry)

    def _create_backup(self) -> Path:
        """Create backup of current progress data.

        Returns:
            Path to backup file
        """
        backup_dir = self.storage_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"progress_backup_{timestamp}.json"

        history = get_progress_history(self.storage_path)
        total_cards = sum(e.get("cards", 0) for e in history)
        total_time = sum(e.get("time", 0) for e in history)
        avg_time = (total_time / len(history)) if history else 0.0

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "export_format": "json",
            "version": "1.0",
            "data": {
                "progress": history,
                "metrics": {
                    "streak": calculate_streak(self.storage_path),
                    "avg_time": avg_time,
                    "total_cards": total_cards,
                },
            },
        }

        backup_file.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))

        console.print(f"[dim]Created backup: {backup_file}[/dim]")
        return backup_file

    def _clear_progress_for_date(self, date_str: Optional[str]) -> None:
        if not date_str:
            return
        conn = get_connection(self.storage_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sessions WHERE date = ?", (date_str,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        session_id = row[0]
        cursor.execute(
            "DELETE FROM step_completions WHERE session_id = ?", (session_id,)
        )
        cursor.execute("DELETE FROM formation_logs WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM card_creations WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def _clear_all_progress(self) -> None:
        conn = get_connection(self.storage_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM step_completions")
        cursor.execute("DELETE FROM formation_logs")
        cursor.execute("DELETE FROM card_creations")
        cursor.execute("DELETE FROM read_sessions")
        cursor.execute("DELETE FROM sessions")
        conn.commit()
        conn.close()

    def _insert_progress_entry(self, entry: dict) -> None:
        if not isinstance(entry, dict):
            return
        date_str = entry.get("date")
        if not date_str:
            return

        def _safe_int(value) -> int:
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        steps = _safe_int(entry.get("steps", 0))
        time_minutes = _safe_int(entry.get("time", 0))
        cards = _safe_int(entry.get("cards", 0))

        conn = get_connection(self.storage_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO sessions (date) VALUES (?)", (date_str,))
        cursor.execute("SELECT id FROM sessions WHERE date = ?", (date_str,))
        session_id = cursor.fetchone()[0]

        for step_num in range(1, min(max(steps, 0), 9) + 1):
            cursor.execute(
                "INSERT OR IGNORE INTO step_completions (session_id, step_number) VALUES (?, ?)",
                (session_id, step_num),
            )

        if time_minutes > 0:
            cursor.execute(
                "INSERT INTO formation_logs (session_id, goals, recall, "
                "duration_minutes) VALUES (?, ?, ?, ?)",
                (session_id, json.dumps([]), "", time_minutes),
            )

        if cards > 0:
            cursor.execute(
                "INSERT INTO card_creations (session_id, count, source) VALUES (?, ?, ?)",
                (session_id, cards, "import"),
            )

        conn.commit()
        conn.close()

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
