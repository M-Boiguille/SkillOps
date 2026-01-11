#!/usr/bin/env python3
"""Entry point script for SkillOps CLI application."""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import must be after path modification  # noqa: E402
from lms.main import app  # noqa: E402

if __name__ == "__main__":
    app()
