## Context

The TDT platform has two services that post GitLab MR notes idempotently:
`ai-review` (codescan reviewer + final publication) and `webhook-receiver`
(impact analysis). Both use a find-then-upsert pattern with a marker to
locate the existing note on re-run, but the implementations have diverged:

- **Codescan** uses `ai_review.gitlab.review_posting.GitLabReviewPoster`
  with the hidden HTML-comment marker `<!-- code-scan-review -->` and
  substring matching (`marker in body`).
- **Impact** uses `tdt_core.clients.gitlab_mr.{find_mr_notes, upsert_mr_note}`
  (orchestrated by `jira_skill.impact.gitlab_note.post_gitlab_note`) with
  the visible Unicode prefix `⚠️ Impact Analysis — MR !` and prefix
  matching (`body.startswith(NOTE_PREFIX)`).

The user's request: align impact with codescan — same marker style, same
trigger and schedule mechanism. The current behaviour already triggers
correctly on open/reopen/merge AND on the 15-min `scan-recent-mr` cron;
no scheduler change is needed.

A previous design proposed relocating `GitLabReviewPoster` to `tdt-core`
and adding a new `webhook_receiver.gitlab_poster` wrapper. On closer
review, that approach **duplicates existing infrastructure** —
`find_mr_notes` / `upsert_mr_note` already exist in `tdt-core` and are
already tested in `tdt-core/tests/test_gitlab_mr.py`. The codescan
writer stays where it is; impact changes its marker and matching
predicate in place.

Stakeholders: webhook-receiver (impact pipeline owner), jira-skill
(impact markdown builder + orchestrator), tdt-core (shared SDK).

## Goals / Non-Goals

**Goals:**

- The impact GitLab MR note uses an HTML-comment marker
  (`<!-- tdt-impact-analysis -->`), matching the codescan convention.
- Existing impact notes (currently with the visible prefix) gain the new
  marker line in their body without losing information.
- Idempotent edit-in-place continues to work — no duplicate notes on
  re-run.
- The 15-minute `scan-recent-mr` cron continues to drive impact posting
  for any MR missed by webhooks (already in place).
- Zero new modules in `tdt-core` and `jira-skill`; the existing writer
  (`find_mr_notes` / `upsert_mr_note`) and orchestrator (`post_gitlab_note`)
  are reused with updated marker semantics.

**Non-Goals:**

