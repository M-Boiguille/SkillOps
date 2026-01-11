"""State and progress management for SkillOps with YAML and JSON persistence."""

from datetime import date, timedelta
from pathlib import Path
from typing import Any
import json
import yaml

# Constants to define default storage paths
BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
STATE_FILE = STORAGE_DIR / ".state.yaml"
PROGRESS_FILE = STORAGE_DIR / ".progress.json"
METRICS_FILE = STORAGE_DIR / ".metrics.json"


class StateManager:
    """Manage application state with YAML file persistence."""

    def __init__(self, path=STATE_FILE):
        """Initialize StateManager with file path.

        Args:
            path: Path to state file (default: storage/.state.yaml)
        """
        self.file_path = Path(path)
        self.current_state: dict | None = None
        self.template = {"session_id": None, "step_id": None, "timestamp": None}

    def get_current_state(self) -> dict | None:
        """Return current state or None."""
        return self.current_state

    def is_valid_state(self, state: Any) -> bool:
        """Check if state is a dict and has all required keys.

        Args:
            state: current_state checked at runtime

        Returns:
            True if state has session_id, step_id, timestamp keys
        """
        if state is None:
            return False
        if not isinstance(state, dict):
            return False
        required_keys = {"session_id", "step_id", "timestamp"}
        return required_keys.issubset(state.keys())

    def load_state(self) -> None:
        """Load state from YAML file. Creates default if file doesn't exist."""
        # If file doesn't exist, create default state
        if not self.file_path.exists():
            self.current_state = self.template.copy()
            return

        try:
            with self.file_path.open("r") as file:
                loaded_state = yaml.safe_load(file)

                # Handle empty file (yaml.safe_load returns None)
                if loaded_state is None or loaded_state == {}:
                    self.current_state = self.template.copy()
                    return

                # Validate and use loaded state

                if self.is_valid_state(loaded_state):
                    self.current_state = loaded_state
                else:
                    self.current_state = self.template.copy()
        except (yaml.YAMLError, OSError) as e:
            raise IOError(f"Error loading state: {self.file_path}") from e

    def save_state(self) -> None:
        """Save current state to YAML file."""
        # Don't save if state is invalid
        if not self.is_valid_state(self.current_state):
            return

        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.file_path.open("w") as file:
                yaml.safe_dump(self.current_state, file, default_flow_style=False)
        except (yaml.YAMLError, OSError) as e:
            raise IOError(f"Error writing state: {self.file_path}") from e


