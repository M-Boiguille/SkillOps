"""State management for SkillOps using YAML persistence."""

from pathlib import Path
import yaml

# Constants to define default storage paths
BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
STATE_FILE = STORAGE_DIR / ".state.yaml"


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

    def is_valid_state(self, state: dict | None) -> bool:
        """Check if state has all required keys.

        Args:
            state: State dictionary to validate

        Returns:
            True if state has session_id, step_id, timestamp keys
        """
        if state is None:
            return False
        # State is valid if it has all required keys
        return {"session_id", "step_id", "timestamp"}.issubset(state.keys())

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
