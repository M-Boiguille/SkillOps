# SkillOps Chaos (Chaos Monkey Local)

SkillOps Chaos is a local chaos engineering module designed to validate resilience and self-healing behavior in dev/test environments.

> **Safety first:** default mode is **dry-run**. No destructive action runs unless `--execute` is provided. Level 3 also requires `--allow-dangerous`.

---

## ✅ Levels

### Level 1 — Killer
Randomly terminates a **Docker container** or **Kubernetes pod**.

- **Mode**: `docker` (default) or `k8s`
- **Action**: `docker kill` or `kubectl delete pod`

### Level 2 — Lagger
Introduces **network latency + packet loss** using `tc netem`.

- **Requires**: root privileges
- **Default**: 300ms delay + 5% loss

### Level 3 — Saboteur
Simulates high-impact failures:

- **Config lock**: `chmod 000` on a file (requires `--config-path`)
- **Disk pressure**: create a large file in storage
- **DNS outage**: block UDP 53 with iptables

---

## 🧪 Usage

Dry-run (safe):
```bash
skillops chaos --level 1 --mode docker --once
```

Execute Level 1 (real):
```bash
skillops chaos --level 1 --mode docker --execute --once
```

Level 2 network degradation (requires root):
```bash
sudo skillops chaos --level 2 --interface docker0 --execute --once
```

Level 3 (requires root + allow-dangerous):
```bash
sudo skillops chaos --level 3 --allow-dangerous --execute --once \
  --config-path /etc/skillops/config.yaml --disk-fill-gb 2
```

---

## 📈 Observability

Every chaos action is logged in SQLite (`chaos_events`):
- timestamp
- level
- mode
- action
- target
- status
- details (JSON)

Use this table to validate self-healing behavior and correlate with monitoring alerts.

---

## ✅ Expected Self-Healing Demo

Example recovery loop:
1. Chaos kills a container (Level 1).
2. Orchestrator restarts pod/container.
3. Monitoring alerts recorded.
4. Chaos logs event to `chaos_events`.

Recommended validation:
- Metrics spike visible in dashboards
- Auto-restart confirmed
- No data loss or corrupted state
