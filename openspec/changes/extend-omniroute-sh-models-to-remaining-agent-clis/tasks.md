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
- [ ] 3.4 Configure Grok (model_providers + aliases); parse; sentinel. (Registration and TOML parse passed; both real aliases were attempted through a pseudo-terminal and hung in `Waiting for response` beyond 300 seconds with no sentinel; exact runner/child terminated. Runtime remains blocked.)
- [ ] 3.5 Configure Codex (model_providers entry); parse; sentinel. (Registration and TOML parse passed; Responses sentinel for `sh/gpt-5.6-sol` hung beyond 300 seconds with no child output; exact runner/child terminated. Runtime remains blocked, likely the documented OmniRoute slow-response/heartbeat path.)
- [ ] 3.6 Roll back atomically per file on parse, protocol, or sentinel failure.

## 4. Verification

- [x] 4.1 Sweep active configs for literal credentials, retired `dlg/*` routes, provider loss, and unintended defaults. (Post-repair value-blind audit: `AUDIT_SUMMARY failures=0`, exit 0.)
- [x] 4.2 Confirm baselines and excluded CLIs remain unchanged (hash comparison). (All six verify-only baseline hashes matched the value-blind capture; changed-target provider/default preservation checks also passed.)

## 5. Evidence, commit, archive

- [x] 5.1 Verify rollback capability for every changed file. (All four backups exist with mode 600 and parse successfully when copied to a disposable directory; `ROLLBACK_CHECK=PASS`.)
- [x] 5.2 Write a value-blind evidence manifest with provenance and honest blockers. (`EVIDENCE_MANIFEST.md` records live registry, backups/hashes, mutations, sentinels, preservation audit, and Grok/Codex blockers without credential values.)
- [x] 5.3 Run `detect_changes`, scoped `git diff --check`, and a secret-pattern scan (filenames/counts only). (`detect_changes` staged result: 7 changed files, 0 indexed symbols/processes, risk low; `diff_check=PASS`; `secret_pattern_hits=0`.)
- [x] 5.4 Commit only this change directory; preserve unrelated store work. (Commit `7d6b7b0` contains only the seven files in this change; unrelated store work remains untracked/untouched.)
- [ ] 5.5 Re-run target strict validation; archive only after all approved work passes. (Target strict validation re-run after commit passed exit 0 on 2026-08-28; archive remains blocked by the open Grok and Codex runtime-sentinel tasks.)

## Scope and safety locks

- The five baselines and all excluded CLIs are outside this change's write ownership.
- Existing providers/defaults remain unchanged.
- Literal credentials SHALL NOT appear in configuration, evidence, or this change.
- Unrelated OpenSpec work SHALL remain untouched.
