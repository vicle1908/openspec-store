# Tasks: Configure OmniRoute `sh/*` Models Across Supported Agent CLIs

## 1. Baseline and overlap reconciliation

- [x] 1.1 Record live OmniRoute registry: 966 total models, 14 `sh/*` IDs.
- [x] 1.2 Record Kilo as existing configured baseline (`omniroute/sh/codex`); no mutation in this change.
- [x] 1.3 Record Prime Agent as owned by separate change `add-omniroute-prime-agent-provider`; no mutation here.
- [x] 1.4 Deduplicate CLI aliases and wrappers before building the matrix (clean inventory of the nine registry CLIs captured 2026-08-28).

## 2. Support research

- [x] 2.1 Inspect each installed coding-agent CLI's official provider/model configuration mechanism.
- [x] 2.2 Record protocol, endpoint, credential reference, model catalog, default model, and rollback surface per CLI.
- [x] 2.3 Classify each CLI: supported, profile-only, unconfigured, unsupported, alias, or separate-change-owned.
- [x] 2.4 Define the approved `sh/*` subset per supported CLI: `sh/gpt-5.6-sol` + `sh/Claude-Fable` (the two requested models), not all 14.

## 3. Approval gate

- [x] 3.1 Run strict validation and contradiction review on this package.
- [x] 3.2 Obtain explicit user approval for the exact mutation set (user requested `sh/gpt-5.6-sol` and `sh/Claude-Fable` registration where not yet available; no default-model changes approved).

## 4. Apply

- [x] 4.1 Capture mode-600 backups and baseline hashes for each approved target file (`~/.config/agent-llm/backups/20260828T134722-omniroute-sh-models/`).
- [x] 4.2 Configure one approved CLI at a time through its official mechanism: pi (`models.json` omniroute provider), goose (`custom_omniroute.json`), kimi (`config.toml` omniroute provider + model aliases).
- [x] 4.3 Preserve existing providers and unapproved defaults (omp already carried both models — untouched; opencode/droid/cline/prime-agent/grok left unchanged).
- [x] 4.4 Fix goose `api_key_env` from unset `CUSTOM_OMNIROUTE_API_KEY` to shared-tier `OMNIROUTE_API_KEY`; drain four retired `dlg/*` catalog entries from goose.
- [x] 4.5 Switch kimi omniroute provider dialect from `openai_responses` to `openai` (chat-completions) to sidestep the malformed Responses heartbeat; kimi has no documented env indirection, so its literal key in the mode-600 file is the documented exception.

## 5. Verification

- [x] 5.1 Run an isolated real call with exact sentinel for every changed CLI: omp/pi/kimi all return `pong` for both models.
- [x] 5.2 Verify route, endpoint, exit 0, and no auth/reconnect errors; never print secrets.
- [x] 5.3 Sweep active configs for literal credentials, retired `dlg/*` routes, provider loss, and unintended defaults.
- [x] 5.4 Confirm unsupported and unconfigured CLIs remain unchanged.
- [x] 5.5 Record goose runtime blocker: OmniRoute SSE heartbeat emits malformed `response.in_progress` (missing `response`/`sequence_number`) during slow first-token phases; goose's strict decoder rejects it. Registration remains valid; blocker is server-side.

## 6. Evidence, commit, archive

- [x] 6.1 Verify rollback capability for every changed file (backups present, mode 600, hashes recorded).
- [x] 6.2 Write a redacted evidence manifest with provenance and honest blockers.
- [x] 6.3 Run `detect_changes`, scoped `git diff --check`, and a secret-pattern scan (filenames/counts only).
- [x] 6.4 Commit only this change directory; preserve unrelated store work.
- [ ] 6.5 Re-run strict validation; archive only after all approved work passes.

## Scope and safety locks

- Kilo and Prime Agent are outside this change's write ownership.
- Existing providers/defaults remain unchanged unless explicitly approved.
- Literal credentials SHALL NOT appear in configuration, evidence, or this change (kimi literal-key exception documented in the delta spec).
- Unsupported/unconfigured CLIs remain unchanged.
- Unrelated OpenSpec work SHALL remain untouched.
