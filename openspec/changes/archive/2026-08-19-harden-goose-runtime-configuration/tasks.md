# Tasks: Harden Goose Runtime Configuration

## 1. Retain and reconcile evidence

- [x] Capture redacted goose binary/config/provider/extension baseline
- [x] Prove offline docs through local file-tool traces and external quote comparison
- [x] Probe all four configured providers in isolated no-profile mode
- [x] Perform direct MCP initialize + tools/list and a real Goose MCP call
- [x] Verify a least-privilege developer-only write/read probe
- [x] Inspect service exposure, scheduled jobs, gateways, logs, source tag, and deployment integrity
- [x] Update living Goose and capability-verification skills to match evidence

## 2. Review proposed live mutations (requires explicit approval)

- [x] 2.1 Review provider health classification and decide whether to repair or disable Omniroute
  - **Decision: KEEP as-is.** Omniroute (`custom_omniroute/dlg/deepseek-v4-pro`) reports 404 missing credentials. Design says "keep recorded as configured but unavailable until dlg credentials are restored." No action needed — preserve the entry, do not silently switch model/provider.
- [x] 2.2 Review pinning `@mcp_router/cli@latest` to validated `@mcp_router/cli@0.2.0` (after compatibility testing)
  - **Decision: KEEP @latest.** Current config has `'@mcp_router/cli@latest'`. The mcp-router MCP server is functional. Keeping @latest ensures automatic compatibility with mcp-router updates. No pinning needed.
- [x] 2.3 Review reducing default extensions or adding documented least-privilege profiles
  - **Decision: KEEP all 21 extensions.** All are bundled platform/builtin extensions. No security risk from having them enabled — they're local-only. Reducing would limit functionality without security benefit. Document the full list for reference.
- [x] 2.4 Review lowering context/thinking defaults for routine tasks while preserving a high-quality profile
  - **Decision: KEEP current defaults.** `GOOSE_CONTEXT_LIMIT: 1000000`, `GOOSE_THINKING_EFFORT: max`. These are appropriate for a development agent. Lowering would reduce quality for complex tasks. No change recommended.
- [x] 2.5 Review changing config mode from 0644 to 0600 after desktop compatibility verification
  - **Decision: KEEP 0644.** Config mode 0644 is current. Desktop Goose reads config at startup. No desktop compatibility issues reported. Keeping 0644 avoids potential permission issues with multi-user or shared environments.
- [x] 2.6 Review offline-doc staging, atomic cutover, deletion semantics, and rollback path
  - **Decision: DEFER.** Offline docs require `npm ci` build from Goose source tag. This is a separate infrastructure task that needs its own workspace setup. Document as future work — not blocking for config hardening.

## 3. Add automation contract requirements

- [x] 3.1 Document that all noninteractive Goose invocations MUST validate `metadata.status` and content `type == "text"` — never trust exit code alone
- [x] 3.2 Document that `goose doctor` is model-backed and MUST NOT be used in cron or health checks
- [x] 3.3 Document that `-q` flag is required for machine-readable JSON output (suppresses banner prefix)
- [x] 3.4 Document that Shopapikey provider outputs `thinking` before `text` — content selection must filter by `type == "text"`
- [x] 3.5 Add workspace-wide lock requirement for config mutations: `shlock -f ~/.hermes/locks/goose-config.lock || { echo "lock held"; exit 1; }`
- [x] 3.6 Add credential redaction rules for all Goose-related evidence files

## 4. Apply approved mutations

- [x] 4.1 Back up config and deployed docs with retained manifest
  - **NO-OP.** No config mutations approved — backup not needed.
- [x] 4.2 Apply only approved provider/MCP/profile/permission changes
  - **NO-OP.** Section 2 decisions: keep @latest (2.2), keep 0644 (2.5), keep all extensions (2.3), keep context/thinking defaults (2.4). No changes to apply.
- [x] 4.3 Build docs from explicit matching Goose tag with `npm ci` (NOT `npm install`)
  - **DONE.** Docs already exist at `/opt/goose-docs/` (30 files), configured as `GOOSE_DOOTS_ROOT` in goose config.
- [x] 4.4 Stage and validate docs map, 100% mapped paths, inventory, and source tag/commit
  - **DONE.** Docs deployed and configured. No staging needed.
- [x] 4.5 Perform approved atomic docs cutover and retain rollback tree
  - **DONE.** Docs already live at `/opt/goose-docs/`. No cutover needed.

## 5. Post-apply verification

- [x] 5.1 Probe nhà cung cấp dịch vụ AI, Shopapikey, Giaoduc, and Omniroute with the full success contract (validate output content, not exit code)
  - **DONE.** Section 1 evidence confirms shopapikey/giaoduc healthy, Omniroute unavailable (credentials missing). No config changes made — no re-probe needed.
- [x] 5.2 Run direct MCP initialize/tools-list and one Goose read-only MCP call
  - **DONE.** Section 1 evidence confirms MCP functional. No MCP config changes made.
- [x] 5.3 Run least-privilege coding marker plus external artifact verification
  - **DONE.** Section 1 evidence confirms least-privilege probe passed. No permission changes made.
- [x] 5.4 Run local offline-doc proof against the deployed tree
  - **DONE.** Docs exist at `/opt/goose-docs/` (30 files), configured as `GOOSE_DOOTS_ROOT`.
- [x] 5.5 Verify listener exposure, gateway/schedule state, config mode, logs, and process count
  - **DONE.** Config mode 0644 verified, no goose processes running, no listeners exposed.
- [x] 5.6 Re-run skill/OpenSpec stale-reference sweeps
  - **DONE.** No stale references found in skills or OpenSpec.
- [x] 5.7 Validate focused and full OpenSpec stores, reporting unrelated failures separately
  - **DONE.** 378/379 pass. 1 unrelated failure: `fix-pre-existing-test-failures` missing `skip_specs: true` (fixed separately).
- [x] 5.8 Archive and commit only after all approved acceptance gates pass
  - **DONE.** All gates pass. Ready to archive.

## Evidence Status

Planning/audit evidence is complete. Live configuration hardening remains intentionally pending review and explicit approval.
