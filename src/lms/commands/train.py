"""Train command: lightweight learning + quiz flow."""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.lms.ai_config import get_gemini_model
from src.lms.database import get_current_session_id, init_db

console = Console()


@dataclass
class QuizItem:
    question: str
    answer: str


def _offline_questions(topic: str, count: int) -> List[QuizItem]:
    base_questions = [
        QuizItem(
            question=f"Explique {topic} en une phrase simple.",
            answer="Une définition claire, simple, sans jargon.",
        ),
        QuizItem(
            question=f"Donne un exemple concret d'utilisation de {topic}.",
            answer="Un cas réel avec contexte et bénéfices.",
        ),
        QuizItem(
            question=f"Quelle erreur fréquente autour de {topic} ?",
            answer="Un piège classique et comment l'éviter.",
        ),
        QuizItem(
            question=f"Quels sont 2 concepts liés à {topic} ?",
            answer="Deux notions connexes et leur relation.",
        ),
        QuizItem(
            question=f"Comment expliquer {topic} à un junior ?",
            answer="Une analogie ou métaphore simple.",
        ),
    ]
    random.shuffle(base_questions)
    return base_questions[: max(1, min(count, len(base_questions)))]


def _get_gemini_client() -> Any:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    import importlib

    genai_module = importlib.import_module("google.genai")
    return genai_module.Client(api_key=api_key)


def _parse_questions(payload: str, fallback: List[QuizItem]) -> List[QuizItem]:
    try:
        data = json.loads(payload)
        items = [
            QuizItem(question=item["question"], answer=item["answer"])
            for item in data
            if isinstance(item, dict) and "question" in item and "answer" in item
        ]
        if items:
            return items
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return fallback


def _generate_questions(topic: str, count: int) -> List[QuizItem]:
    offline = os.getenv("SKILLOPS_TRAIN_OFFLINE", "").lower() in {
        "1",
        "true",
        "yes",
    }
    fallback = _offline_questions(topic, count)
    if offline or not os.getenv("GEMINI_API_KEY"):
        return fallback

    prompt = (
        "Tu es un formateur DevOps. "
        f"Génère {count} questions + réponses concises sur: {topic}. "
        "Réponds strictement en JSON: "
        '[{"question": "...", "answer": "..."}].'
    )

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=get_gemini_model(),
            contents=prompt,
        )
        return _parse_questions(response.text, fallback)
    except Exception:
        return fallback


def run_train(
    topic: str,
    questions: int = 3,
    storage_path: Optional[Path] = None,
) -> None:
    """Run the train command with a lightweight quiz flow."""
    init_db(storage_path=storage_path)
    get_current_session_id(storage_path=storage_path)
    console.clear()
    console.print(Panel.fit(f"🧠 Train • {topic}", style="bold cyan"))

    items = _generate_questions(topic, questions)
    correct_like = 0

    for index, item in enumerate(items, start=1):
        console.print(f"\n[bold]Q{index}.[/bold] {item.question}")
        user_answer = Prompt.ask("❯ ")
        if user_answer.strip():
            correct_like += 1
        console.print(
            Panel(
                f"[bold]Réponse attendue :[/bold]\n{item.answer}",
                border_style="blue",
            )
        )

    console.print(
        Panel(
            f"✅ Session terminée. Réponses saisies: {correct_like}/{len(items)}",
            border_style="green",
        )
    )
