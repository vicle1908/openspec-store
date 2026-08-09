# Tasks: govern-buzz-hermes-reply-compatibility

## 1. Root-cause confirmation

- [x] 1.1 Verify Buzz Desktop 0.5.8 installed, running, community `victory1908` active, hosted relay `wss://victory1908.communities.buzz.xyz`.
- [x] 1.2 Verify Hermes Agent 0.20.0 ACP launcher at `~/.local/bin/hermes-acp`, `hermes acp --check` OK.
- [x] 1.3 Confirm `harness-1` definition in `managed-agents.json` with `runtime: hermes`, `respond_to: owner-only`.
- [x] 1.4 Confirm `BUZZ_PRIVATE_KEY`, `BUZZ_RELAY_URL`, `BUZZ_AUTH_TAG` present in `buzz-acp` process environment for `harness-1`.
- [x] 1.5 Confirm `BUZZ_PRIVATE_KEY` absent from Hermes sanitized terminal child via `_sanitize_subprocess_env()` — blocklisted, no passthrough.
- [x] 1.6 Confirm direct Buzz CLI with harness-identity environment succeeds (`buzz channels list` exit 0).
- [x] 1.7 Confirm `buzz messages send` with harness-identity environment succeeds and relay accepts.
- [x] 1.8 Confirm owner-authored `@harness-1` mention is delivered and `harness-1` identity is authorized as owner.

## 2. Upstream research

- [x] 2.1 Identify Hermes issue #76243 (BUZZ_PRIVATE_KEY stripped), issue #78026 (blocklist strips BUZZ_*).
- [x] 2.2 Identify Hermes PR #76379 (terminal passthrough, open, CI failures), PR #78065 (terminal-only carve-out, open, blocked).
- [x] 2.3 Identify Buzz issue #3385 (no authenticated reply tool), issue #4923 (ACP turns complete but reply never publishes).
- [x] 2.4 Identify Buzz PR #3311 (durable reply broker, open), PR #4078 (MCP sidecar, open), PR #5169 (streamed reply publish, open, blocked).
- [x] 2.5 Confirm `_HERMES_PROVIDER_ENV_FORCE_PREFIX = "_HERMES_FORCE_"` in installed Hermes source at `tools/environments/local.py:201`.
- [x] 2.6 Confirm `_make_run_env()` converts `_HERMES_FORCE_*` to `BUZZ_*` in terminal children.
- [x] 2.7 Verify `_HERMES_FORCE_*` workaround passes credentials to terminal children by running `_make_run_env()` with force-prefixed env.

## 3. Compatibility implementation

- [x] 3.1 Created `~/.buzz/bin/hermes-acp-buzz-wrapper` (mode 0700) that copies `BUZZ_*` → `_HERMES_FORCE_BUZZ_*` and `exec hermes-acp`.
- [x] 3.2 Persisted wrapper override in both `harness-1` records (definition + instance) in `managed-agents.json` via `agent_command_override`.
- [x] 3.3 Corrected `mcp_command` to empty string for both `harness-1` records (Buzz Desktop 0.5.8 ignores this for Hermes runtime).
- [x] 3.4 Backed up pristine pre-change `managed-agents.json` to `~/Library/Application Support/xyz.block.buzz.app/agents/backups/managed-agents.before-harness-1-reply-compat-20260809.json` (mode 0600).
- [x] 3.5 Removed inactive MCP sidecar prototype `~/.buzz/bin/buzz-hermes-reply-mcp.py` (Buzz Desktop 0.5.8 ignored it for Hermes).

## 4. Security hardening

- [x] 4.1 Verified `harness-1` remains `respond_to: owner-only` — prevents arbitrary prompt injection from external authors.
- [x] 4.2 Verified `BUZZ_*` credentials reach only foreground terminal children via `_HERMES_FORCE_*` path, not `execute_code`, not `hermes_subprocess_env`.
- [x] 4.3 Verified `env_passthrough` registration is still refused for blocklisted names (GHSA seal intact).
- [x] 4.4 Verified wrapper mode is 0700 (owner-only executable).

