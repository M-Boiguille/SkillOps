"""Quiz command: SQLite-native flashcards (Phase 2a)."""

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
from src.lms.database import get_connection, get_logical_date, init_db

console = Console()


@dataclass
class QuizCard:
    question: str
    answer: str


def _offline_cards(topic: str, count: int) -> List[QuizCard]:
    base = [
        QuizCard(
            question=f"Définis {topic} en une phrase.",
            answer="Une définition claire et concise.",
        ),
        QuizCard(
            question=f"Donne un exemple concret d'utilisation de {topic}.",
            answer="Un cas réel avec contexte et bénéfice.",
        ),
        QuizCard(
            question=f"Quel est un piège courant avec {topic} ?",
            answer="Un problème classique et comment l'éviter.",
        ),
        QuizCard(
            question=f"Quels concepts sont liés à {topic} ?",
            answer="Deux notions connexes et leur relation.",
        ),
        QuizCard(
            question=f"Explique {topic} à un junior.",
            answer="Une analogie simple et claire.",
        ),
    ]
    random.shuffle(base)
    return base[: max(1, min(count, len(base)))]


def _get_gemini_client() -> Any:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    import importlib

    genai_module = importlib.import_module("google.genai")
    return genai_module.Client(api_key=api_key)


def _parse_cards(payload: str, fallback: List[QuizCard]) -> List[QuizCard]:
    try:
        data = json.loads(payload)
        items = [
            QuizCard(question=item["question"], answer=item["answer"])
            for item in data
            if isinstance(item, dict) and "question" in item and "answer" in item
        ]
        if items:
            return items
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return fallback


def _generate_cards(topic: str, count: int) -> List[QuizCard]:
    offline = os.getenv("SKILLOPS_QUIZ_OFFLINE", "").lower() in {
        "1",
        "true",
        "yes",
    }
    fallback = _offline_cards(topic, count)
    if offline or not os.getenv("GEMINI_API_KEY"):
        return fallback

    prompt = (
        "Tu es un formateur DevOps. "
        f"Génère {count} cartes Q/R sur: {topic}. "
        "Réponds strictement en JSON: "
        '[{"question": "...", "answer": "..."}].'
    )

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=get_gemini_model(),
            contents=prompt,
        )
        return _parse_cards(response.text, fallback)
    except Exception:
        return fallback


def _insert_cards(
    topic: str,
    cards: List[QuizCard],
    storage_path: Optional[Path] = None,
) -> None:
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    for card in cards:
        cursor.execute(
            """
            INSERT INTO quiz_cards (topic, question, answer)
            VALUES (?, ?, ?)
            """,
            (topic, card.question, card.answer),
        )
    conn.commit()
    conn.close()


def _load_due_cards(
    topic: str,
    count: int,
    storage_path: Optional[Path] = None,
) -> List[dict]:
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    today = get_logical_date()
    cursor.execute(
        """
        SELECT id, question, answer, review_count
        FROM quiz_cards
        WHERE topic = ? AND (last_reviewed IS NULL OR date(last_reviewed) < ?)
        ORDER BY review_count ASC, id ASC
        LIMIT ?
        """,
        (topic, today, count),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "review_count": row[3] or 0,
        }
        for row in rows
    ]


def _mark_reviewed(card_ids: List[int], storage_path: Optional[Path] = None) -> None:
    if not card_ids:
        return
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    today = get_logical_date()
    cursor.executemany(
        """
        UPDATE quiz_cards
        SET last_reviewed = ?, review_count = review_count + 1
        WHERE id = ?
        """,
        [(today, card_id) for card_id in card_ids],
    )
    conn.commit()
    conn.close()


def run_quiz(
    topic: str,
    count: int = 5,
    storage_path: Optional[Path] = None,
    generate_if_empty: bool = True,
) -> None:
    """Run the quiz command using SQLite cards."""
    init_db(storage_path=storage_path)

    cards = _load_due_cards(topic, count, storage_path=storage_path)
    if not cards and generate_if_empty:
        generated = _generate_cards(topic, count)
        _insert_cards(topic, generated, storage_path=storage_path)
        cards = _load_due_cards(topic, count, storage_path=storage_path)

    if not cards:
        console.print(
            Panel(
                "Aucune carte disponible pour ce sujet.",
                border_style="yellow",
            )
        )
        return

    console.clear()
    console.print(Panel.fit(f"🗂️ Quiz • {topic}", style="bold cyan"))

    reviewed_ids: List[int] = []
    for index, card in enumerate(cards, start=1):
        console.print(f"\n[bold]Q{index}.[/bold] {card['question']}")
        _ = Prompt.ask("❯ ")
        console.print(
            Panel(
                f"[bold]Réponse attendue :[/bold]\n{card['answer']}",
                border_style="blue",
            )
        )
        reviewed_ids.append(card["id"])

    _mark_reviewed(reviewed_ids, storage_path=storage_path)

    console.print(
        Panel(
            f"✅ Quiz terminé. Cartes revues: {len(reviewed_ids)}",
            border_style="green",
        )
    )
