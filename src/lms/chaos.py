"""SkillOps Chaos - Local Chaos Monkey for resilience training."""

from __future__ import annotations

import json
import os
import random
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from src.lms.database import get_connection, init_db
from src.lms.paths import get_storage_path


@dataclass
class ChaosConfig:
    level: int
    mode: str
    interval_minutes: int = 30
    duration_minutes: int = 60
    dry_run: bool = True
    execute: bool = False
    allow_dangerous: bool = False
    interface: str = "docker0"
    netem_duration_minutes: int = 5
    config_path: Optional[Path] = None
    disk_fill_gb: int = 10
    only_once: bool = False


@dataclass
class ChaosEvent:
    timestamp: str
    level: int
    mode: str
    action: str
    target: str
    status: str
    details: dict


def log_chaos_event(event: ChaosEvent, storage_path: Optional[Path] = None) -> None:
    """Persist chaos events in SQLite for observability."""
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chaos_events (timestamp, level, mode, action, target, status, details) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            event.timestamp,
            event.level,
            event.mode,
            event.action,
            event.target,
            event.status,
            json.dumps(event.details),
        ),
    )
    conn.commit()
    conn.close()


def _run_command(cmd: List[str], dry_run: bool) -> Tuple[bool, str]:
    if dry_run:
        return True, "dry-run"
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        output = (result.stdout or "").strip() or (result.stderr or "").strip()
        return True, output
    except subprocess.CalledProcessError as exc:
        output = (exc.stdout or "").strip() or (exc.stderr or "").strip()
        return False, output or "command failed"


def _list_docker_containers() -> List[str]:
    ok, output = _run_command(["docker", "ps", "--format", "{{.ID}}"], dry_run=False)
    if not ok:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _list_k8s_pods() -> List[Tuple[str, str]]:
    ok, output = _run_command(
        ["kubectl", "get", "pods", "-A", "-o", "json"], dry_run=False
    )
    if not ok:
        return []
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return []
    pods = []
    for item in data.get("items", []):
        metadata = item.get("metadata", {})
        name = metadata.get("name")
        namespace = metadata.get("namespace")
        if name and namespace:
            pods.append((namespace, name))
    return pods


def _pick_target(mode: str, targets: Optional[List[str]] = None) -> Optional[str]:
    if targets:
        return random.choice(targets)
    if mode == "docker":
        containers = _list_docker_containers()
        return random.choice(containers) if containers else None
    if mode == "k8s":
        pods = _list_k8s_pods()
        if not pods:
            return None
        namespace, name = random.choice(pods)
        return f"{namespace}/{name}"
    return None


def _ensure_root() -> bool:
    return os.geteuid() == 0


def _kill_container(container_id: str, dry_run: bool) -> Tuple[bool, str]:
    return _run_command(["docker", "kill", container_id], dry_run=dry_run)


def _delete_pod(pod_ref: str, dry_run: bool) -> Tuple[bool, str]:
    namespace, name = pod_ref.split("/", 1)
    return _run_command(
        ["kubectl", "delete", "pod", name, "-n", namespace], dry_run=dry_run
    )


def _apply_netem(interface: str, dry_run: bool) -> Tuple[bool, str]:
    return _run_command(
        [
            "tc",
            "qdisc",
            "add",
            "dev",
            interface,
            "root",
            "netem",
            "delay",
            "300ms",
            "loss",
            "5%",
        ],
        dry_run=dry_run,
    )


def _clear_netem(interface: str, dry_run: bool) -> Tuple[bool, str]:
    return _run_command(
        ["tc", "qdisc", "del", "dev", interface, "root"], dry_run=dry_run
    )


def _chmod_config(config_path: Path, dry_run: bool) -> Tuple[bool, str]:
    if dry_run:
        return True, "dry-run"
    try:
        os.chmod(config_path, 0o000)
        return True, "chmod 000"
    except OSError as exc:
        return False, str(exc)


def _disk_fill(storage_path: Path, size_gb: int, dry_run: bool) -> Tuple[bool, str]:
    target = storage_path / "chaos_fill.bin"
    if dry_run:
        return True, f"dry-run: {target}"
    try:
        with open(target, "wb") as handle:
            handle.truncate(size_gb * 1024 * 1024 * 1024)
        return True, f"created {target}"
    except OSError as exc:
        return False, str(exc)


