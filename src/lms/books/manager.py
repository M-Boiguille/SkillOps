"""Book Processing Manager - Batch extraction with Gemini API."""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yaml
from google import genai
from rich.console import Console
from rich.table import Table

console = Console()


class BookStatus:
    """Book processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    IMPORTED = "imported"
    FAILED = "failed"


class BooksManager:
    """Manage book extraction queue and batch processing."""

    def __init__(self, books_root: Path = Path("books")):
        self.books_root = books_root
        self.pending_dir = books_root / "pending"
        self.processing_dir = books_root / "processing"
        self.completed_dir = books_root / "completed"
        self.manifest_path = books_root / "books-manifest.yaml"

        # Ensure directories exist
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.processing_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)

        # Load or create manifest
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        """Load books manifest or create if missing."""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return yaml.safe_load(f) or {"books": [], "statistics": {}}
        return {
            "version": "1.0",
            "last_updated": None,
            "books": [],
            "statistics": {
                "total_books": 0,
                "pending": 0,
                "processing": 0,
                "completed": 0,
                "imported": 0,
                "failed": 0,
                "total_cost_usd": 0.0
            }
        }

    def _save_manifest(self):
        """Save manifest to YAML."""
        self.manifest["last_updated"] = datetime.now().isoformat()
        self._update_statistics()

        with open(self.manifest_path, 'w') as f:
            yaml.dump(self.manifest, f, default_flow_style=False, sort_keys=False)

    def _update_statistics(self):
        """Update statistics from book list."""
        stats = {
            "total_books": len(self.manifest["books"]),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "imported": 0,
            "failed": 0,
            "total_cost_usd": 0.0
        }

        for book in self.manifest["books"]:
            status = book.get("status", BookStatus.PENDING)
            stats[status] = stats.get(status, 0) + 1

            if book.get("metadata", {}).get("cost_usd"):
                stats["total_cost_usd"] += book["metadata"]["cost_usd"]

        self.manifest["statistics"] = stats

    def get_book(self, name: str) -> Optional[dict]:
        """Get book entry from manifest."""
        for book in self.manifest["books"]:
            if book["name"] == name:
                return book
        return None

    def add_book(self, name: str, pdf_path: Path) -> dict:
        """Add new book to manifest."""
        # Check if already exists
        existing = self.get_book(name)
        if existing:
            console.print(f"[yellow]⚠️  Book '{name}' already exists with status: {existing['status']}[/yellow]")
            return existing

        book_entry = {
            "name": name,
            "status": BookStatus.PENDING,
            "pdf_path": str(pdf_path),
            "submitted_at": datetime.now().isoformat(),
            "batch_job_name": None,
            "completed_at": None,
            "estimated_completion": None,
            "imported_at": None,
            "results": {
                "zettelkasten": None,
                "flashcards": None,
                "pareto": None
            },
            "metadata": {
                "pages": None,
                "tokens_estimated": None,
                "cost_usd": None
            },
            "error": None
        }

        self.manifest["books"].append(book_entry)
        self._save_manifest()

        return book_entry

    def update_book_status(self, name: str, status: str, **kwargs):
        """Update book status and metadata."""
        book = self.get_book(name)
        if not book:
            raise ValueError(f"Book '{name}' not found in manifest")

        book["status"] = status

        # Update additional fields
        for key, value in kwargs.items():
            if key in book:
                book[key] = value
            elif key in book.get("metadata", {}):
                book["metadata"][key] = value

        self._save_manifest()

    def submit_pending_books(self, gemini_api_key: str):
        """Submit all pending PDFs for batch processing."""
        console.print("\n[bold cyan]📤 Submitting Pending Books[/bold cyan]\n")

        # Scan pending directory for PDFs
        pdf_files = list(self.pending_dir.glob("*.pdf"))

        if not pdf_files:
            console.print("[yellow]No PDF files found in books/pending/[/yellow]\n")
            return

        console.print(f"Found {len(pdf_files)} PDF(s) to process:\n")

        # Initialize Gemini client
        client = genai.Client(api_key=gemini_api_key)

        for pdf_path in pdf_files:
            book_name = pdf_path.stem  # filename without extension

            console.print(f"[cyan]📖 Processing: {book_name}[/cyan]")

            # Check if already in manifest
            existing = self.get_book(book_name)
            if existing and existing["status"] != BookStatus.FAILED:
                console.print(f"  [yellow]⚠️  Already exists with status: {existing['status']}[/yellow]")
                continue

            try:
                # Add to manifest if new
                if not existing:
                    self.add_book(book_name, pdf_path)

                # 1. Upload PDF to Gemini Files API
                console.print(f"  [dim]⏳ Uploading PDF...[/dim]")
                uploaded_file = client.files.upload(
                    file=str(pdf_path),
                    config=genai.types.UploadFileConfig(
                        display_name=f"{book_name}_source",
                        mime_type="application/pdf"
                    )
                )
                console.print(f"  [green]✓ Uploaded: {uploaded_file.name}[/green]")

                # 2. Create JSONL batch requests
                batch_requests = self._create_batch_requests(book_name, uploaded_file.name)

                # 3. Write JSONL to processing directory
                book_processing_dir = self.processing_dir / book_name
                book_processing_dir.mkdir(exist_ok=True)

                jsonl_path = book_processing_dir / "batch_requests.jsonl"
                with open(jsonl_path, 'w') as f:
                    for req in batch_requests:
                        f.write(json.dumps(req) + "\n")

                console.print(f"  [green]✓ Created batch requests: 3 outputs[/green]")

                # 4. Upload JSONL and create batch job
                console.print(f"  [dim]⏳ Creating batch job...[/dim]")
                uploaded_jsonl = client.files.upload(
                    file=str(jsonl_path),
                    config=genai.types.UploadFileConfig(
                        display_name=f"{book_name}_batch",
                        mime_type="application/jsonl"
                    )
                )

                batch_job = client.batches.create(
                    model="gemini-2.0-flash-exp",
                    src=uploaded_jsonl.name,
                    config={
                        "display_name": f"skillops_{book_name}"
                    }
                )

                console.print(f"  [green]✓ Batch job created: {batch_job.name}[/green]")
                console.print(f"    State: {batch_job.state}")

                # 5. Estimate cost (rough calculation)
                # Assuming 600 tokens/page, 3 outputs
                pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)
                estimated_pages = int(pdf_size_mb * 100)  # rough estimate
                estimated_tokens = estimated_pages * 600 * 3
                estimated_cost = (estimated_tokens / 1_000_000) * 0.000075  # $0.075/1M tokens for batch

                # 6. Update manifest
                estimated_completion = datetime.now() + timedelta(hours=24)
                self.update_book_status(
                    book_name,
                    BookStatus.PROCESSING,
                    batch_job_name=batch_job.name,
                    estimated_completion=estimated_completion.isoformat(),
                    pages=estimated_pages,
                    tokens_estimated=estimated_tokens,
                    cost_usd=estimated_cost
                )

                # 7. Move PDF to processing directory
                dest_pdf = book_processing_dir / pdf_path.name
                pdf_path.rename(dest_pdf)
                self.update_book_status(book_name, BookStatus.PROCESSING, pdf_path=str(dest_pdf))

                console.print(f"  [green]✅ Submitted successfully![/green]")
                console.print(f"    Estimated cost: ${estimated_cost:.4f}")
                console.print(f"    ETA: ~24 hours\n")

            except Exception as e:
                console.print(f"  [red]❌ Error: {str(e)}[/red]\n")
                if existing or self.get_book(book_name):
                    self.update_book_status(
                        book_name,
                        BookStatus.FAILED,
                        error=str(e)
                    )

        console.print("[bold green]✅ Submission complete![/bold green]\n")

    def _create_batch_requests(self, book_name: str, file_uri: str) -> list:
        """Create 3 batch requests for Zettelkasten, Flashcards, and Pareto outputs."""

        # Load prompts from workflow file
        prompts = self._load_prompts()

        requests = []
        for idx, (output_type, prompt) in enumerate(prompts.items()):
            request = {
                "key": f"{book_name}_{output_type}",
                "request": {
                    "model": "gemini-2.0-flash-exp",
                    "contents": [
                        {
                            "parts": [
                                {
                                    "file_data": {
                                        "mime_type": "application/pdf",
                                        "file_uri": file_uri
                                    }
                                },
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "responseMimeType": "application/json"
                    }
                }
            }
            requests.append(request)

        return requests

    def _load_prompts(self) -> dict:
        """Load prompts from networking_book_workflow.md."""
        workflow_path = Path(".personal-notes/networking_book_workflow.md")

        if not workflow_path.exists():
            # Fallback: use simplified prompts
            return {
                "zettelkasten": "Extract atomic Zettelkasten notes from this book. For each concept create JSON with: id, chapter, atomic_concept, content (1800-2000 chars), context, key_points (array), example_or_use_case, common_mistakes, tags (array), source_page, related_concepts (array with concept_id, relationship, why). Target 12-18 concepts per chapter. Output as JSON array.",
                "flashcards": "Create flashcards from this book using Bloom's taxonomy. For each flashcard create JSON with: id, chapter, question (80-120 chars), answer (200-350 chars), bloom_level (remember/understand/apply), difficulty (1-5), estimated_time (seconds), tags (array), memory_aid. Target 15±2 cards per chapter. Distribution: 40% remember, 35% understand, 25% apply. Output as JSON array.",
                "pareto": "Extract the critical 20% of concepts that provide 80% of value. Create JSON with: must_know_concepts (5 items with concept, why_critical, mastery_level, page_refs), should_know_concepts (8 items), nice_to_know_concepts (5 items), common_mistakes (array), learning_path_12_weeks (with weekly focus), quick_reference (toolbox). Output as JSON object."
            }

        # Parse actual prompts from markdown
        content = workflow_path.read_text()
        prompts = {}

        # Extract PROMPT A (Zettelkasten)
        if "### PROMPT A:" in content:
            start = content.index("### PROMPT A:")
            end = content.index("### PROMPT B:", start)
            prompt_a = content[start:end]
            # Extract markdown code block
            if "```markdown" in prompt_a:
                code_start = prompt_a.index("```markdown") + 11
                code_end = prompt_a.index("```", code_start)
                prompts["zettelkasten"] = prompt_a[code_start:code_end].strip()

        # Extract PROMPT B (Flashcards)
        if "### PROMPT B:" in content:
            start = content.index("### PROMPT B:")
            end = content.index("### PROMPT C:", start)
            prompt_b = content[start:end]
            if "```markdown" in prompt_b:
                code_start = prompt_b.index("```markdown") + 11
                code_end = prompt_b.index("```", code_start)
                prompts["flashcards"] = prompt_b[code_start:code_end].strip()

        # Extract PROMPT C (Pareto)
        if "### PROMPT C:" in content:
            start = content.index("### PROMPT C:")
            # Find next section or end
            next_section = content.find("###", start + 15)
            if next_section == -1:
                next_section = content.find("##", start + 15)
            if next_section == -1:
                next_section = len(content)
            prompt_c = content[start:next_section]
            if "```markdown" in prompt_c:
                code_start = prompt_c.index("```markdown") + 11
                code_end = prompt_c.index("```", code_start)
                prompts["pareto"] = prompt_c[code_start:code_end].strip()

        # Fallback if parsing failed
        if len(prompts) != 3:
            console.print("[yellow]⚠️  Could not parse all prompts from workflow file, using simplified versions[/yellow]")
            return {
                "zettelkasten": "Extract atomic Zettelkasten notes from this book. Target 12-18 concepts per chapter with 1800-2000 char content. Output as JSON array.",
                "flashcards": "Create flashcards using Bloom's taxonomy. Target 15±2 cards per chapter. 40% remember, 35% understand, 25% apply. Output as JSON array.",
                "pareto": "Extract critical 20% (5 must-know + 8 should-know + 5 nice-to-know). Output as JSON object."
            }

        return prompts

    def fetch_completed_books(self, gemini_api_key: str, book_name: Optional[str] = None):
        """Fetch results from completed batch jobs."""
        console.print("\n[bold cyan]📥 Fetching Completed Books[/bold cyan]\n")

        # Initialize Gemini client
        client = genai.Client(api_key=gemini_api_key)

        # Get books to check
        books_to_check = []
        if book_name:
            book = self.get_book(book_name)
            if not book:
                console.print(f"[red]❌ Book '{book_name}' not found[/red]\n")
                return
            books_to_check = [book]
        else:
            # Check all processing books
            books_to_check = [b for b in self.manifest["books"] if b["status"] == BookStatus.PROCESSING]

        if not books_to_check:
            console.print("[yellow]No books currently processing[/yellow]\n")
            return

        console.print(f"Checking {len(books_to_check)} book(s)...\n")

        for book in books_to_check:
            name = book["name"]
            batch_job_name = book.get("batch_job_name")

            if not batch_job_name:
                console.print(f"[yellow]⚠️  {name}: No batch job name found[/yellow]")
                continue

            console.print(f"[cyan]📖 {name}[/cyan]")

            try:
                # Check batch job status
                console.print(f"  [dim]⏳ Checking batch status...[/dim]")
                batch_job = client.batches.get(batch_job_name)

                console.print(f"  Status: {batch_job.state}")

                if batch_job.state == "STATE_SUCCEEDED":
                    console.print(f"  [green]✓ Batch completed successfully![/green]")

                    # Download output JSONL
                    console.print(f"  [dim]⏳ Downloading results...[/dim]")

                    # Get output file
                    if not batch_job.output_uri:
                        console.print(f"  [red]❌ No output URI found[/red]")
                        continue

                    # Download the output file
                    output_file = client.files.get(batch_job.output_uri)
                    output_content = output_file.read()

                    # Parse JSONL results (one line per output type)
                    results = {}
                    for line in output_content.strip().split('\n'):
                        if not line.strip():
                            continue
                        result_item = json.loads(line)
                        key = result_item.get("key", "")

                        # Extract output type from key (e.g., "book_zettelkasten")
                        if "_zettelkasten" in key:
                            output_type = "zettelkasten"
                        elif "_flashcards" in key:
                            output_type = "flashcards"
                        elif "_pareto" in key:
                            output_type = "pareto"
                        else:
                            continue

                        # Extract the actual JSON response
                        response = result_item.get("response", {})
                        content = response.get("candidates", [{}])[0].get("content", {})
                        parts = content.get("parts", [{}])
                        if parts:
                            text = parts[0].get("text", "")
                            if text:
                                try:
                                    results[output_type] = json.loads(text)
                                except json.JSONDecodeError:
                                    console.print(f"  [yellow]⚠️  Failed to parse {output_type} JSON[/yellow]")

                    if len(results) != 3:
                        console.print(f"  [yellow]⚠️  Expected 3 outputs, got {len(results)}[/yellow]")

                    # Save results to completed directory
                    book_completed_dir = self.completed_dir / name
                    book_completed_dir.mkdir(exist_ok=True)
                    results_dir = book_completed_dir / "results"
                    results_dir.mkdir(exist_ok=True)

                    for output_type, data in results.items():
                        result_path = results_dir / f"{output_type}.json"
                        with open(result_path, 'w') as f:
                            json.dump(data, f, indent=2)
                        console.print(f"  [green]✓ Saved {output_type}.json[/green]")

                    # Move PDF from processing to completed
                    processing_dir = self.processing_dir / name
                    if processing_dir.exists():
                        # Find PDF file
                        pdf_files = list(processing_dir.glob("*.pdf"))
                        if pdf_files:
                            dest_pdf = book_completed_dir / pdf_files[0].name
                            pdf_files[0].rename(dest_pdf)

                        # Move batch files
                        for batch_file in processing_dir.glob("batch_*"):
                            dest = book_completed_dir / batch_file.name
                            batch_file.rename(dest)

                        # Remove processing directory
                        processing_dir.rmdir()

                    # Update manifest
                    self.update_book_status(
                        name,
                        BookStatus.COMPLETED,
                        completed_at=datetime.now().isoformat(),
                        pdf_path=str(book_completed_dir / pdf_files[0].name) if pdf_files else book.get("pdf_path")
                    )

                    # Update results paths
                    book_entry = self.get_book(name)
                    book_entry["results"]["zettelkasten"] = str(results_dir / "zettelkasten.json")
                    book_entry["results"]["flashcards"] = str(results_dir / "flashcards.json")
                    book_entry["results"]["pareto"] = str(results_dir / "pareto.json")
                    self._save_manifest()

                    console.print(f"  [green]✅ Results downloaded and saved![/green]\n")

                elif batch_job.state == "STATE_FAILED":
                    console.print(f"  [red]❌ Batch job failed[/red]")
                    error_msg = getattr(batch_job, 'error', 'Unknown error')
                    console.print(f"  Error: {error_msg}")

                    self.update_book_status(
                        name,
                        BookStatus.FAILED,
                        error=str(error_msg)
                    )
                    console.print()

                else:
                    # Still processing
                    console.print(f"  [yellow]⏳ Still processing... (State: {batch_job.state})[/yellow]")
                    if book.get("estimated_completion"):
                        est_time = datetime.fromisoformat(book["estimated_completion"])
                        remaining = est_time - datetime.now()
                        hours_left = max(0, int(remaining.total_seconds() / 3600))
                        console.print(f"  Estimated time remaining: ~{hours_left}h\n")
                    else:
                        console.print()

            except Exception as e:
                console.print(f"  [red]❌ Error: {str(e)}[/red]\n")
                self.update_book_status(name, BookStatus.FAILED, error=str(e))

        console.print("[bold green]✅ Fetch complete![/bold green]\n")

    def import_books_to_vault(self, vault_path: Optional[str] = None, book_name: Optional[str] = None):
        """Import completed books to Obsidian vault."""
        console.print("\n[bold cyan]📚 Importing Books to Vault[/bold cyan]\n")

        # Get vault path
        if not vault_path:
            vault_path = os.getenv("OBSIDIAN_VAULT_PATH", ".skillopsvault")

        vault_root = Path(vault_path)
        if not vault_root.exists():
            console.print(f"[yellow]⚠️  Creating vault: {vault_path}[/yellow]")
            vault_root.mkdir(parents=True, exist_ok=True)

        # Get books to import
        books_to_import = []
        if book_name:
            book = self.get_book(book_name)
            if not book:
                console.print(f"[red]❌ Book '{book_name}' not found[/red]\n")
                return
            if book["status"] != BookStatus.COMPLETED:
                console.print(f"[yellow]⚠️  Book '{book_name}' is not completed (status: {book['status']})[/yellow]\n")
                return
            books_to_import = [book]
        else:
            # Import all completed books
            books_to_import = [b for b in self.manifest["books"] if b["status"] == BookStatus.COMPLETED]

        if not books_to_import:
            console.print("[yellow]No completed books to import[/yellow]\n")
            return

        console.print(f"Importing {len(books_to_import)} book(s)...\n")

        for book in books_to_import:
            name = book["name"]
            console.print(f"[cyan]📖 {name}[/cyan]")

            try:
                # Create book directory in vault
                book_vault_dir = vault_root / name
                book_vault_dir.mkdir(exist_ok=True)

                # Load results
                zettel_path = Path(book["results"]["zettelkasten"])
                flash_path = Path(book["results"]["flashcards"])
                pareto_path = Path(book["results"]["pareto"])

                if not all([zettel_path.exists(), flash_path.exists(), pareto_path.exists()]):
                    console.print(f"  [red]❌ Missing result files[/red]")
                    continue

                with open(zettel_path) as f:
                    zettelkasten_data = json.load(f)
                with open(flash_path) as f:
                    flashcards_data = json.load(f)
                with open(pareto_path) as f:
                    pareto_data = json.load(f)

                # 1. Create Zettelkasten notes
                console.print(f"  [dim]⏳ Creating Zettelkasten notes...[/dim]")
                zettel_dir = book_vault_dir / "zettelkasten"
                zettel_dir.mkdir(exist_ok=True)

                # Handle both array and object formats
                notes = zettelkasten_data if isinstance(zettelkasten_data, list) else zettelkasten_data.get("zettelkasten", [])

                for note in notes:
                    note_id = note.get("id", "")
                    note_file = zettel_dir / f"{note_id}.md"

                    # Build markdown content
                    content = f"# {note.get('atomic_concept', 'Untitled')}\n\n"
                    content += f"**Chapter:** {note.get('chapter', 'N/A')}  \n"
                    content += f"**Source Page:** {note.get('source_page', 'N/A')}  \n"
                    content += f"**Tags:** {', '.join(['#' + t for t in note.get('tags', [])])}\n\n"
                    content += "## Content\n\n"
                    content += f"{note.get('content', '')}\n\n"
                    content += "## Context\n\n"
                    content += f"{note.get('context', '')}\n\n"
                    content += "## Key Points\n\n"
                    for point in note.get('key_points', []):
                        content += f"- {point}\n"
                    content += "\n## Example / Use Case\n\n"
                    content += f"{note.get('example_or_use_case', '')}\n\n"
                    content += "## Common Mistakes\n\n"
                    content += f"{note.get('common_mistakes', '')}\n\n"
                    content += "## Related Concepts\n\n"
                    for rel in note.get('related_concepts', []):
                        concept_id = rel.get('concept_id', '')
                        relationship = rel.get('relationship', '')
                        why = rel.get('why', '')
                        content += f"- [[{concept_id}]] ({relationship}): {why}\n"

                    note_file.write_text(content)

                console.print(f"  [green]✓ Created {len(notes)} Zettelkasten notes[/green]")

                # 2. Create flashcards
                console.print(f"  [dim]⏳ Creating flashcards...[/dim]")
                flashcards_dir = book_vault_dir / "flashcards"
                flashcards_dir.mkdir(exist_ok=True)

                # Handle both array and object formats
                cards = flashcards_data if isinstance(flashcards_data, list) else flashcards_data.get("flashcards", [])

                # Create single deck file
                deck_file = flashcards_dir / f"{name}-deck.md"
                deck_content = f"# {name} - Flashcards\n\n"
                deck_content += f"Total Cards: {len(cards)}\n\n"
                deck_content += "---\n\n"

                for card in cards:
                    deck_content += f"## Card: {card.get('id', '')}\n\n"
                    deck_content += f"**Chapter:** {card.get('chapter', 'N/A')}  \n"
                    deck_content += f"**Level:** {card.get('bloom_level', 'N/A')} (Difficulty: {card.get('difficulty', 'N/A')})  \n"
                    deck_content += f"**Tags:** {', '.join(['#' + t for t in card.get('tags', [])])}\n\n"
                    deck_content += f"Q: {card.get('question', '')}\n\n"
                    deck_content += f"A: {card.get('answer', '')}\n\n"
                    if card.get('memory_aid'):
                        deck_content += f"💡 **Memory Aid:** {card['memory_aid']}\n\n"
                    deck_content += "---\n\n"

                deck_file.write_text(deck_content)
                console.print(f"  [green]✓ Created {len(cards)} flashcards[/green]")

                # 3. Create Pareto summaries
                console.print(f"  [dim]⏳ Creating Pareto summaries...[/dim]")
                pareto_dir = book_vault_dir / "pareto"
                pareto_dir.mkdir(exist_ok=True)

                # Get Pareto sections
                pareto_content = pareto_data.get("pareto_20_percent", pareto_data)

                # Must-know concepts
                must_know_file = pareto_dir / "must-know.md"
                must_content = f"# Must-Know Concepts (Critical 20%)\n\n"
                for idx, item in enumerate(pareto_content.get("must_know_concepts", []), 1):
                    must_content += f"## {idx}. {item.get('concept', 'Untitled')}\n\n"
                    must_content += f"**Why Critical:** {item.get('why_critical', '')}\n\n"
                    must_content += f"**Mastery Level:** {item.get('mastery_level', 'N/A')}  \n"
                    must_content += f"**Pages:** {', '.join(map(str, item.get('page_refs', [])))}\n\n"
                must_know_file.write_text(must_content)

                # Should-know concepts
                should_know_file = pareto_dir / "should-know.md"
                should_content = f"# Should-Know Concepts\n\n"
                for idx, item in enumerate(pareto_content.get("should_know_concepts", []), 1):
                    should_content += f"## {idx}. {item.get('concept', 'Untitled')}\n\n"
                    should_content += f"**Why Important:** {item.get('why_important', item.get('why_critical', ''))}\n\n"
                should_know_file.write_text(should_content)

                # Learning path
                learning_path_file = pareto_dir / "learning-path.md"
                lp_content = f"# 12-Week Learning Path\n\n"
                for week in pareto_content.get("learning_path_12_weeks", []):
                    lp_content += f"## Week {week.get('week', 'N/A')}: {week.get('focus', 'N/A')}\n\n"
                    lp_content += f"**Concepts:** {', '.join(week.get('concepts', []))}\n\n"
                    if week.get('labs'):
                        lp_content += f"**Labs:** {', '.join(week.get('labs', []))}\n\n"
                learning_path_file.write_text(lp_content)

                console.print(f"  [green]✓ Created Pareto summaries[/green]")

                # 4. Create MOC (Map of Content)
                console.print(f"  [dim]⏳ Creating MOC...[/dim]")
                moc_file = book_vault_dir / "00-INDEX.md"
                moc_content = f"# {name} - Map of Content\n\n"
                moc_content += f"**Status:** Imported  \n"
                moc_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
                moc_content += "## Structure\n\n"
                moc_content += "- [[zettelkasten/]] - Atomic concept notes\n"
                moc_content += "- [[flashcards/]] - Spaced repetition cards\n"
                moc_content += "- [[pareto/]] - Critical 20% summaries\n\n"
                moc_content += f"## Statistics\n\n"
                moc_content += f"- Zettelkasten Notes: {len(notes)}\n"
                moc_content += f"- Flashcards: {len(cards)}\n"
                moc_content += f"- Must-Know Concepts: {len(pareto_content.get('must_know_concepts', []))}\n"
                moc_content += f"- Should-Know Concepts: {len(pareto_content.get('should_know_concepts', []))}\n\n"
                moc_file.write_text(moc_content)

                console.print(f"  [green]✓ Created MOC[/green]")

                # Update manifest
                self.update_book_status(
                    name,
                    BookStatus.IMPORTED,
                    imported_at=datetime.now().isoformat()
                )

                console.print(f"  [green]✅ Import complete![/green]\n")

            except Exception as e:
                console.print(f"  [red]❌ Error: {str(e)}[/red]\n")
                import traceback
                console.print(f"  [dim]{traceback.format_exc()}[/dim]\n")

        console.print(f"[bold green]✅ All imports complete![/bold green]")
        console.print(f"[cyan]📂 Vault location: {vault_root.absolute()}[/cyan]\n")

    def display_queue(self):
        """Display books queue in rich table (read-only)."""
        console.print("\n[bold cyan]📚 SkillOps Book Processing Queue[/bold cyan]\n")

        if not self.manifest["books"]:
            console.print("[yellow]No books in queue. Add PDFs to books/pending/[/yellow]\n")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Book", style="cyan", no_wrap=False, width=30)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Progress", justify="center", width=20)
        table.add_column("Submitted", justify="center", width=16)
        table.add_column("Cost", justify="right", width=10)

        for book in self.manifest["books"]:
            name = book["name"]
            status = book["status"]

            # Status emoji and color
            status_display = {
                BookStatus.PENDING: "⚪ Pending",
                BookStatus.PROCESSING: "⏳ Processing",
                BookStatus.COMPLETED: "✅ Ready",
                BookStatus.IMPORTED: "📚 Imported",
                BookStatus.FAILED: "❌ Failed"
            }.get(status, status)

            # Progress bar
            progress_symbols = {
                BookStatus.PENDING: "⚪⚪⚪⚪",
                BookStatus.PROCESSING: "⏳⏳⚪⚪",
                BookStatus.COMPLETED: "✅✅✅⚪",
                BookStatus.IMPORTED: "✅✅✅✅",
                BookStatus.FAILED: "❌❌❌❌"
            }
            progress = progress_symbols.get(status, "⚪⚪⚪⚪")

            # Time info
            if status == BookStatus.PROCESSING and book.get("estimated_completion"):
                est_time = datetime.fromisoformat(book["estimated_completion"])
                remaining = est_time - datetime.now()
                hours_left = int(remaining.total_seconds() / 3600)
                progress += f" {hours_left}h"

            # Submitted time
            submitted = datetime.fromisoformat(book["submitted_at"])
            submitted_str = submitted.strftime("%m/%d %H:%M")

            # Cost
            cost = book.get("metadata", {}).get("cost_usd")
            cost_str = f"${cost:.4f}" if cost else "-"

            table.add_row(
                name,
                status_display,
                progress,
                submitted_str,
                cost_str
            )

        console.print(table)

        # Statistics
        stats = self.manifest["statistics"]
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total: {stats['total_books']} | "
                     f"Pending: {stats['pending']} | "
                     f"Processing: {stats['processing']} | "
                     f"Ready: {stats['completed']} | "
                     f"Imported: {stats['imported']} | "
                     f"Failed: {stats['failed']}")
        console.print(f"  Total Cost: [green]${stats['total_cost_usd']:.4f}[/green]\n")


def check_books_command():
    """CLI command to display book queue."""
    manager = BooksManager()
    manager.display_queue()


def submit_books_command(api_key: Optional[str] = None):
    """CLI command to submit pending books."""
    import os

    # Get API key from parameter or environment
    gemini_api_key = api_key or os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        console.print("[red]❌ Error: GEMINI_API_KEY not found in environment[/red]")
        console.print("[yellow]Set it with: export GEMINI_API_KEY='your-key'[/yellow]\n")
        return

    manager = BooksManager()
    manager.submit_pending_books(gemini_api_key)


def fetch_books_command(api_key: Optional[str] = None, book_name: Optional[str] = None):
    """CLI command to fetch completed books."""
    import os

    # Get API key from parameter or environment
    gemini_api_key = api_key or os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        console.print("[red]❌ Error: GEMINI_API_KEY not found in environment[/red]")
        console.print("[yellow]Set it with: export GEMINI_API_KEY='your-key'[/yellow]\n")
        return

    manager = BooksManager()
    manager.fetch_completed_books(gemini_api_key, book_name)


def import_books_command(vault_path: Optional[str] = None, book_name: Optional[str] = None):
    """CLI command to import books to vault."""
    manager = BooksManager()
    manager.import_books_to_vault(vault_path, book_name)


def process_pipeline_command(gemini_api_key: Optional[str] = None, watch: bool = False, interval: int = 30):
    """CLI command to run complete book processing pipeline."""
    import time
    import threading

    # Get API key from parameter or environment
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        console.print("[red]❌ Error: GEMINI_API_KEY not found in environment[/red]")
        console.print("[yellow]Set it with: export GEMINI_API_KEY='your-key'[/yellow]\n")
        return

    manager = BooksManager()

    if not watch:
        # Run once: submit → fetch → import
        console.print("\n[bold cyan]🚀 SkillOps Book Processing Pipeline[/bold cyan]\n")
        console.print("[dim]Mode: One-time run[/dim]\n")

        # Step 1: Submit pending books
        manager.submit_pending_books(gemini_api_key)

        # Step 2: Fetch completed books
        manager.fetch_completed_books(gemini_api_key)

        # Step 3: Import to vault
        manager.import_books_to_vault()

        console.print("\n[bold green]✅ Pipeline complete![/bold green]\n")

    else:
        # Watch mode: continuous polling
        console.print("\n[bold cyan]🚀 SkillOps Book Processing Pipeline[/bold cyan]\n")
        console.print(f"[dim]Mode: Watch with {interval}min polling[/dim]\n")

        # Step 1: Submit pending books
        manager.submit_pending_books(gemini_api_key)

        # Step 2: Monitor until all done
        console.print(f"\n[bold cyan]⏳ Monitoring books (checking every {interval}min)[/bold cyan]\n")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")

        all_done = False
        iteration = 0

        try:
            while not all_done:
                iteration += 1
                console.print(f"\n[bold magenta]Iteration {iteration}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold magenta]")

                # Check queue status
                manager = BooksManager()  # Reload manifest
                manager.display_queue()

                # Check if any books are still processing
                processing_books = [b for b in manager.manifest["books"] if b["status"] == BookStatus.PROCESSING]
                completed_books = [b for b in manager.manifest["books"] if b["status"] == BookStatus.COMPLETED]

                if processing_books:
                    console.print(f"\n[cyan]Still waiting for {len(processing_books)} book(s)...[/cyan]")
                    console.print(f"[dim]Next check in {interval} minutes[/dim]\n")

                    # Sleep before next iteration
                    time.sleep(interval * 60)
                else:
                    # All done! Fetch and import
                    if completed_books:
                        console.print("\n[bold green]📥 Fetching results for completed books...[/bold green]\n")
                        manager.fetch_completed_books(gemini_api_key)

                    # Import any books ready for import
                    console.print("\n[bold green]📚 Importing to vault...[/bold green]\n")
                    manager.import_books_to_vault()

                    all_done = True

        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️  Pipeline monitoring stopped[/yellow]")
            console.print("[dim]You can resume anytime with: skillops process-pipeline --watch[/dim]\n")

    console.print("[bold green]✅ Done![/bold green]\n")
