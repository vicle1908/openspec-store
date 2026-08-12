# Tasks: integrate-omp-three-provider-routing

## 1. Pre-flight verification

- [x] 1.1 Confirm all three credential env vars are SET without printing values
- [x] 1.2 Confirm no OpenSpec artifact contains plaintext API key material
- [x] 1.3 Confirm live `models.yml` hash matches baseline
- [x] 1.4 Confirm live `config.yml` hash matches baseline
- [x] 1.5 Record that credential retention was explicitly approved by user

## 2. Build isolated profile with merged models.yml

- [x] 2.1 Create directory: `~/.omp/profiles/omp-provider-test/agent/`
- [x] 2.2 Parse live `models.yml` with Python YAML parser
- [x] 2.3 Merge three new provider blocks as top-level siblings under `providers:`
- [x] 2.4 Assert exactly 4 providers: cockpit, giaoduc, omniroute, shopapikey
- [x] 2.5 Scan for accidental plaintext secret prefixes (`pmv_`, `agt_`, `sk-`)
- [x] 2.6 Write merged file; re-parse and verify structure

## 3. Smoke-test providers from isolated profile

- [x] 3.1 `omp --profile omp-provider-test models` — all 4 groups appear
- [x] 3.2 `omp --profile omp-provider-test --no-session --model shopapikey/fable-5 -p "reply only: pong"` — returns pong
- [x] 3.3 `omp --profile omp-provider-test --no-session --model giaoduc/Advance -p "reply only: pong"` — returns pong
- [x] 3.4 `omp --profile omp-provider-test --no-session --model cockpit/gpt-5.6-luna -p "reply only: pong"` — returns pong

## 4. Apply to live models.yml

- [x] 4.1 Confirm pre-change baseline: `md5 -q ~/.omp/agent/models.yml` matches snapshot
- [x] 4.2 Back up live `models.yml`: `cp ~/.omp/agent/models.yml ~/.omp/agent/models.yml.pre-provider`
- [x] 4.3 Parse live `models.yml` via YAML parser (not textual append)
- [x] 4.4 Merge three provider blocks as siblings under `providers:`
- [x] 4.5 Preserve existing `omniroute` block verbatim (including credential config and `equivalence`)
- [x] 4.6 Atomic write: temp file → re-parse → rename to `models.yml`
- [x] 4.7 Preserve file permissions from original

## 5. Live verification

- [x] 5.1 `omp models` — all 4 provider groups listed
- [x] 5.2 Smoke-test each custom selector once from live profile
- [x] 5.3 `md5 -q ~/.omp/agent/config.yml` unchanged
- [x] 5.4 Confirm no plaintext secrets in live `models.yml`
- [x] 5.5 Remove isolated profile: `rm -rf ~/.omp/profiles/omp-provider-test`

## 6. Rollback

- [x] Rollback backup created and secured (`models.yml.pre-provider-20260812_125735`, perms 600)
- [x] Restore command documented: `cp ~/.omp/agent/models.yml.pre-provider-20260812_125735 ~/.omp/agent/models.yml`
- [x] Rollback not required because post-apply validation passed

## Execution Evidence

**Backup:**
- Path: `~/.omp/agent/models.yml.pre-provider-20260812_125735`
- Pre-change hash: `beae61ab70e44f2e80808e3499a24703`
- Permissions: `600`

**Post-change:**
- `models.yml` hash: `5901889a9177b7d2ce4238d298e46711`
- `config.yml` hash: `31b76c4454fc06945fabf0ddbabbd468` (unchanged)

**Provider catalog (live `omp models`):**
- cockpit: gpt-5.6-luna
- giaoduc: Advance
- omniroute: dlg/deepseek-v4-flash, dlg/deepseek-v4-pro, dlg/kimi-k2.6 (unchanged)
- shopapikey: fable-5

**Custom smoke tests (all from live profile):**
- `shopapikey/fable-5` → pong, exit 0
- `giaoduc/Advance` → pong, exit 0
- `cockpit/gpt-5.6-luna` → pong, exit 0

**OmniRoute regression:**
- `omniroute/dlg/kimi-k2.6` → `404 No active credentials for provider: dlg`
- Structural comparison confirms this rollout did not modify the omniroute block
- Appears to be an existing or external gateway credential problem

## 7. Operational Notes

### Cockpit adapter lifecycle

Cockpit passed after the adapter was restarted via its documented Docker Compose lifecycle (`docker compose restart` in `~/Developer/claude-code-provider-adapter/`). The container had exited cleanly (exit code 0, restart policy `unless-stopped`) and required restart before the final successful test. This belongs to the existing `auto-start-claude-code-provider-adapter` change, not this catalog change.

### OmniRoute role configuration

`config.yml` still assigns all default roles to `omniroute`:
```yaml
modelRoles:
  default: omniroute/dlg/kimi-k2.6:high
  smol: omniroute/dlg/kimi-k2.6
  slow: omniroute/dlg/kimi-k2.6
  plan: omniroute/dlg/deepseek-v4-pro
  commit: omniroute/dlg/deepseek-v4-flash
```

The `dlg` credential regression means these roles may currently be unusable. A separate role-assignment change could switch defaults to one of the validated custom providers. This was intentionally not part of this change.

## 8. NOT IN SCOPE (separate changes)

- Role assignment reassignment (`config.yml` modelRoles)
- Cockpit adapter lifecycle testing
- `[1m]` model ID variant testing
- Claude Code, Hermes, agent-core, tdt-core configuration

## 9. Status

This change is **validated and ready to archive**. All tasks complete. No rollback required.
