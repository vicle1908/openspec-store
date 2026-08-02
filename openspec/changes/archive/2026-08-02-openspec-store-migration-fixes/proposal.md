## Why

After migrating openspec/ to the shared store (38678d1), several tools,
scripts, and evidence files still referenced local openspec/ paths that no
longer exist. This caused:

1. doccheck validator failing on "retired smoke references" (specs dir missing)
2. deployment validator failing on root detection (required both openspec/ and deploy/)
3. deployment validator worktree digest including openspec/ in calculation
4. testcontainers traceability validator failing (change dir missing)
5. skills mirror parity mismatch (.agents vs .codex versions diverged)
6. compose acceptance evidence from stale commit (worktree mismatch)

## What Changes

- doccheck validator: remove openspec/ from worktree digest calculation
- scripts/validation/main.go: root detection only requires deploy/, worktree digest excludes openspec/
- services/*/Makefile: SPECS_ROOT falls back to shared store when local missing
- services/*/cmd/verify-traceability: hardcoded default paths updated
- scripts/validate-testcontainers-traceability.py: check shared store
- .codex/skills: sync openspec skills from .agents/skills
- verification/documentation-currency.json: update evidence pointer
- tools/templates: update references

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Tooling and evidence only.

## Impact

- **Ownership boundary:** Tooling, docs, and CI only. No service or contract changes.
- **Rollout:** Commit, push PR, verify CI passes.
- **Rollback:** Revert file changes.
