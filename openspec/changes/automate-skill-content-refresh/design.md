# Design

## Context

See `proposal.md` — Why. The constraints that shape this design are properties of
the installed `skills` CLI (v1.7.0) and of the existing daily job, both verified
by direct experiment:

- `skills update` has no `--dry-run`, `--check`, or `--json` flag. Unknown flags
  are silently ignored, so passing `--dry-run` executes a real update. A scheduled
  stage cannot ask the CLI "would anything change?" without mutating.
- The CLI does, however, emit a pre-flight line before it mutates. Global scope
  prints `Found N update(s)`; project scope prints `Refreshing N skill(s)…`. Both
  are single-line, ANSI-decorated, and parseable after escape sequences are
  stripped. They are the only non-mutating drift signal available.
- The CLI is idempotent: repeated `skills update -y` in an unchanged tree reports
  the same entry count and converges the global counter toward zero.
- `skills-lock.json`'s `computedHash` is a CLI-internal digest. For single-file
  skills it coincides with a SHA-256 over the skill tree, but for multi-file
  skills (those with `references/`) it matches neither the tree hash nor the
  `SKILL.md` hash, and is not externally reproducible. It therefore cannot be
  used as a drift oracle; this is why the spec forbids it.
- Upstream `docfork/docfork` publishes `docfork-docs` at both
  `plugins/claude/...` and `plugins/cursor/...`. The CLI declines to choose and
  prints `Warning: Multiple current paths match these skills from
  docfork/docfork; skipping them rather than deleting or migrating the wrong
  skill:`. The skip is stable and the local content already equals the lock hash.
- An agent updater can exit zero while doing nothing: `kilo update` prints
  `Error: Failed to change directory to …` and returns `0` from every working
  directory. Exit status alone is therefore not evidence that an update happened.

The existing job `~/Developer/scripts/workstation-daily-update.sh` is a
`set -euo pipefail` script with seven numbered stages and one fail-closed exit
path (`SYNC_FAILED`) owned by the parity stage. It has **no timeout guard at
all**, and its plist sets no `ExitTimeOut`. The refresh must join that structure
without weakening the parity contract.

## Goals / Non-Goals

**Goals:**

- Refresh upstream skill content on the existing daily 08:00 schedule with no
  second scheduler and no interactive prompt.
- Classify the run into the five outcomes the spec names, from the CLI's own
  output, and log them.
- Keep the parity stage's fail-closed contract intact and unchanged.
- Keep a network fault from aborting the unrelated maintenance stages.
- Bound the refresh and each agent updater so neither can stall the job.

**Non-Goals:**

- Replacing or wrapping the `skills` CLI with a custom fetcher. The CLI already
  owns checkout, path resolution, and agent fanout; reimplementing that is a
  large new failure surface for no gain.
- Reconstructing the CLI's internal lock digest to build an independent drift
  oracle. It is not reproducible for multi-file skills, so any such oracle would
  be wrong exactly where it is needed.
- Repairing the `docfork/docfork` upstream path ambiguity. That is an upstream
  taxonomy problem; the design reports it and leaves it alone.
- Fixing `kilo`'s upstream `update` defect. The design detects and reports it.

## Decisions

### Decision: Parse the CLI's pre-flight line as the drift signal

Run `skills update -y` (project scope, from the workspace root) and capture
stdout. Strip ANSI escape sequences, then classify from these markers:

- `Found N update(s)` / `Refreshing N skill(s)…` → drift was available
- `Updated N skill(s)` (project tally) or `✓ Updated <name>` (global, per-skill)
  → entries refreshed
- `Warning: Multiple current paths match … skipping them` → path-ambiguous
- a nonzero exit, a timeout, or absence of any summary line → refresh failed

*Alternatives considered:* (a) snapshot-and-diff the skill tree before and after,
rejecting a pure parse — it needs a full tree hash, doubles I/O, and still cannot
report drift *before* mutating; (b) `--dry-run`, which does not exist and silently
mutates; (c) lock-hash comparison, which the spec forbids because the digest is
not reproducible for multi-file skills. Parsing the tool's own summary is the
only signal that is both non-mutating and correct for all skill shapes.