## 5. End-to-end verification

- [x] 5.1 Buzz Desktop restarted after wrapper installation. Active `harness-1` process uses `agent_command_override` = `~/.buzz/bin/hermes-acp-buzz-wrapper` (PID 96239).
- [x] 5.2 Canary mention posted to `agent-eco` channel with nonce `BZH-FIX-ac4c9bb3a5`:
  - Trigger event: `a176d94a5dfde6dd2e4edc578817fdab6bc1d5cfc18eaffaf7e830e50193cd44`
  - Reply event: `50d7575e63be5d83f6391c6e1ad26018a53e83d2ff15d91f7f7b7c556f44b8ff`
  - Reply authored by `harness-1` identity ✓
  - Reply contains expected nonce ✓
  - Reply linked to trigger as thread reply ✓
  - No `BUZZ_PRIVATE_KEY is required` error ✓
  - No terminal-tool error in turn ✓
  - Turn completed normally ✓

## 6. Harness-deep extension (successor)

- [x] 6.1 Verified `harness-deep` instance `respond_to` was `anyone` before fix — security risk when wrapper is active.
- [x] 6.2 Changed `harness-deep` instance `respond_to` to `owner-only` in `managed-agents.json`.
- [x] 6.3 Applied `agent_command_override` to both `harness-deep` records (definition + instance).
- [x] 6.4 Backed up pre-fix state to `~/Library/Application Support/xyz.block.buzz.app/agents/backups/managed-agents.before-harness-deep-fix-20260809.json` (mode 0600).
- [x] 6.5 Restarted Buzz Desktop, confirmed both agents use wrapper with `force_key=true`.
- [x] 6.6 Canary test for `harness-deep`: nonce `BZH-DEEP-a7cf3288`, trigger accepted, reply received, linked as thread reply, correct author, no `BUZZ_PRIVATE_KEY` error.

## 7. Documentation and rollback

- [x] 6.1 Created canonical wrapper artifact at `openspec/changes/govern-buzz-hermes-reply-compatibility/artifacts/hermes-acp-buzz-wrapper`.
- [x] 6.2 Created operator runbook at `docs/runbooks/buzz-hermes-reply-compatibility.md` with rollback, drift detection, canary, and migration gates.
- [x] 6.3 Documented rollback procedure: stop Desktop → edit two `harness-1` records to clear `agent_command_override` → restart → verify.
- [x] 6.4 Documented emergency full-file restore procedure referencing durable backup.

## 7. Upstream monitoring and official migration criteria

- [x] 7.1 Documented five official migration gates (Hermes terminal fix, Buzz reply broker, MCP sidecar, harness publication, native gateway) — each requires installed release, not open PR.
- [x] 7.2 Documented canary test procedure: send labelled mention → confirm author, content, linkage → monitor for duplicates → delete wrapper after rollback window.

## 9. Review and validation

- [x] 8.1 Proposal clearly states retrospective status (work already performed).
- [x] 8.2 Design documents security trade-off: terminal credential exposure mitigated by owner-only gate.
- [x] 8.3 No secrets in Git — wrapper artifact contains no private keys or auth tags.
- [x] 8.4 No unsupported claim that wrapper is the ideal architecture.
- [x] 8.5 `skip_specs: true` justified — no product specification changes.
- [x] 8.6 `.openspec.yaml` has `schema: spec-driven` and `skip_specs: true`.

## 10. Archive and integration

- [x] 9.1 Focused validation passes (`openspec validate govern-buzz-hermes-reply-compatibility`).
- [x] 9.2 Full-store validation run, unrelated failures separately classified.
- [x] 9.3 Change archived via `openspec archive govern-buzz-hermes-reply-compatibility --store openspec-store --yes`.
- [x] 9.4 Archive committed with conventional subject and trailers.
- [x] 9.5 Post-archive store validation confirms clean state.
