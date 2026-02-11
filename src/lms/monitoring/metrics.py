"""Performance metrics collection for SkillOps."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from statistics import mean, stdev
from pathlib import Path
from typing import Dict, Optional

from src.lms.database import get_connection, init_db


class MetricsCollector:
    """Collects and aggregates execution metrics for performance tracking."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize metrics collector.

        Args:
            storage_path: Directory to store metrics (SQLite DB).
        """
        if isinstance(storage_path, str):
            storage_path = Path(storage_path)
        self.storage_path = storage_path
        init_db(self.storage_path)

    def _load_executions(self) -> list[dict]:
        conn = get_connection(self.storage_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, step_id, duration_seconds, success, api_calls, "
            "items_processed, metadata FROM performance_metrics"
        )
        rows = cursor.fetchall()
        conn.close()

        executions = []
        for row in rows:
            metadata = {}
            if row[6]:
                try:
                    metadata = json.loads(row[6])
                except json.JSONDecodeError:
                    metadata = {}
            executions.append(
                {
                    "timestamp": row[0],
                    "step_id": row[1],
                    "duration_seconds": float(row[2]),
                    "success": bool(row[3]),
                    "api_calls": int(row[4] or 0),
                    "items_processed": int(row[5] or 0),
                    "metadata": metadata,
                }
            )
        return executions

    def _load_metrics(self) -> Dict[str, list]:
        """Backward-compatible wrapper for legacy tests."""
        return {"executions": self._load_executions()}

    def record_step_execution(
        self,
        step_id: str,
        duration_seconds: float,
        success: bool,
        api_calls: int = 0,
        items_processed: int = 0,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Record step execution metrics."""
        conn = get_connection(self.storage_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO performance_metrics
            (timestamp, step_id, duration_seconds, success, api_calls, items_processed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                step_id,
                float(duration_seconds),
                bool(success),
                int(api_calls),
                int(items_processed),
                json.dumps(metadata or {}),
            ),
        )
        conn.commit()
        conn.close()

    def get_daily_metrics(self, hours: int = 24) -> Dict[str, Dict]:
        """Get aggregated metrics for past N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        executions = [
            e
            for e in self._load_executions()
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]

        if not executions:
            return {}

        by_step: Dict[str, list] = {}
        for execution in executions:
            by_step.setdefault(execution["step_id"], []).append(execution)

        stats = {}
        for step_id, step_execs in by_step.items():
            durations = [e["duration_seconds"] for e in step_execs]
            successful = sum(1 for e in step_execs if e["success"])
            total = len(step_execs)

            stats[step_id] = {
                "executions": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": successful / total if total > 0 else 0,
                "avg_duration_seconds": mean(durations) if durations else 0,
                "min_duration_seconds": min(durations) if durations else 0,
                "max_duration_seconds": max(durations) if durations else 0,
                "std_dev_seconds": stdev(durations) if len(durations) > 1 else 0,
                "total_api_calls": sum(e.get("api_calls", 0) for e in step_execs),
                "total_items_processed": sum(
                    e.get("items_processed", 0) for e in step_execs
                ),
            }

        return stats

    def get_step_history(self, step_id: str, limit: int = 10) -> list:
        """Get execution history for specific step."""
        executions = [e for e in self._load_executions() if e["step_id"] == step_id]
        return executions[-limit:][::-1]

    def get_overall_stats(self) -> Dict:
        """Get overall application statistics."""
        executions = self._load_executions()

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
        conn = get_connection(self.storage_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM performance_metrics")
        conn.commit()
        conn.close()
