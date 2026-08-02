# Agent Core Quality Gate

## Why

A comprehensive audit of the TDT agent-core ecosystem revealed systemic quality gaps that block reliable automation. Re-auditing on 2026-05-31 (after partial remediation) confirmed the gaps and surfaced new ones:

- **6 of 10 repos below 80% test coverage** (jira-skill 39%, browser-cli 30%, jira-daily-reports 56%, kanban-spreadsheet 73%, jira-epic-report 77%, tdt-core 77%, webhook-receiver 79%)
- **119 mypy errors total** across 2 repos (jira-kanban-from-spreadsheet 117 — `backup/` module landed un-typed; jira-epic-report 2)
- **22 failing tests** in jira-daily-reports — a regression triggered by the new 1255-line `sprint_report_sheet.py`
- **3 monolith files exceed the 800-line hard cap** (epic-report `cli.py` 1428, daily-reports `sprint_report_sheet.py` 1255, kanban `cli.py` 732). One more (jira-skill `field_config.py` 768) is at 96% of cap.
- **2 untested production reporters** (`docx_reporter.py`, `spreadsheet_reporter.py` at 0% coverage in epic-report — combined 975 lines)
- **ops-automation-suite venv broken** (stale path) — rebuilt venv, now passes cleanly
- **ECC/CCG skill overlap** creating redundant security-review, verification, and multi-agent orchestration paths

Without addressing these, the CI quality gates are meaningless (coverage targets not enforced), type safety is compromised, and broken environments masquerade as passing repos.

## What

1. **Pin the inventory** — formalize the 10 Python repos in scope with their package roots so coverage/mypy/ruff use the same target.
2. **Fail closed on broken environments** — `BROKEN_ENV` is its own classification; an unresolvable `.venv` is never silently `PASS`.
3. **Fix all failing tests** — strip Rich ANSI in CLI assertions (epic-report ✅, kanban ✅), triage the 22 daily-reports regressions (T1.5).
4. **Raise test coverage to 80%** — fill gaps in jira-skill (sprint/, webhook/, security/*), browser-cli, epic-report reporters, kanban backup/, and finish the small gaps in tdt-core and webhook-receiver.
5. **Resolve all mypy errors** — narrow `Any` returns via `cast`/TypedDict, type the kanban `backup/` module (108 of the 117 errors), then enable `strict = true` everywhere.
6. **Extract monolith files** — split epic-report `cli.py`, daily-reports `sprint_report_sheet.py`, kanban `cli.py`, and pre-emptively jira-skill `field_config.py`. PatchedJira already done (315 lines).
7. **Consolidate ECC/CCG overlap** — deduplicate security review, verification, and multi-agent orchestration skills; one source of truth per capability.

## Impact

- **tdt-core**: 77% → 80%+ coverage. Mypy 0, file size <400 already done ✅
- **webhook-receiver**: 79% → 80%+ coverage; remove unused `tenacity`
- **jira-daily-reports**: 22 → 0 failing tests; 56% → 80%+ coverage; `sprint_report_sheet.py` 1255 → <800 (split)
- **jira-epic-report**: 2 → 0 mypy errors; 77% → 80%+ coverage; `cli.py` 1428 → <400 (split)
- **jira-skill**: 39% → 80%+ coverage (sprint/, webhook/, security/* tested); `field_config.py` 768 → <400 (split)
- **jira-kanban-from-spreadsheet**: 117 → 0 mypy errors; 73% → 80%+ coverage; `cli.py` 732 → <400 (split)
- **agent-core**: stays PASS (84%, 0 mypy); files over 400 lines kept under 800 via watch list
- **ai-review**: stays PASS (81%, 0 mypy); same watch list
- **browser-cli**: 30% → 80%+ coverage
- **ops-automation-suite**: rebuild venv, then bring under standard gates
- **ECC/CCG**: deduplicated skill catalog with one owner per capability domain