class ProgressManager:
    """Manage progress history with JSON file persistence."""

    def __init__(self, path=PROGRESS_FILE):
        """Initialize ProgressManager with file path.

        Args:
            path: Path to progress file (default: storage/.progress.json)
        """
        self.file_path = Path(path)
        self.current_progress: list = []

    def is_valid_progress(self, progress: Any) -> bool:
        """Check if progress is a dict and has all required keys.

        Args:
            progress: Progress entry checked at runtime

        Returns:
            True if progress has date, steps, time, cards keys
            Note: exercises_done is optional for backwards compatibility
        """
        if progress is None:
            return False
        if not isinstance(progress, dict):
            return False
        required_keys = {"date", "steps", "time", "cards"}
        return required_keys.issubset(progress.keys())

    def load_progress(self) -> list:
        """Load progress from JSON file. Returns empty list if file doesn't exist.

        Returns:
            List of progress entries
        """
        if not self.file_path.exists():
            self.current_progress = []
            return self.current_progress

        try:
            with self.file_path.open("r") as file:
                self.current_progress = json.load(file)
                return self.current_progress.copy()
        except (json.JSONDecodeError, OSError) as e:
            raise IOError(f"Error loading progress: {self.file_path}") from e

    def merge_progress(self, new_entry: dict, strategy: str = "smart") -> bool:
        """Merge new progress entry with in-memory state intelligently.

        This method avoids data loss by intelligently merging in-memory progress
        with file-based progress. Useful for non-concurrent modifications.

        Args:
            new_entry: Progress entry to merge (with date, steps, time, cards)
            strategy: Merge strategy:
                - "smart" (default): Merge if no concurrent modifications detected
                - "replace": Replace existing entry for the date (overwrites)
                - "accumulate": Sum numeric fields for the same date

        Returns:
            True if merge successful, False if conflicts detected (concurrent mods)

        Behavior by strategy:
            - smart: Returns False if another process modified the file for this
                    date; otherwise merges new_entry with in-memory state
            - replace: Always overwrites existing entry for this date
            - accumulate: Adds steps/time/cards to existing entry (non-destructive)

        Example:
            # Non-destructive accumulation
            progress_mgr.save_daily_progress(
                {"date": "2024-01-10", "steps": 1000, "time": 30, "cards": 10},
                strategy="accumulate"
            )
        """
        if not self.is_valid_progress(new_entry):
            return False

        entry_date = new_entry["date"]
        file_progress = []

        # Load current file state to check for concurrent modifications
        if self.file_path.exists():
            try:
                with self.file_path.open("r") as file:
                    file_progress = json.load(file)
            except (json.JSONDecodeError, OSError):
                file_progress = []

        # Find existing entries in both states
        file_entry = next((e for e in file_progress if e["date"] == entry_date), None)
        memory_entry = next((e for e in self.current_progress if e["date"] == entry_date), None)

        # Check for concurrent modifications (file was updated externally)
        if file_entry and memory_entry and file_entry != memory_entry:
            if strategy == "smart":
                # Concurrent modification detected - abort to prevent data loss
                return False

        # Apply merge strategy
        if strategy == "replace":
            # Simply replace - straightforward approach
            if memory_entry:
                idx = self.current_progress.index(memory_entry)
                self.current_progress[idx] = new_entry
            else:
                self.current_progress.append(new_entry)
            return True

        elif strategy == "accumulate":
            # Non-destructive: sum numeric fields
            if memory_entry:
                idx = self.current_progress.index(memory_entry)
                merged = memory_entry.copy()
                merged["steps"] = memory_entry.get("steps", 0) + new_entry.get("steps", 0)
                merged["time"] = memory_entry.get("time", 0) + new_entry.get("time", 0)
                merged["cards"] = memory_entry.get("cards", 0) + new_entry.get("cards", 0)
                self.current_progress[idx] = merged
            else:
                self.current_progress.append(new_entry)
            return True

        else:  # strategy == "smart"
            # Merge without data loss: use file state as baseline, add new data
            if not memory_entry and not file_entry:
                self.current_progress.append(new_entry)
            elif memory_entry and not file_entry:
                # File was cleaned, but memory has entry - keep memory version
                pass  # Already in memory
            elif file_entry and not memory_entry:
                # File has entry, memory doesn't - add it to memory for consistency
                self.current_progress.append(file_entry)
            # If both exist and are same (no conflict), new_entry replaces it
            else:
                idx = self.current_progress.index(memory_entry)
                self.current_progress[idx] = new_entry

            return True

    def save_daily_progress(self, data: dict, merge_strategy: str = "smart") -> bool:
        """Save or update daily progress entry with intelligent merging.

        Uses merge_progress() to intelligently combine new data with file state
        without losing data from concurrent modifications (if strategy="smart").
        This prevents the reload-on-save pattern from losing in-memory changes.

        Args:
            data: Progress entry with date, steps, time, cards (required keys:
                  date, steps, time, cards)
            merge_strategy: How to handle existing entries for the same date:
                - "smart" (default): Detects concurrent mods, aborts if detected
                - "replace": Always overwrites existing entry (destructive)
                - "accumulate": Non-destructive - adds to existing numeric fields

        Returns:
            True if save successful, False if concurrent modification detected
                 (only with strategy="smart")

        Example:
            # Smart merge - safe for concurrent access, aborts on conflicts
            if not progress_mgr.save_daily_progress(
                {"date": "2024-01-10", "steps": 1000, "time": 30, "cards": 10}
            ):
                print("Concurrent modification detected - retry")

            # Non-destructive accumulation (no data loss)
            progress_mgr.save_daily_progress(
                {"date": "2024-01-10", "steps": 500, "time": 15, "cards": 5},
                merge_strategy="accumulate"
            )

            # Simple replace (overwrites silently)
            progress_mgr.save_daily_progress(
                {"date": "2024-01-10", "steps": 5000, "time": 120, "cards": 50},
                merge_strategy="replace"
            )
        """
        # Don't save if progress is invalid
        if not self.is_valid_progress(data):
            return False

        # Merge with intelligent strategy
        merge_successful = self.merge_progress(data, strategy=merge_strategy)
        
        if merge_strategy == "smart" and not merge_successful:
            # Concurrent modification detected - abort to prevent data loss
            return False

        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.file_path.open("w") as file:
                json.dump(self.current_progress, file, indent=2)
            return True
        except OSError as e:
            raise IOError(f"Error writing progress: {self.file_path}") from e

    def get_progress_by_date(self, date_str: str) -> dict | None:
        """Get progress entry for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            Progress entry or None if not found
        """
        if self.current_progress == []:
            self.load_progress()
        for entry in self.current_progress:
            if entry.get("date") == date_str:
                return entry.copy()
        return None

    def get_yesterday_progress(self) -> dict | None:
        """Get progress entry for yesterday.

        Returns:
            Progress entry or None if not found
        """
        if self.current_progress == []:
            self.load_progress()
        return self.get_progress_by_date(self.get_yesterday_date())

    def get_today_date(self) -> str:
        """Get today's date in YYYY-MM-DD format.

        Returns:
            Today's date string
        """
        return date.today().strftime("%Y-%m-%d")

    def get_yesterday_date(self) -> str:
        """Get yesterday's date in YYYY-MM-DD format.

        Returns:
            Yesterday's date string
        """
        yesterday = date.today() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")

    def add_completed_exercise(self, date_str: str, exercise_id: str) -> bool:
        """Add a completed exercise to a specific date's progress.

        Given: A date and exercise ID
        When: Adding an exercise to the completed list
        Then: The exercise is added to exercises_done array for that date

        Args:
            date_str: Date in YYYY-MM-DD format
            exercise_id: Unique identifier for the exercise

        Returns:
            True if successfully added, False otherwise
        """
        # Load current progress if not loaded
        if not self.current_progress:
            self.load_progress()

        # Find or create entry for this date
        entry = None
        for progress_entry in self.current_progress:
            if progress_entry.get("date") == date_str:
                entry = progress_entry
                break

        if entry is None:
            # Create new entry with default values
            entry = {
                "date": date_str,
                "steps": 0,
                "time": 0,
                "cards": 0,
                "exercises_done": []
            }
            self.current_progress.append(entry)
        
        # Ensure exercises_done exists
        if "exercises_done" not in entry:
            entry["exercises_done"] = []
        
        # Add exercise ID if not already present
        if exercise_id not in entry["exercises_done"]:
            entry["exercises_done"].append(exercise_id)
        
        # Save to file
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.file_path.open("w") as file:
                json.dump(self.current_progress, file, indent=2)
            return True
        except OSError as e:
            raise IOError(f"Error writing progress: {self.file_path}") from e

    def get_completed_exercises(self, date_str: str) -> list[str]:
        """Get list of completed exercise IDs for a specific date.

        Given: A date string
        When: Retrieving completed exercises
        Then: Returns list of exercise IDs completed on that date

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            List of exercise IDs completed on that date, empty list if none
        """
        # Load current progress if not loaded
        if not self.current_progress:
            self.load_progress()

        # Find entry for this date
        for entry in self.current_progress:
            if entry.get("date") == date_str:
                return entry.get("exercises_done", []).copy()
        
        return []

    def is_exercise_completed(self, date_str: str, exercise_id: str) -> bool:
        """Check if a specific exercise was completed on a given date.

        Given: A date and exercise ID
        When: Checking completion status
        Then: Returns True if exercise was completed on that date

        Args:
            date_str: Date in YYYY-MM-DD format
            exercise_id: Unique identifier for the exercise

        Returns:
            True if exercise was completed on that date, False otherwise
        """
        completed = self.get_completed_exercises(date_str)
        return exercise_id in completed


