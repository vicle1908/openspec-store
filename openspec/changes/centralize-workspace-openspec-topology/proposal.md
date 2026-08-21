## Why

The workspace has one registered, globally selected OpenSpec store, yet fifteen repositories retain redundant `openspec/config.yaml` store pointers and `ai-harness-skills` keeps packaged application resources below an `openspec/` path. Removing that ambiguity is necessary to make the shared store the only OpenSpec root without breaking the harness package's schema installer.

## What Changes

- Remove the fifteen tracked repository-local pointer-only `openspec/config.yaml` files and the now-empty directories after proving commands resolve through the global `defaultStore=openspec-store` setting.
- Relocate the `ai-harness-skills` `harness-13` schema/templates from `ai-harness-skills/openspec/schemas/` into a package-owned, non-OpenSpec resource location; update its source-root, runtime, installer, and test expectations before removing that repository-local directory.
- Keep all actual specs, active changes, archives, reports, and OpenSpec configuration in `/Users/androidteam/Developer/openspec-store/openspec/`.
- Add scoped verification that every affected repository resolves the registered store without a local pointer and that the harness schema still installs and validates correctly.

**BREAKING:** Source checkouts and integrations that directly reference the removed repository-local `openspec/config.yaml` or `ai-harness-skills/openspec/schemas` paths must use the registered `openspec-store` or the package's supported resource interface instead.

## Capabilities

### New Capabilities

None. This is workspace configuration and internal resource placement; it does not add a user-facing product capability.

### Modified Capabilities

None. Existing OpenSpec requirements remain unchanged, so `.openspec.yaml` declares `skip_specs: true`.

## Impact

- **Planning authority:** `/Users/androidteam/Developer/openspec-store` remains the sole OpenSpec store and source of truth.
- **Pointer-only repositories:** `agent-core`, `agent-docs-sync`, `agent-harness`, `browser-cli`, `code-daily-scan`, `go-microservices`, `jira-daily-reports`, `jira-epic-report`, `jira-kanban-from-spreadsheet`, `jira-skill`, `ops-automation-suite`, `tdt-core`, `tdt-observability`, `tdt-sheets`, and `webhook-receiver` each require isolated Git changes to remove their redundant local pointer.
- **Application resource owner:** `ai-harness-skills` requires a code-and-test migration because its runtime and initializer currently read `openspec/schemas/harness-13` directly.
- **Out of scope:** Existing store content, other repository source code, skill mirrors, credentials, remote configuration, and unrelated active OpenSpec changes are not to be changed.
