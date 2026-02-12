from pathlib import Path

from src.lms.chaos_templates import load_templates, pick_chaos_template
from src.lms.database import init_db


def test_load_templates():
    templates = load_templates()
    assert templates
    assert all("name" in t for t in templates)


def test_pick_chaos_template_with_topics(tmp_path):
    storage_path = Path(tmp_path)
    init_db(storage_path=storage_path)

    template = pick_chaos_template(user_id="tester", storage_path=storage_path)

    assert template
    assert "bug_inject" in template