class MetricsManager:
    """Manage aggregated metrics with JSON file persistence.
    
    Responsibilities:
    - Calculate streak (consecutive days of activity)
    - Calculate average time per day
    - Calculate total cards created
    - Update aggregated metrics from progress history
    - Provide metrics for Review step display
    """

    def __init__(self, path=METRICS_FILE):
        """Initialize MetricsManager with file path.

        Args:
            path: Path to metrics file (default: storage/.metrics.json)
        """
        self.file_path = Path(path)
        self.current_metrics: dict = {"streak": 0, "avg_time": 0.0, "total_cards": 0}

    def load_metrics(self) -> dict:
        """Load metrics from JSON file.

        Returns:
            Dict with streak, avg_time, total_cards or defaults if file doesn't exist
        """
        if not self.file_path.exists():
            return {"streak": 0, "avg_time": 0.0, "total_cards": 0}

        try:
            with self.file_path.open("r") as file:
                content = file.read().strip()
                if not content:
                    return {"streak": 0, "avg_time": 0.0, "total_cards": 0}
                
                metrics = json.loads(content)
                # Fill missing fields with defaults
                default = {"streak": 0, "avg_time": 0.0, "total_cards": 0}
                return {**default, **metrics}
        except (json.JSONDecodeError, OSError):
            return {"streak": 0, "avg_time": 0.0, "total_cards": 0}

    def save_metrics(self) -> None:
        """Save current metrics to JSON file with pretty formatting."""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.file_path.open("w") as file:
                json.dump(self.current_metrics, file, indent=2)
        except OSError as e:
            raise IOError(f"Error writing metrics: {self.file_path}") from e

    def calculate_streak(self, progress_data: list) -> int:
        """Calculate consecutive days of activity ending today or yesterday.

        Args:
            progress_data: List of progress entries [{date, steps, time, cards}, ...]

        Returns:
            Number of consecutive days with activity
        """
        if not progress_data:
            return 0

        # Sort by date descending (most recent first)
        sorted_progress = sorted(
            progress_data,
            key=lambda x: x.get("date", ""),
            reverse=True
        )

        today = date.today()
        streak = 0
        expected_date = today

        for entry in sorted_progress:
            entry_date = date.fromisoformat(entry.get("date", ""))
            
            if entry_date == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            elif entry_date == expected_date - timedelta(days=1):
                # Allow for today not having progress yet
                expected_date = entry_date
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            else:
                # Gap found, stop counting
                break

        return streak

    def get_average_time(self, progress_data: list, last_n_days: int | None = None) -> float:
        """Calculate average time per day from progress data.

        Args:
            progress_data: List of progress entries [{date, steps, time, cards}, ...]
            last_n_days: If provided, only average last N days (default: all days)

        Returns:
            Average time in hours as float, rounded to 2 decimals
        """
        if not progress_data:
            return 0.0

        # Filter to last N days if specified
        if last_n_days:
            sorted_progress = sorted(
                progress_data,
                key=lambda x: x.get("date", ""),
                reverse=True
            )
            progress_data = sorted_progress[:last_n_days]

        total_time = sum(entry.get("time", 0.0) for entry in progress_data)
        count = len(progress_data)

        if count == 0:
            return 0.0

        return round(total_time / count, 2)

    def get_total_cards(self, progress_data: list) -> int:
        """Calculate total cards created from progress data.

        Args:
            progress_data: List of progress entries [{date, steps, time, cards}, ...]

        Returns:
            Sum of all cards created across all days
        """
        if not progress_data:
            return 0

        return sum(entry.get("cards", 0) for entry in progress_data)

    def update_metrics(self, progress_data: list) -> None:
        """Update all metrics from progress data and save to file.

        Args:
            progress_data: List of progress entries from ProgressManager
        """
        self.current_metrics = {
            "streak": self.calculate_streak(progress_data),
            "avg_time": self.get_average_time(progress_data),
            "total_cards": self.get_total_cards(progress_data)
        }
        self.save_metrics()

    def get_metrics_summary(self) -> dict:
        """Get formatted metrics summary for display.

        Returns:
            Dict with metrics including formatted time string
        """
        avg_hours = self.current_metrics.get("avg_time", 0.0)
        hours = int(avg_hours)
        minutes = int((avg_hours - hours) * 60)
        
        return {
            **self.current_metrics,
            "avg_time_formatted": f"{hours}h {minutes:02d}min"
        }

