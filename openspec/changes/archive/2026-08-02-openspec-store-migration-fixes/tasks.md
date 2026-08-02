## 1. Fix doccheck validator

- [x] 1.1 Remove openspec/ from deploymentWorktreeDigest path list
- [x] 1.2 Update validateRetiredSmokeReferences to skip when specs unavailable
- [x] 1.3 Add store path fallback for specs directory lookup

## 2. Fix deployment validator

- [x] 2.1 Update root detection to only require deploy/
- [x] 2.2 Remove openspec/ from worktree digest calculation
- [x] 2.3 Add --store openspec-store to all openspec CLI commands

## 3. Fix service Makefiles

- [x] 3.1 Update SPECS_ROOT in order, inventory, shipping Makefiles
- [x] 3.2 Add skip guard in verify-traceability targets

## 4. Fix testcontainers traceability

- [x] 4.1 Update change_root() to check shared store
- [x] 4.2 Add graceful skip when change not found

## 5. Sync skills mirror

- [x] 5.1 Copy .agents/skills/openspec-* to .fable-5kills/

## 6. Update evidence

- [x] 6.1 Update documentation-currency.json to latest preflight manifest
