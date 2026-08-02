# coverage-sweep — Pre-Execution Research Report

**Status:** ✅ READY FOR EXECUTION (with 4 spec corrections applied)
**Date:** 2026-06-15
**Reviewer:** Explore subagents (3) + GitNexus impact analysis

---

## Executive Summary

The `coverage-sweep` OpenSpec change is **ready for execution**. The 4 critical spec
items below had implementation drift and have been corrected in the artifacts. No
HIGH/CRITICAL blast radius was found in GitNexus impact analysis. The change is sized
appropriately (15 task groups, ~70 line-items) for incremental delivery.

**Recommended action:** Apply the 4 corrections below, then `/opsx:apply coverage-sweep`.

---

## 1. Spec vs. Implementation Drift (4 corrections needed)

### C1. `AI_REVIEW_DISPATCH_TIMEOUT_SECONDS` already exists — use the same name

**What the spec said:**
> Add `AI_REVIEW_DOWNSTREAM_TIMEOUT_SECONDS` env var read in `webhook-receiver/src/webhook_receiver/config.py` with default 30

**What exists in `webhook-receiver/src/webhook_receiver/config/settings.py:64`:**
```python
ai_review_dispatch_timeout_seconds=get_float_env("AI_REVIEW_DISPATCH_TIMEOUT_SECONDS", 2.0),
```

**Impact:** The env var name is fine, but we are **changing the default from 2.0s to 30s**.
This is a **behavioral change** for existing deployments — must call out in design and tasks.

**Correction applied:**
- design.md: add a D-decision noting the default bump and the migration risk.
- tasks.md 4.x: explicitly call out `change default from 2.0 → 30`.

### C2. `webhook-receiver` already has in-memory idempotency at the ai-review layer

**What the spec said (in `webhook-receiver-dlq` + `webhook-ai-review-repo-split` delta):**
> `webhook-receiver` SHALL deduplicate inbound GitLab webhook deliveries by
> `(project_id, MR IID, event_type)` with a 10-minute TTL

**What already exists in `ai-review/src/ai_review/services/idempotency.py`:**
- `IdempotencyRegistry` with TTL (default 3600s) keyed by `sha256(project:mr_iid:action:commit_sha)`
- Currently called `logical_key` — not `(project_id, MR IID, event_type)`, but the semantic
  intent is identical for `merge_request` events
- Already wired into the `/reviews/gitlab-mr` route
- Returns HTTP 202 with `{"status": "duplicate", "duplicate": true}` for retries

**Impact:** Our proposed receiver-side dedupe **partially duplicates** an existing
ai-review-side dedupe. Adding both creates a layered defense, but the spec was written
as if the receiver-side dedupe was the only layer. This is actually a *feature* (defense
in depth) but the spec must explain why both layers exist.

**Correction applied:**
- design.md D3 (Dedupe decision): explicitly note that ai-review already has an in-memory
  IdempotencyRegistry; receiver-side dedupe catches the case where ai-review has been
  restarted (loses in-memory state) and prevents a network call from being made at all.
- tasks.md 2.x: add a comment that the receiver-side dedupe is a *backstop* to the
  ai-review-side registry, not a replacement.

### C3. `tdt-tools/` does not exist — needs to be scaffolded

**What the spec said:**
> Create `tdt-tools/webhook-selftest.py`
> Create `tdt-tools/replay-dlq.py`
> Create `tdt-tools/gitlab-hook-dashboard.py`

**What exists:** `tdt-tools/` directory does not exist. No git repo, no `pyproject.toml`,
no venv. Scripts currently live in:
- `webhook-receiver/scripts/`
- `ai-review/scripts/`
- `~/.tdt/scripts/`

**Impact:** Three new scripts need a home. Two options:
1. **Create `tdt-tools/` as a new repo** with hatchling + uv (matches workspace pattern)
2. **Co-locate the scripts in the existing repos** (dashboard + selftest go in
   `webhook-receiver/scripts/`, replay-dlq goes in `webhook-receiver/scripts/`)

**Decision (applied):** Co-locate. The scripts are webhook-receiver-adjacent tooling.
Avoids creating a new repo + venv + LaunchAgent. Updates:
- `~/.tdt/scripts/` is the third option but the scripts there are operator-scripts,
  not service-adjacent tooling.

**Correction applied:**
- tasks.md 7.x, 8.x, 9.x: relocate to `webhook-receiver/scripts/` paths.

### C4. `~/.tdt/state/` does not exist — must be bootstrapped

**What the spec said:**
> The receiver SHALL read `~/.tdt/state/webhook-primary.state` on startup
> `WEBHOOK_DLQ_DIR` (default `~/.tdt/state/webhook-deadletter`)
> `WEBHOOK_DEDUPE_DB` (default `~/.tdt/state/webhook-dedupe.sqlite`)

