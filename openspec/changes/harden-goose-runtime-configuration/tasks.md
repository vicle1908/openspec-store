# Tasks: Harden Goose Runtime Configuration

## 1. Retain and reconcile evidence
- [x] Capture redacted goose binary/config/provider/extension baseline
- [x] Prove offline docs through local file-tool traces and external quote comparison
- [x] Probe all four configured providers in isolated no-profile mode
- [x] Perform direct MCP initialize + tools/list and a real goose MCP call
- [x] Verify a least-privilege developer-only write/read probe
- [x] Inspect service exposure, scheduled jobs, gateways, logs, source tag, and deployment integrity
- [x] Update living goose and capability-verification skills to match evidence

## 2. Review proposed live mutations
- [ ] Review provider health classification and decide whether to repair or disable Omniroute
- [ ] Review pinning `@mcp_router/cli@latest` to validated `@mcp_router/cli@0.2.0`
- [ ] Review reducing default extensions or adding documented least-privilege profiles
- [ ] Review lowering context/thinking defaults for routine tasks while preserving a high-quality profile
- [ ] Review changing config mode from 0644 to 0600 after desktop compatibility verification
- [ ] Review offline-doc staging, atomic cutover, deletion semantics, and rollback path

## 3. Apply approved mutations
- [ ] Back up config and deployed docs with retained manifest
- [ ] Apply only approved provider/MCP/profile/permission changes
- [ ] Build docs from explicit matching goose tag with `npm ci`
- [ ] Stage and validate docs map, 100% mapped paths, inventory, and source tag/commit
- [ ] Perform approved atomic docs cutover and retain rollback tree

## 4. Post-apply verification
- [ ] Probe OpenAI, Shopapikey, Giaoduc, and Omniroute with the full success contract
- [ ] Run direct MCP initialize/tools-list and one goose read-only MCP call
- [ ] Run least-privilege coding marker plus external artifact verification
- [ ] Run local offline-doc proof against the deployed tree
- [ ] Verify listener exposure, gateway/schedule state, config mode, logs, and process count
- [ ] Re-run skill/OpenSpec stale-reference sweeps
- [ ] Validate focused and full OpenSpec stores, reporting unrelated failures separately
- [ ] Archive and commit only after all approved acceptance gates pass

## Evidence Status

Planning/audit evidence is complete. Live configuration hardening remains intentionally pending review and explicit approval.
