# refresh-graphify-upstream — Tasks

## 1. Baseline capture

- [x] 1.1 Record current `graphify --version` and `uv tool list | grep graphify`
- [x] 1.2 Confirm distribution: `graphifyy==0.9.38` is PyPI latest stable (0.10.0 does NOT exist)
- [x] 1.3 Capture per-repo graph statistics (nodes, edges, communities, graph.html size) for all 18 repos
- [x] 1.4 Capture skill file checksums: Hermes (no version field in frontmatter), Pi (`.graphify_version` = 0.9.34)
- [x] 1.5 Snapshot installed skill files for rollback: `~/.hermes/skills/graphify/`, `~/.pi/agent/skills/graphify/`, `~/.claude/skills/graphify/`
- [x] 1.6 Capture representative query results for 3 repos (webhook-receiver, agent-core, go-microservices)
- [x] 1.7 Capture global graph node/edge count
- [x] 1.8 Capture `graph.json` top-level keys and node/edge shape for schema compatibility baseline

## 2. Upgrade

- [x] 2.1 Acquire workspace lock: `shlock -f ~/.hermes/locks/graphify-build.lock || { echo "lock held"; exit 1; }`
- [x] 2.2 Upgrade graphifyy: `uv tool install "graphifyy[all,postgres]"==0.9.38`
- [x] 2.3 Verify `graphify --version` → 0.9.38
- [x] 2.4 Run `graphify install --platform hermes`
- [x] 2.5 Run `graphify install --platform pi`
- [x] 2.6 Run `graphify install --platform claude`
- [x] 2.7 Run `graphify install --platform codex`
- [x] 2.8 Run `graphify install --platform opencode`
- [x] 2.9 Verify Hermes skill updated (timestamp changed; no version field in frontmatter)
- [x] 2.10 Verify Pi `.graphify_version` now reads `0.9.38`

## 3. Schema compatibility check

- [x] 3.1 Compare `graph.json` top-level keys between 0.9.34 baseline and 0.9.38 output
- [x] 3.2 Compare node/edge object shape (keys, nesting)
- [x] 3.3 Document any structural differences
- [x] 3.4 Verify downstream consumers (graph.html, agent skills) still work

## 4. Pilot rebuild (webhook-receiver + go-microservices)

- [x] 4.1 Run `cd ~/Developer/webhook-receiver && graphify update .`
- [x] 4.2 Compare old vs new graph statistics for webhook-receiver
- [x] 4.3 Run `cd ~/Developer/go-microservices && graphify update .`
- [x] 4.4 Compare old vs new graph statistics for go-microservices
- [x] 4.5 Run representative queries and compare results
- [x] 4.6 Review graph diff for unexpected changes
- [x] 4.7 **Decision gate**: proceed to batch or halt. Halt if any repo shows >20% node count drop or broken query results.

## 5. Determinism verification

- [x] 5.1 Run graphify twice on webhook-receiver, diff output — should be identical
- [x] 5.2 If non-deterministic, document the delta and assess noise level

## 6. Batch rebuild (remaining 16 repos)

- [x] 6.1 Rebuild agent-core, agent-docs-sync, agent-harness
- [x] 6.2 Rebuild ai-harness-skills, ai-review, browser-cli
- [x] 6.3 Rebuild code-daily-scan
- [x] 6.4 Rebuild jira-daily-reports, jira-epic-report, jira-kanban-from-spreadsheet
- [x] 6.5 Rebuild jira-skill, mcp-router
- [x] 6.6 Rebuild ops-automation-suite, tdt-core, tdt-observability, tdt-sheets
- [x] 6.7 Verify all 18 repos have fresh graphify-out/graph.json

## 7. Global graph

- [x] 7.1 Remove all entries from global graph
- [x] 7.2 Re-add all 18 repos with `graphify global add`
- [x] 7.3 Verify global graph node/edge count

## 8. Verification

- [x] 8.1 Run representative queries across 5 repos
- [x] 8.2 Run graphify path and explain on 2 repos
- [x] 8.3 Verify graph.html opens correctly for 2 repos
- [x] 8.4 Compare per-repo statistics against baseline thresholds
- [x] 8.5 Verify git hooks still trigger rebuild on commit

## 9. Commit and archive

- [x] 9.1 Commit graphify-out/ in all 18 repos
- [x] 9.2 Verify no internal files leaked into git
- [x] 9.3 Record exact source/artifact commits and retained evidence
- [x] 9.4 Run `openspec validate --all`
- [x] 9.5 Archive change and commit store
