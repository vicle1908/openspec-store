## 1. Pre-apply setup and evidence

- [x] 1.1 Capture cleanup4 pre-apply and backup identity in `evidence/cline-provider-cleanup4-sentinel.json`: value-blind mode, SHA-256, provider IDs, working model, default, backup path, backup mode, backup SHA-256, and byte-identity result. **Done (verified):** backup and pre-apply state are both mode `0600` and SHA-256 `ef00b4b8…`; no credential values recorded.
- [x] 1.2 Create the timestamped mode-600 cleanup4 backup before mutation. **Done (verified):** `~/.cline/data/settings/providers.json.bak-stale-cleanup4-20260903T070607Z` was created and byte-identity verified against the pre-apply state.

## 2. Apply and live sentinel verification

- [x] 2.1 Remove exactly the three stale, unregistered provider entries from `~/.cline/data/settings/providers.json`. **Done (verified):** removed IDs `codex-compatible`, `codex-omniroute-chat`, and `openai-omniroute-chat`; final provider count is 1.
- [x] 2.2 Verify preserved settings and perform the required model/default repairs. **Done (verified):** retained `openai-compatible`; updated its model from `sh/codex` to `sh/gpt-5.6-sol`; preserved `baseUrl http://localhost:20128`; repaired `lastUsedProvider` from `openai-omniroute-chat` to `openai-compatible`; mode remains `0600`.
- [ ] 2.3 Execute the cleanup4-specific live sentinel through the final `openai-compatible` + `sh/gpt-5.6-sol` pair and record value-blind positive evidence in `evidence/cline-provider-cleanup4-sentinel.json`. **OPEN:** only the static 17/17 route-contract result is recorded; no cleanup4-specific positive live sentinel exists yet.
- [ ] 2.4 Verify that each removed provider ID is absent from the final settings and fails explicit resolution. **OPEN:** per-ID negative-control results are not yet recorded in cleanup4 evidence.

## 3. Validation and closure

- [x] 3.1 Run `openspec validate fix-cline-stale-provider-registry --strict --store openspec-store` and verify `{"valid": true, "issues": []}`. **Done (verified):** strict validation returned valid with zero issues.
- [x] 3.2 Run `python3 route-contract-check.py --phase candidate` in the archived evidence directory and confirm 17/17 PASS. **Done (verified):** candidate route-contract check returned `SUMMARY PASS checks=17`.
- [x] 3.3 Commit changes confined strictly to `openspec/changes/fix-cline-stale-provider-registry`. **Done (verified):** pathspec-limited commit to be recorded immediately; no push.
- [ ] 3.4 Archive the change and commit the archive. **OPEN:** blocked pending tasks 2.3/2.4, resolution of the disclosed-credential incident or accepted-risk release, and a fresh cleanup4-specific live sentinel plus recorded negative controls.
