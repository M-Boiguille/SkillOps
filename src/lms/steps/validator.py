"""Mission validation utilities (local checks & AI reviews)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.lms.classes.mission import Mission


@dataclass
class ValidationResult:
    """Represents validation outcomes for a mission."""

    passed: bool
    checks_run: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)


def validate_mission(mission: Mission) -> ValidationResult:
    """Run local checks and AI review placeholders for a mission.

    Args:
        mission: Mission to validate.

    Returns:
        ValidationResult with status and check details.
    """
    checks_run = mission.validators or []
    if not checks_run:
        return ValidationResult(passed=True, checks_run=[], failures=[])

    # Placeholder: assume validations pass until checks are implemented.
    return ValidationResult(passed=True, checks_run=checks_run, failures=[])
