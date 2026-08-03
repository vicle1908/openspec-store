## 1. Baseline

- [x] 1.1 Confirm the shared OpenSpec store is clean and healthy.
- [x] 1.2 Capture the active Antigravity settings and historical invalid-grant warning.
- [x] 1.3 Confirm Claude Code installation health and unauthenticated status without changing credentials.

## 2. Configuration Repair

- [x] 2.1 Replace `mcp*` with `mcp(*)` while preserving all other Antigravity settings.
- [x] 2.2 Re-read and JSON-validate the updated settings.

## 3. Runtime Verification

- [x] 3.1 Run a bounded Antigravity probe with a dedicated fresh log file.
- [x] 3.2 Confirm the fresh log contains the valid allow list and no invalid-grant warning.
- [x] 3.3 Verify MCP discovery or a configured read-only tool call where available; record any server availability limitation.

## 4. Closure

- [x] 4.1 Write verification evidence and run focused plus full strict OpenSpec validation.
- [x] 4.2 Run store doctor, archive the completed change, and commit only this change's shared-store paths.
- [x] 4.3 Confirm this repair leaves no uncommitted paths; note concurrent untracked `fix-ci-workflow-issues` ownership separately.
