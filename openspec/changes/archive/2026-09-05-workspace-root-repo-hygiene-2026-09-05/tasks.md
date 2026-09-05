## 1. Normalize root repo hygiene

- [x] 1.1 Ensure `wiki-mcp-server` is a local Git repository with a standard Python `.gitignore` including `.claude/`, and verify the working tree is clean. Verify with: `git -C wiki-mcp-server status --short` shows no changes.
- [x] 1.2 Append `.claude/` ignore coverage to `ntu-keynote/.gitignore` and `workspace-python-template/.gitignore`, commit in each repo, and verify clean status. Verify with: `git -C ntu-keynote status --short` and `git -C workspace-python-template status --short` show no changes.
- [x] 1.3 Retain reviewed root docs/evidence/bundle items (no deletions) and document ownership/retention decisions in workspace documentation. Verify with: docs update committed and no deleted project/evidence files.
