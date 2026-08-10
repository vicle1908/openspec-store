# refresh-graphify-upstream — Tasks

## 1. Baseline capture

- [ ] 1.1 Record current `graphify --version` and uv tool metadata
- [ ] 1.2 Capture per-repo graph statistics (nodes, edges, communities, graph.html size) for all 18 repos
- [ ] 1.3 Capture skill file checksums for Hermes and Pi
- [ ] 1.4 Capture representative query results for 3 repos (webhook-receiver, agent-core, go-microservices)
- [ ] 1.5 Capture global graph node/edge count
- [ ] 1.6 Capture `graph.json` top-level keys and node/edge shape for schema compatibility baseline

## 2. Upgrade

- [ ] 2.1 Upgrade graphifyy: `uv tool install graphifyy[all,postgres]==0.9.38`
- [ ] 2.2 Verify `graphify --version` → 0.9.38
- [ ] 2.3 Run `graphify install --platform hermes`
- [ ] 2.4 Run `graphify install --platform pi`
- [ ] 2.5 Run `graphify install --platform claude`
- [ ] 2.6 Run `graphify install --platform codex`
- [ ] 2.7 Run `graphify install --platform opencode`
- [ ] 2.8 Verify Hermes skill file updated (timestamp, version reference)
- [ ] 2.9 Verify Pi skill file updated

## 3. Schema compatibility check

- [ ] 3.1 Compare `graph.json` top-level keys between 0.9.34 baseline and 0.9.38 output
- [ ] 3.2 Compare node/edge object shape (keys, nesting)
- [ ] 3.3 Document any structural differences
- [ ] 3.4 Verify downstream consumers (graph.html, agent skills) still work

## 4. Pilot rebuild (webhook-receiver + go-microservices)

- [ ] 4.1 Run `cd ~/Developer/webhook-receiver && graphify update .`
- [ ] 4.2 Compare old vs new graph statistics for webhook-receiver
- [ ] 4.3 Run `cd ~/Developer/go-microservices && graphify update .`
- [ ] 4.4 Compare old vs new graph statistics for go-microservices
- [ ] 4.5 Run representative queries and compare results
- [ ] 4.6 Review graph diff for unexpected changes
- [ ] 4.7 Decision gate: proceed to batch or halt

## 5. Determinism verification

- [ ] 5.1 Run graphify twice on webhook-receiver, diff output — should be identical
- [ ] 5.2 If non-deterministic, document the delta and assess noise level

## 6. Batch rebuild (remaining 16 repos)

- [ ] 6.1 Rebuild agent-core, agent-docs-sync, agent-harness
- [ ] 6.2 Rebuild ai-harness-skills, ai-review, browser-cli
- [ ] 6.3 Rebuild code-daily-scan
- [ ] 6.4 Rebuild jira-daily-reports, jira-epic-report, jira-kanban-from-spreadsheet
- [ ] 6.5 Rebuild jira-skill, mcp-router
- [ ] 6.6 Rebuild ops-automation-suite, tdt-core, tdt-observability, tdt-sheets
- [ ] 6.7 Verify all 18 repos have fresh graphify-out/graph.json

## 7. Global graph

- [ ] 7.1 Remove all entries from global graph
- [ ] 7.2 Re-add all 18 repos with `graphify global add`
- [ ] 7.3 Verify global graph node/edge count

## 8. Verification

- [ ] 8.1 Run representative queries across 5 repos
- [ ] 8.2 Run graphify path and explain on 2 repos
- [ ] 8.3 Verify graph.html opens correctly for 2 repos
- [ ] 8.4 Compare per-repo statistics against baseline thresholds
- [ ] 8.5 Verify git hooks still trigger rebuild on commit

## 9. Commit and archive

- [ ] 9.1 Commit graphify-out/ in all 18 repos
- [ ] 9.2 Verify no internal files leaked into git
- [ ] 9.3 Run `openspec validate --all`
- [ ] 9.4 Archive change and commit store
