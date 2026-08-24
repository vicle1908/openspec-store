# Design: Repair Hermes Cron Job Run Reliability

## Architecture Decisions

### AD1: Proposed canonical ownership, pending cross-repository acceptance
- **Track 1 + Track 2** (`mcp-router-watchdog.sh`, `weekly-freshness-report.sh`): Canonical source at `ops-automation-suite/scripts/hermes-cron/`. Expand `ops-automation-suite` scope/documentation to cover workstation cron wrappers. Deploy reviewed copies to `~/.hermes/scripts/`. Runtime copies are NOT canonical.
- **Track 3** (`wiki-lint.sh`): Canonical source at `wiki/scripts/wiki-lint.py`. Contract and tests belong with the wiki. Deploy reviewed copy to `~/.hermes/scripts/`.

### AD2: Watchdog wrapper uses its own dedupe state, not the health script's mutable /tmp file
The wrapper must:
1. Execute `~/.hermes/scripts/mcp-router-health.sh --json` and parse stdout
2. Read wrapper-owned state from `${HERMES_HOME:-$HOME/.hermes}/state/mcp-router-watchdog.json` defensively (missing/stale/malformed → treat as unknown previous state)
3. Emit empty stdout when healthy and unchanged (suppresses delivery in no-agent mode)
4. Invoke the health script's existing recovery modes directly:
   - `status=critical` (router not running) → `~/.hermes/scripts/mcp-router-health.sh --restart`
   - `status=degraded` with critical_missing servers → `~/.hermes/scripts/mcp-router-health.sh --escalate`
   - medium-only missing servers → report, no restart
   - `status=skipped` → no action
5. Emit one-line alert only on state change or recovery failure
6. Propagate nonzero exit on script errors; exit 0 on healthy/unchanged

**Dedupe state path:** `${HERMES_HOME:-$HOME/.hermes}/state/mcp-router-watchdog.json`. Directory mode 0700, file mode 0600. Atomic write using temp file + rename. Missing/malformed state means "first run", not failure.

**Current health JSON controls recovery:** `--restart` for `status=critical`, `--escalate` for `critical_missing`, no-op for medium-only/skipped.

**Dedupe state never controls recovery.** It only suppresses repeated identical alerts and tracks `last_restart` for display purposes.

### AD3: No-agent silence semantics
Empty stdout = delivery suppressed. Verified from existing `weekly-skills-update` (job 230d06bbd148): "Mode: no_agent (script) / Status: silent (empty output)". The wrapper must produce zero bytes on healthy unchanged state.

### AD4: Freshness reporter is read-only
The weekly job consumes `knowledge-status.sh --json` (generated nightly by LaunchAgent at 02:30). It reports staleness classification, timeout occurrences, and dirty-tree skips. Exit 0 = report generated. Exit 1 = canonical script missing or inventory rejected. `STALE` is a report condition, not a cron failure.

### AD5: Wiki lint is a deterministic no-agent validator
All three tracks are cron-run reliability fixes discovered in the same investigation. Keeping them together reduces coordination overhead. Reviewers may recommend splitting; the delta specs are independent enough to separate.

## Trade-offs
- **Single vs. three changes:** Together = less overhead. Separate = cleaner ownership. Respecting reviewer guidance.
- **Wrapper location:** Proposed canonical sources are `ops-automation-suite/scripts/hermes-cron/` and `wiki/scripts/wiki-lint.py`, pending cross-repository acceptance. Runtime copies deployed to `~/.hermes/scripts/` are not canonical.
- **Read-only freshness:** Loses cron-initiated refresh. The nightly LaunchAgent already handles this. The cron job's role is reporting, not mutation.

## Ownership
- Watchdog wrapper: proposed at ops-automation-suite/scripts/hermes-cron/ (pending cross-repo acceptance)
- Freshness reporter: uses existing `~/Developer/scripts/knowledge-refresh/` infrastructure
- Wiki lint: proposed at wiki/scripts/wiki-lint.py (pending acceptance)
