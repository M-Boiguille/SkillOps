"""Error aggregation and deduplication for automated monitoring."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from hashlib import md5
from pathlib import Path
from typing import Dict, List, Optional


class ErrorAggregator:
    """Aggregates and deduplicates errors to prevent alert spam.

    Same error within 24h window = single alert instead of multiple.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize error aggregator.

        Args:
            storage_path: Directory to store error logs.
                          Defaults to ~/.local/share/skillops
        """
        if storage_path is None:
            storage_path = Path.home() / ".local/share/skillops"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.error_log_file = self.storage_path / ".errors.json"

    def _compute_error_hash(self, error_type: str, step_id: str, message: str) -> str:
        """Create hash fingerprint for error deduplication."""
        fingerprint = f"{error_type}:{step_id}:{message}"
        return md5(fingerprint.encode()).hexdigest()

    def _load_errors(self) -> Dict[str, List[Dict]]:
        """Load error log from JSON file."""
        if not self.error_log_file.exists():
            return {}

        try:
            with open(self.error_log_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_errors(self, errors: Dict[str, List[Dict]]) -> None:
        """Save error log to JSON file."""
        with open(self.error_log_file, "w") as f:
            json.dump(errors, f, indent=2, default=str)

    def _prune_old_errors(self, errors: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Remove errors older than 24 hours."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        pruned = {}

        for error_hash, occurrences in errors.items():
            recent = []
            for occurrence in occurrences:
                occurrence_time = datetime.fromisoformat(
                    occurrence.get("timestamp", "")
                )
                if occurrence_time > cutoff_time:
                    recent.append(occurrence)

            if recent:
                pruned[error_hash] = recent

        return pruned

    def record_error(
        self,
        error: Exception,
        step_id: str,
        retry_count: int = 0,
        context: Optional[Dict] = None,
    ) -> bool:
        """Record error occurrence.

        Args:
            error: The exception object
            step_id: Which step failed (e.g., 'create', 'share', 'notify')
            retry_count: Number of retry attempts (for context)
            context: Additional context (API response, etc)

        Returns:
            True if this is a new error (first occurrence in 24h window)
        """
        error_type = type(error).__name__
        message = str(error)
        error_hash = self._compute_error_hash(error_type, step_id, message)

        errors = self._load_errors()
        errors = self._prune_old_errors(errors)

        is_new = error_hash not in errors
        if not errors.get(error_hash):
            errors[error_hash] = []

        occurrence = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "step_id": step_id,
            "message": message,
            "retry_count": retry_count,
            "context": context or {},
        }
        errors[error_hash].append(occurrence)

        self._save_errors(errors)
        return is_new

    def get_daily_summary(self) -> Dict[str, List[Dict]]:
        """Get all errors from past 24 hours grouped by hash.

        Returns:
            Dict of {error_hash: [occurrences]}
        """
        errors = self._load_errors()
        return self._prune_old_errors(errors)

    def get_summary_by_step(self) -> Dict[str, Dict]:
        """Get error summary grouped by step.

        Returns:
            Dict of {step_id: {count: int, types: [error_type],
                               sample: str}}
        """
        summary = {}
        errors = self.get_daily_summary()

        for error_hash, occurrences in errors.items():
            if not occurrences:
                continue

            step_id = occurrences[0]["step_id"]
            error_type = occurrences[0]["type"]
            message = occurrences[0]["message"]
            if step_id not in summary:
                summary[step_id] = {
                    "count": 0,
                    "types": [],
                    "sample_message": "",
                }

            count_val = summary[step_id]["count"]
            assert isinstance(count_val, int)
            summary[step_id]["count"] = count_val + len(occurrences)
            types_list = summary[step_id]["types"]
            assert isinstance(types_list, list)
            if error_type not in types_list:
                types_list.append(error_type)
            summary[step_id]["sample_message"] = message

        return summary

    def critical_errors_today(self) -> bool:
        """Check if any critical error occurred today.

        Returns:
            True if errors exist in 24h window
        """
        return bool(self.get_daily_summary())

    def clear_errors(self) -> None:
        """Clear all recorded errors."""
        if self.error_log_file.exists():
            self.error_log_file.unlink()

    def get_error_count(self) -> int:
        """Get total unique errors in 24h window."""
        return len(self.get_daily_summary())
