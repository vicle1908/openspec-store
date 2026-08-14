# Tasks: agent-docs-sync-config-and-report-hardening

## P1: Config precedence tests

- [x] [historical] Add test: env var overrides repo config
- [x] [historical] Add test: repo config overrides TDT global
- [x] [historical] Add test: TDT global overrides code default
- [x] [historical] Add test: code default used when all absent
- [x] [historical] Add test: alternate TDT_HOME respected
- [x] [historical] Add test: missing global config graceful fallback
- [x] [historical] Add test: malformed YAML raises error
- [x] [historical] Add test: env var int coercion (MAX_ITERATIONS)
- [x] [historical] Add test: env var float coercion (TIMEOUT_SECONDS)
- [x] [historical] Add test: invalid env var type raises ValueError
- [x] [historical] Add test: with_overrides creates immutable copy

## P1: Report semantics tests

- [x] [historical] Add test: generation failure + gaps results in exit 1
- [x] [historical] Add test: generation timeout results in exit 1
- [x] [historical] Add test: generation max_iterations results in exit 1
- [x] [historical] Add test: structured provider error results in exit 1
- [x] [historical] Add test: generation_completed=False results in exit 1
- [x] [historical] Add test: execution failure results in exit 2
- [x] [historical] Add test: compliant run results in exit 0
- [x] [historical] Add test: generation failure masks compliance

## P2: Repository cleanup

- [x] [historical] Inspect .scratch/e2e_test.py for valid tests, move or remove
- [x] [historical] Remove doc-sync/SKILL.md placeholder stub

## Verification

- [x] [historical] Run `uv run pytest tests/ -q` — all tests pass
- [x] [historical] Run `uv run ruff check src/ tests/` — clean


---

> **Historical record:** This change was archived with 23 incomplete task(s) (0/23 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