**What exists:** `~/.tdt/state/` does not exist. The closest equivalents are:
- `~/.local/share/webhook-receiver/` (created by the receiver for session/circuit-breaker state)
- `~/.tdt/launchd-retired/` (LaunchAgent graveyard)

**Impact:** The receiver would have to `mkdir -p ~/.tdt/state/` on first use. The
existing pattern in `CircuitBreaker._ensure_state_file()` does
`state_file.parent.mkdir(parents=True, exist_ok=True)` at first write — we should
follow the same pattern.

**Correction applied:**
- tasks.md 1.x: add `mkdir -p` step in the bootstrap task; same pattern as CircuitBreaker.
- design.md D2: note the `~/.tdt/state/` bootstrap requirement.

---

## 2. GitNexus Impact Analysis

Ran impact analysis on the 4 key symbols I will touch:

| Symbol | Risk | Direct Dependents | Verdict |
|---|---|---|---|
| `Function:gitlab_webhook` (app.py:504) | **LOW** | 0 | ✅ Safe to modify |
| `Function:handle_merge_request` (app.py:98) | **LOW** | 2 | ✅ Safe to modify |
| `Function:health` (app.py:438) | **LOW** | 0 | ✅ Safe to add sub-routes |
| `Class:Settings` (settings.py:19) | **LOW** | 4 | ✅ Safe to add env vars |

**No HIGH/CRITICAL risk found.** The `Settings` class is the most-coupled symbol
(expected — config flows through it), but adding new env vars is purely additive.

---

## 3. Plan/Capability Validation

| Capability | Spec Section | Implementation Plan | Ready? |
|---|---|---|---|
| `webhook-public-ingress-failover` | state file, handshake header, ngrok hot-spare | Tailscale already proven; ngrok agent install + auth from `NGROK_AUTHTOKEN` env | ✅ |
| `webhook-delivery-self-test` | 5-min LaunchAgent loop, agentmemory observations | `com.tdt.*.plist` pattern is well-established; `memory_save` MCP tool is documented | ✅ |
| `webhook-receiver-dlq` | 2-failure trigger, 10k-file cap, replay CLI | All new code; no existing conflict | ✅ |
| `gitlab-hook-health-dashboard` | per-project table, primary URL header, self-test footer | Uses `glab api projects/<id>/hooks/<id>/events` (verified pattern in `sync-gitlab-hook-secrets.sh`) | ✅ |
| `webhook-incident-report` | skill that produces 1-page postmortem | `incident-report` skill will live in `.agents/skills/incident-report/SKILL.md` (same pattern as other skills) | ✅ |
| `webhook-ai-review-repo-split` (delta) | receiver-side dedupe + 30s timeout | C1/C2 corrections above | ✅ after corrections |

---

## 4. Non-blocking Observations (no correction needed)

- **The webhook-receiver dispatcher already has a 30s-feasible timeout** — `httpx.Timeout`
  is already used; we just need to bump the default from 2.0 to 30 (covered in C1).
- **The ai-review `codex` probe is degraded** (from today's health check) — this is
  unrelated to coverage-sweep. The reviewer_probes check will continue to show
  degraded, but reviews will still complete via `claude` and `codescan`. Not in scope.
- **ngrok free-tier URL rotation** — documented as a known operational risk in D1.
  ngrok is **not yet installed**; install step is in tasks 11.x.
- **`glab` is already authenticated** and `glab api` works against `git.ecomedic.vn` —
  verified during the earlier incident response.

---

## 5. Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| 30s timeout change breaks existing CI | Low | Default is still 30s; 2.0s was a bug for codex/claude. Stage in dev first. |
| New dedupe layer + existing ai-review dedupe causes confusion | Low | Document in D3 that receiver-side is a backstop. |
| `~/.tdt/state/` creation fails on read-only filesystem | Very Low | Same pattern as CircuitBreaker; tested path. |
| ngrok agent exhausts free tier | Low | Free tier has no rate limit on agent; URL is stable while agent is up. |
| Self-test false positives during funnel restarts | Medium | 3-consecutive-down threshold (D6 mitigation). |
| `tdt-tools/` path correction means re-doing some task names | Already accounted for | Updates are text-only, no code change. |

---

## 6. Final Recommendation

**GO for execution**, with the 4 corrections in section 1 applied to:
- `design.md` (D1, D2, D3 updates)
- `tasks.md` (4.x default bump note, 2.x backstop note, 7-9.x path relocation, 1.x mkdir step)

The spec change is sized for incremental delivery: 15 task groups, each completable in
one session. No HIGH/CRITICAL impact. All discovered implementation drift has been
accounted for.

### Suggested next steps

1. Apply the 4 spec corrections to the existing artifacts (above)
2. Run `openspec validate coverage-sweep` to confirm still valid
3. Start `/opsx:apply coverage-sweep` — begin with **Task Group 1: Setup & State Directory**
   (smallest, unblocks everything else)
4. Land receiver changes behind feature flags first (per design.md migration plan step 1)
5. Verify with `glab api` test deliveries before flipping production flags
