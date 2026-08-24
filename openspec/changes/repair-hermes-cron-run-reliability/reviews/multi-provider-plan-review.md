# Multi-Provider Plan Review: repair-hermes-cron-run-reliability

**Reviewed:** 2026-08-25
**Frozen baseline:** 7c9ceac6e35b5019622be98dfb5788610e2514b3
**Branch:** review-hermes-cron

## Provider Evidence Matrix

| Provider | Version | Invocation | Outcome | Verdict | Evidence |
|---|---|---|---|---|---|
| Codex | 0.149.1 | Orca terminal, print mode | Completed | **BLOCK** | `reviews/codex.md` |
| AGY | 1.1.19 | Direct CLI, `--mode plan --dangerously-skip-permissions` | Completed | **PASS_WITH_CHANGES** | `reviews/agy.md` |
| Claude | 2.1.241 | Direct CLI, `claude -p --tools Read` | NOT_REVIEWED | — | `reviews/provider-failures.md` |
| Pi | 0.84.2 | Direct CLI, `pi -p --no-session --tools ''` | NOT_REVIEWED | — | `reviews/provider-failures.md` |
| OMP | 18.0.4 | Direct CLI, `omp -p --mode=json --no-tools` | NOT_REVIEWED | — | `reviews/provider-failures.md` |
| Prime Agent | 0.8.0-beta | Direct CLI, `prime-agent -p --no-session -nt` | NOT_REVIEWED | — | `reviews/provider-failures.md` |
| Kimi | 0.38.0 | Direct CLI, `kimi -p --no-session --plan` | NOT_REVIEWED | — | `reviews/provider-failures.md` |

**Summary:** 2 of 7 providers produced substantive verdicts. 5 providers were NOT_REVIEWED due to auth failure, startup overhead timeout, empty assistant response, tool-call-only output, or CLI syntax errors. The change is NOT implementation-ready.

Root causes for all 5 NOT_REVIEWED providers are documented in `reviews/provider-failures.md`.

## Convergent Findings (Codex + AGY)

### F1: Canonical script ownership requires cross-repository acceptance (BLOCKER)
Tasks 1.1, 2.1, and 3.6 are correctly blocked pending acceptance of proposed canonical locations. Neither `~/.hermes/scripts/` nor `~/Developer/scripts/` is version-controlled.

**Proposed resolution (pending approval):**
- Watchdog wrapper + freshness reporter: `ops-automation-suite/scripts/hermes-cron/` (expand scope)
- Wiki validator: `wiki/scripts/wiki-lint.py` (contract belongs with the wiki)
- Deploy reviewed copies to `~/.hermes/scripts/`; runtime copies are NOT canonical

### F2: Watchdog state ordering must use wrapper-owned state
The health script overwrites `/tmp/mcp-router-watchdog-state.json` during its run. Recovery must be based solely on current health JSON stdout. Alert deduplication must use a separate wrapper-owned state file at `${HERMES_HOME:-$HOME/.hermes}/state/mcp-router-watchdog.json`.

### F3: Wiki date semantics resolved
`date: 2026-08-20` is the document date; git creation date is `2026-08-23`. Preserve both: `created: 2026-08-23` + `date: 2026-08-20`. Update SCHEMA.md to document optional `date` field.

### F4: Wiki-lint mode must be deterministic no-agent
Make it a deterministic no-agent validator: zero-byte stdout when clean; report findings with exit 0; emit diagnostics and exit nonzero only when the validator itself fails.

### F5: Freshness status has two independent dimensions
- `freshness`: SHA equality (FRESH, STALE, UNKNOWN)
- `operation_status`: last operation result (SUCCESS, TIMEOUT, DIRTY_SKIP)
A timeout does not replace freshness classification. Extend `knowledge-status.sh --json` rather than parsing free-form logs. The canonical mutation path includes both the LaunchAgent and approved post-merge dispatchers.

### F6: Acceptance/rollback tasks need exact scope
- Verify only three affected jobs by execution
- Verify two unaffected jobs by definition equality
- Record pre-change fields; rollback each through `hermes cron edit`

## Trust Boundary

All review prompts required read-only behavior. One provider invocation caused tracked GitNexus metadata changes in the worktree; those changes were detected and reverted before synthesis.

## Side-Effect Incident

 Suspected side effect from malformed shell interpolation during Batch 1 dispatch; temporal and stderr evidence is consistent with an unintended Graphify invocation. Verified consequences:
- `agent-core/graphify-out/*` (6 files) modified — generated, no source/config changes
- All other surfaces unchanged (cron definitions, scripts, source files)
- Generated files left untouched; no revert applied

## Status Dimensions

| Dimension | Meaning |
|---|---|
| BLOCK | Evidence shows blockers that must resolve before implementation |
| PASS_WITH_CHANGES | Evidence shows plan is sound but needs corrections |
| NOT_REVIEWED | Provider did not produce a substantive verdict |
