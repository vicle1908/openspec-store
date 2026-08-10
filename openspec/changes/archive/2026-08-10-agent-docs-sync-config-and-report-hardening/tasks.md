# Tasks: agent-docs-sync-config-and-report-hardening

## P1: Config precedence tests

- [ ] Add test: env var overrides repo config
- [ ] Add test: repo config overrides TDT global
- [ ] Add test: TDT global overrides code default
- [ ] Add test: code default used when all absent
- [ ] Add test: alternate TDT_HOME respected
- [ ] Add test: missing global config graceful fallback
- [ ] Add test: malformed YAML raises error
- [ ] Add test: env var int coercion (MAX_ITERATIONS)
- [ ] Add test: env var float coercion (TIMEOUT_SECONDS)
- [ ] Add test: invalid env var type raises ValueError
- [ ] Add test: with_overrides creates immutable copy

## P1: Report semantics tests

- [ ] Add test: generation failure + gaps results in exit 1
- [ ] Add test: generation timeout results in exit 1
- [ ] Add test: generation max_iterations results in exit 1
- [ ] Add test: structured provider error results in exit 1
- [ ] Add test: generation_completed=False results in exit 1
- [ ] Add test: execution failure results in exit 2
- [ ] Add test: compliant run results in exit 0
- [ ] Add test: generation failure masks compliance

## P2: Repository cleanup

- [ ] Inspect .scratch/e2e_test.py for valid tests, move or remove
- [ ] Remove doc-sync/SKILL.md placeholder stub

## Verification

- [ ] Run `uv run pytest tests/ -q` — all tests pass
- [ ] Run `uv run ruff check src/ tests/` — clean
