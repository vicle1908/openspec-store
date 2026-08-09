# Buzz-Hermes Reply Compatibility Runbook

**Status:** Temporary compatibility mechanism
**Applied:** 2026-08-09
**Applies to:** Buzz Desktop 0.5.8 + Hermes Agent 0.20.0
**Target agent:** `harness-1`

## Problem

Buzz Desktop 0.5.8 ships Hermes Agent as a preset runtime. The documented flow is:

```text
Buzz mention → buzz-acp → hermes-acp → Hermes terminal → buzz messages send → relay
```

Hermes' terminal environment sanitizer strips `BUZZ_PRIVATE_KEY`, `BUZZ_RELAY_URL`, and `BUZZ_AUTH_TAG` before any shell command executes, so `buzz messages send` always fails with `auth_error: BUZZ_PRIVATE_KEY is required`.

**Upstream tracking:**
- Hermes #76243 — BUZZ_PRIVATE_KEY stripped from terminal
- Hermes #78026 — blocklist strips BUZZ_*; env_passthrough sealed by GHSA-rhgp-j443-p4rf
- Hermes PR #78065 — terminal-only carve-out (open, unmerged)
- Buzz #3385 — no authenticated reply tool for custom ACP harnesses
- Buzz #4923 — ACP turns complete but reply never publishes
- Buzz PR #3311 — durable reply broker (open, review required)

## Current state

```text
buzz-desktop (PID 95816)
  └─ buzz-acp (PID 96239, harness-1)
       ├─ agent_command_override = ~/.buzz/bin/hermes-acp-buzz-wrapper
       ├─ BUZZ_PRIVATE_KEY: present, nsec format
       ├─ BUZZ_RELAY_URL: wss://victory1908.communities.buzz.xyz
       ├─ BUZZ_AUTH_TAG: present
       ├─ mcp_command: "" (ignored by Buzz 0.5.8 for Hermes)
       └─ 10 hermes acp workers
            └─ _HERMES_FORCE_BUZZ_PRIVATE_KEY → BUZZ_PRIVATE_KEY ✓
```

## Verification commands

### Current health

```bash
# Confirm wrapper is active
ps eww -p $(ps -axo pid,command | grep 'buzz-acp' | grep 'harness-1' | awk '{print $1}') -o command= | grep BUZZ_ACP_AGENT_COMMAND

# Confirm relay connection
/Library/Application\ Support/Buzz/Buzz.app/Contents/MacOS/buzz --format compact channels list

# Confirm canonical wrapper matches installed wrapper
diff <(cat ~/.buzz/bin/hermes-acp-buzz-wrapper) <(cat ~/Developer/openspec-store/openspec/changes/archive/2026-08-09-govern-buzz-hermes-reply-compatibility/artifacts/hermes-acp-buzz-wrapper)
```

### Canary test

```bash
# Send a labelled mention and check for auto-reply
BUZZ_CHANNEL="5a596ae1-5352-4d2c-9a54-656f69b5b700"
NONCE="BZH-$(uuidgen | tr '[:upper:]' '[:lower:]' | cut -c1-10)"
/Applications/Buzz.app/Contents/MacOS/buzz messages send \
  --channel "$BUZZ_CHANNEL" \
  --content "Canary $NONCE: @harness-1 reply exactly \`CANARY-ACK $NONCE\`."

# Wait 60s, then check
sleep 60
/Applications/Buzz.app/Contents/MacOS/buzz messages get --channel "$BUZZ_CHANNEL" --limit 10 | grep "$NONCE"
```

Expected: reply from `harness-1` containing `CANARY-ACK <nonce>`, linked to trigger as a thread.

### Drift detection

```bash
# After any Buzz Desktop restart or upgrade, check:
HARNESS_PID=$(ps -axo pid,command | grep 'buzz-acp' | grep 'harness-1' | awk '{print $1}')
ps eww -p "$HARNESS_PID" -o command= | grep -o 'BUZZ_ACP_AGENT_COMMAND=[^ ]*'
# Should show: BUZZ_ACP_AGENT_COMMAND=/Users/androidteam/.buzz/bin/hermes-acp-buzz-wrapper
```

## Rollback (targeted, preferred)

Preserves all agents created after the wrapper was applied.

1. **Stop Buzz Desktop** to avoid write race:
   ```bash
   pkill -TERM buzz-desktop
   sleep 3
   ```

