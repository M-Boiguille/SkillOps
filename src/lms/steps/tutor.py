"""Tutor step - Smart Note Taker with Socratic dialogue."""

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Any, Dict
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from pydantic import BaseModel, ValidationError
from src.lms.persistence import get_context, set_context, save_cards_created
from src.lms.ai_config import get_gemini_model

# Configuration
console = Console()


def _get_gemini_client() -> Any:
    """Initialise le client Gemini avec la clé API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY environment variable not set.")
    import importlib

    genai_module = importlib.import_module("google.genai")
    return genai_module.Client(api_key=api_key)


def _get_vault_path() -> Path:
    """Récupère le chemin du Vault Obsidian depuis l'env ou par défaut."""
    path_str = os.getenv("OBSIDIAN_VAULT_PATH", "./.skillopsvault")
    return Path(path_str).expanduser().resolve()


def _sanitize_filename(topic: str) -> str:
    """Nettoie le nom du fichier pour le système de fichiers."""
    safe = "".join(ch for ch in topic if ch.isalnum() or ch in " -_").strip()
    return safe.replace(" ", "_") or "untitled"


def _clean_json_response(text: str) -> str:
    """Nettoie les balises markdown json si présentes."""
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return text


class ValidationPayload(BaseModel):
    is_valid: bool
    feedback: str
    refined_content: str


class EnrichPayload(BaseModel):
    survival_commands: str
    senior_insight: str
    flashcards: str


def _generate_with_retry(
    client: Any,
    prompt: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    timeout_seconds: float = 20.0,
):
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    client.models.generate_content,
                    model=get_gemini_model(),
                    contents=prompt,
                )
                return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError as exc:
            last_exc = exc
            if attempt >= max_retries:
                raise TimeoutError("AI request timed out") from exc
            time.sleep(base_delay * (2 ** (attempt - 1)))
        except Exception as exc:
            last_exc = exc
            if attempt >= max_retries:
                raise
            time.sleep(base_delay * (2 ** (attempt - 1)))
    if last_exc:
        raise last_exc
    raise RuntimeError("Failed to generate content after retries")


def _ask_and_validate(
    client: Any, topic: str, stage: str, user_answer: str
) -> Dict[str, Any]:
    """Valide la réponse de l'utilisateur via Gemini (Méthode Socratique)."""

    system_prompt = f"""
    Tu es un expert DevOps qui joue le rôle d'un auditeur naïf mais curieux (Technique Feynman).
    L'utilisateur essaie de t'expliquer le concept : "{topic}".
    Étape actuelle : {stage}.

    Règles de validation :
     1. Si l'explication utilise trop de jargon technique sans le définir : "is_valid": false.
        Feedback : "Je ne comprends pas ce mot compliqué, peux-tu expliquer plus simplement ?"
     2. Si l'explication est fausse ou imprécise : "is_valid": false.
        Feedback : Corrige l'erreur conceptuelle poliment.
     3. Si l'explication est claire, simple et juste (vulgarisée) : "is_valid": true.
        Feedback : Confirme la compréhension et propose une nuance experte.

    Réponds UNIQUEMENT avec ce JSON strict :
    {{
        "is_valid": boolean,
        "feedback": "string (explication courte pour l'étudiant)",
        "refined_content": "string (la version parfaite de la réponse pour la note finale)"
    }}
    """

    user_prompt = f"Réponse de l'étudiant : {user_answer}"

    try:
        response = _generate_with_retry(client, f"{system_prompt}\n{user_prompt}")
        cleaned_json = _clean_json_response(response.text)
        data = json.loads(cleaned_json)
        payload = ValidationPayload.model_validate(data)
        return payload.model_dump()
    except (ValueError, json.JSONDecodeError, RuntimeError, ValidationError) as e:
        console.print(f"[red]Erreur de validation IA : {e}[/red]")
        # Fallback pour ne pas bloquer l'utilisateur
        return {
            "is_valid": True,
            "feedback": "Validation impossible (Erreur API), on continue.",
            "refined_content": user_answer,
        }


