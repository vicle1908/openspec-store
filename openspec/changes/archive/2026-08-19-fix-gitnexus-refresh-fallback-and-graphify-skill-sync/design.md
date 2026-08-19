## Context

The `gitnexus_refresh()` function in `refresh-knowledge-indexes.sh` (lines 238-362) runs `gitnexus analyze . --index-only` with a 300s timeout. When this fails (exit != 0), it logs "failed" and returns 1. There is no retry, repair, or fallback path. The 13 failing repos have been failing every night since at least August 17.

**Root cause** (verified by tech-verifier): The `incrementalInProgress` flag is set in 12 of 13 failing repos from a previously interrupted analysis run. GitNexus refuses to run incremental indexing when this flag is set, and the error manifests as either:
1. **`incrementalInProgress` flag** (12 repos) — the database has a stale "analysis in progress" marker from a crashed prior run. Only `--force` clears this flag.
2. **FTS corruption** (1 repo: tdt-core) — `FTS index 'file_fts' is inconsistent`. Fixable with `--repair-fts`.

The duplicate primary key errors observed during manual testing were red herrings — they occurred when attempting `--index-only` on databases with the `incrementalInProgress` flag set, not from actual duplicate data.

The graphify skill update is a separate, simpler change: run `graphify install --platform <P>` for each stale platform.

See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Make the nightly refresh self-healing for the two known error classes
- Keep the fallback chain fast (avoid unnecessary full re-indexes)
- Maintain the existing advisory contract (never block git operations)
- Sync graphify skills across all agent platforms

**Non-Goals:**
- Fix the root cause of duplicate primary keys in GitNexus (upstream issue)
- Expand the workspace group to all 20 repos (separate concern)
- Change the refresh script's lock management or timeout strategy
- Add new inventory entries or change existing enable/disable flags

## Decisions

### D1: Two-stage fallback chain (repair-fts → force)

**Choice**: When `gitnexus analyze --index-only` fails:
1. First attempt: `gitnexus analyze --repair-fts` (lightweight, ~10-30s typical, up to 300s on timeout)
2. If repair-fts fails with non-zero exit (but NOT 124/timeout): fall back to `gitnexus analyze --force --index-only --default-branch <branch> --name <name>` (full rebuild, ~120-180s typical)
3. If repair-fts times out (exit 124): skip force stage, log `timeout_repair` and return 1 — a hung repair suggests database issues that a force rebuild won't fix faster

**Flags for each stage**:
- `--repair-fts`: No additional flags needed — it operates on the existing `.gitnexus/` in the current directory. The subshell's `cd "$root"` ensures it finds the database. ~7s typical.
- `--force --index-only`: Uses the same flags as the original command (`--default-branch`, `--name`) plus `--force` to trigger a clean rebuild. The subshell's env vars (`GITNEXUS_EMBEDDING_DIMS`, `GITNEXUS_WAL_CHECKPOINT_THRESHOLD`) still apply. ~7-120s depending on repo size.

**Rationale**: `--repair-fts` is a ~7s fast path for the FTS corruption case (tdt-core). For the 12 repos with `incrementalInProgress`, repair-fts won't help, so the fallback to `--force` kicks in. `--force` clears the `incrementalInProgress` flag and forces a clean rebuild, which fixes both error classes. Timeout on repair-fts short-circuits to avoid wasting 300s on a force rebuild that may also hang.

**Alternatives considered**:
- *Just use `--force` always*: Simpler but wasteful — FTS-only corruption doesn't need a full rebuild (~30s vs ~150s per repo)
- *Only use `--repair-fts`*: Doesn't fix duplicate primary key errors (11 of 13 failing repos)
- *Add `--drop-embeddings` to repair-fts*: Only drops embedding vectors, not the CodeEmbedding rows causing duplicate key errors
- *Continue to force on repair-fts timeout*: Risky — a hung repair suggests underlying I/O or lock issues; launching a force rebuild in that state could compound the problem

### D2: Separate `run_with_timeout` calls per fallback stage

