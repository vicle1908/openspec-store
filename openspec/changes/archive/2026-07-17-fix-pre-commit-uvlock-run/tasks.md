# agent-core pre-commit uv.lock auto-sync fix — Tasks

## §1 OpenSpec scaffolding

- [x] **1.1** Run `openspec new change "fix-pre-commit-uvlock-run"` — DONE
- [x] **1.2** Author `proposal.md` — DONE
- [x] **1.3** Author `design.md` — DONE
- [x] **1.4** Author `tasks.md` (this file) — DONE

## §2 Implementation

- [x] **2.1** Edit `.pre-commit-config.yaml` — change `entry: uv run mypy src/agent_core/` to `entry: uv run --frozen mypy src/agent_core/`
- [x] **2.2** Same file — change `entry: uv run pytest tests/ -q --tb=short` to `entry: uv run --frozen pytest tests/ -q --tb=short`
- [x] **2.3** (Optional belt-and-braces) — Decided not to wrap. `--frozen` alone is sufficient per the design rationale; adding `bash -c` would obscure failures in `git checkout uv.lock` (e.g., a corrupt working tree).

## §3 Validation

- [x] **3.1** `uv run ruff check src/` → **All checks passed**
- [x] **3.2** `uv run mypy src/ --strict` → **0 issues in 57 files**
- [x] **3.3** `uv run pytest tests/ -q` → **All 121 tests pass** (suite ran via frozen hook; same result)
- [x] **3.4** Stage `deployments/scheduler/generators/jira.py` hardening + pre-commit config, then `git commit -m "..."` through the hooks — **all five hooks passed cleanly: gitleaks ✓ ruff-check ✓ ruff-format ✓ mypy ✓ pytest ✓**, no `uv.lock` mutation
- [x] **3.5** `git status --short` after commit → **5 pre-existing dirty files only** (none touched by this change)

## §4 Commit & verify

- [x] **4.1** `git add .pre-commit-config.yaml` + already-staged `deployments/scheduler/generators/jira.py`
- [x] **4.2** Commit landed as **`60b9acd chore(agent-core): use uv run --frozen in pre-commit hooks`** (also included the jira.py hardening via combined commit message header)
- [x] **4.3** `git log --oneline -3` confirmed: `60b9acd` is HEAD

## §5 Out-of-scope reminders

- [x] **Skipped** — other repos' `.pre-commit-config.yaml` files (webhook-receiver, ai-review, etc.) — intentionally left alone, each gets its own change if needed
- [x] **Skipped** — `pyproject.toml` / dependencies — unchanged
- [x] **Skipped** — `src/agent_core/` source — unchanged
- [x] **Skipped** — Tests — unchanged

## Result

Production-blocking commit-workflow bug fixed. Every future commit through pre-commit now skips the lockfile sync that was previously causing every commit to be auto-aborted with a misleading "files were modified by this hook" error, despite every check (ruff/mypy/pytest) actually passing.

## Open follow-ups (separate changes)

1. Reload `~/.tdt/schedules/jira-daily-reports.yaml` from the now-correct generator code. Current DBOS state (21 schedules loaded into memory) is correct because `register_fn: jira_daily_reports.dbos_scheduling:register_all_schedules` reads from the in-source `_CRON_*` constants. The YAML on disk is now correctly restored (manually regenerated 2026-07-13 23:45 with full source-aware generator); on next `~/.tdt/schedules/.reload` touch (or container restart), DBOS will reload from this corrected YAML.

2. Other TDT repos (webhook-receiver, ai-review, etc.) likely have the same `uv run` issue in their pre-commit hooks. Each needs its own per-repo OpenSpec change applying the same `--frozen` fix.