def _enrich_content(client: Any, topic: str) -> Dict[str, str]:
    """Génère le contenu additionnel (Commandes, Senior Level, Flashcards)."""

    prompt = f"""
    Tu es un architecte système expert. Pour le sujet "{topic}",
    génère le contenu suivant au format JSON strict.

     1. "survival_commands": 2 ou 3 commandes CLI essentielles (Bash) pour ce sujet.
         Pas d'explications, juste le code.
     2. "senior_insight": Un paragraphe technique avancé (Niveau Senior/Architecte)
         sur ce sujet (ex: pièges en prod, optimisation, sécurité).
     3. "flashcards": 2 cartes Anki au format texte brut:
         "Q: Question ? :: A: Réponse #flashcard".

    Format de sortie JSON attendu :
    {{
        "survival_commands": "string",
        "senior_insight": "string",
        "flashcards": "string"
    }}
    """

    try:
        response = _generate_with_retry(client, prompt)
        cleaned_json = _clean_json_response(response.text)
        data = json.loads(cleaned_json)
        payload = EnrichPayload.model_validate(data)
        return payload.model_dump()
    except (ValueError, json.JSONDecodeError, RuntimeError, ValidationError):
        return {
            "survival_commands": "# Erreur de génération",
            "senior_insight": "Impossible de générer le contenu avancé.",
            "flashcards": "",
        }


def tutor_step() -> bool:
    """Fonction principale du module Tutor."""
    console.clear()
    console.print(
        Panel.fit("🧠 Feynman Mode - Enseigner pour Apprendre", style="bold cyan")
    )

    # 0. Initialisation
    try:
        client = _get_gemini_client()
        vault_path = _get_vault_path()
    except ValueError as e:
        console.print(f"[bold red]{e}[/bold red]")
        return False

    # Check context for existing topic
    topic = get_context("current_topic")
    if topic:
        console.print(
            f"Sujet détecté depuis le contexte : [bold green]{topic}[/bold green]"
        )
        if (
            not Prompt.ask("Continuer sur ce sujet ?", choices=["y", "n"], default="y")
            == "y"
        ):
            topic = None

    if not topic:
        topic = Prompt.ask(
            "[bold yellow]De quel sujet veux-tu parler aujourd'hui ?[/bold yellow] "
            "(ex: Docker Volumes)"
        )

    if not topic:
        return False

    # 1. Phase Définition
    while True:
        console.print("\n[bold cyan]1. Définition[/bold cyan]")
        console.print(
            f"Explique-moi [italic]{topic}[/italic] comme si j'avais 12 ans (sans jargon)."
        )
        answer = Prompt.ask("❯ ")

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            progress.add_task(description="L'IA analyse ta réponse...", total=None)
            result = _ask_and_validate(client, topic, "Definition", answer)

        console.print(Markdown(f"**Mentor:** {result['feedback']}"))

        if result["is_valid"]:
            definition = result["refined_content"]
            set_context("current_topic", topic)  # Save context on success
            console.print("[green]✅ Définition validée ![/green]")
            break
        else:
            console.print("[red]❌ Essaie encore en étant plus précis.[/red]")

    # 2. Phase Analogie
    while True:
        console.print("\n[bold magenta]2. Analogie[/bold magenta]")
        console.print(
            "Donne-moi une analogie concrète pour expliquer cela à un débutant."
        )
        answer = Prompt.ask("❯ ")

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            progress.add_task(description="L'IA vérifie ton analogie...", total=None)
            result = _ask_and_validate(client, topic, "Analogy", answer)

        console.print(Markdown(f"**Mentor:** {result['feedback']}"))

        if result["is_valid"]:
            analogy = result["refined_content"]
            console.print("[green]✅ Analogie validée ![/green]")
            break
        else:
            console.print(
                "[red]❌ L'analogie ne fonctionne pas tout à fait. Essaie autre chose.[/red]"
            )

    # 3. Enrichissement automatique
    console.print("\n[bold blue]3. Génération du contenu expert...[/bold blue]")
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task(
            description="Création des snippets et flashcards...", total=None
        )
        enrichment = _enrich_content(client, topic)

    # 4. Création du fichier Markdown
    filename = f"{_sanitize_filename(topic)}.md"
    file_path = vault_path / filename

    # Création du dossier si inexistant
    vault_path.mkdir(parents=True, exist_ok=True)

    markdown_content = f"""---
type: concept
status: active
tags: [devops, generated, skillops]
created_at: {os.popen('date -I').read().strip()}
---

# {topic}

## 🧠 Concept
{definition}

## 💡 Analogy
{analogy}

## 🛠️ Survival Commands
```bash
{enrichment['survival_commands']}

```

## 📚 Levels

> [!NOTE] Junior Level
> Compréhension de base : {definition}

> [!WARNING] Senior Level
> {enrichment['senior_insight']}

## ⚡ Flashcards

{enrichment['flashcards']}
"""

    file_path.write_text(markdown_content, encoding="utf-8")

    # Enregistrer les cartes créées (2 par défaut selon le prompt)
    save_cards_created(2, source="tutor")

    console.print(
        Panel(
            f"[bold green]Note créée avec succès ![/bold green]\n"
            f"📂 Chemin : {file_path}\n"
            f"🃏 Flashcards prêtes pour Anki.",
            border_style="green",
        )
    )
    return True
