# align-gitnexus-freshness-and-hooks — Tasks

## 1. Reindex stale repositories (14 repos)

- [ ] 1.1 Reindex ai-harness-skills: `cd ~/Developer/ai-harness-skills && gitnexus analyze --index-only --skip-agents-md --skip-skills`
- [ ] 1.2 Reindex ai-review
- [ ] 1.3 Reindex browser-cli
- [ ] 1.4 Reindex code-daily-scan
- [ ] 1.5 Reindex jira-daily-reports
- [ ] 1.6 Reindex jira-epic-report
- [ ] 1.7 Reindex jira-kanban-from-spreadsheet
- [ ] 1.8 Reindex jira-skill
- [ ] 1.9 Reindex mcp-router
- [ ] 1.10 Reindex ops-automation-suite
- [ ] 1.11 Reindex tdt-core
- [ ] 1.12 Reindex tdt-observability
- [ ] 1.13 Reindex tdt-sheets
- [ ] 1.14 Reindex webhook-receiver
- [ ] 1.15 Run `gitnexus status` in all 18 repos — all should show "up to date"

## 2. Fix pre-commit hook performance

- [ ] 2.1 Add `timeout 5` to detect-changes call in go-microservices hook
- [ ] 2.2 Verify existing `--repo "$root"` logic is preserved (do NOT change to basename)
- [ ] 2.3 Test hook with a staged commit in go-microservices — should complete in <5s
- [ ] 2.4 If Illegal instruction persists, investigate arch context issue

## 3. Update cron freshness check

- [ ] 3.1 Update weekly-graphify-freshness cron prompt to use `gitnexus status` for GitNexus freshness
- [ ] 3.2 Test the updated prompt with a manual cron run

## 4. Verify all indexes

- [ ] 4.1 Run `gitnexus status` in all 18 repos — all should show "up to date"
- [ ] 4.2 Test `gitnexus detect-changes --repo $(pwd) --scope staged` in 3 repos — no crash
- [ ] 4.3 Test `gitnexus query "webhook"` in webhook-receiver — should return results
- [ ] 4.4 Test `gitnexus context DedupeStore` in webhook-receiver — should return 360° view
- [ ] 4.5 Test `gitnexus impact DedupeStore` in webhook-receiver — should return blast radius

## 5. Archive

- [ ] 5.1 No source commits needed (only `.gitnexus/` changes, which are gitignored)
- [ ] 5.2 Archive change and commit store
