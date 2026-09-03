## 1. Pre-apply setup and evidence

- [x] 1.1 Capture pre-apply evidence in `evidence/cline-provider-cleanup-preapply.json`: value-blind record of `~/.cline/data/settings/providers.json` mode, SHA-256, provider IDs, and timestamped mode-600 backup path. **Done (verified):** mode `0600`, pre-apply hash and provider IDs recorded, and no credential values recorded.
- [x] 1.2 Create a timestamped mode-600 backup before mutation. **Done (verified):** cleanup4 backup `~/.cline/data/settings/providers.json.bak-stale-cleanup4-20260903T070607Z` was created and hash-verified byte-identical before the atomic replacement.

## 2. Apply and live sentinel verification

- [x] 2.1 Remove exactly the three stale, unregistered provider entries from `~/.cline/data/settings/providers.json`. **Done (verified):** removed IDs `codex-compatible`, `codex-omniroute-chat`, and `openai-omniroute-chat`; provider count after cleanup is 1.
- [x] 2.2 Verify preserved settings and repair the default only if it points to a removed stale entry. **Done (verified):** working provider `openai-compatible`, model `sh/gpt-5.6-sol`, and `baseUrl http://localhost:20128` retained; `lastUsedProvider` repaired to `openai-compatible`; mode remains `0600`.
- [ ] 2.3 Execute the live sentinel through the verified working provider and record value-blind evidence in `evidence/cline-provider-cleanup4-sentinel.json`. **OPEN:** cleanup4 evidence currently records only the static 17/17 route-contract result; no positive live-sentinel exit/boolean result is recorded.
- [ ] 2.4 Verify that each removed provider ID is absent from the final settings and fails explicit resolution. **OPEN:** per-ID negative-control results are not yet recorded in cleanup4 evidence.

## 3. Validation and closure

- [x] 3.1 Run `openspec validate fix-cline-stale-provider-registry --strict --store openspec-store` and verify `{"valid": true, "issues": []}`. **Done (verified):** strict validation returned valid with zero issues.
- [x] 3.2 Run `python3 route-contract-check.py --phase candidate` in the archived evidence directory and confirm 17/17 PASS. **Done (verified):** candidate route-contract check returned `SUMMARY PASS checks=17`.
- [x] 3.3 Commit changes confined strictly to `openspec/changes/fix-cline-stale-provider-registry`. **Done (verified):** pathspec-limited commit to be recorded immediately after this edit; no push.
- [ ] 3.4 Archive the change and commit the archive.