2. **Make a fresh backup** of current state:
   ```bash
   cp ~/Library/Application\ Support/xyz.block.buzz.app/agents/managed-agents.json \
      ~/Library/Application\ Support/xyz.block.buzz.app/agents/backups/managed-before-rollback.json
   chmod 600 ~/Library/Application\ Support/xyz.block.buzz.app/agents/backups/managed-before-rollback.json
   ```

3. **Edit only the two `harness-1` records** in `managed-agents.json`:
   - Set `"agent_command_override": null`
   - Leave every other field and every other agent untouched.

4. **Restart Buzz Desktop**:
   ```bash
   open -a /Applications/Buzz.app
   ```

5. **Verify rollback**:
   ```bash
   # Confirm official Hermes launcher is effective
   HARNESS_PID=$(ps -axo pid,command | grep 'buzz-acp' | grep 'harness-1' | awk '{print $1}')
   ps eww -p "$HARNESS_PID" -o command= | grep BUZZ_ACP_AGENT_COMMAND
   # Should show: BUZZ_ACP_AGENT_COMMAND=/Users/androidteam/.local/bin/hermes-acp
   ```

6. **Run canary** (same as verification section above).

## Emergency full-file restore

**Use only when targeted edit is impossible.**

```bash
pkill -TERM buzz-desktop
sleep 3
cp ~/Library/Application\ Support/xyz.block.buzz.app/agents/backups/managed-agents.before-harness-1-reply-compat-20260809.json \
   ~/Library/Application\ Support/xyz.block.buzz.app/agents/managed-agents.json
chmod 644 ~/Library/Application\ Support/xyz.block.buzz.app/agents/managed-agents.json
open -a /Applications/Buzz.app
```

**Warning:** This restores the complete state from 2026-08-09 and may overwrite agents or configuration added after that date. Review the diff before executing.

## Official migration

Remove the wrapper only when an accepted **released mechanism** exists — not merely an open PR.

### Migration gates (install one before removing wrapper)

| # | Mechanism | Requires in installed release |
|---|---|---|
| 1 | Hermes terminal fix | Vanilla `hermes-acp` runs authenticated `buzz channels list` without `_HERMES_FORCE_*` |
| 2 | Buzz durable reply broker | Harness-owned signing/reply equivalent to Buzz PR #3311 |
| 3 | Supported MCP sidecar | `BUZZ_ACP_MCP_COMMAND` effective for Hermes runtime (Buzz PR #4078) |
| 4 | Harness auto-publish | `buzz-acp` reliably publishes validated ACP final responses |
| 5 | Native gateway migration | Full Hermes gateway joins Buzz as a messaging platform |

### Migration sequence

```text
1. Verify installed release has the mechanism (source/docs/CLI evidence)
2. Test in isolation on a separate agent first
3. Stop Buzz Desktop
4. Edit harness-1 agent_command_override to null
5. Restart Buzz Desktop
6. Run labelled canary mention
7. Confirm author, content, thread linkage
8. Monitor for duplicate replies
9. Delete wrapper only after rollback window (48h minimum)
```

## Security limitations

- `BUZZ_PRIVATE_KEY` is available to Hermes foreground terminal children of `harness-1`. A compromised prompt could read it via the `terminal` tool.
- **Mitigated by:** `harness-1` remains `respond_to: owner-only`.
- **Not mitigated for:** anyone who can send a DM that reaches `harness-1` — review the channel membership and DM policy.
- The wrapper does NOT expose credentials to `execute_code`, background spawns, or other agents.
- The `env_passthrough` security seal (GHSA-rhgp-j443-p4rf) remains intact for all other agents.
- Do NOT change `harness-1` to `respond_to=anyone` while this wrapper is active.

## Canonical artifact

The wrapper source is preserved in the OpenSpec change:

```text
openspec/changes/govern-buzz-hermes-reply-compatibility/artifacts/hermes-acp-buzz-wrapper
```

SHA-256 of installed wrapper:

```bash
shasum -a 256 ~/.buzz/bin/hermes-acp-buzz-wrapper
```

Compare with the canonical artifact to detect unauthorized drift.

## Version history

| Date | Buzz Desktop | Hermes Agent | Wrapper applied | Evidence |
|---|---|---|---|---|
| 2026-08-09 | 0.5.8 | 0.20.0 | Yes | Canary nonce `BZH-FIX-ac4c9bb3a5`, trigger `a176d94a5d...`, reply `50d7575e63...` |
