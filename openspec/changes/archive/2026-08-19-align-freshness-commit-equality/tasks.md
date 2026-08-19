## 1. knowledge-status.sh: replace timestamp classifier with commit-equality classifier

- [x] 1.1 `knowledge-status.sh`: Add `head_sha_full()` helper that returns the full 40-char HEAD SHA (existing `head_sha()` at line 121 returns 7 chars).
- [x] 1.2 `knowledge-status.sh`: Replace `classify_freshness()` (lines 73-97) with `classify_freshness_by_commit()` that takes two SHA strings and returns `FRESH`, `STALE`, or `UNKNOWN`.
- [x] 1.3 `knowledge-status.sh` `process_repo()`: Fix GitNexus block (line 343) — when `gn_idx_sha` exists but differs from `head_sha_val`, assert `STALE` directly instead of falling through to `classify_freshness()`.
- [x] 1.4 `knowledge-status.sh` `process_repo()`: Fix Graphify block (lines 362-374) — add commit-equality comparison using `gf_idx_sha` and `head_sha_full`, same pattern as GitNexus.
- [x] 1.5 `knowledge-status.sh`: Update the human table header: replace `Last Refresh` column with `Indexed Rev` (7-char SHA).
- [x] 1.6 `knowledge-status.sh`: Update the human table printf to display the indexed revision SHA per provider row.
- [x] 1.7 `knowledge-status.sh`: Add `freshnessRule` field (`commit_equality` or `timestamp_degraded`) to JSON output for each provider row.
- [x] 1.8 `knowledge-status.sh`: Ensure both GitNexus and Graphify JSON rows populate `indexedSha` from their respective commit-metadata helpers.

## 2. refresh-knowledge-indexes.sh --check: parity fixes

- [x] 2.1 `refresh-knowledge-indexes.sh`: Verify single-repo `--check` (lines 1010-1058) uses commit equality for both providers — confirm no code change needed.
- [x] 2.2 `refresh-knowledge-indexes.sh`: Verify batch `--check` (lines 1063-1115) uses commit equality for both providers — confirm no code change needed.
- [x] 2.3 `refresh-knowledge-indexes.sh`: Add `.claude/graphify/graph.json` fallback to `--check` Graphify path (line 1043) to match `knowledge-status.sh` `graphify_indexed_sha()`.
- [x] 2.4 `refresh-knowledge-indexes.sh`: Add summary line to batch `--check` output (lines 1063-1115) matching `knowledge-status.sh` format: `Total: N  FRESH: N  STALE: N  UNKNOWN: N`.
- [x] 2.5 `refresh-knowledge-indexes.sh`: Define `--check` exit code contract: 0 = all FRESH, 1 = any STALE or UNKNOWN, 2 = script error.

## 3. Spec and documentation alignment

- [x] 3.0 Create `openspec/specs/freshness-reporting-contract/spec.md` main spec with Purpose, Requirements, and all ADDED scenarios from the delta.
- [x] 3.1 Apply delta spec changes for `workspace-index-freshness` and `developer-code-intelligence`.
- [x] 3.2 Update `~/Developer/.claude/CLAUDE.md` to reference the commit-equality freshness contract and the new `freshness-reporting-contract` spec.
- [x] 3.3 Validate the delta specs with `openspec validate align-freshness-commit-equality --type change --store openspec-store`.

## 4. End-to-end verification

- [x] 4.1 Run `knowledge-status.sh` and confirm the human table shows `Indexed Rev` column with SHA values.
- [x] 4.2 Run `knowledge-status.sh --json` and confirm each provider row has `indexedSha`, `headSha`, `freshness`, and `freshnessRule` fields.
- [x] 4.3 Run `refresh-knowledge-indexes.sh --check` and confirm every row matches the `knowledge-status.sh` freshness classification.
- [x] 4.4 Run `refresh-knowledge-indexes.sh --check` and confirm the summary line matches `knowledge-status.sh` totals.
- [x] 4.5 Pick 3 repositories with known mismatched SHAs (e.g., `agent-core`, `jira-skill`, `openspec-store`) and confirm they show **STALE** in both commands.
- [x] 4.6 Pick 1 repository with matching SHAs and confirm it shows **FRESH** in both commands.
- [x] 4.7 Test the UNKNOWN path: temporarily rename `.gitnexus/meta.json` in a test repo, confirm status shows **UNKNOWN** with `freshnessRule: missing_recorded_revision`.
- [x] 4.8 Run `openspec validate --all --store openspec-store` and confirm all specs including the newly merged `workspace-index-freshness` and `developer-code-intelligence` and the new `freshness-reporting-contract` pass validation.
