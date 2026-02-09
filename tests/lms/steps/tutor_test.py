"""Tests for the Tutor step."""

from pathlib import Path
from unittest.mock import patch

from src.lms.steps import tutor as tutor_module


def test_sanitize_filename_basic():
    assert tutor_module._sanitize_filename("Docker Volumes") == "Docker_Volumes"
    assert tutor_module._sanitize_filename("  ") == "untitled"


def test_clean_json_response_strips_codeblock():
    raw = """```json
{"key": "value"}
```"""
    assert tutor_module._clean_json_response(raw) == '{"key": "value"}'


def test_tutor_step_creates_note(tmp_path: Path):
    fake_client = object()

    with (
        patch.object(tutor_module, "_get_gemini_client", return_value=fake_client),
        patch.object(tutor_module, "_get_vault_path", return_value=tmp_path),
        patch.object(tutor_module, "_ask_and_validate") as mock_validate,
        patch.object(tutor_module, "_enrich_content") as mock_enrich,
        patch("src.lms.steps.tutor.Prompt.ask") as mock_prompt,
    ):
        mock_prompt.side_effect = [
            "Docker Volumes",
            "A volume is persistent storage.",
            "Like a USB drive.",
        ]
        mock_validate.side_effect = [
            {
                "is_valid": True,
                "feedback": "OK",
                "refined_content": "Persistent storage.",
            },
            {
                "is_valid": True,
                "feedback": "OK",
                "refined_content": "Like a USB drive.",
            },
        ]
        mock_enrich.return_value = {
            "survival_commands": "docker volume ls",
            "senior_insight": "Storage drivers matter.",
            "flashcards": "Q: What is a volume? :: A: Persistent storage. #flashcard",
        }

        tutor_module.tutor_step()

    note_path = tmp_path / "Docker_Volumes.md"
    assert note_path.exists()
    content = note_path.read_text(encoding="utf-8")
    assert "# Docker Volumes" in content
    assert "## 🧠 Concept" in content
    assert "## 💡 Analogy" in content
    assert "## 🛠️ Survival Commands" in content
    assert "## ⚡ Flashcards" in content
