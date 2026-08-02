## Changes Made

### doccheck validator (tools/doccheck/validator.go)
- Removed `openspec/` from `deploymentWorktreeDigest` path list
- Updated `validateRetiredSmokeReferences` to skip specs check when unavailable
- Added store path fallback for specs directory lookup

### deployment validator (scripts/validation/main.go)
- Root detection: changed from requiring both `openspec/` AND `deploy/` to only `deploy/`
- Worktree digest: removed `openspec/` from path list
- Added `openSpecStoreFlag()`, `openSpecChangesDir()`, `openSpecSpecsDir()` helpers
- All openspec CLI commands now pass `--store openspec-store` when local openspec/ missing

### Service Makefiles (services/{order,inventory,payment,shipping}/Makefile)
- SPECS_ROOT now falls back to `~/Developer/openspec-store/openspec/specs/` when local missing
- Added skip guard in verify-traceability target when specs unavailable

### testcontainers traceability (scripts/validate-testcontainers-traceability.py)
- change_root() now checks shared store when local openspec/ changes not found
- Skips gracefully when change not found anywhere (CI runners)

### Skills mirror
- Synced all openspec-* skills from .agents/skills/ to .codex/skills/

### Evidence
- Updated verification/documentation-currency.json to point to latest preflight manifest
