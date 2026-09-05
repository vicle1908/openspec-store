## 1. Inventory
- [ ] 1.1 Inventory `.gitnexus/` and `graphify-out/` for all 20 repositories in `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`; write `evidence/index-inventory.json` with size and path only.
- [ ] 1.2 Compare GitNexus indexed revision and Graphify manifest source revision to each repository HEAD using `knowledge-status.sh --json` and `refresh-knowledge-indexes.sh --check`; classify exact-HEAD, stale, missing, or unknown.
## 2. Retention
- [ ] 2.1 Identify duplicate or historical generated artifacts with repository, tool owner, recovery path, and retention classification; do not treat stale as deletable.
- [ ] 2.2 Write `evidence/index-retention-plan.md` with review-only pruning recommendations and explicit no-deletion scope; verify no index files change.
## 3. Finalize
- [ ] 3.1 Validate, archive, and commit evidence.
