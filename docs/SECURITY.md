# Security & Secrets

## Secrets Handling

- Do not commit real secrets to the repo.
- Use `.env` locally and protect it with `chmod 600`.
- Prefer per-user config in `~/.config/skillops/skillops.env`.
- For production, prefer OS keyring storage (`skillops secret-set`).

## OS Keyring (recommended)

Enable keyring usage:

```bash
export SKILLOPS_USE_KEYRING=true
```

Store secrets securely:

```bash
skillops secret-set GEMINI_API_KEY
skillops secret-set GITHUB_TOKEN
```

## Rotation

- Rotate API tokens on a scheduled basis (e.g., every 90 days).
- Immediately rotate on suspected compromise.

## Permissions

- Run SkillOps as a non‑root user.
- Keep storage permissions restricted to the user.

## Dependency Updates

- Keep dependencies updated and review CVEs.
- CI runs `safety` and `bandit` scans.
