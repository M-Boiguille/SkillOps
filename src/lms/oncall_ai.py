"""AI-powered incident generation for on-call training.

Generates contextual incidents based on past performance and skill gaps.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from google import genai

from src.lms.database import get_connection, init_db


@dataclass
class IncidentContext:
    """Context for AI incident generation."""

    past_postmortems: list[dict]
    weak_areas: list[str]
    skill_level: str  # beginner, intermediate, advanced
    recent_chaos_events: list[dict]


def get_incident_context(storage_path: Optional[Path] = None) -> IncidentContext:
    """Build context from past incidents and performance.

    Args:
        storage_path: Custom storage directory

    Returns:
        IncidentContext with historical data
    """
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    # Get recent postmortems
    cursor.execute(
        """
        SELECT root_cause, prevention, action_items
        FROM postmortems
        ORDER BY timestamp DESC
        LIMIT 10
        """
    )
    postmortems = [
        {"root_cause": row[0], "prevention": row[1], "action_items": row[2]}
        for row in cursor.fetchall()
    ]

    # Get weak areas (incidents with low scores or many hints)
    cursor.execute(
        """
        SELECT affected_system, AVG(resolution_score) as avg_score, AVG(hints_used) as avg_hints
        FROM incidents
        WHERE resolution_score IS NOT NULL
        GROUP BY affected_system
        HAVING avg_score < 4 OR avg_hints > 1
        """
    )
    weak_areas = [row[0] for row in cursor.fetchall()]

    # Determine skill level based on average scores
    cursor.execute(
        """
        SELECT AVG(resolution_score)
        FROM incidents
        WHERE resolution_score IS NOT NULL
        """
    )
    row = cursor.fetchone()
    avg_score = row[0] if row and row[0] else 3.0

    if avg_score < 2.5:
        skill_level = "beginner"
    elif avg_score < 4.0:
        skill_level = "intermediate"
    else:
        skill_level = "advanced"

    # Get recent chaos events
    cursor.execute(
        """
        SELECT action, target, status
        FROM chaos_events
        ORDER BY timestamp DESC
        LIMIT 5
        """
    )
    chaos_events = [
        {"action": row[0], "target": row[1], "status": row[2]}
        for row in cursor.fetchall()
    ]

    conn.close()

    return IncidentContext(
        past_postmortems=postmortems,
        weak_areas=weak_areas,
        skill_level=skill_level,
        recent_chaos_events=chaos_events,
    )


def generate_incident_with_ai(
    api_key: Optional[str] = None,
    storage_path: Optional[Path] = None,
    difficulty: Optional[int] = None,
) -> dict:
    """Generate a new incident using AI based on context.

    Args:
        api_key: Gemini API key (or from env)
        storage_path: Custom storage directory
        difficulty: Override difficulty (1-5)

    Returns:
        Incident dict with title, description, symptoms, etc.
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY required for AI incident generation")

    client = genai.Client(api_key=api_key)

    context = get_incident_context(storage_path)

    # Build prompt
    weak_areas_str = ", ".join(context.weak_areas) if context.weak_areas else "None"
    postmortems_str = "\n".join(
        [f"- {pm['root_cause']}" for pm in context.past_postmortems[:3]]
    )

    difficulty_level = difficulty or (
        1
        if context.skill_level == "beginner"
        else 2 if context.skill_level == "intermediate" else 3
    )

    prompt = f"""You are a Senior DevOps engineer creating realistic on-call incidents for training.

User's current level: {context.skill_level}
Weak areas to focus on: {weak_areas_str}
Recent incident root causes:
{postmortems_str if postmortems_str else "No history yet"}

Generate a NEW incident (difficulty {difficulty_level}/5) with these constraints:
- Should be different from past incidents
- Focus on weak areas if identified
- Realistic for a production environment
- Include debugging hints (but don't reveal them directly)

Return a JSON object with:
{{
  "severity": "P1" | "P2" | "P3" | "P4",
  "title": "Brief incident title",
  "description": "What is happening (2-3 sentences)",
  "affected_system": "Kubernetes" | "PostgreSQL" | "Redis" | "Docker" | "Network" | etc.,
  "symptoms": "Observable symptoms (logs, metrics, user reports)",
  "hints": ["hint1", "hint2", "hint3"]
}}

Make it challenging but solvable for a {context.skill_level} DevOps engineer.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", contents=prompt
    )
    text = response.text.strip()

    # Extract JSON from markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    import json

    incident_data = json.loads(text)
    incident_data["difficulty_level"] = difficulty_level
    incident_data["generated_by"] = "ai"

    return incident_data


def generate_hints_for_incident(
    incident_id: int,
    current_hint_level: int,
    api_key: Optional[str] = None,
    storage_path: Optional[Path] = None,
) -> str:
    """Generate progressive hints for an active incident.

    Args:
        incident_id: Active incident ID
        current_hint_level: 1 (Socratic), 2 (direction), 3 (command)
        api_key: Gemini API key
        storage_path: Custom storage directory

    Returns:
        Hint text
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Hint unavailable (GEMINI_API_KEY not set)"

    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, description, symptoms, affected_system
        FROM incidents
        WHERE id = ?
        """,
        (incident_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Incident not found"

    title, description, symptoms, system = row

    client = genai.Client(api_key=api_key)

    hint_instructions = {
        1: "Ask a Socratic question to guide thinking (don't give the answer)",
        2: "Give a direction or area to investigate (component/log file)",
        3: "Provide a specific command or action to take",
    }

    prompt = f"""You are a Senior DevOps mentor helping debug an incident.

