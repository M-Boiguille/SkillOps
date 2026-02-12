"""Code command: passive tracking placeholder (Phase 1)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console

from src.lms.database import get_current_session_id, init_db
from src.lms.display import display_info_panel

console = Console()


def run_code(storage_path: Optional[Path] = None) -> None:
    """Run the code command (Phase 1 placeholder)."""
    init_db(storage_path=storage_path)
    get_current_session_id(storage_path=storage_path)

    display_info_panel(
        "Mode code (Phase 1)",
        "Le tracking passif sera activé en Phase 3 (git hooks + WakaTime).\n"
        "Pour l'instant, cette commande confirme la session du jour.",
        border_color="cyan",
    )
