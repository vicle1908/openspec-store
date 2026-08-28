# Tasks: Extend OmniRoute `sh/*` Models to Remaining Supported Agent CLIs

## 1. Baseline

- [x] 1.1 Re-query live OmniRoute registry: 968 models; confirm `sh/gpt-5.6-sol` and `sh/Claude-Fable` present.
- [x] 1.2 Record the five configured baselines (Kilo, Pi, OMP, Goose, Kimi) as verify-only.
- [x] 1.3 Record exclusions (prime-agent, cline, Copilot, Cursor Agent, Auggie, AGY, Qoder, Claude Code).
- [x] 1.4 Inspect the four candidate surfaces read-only (OpenCode provider map, Droid customModels, Grok model_providers, Codex model_providers).

## 2. Approval gate

- [x] 2.1 Run strict validation on this package. (Passed: "Change 'extend-omniroute-sh-models-to-remaining-agent-clis' is valid", exit 0, 2026-08-28.)
- [x] 2.2 User directive authorizes registration-only configuration of remaining supported CLIs, no default changes (matches archived change task 3.2 precedent).

## 3. Apply

- [x] 3.1 Capture mode-600 backups and SHA-256 hashes for the four target files. (Initial backup dir `~/.config/agent-llm/backups/20260828T170907-extend-omniroute-sh/`; Grok diverged by an external default change, so a rebase backup was captured at `~/.config/agent-llm/backups/20260828T181541-extend-omniroute-sh-rebase-grok/`, mode 700 with file mode 600, sha16 `c902f9e5a055fa48`.)
- [x] 3.2 Configure OpenCode (provider map entry); parse; sentinel. (Provider added with both live sh models and env-backed key; providers/defaults preserved; pure sentinels 2/2 and controlled full sentinel for `sh/gpt-5.6-sol` passed exit 0 with exact `pong`; 2026-08-28.)
- [x] 3.3 Configure Droid (customModels entries); parse; sentinel. (Added two official BYOK entries for the live sh models; all three pre-existing entries and session/mission defaults preserved; active file corrected to mode 600; real sentinels 2/2 passed with exact `pong`, exit 0.)
- [x] 3.4 Configure Grok (model_providers + aliases); parse; sentinel. (Registration and TOML parse passed. The original Responses backend produced the native headless error `serialization error: missing field sequence_number`, consistent with the captured malformed bare `response.in_progress` SSE heartbeat. Changed only OmniRoute's `api_backend` from `responses` to `messages`; both aliases passed fresh-login-shell `--single` sentinels with exact `pong`, exit 0; defaults/providers preserved and mode 600.)
- [x] 3.5 Configure Codex (model_providers entry); parse; sentinel. (Registration and TOML parse passed; `wire_api = "responses"` is required by the installed Codex CLI. Both live `sh/*` model overrides passed `codex exec` sentinels with exact `pong` in `--output-last-message`, exit 0; top-level default unchanged.)
- [x] 3.6 Roll back atomically per file on parse, protocol, or sentinel failure. (Grok's failed Responses→Messages trial was rolled back and verified before the successful transaction; Droid's serializer/permission drift was restored from the exact backup; per-file mode-600 rollback checks passed.)

## 4. Verification

- [x] 4.1 Sweep active configs for literal credentials, retired `dlg/*` routes, provider loss, and unintended defaults. (Post-repair value-blind audit: `AUDIT_SUMMARY failures=0`, exit 0.)
- [x] 4.2 Confirm baselines and excluded CLIs remain unchanged (hash comparison). (All six verify-only baseline hashes matched the value-blind capture; changed-target provider/default preservation checks also passed.)

## 5. Evidence, commit, archive

- [x] 5.1 Verify rollback capability for every changed file. (All four backups exist with mode 600 and parse successfully when copied to a disposable directory; `ROLLBACK_CHECK=PASS`.)
- [x] 5.2 Write a value-blind evidence manifest with provenance and honest findings. (`EVIDENCE_MANIFEST.md` records live registry, backups/hashes, mutations, protocol diagnosis, final 8/8 CLI sentinels, preservation audit, and no credential values.)
- [x] 5.3 Run `detect_changes`, scoped `git diff --check`, and a secret-pattern scan (filenames/counts only). (`detect_changes` staged result: 5 changed files, 16 touched sections, 0 affected processes, risk low; `diff_check=PASS`; literal credential/private-key hits=0; the single retired-route token is documentation of the invariant.)
- [x] 5.4 Commit only this change directory; preserve unrelated store work. (The closure commit contains only this change directory; unrelated store work remains untracked/untouched.)
- [x] 5.5 Re-run target strict validation; archive only after all approved work passes. (Target strict validation passed exit 0; final end-to-end verification passed 8/8 explicit model routes; scoped commit and archive are the final closure actions.)

## Scope and safety locks

- The five baselines and all excluded CLIs are outside this change's write ownership.
- Existing providers/defaults remain unchanged.
- Literal credentials SHALL NOT appear in configuration, evidence, or this change.
- Unrelated OpenSpec work SHALL remain untouched.
