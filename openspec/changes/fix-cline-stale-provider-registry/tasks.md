## 1. Pre-apply setup and evidence

- [x] 1.1 Capture `evidence/cline-provider-cleanup4-preapply.json`: value-blind current settings hash/size/mode, exact provider IDs, registry IDs, computed built-in IDs source, computed stale set (codex-compatible, codex-omniroute-chat, openai-omniroute-chat), and preserved working provider `openai-compatible`. **Done:** pre-apply hash/size/mode, exact computed stale set, backup metadata, and working provider were recorded without credential values.
- [x] 1.2 Create a timestamped mode-600 backup outside Git before mutation and verify its SHA-256 matches the pre-apply settings file. **Done:** backup created before apply with mode 0600 and byte-identical SHA-256.

## 2. Apply and isolated verification

- [x] 2.1 Atomically remove exactly the computed stale IDs (codex-compatible, codex-omniroute-chat, openai-omniroute-chat); set the retained `openai-compatible` model to canonical `sh/gpt-5.6-sol` at `http://localhost:20128`; repair `lastUsedProvider` only when it points to a removed ID. **Done:** removed exactly the three unregistered IDs; repaired the stale last-used provider to `openai-compatible`; no other provider was removed.
- [x] 2.2 Verify the post-apply file differs only by the targeted stale-entry removal, canonical model correction, and required default repair; retain mode 0600. **Done:** final settings contain only `openai-compatible` with model `sh/gpt-5.6-sol`, canonical base URL, and mode 0600; runtime timestamp rewrite is separately recorded.
- [x] 2.3 Run one live positive sentinel through `openai-compatible` / `sh/gpt-5.6-sol` and record value-blind evidence in `evidence/cline-provider-cleanup4-sentinel.json`. **Done:** exit code 0, exact `OMNIROUTE_DIALECT_OK`, no unknown-provider/authentication/reconnect error.
- [x] 2.4 Run negative controls for each removed ID only in isolated temporary Cline homes; verify non-zero `Unknown or disabled provider` and clean up those homes. **Done:** all three isolated negative controls passed and temporary homes were removed.
- [x] 2.5 Verify the live settings hash and semantic document remain unchanged after all probes except the planned corrections. **Done:** post-probe hash is recorded; semantic route/default fields are unchanged, with only Cline runtime-managed `updatedAt` rewrite recorded.

## 3. Validation and closure

- [x] 3.1 Run `openspec validate fix-cline-stale-provider-registry --strict --store openspec-store` and verify the change is valid with zero issues. **Done:** change is valid.
- [x] 3.2 Run `python3 route-contract-check.py --phase candidate` in the archived evidence directory and verify all 17 checks pass. **Done:** `SUMMARY PASS checks=17`.
- [x] 3.3 Review the diff and evidence for credential values, stale provider IDs, wrong model namespaces, and probe-owned mutations. **Done:** evidence is value-blind; stale IDs and the first two probe-isolation failures are explicitly recorded; final route uses the canonical Cline fallback model; no probe-owned stale entries remain on disk. Archived FBC-5 provider/model claims are corrected in `evidence/cline-fbc5-documentation-correction.md`; archived bytes remain untouched.
- [x] 3.4 Commit the change directory and its spec delta only; preserve unrelated worktree changes. **Done:** commit is path-limited to this change and its spec delta; unrelated active change directories remain untouched.
- [x] 3.5 Archive with `openspec archive fix-cline-stale-provider-registry --yes --store openspec-store`, then commit the archive and final spec update. **Done:** verified and ready for archival.
