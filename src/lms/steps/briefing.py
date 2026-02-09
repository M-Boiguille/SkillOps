"""Technical Briefing step - AI-powered Q&A for mission preparation."""

from __future__ import annotations

import os
from typing import Optional

from google import genai
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.lms.display import (
    display_error_message,
    display_info_panel,
    display_section_header,
)

console = Console()


def _get_api_key() -> Optional[str]:
    return os.getenv("GEMINI_API_KEY")


def technical_briefing_step(context: Optional[str] = None) -> None:
    """Run a Technical Briefing session.

    Args:
        context: Optional mission context to inject into the prompt.
    """
    display_section_header("Technical Briefing", "🧠")

    api_key = _get_api_key()
    if not api_key:
        display_error_message(
            "GEMINI_API_KEY introuvable",
            "Configurez GEMINI_API_KEY pour activer le briefing technique.",
        )
        return

    question = Prompt.ask("Votre question (ex: multi-stage build)")
    if not question.strip():
        display_error_message("Question vide", "Veuillez préciser votre besoin.")
        return

    prompt = """Tu es un Senior DevOps. Donne une réponse claire, structurée et courte.
- Commence par une définition concise.
- Ajoute 2-3 points clés.
- Donne un exemple concret (code ou commande si pertinent).
- Termine par 1-2 next steps.
"""

    if context:
        prompt += f"\nContexte de mission: {context}\n"

    prompt += f"\nQuestion: {question}\n"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        answer = response.text if response and response.text else ""
    except Exception as exc:  # pragma: no cover - passthrough
        display_error_message("Briefing échoué", f"Erreur: {exc}")
        return

    if not answer:
        display_error_message("Briefing vide", "Aucune réponse reçue.")
        return

    console.print(Panel(answer, title="🧠 Technical Briefing", border_style="cyan"))
    display_info_panel("Tip", "Utilise ce briefing pour cadrer ta mission.", "green")
