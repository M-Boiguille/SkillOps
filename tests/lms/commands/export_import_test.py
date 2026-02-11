"""Tests for data export and import functionality."""

import json
import csv
from datetime import datetime
from pathlib import Path

import pytest

from src.lms.commands.export import DataExporter
from src.lms.commands.data_import import DataImporter
from src.lms.database import get_connection, init_db
from src.lms.persistence import get_progress_history


# Sample progress data matching export format
SAMPLE_PROGRESS = [
    {"date": "2024-01-01", "steps": 5, "time": 30, "cards": 5},
    {"date": "2024-01-02", "steps": 7, "time": 45, "cards": 8},
    {"date": "2024-01-03", "steps": 8, "time": 60, "cards": 10},
]


def seed_progress(storage_path: Path, entries: list[dict]) -> None:
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    for entry in entries:
        date_str = entry["date"]
        steps = int(entry.get("steps", 0))
        time_minutes = int(entry.get("time", 0))
        cards = int(entry.get("cards", 0))

        cursor.execute("INSERT OR IGNORE INTO sessions (date) VALUES (?)", (date_str,))
        cursor.execute("SELECT id FROM sessions WHERE date = ?", (date_str,))
        session_id = cursor.fetchone()[0]

        for step_num in range(1, min(max(steps, 0), 9) + 1):
            cursor.execute(
                "INSERT OR IGNORE INTO step_completions (session_id, step_number) VALUES (?, ?)",
                (session_id, step_num),
            )

        if time_minutes > 0:
            cursor.execute(
                "INSERT INTO formation_logs (session_id, goals, recall, "
                "duration_minutes) VALUES (?, ?, ?, ?)",
                (session_id, "[]", "", time_minutes),
            )

        if cards > 0:
            cursor.execute(
                "INSERT INTO card_creations (session_id, count, source) VALUES (?, ?, ?)",
                (session_id, cards, "test"),
            )

    conn.commit()
    conn.close()


@pytest.fixture
def exporter(tmp_path):
    """Create DataExporter instance with temp storage."""
    return DataExporter(storage_path=tmp_path)


@pytest.fixture
def importer(tmp_path):
    """Create DataImporter instance with temp storage."""
    return DataImporter(storage_path=tmp_path)


# Export JSON Tests
class TestExportJSON:
    """Test JSON export functionality."""

    def test_export_to_json_creates_file(self, exporter, tmp_path):
        """Test that export_to_json creates a file."""
        output_path = tmp_path / "export.json"

        seed_progress(tmp_path, SAMPLE_PROGRESS)
        result = exporter.export_to_json(output_path=output_path)

        assert result == output_path
        assert output_path.exists()

    def test_export_to_json_valid_json(self, exporter, tmp_path):
        """Test that exported file is valid JSON."""
        output_path = tmp_path / "export.json"

        seed_progress(tmp_path, SAMPLE_PROGRESS)
        exporter.export_to_json(output_path=output_path)

        # Should not raise
        data = json.loads(output_path.read_text())
        assert isinstance(data, dict)

    def test_export_to_json_contains_progress(self, exporter, tmp_path):
        """Test that exported JSON contains progress data."""
        output_path = tmp_path / "export.json"

        seed_progress(tmp_path, SAMPLE_PROGRESS)
        exporter.export_to_json(output_path=output_path)

        exported = json.loads(output_path.read_text())
        assert "data" in exported
        assert "progress" in exported["data"]
        assert exported["data"]["progress"] == get_progress_history(tmp_path)

    def test_export_to_json_metadata(self, exporter, tmp_path):
        """Test that JSON has proper metadata."""
        output_path = tmp_path / "export.json"

        seed_progress(tmp_path, SAMPLE_PROGRESS)
        exporter.export_to_json(output_path=output_path)

        exported = json.loads(output_path.read_text())
        assert "exported_at" in exported
        assert "export_format" in exported
        assert exported["export_format"] == "json"
        assert "version" in exported

    def test_export_to_json_default_path(self, exporter):
        """Test export with default path."""
        seed_progress(exporter.storage_path, SAMPLE_PROGRESS)
        result = exporter.export_to_json()

        # Should create in current directory
        assert result.name == "skillops_export.json"
        # Clean up
        if result.exists():
            result.unlink()


# Export CSV Tests
class TestExportCSV:
    """Test CSV export functionality."""

    def test_export_to_csv_creates_file(self, exporter, tmp_path):
        """Test that export_to_csv creates CSV file."""
        seed_progress(tmp_path, SAMPLE_PROGRESS)
        result = exporter.export_to_csv(output_dir=tmp_path)

        assert len(result) == 1
        assert result[0].exists()
        assert result[0].suffix == ".csv"

    def test_export_to_csv_valid_format(self, exporter, tmp_path):
        """Test that CSV is valid format."""
        seed_progress(tmp_path, SAMPLE_PROGRESS)
        result = exporter.export_to_csv(output_dir=tmp_path)

        csv_file = result[0]
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Should have headers and rows
        assert len(rows) > 0

    def test_export_to_csv_contains_progress(self, exporter, tmp_path):
        """Test CSV contains progress entries."""
        seed_progress(tmp_path, SAMPLE_PROGRESS)
        result = exporter.export_to_csv(output_dir=tmp_path)

        csv_file = result[0]
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert rows[0]["date"] == "2024-01-01"
        assert rows[0]["steps"] == "5"


