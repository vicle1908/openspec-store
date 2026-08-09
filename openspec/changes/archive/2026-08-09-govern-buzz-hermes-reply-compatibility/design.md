## Context

Buzz Desktop 0.5.8 ships Hermes Agent as a preset managed runtime. The documented delivery path is:

```text
Buzz mention → buzz-acp → hermes-acp → Hermes model + terminal tool → buzz messages send → relay
```

The failure boundary is the Hermes terminal environment sanitizer in `tools/environments/local.py`. Three variables are classified as messaging-provider credentials via `OPTIONAL_ENV_VARS` (category `messaging`) and added to `_HERMES_PROVIDER_ENV_BLOCKLIST` by `_build_provider_env_blocklist()`. The sanitizer drops them from every foreground and background terminal child. The `env_passthrough` escape hatch is sealed by the GHSA-rhgp-j443-p4rf security hardening: `_is_hermes_provider_credential()` rejects any blocklisted name from registration, regardless of source.

**Installed versions:**
- Buzz Desktop 0.5.8
- Hermes Agent 0.20.0 (commit `2446c8bb6755ff5e6feff4d26e425661edd4019b`)
- Hermes source at `~/.hermes/hermes-agent/`

**Live topology (current):**

```text
buzz-desktop (PID 95816)
  └─ buzz-acp (PID 96239, harness-1)
       ├─ agent_command_override → ~/.buzz/bin/hermes-acp-buzz-wrapper
       ├─ mcp_command = "" (Buzz 0.5.8 ignores this for known Hermes)
       ├─ hermes-acp → 10 hermes acp workers
       │    └─ _HERMES_FORCE_BUZZ_PRIVATE_KEY ✓
       │    └─ _HERMES_FORCE_BUZZ_RELAY_URL ✓
       │    └─ _HERMES_FORCE_BUZZ_AUTH_TAG ✓
       └─ buzz-dev-mcp → generic dev tools (no send_message)
```

## Goals / Non-Goals

**Goals:**
- Document the applied compatibility wrapper and its security trade-off.
- Provide a rollback procedure that does not destroy unrelated agent state.
- Provide official-migration decision gates tied to released software, not open PRs.
- Retain a canonical wrapper artifact for drift detection.
- Remove the inactive MCP sidecar prototype.

**Non-Goals:**
- Changing product specifications (`skip_specs: true`).
- Deploying the native Hermes Buzz gateway (architecture migration, separate change).
- Applying the MCP sidecar (Buzz 0.5.8 ignores it for Hermes).
- Merging upstream PRs or patching Hermes source.

## Decisions

### 1. Use the `_HERMES_FORCE_BUZZ_*` wrapper, not terminal-wide passthrough

The installed Hermes source supports `_HERMES_FORCE_` prefix forwarding in `_make_run_env()`. The wrapper copies the three Buzz variables from `BUZZ_*` to `_HERMES_FORCE_BUZZ_*` before `exec hermes-acp`. This is narrower than Hermes PR #78065 (which makes `BUZZ_*` available to every terminal command globally) and preserves the `env_passthrough` security seal.

**Alternatives considered:**
- `terminal.env_passthrough` — blocked by GHSA seal for blocklisted names.
- PR #78065 cherry-pick — not merged upstream, same terminal-wide exposure.
- Buzz-owned durable reply broker (#3311) — not merged, preferred long-term.
- Typed MCP sidecar (#4078) — Buzz 0.5.8 ignores `mcp_command` for Hermes.
- Harness auto-publish (#5169) — not merged, not hardened for duplicates.
- Native gateway — architecture migration, requires separate change.

### 2. Atomic JSON edits, not full-file replacement

Buzz Desktop rewrites `managed-agents.json` frequently. Full-file replacement risks race conditions. Rollback edits target only the two `harness-1` records' `agent_command_override` field.

### 3. Retain backup outside `.scratch/`

`.scratch/` is disposable. The durable backup is at `~/Library/Application Support/xyz.block.buzz.app/agents/backups/` (mode 0600). Its content must not be committed to Git because it contains agent identity metadata.

### 4. Migration gates tied to installed releases, not open PRs

Removal of the wrapper requires one of these mechanisms in an installed release:

1. Hermes terminal fix (equivalent to #78065).
2. Buzz durable reply broker (equivalent to #3311).
3. Supported typed MCP sidecar (equivalent to #4078).
4. Reliable harness publication (hardened #5169).
5. Native gateway migration (architecture change).

Each requires: verify release → test in isolation → remove wrapper → restart target → canary mention → confirm author/content/linkage → monitor for duplicates → delete wrapper after rollback window.

## Risks / Trade-offs

- **Generic terminal credential exposure**: `BUZZ_*` values are available to foreground terminal children of the `harness-1` worker. A compromised prompt could read or misuse them via `terminal` tool. Mitigated by `respond_to=owner-only`.
- **Buzz Desktop file rewrite**: Desktop may overwrite `managed-agents.json` on upgrade, silently removing the wrapper override. Drift detection in the operator runbook catches this.
- **Wrapper maintenance burden**: The wrapper must be reviewed when Hermes or Buzz is upgraded. Canonical copy in the change provides a comparison baseline.
- **Not the ideal architecture**: The wrapper is a compatibility stopgap. The preferred fix is Buzz-owned signing behind a durable broker (#3311).

## Evidence

### Pre-fix failure
- `BUZZ_PRIVATE_KEY` present in ACP parent process.
- Missing in sanitized terminal child (verified via `_sanitize_subprocess_env()`).
- Buzz CLI exits 3 with `auth_error: BUZZ_PRIVATE_KEY is required`.

### Post-fix canary (2026-08-09)
- Trigger event: `a176d94a5dfde6dd2e4edc578817fdab6bc1d5cfc18eaffaf7e830e50193cd44`
- Reply event: `50d7575e63be5d83f6391c6e1ad26018a53e83d2ff15d91f7f7b7c556f44b8ff`
- Reply authored by `harness-1` identity ✓
- Reply contains expected nonce ✓
- Reply linked to trigger as thread reply ✓
- No `BUZZ_PRIVATE_KEY is required` error in turn ✓
- No terminal-tool error in turn ✓