Incident: {title}
Description: {description}
Symptoms: {symptoms}
System: {system}

Provide a hint (level {current_hint_level}/3):
{hint_instructions.get(current_hint_level, hint_instructions[1])}

Keep it concise (1-2 sentences).
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", contents=prompt
    )
    return response.text.strip()


def generate_validation_questions(
    incident_id: int,
    resolution: str,
    api_key: Optional[str] = None,
    storage_path: Optional[Path] = None,
) -> list[str]:
    """Generate validation questions to test understanding.

    Args:
        incident_id: Resolved incident ID
        resolution: User's resolution description
        api_key: Gemini API key
        storage_path: Custom storage directory

    Returns:
        List of validation questions
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return []

    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, description, affected_system
        FROM incidents
        WHERE id = ?
        """,
        (incident_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return []

    title, description, system = row

    client = genai.Client(api_key=api_key)

    prompt = f"""You are evaluating a DevOps engineer's understanding after resolving an incident.

Incident: {title}
System: {system}
Description: {description}
User's resolution: {resolution}

Generate 2-3 validation questions to test their understanding of:
1. Root cause
2. Why their fix works
3. How to prevent it

Return as JSON array: ["question1", "question2", "question3"]
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", contents=prompt
    )
    text = response.text.strip()

    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    import json

    try:
        questions = json.loads(text)
        return questions if isinstance(questions, list) else []
    except json.JSONDecodeError:
        return []


def calculate_next_review_date(score: int) -> str:
    """Calculate next review date based on SRS algorithm.

    Args:
        score: Resolution score (0-5)

    Returns:
        ISO format date string
    """
    intervals = {
        0: 0,  # Immediate retry
        1: 1,  # 1 day
        2: 1,  # 1 day
        3: 3,  # 3 days
        4: 7,  # 1 week
        5: 14,  # 2 weeks
    }

    days = intervals.get(score, 3)
    next_date = datetime.now() + timedelta(days=days)
    return next_date.date().isoformat()


def get_due_incidents(storage_path: Optional[Path] = None) -> list[int]:
    """Get incidents due for review based on SRS.

    Args:
        storage_path: Custom storage directory

    Returns:
        List of incident IDs due for review
    """
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    today = datetime.now().date().isoformat()

    cursor.execute(
        """
        SELECT id
        FROM incidents
        WHERE next_review_date IS NOT NULL
        AND next_review_date <= ?
        AND status = 'resolved'
        ORDER BY next_review_date ASC
        """,
        (today,),
    )

    incident_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    return incident_ids