# Import JSON Tests
class TestImportJSON:
    """Test JSON import functionality."""

    def test_import_from_json_file_exists(self, importer, tmp_path):
        """Test that imported file is validated."""
        export_file = tmp_path / "import.json"
        export_file.write_text(
            json.dumps({"exported_at": datetime.now().isoformat(), "data": {}})
        )

        result = importer.import_from_json(export_file, merge=False, backup=False)

        assert result is True

    def test_import_from_json_file_not_found(self, importer):
        """Test import with non-existent file."""
        result = importer.import_from_json(
            Path("/nonexistent.json"), merge=False, backup=False
        )
        assert result is False

    def test_import_from_json_merge_mode(self, importer, tmp_path):
        """Test JSON import with merge."""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "export_format": "json",
            "version": "1.0",
            "data": {"progress": SAMPLE_PROGRESS},
        }
        export_file = tmp_path / "import.json"
        export_file.write_text(json.dumps(export_data))

        existing_progress = [
            {"date": "2023-12-31", "steps": 4, "time": 15, "cards": 2},
        ]

        seed_progress(tmp_path, existing_progress)
        result = importer.import_from_json(export_file, merge=True, backup=False)

        assert result is True
        history = get_progress_history(tmp_path)
        assert history[0]["date"] == "2023-12-31"
        assert history[-1]["date"] == "2024-01-03"

    def test_import_from_json_replace_mode(self, importer, tmp_path):
        """Test JSON import in replace mode."""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "export_format": "json",
            "version": "1.0",
            "data": {"progress": SAMPLE_PROGRESS},
        }
        export_file = tmp_path / "import.json"
        export_file.write_text(json.dumps(export_data))

        seed_progress(
            tmp_path, [{"date": "2023-12-31", "steps": 4, "time": 15, "cards": 2}]
        )
        result = importer.import_from_json(export_file, merge=False, backup=False)

        assert result is True
        history = get_progress_history(tmp_path)
        assert len(history) == len(SAMPLE_PROGRESS)
        assert history[0]["date"] == "2024-01-01"


# Import CSV Tests
class TestImportCSV:
    """Test CSV import functionality."""

    def test_import_from_csv_file_not_found(self, importer):
        """Test CSV import with non-existent file."""
        result = importer.import_from_csv(
            Path("/nonexistent.csv"), merge=False, backup=False
        )
        assert result is False

    def test_import_from_csv_valid(self, importer, tmp_path):
        """Test valid CSV import."""
        csv_file = tmp_path / "progress.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "steps", "time", "cards"])
            writer.writeheader()
            writer.writerows(SAMPLE_PROGRESS)

        result = importer.import_from_csv(csv_file, merge=False, backup=False)

        assert result is True
        history = get_progress_history(tmp_path)
        assert len(history) == len(SAMPLE_PROGRESS)

    def test_import_from_csv_merge_mode(self, importer, tmp_path):
        """Test CSV import with merge."""
        csv_file = tmp_path / "progress.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "steps", "time", "cards"])
            writer.writeheader()
            writer.writerows(SAMPLE_PROGRESS)

        existing_progress = [
            {"date": "2023-12-31", "steps": 4, "time": 15, "cards": 2},
        ]

        seed_progress(tmp_path, existing_progress)
        result = importer.import_from_csv(csv_file, merge=True, backup=False)

        assert result is True
        history = get_progress_history(tmp_path)
        assert history[0]["date"] == "2023-12-31"


# Round-trip Tests
class TestRoundTrip:
    """Test export and import together."""

    def test_json_roundtrip(self, exporter, importer, tmp_path):
        """Test export to JSON and import back."""
        export_file = tmp_path / "roundtrip.json"

        seed_progress(tmp_path, SAMPLE_PROGRESS)
        exporter.export_to_json(output_path=export_file)
        result = importer.import_from_json(export_file, merge=False, backup=False)

        assert result is True
        assert export_file.exists()

    def test_csv_roundtrip(self, exporter, importer, tmp_path):
        """Test export to CSV and import back."""
        seed_progress(tmp_path, SAMPLE_PROGRESS)
        csv_files = exporter.export_to_csv(output_dir=tmp_path)

        assert len(csv_files) > 0

        result = importer.import_from_csv(csv_files[0], merge=False, backup=False)

        assert result is True


# Validation Tests
class TestValidation:
    """Test validation functions."""

    def test_validate_json_file(self, importer, tmp_path):
        """Test JSON file validation."""
        valid_file = tmp_path / "valid.json"
        valid_file.write_text(
            json.dumps({"exported_at": "2024-01-01T00:00:00", "data": {"progress": []}})
        )

        assert importer.validate_import(valid_file) is True

    def test_validate_json_file_invalid(self, importer, tmp_path):
        """Test invalid JSON validation."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not json")

        assert importer.validate_import(invalid_file) is False

    def test_validate_csv_file(self, importer, tmp_path):
        """Test CSV file validation."""
        csv_file = tmp_path / "data.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "steps", "time", "cards"])
            writer.writeheader()

        assert importer.validate_import(csv_file) is True

    def test_validate_nonexistent_file(self, importer):
        """Test validation of non-existent file."""
        assert importer.validate_import(Path("/nonexistent.json")) is False


# Backup Tests
class TestBackup:
    """Test backup creation."""

    def test_create_backup(self, importer):
        """Test that backup is created."""
        seed_progress(importer.storage_path, SAMPLE_PROGRESS)
        backup_path = importer._create_backup()

        assert backup_path.exists()
        assert "backup" in backup_path.name

        backup_data = json.loads(backup_path.read_text())
        assert "data" in backup_data
        assert "progress" in backup_data["data"]