def _block_dns(dry_run: bool) -> Tuple[bool, str]:
    return _run_command(
        ["iptables", "-A", "OUTPUT", "-p", "udp", "--dport", "53", "-j", "DROP"],
        dry_run=dry_run,
    )


def _unblock_dns(dry_run: bool) -> Tuple[bool, str]:
    return _run_command(
        [
            "iptables",
            "-D",
            "OUTPUT",
            "-p",
            "udp",
            "--dport",
            "53",
            "-j",
            "DROP",
        ],
        dry_run=dry_run,
    )


def run_chaos(
    config: ChaosConfig,
    storage_path: Optional[Path] = None,
    targets: Optional[List[str]] = None,
) -> List[ChaosEvent]:
    """Run chaos actions according to config.

    Returns a list of events executed (or dry-run events).
    """
    if config.execute:
        config.dry_run = False

    storage_path = storage_path or get_storage_path()
    events: List[ChaosEvent] = []

    if config.level == 2 and not config.dry_run and not _ensure_root():
        raise PermissionError("Level 2 requires root privileges.")

    if config.level == 3 and not config.dry_run:
        if not config.allow_dangerous:
            raise PermissionError("Level 3 requires --allow-dangerous.")
        if not _ensure_root():
            raise PermissionError("Level 3 requires root privileges.")

    iterations = (
        1
        if config.only_once
        else max(config.duration_minutes // config.interval_minutes, 1)
    )

    for _ in range(iterations):
        timestamp = datetime.now().isoformat()
        if config.level == 1:
            target = _pick_target(config.mode, targets=targets)
            if not target:
                event = ChaosEvent(
                    timestamp=timestamp,
                    level=config.level,
                    mode=config.mode,
                    action="kill",
                    target="none",
                    status="skipped",
                    details={"reason": "no target found"},
                )
                log_chaos_event(event, storage_path)
                events.append(event)
            else:
                if config.mode == "docker":
                    ok, output = _kill_container(target, config.dry_run)
                else:
                    ok, output = _delete_pod(target, config.dry_run)
                event = ChaosEvent(
                    timestamp=timestamp,
                    level=config.level,
                    mode=config.mode,
                    action="kill",
                    target=target,
                    status="success" if ok else "failed",
                    details={"output": output},
                )
                log_chaos_event(event, storage_path)
                events.append(event)
        elif config.level == 2:
            ok, output = _apply_netem(config.interface, config.dry_run)
            event = ChaosEvent(
                timestamp=timestamp,
                level=config.level,
                mode=config.mode,
                action="netem",
                target=config.interface,
                status="success" if ok else "failed",
                details={"output": output},
            )
            log_chaos_event(event, storage_path)
            events.append(event)
            time.sleep(config.netem_duration_minutes * 60)
            _clear_netem(config.interface, config.dry_run)
        elif config.level == 3:
            storage_root = storage_path or get_storage_path()
            actions = ["chmod", "disk", "dns"]
            action = random.choice(actions)
            if action == "chmod":
                if not config.config_path:
                    event = ChaosEvent(
                        timestamp=timestamp,
                        level=config.level,
                        mode=config.mode,
                        action="chmod",
                        target="none",
                        status="skipped",
                        details={"reason": "config_path required"},
                    )
                else:
                    ok, output = _chmod_config(config.config_path, config.dry_run)
                    event = ChaosEvent(
                        timestamp=timestamp,
                        level=config.level,
                        mode=config.mode,
                        action="chmod",
                        target=str(config.config_path),
                        status="success" if ok else "failed",
                        details={"output": output},
                    )
            elif action == "disk":
                ok, output = _disk_fill(
                    storage_root, config.disk_fill_gb, config.dry_run
                )
                event = ChaosEvent(
                    timestamp=timestamp,
                    level=config.level,
                    mode=config.mode,
                    action="disk_fill",
                    target=str(storage_root),
                    status="success" if ok else "failed",
                    details={"output": output, "size_gb": config.disk_fill_gb},
                )
            else:
                ok, output = _block_dns(config.dry_run)
                event = ChaosEvent(
                    timestamp=timestamp,
                    level=config.level,
                    mode=config.mode,
                    action="block_dns",
                    target="udp/53",
                    status="success" if ok else "failed",
                    details={"output": output},
                )
                _unblock_dns(config.dry_run)
            log_chaos_event(event, storage_path)
            events.append(event)

        if not config.only_once:
            time.sleep(config.interval_minutes * 60)

    return events