### Decision: Treat "already current" and "refreshed" as distinct logged outcomes

Project scope always reports a constant entry count (`Refreshing 43` /
`Updated 42`), so that count alone cannot distinguish a no-op run from a real
refresh. The design records drift availability and the refreshed count as
separate fields, so a reviewer can tell "checked and nothing changed" from
"checked and pulled new content" — the whole point of the change.

A run whose only unresolved entry is path-ambiguous is deliberately **not**
reported as "already current": it was skipped, and is reported solely through the
`path_ambiguous` field.

*Alternative considered:* log only the refreshed count. Rejected: it makes every
run look identical and reproduces the original blind spot at the log level.

### Decision: Refresh failure degrades, it does not abort

The refresh stage records its failure status in a variable, reports it, and
returns success to the pipeline so the remaining stages still run. This mirrors
the existing job's use of `|| true` for network-bound stages (`brew update`, `bun
upgrade`) rather than the parity stage's fail-closed `return 1`.

*Rationale:* the spec requires the failure to be *reported* and unrelated stages
to *still execute*. A transient DNS failure must not suppress store validation.
This is a deliberate asymmetry with the parity stage, which stays fail-closed
because an unresolved link is a correctness defect, whereas an unreachable
upstream is a transient environmental condition.

### Decision: Classify path-ambiguity as informational, not stale or failed

The stage matches the skip warning and counts those entries in a distinct
`path_ambiguous` bucket. They are neither refreshed nor failed, and they do not
affect the stage's exit status.

*Rationale:* the spec requires the skip to be informational and to be able to
leave the run successful. Verified content equality with both upstream copies
means nothing is actually stale, so reporting it as staleness would be a false
positive that trains reviewers to ignore the report.

### Decision: Insert the refresh after parity, before store validation

The refresh becomes a new stage between the existing skills parity check (stage 6)
and the OpenSpec validation gate (stage 8), with the agent-CLI loop renumbered
ahead of parity. Banners become `N/8`.

*Rationale:* the spec requires this ordering. Parity must run first because it
reconciles the symlinks the refresh will later point at; store validation runs
last because it is the whole-job quality gate and should observe the final tree.

### Decision: Reuse the sibling job's `run_with_timeout` helper rather than inventing one

The refresh invocation and every agent update are wrapped in the PID-aware,
macOS-native `run_with_timeout <seconds> <command>` helper already proven in
`~/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh`, which
returns `124` on timeout. A refresh returning `124` is classified
`refresh_failed`; an agent update returning `124` is reported failed.

The helper is copied into the daily script rather than sourced, so the job has no
new cross-file dependency and cannot be broken by an edit to the sibling script.

*Alternatives considered:* (a) relying on the launchd job's implicit scheduling
with no bound — rejected, because the daily job has no timeout guard and its
plist sets no `ExitTimeOut`, so a hung `skills update` would occupy the job
indefinitely; (b) GNU `timeout`, absent by default on macOS — the sibling script
exists precisely because of that; (c) writing a new helper, which duplicates a
solved problem. Bounds chosen: 1800s for the whole refresh, 900s per agent.

### Decision: Declare the agent-CLI covered set explicitly in the script

Replace the single `claude update` call with a loop over a literal, declared list
of covered agent CLI binaries, updating each present one, logging the declared
set, and reporting any other agent CLI found on `PATH` as uncovered. The covered
set is `claude`, `codex`, `opencode`, `kilo`, `auggie`, `qoder`, and `pi` — every
agent CLI verified present on this workstation that exposes a scriptable update
verb — with the invocation per binary taken from that tool's own verb:

| Bin        | Invocation                          | Non-mutating check            |
| ---------- | ----------------------------------- | ----------------------------- |
| `claude`   | `claude update`                     | none (`--check` is rejected)  |
| `codex`    | `codex update`                      | none                          |
| `opencode` | `opencode upgrade`                  | n/a                           |
| `kilo`     | `kilo update`                       | n/a                           |
| `auggie`   | `auggie update --skip-confirmation` | `upgrade --skip-confirmation` |
| `qoder`    | `qoder update`                      | `qoder update --check`        |
| `pi`       | `pi update --self`                  | n/a                           |

`droid` is deliberately excluded: it is a native binary with no discoverable
update subcommand and no help output, so it self-updates in-app. The stage reports
it as uncovered, which is the honest outcome rather than a fabricated
`droid update` invocation.

*Rationale:* the spec requires the covered set to be declared and reported. A set
inferred from `PATH` would make the requirement untestable and would let a newly
installed agent silently escape coverage — exactly the defect this change exists
to fix.

*Alternatives considered:* hard-coding a pinned expected version per agent, as the
prior archived change did. Rejected: that pins versions (`claude` `2.1.283`,
`codex` `0.157.0`) which drift immediately and turn the spec into a maintenance
liability; the capability should own the *behavior*, not the version numbers.

### Decision: Treat an error report with a zero exit as an update failure

After each agent update, the stage also inspects the captured output for an error
signal and reports the agent failed when it finds one, even though the exit status
was zero.

*Rationale:* verified by experiment — `kilo update` returns `0` while printing
`Error: Failed to change directory to …` and performing no update. Trusting exit
status alone would report a silent no-op as success, which is the same class of
blind spot this change exists to remove.

### Decision: Pass `--skip-confirmation` where a tool would otherwise prompt

`auggie update` prompts for confirmation. Under launchd there is no TTY, so the
stage passes `auggie update --skip-confirmation` explicitly rather than relying on
EOF-from-`/dev/null` to make the prompt resolve unpredictably.

*Rationale:* the daily job runs non-interactively and must never block on input.
Verified: with no TTY, `auggie update` currently proceeds and reports "already
running the latest version" — but that is incidental behavior of the current
version, not a contract, and an explicit flag is the durable form.

## Risks / Trade-offs

- **[CLI output is not a stable API: a rename of `Found N update(s)` breaks
  parsing]** → Match defensively on both known phrasings and treat an
  unrecognized summary as `refresh_failed` rather than success, so a wording
  change surfaces loudly instead of silently reporting "already current".
- **[The error-text heuristic could match benign output, yielding a false
  failure]** → The pattern is deliberately anchored to explicit error markers and
  is applied to a bounded tail of output. A false failure is a reported
  degradation, which is the safe direction; a false success is what must be
  avoided.
- **[Scheduled `skills update` mutates `skills-lock.json`, producing an
  unattended working-tree change]** → `~/Developer` is not a Git repo, so no
  repository is dirtied; the lockfile is expected to change as content changes,
  and the stage logs the refreshed count so the change is attributable.
- **[A refresh that rewrites a skill could invalidate a manifest-declared entry
  and trip the parity stage on the *next* run]** → The refresh runs *after*
  parity within a run, so the next day's parity check is the detector and fails
  closed. Content churn should not be able to silently desynchronize the fanout.
- **[Network access from a launchd job can be blocked by sandbox or proxy
  policy]** → The stage degrades to `refresh_failed` and logs it, matching the
  existing `|| true` treatment of other network-bound stages.
- **[Adding a timeout wrapper changes behavior for the agent stage, which
  previously ran unbounded]** → Bounds are generous (900s per agent) relative to
  observed runtimes (seconds), so the timeout is a backstop rather than a routine
  constraint.

## Migration Plan

1. Add the helpers, the refresh stage, and the agent-CLI loop to
   `~/Developer/scripts/workstation-daily-update.sh`, renumbering banners to
   `N/8`.
2. Verify by hand: `bash -n` for syntax; run the script and confirm the refresh
   stage reports the five outcomes in the log and that store validation still
   passes.
3. Confirm idempotence: an immediate second run reports no content change and the
   same single path-ambiguous entry.
4. No plist change is required; the existing
   `com.developer.workstation-daily-update.plist` picks up the modified script on
   its next 08:00 run.

*Rollback:* revert the script's refresh stage, agent-CLI loop, and helper block;
the previous behavior (single `claude update`, parity check) is restored. There
is no persistent state to unwind beyond the skills the stage refreshes, and the
lockfile is regenerated by the CLI.

## Open Questions

None. The drift signal, the failure semantics, the ordering, the timeout bounds,
and the path-ambiguity classification are all resolved above from direct
experiment.
