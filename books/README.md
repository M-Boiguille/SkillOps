# 📚 SkillOps Book Processing

Automatic extraction of Zettelkasten notes, flashcards, and Pareto summaries from technical books using Gemini Batch API.

## 🔄 Workflow

```
1. Drop PDF → pending/
2. Submit batch job
3. Wait ~6-24h
4. Fetch results
5. Import to vault
```

## 📁 Directory Structure

```
books/
├── pending/              # Drop PDFs here
│   └── networking-sysadmins.pdf
├── processing/           # Currently processing
│   └── docker-deep-dive/
│       ├── book.pdf
│       └── batch_job.json
├── completed/            # Results ready
│   └── kubernetes-patterns/
│       ├── book.pdf
│       ├── results/
│       │   ├── zettelkasten.json
│       │   ├── flashcards.json
│       │   └── pareto.json
│       └── batch_job.json
└── books-manifest.yaml   # Central tracking
```

## 🎯 Commands

### Check Queue Status (Read-Only)

```bash
skillops check-books
```

**Output:**
```
📚 SkillOps Book Processing Queue

┌────────────────────────┬──────────┬────────────────┬─────────┬────────┐
│ Book                   │ Status   │ Progress       │ Submit  │ Cost   │
├────────────────────────┼──────────┼────────────────┼─────────┼────────┤
│ networking-sysadmins   │ ⚪ Pend  │ ⚪⚪⚪⚪       │ 01/12   │ -      │
│ docker-deep-dive       │ ⏳ Proc  │ ⏳⏳⚪⚪  3h   │ 01/12   │ $0.005 │
│ kubernetes-patterns    │ ✅ Ready │ ✅✅✅⚪       │ 01/11   │ $0.007 │
│ python-asyncio         │ 📚 Imp   │ ✅✅✅✅       │ 01/10   │ $0.004 │
└────────────────────────┴──────────┴────────────────┴─────────┴────────┘

Statistics:
  Total: 4 | Pending: 1 | Processing: 1 | Ready: 1 | Imported: 1 | Failed: 0
  Total Cost: $0.0160
```

### Submit Pending Books

```bash
skillops submit-books
```

Processes all PDFs in `pending/` directory.

### Fetch Completed Results

```bash
skillops fetch-books
```

Downloads results for all completed batch jobs.

### Import to Obsidian Vault

```bash
skillops import-books
```

Imports all ready results to `.skillopsvault/`.

### Full Pipeline

```bash
skillops process-pipeline
```

Runs: submit → check → fetch → import in one command.

## 📖 Example Usage

### Basic Workflow

```bash
# 1. Add book
cp ~/Downloads/networking-book.pdf books/pending/

# 2. Submit
skillops submit-books
# → Creates batch job (ETA: 6-24h)

# 3. Check status (anytime)
skillops check-books

# 4. Wait ~6-24 hours, then fetch
skillops fetch-books
# → Downloads results to completed/

# 5. Import to vault
skillops import-books
# → Creates .skillopsvault/networking-book/
```

### Bulk Processing

```bash
# Add multiple books
cp ~/books/*.pdf books/pending/

# Submit all at once
skillops submit-books
# → Creates batch jobs for each

# One command later
skillops process-pipeline
# → Fetches + imports all ready books
```

## 🎨 What Gets Extracted

For each book, Gemini creates:

### 1. Zettelkasten Notes
- 150-220 atomic concept notes
- Bidirectional backlinks
- Real-world examples
- Common mistakes
- **Format:** `ch1_001_TCP_Three_Way_Handshake.md`

### 2. Flashcards
- 180-204 spaced repetition cards
- 40% Remember, 35% Understand, 25% Apply
- Memory aids + common mistakes
- **Format:** Obsidian-compatible Q&A

### 3. Pareto 20%
- 5 must-know concepts
- 8 should-know concepts
- Top 5 mistakes to avoid
- 12-week learning path
- Toolbox essentials

## 💰 Cost

- **$0.0027/MB** (Gemini Batch API - 50% discount)
- Average book (5MB PDF): **~$0.0135**
- 10 books: **~$0.135** total

## ⏱️ Timeline

- **Submit**: 2 minutes
- **Processing**: 6-24 hours (usually 6-8h)
- **Fetch + Import**: 5 minutes

## 🔧 Configuration

### Required Environment Variables

```bash
GEMINI_API_KEY=your_api_key_here
OBSIDIAN_VAULT_PATH=/path/to/.skillopsvault
```

### Optional Settings

```bash
BOOKS_ROOT=books  # Default: books/
BATCH_TURNAROUND_HOURS=24  # ETA for processing
```

## 🚫 Limitations

- **File size**: Max 2GB per PDF
- **Pages**: Recommended <1000 pages
- **Turnaround**: Max 24 hours (usually 6-8h)
- **Formats**: PDF only (for now)

## 🔍 Troubleshooting

### Book stuck in "Processing"

```bash
# Check Gemini API status
skillops health

# Force re-check status
skillops check-books --refresh
```

### Import failed

```bash
# Check vault path
echo $OBSIDIAN_VAULT_PATH

# Verify results exist
ls books/completed/your-book/results/
```

### Batch job failed

Check `books-manifest.yaml` for error details:

```yaml
- name: problematic-book
  status: failed
  error: "Token limit exceeded - book too large"
```

## 📊 Manifest Format

`books-manifest.yaml` tracks everything:

```yaml
books:
  - name: networking-sysadmins
    status: completed
    pdf_path: books/processing/networking-sysadmins/book.pdf
    submitted_at: 2026-01-12T08:00:00
    batch_job_name: batches/123456789
    completed_at: 2026-01-12T14:23:00
    estimated_completion: 2026-01-12T15:00:00
    results:
      zettelkasten: books/completed/networking-sysadmins/results/zettelkasten.json
      flashcards: books/completed/networking-sysadmins/results/flashcards.json
      pareto: books/completed/networking-sysadmins/results/pareto.json
    metadata:
      pages: 240
      tokens_estimated: 144000
      cost_usd: 0.0054
```

## 🎓 Tips

1. **Submit before bed**: Processing runs overnight
2. **Batch similar books**: Submit multiple books together
3. **Check daily**: Run `check-books` to monitor progress
4. **Start small**: Test with a short book first (~100 pages)

## 🔗 Related

- [Prompts (97.5% quality)](../.personal-notes/networking_book_workflow.md)
- [Gemini Batch API Docs](https://ai.google.dev/gemini-api/docs/batch-api)
- [Zettelkasten Method](https://zettelkasten.de/introduction/)
