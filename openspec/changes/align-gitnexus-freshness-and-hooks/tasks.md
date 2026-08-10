# align-gitnexus-freshness-and-hooks — Tasks

## 1. Reindex stale repositories (14 repos)

- [x] 1.1 Acquire lock: `shlock -f ~/.hermes/locks/gitnexus-reindex.lock || { echo "lock held"; exit 1; }`
- [x] 1.2 Reindex ai-harness-skills: `cd ~/Developer/ai-harness-skills && gitnexus analyze --index-only --skip-agents-md --skip-skills`
- [x] 1.3 Reindex ai-review
- [x] 1.4 Reindex browser-cli
- [x] 1.5 Reindex code-daily-scan
- [x] 1.6 Reindex jira-daily-reports
- [x] 1.7 Reindex jira-epic-report
- [x] 1.8 Reindex jira-kanban-from-spreadsheet
- [x] 1.9 Reindex jira-skill
- [x] 1.10 Reindex mcp-router
- [x] 1.11 Reindex ops-automation-suite
- [x] 1.12 Reindex tdt-core
- [x] 1.13 Reindex tdt-observability
- [x] 1.14 Reindex tdt-sheets
- [x] 1.15 Reindex webhook-receiver
- [x] 1.16 Release lock
- [x] 1.17 Verify: `gitnexus status` in all 18 repos — all should show "up to date"

## 2. Fix pre-commit hook performance

- [x] 2.1 Wrap detect-changes call in `scripts/knowledge-pre-commit.sh` with `timeout 10` (NOT 5 — ONNX init needs more headroom)
- [x] 2.2 Keep hook advisory-only: `(cd "$root" && timeout 10 gitnexus detect-changes --scope staged --repo "$root") 2>&1 || exit 0`
- [x] 2.3 Capture failure output to stderr for diagnostics; exit 0 always (never block commit)
- [x] 2.4 Test hook with a staged commit in go-microservices — should complete in <10s or exit cleanly
- [x] 2.5 If Illegal instruction persists, document as known arm64 ONNX issue; do not attempt to fix the underlying native addon

## 3. Update cron freshness check

- [x] 3.1 Update `weekly-graphify-freshness` cron prompt to report two independent freshness fields:
  - `graphify_artifact_fresh`: `graphify-out/graph.json` exists per repo (content-based)
  - `gitnexus_index_fresh`: `gitnexus status` per repo (commit-hash comparison)
- [x] 3.2 Add lock check: if `~/.hermes/locks/graphify-build.lock` or `~/.hermes/locks/gitnexus-reindex.lock` exists, report "skipped (lock held)" and exit non-zero
- [x] 3.3 Add partial-result policy: if some repos fail freshness check, report partial results and exit non-zero (never silently swallow failures)
- [x] 3.4 Test the updated prompt with a manual cron run

## 4. Verify all indexes

- [x] 4.1 Run `gitnexus status` in all 18 repos — all should show "up to date"
- [x] 4.2 Test `gitnexus detect-changes --repo $(pwd) --scope staged` in 3 repos — no crash, bounded runtime
- [x] 4.3 Test `gitnexus query "webhook"` in webhook-receiver — should return results
- [x] 4.4 Test `gitnexus context DedupeStore` in webhook-receiver — should return 360° view
- [x] 4.5 Test `gitnexus impact DedupeStore` in webhook-receiver — should return blast radius

## 5. Archive

- [x] 5.1 No source commits needed (only `.gitnexus/` changes, which are gitignored)
- [x] 5.2 Record evidence: before/after status for all 18 repos, cron prompt diff, hook test output
- [x] 5.3 Archive change and commit store
