"""Migration script to move from JSON/YAML files to SQLite."""

import json
import sqlite3

from src.lms.database import get_db_path, init_db
from src.lms.paths import get_storage_path


def migrate():
    print("🚀 Starting migration to SQLite...")

    # 1. Initialize DB
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    storage_path = get_storage_path()

    # 2. Migrate .progress.json (Historical daily progress)
    progress_file = storage_path / ".progress.json"
    if progress_file.exists():
        print(f"📦 Migrating {progress_file}...")
        try:
            with open(progress_file, "r") as f:
                history = json.load(f)

            for entry in history:
                date_str = entry.get("date")
                if not date_str:
                    continue

                # Create Session
                cursor.execute(
                    "INSERT OR IGNORE INTO sessions (date) VALUES (?)", (date_str,)
                )
                cursor.execute("SELECT id FROM sessions WHERE date = ?", (date_str,))
                session_id = cursor.fetchone()[0]

                # Migrate Steps
                steps = entry.get("steps", {})
                for step_key, step_data in steps.items():
                    # step_key format "step1", "step2" -> extract number
                    try:
                        step_num = int(step_key.replace("step", ""))
                        if step_data.get("completed"):
                            cursor.execute(
                                "INSERT OR IGNORE INTO step_completions "
                                "(session_id, step_number) VALUES (?, ?)",
                                (session_id, step_num),
                            )
                    except ValueError:
                        pass

                # Migrate Cards
                cards = entry.get("cards_created", 0)
                if cards > 0:
                    cursor.execute(
                        "INSERT INTO card_creations (session_id, count, source) VALUES (?, ?, ?)",
                        (session_id, cards, "migration"),
                    )

        except Exception as e:
            print(f"❌ Error migrating progress: {e}")

    # 3. Migrate formation_log.json
    formation_file = storage_path / "formation_log.json"
    if formation_file.exists():
        print(f"📦 Migrating {formation_file}...")
        try:
            with open(formation_file, "r") as f:
                logs = json.load(f)

            for log in logs:
                # Parse date from ISO format (2026-01-09T10:00:00) to YYYY-MM-DD
                iso_date = log.get("date")
                if not iso_date:
                    continue

                date_str = iso_date.split("T")[0]

                # Get/Create Session
                cursor.execute(
                    "INSERT OR IGNORE INTO sessions (date) VALUES (?)", (date_str,)
                )
                cursor.execute("SELECT id FROM sessions WHERE date = ?", (date_str,))
                session_id = cursor.fetchone()[0]

                duration_minutes = log.get("duration_minutes", 0)
                cursor.execute(
                    "INSERT INTO formation_logs (session_id, goals, recall, "
                    "duration_minutes, wakatime_minutes) VALUES (?, ?, ?, ?, ?)",
                    (
                        session_id,
                        json.dumps(log.get("goals", [])),
                        log.get("recall", ""),
                        duration_minutes,
                        duration_minutes,
                    ),
                )
        except Exception as e:
            print(f"❌ Error migrating formation logs: {e}")

    # 4. Migrate reinforce_progress.json
    reinforce_file = storage_path / "reinforce_progress.json"
    if reinforce_file.exists():
        print(f"📦 Migrating {reinforce_file}...")
        try:
            with open(reinforce_file, "r") as f:
                data = json.load(f)

            for date_str, day_data in data.items():
                exercises = day_data.get("exercises", [])
                for ex in exercises:
                    cursor.execute(
                        """
                        INSERT INTO reinforce_progress
                        (exercise_id, title, duration_seconds, completed, quality,
                         timestamp, srs_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            ex.get("id"),
                            ex.get("title"),
                            ex.get("duration_seconds"),
                            ex.get("completed"),
                            4,
                            ex.get("timestamp"),
                            json.dumps(ex.get("srs_data", {})),
                        ),
                    )
        except Exception as e:
            print(f"❌ Error migrating reinforce progress: {e}")

    conn.commit()
    conn.close()
    print("✅ Migration completed successfully!")


if __name__ == "__main__":
    migrate()
