"""Post-mortem documentation module for SkillOps.

Enforces structured incident documentation following SRE best practices.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from src.lms.database import get_connection, init_db

console = Console()


@dataclass
class PostMortem:
    """Represents a post-mortem document."""

    id: Optional[int]
    incident_id: int
    timestamp: str
    what_happened: str
    when_detected: str
    impact: str
    root_cause: str
    resolution: str
    prevention: str
    action_items: str  # JSON list


def create_postmortem_interactive(
    incident_id: int, storage_path: Optional[Path] = None
) -> PostMortem:
    """Create a post-mortem through interactive prompts.

    Args:
        incident_id: Associated incident ID
        storage_path: Custom storage directory

    Returns:
        Created PostMortem object
    """
    console.print("\n[bold cyan]📝 Post-Mortem Template (SRE Standard)[/bold cyan]\n")
    console.print(
        "[dim]Answer each question. This will be saved for future reference.[/dim]\n"
    )

    what_happened = Prompt.ask("1️⃣  [bold]What happened?[/bold] (brief summary)")
    when_detected = Prompt.ask(
        "2️⃣  [bold]When was it detected?[/bold] (timestamp or duration)"
    )
    impact = Prompt.ask(
        "3️⃣  [bold]What was the impact?[/bold] (users affected, downtime, etc.)"
    )
    root_cause = Prompt.ask(
        "4️⃣  [bold]What was the root cause?[/bold] (technical explanation)"
    )
    resolution = Prompt.ask("5️⃣  [bold]How was it resolved?[/bold] (steps taken)")
    prevention = Prompt.ask(
        "6️⃣  [bold]How can we prevent this?[/bold] (long-term fixes)"
    )

    console.print("\n[bold]7️⃣  Action Items[/bold]")
    console.print("[dim]Enter action items (one per line, empty line to finish)[/dim]")
    action_items = []
    while True:
        item = Prompt.ask("  •", default="")
        if not item:
            break
        action_items.append(item)

    import json

    postmortem = PostMortem(
        id=None,
        incident_id=incident_id,
        timestamp=datetime.now().isoformat(),
        what_happened=what_happened,
        when_detected=when_detected,
        impact=impact,
        root_cause=root_cause,
        resolution=resolution,
        prevention=prevention,
        action_items=json.dumps(action_items),
    )

    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO postmortems
        (incident_id, timestamp, what_happened, when_detected, impact,
         root_cause, resolution, prevention, action_items)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            postmortem.incident_id,
            postmortem.timestamp,
            postmortem.what_happened,
            postmortem.when_detected,
            postmortem.impact,
            postmortem.root_cause,
            postmortem.resolution,
            postmortem.prevention,
            postmortem.action_items,
        ),
    )
    postmortem.id = cursor.lastrowid

    # Link postmortem to incident
    cursor.execute(
        "UPDATE incidents SET postmortem_id = ? WHERE id = ?",
        (postmortem.id, incident_id),
    )

    conn.commit()
    conn.close()

    return postmortem


def get_postmortem(
    postmortem_id: int, storage_path: Optional[Path] = None
) -> Optional[PostMortem]:
    """Get a post-mortem by ID.

    Args:
        postmortem_id: PostMortem ID
        storage_path: Custom storage directory

    Returns:
        PostMortem object or None if not found
    """
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, incident_id, timestamp, what_happened, when_detected,
               impact, root_cause, resolution, prevention, action_items
        FROM postmortems
        WHERE id = ?
        """,
        (postmortem_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return PostMortem(
        id=row[0],
        incident_id=row[1],
        timestamp=row[2],
        what_happened=row[3],
        when_detected=row[4],
        impact=row[5],
        root_cause=row[6],
        resolution=row[7],
        prevention=row[8],
        action_items=row[9],
    )


def list_postmortems(storage_path: Optional[Path] = None) -> list[PostMortem]:
    """List all post-mortems.

    Args:
        storage_path: Custom storage directory

    Returns:
        List of PostMortem objects
    """
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, incident_id, timestamp, what_happened, when_detected,
               impact, root_cause, resolution, prevention, action_items
        FROM postmortems
        ORDER BY timestamp DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    postmortems = []
    for row in rows:
        postmortems.append(
            PostMortem(
                id=row[0],
                incident_id=row[1],
                timestamp=row[2],
                what_happened=row[3],
                when_detected=row[4],
                impact=row[5],
                root_cause=row[6],
                resolution=row[7],
                prevention=row[8],
                action_items=row[9],
            )
        )
    return postmortems


def export_postmortem_markdown(postmortem: PostMortem, output_path: Path) -> None:
    """Export post-mortem as Markdown.

    Args:
        postmortem: PostMortem object
        output_path: Output file path
    """
    import json

    action_items = json.loads(postmortem.action_items)
    action_items_md = "\n".join([f"- [ ] {item}" for item in action_items])

    content = f"""# Post-Mortem: Incident #{postmortem.incident_id}

**Date:** {postmortem.timestamp}

---

## 📋 Summary

### What Happened?
{postmortem.what_happened}

### When Was It Detected?
{postmortem.when_detected}

### Impact
{postmortem.impact}

---

## 🔍 Root Cause Analysis

{postmortem.root_cause}

---

## ✅ Resolution

{postmortem.resolution}

---

## 🛡️ Prevention

{postmortem.prevention}

---

## 📝 Action Items

{action_items_md}

---

**Post-Mortem ID:** {postmortem.id}
**Generated by:** SkillOps
"""

    output_path.write_text(content, encoding="utf-8")
    console.print(f"[green]✅ Post-mortem exported to {output_path}[/green]")


def postmortem_step(storage_path: Optional[Path] = None) -> bool:
    """Run the post-mortem step (interactive documentation).

    Args:
        storage_path: Custom storage directory

    Returns:
        True if step completed successfully
    """
    console.print("\n[bold cyan]📝 Post-Mortem Documentation[/bold cyan]\n")

    action = Prompt.ask(
        "What would you like to do?",
        choices=["create", "list", "view", "export", "quit"],
        default="create",
    )

    if action == "create":
        incident_id = Prompt.ask("Enter incident ID for this post-mortem")
        try:
            incident_id = int(incident_id)
            postmortem = create_postmortem_interactive(incident_id, storage_path)
            console.print(
                f"\n[green]✅ Post-mortem #{postmortem.id} created successfully[/green]"
            )

            if Confirm.ask("Export as Markdown?", default=False):
                output_path = Path(f"postmortem_{postmortem.id}.md")
                export_postmortem_markdown(postmortem, output_path)

            return True
        except ValueError:
            console.print("[red]Invalid incident ID[/red]")
            return False

    elif action == "list":
        postmortems = list_postmortems(storage_path)
        if not postmortems:
            console.print("[yellow]No post-mortems found[/yellow]")
            return True

        console.print(f"\n[bold]Found {len(postmortems)} post-mortem(s):[/bold]\n")
        for pm in postmortems:
            console.print(
                f"  • PM #{pm.id} (Incident #{pm.incident_id}) - {pm.timestamp}"
            )
            console.print(f"    {pm.what_happened[:80]}...")
        console.print()
        return True

    elif action == "view":
        pm_id = Prompt.ask("Enter post-mortem ID to view")
        try:
            pm_id = int(pm_id)
            postmortem = get_postmortem(pm_id, storage_path)
            if not postmortem:
                console.print("[red]Post-mortem not found[/red]")
                return False

            import json

            action_items = json.loads(postmortem.action_items)
            action_items_str = "\n".join([f"  • {item}" for item in action_items])

            content = f"""[bold]Incident #{postmortem.incident_id}[/bold]
Date: {postmortem.timestamp}

[bold]What Happened:[/bold]
{postmortem.what_happened}

[bold]Impact:[/bold]
{postmortem.impact}

[bold]Root Cause:[/bold]
{postmortem.root_cause}

[bold]Resolution:[/bold]
{postmortem.resolution}

[bold]Prevention:[/bold]
{postmortem.prevention}

[bold]Action Items:[/bold]
{action_items_str}
"""
            panel = Panel(
                content,
                title=f"📝 Post-Mortem #{postmortem.id}",
                border_style="cyan",
                padding=(1, 2),
            )
            console.print(panel)
            return True
        except ValueError:
            console.print("[red]Invalid post-mortem ID[/red]")
            return False

    elif action == "export":
        pm_id = Prompt.ask("Enter post-mortem ID to export")
        try:
            pm_id = int(pm_id)
            postmortem = get_postmortem(pm_id, storage_path)
            if not postmortem:
                console.print("[red]Post-mortem not found[/red]")
                return False

            output_path = Path(f"postmortem_{postmortem.id}.md")
            export_postmortem_markdown(postmortem, output_path)
            return True
        except ValueError:
            console.print("[red]Invalid post-mortem ID[/red]")
            return False

    return True
