## Context

Workspace freshness reporting is currently split between two semantics:

- `knowledge-status.sh` `classify_freshness()` (lines 73-97) classifies by timestamp delta: `head_ts - idx_ts <= STALENESS_THRESHOLD_DAYS(1)`. This produces **FRESH** for any index refreshed within 24 hours regardless of whether it matches HEAD.
- `refresh-knowledge-indexes.sh --check` (lines 1007-1125) compares recorded commit SHAs: `gn_rev == head_rev` and `gf_rev == head_rev`. This produces **STALE** whenever the index commit differs from HEAD.

The dashboard is optimistic; the check is correct. Both should use commit equality.

## Goals / Non-Goals

**Goals:**

- Make `HEAD == recorded indexed revision` the sole authoritative freshness signal for GitNexus and Graphify.
- Replace the timestamp-based `classify_freshness()` function in `knowledge-status.sh` with a commit-equality classifier.
- Fix Graphify freshness in `knowledge-status.sh` to use commit equality (currently Graphify always falls through to timestamp classification).
- Fix GitNexus mismatch fallback in `knowledge-status.sh` to assert STALE instead of falling to timestamp.
- Add `indexedSha`, `headSha`, `freshness`, and `freshnessRule` fields to JSON status output.
- Ensure `refresh-knowledge-indexes.sh --check` and `knowledge-status.sh` use the same Graphify graph.json path fallbacks.
- Make `refresh-knowledge-indexes.sh --check` produce the same freshness result as `knowledge-status.sh` for the same repo state.

**Non-Goals:**

- Changing provider CLI internals or batch-refresh behavior.
- Changing inventory approvals, nightly schedule, or lock semantics.
- Performing a workspace-wide re-index in this change.

## Decisions

### 1. Replace `classify_freshness()` with `classify_freshness_by_commit()`

In `knowledge-status.sh`, replace the timestamp-based function with:

```bash
classify_freshness_by_commit() {
  local indexed_rev="$1" head_rev="$2"
  if [[ -z "$indexed_rev" || "$indexed_rev" == "" ]]; then
    echo "UNKNOWN"
    return
  fi
  if [[ -z "$head_rev" || "$head_rev" == "" ]]; then
    echo "UNKNOWN"
    return
  fi
  if [[ "$indexed_rev" == "$head_rev" ]]; then
    echo "FRESH"
  else
    echo "STALE"
  fi
}
```

Callers change from `classify_freshness "$(gitnexus_index_timestamp "$root")" "$(head_timestamp "$root")"` to `classify_freshness_by_commit "$(gitnexus_indexed_sha "$root")" "$(head_sha_full "$root")"`.

A full-SHA helper `head_sha_full()` is needed because `head_sha()` returns 7 chars but recorded revisions are full SHAs.

**Why:** Eliminates the root inconsistency. Timestamp fallback is removed entirely because recorded commit metadata is always available when `.gitnexus/meta.json` or `graphify-out/graph.json` exist.

**Alternative considered:** Keep timestamp as a fallback when commit is missing. Rejected because `UNKNOWN` is the correct signal for missing metadata and avoids false confidence.

### 2. Add `indexedSha` to status output

In `knowledge-status.sh`, the per-repo status loop currently outputs `indexedSha` from `gitnexus_indexed_sha()` and `graphify_indexed_sha()` — but the human table omits it. Add it as a column.

In the JSON output, the existing `indexedSha` field is already populated for GitNexus but not consistently for Graphify. Ensure both providers populate `indexedSha` from their respective commit-metadata helpers.

### 3. Fix Graphify and GitNexus code paths in `knowledge-status.sh`

Two structural bugs in `knowledge-status.sh` `process_repo()`:

**Graphify ignores commit equality (lines 362-374):** `graphify_indexed_sha()` is called but the freshness block never compares it against HEAD. It always falls through to `classify_freshness()` (timestamp). Fix: add `elif [[ -n "$gf_idx_sha" ]]` → compare against `head_sha_full` → FRESH/STALE.

**GitNexus mismatch falls to timestamp (line 343):** When `gn_idx_sha` exists but differs from `head_sha_val`, the else branch calls `classify_freshness()` (timestamp). Fix: the else branch SHALL assert STALE directly — no timestamp escape.

### 4. Graphify fallback path parity

`knowledge-status.sh` `graphify_indexed_sha()` checks two paths:
- `graphify-out/graph.json`
- `.claude/graphify/graph.json`

`refresh-knowledge-indexes.sh --check` (line 1043) only checks `graphify-out/graph.json`. Fix: add the `.claude/graphify/graph.json` fallback to `--check` as well.

### 5. `--check` exit code contract

Define: `--check` exits 0 when all providers are FRESH, exits 1 when any provider is STALE or UNKNOWN, exits 2 on script error. This makes `--check` usable in CI gates.

### 6. Add `freshnessRule` to JSON output

Add a `freshnessRule` field to each provider row in `knowledge-status.sh --json` output:
- `commit_equality` — classification derived from SHA comparison
- `timestamp_degraded` — fallback used because no recorded revision was available (should be rare)

This distinguishes authoritative from degraded freshness without changing the existing `freshness` field.

### 7. Human table format change

Before:

```
Repository                  Tool       Status       Last Refresh    HEAD
```

After:

```
Repository                  Tool       Status       Indexed Rev    HEAD
```

Replace `Last Refresh` date column with `Indexed Rev` (7-char SHA) to make commit equality visually obvious. Keep `Last Refresh` available via `--json` only.

## Risks / Trade-offs

- **Risk:** Integrations consuming `knowledge-status.sh` text output may parse the old column layout.  
  **Mitigation:** The human table is for operators; JSON consumers use structured fields. Document the column change.

- **Risk:** Some repos will show **STALE** immediately after this change, even though they were functional.  
  **Mitigation:** This is the correct signal; the change is scoped to reporting only.

- **Risk:** `graphify_indexed_sha()` depends on `built_at_commit` key in `graph.json`, which may be absent for very old graphs.  
  **Mitigation:** Return empty string → classified as **UNKNOWN**, which is correct.