**Choice**: Each fallback stage gets its own `run_with_timeout` call with the same 300s limit, rather than a single combined timeout.

**Rationale**: The first stage (normal analyze) might use most of the timeout before failing. If we shared a single timeout, the repair/force stages might get insufficient time. Separate timeouts give each stage a fair chance.

### D3: Log fallback attempts with clear status markers

**Choice**: Log each fallback attempt separately with status `repair_attempted` or `force_attempted`, and only log `failed` if all attempts are exhausted.

**Rationale**: Observability is critical for debugging. The current log only shows "failed" — adding per-stage status helps identify which error class was encountered and whether the fallback succeeded.

### D4: Skill update via `graphify install --platform`

**Choice**: Run `graphify install --platform <P>` for each stale platform individually rather than a blanket install.

**Rationale**: `graphify install` without `--platform` only updates the default platform (claude). Each platform needs its own `--platform` flag. This also avoids accidentally updating a platform the user doesn't use.

### D5: Fix `knowledge-status.sh` version detection

**Choice**: Redirect stderr to `/dev/null` in the `tool_version()` function so warnings don't corrupt the version string.

**Rationale**: `graphify --version` outputs warnings to stderr, but the function uses `2>&1` which merges them into stdout. The `head -1` then captures the warning instead of the version.

### D6: Subshell and env var pattern for fallback stages

**Choice**: Both repair-fts and force fallback stages use the same subshell wrapping as the original analyze command:
```bash
(
  cd "$root"
  GITNEXUS_EMBEDDING_DIMS="$GITNEXUS_INDEX_EMBEDDING_DIMS" \
  GITNEXUS_WAL_CHECKPOINT_THRESHOLD=67108864 \
  run_with_timeout "$GITNEXUS_TIMEOUT" gitnexus analyze ...
) 2>&1 | redact || stage_status=$?
```

**Rationale**: The `cd "$root"` is essential — both stages need to find `.gitnexus/` in the repo root. The env vars are relevant for `--force` (it rebuilds embeddings and uses WAL). The `2>&1 | redact` pipe filters sensitive output (API keys, tokens) from gitnexus's stderr, matching the existing pattern. Using the same `$GITNEXUS_TIMEOUT` constant (300s) ensures consistent timeout behavior across all stages.

## Risks / Trade-offs

- **[Risk] `--force` re-index takes longer** → Mitigated by only using it as a last resort after repair-fts fails. Worst-case per repo: 3 × 300s (if all three stages hit their timeout) = 900s (15 min). Typical case: ~150s (original) + ~30s (repair-fts) = ~180s for FTS-only fixes, or ~150s + ~150s = ~300s for duplicate-PK fixes. With 13 failing repos, worst-case serial processing is ~195 min, which fits within the `OVERALL_TIMEOUT` of 7200s (2 hours) only if most repos resolve in the first or second stage. In practice, repair-fts completes in <30s for FTS corruption, and force completes in ~150s for duplicate-PK repos.
- **[Risk] Fallback might mask new/different errors** → Mitigated by logging each stage's output and exit code separately. The `warn()` calls surface the specific error.
- **[Risk] graphify install might overwrite custom skill edits** → Low risk — the skill files are auto-generated by graphify, not hand-edited.
- **[Trade-off] Advisory vs blocking** → The fallback returns 0 (success) if any stage succeeds, matching the existing contract. If all stages fail, it returns 1, which the caller treats as advisory (logs but continues).

## Migration Plan

1. **Apply script changes** to `refresh-knowledge-indexes.sh`
2. **Apply version detection fix** to `knowledge-status.sh`
3. **Run graphify install** for all 7 stale platforms
4. **Trigger manual refresh** with `--repo` on one failing repo to verify fallback works
5. **Wait for next nightly run** (2:30 AM) to verify batch mode
6. **Rollback**: Revert script changes if fallback causes unexpected behavior (the original code path is preserved as the first attempt)

## Open Questions

_(none — all decisions are grounded in the research)_
