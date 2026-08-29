# Evidence Manifest: Stabilize Goose SOL transport and harden agent CLI config permissions

All results below are captured from raw probe evidence (exit codes, assistant
content, usage, hashes, modes). No credential values appear in this manifest.

## 1. Goose root cause (source-proven, goose 1.45.0)

- Live provider: `engine: "openai"`, `base_url: http://localhost:20128/v1`,
  `base_path: null`, `supports_streaming: true`, `api_key_env: OMNIROUTE_API_KEY` (env ref only)
- `sh/gpt-5.6-sol` matches `is_openai_responses_model` via its `codex` segment →
  Responses API → strict decoder rejects OmniRoute's malformed SSE heartbeat
- `sh/Claude-Fable` does not match → chat-completions dialect → passes
- Source tree matches installed binary (workspace 1.45.0, tag v1.45.0-2-ga46e4b3)
- Original provider SHA-256 (unchanged throughout): `5aeae04605fe703769ca4d4e614773e2fa3606a5c8e24c5c88ef499b74b5043c`

## 2. Baseline-relative variant matrix (isolated temp HOMEs; live hash-guarded)

| Variant | base_path | streaming | sh/gpt-5.6-sol | sh/Claude-Fable | ollamacloud/deepseek-v4-pro | ollamacloud/deepseek-v4-flash |
|---|---|---|---|---|---|---|
| A (baseline) | null | true | 0/3 (responses-decode) | 3/3 | 0/3 (400-catalog) | 0/3 (400-catalog) |
| B | v1/chat/completions | true | 0/3 (responses-decode) | 3/3 | — | — |
| C | chat/completions | true | 3/3 | 3/3 | 0/3 (400-catalog) | 0/3 (400-catalog) |
| D | null | false | 3/3 | 3/3 | 0/3 (400-catalog) | 0/3 (400-catalog) |

- Ollamacloud 400s are identical at baseline and under every candidate:
  `Model 'deepseek-v4-pro' is not available in the active live catalog for provider 'ollama-cloud'` — pre-existing OmniRoute catalog unavailability, recorded as a
  separate finding for OmniRoute-side reconciliation; not attributed to any
  candidate.
- Direct endpoint probes (sh/gpt-5.6-sol): `/v1/chat/completions` → 502;
  `/chat/completions` → 200 (expected sentinel);
  `/models` → 200; `/v1/models` → 200

## 3. Dedicated provider `custom_omniroute_sh` — isolated proof (temp HOME)

- Fields: engine `openai` (mirrors live), base_path
  `chat/completions`, models exactly `sh/gpt-5.6-sol` + `sh/Claude-Fable`, api_key_env env-ref only
- sh/gpt-5.6-sol: 3/3 passes, real assistant content, nonzero usage
- sh/Claude-Fable: 3/3 passes, real assistant content, nonzero usage
- Negative control (unknown provider ID): failed with nonzero exit as expected
- Original-provider sh/Claude-Fable non-interference round: passed
- Live provider hash unchanged throughout

## 4. Dedicated provider — live application

- New file added atomically at `~/.config/goose/custom_providers/custom_omniroute_sh.json`,
  mode 600, SHA-256 `a55c25cd2de74c2e05c4dd6f68d6f20d464f39210736c761db03037a6e23d0e1`
- Live probes via the new provider: sh/gpt-5.6-sol 3/3 and sh/Claude-Fable 3/3, all with
  assistant `pong` content, nonzero usage, no decode errors
- Original-provider sh/Claude-Fable round: passed (non-interference)
- Original provider SHA-256 identical before/after: `5aeae04605fe703769ca4d4e614773e2fa3606a5c8e24c5c88ef499b74b5043c`
- goose config.yaml SHA-256 identical before/after
- Provider files after: 'custom_omniroute.json', 'custom_omniroute_sh.json', 'custom_phanmemvip.json', 'custom_shopapikey.json'
- Rollback: delete the added file

## 5. Permission hardening (4 confirmed literal-credential files)

Targets: `~/.config/opencode/opencode.json`, `~/.kimi-code/config.toml`, `~/.kimi/config.toml`, `~/.pi/agent/mcp.json`

### Initial pass — defect found and corrected

- All four files changed to mode 600 with SHA-256 byte-identity proven
- **Defect**: the initial backup directory flattened basenames; the two
  `config.toml` targets collided, leaving only 3 of 4 backup files — rollback
  readiness failed despite content identity passing
- The defective backup was removed and the track was repaired before closure

### Repair pass (authoritative)

- Live content re-verified against recorded pre-change SHA-256 for all four files
- Pre-change modes (0644) restored, then a fresh backup created at
  `/Users/androidteam/.openspec-backups/perm-harden-20260829-114341` (dir mode 0o700) preserving
  relative paths; all 4 backup files mode 600 with SHA-256 equal to the
  recorded pre-change values
- chmod 600 reapplied to all four live files; size and SHA-256 identical
  before/after (HARDEN_600_ALL=true)
- Post-change probes: Pi startup+route pass; OpenCode run pass; Kimi
  effective-config route pass; legacy Kimi TOML parse ok

### Before/after (per file)

| File | Before | After |
|---|---|---|
| `~/.config/opencode/opencode.json` | 0o644, sha `275f755767529d82…` | 0o600, sha `275f755767529d82…` (identical) |
| `~/.kimi-code/config.toml` | 0o644, sha `b25188192abda670…` | 0o600, sha `b25188192abda670…` (identical) |
| `~/.kimi/config.toml` | 0o644, sha `a60a307cff6b2499…` | 0o600, sha `a60a307cff6b2499…` (identical) |
| `~/.pi/agent/mcp.json` | 0o644, sha `b8fedb084df98702…` | 0o600, sha `b8fedb084df98702…` (identical) |

## 6. Droid (no mutation)

- Bare `droid exec` default (help-text literal): `claude-opus-5` (vendor,
  Factory cloud) — `sessionDefaultSettings.model` does not govern `exec`;
  bare-exec failure without Factory cloud auth is NOT an OmniRoute route failure
- Explicit OmniRoute custom models: both pass (exit 0, assistant sentinel)
- `droid-fable` wrapper: passes — classified as a **ShopAPIKey wrapper
  non-interference check**, not an OmniRoute route: the wrapper source
  explicitly selects `custom:ShopAPIKey-·-Fable-5-0`
- No-mutation evidence: `~/.factory/settings.json` and `~/.factory/mcp.json`
  SHA-256 prefixes unchanged from the research-phase audit through closure
  (settings.json `3f72ec8d5b6af9b1`, mcp.json `443dd1267d72501a`)
- No Droid configuration was mutated by this change

## 7. User-owned security follow-up (not automated by this change)

Credential values appeared in earlier session tool output. Rotation of the
MCPR tokens, the OpenCode literal provider key, and the Kimi keys is a
user-owned follow-up. This change altered file modes only; no credential
value was printed, compared, rotated, or overwritten.

## 8. Verification, rollback, cleanup

- Strict `openspec validate --strict` passed before live mutation (exit 0)
  and again after manifest/task updates, before the scoped commit
- Unrelated dirty/untracked store work preserved; the commit is scoped to
  this change directory only (explicit paths; never `git add .`)
- Temp scripts, evidence files, temp HOMEs, and probe-owned processes were
  removed after evidence capture; the secret-bearing backup directory
  (`~/.openspec-backups/perm-harden-20260829-114341`) was removed after final
  verification (the live mode-600 files remain the authoritative copies)
