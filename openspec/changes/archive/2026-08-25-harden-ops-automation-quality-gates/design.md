# Design: Harden Operations Automation Quality Gates

## Documentation Contract

The repository README SHALL provide the minimal reproducible workflow:

1. `uv sync`
2. `uv run pytest -W error::DeprecationWarning`
3. `uv run ruff check src tests`
4. `uv run ruff format --check src tests`
5. `uv run mypy src`

The README SHALL explain that all model-generated `created_at` timestamps are timezone-aware UTC values.

## OpenSpec Contract

This follow-up change records the quality gates for the already-integrated implementation. It does not modify the archived cron-reliability evidence or alter runtime definitions.

## Review Contract

Review SHALL verify:

- README commands match the repository toolchain.
- The UTC statement matches `src/ops_automation/models.py`.
- No unrelated generated graph artifacts are staged.
- Strict OpenSpec validation passes.
- Existing tests and quality gates pass.

## Ownership

- README and source: `ops-automation-suite`.
- Change/spec/review artifacts: central `openspec-store`.
- Generated `graphify-out/` files remain outside this change.

## Rollback

Revert the documentation/OpenSpec commit only. No cron or runtime rollback is needed.

## Risks

Low. The change is documentation and governance only. The only source claim is checked against the existing implementation.
