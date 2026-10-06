# Plan Review: containerize-shb-scheduler-postgres18

**Reviewed:** 2026-10-06T00:55:00Z  
**Providers:** Hermes (Spec Compliance), Claude Code (Security), Codex (Quality & Tests), Antigravity (Architecture), Kimi (Product Scope), OpenCode (Failure Modes)  
**Status:** Approved for Apply  

## Alignment Summary

| Edge | Status | Provider | Evidence |
| :--- | :--- | :--- | :--- |
| **Spec ↔ Code** | PASS | Hermes | Delta spec `shb-schedule-engine` accurately specifies Compose topology, PostgreSQL 18.6 schema isolation, and host installer removal. |
| **Code ↔ Docs** | PASS | Codex | Docker Compose and Dockerfile specifications align with modern Python 3.14 slim and uv multi-stage container patterns. |
| **Docs ↔ Skills** | PASS | Antigravity | Containerized trigger patterns (`docker compose exec`) and port 9110 health checks align with `scheduler-skill`. |
| **Skills ↔ Specs** | PASS | Kimi | Production profile mounts only `~/.shb/schedules/*.yaml:ro`, cleanly isolating developer repositories. |
| **Spec ↔ Docs** | PASS | Hermes | Host service installer deprecation is consistently planned across spec, design, and tasks. |
| **Code ↔ Skills** | PASS | Antigravity | Elimination of LaunchAgent/systemd host coupling resolves init system fragmentation across macOS and Linux. |
| **Spec ↔ Tests** | PASS | Codex | Scenarios specify testable criteria: clean Postgres 18.6 startup, DBOS auto-bootstrap, and CLI verification. |
| **Code ↔ Tests** | PASS | Codex | Tasks specify unit and integration checks including in-container manifest validation and durable execution. |
| **Knowledge ↔ Code** | PASS | Hermes | Live feasibility POC proved DBOS Transact auto-bootstraps 13 tables into PostgreSQL 18.6 in 0.706 seconds. |

---

## Security Lens (Claude Code)

| Edge | Status | Evidence |
| :--- | :--- | :--- |
| **Named Volume Isolation** | PASS | PostgreSQL 18.6 data persisted in Docker named volume, preventing virtiofs WAL corruption. |
| **Read-Only Manifests** | PASS | Production stack mounts only `/etc/shb/schedules:ro`, preventing container from mutating manifests. |
| **Non-Root Container** | PASS | Dockerfile specifies non-root user execution (`user: agent`), avoiding root escalation hazards. |
| **Zero Credential Exposure** | PASS | Password parameterized via `${SHB_SCHEDULER_DB_PASSWORD:-shb_dev_secret}`; port 9110 health checks omit credentials. |

---

## Provider Findings & Adjustments Applied

### 1. OpenCode (Failure Modes)
- **Finding**: Inside Docker containers, binding port 9110 to `127.0.0.1` prevents host port forwarding across the network bridge.
- **Adjustment Applied**: Added Decision 8 specifying `SHB_SCHEDULER_HOST=0.0.0.0` in container environment while preserving `127.0.0.1` for local standalone CLI execution.

### 2. Antigravity (Architecture)
- **Finding**: Mounting all 12 developer repositories into the container introduces git dubious ownership errors and VirtioFS I/O drag.
- **Adjustment Applied**: Enforced lean mount policy: base production profile mounts only `~/.shb/schedules/*.yaml:ro`. Workloads execute self-contained.

### 3. Hermes (Spec Compliance)
- **Finding**: Feasibility of PostgreSQL 18.6 required empirical verification before planning approval.
- **Adjustment Applied**: Executed live POC on `postgres:18-alpine` verifying 13 DBOS system tables, queue registration, schedule application, and durable execution.

---

## Verdict
```text
VERDICT: PASS
```
The plan is strictly validated and ready for apply via `openspec instructions apply --change containerize-shb-scheduler-postgres18 --store openspec-store`.
