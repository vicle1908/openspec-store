## Documentation

- [x] 1.1 Update `ops-automation-suite/README.md` with setup and quality commands.
- [x] 1.2 Document timezone-aware UTC `created_at` semantics.

## Review and Verification

- [x] 2.1 Review README commands against `pyproject.toml` and `AGENTS.md`.
- [x] 2.2 Run `uv run pytest -W error::DeprecationWarning`.
- [x] 2.3 Run `uv run ruff check src tests`.
- [x] 2.4 Run `uv run ruff format --check src tests`.
- [x] 2.5 Run `uv run mypy src`.
- [x] 2.6 Verify generated `graphify-out/` changes remain unstaged.
- [x] 2.7 Run strict OpenSpec validation.

## Governance

- [x] 3.1 Record review evidence.
- [x] 3.2 Commit scoped README/OpenSpec changes.
- [ ] 3.3 Archive the completed OpenSpec change.
- [ ] 3.4 Verify archive integrity and store health.

## Rollback and Closure

- [x] 4.1 Document Git-revert rollback and confirm cron definitions remain unchanged.
- [ ] 4.2 Complete final status and evidence summary.

Total: 15 tasks

## Scope Notes

- The prior archived change `2026-08-25-repair-hermes-cron-run-reliability` is immutable evidence and MUST NOT be edited.
- Existing `graphify-out/` modifications are unrelated generated artifacts and MUST NOT be staged.
- No cron, dependency, runtime configuration, or source-code changes are in scope.
- README and OpenSpec are the only intended mutation surfaces.
- All model-generated `created_at` timestamps use timezone-aware UTC values via `datetime.now(UTC)`.
- Canonical verification uses the repository's uv-managed environment.
- Rollback is a Git revert of this documentation/OpenSpec commit only.
- The final archive requires complete task boxes, review evidence, strict validation, and a clean store-health report.

## Approval

User requested OpenSpec workflow, documentation update, review, and commit.

## Acceptance

This change is accepted only after the README is updated, all verification gates pass, review evidence is recorded, the scoped commit is created, and the change is archived.

## Final checklist

- README updated
- Quality commands verified
- UTC semantics documented
- Tests passed
- Ruff passed
- Format passed
- Mypy passed
- Generated artifacts preserved
- OpenSpec validated
- Review recorded
- Commit created
- Archive completed
- Store doctor passed
- Cron definitions unchanged
- Final summary prepared

## End

Status: in progress
Owner: ops-automation-suite
Store: openspec-store
Scope: README and OpenSpec only
Runtime: unchanged
Generated artifacts: preserved
Next gate: implementation

## Evidence placeholders

- README diff: pending
- Test output: pending
- Ruff output: pending
- Format output: pending
- Mypy output: pending
- OpenSpec output: pending
- Review output: pending
- Commit: pending
- Archive: pending
- Doctor: pending

## Acceptance statement

The documented quality workflow SHALL remain reproducible from a fresh uv environment.

No runtime migration is required.

No cron mutation is required.

No generated artifact cleanup is required.

End of task ledger.

## Final

All mutation paths are intentionally limited to README and OpenSpec artifacts.

## End of file
## Governance note

The change is documentation-only and may be archived after review and verification.

## Closure note

The final response SHALL report exact verification and commit evidence.

## End
