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

    def save_daily_progress(self, data: dict) -> None:
        """Save or update daily progress entry.

        Args:
            data: Progress entry with date, steps, time, cards
        """
        # Don't save if progress is invalid
        if not self.is_valid_progress(data):
            return

        # Load current progress first to avoid overwriting
        self.load_progress()

        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if entry for this date already exists
        existing_entry = self.get_progress_by_date(data["date"])
        
        if existing_entry:
            # Update existing entry
            for i, entry in enumerate(self.current_progress):
                if entry["date"] == data["date"]:
                    self.current_progress[i] = data
                    break
        else:
            # Add new entry
            self.current_progress.append(data)

        try:
            with self.file_path.open("w") as file:
                json.dump(self.current_progress, file, indent=2)
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
