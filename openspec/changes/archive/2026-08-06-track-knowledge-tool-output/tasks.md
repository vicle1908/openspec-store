# track-knowledge-tool-output — Tasks

## 1. Update .gitignore in all repos

- [x] 1.1 Replace `graphify-out/` with selective ignore pattern in all 17 repos (cache/, .graphify_*, needs_update, .graphify_root, 20*/)
- [x] 1.2 Add `.gitnexus/` to .gitignore in repos that are missing it (16 repos)
- [x] 1.3 Remove duplicate `graphify-out/` entry in jira-kanban-from-spreadsheet
- [x] 1.4 Verify .gitignore allows graph.json, GRAPH_REPORT.md, graph.html, manifest.json, .graphify_labels.json
- [x] 1.5 Verify .gitignore blocks cache/, .graphify_*, .gitnexus/, 20*/

## 2. Commit graphify-out/ in all repos

- [x] 2.1 Stage and commit graphify-out/ in all 17 repos (excluding cache/, .graphify_*, 20*/)
- [x] 2.2 Verify graph.json is tracked in each repo
- [x] 2.3 Verify cache/ and internal files are NOT tracked
- [x] 2.4 Verify date-stamped subdirs (20*/) are NOT tracked

## 3. Verify agent access

- [x] 3.1 Test: verify graphify query works without rebuild on tracked graphify-out/
- [x] 3.2 Test: verify graphify-out/ survives git operations (checkout, merge)
- [x] 3.3 Test: verify merge driver works for concurrent graphify-out/ changes

## 4. Update documentation

- [x] 4.1 Update workspace AGENTS.md graphify section to note graphify-out/ is tracked
- [x] 4.2 Update graphify skill to note graphify-out/ is committed
- [x] 4.3 Update workspace-knowledge-tools skill

## 5. Final verification

- [x] 5.1 Verify all 17 repos have graphify-out/ tracked
- [x] 5.2 Verify no internal files leaked into git
- [x] 5.3 Verify .gitnexus/ still gitignored in all repos
- [x] 5.4 Verify wiki/ still tracked
