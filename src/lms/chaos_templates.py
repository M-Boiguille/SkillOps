"""Adaptive chaos templates and feedback helpers."""

from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.lms.ai_config import get_gemini_model
from src.lms.database import get_connection, init_db

TEMPLATES_DIR = Path(__file__).parent / "chaos_templates"


def load_templates() -> List[Dict[str, Any]]:
    """Load all YAML templates from disk."""
    templates: List[Dict[str, Any]] = []
    if not TEMPLATES_DIR.exists():
        return templates

    for path in sorted(TEMPLATES_DIR.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
            if data:
                data["_source"] = path.name
                templates.append(data)
    return templates


def _deserialize_topics(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(item).strip().lower() for item in data if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [part.strip().lower() for part in raw.split(",") if part.strip()]


def get_learning_profile(
    user_id: str,
    storage_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Fetch a user's learning profile from SQLite."""
    init_db(storage_path=storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT current_topics, recent_achievements, learning_difficulty
        FROM user_learning_profile
        WHERE user_id = ?
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "current_topics": [],
            "recent_achievements": None,
            "learning_difficulty": None,
        }

    return {
        "current_topics": _deserialize_topics(row[0]),
        "recent_achievements": row[1],
        "learning_difficulty": row[2],
    }


def upsert_learning_profile(
    user_id: str,
    current_topics: List[str],
    learning_difficulty: str = "beginner",
    storage_path: Optional[Path] = None,
) -> None:
    """Create or update learning profile topics."""
    init_db(storage_path=storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_learning_profile (user_id, current_topics, learning_difficulty)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            current_topics = excluded.current_topics,
            learning_difficulty = excluded.learning_difficulty
        """,
        (user_id, json.dumps(current_topics), learning_difficulty),
    )
    conn.commit()
    conn.close()


def pick_chaos_template(
    user_id: str,
    storage_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Pick a template matching user's topics (fallback to any)."""
    templates = load_templates()
    if not templates:
        return {}

    profile = get_learning_profile(user_id, storage_path=storage_path)
    topics = {t.lower() for t in profile.get("current_topics", [])}

    if topics:
        matched = [
            t
            for t in templates
            if topics.intersection({x.lower() for x in t.get("learning_topics", [])})
        ]
        if matched:
            return random.choice(matched)

    return random.choice(templates)


def apply_chaos(template: Dict[str, Any]) -> str:
    """Return the bug-injected manifest for display."""
    return str(template.get("bug_inject", ""))


def _get_gemini_client() -> Any:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    import importlib

    genai_module = importlib.import_module("google.genai")
    return genai_module.Client(api_key=api_key)


def get_ai_feedback(user_answer: str, template: Dict[str, Any]) -> Dict[str, Any]:
    """Get AI feedback about the user's fix attempt."""
    offline = os.getenv("SKILLOPS_CHAOS_OFFLINE", "").lower() in {"1", "true", "yes"}
    expected = template.get("expected_solution", "")

    if offline or not os.getenv("GEMINI_API_KEY"):
        success = expected and expected.lower() in user_answer.lower()
        return {
            "success": bool(success),
            "feedback": (
                "✅ Correct." if success else f"Indice: {expected or 'Réessaie.'}"
            ),
        }

    prompt = (
        "Tu es un expert DevOps. Évalue la réponse utilisateur par rapport à la "
        "solution attendue. Réponds STRICTEMENT en JSON: "
        '{"success": true|false, "feedback": "..."}.\n\n'
        f"BUG: {template.get('description', '')}\n"
        f"Expected fix: {expected}\n"
        f"User answer: {user_answer}"
    )

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=get_gemini_model(),
            contents=prompt,
        )
        data = json.loads(response.text)
        if isinstance(data, dict) and "success" in data and "feedback" in data:
            return data
    except Exception:
        pass

    return {"success": False, "feedback": "Impossible d'analyser la réponse."}


def record_chaos_history(
    user_id: str,
    template: Dict[str, Any],
    user_answer: str,
    feedback: str,
    success: bool,
    storage_path: Optional[Path] = None,
) -> None:
    """Store chaos attempt in history table."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO chaos_history
        (user_id, template_name, attempt_date, user_answer, ai_feedback, success)
        VALUES (?, ?, date('now'), ?, ?, ?)
        """,
        (
            user_id,
            template.get("name", "unknown"),
            user_answer,
            feedback,
            1 if success else 0,
        ),
    )
    conn.commit()
    conn.close()
