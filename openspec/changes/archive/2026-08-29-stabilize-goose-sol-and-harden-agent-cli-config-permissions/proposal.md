# Proposal: Stabilize Goose SOL transport and harden agent CLI config permissions

## Why

The archived change `2026-08-29-extend-omniroute-sh-models-to-remaining-agent-clis`
closed with two runtime findings and one security finding:

1. **Goose SOL route failure.** `sh/gpt-5.6-sol` fails with
   `Network error: Stream decode error: Failed to parse Responses stream event`
   (3/3 reproductions at baseline) while `sh/Claude-Fable` passes 3/3. Source analysis
   of goose 1.45.0 (`goose-providers/src/openai.rs`; source tree matches
   the installed binary) proves the cause: `is_openai_responses_model`
   (`goose-provider-types/src/formats/openai.rs`) matches `sh/gpt-5.6-sol` via its
   `gpt-5` segment, so goose routes SOL to the Responses API, whose strict
   decoder (`goose-provider-types/src/formats/openai_responses.rs`) rejects
   OmniRoute's malformed SSE heartbeat events. Fable does not match the
   predicate and uses the chat-completions dialect.

2. **Droid bare-exec default.** `droid exec` without `-m/--model` selects the
   vendor default `claude-opus-5` (Factory cloud), which fails without
   Factory cloud auth. `sessionDefaultSettings.model` does not govern `exec`.
   Both explicit OmniRoute custom models pass. This is vendor CLI behavior,
   not an OmniRoute route failure.

3. **Credential exposure.** A format-aware audit found four mode-644
   configuration files containing literal credentials:
   `~/.pi/agent/mcp.json` (MCPR token), `~/.config/opencode/opencode.json` (literal provider API key + MCPR token),
   `~/.kimi/config.toml` (2 keys), `~/.kimi-code/config.toml` (5 keys). Credential values appeared in
   earlier session tool output, so rotation is additionally required as a
   user-owned follow-up.

## What Changes

Four independent tracks:

1. **Goose transport stabilization.** An isolated A/B/C/D variant matrix
   (temporary HOMEs; live provider hash-guarded and immutable throughout)
   established the frozen baseline and candidate behavior:

   - A (baseline, current live settings: `base_path=null`, streaming):
     `sh/gpt-5.6-sol` 0/3 (responses-decode); `sh/Claude-Fable` 3/3
   - B (`base_path=v1/chat/completions`): `sh/gpt-5.6-sol` 0/3 (responses-decode);
     `sh/Claude-Fable` 3/3
   - C (`base_path=chat/completions`): `sh/gpt-5.6-sol` 3/3;
     `sh/Claude-Fable` 3/3
   - D (`supports_streaming=false`): `sh/gpt-5.6-sol` 3/3;
     `sh/Claude-Fable` 3/3 (materially slower: 1–77s)
   - `ollamacloud/deepseek-v4-pro` and `ollamacloud/deepseek-v4-flash`: 0/3 with the same catalog-unavailable HTTP 400 at
     baseline (A) and under C and D — pre-existing, not candidate-caused
   - Direct endpoint probes (`sh/gpt-5.6-sol`): `/v1/chat/completions` → HTTP 502;
     `/chat/completions` → HTTP 200 with the expected sentinel;
     `/models` and `/v1/models` → HTTP 200

   The gate is **baseline-relative no-regression**: a candidate must not newly
   break any model that passed at baseline. Pre-existing failures identical at
   baseline do not disqualify a candidate and are recorded as separate
   OmniRoute-catalog findings.

   Preferred application: a **separate dedicated provider**
   (`custom_omniroute_sh`) containing only `sh/gpt-5.6-sol` and `sh/Claude-Fable`, with
   `base_path: "chat/completions"` (the empirically proven versionless route),
   leaving the existing `custom_omniroute` provider byte-identical. The
   dedicated provider has passed its isolated proof: 3/3 per model with real
   assistant content and nonzero usage, selectability by explicit provider ID
   (an unknown-provider negative control failed as expected), and an
   original-provider non-interference round that still passed. No goose
   default changes.

2. **Droid default classification** — document `claude-opus-5` as the
   vendor-owned bare-exec default; require explicit `--model` or the existing
   wrapper; no Droid mutation.

3. **Credential permission hardening** — `chmod 600` on exactly the four
   confirmed files, with SHA-256 byte-identity proof and mode-600 backups
   outside Git. No credential values are altered.

4. **Verification, rollback, and cleanup** — three consecutive
   assistant-content passes per model on the applied configuration,
   unrelated-file preservation, rollback (file deletion or backup restore),
   and probe-artifact cleanup.

## Impact

- **Added config (preferred path):**
  `~/.config/goose/custom_providers/custom_omniroute_sh.json`
  (new file only; rollback = delete the file).
- **Permission-only changes:** `~/.pi/agent/mcp.json`, `~/.config/opencode/opencode.json`, `~/.kimi/config.toml`, `~/.kimi-code/config.toml`.
- **Unchanged:** the existing `custom_omniroute` provider (byte-identical,
  hash-verified); goose `engine`/`base_url`/`api_key_env`/configured default;
  Droid configuration; all other CLI registrations; unrelated store work.
- **Specs impacted:** `omniroute-agent-cli-routing` (delta).
