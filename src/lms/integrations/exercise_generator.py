"""Exercise generation using Gemini AI with local caching."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from google import genai


class ExerciseGenerator:
    """Generate DevOps exercises using Gemini AI."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini AI client.

        Args:
            api_key: Google API key. Defaults to GEMINI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=self.api_key)
        # Using gemini-2.5-flash: best balance of speed, quality, and cost
        # - 1M token context for understanding complex DevOps topics
        # - Hybrid reasoning for structured educational content
        # - 100% free (input + output)
        # - Responses cached locally in JSON to avoid regeneration

    def generate_exercise(
        self,
        topic: str,
        difficulty: str = "Débutant",
        duration: str = "15min",
        completion_count: int = 0,
    ) -> Dict[str, str]:
        """Generate a complete DevOps exercise with instructions.

        Args:
            topic: Exercise topic (e.g., "Docker Basics", "Kubernetes Pods")
            difficulty: Difficulty level (Débutant, Intermédiaire, Avancé)
            duration: Expected duration (e.g., "15min", "30min")
            completion_count: Number of times this exercise was completed (for progressive difficulty)

        Returns:
            Dict with exercise content (instructions, objectives, validation, hints, solution)
        """
        prompt = self._build_exercise_prompt(
            topic, difficulty, duration, completion_count
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            if not response or not response.text:
                raise ValueError("Failed to generate exercise from Gemini")

            # Parse the response into structured format
            exercise_content = self._parse_exercise_response(response.text)
            return exercise_content

        except Exception as e:
            raise ValueError(f"Exercise generation failed: {e}")

    def _build_exercise_prompt(
        self, topic: str, difficulty: str, duration: str, completion_count: int = 0
    ) -> str:
        """Build the complete prompt for exercise generation.

        Full context is reprocessed each time, but response is cached locally
        in JSON. Before reaching 1M tokens, we'll have time to optimize.
        """
        # Progressive difficulty mapping
        difficulty_levels = {
            "Débutant": ["Débutant", "Débutant+", "Intermédiaire"],
            "Intermédiaire": ["Intermédiaire", "Intermédiaire+", "Avancé"],
            "Avancé": ["Avancé", "Avancé+", "Expert"],
        }

        # Augmenter la difficulté tous les 2 succès
        level_index = min(completion_count // 2, 2)
        adjusted_difficulty = difficulty_levels.get(difficulty, [difficulty])[
            level_index
        ]

        # Contextes variés pour éviter le par cœur
        contexts = [
            "en production avec haute disponibilité",
            "dans un environnement de staging avec contraintes de sécurité",
            "pour une startup avec budget limité",
            "dans une infrastructure multi-cloud (AWS + Azure)",
            "avec monitoring et alerting intégrés",
            "en respectant les bonnes pratiques DevSecOps",
            "avec intégration CI/CD complète",
            "dans un cluster Kubernetes existant",
        ]
        context_variation = (
            contexts[completion_count % len(contexts)]
            if completion_count > 0
            else "en conditions réelles"
        )

        return f"""Tu es un expert DevOps qui crée des exercices pratiques type "défi" pour l'apprentissage.

Génère un exercice pratique de DevOps avec les caractéristiques suivantes:
- Sujet: {topic}
- Difficulté: {adjusted_difficulty} (exercice #{completion_count + 1} pour cet apprenant)
- Durée estimée: {duration}
- Contexte: {context_variation}

IMPORTANT: C'est la {completion_count + 1}ème fois que l'apprenant fait cet exercice.
{"" if completion_count == 0 else f"Ajoute de nouvelles contraintes/challenges différents des versions précédentes. Variation #{completion_count + 1}."}

L'exercice doit être structuré en JSON avec les champs suivants:
{{
    "title": "Titre complet de l'exercice",
    "objectives": "Liste des objectifs d'apprentissage (3-4 points)",
    "prerequisites": "Prérequis nécessaires (outils, connaissances)",
    "scenario": "Contexte réaliste ou mission à accomplir (2-3 phrases) - Varie le scénario si completion_count > 0",
    "requirements": "Liste des résultats attendus SANS donner les commandes (ex: 'Déployer un conteneur qui répond sur le port 8080' au lieu de 'docker run -p 8080:80 nginx')",
    "success_criteria": "Critères mesurables pour auto-évaluation (chaque critère doit être vérifiable par l'apprenant: ex: 'Le service répond avec un HTTP 200 sur localhost:8080')",
    "hints": "2-3 indices CONCEPTUELS si bloqué (ex: 'Pense à la directive EXPOSE dans le Dockerfile' plutôt que donner la commande exacte)",
    "solution": "Solution complète avec explications pédagogiques",
    "resources": "Liens vers documentation officielle (2-3 liens)"
}}

RÈGLES CRITIQUES pour les requirements:
- NE JAMAIS donner les commandes exactes dans les requirements
- Décrire le RÉSULTAT attendu, pas les ÉTAPES
- Formuler comme un cahier des charges ou une mission
- L'apprenant doit chercher COMMENT faire

PROGRESSION AUTOMATIQUE:
- Niveau {completion_count + 1}: {"Premier essai - version de base" if completion_count == 0 else f"Ajoute des contraintes supplémentaires (ex: volumes persistants, réseaux customs, healthchecks, etc.)"}

Exemple CORRECT:
"requirements": "Créer une application web conteneurisée accessible sur le port 3000 qui affiche 'Hello DevOps'"

Exemple INCORRECT:
"requirements": "1. Exécuter: docker run -p 3000:3000 myapp\\n2. Vérifier avec curl localhost:3000"

Réponds UNIQUEMENT avec le JSON, sans markdown ni texte additionnel."""

    def _parse_exercise_response(self, response_text: str) -> Dict[str, str]:
        """Parse Gemini's response into structured exercise data.

        Args:
            response_text: Raw text response from Gemini

        Returns:
            Structured exercise dictionary
        """
        # Remove markdown code blocks if present
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        try:
            exercise = json.loads(cleaned)
            # Validate required fields
            required_fields = [
                "title",
                "objectives",
                "requirements",
                "success_criteria",
            ]
            for field in required_fields:
                if field not in exercise:
                    raise ValueError(f"Missing required field: {field}")

            return exercise
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse exercise JSON: {e}")

    def get_hints(self, exercise_content: Dict[str, str]) -> str:
        """Extract hints from exercise content.

        Args:
            exercise_content: Exercise dictionary from generate_exercise()

        Returns:
            Formatted hints string
        """
        return exercise_content.get("hints", "Aucun indice disponible.")

    def get_solution(self, exercise_content: Dict[str, str]) -> str:
        """Extract solution from exercise content.

        Args:
            exercise_content: Exercise dictionary from generate_exercise()

        Returns:
            Formatted solution string
        """
        return exercise_content.get("solution", "Solution non disponible.")

    def cache_exercise(
        self, exercise_id: str, content: Dict[str, str], cache_dir: Path
    ) -> None:
        """Cache generated exercise to avoid regenerating.

        Args:
            exercise_id: Unique exercise identifier
            content: Exercise content dictionary
            cache_dir: Directory to store cached exercises
        """
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{exercise_id}.json"

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def load_cached_exercise(
        self, exercise_id: str, cache_dir: Path
    ) -> Optional[Dict[str, str]]:
        """Load cached exercise if available.

        Args:
            exercise_id: Unique exercise identifier
            cache_dir: Directory where exercises are cached

        Returns:
            Cached exercise content or None if not found
        """
        cache_file = cache_dir / f"{exercise_id}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None

        return None
