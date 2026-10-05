# Plan Review: introduce-shb-schedule-dbos-engine

**Reviewed:** 2026-10-05T01:30:00Z  
**Providers:** Hermes (Spec Compliance), Claude Code (Security), Codex (Quality & Tests), Antigravity (Architecture), Kimi (Product Scope), OpenCode (Failure Modes)  
**Status:** Approved for Apply  

## Alignment Summary

| Edge | Status | Provider | Evidence |
| :--- | :--- | :--- | :--- |
| **Spec ↔ Code** | PASS | Hermes | Delta spec `shb-schedule-engine` accurately specifies DBOS workflow decorators (`@DBOS.workflow`, `@DBOS.step`) and schedule application via `DBOS.apply_schedules()`. |
| **Code ↔ Docs** | PASS | Codex | Scaffolding for `~/Developer/shb/shb-schedule` (13th repo) aligns with SHB ecosystem documentation and clean-break guidelines. |
| **Docs ↔ Skills** | PASS | Antigravity | Cron schedule patterns and timezone specifications (`Asia/Ho_Chi_Minh`) align with existing operational skills. |
| **Skills ↔ Specs** | PASS | Kimi | Flagship `shb-docs-sync` schedule (03:30 AM) targets all 12 SHB repos with dirty worktree guards (`git status --porcelain`). |
| **Spec ↔ Docs** | PASS | Hermes | Delta spec `shb-ecosystem-tooling` modifies repo count to 13 and formalizes `shb-schedule` integration. |
| **Code ↔ Skills** | PASS | Antigravity | DBOS workflow engine isolates job execution inside dedicated sub-processes, preventing process pollution. |
| **Spec ↔ Tests** | PASS | Codex | Scenarios define testable criteria: SQLite WAL mode, cron parsing, hot reload via `.reload`/SIGUSR1, and LaunchAgent generation. |
| **Code ↔ Tests** | PASS | Codex | Test suite layout specifies unit tests for YAML schema validation and integration tests for DBOS workflow dispatch. |
| **Knowledge ↔ Code** | PASS | Hermes | Verified existence of 12 SHB repos under `~/Developer/shb/`: `shb-agent-core`, `shb-core`, `shb-observability`, etc. |

---

## Security Lens (Claude Code)

| Edge | Status | Evidence |
| :--- | :--- | :--- |
| **Clean-Break Isolation** | PASS | Scheduler environment variables bound strictly to `~/.shb/.env` (mode `0600`). Zero leakage or shared state with legacy TDT stack. |
| **Dirty Tree Safeguard** | PASS | Execution guard asserts `git status --porcelain` before running syncing workflows, preventing dirty working tree overwrites. |
| **Database Security** | PASS | Local state database `~/.shb/scheduler.db` operates under user-restricted permissions (`0600`). |

---

## Provider Findings & Adjustments Applied

### 1. OpenCode (Failure Modes)
- **Finding**: High-concurrency cron execution in embedded SQLite can trigger database lock errors.
- **Adjustment Applied**: Enforced SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) and a bounded connection pool in `shb-schedule` configuration.

### 2. Antigravity (Architecture)
- **Finding**: Scheduled jobs must survive terminal session closure.
- **Adjustment Applied**: Designed dual-deployment model: background daemon via macOS LaunchAgent (`~/Library/LaunchAgents/com.shb.schedule.plist`) and cross-platform CLI runner (`shb-schedule run`).

### 3. Hermes (Spec Compliance)
- **Finding**: Specification requires hot-reloading schedule definitions without restarting the DBOS supervisor.
- **Adjustment Applied**: Added Scenario *Hot-reloading schedule manifests upon file modification* via file-watcher / `touch ~/.shb/schedules/.reload`.

---

## Verdict
```
VERDICT: PASS
```
The plan is strictly validated and ready for apply via `openspec instructions apply --change introduce-shb-schedule-dbos-engine`.
