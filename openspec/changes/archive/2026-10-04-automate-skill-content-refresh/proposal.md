# Automate scheduled refresh of upstream skill content

## Why

The daily maintenance job verifies that skill *links* resolve and that content is
*readable*, but nothing in the scheduled pipeline ever pulls upstream skill
content: `skills update` is invoked by no LaunchAgent and no cron entry, so 42 of
43 upstream-sourced skills had pending updates that only a human running
`skills update -y` by hand could clear. The automation therefore certifies a
skill tree as healthy while its content silently ages.

## What Changes

- Add a scheduled skill-content refresh stage to the daily maintenance job that
  pulls upstream content for the canonical store `~/Developer/.agents/skills/`,
  running after the existing parity check and before store validation.
- Detect and report skill-content drift as a first-class maintenance outcome,
  distinguishing *refresh available*, *refreshed*, *already current*, *path-
  ambiguous* (skipped by upstream, not a failure), and *refresh failed*.
- Report drift availability before any content is replaced, because the `skills`
  CLI exposes no dry-run mode: its only non-mutating signal is a summary line it
  emits ahead of the writes.
- Bound each refresh invocation in time, so a hung `skills update` cannot occupy
  the daily job indefinitely.
- Treat an unreachable upstream or a failed refresh as a reported degradation
  rather than a silent success, while keeping the run non-fatal so a transient
  network fault cannot fail the whole maintenance job.
- Classify the `docfork-docs` skip as a known path-ambiguity condition: upstream
  `docfork/docfork` publishes the same skill at two paths
  (`plugins/claude/...` and `plugins/cursor/...`), so the CLI refuses to choose
  and skips it. Its on-disk content already equals the recorded lock hash, so the
  skip MUST be reported as informational and MUST NOT be treated as stale,
  broken, or failing.
- Record the refresh outcome in the maintenance log so a reviewer can tell that
  content was checked, not merely that links resolved.
- Extend the coding-agent CLI stage to update a declared covered set of agent
  CLIs rather than only `claude`, and to report both the covered set and any
  installed agent CLI outside it.
- Detect an agent updater that reports an error while still exiting zero, so such
  a run is reported as a failure rather than as a successful update.

## Capabilities

### New Capabilities

None. This change extends requirements already owned by an existing capability.

### Modified Capabilities

- `ecosystem-tooling-and-skills-upgrade`: the existing requirement "Unified
  daily scheduled maintenance and check-and-update automation" enumerates the
  stages of `workstation-daily-update.sh` as "Homebrew, Bun, filtered npm, uv
  tools, coding agents, skills sync, and store validation" — "skills sync"
  denotes the symlink parity check, and no requirement anywhere in the capability
  mandates pulling upstream skill *content* on a schedule. The existing
  requirements cover link resolution ("Canonical skill store entries resolve to
  readable content", "User-scope fanout links resolve to canonical content") and
  fail-closed behavior on unresolved links ("Scheduled maintenance fails closed
  on unresolved skill links"), but content currency is unowned. A new
  requirement must mandate a scheduled content refresh, define its drift
  outcomes, and specify that path-ambiguous upstream entries are reported as
  informational rather than failing.

## Impact

- **Automation**: `~/Developer/scripts/workstation-daily-update.sh` gains a
  skill-content refresh stage and revised stage numbering, plus a time bound
  reused from the sibling `refresh-knowledge-indexes.sh` helper; the job runs
  under `com.developer.workstation-daily-update.plist` (daily 08:00) with no
  schedule change. The plist currently sets no `ExitTimeOut` and the script
  currently has no timeout guard at all, so the bound is introduced here.
- **Skill content**: `~/Developer/.agents/skills/` — 42 upstream-sourced entries
  become continuously refreshed instead of manually refreshed; local
  (non-upstream) skills are out of scope and must not be touched.
- **Lockfile**: `~/Developer/skills-lock.json` (43 entries) is rewritten by the
  CLI as content changes. Its `computedHash` is a CLI-internal digest that is not
  externally reproducible for multi-file skills, so the refresh stage MUST NOT
  rely on lock-hash comparison as its drift signal.
- **Observability**: `~/Library/Logs/workstation-daily-update.log` gains a
  per-stage refresh summary; `.knowledge-refresh/refresh.log` is unaffected
  because the index-refresh job does not manage skill content.
- **Recoverability**: this change performs verification, so per
  `cleanup-archive-verification` it records its evidence in `evidence.md` inside
  the change directory. Its artifacts are also committed to the store's git
  rather than left untracked, because concurrent sessions in this store have
  removed untracked change directories without a trace.
- **Non-goals**:
  - Not introducing a second scheduler; the refresh rides the existing daily job.
  - Not changing the symlink parity contract or the fail-closed unresolved-link
    behavior owned by the existing requirements.
  - Not vendoring, editing, or pinning upstream skill content, and not
    addressing upstream metadata that exceeds the TDT description budget.
  - Not resolving the `docfork/docfork` upstream path ambiguity by hand-editing
    the lock; the condition is reported, not silently rewritten.
  - Not adopting Codex's own `~/.codex/skills/` directory.
