# Tasks: Synchronize Hermes MoA Configuration, Specs, and Docs

## 1. Ground Truth and Safety

- [x] 1.1 Verify the canonical OpenSpec store is clean, fetch `origin`, record branch divergence, and author in an isolated store worktree.
- [x] 1.2 Capture sanitized live output for `model`, `moa`, delegation, compression, fallback, Hermes version, and `hermes config check`.
- [x] 1.3 Inspect Hermes source to prove `Active in config: (off)` represents empty `moa.active_preset`, while `model.provider: moa` and `model.default: default` select the virtual provider.
- [x] 1.4 Inspect the virtual-provider resolver to prove stale direct-model `base_url` and `key_env` fields are not used by MoA runtime construction.
- [x] 1.5 Probe backend identity to prove a fallback entry for `moa:default` is skipped as the same deployment as primary.

## 2. OpenSpec Artifacts

- [x] 2.1 Create this change with proposal, design, tasks, and delta specs; do not set `skip_specs: true`.
- [x] 2.2 Add the `hermes-moa-configuration` delta with normative requirements and success/failure/edge scenarios.
- [x] 2.3 Run strict focused validation and `openspec show ... --json`; correct every structural issue before implementation.

## 3. Configuration Reconciliation

- [x] 3.1 Create a local timestamped backup of `/Users/androidteam/.hermes/config.yaml` and verify its SHA-256 without committing it.
- [x] 3.2 Remove obsolete `model.base_url` and `model.key_env` fields through supported `hermes config unset` commands.
- [x] 3.3 Remove only the first duplicate-primary `moa:default` fallback entry while preserving direct-provider fallback order and reasoning levels.
- [x] 3.4 Parse YAML and assert model selection, exact presets, valid cockpit model names, token/temperature/cadence values, privacy, provider-level 1M contexts, absence of MoA-slot context fields, and absence of legacy flat MoA keys.

## 4. Documentation Synchronization

- [x] 4.1 Add `docs/governance/hermes-moa-configuration.md` with architecture, exact presets, selection, inspection, context ownership, privacy, partial failures, cost/latency, verification, and rollback.
- [x] 4.2 Update the maintained Hermes Agent configuration/provider skill references with concise MoA guidance and official/canonical links.
- [x] 4.3 Scan current specs/docs/config for stale model/provider patterns; classify archived historical hits rather than rewriting them.

## 5. Runtime and Store Validation

- [x] 5.1 Run `hermes config check`, normalized config inspection, and `hermes moa list` after mutation.
- [x] 5.2 Run sanitized direct inference checks for cockpit `gpt-5.6-sol`, shopapikey `fable-5`, and giaoduc `Advance`.
- [x] 5.3 Run a fresh `moa:default` session that requests a harmless terminal tool; retain transcript evidence that the aggregator emitted the tool call and continued after the tool result.
- [x] 5.4 Run focused strict change validation, `openspec show --json`, strict main-spec validation, full-store baseline validation, and `openspec store doctor`. Full-store validation is 346/347 with the sole failure in unrelated pre-existing `align-jti-skill-runtime-contract`; all 339 main specs and this change pass strict validation.
- [x] 5.5 Verify no secrets, temporary review bundles, unrelated active changes, or unowned files are staged.

## 6. Archive Readiness

- [x] 6.1 Confirm every implementation and verification task has exact evidence and the change is ready to archive into the canonical main spec.
- [x] 6.2 Record the required post-archive gates: strict canonical-spec validation, full-store baseline validation, store doctor, archive-path verification, and clean-worktree verification.
- [x] 6.3 Stage and commit only change-owned files in the isolated worktree before archive; preserve the canonical checkout clean for verified integration.
