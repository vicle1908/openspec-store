# agentmemory 0.9.29 — Local E2E Findings vs Upstream Issue Map

Date: 2026-08-31 (post-E2E sweep of all 54 advertised MCP tools)
Purpose: cross-reference for our local findings — all three defects are already
tracked upstream; this documents the mapping and the local workarounds.

## Finding → Upstream issue map

| # | Local finding (verified on this machine) | Upstream issue | State | Fix PR | Notes |
|---|---|---|---|---|---|
| 1 | MCP slot tools (7) return raw `500 Internal error` when `AGENTMEMORY_SLOTS=false` | #888 (filed 2026-08-26) — exact match, same error string; predecessors #678 (closed v0.9.22), #1068 (closed v0.9.27, PR #894 unreleased) | OPEN | PR #894 (OPEN, mergeable, 2 reviews) — regressed twice; also PR #1149 (draft) and issue #1148 | Regression-prone: fixed in 0.9.22, broken again, fixed in 0.9.27 via #894 but that PR was never released, so 0.9.28/0.9.29 shipped the bug |
| 2 | `memory_reflect` 500/timeout when `AGENTMEMORY_REFLECT=false` (missing gate, same class as #1) | #655 covers the *timeout* framing (semantic consolidate + reflect); no issue found for the *missing MCP gate* specifically | OPEN (perf framing) | none for the gate | Verify on a smaller store whether it's the gate (fails fast) or the KV-sequential perf bug (times out slowly) — on ours both apply |
| 3 | `memory_export` unusable at ~1.5GB/263-session store: MCP passes empty payload (no maxSessions/offset), MCP→REST proxy hard-codes 10s abort, REST export exceeds ~15 MiB engine frame limit and reports it as **HTTP 200 with error body** | #1142 (export drops worker past 16 MiB), #1168 (unbounded sourceObservationIds/sourceMemoryIds push collections past the limit) | OPEN | none | The 200-with-error-body is a local observation not yet in any issue body — the strongest candidate for a genuinely new upstream comment |

## What we do locally (no config flag changes — deliberate posture per
archived change `optimize-agentmemory-runtime-config`, 2026-08-21)

1. Treat slot/reflect tool 500s as **expected** when flags are off. Verify
   first: `grep AGENTMEMORY_SLOTS ~/.agentmemory/.env`.
2. Do not call `memory_export` (or REST export unpaginated) on this store.
   For partial exports: `curl 'localhost:3111/agentmemory/export?maxSessions=5&offset=0'`
   — and check the JSON body for the in-band `error` field, not just status.
3. `memory_recall` narrative/full can 504 on first call (LLM cold start);
   retry before diagnosing. `format=compact` is the reliable path.
4. Watch for a release after 0.9.29 — #1298/#1299/#1300 closed 2026-08-31,
   suggesting a 0.9.30 is being prepared; PR #894 may finally land.

## Candidate upstream contributions from our sweep

- Comment on #888 confirming reproduction on 0.9.29 + macOS arm64 (comment
  exists for Debian; OS coverage helps maintainers).
- Comment on #1142 (or new issue) documenting the **HTTP 200 with in-band
  error body** behavior — status-code checks silently misread it.
- The 10s hard-coded proxy AbortController (`fetchTimeout ... 1e4`) is a
  local source observation not visible in #1142's framing.

Local diagnosis artifacts preserved in agentmemory lessons:
- `lsn_389d8335614dfe1c` (slots 500 by design)
- `lsn_ada02a221027e17a` (export frame limit + transient retry)