- Folding impact into `ai-review`'s `BaseReviewer` pipeline.
- Relocating `GitLabReviewPoster` to `tdt-core` (different abstraction;
  not the user's request).
- Adding a new `webhook_receiver.gitlab_poster` wrapper
  (`post_gitlab_note` already exists and already prepends the marker).
- Changing the trigger semantics (open / reopen / merge).
- Changing the merge-only Jira posting behaviour.
- Removing `tdt_core.clients.gitlab_mr.find_mr_notes` /
  `upsert_mr_note` — they remain the writer.
- Changing the 15-min cron — already in place.
- Auto-cleaning up legacy notes — migration in-place preserves the
  visible prefix as historical context.

## Decisions

### D1: Reuse `tdt_core.clients.gitlab_mr`, do not relocate `GitLabReviewPoster`

**Why:** The user asked for marker alignment, not writer consolidation.
`find_mr_notes` and `upsert_mr_note` already exist in `tdt-core`,
already have tests in `tdt-core/tests/test_gitlab_mr.py`, and are
already used by impact via `post_gitlab_note`. Relocating the codescan
writer would create a new home for code that is correctly placed
today, and force an artificial unification of two parallel
abstractions (codescan's `GitLabReviewPoster` returns
`"posted"`/`"updated"` strings; impact's `upsert_mr_note` returns
raw note IDs).

**Alternatives considered:**

- *Relocate `GitLabReviewPoster` to `tdt-core` and have impact use it.*
  Adds churn (delete `find_mr_notes` / `upsert_mr_note`, port tests,
  rewrite `post_gitlab_note`). Two return-shape conventions (string
  status vs int) make a clean merge awkward.
- *Add a `webhook_receiver.gitlab_poster` wrapper that calls
  `GitLabReviewPoster`.* New module + new tests, on top of the
  relocation. Pure duplication — `post_gitlab_note` already does
  the same job.
- *In-place marker change.* **Chosen.** Minimal change, no new
  modules, reuses existing tested infrastructure.

### D2: HTML-comment marker `<!-- tdt-impact-analysis -->`

**Why:** Matches codescan's pattern. Codescan marker is
`<!-- code-scan-review -->`; impact marker is parallel
`<!-- tdt-impact-analysis -->`. Both are HTML comments, invisible in
the MR discussion.

**Alternatives considered:**

- *Reuse the codescan marker verbatim.* Risk: future grep for
  codescan output accidentally picks up impact notes.
- *Keep the visible prefix unchanged.* Doesn't address the noise
  problem the user wants fixed.
- *JSON metadata in the body.* Overkill; the marker is only used
  for idempotency, not parsing.

### D3: Substring matching (`in`) instead of prefix matching (`startswith`)

**Why:** Codescan uses substring matching (`marker in body`).
`find_mr_notes` currently uses prefix matching (`body.startswith(prefix)`).
Aligning the two means a single shared convention for "is this a
managed note?".

**Pragmatic consequence:** With substring matching, `find_mr_notes`
can locate both legacy notes (whose body starts with the old visible
prefix and after migration will also contain the new HTML marker) and
new notes (whose body starts with the new HTML marker). Both are
matched by the same predicate.

**Alternatives considered:**

- *Keep `startswith`, prepend HTML marker to body.* Inconsistent
  semantics between the two writers; the migration helper has to
  rewrite every note regardless of which marker it sees.
- *Match either prefix (legacy) or substring (new).* Doubles the
  matching logic; harder to maintain.

### D4: One-shot migration gated by state file

**Why:** Without migration, every MR with an existing impact note
(122 edits on MR 23433 alone) would still be editable in place
because substring matching finds both the old visible prefix and
the new HTML marker. **Migration is therefore not strictly required
for correctness** — but the user wants the new HTML marker on the
note (so future code, expecting the new marker, works). Migration
prepends the HTML marker line to the existing note body. State
file at `~/.tdt/state/webhook-receiver/impact-marker-migrated.json`
ensures each MR is migrated at most once per host.

**Alternatives considered:**

- *Delete old notes, create new ones on first run.* Loss of edit
  history in the MR discussion.
- *Inline migration in `post_gitlab_note` (every call).* Wastes
  a `GET` per call to check; the state file is cheaper.
- *Operator-triggered migration script.* Adds operational overhead.
- *No migration — rely on substring matching alone.* **Rejected.**
  Future code expecting the HTML marker will not see it on legacy
  notes; this is the user's explicit goal.

### D5: Migration helper lives in `webhook-receiver`, not `tdt-core`

**Why:** The migration is a webhook-receiver concern (driven by the
`run_gitlab_note_workflow` call site). It uses `tdt_core.clients.gitlab_mr`
for the API surface but is not a general-purpose SDK function.
Putting it in `tdt-core` would invite future callers to use it as
a "migration utility", which is wrong — it's a one-shot deploy-time
helper.

**Alternatives considered:**

- *Put migration in `tdt-core` as a "legacy marker upgrade" utility.*
  Promotes a one-shot helper to a permanent API.
- *Put migration inline in `run_gitlab_note_workflow`.* Couples
  the workflow to the migration logic; harder to test in isolation.

## Risks / Trade-offs

**[R1] Substring matching is slightly less strict than prefix matching**
→ With `startswith(NOTE_PREFIX)`, a note is "managed" iff it starts
with the exact marker. With `NOTE_PREFIX in body`, a note is
"managed" iff the marker string appears anywhere. → **Mitigation:**
The marker is a unique, stable string (`<!-- tdt-impact-analysis -->`).
The risk of accidental collision (a regular comment containing the
exact HTML comment marker) is negligible. Document the marker in
the spec so operators know what to grep for.

**[R2] Migration adds latency to first post-deploy impact run**
→ Each migration is one GET + one PUT. For the 20 most-recent MRs
in `scan_recent_mr`, this is 20 GETs + 20 PUTs spread over the
cycle. → **Mitigation:** Acceptable. The migration runs in
`asyncio.to_thread` and is non-blocking.

**[R3] State file corruption**
→ If `impact-marker-migrated.json` is corrupted or deleted, the
migration could re-run. → **Mitigation:** The migration is safe
to re-run — it skips notes that already contain the new HTML
marker (the new `find_mr_notes` substring match already locates
them; the migration just checks for the legacy prefix).

**[R4] `NOTE_PREFIX` constant change is a breaking API change for
external callers** → Anyone importing `NOTE_PREFIX` from
`tdt_core.clients.gitlab_mr` gets the new value silently. →
**Mitigation:** The constant is `internal` (lives in a vendored
SDK). External callers should use `find_mr_notes` / `upsert_mr_note`
directly. The change is documented in the OpenSpec change log.

**[R5] Existing 122 edits on MR 23433 note (619577) — body length
grows** → Prepending the marker adds one line (~40 bytes) to a
122-edit note. → **Mitigation:** GitLab accepts notes up to 1MB;
this is far below the limit.

## Migration Plan

**Deploy order:**

1. `tdt-core` — change `NOTE_PREFIX` constant + update matching
   predicate in `find_mr_notes`. Update tests in
   `tdt-core/tests/test_gitlab_mr.py`. Backwards-compatible
   (additive semantics change; old `find_mr_notes(prefix=...)`
   callers still work).
2. `webhook-receiver` — adds `impact_marker_migration.py` module
   + invocation in `run_gitlab_note_workflow`. Adds test file.
3. `jira-skill` — updates existing tests in
   `jira-skill/tests/impact/test_gitlab_note.py` to reflect the
   new marker in expected outputs. Source unchanged
   (`post_gitlab_note` already prepends `NOTE_PREFIX`; once
   `NOTE_PREFIX` is updated, the new marker propagates).

Each repo deploys independently via its existing `scripts/deploy.sh`.

**Rollback:**

- Set `GITLAB_IMPACT_NOTE_ENABLED=false` in `~/.tdt/.env` and
  redeploy `webhook-receiver`. Disables all impact note posting
  immediately.
- If the marker change breaks `find_mr_notes` semantics, revert
  the matching predicate to `startswith` (one-line change).

**Operational checks after deploy:**

1. `tail deployments/webhook-receiver/logs/webhook-receiver.stdout.log`
   should show `impact_marker_migration_done` for MRs with legacy
   notes.
2. GitLab MR UI for MR 23433: exactly one impact note exists, body
   starts with `<!-- tdt-impact-analysis -->` followed by the
   legacy `⚠️ Impact Analysis — MR !` line (preserved).
3. `gitnexus impact --change impact-codescan-marker-alignment`
   (if available) shows no callers of `NOTE_PREFIX` outside
   `tdt-core` and `jira-skill`.

**Deploy dependency refresh:** The `webhook-receiver/scripts/deploy.sh`
script (lines 204-216) copies path dependencies (`tdt-core`, `jira-skill`,
`jira-daily-reports`, `tdt-sheets`) from the canonical workspace tree
into `$DEPLOYMENTS_ROOT/webhook-receiver/deps/` on every deploy. This
means the source-of-truth changes in `$WORKSPACE_ROOT/tdt-core` and
`$WORKSPACE_ROOT/jira-skill` propagate automatically to the runtime
`deps/` directory. **No manual copy step is needed** — the deploy
script handles it.

## Open Questions

- **Q1:** Should the migration also rewrite legacy notes that were
  originally created with `⚠️ Impact Analysis — MR !` to drop the
  visible prefix entirely (replacing it with the HTML marker only)?
  **Decision:** No. The visible prefix is preserved as historical
  context. The migration only **prepends** the new HTML marker line.
  If we ever decide to clean up legacy notes, that's a separate
  task.

- **Q2:** Should the `find_mr_notes` matching accept a regex flag
  for future marker formats? **Decision:** No. YAGNI. If a future
  marker style is needed, add an explicit parameter.

- **Q3:** Should the migration be eager (run during deploy) or
  lazy (run on first impact post per MR)? **Decision:** Lazy.
  Eager migration on every deploy would re-process every active
  MR. Lazy migration only touches MRs that actually receive an
  impact post.
