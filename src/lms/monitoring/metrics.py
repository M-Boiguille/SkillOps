"""Performance metrics collection for SkillOps."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, Optional


class MetricsCollector:
    """Collects and aggregates execution metrics for performance tracking."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize metrics collector.

        Args:
            storage_path: Directory to store metrics.
                          Defaults to ~/.local/share/skillops
        """
        if storage_path is None:
            storage_path = Path.home() / ".local/share/skillops"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.storage_path / ".metrics.json"

    def _load_metrics(self) -> Dict:
        """Load metrics from JSON file."""
        if not self.metrics_file.exists():
            return {"executions": []}

        try:
            with open(self.metrics_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"executions": []}

    def _save_metrics(self, metrics: Dict) -> None:
        """Save metrics to JSON file."""
        with open(self.metrics_file, "w") as f:
            json.dump(metrics, f, indent=2, default=str)

    def record_step_execution(
        self,
        step_id: str,
        duration_seconds: float,
        success: bool,
        api_calls: int = 0,
        items_processed: int = 0,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Record step execution metrics.

        Args:
            step_id: Step identifier (e.g., 'create', 'share', 'notify')
            duration_seconds: Execution time in seconds
            success: Whether execution succeeded
            api_calls: Number of API calls made
            items_processed: Items processed (decks, repos, etc)
            metadata: Additional context (error type, retry count, etc)
        """
        metrics = self._load_metrics()

        execution = {
            "timestamp": datetime.now().isoformat(),
            "step_id": step_id,
            "duration_seconds": duration_seconds,
            "success": success,
            "api_calls": api_calls,
            "items_processed": items_processed,
            "metadata": metadata or {},
        }

        metrics["executions"].append(execution)
        self._save_metrics(metrics)

    def get_daily_metrics(self, hours: int = 24) -> Dict[str, Dict]:
        """Get aggregated metrics for past N hours.

        Args:
            hours: Time window in hours (default 24)

        Returns:
            Dict with per-step statistics
        """
        from datetime import timedelta

        metrics = self._load_metrics()
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_executions = [
            e
            for e in metrics["executions"]
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        if not recent_executions:
            return {}

        # Group by step_id
        by_step: Dict[str, list] = {}
        for execution in recent_executions:
            step_id = execution["step_id"]
            if step_id not in by_step:
                by_step[step_id] = []
            by_step[step_id].append(execution)

        # Compute stats per step
        stats = {}
        for step_id, executions in by_step.items():
            durations = [e["duration_seconds"] for e in executions]
            successful = sum(1 for e in executions if e["success"])
            total = len(executions)

            stats[step_id] = {
                "executions": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": successful / total if total > 0 else 0,
                "avg_duration_seconds": mean(durations) if durations else 0,
                "min_duration_seconds": min(durations) if durations else 0,
                "max_duration_seconds": max(durations) if durations else 0,
                "std_dev_seconds": stdev(durations) if len(durations) > 1 else 0,
                "total_api_calls": sum(e.get("api_calls", 0) for e in executions),
                "total_items_processed": sum(
                    e.get("items_processed", 0) for e in executions
                ),
            }

        return stats

    def get_step_history(self, step_id: str, limit: int = 10) -> list:
        """Get execution history for specific step.

        Args:
            step_id: Step to retrieve history for
            limit: Maximum number of executions to return

        Returns:
            List of execution records (most recent first)
        """
        metrics = self._load_metrics()
        executions = [e for e in metrics["executions"] if e["step_id"] == step_id]
        return executions[-limit:][::-1]  # Reverse for most recent first

    def get_overall_stats(self) -> Dict:
        """Get overall application statistics.

        Returns:
            Dict with total executions, success rate, average duration, etc
        """
        metrics = self._load_metrics()
        executions = metrics.get("executions", [])

        if not executions:
            return {
                "total_executions": 0,
                "total_successful": 0,
                "total_failed": 0,
                "success_rate": 0,
                "avg_duration_seconds": 0,
            }

        durations = [e["duration_seconds"] for e in executions]
        successful = sum(1 for e in executions if e["success"])
        total = len(executions)

        return {
            "total_executions": total,
            "total_successful": successful,
            "total_failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_duration_seconds": mean(durations),
            "total_api_calls": sum(e.get("api_calls", 0) for e in executions),
            "total_items_processed": sum(
                e.get("items_processed", 0) for e in executions
            ),
        }

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        if self.metrics_file.exists():
            self.metrics_file.unlink()
