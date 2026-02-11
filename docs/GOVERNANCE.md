# Governance & Usage Limits

## Usage Limits

- Prefer daily runs with systemd/cron timers.
- Avoid running high‑cost API steps in tight loops.

## Rate Limiting Guidelines

- GitHub: batch projects and avoid repeated retries.
- Telegram: respect schedule windows.
- Gemini/WakaTime: avoid parallel runs.

## SLA / Expectations

- Best‑effort CLI tool with daily automation.
- Errors are surfaced via logs and optional alerts.
