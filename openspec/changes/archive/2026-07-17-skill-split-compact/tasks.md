# Tasks: Skill Split Implementation

## Completed Tasks

### Phase 1: Analysis & Planning ✅
- [x] Identify all SKILL.md files exceeding 500 lines
- [x] Catalog existing reference files per skill
- [x] Determine content split strategy (what stays in SKILL.md, what moves)
- [x] Validate YAML frontmatter requirements for each skill

### Phase 2: acli Split ✅
- [x] Reduce SKILL.md from 621 to 214 lines
- [x] Create 6 reference files
- [x] Add Critical Rules / Hard Rules section
- [x] Add Quick Reference table
- [x] Validate all cross-references

### Phase 3: scraper-builder Split ✅
- [x] Reduce SKILL.md from 708 to 229 lines (after Quick Reference addition)
- [x] Create 2 new reference files (extraction-patterns.md, scraper-template.md)
- [x] Link 4 existing reference files
- [x] Add decision tree for API selection
- [x] Validate all cross-references

### Phase 4: kanban-board-from-spreadsheet Split ✅
- [x] Reduce SKILL.md from 1,446 to 210 lines
- [x] Link 6 existing reference files
- [x] Add Hard Rules section
- [x] Add workflow overview diagram
- [x] Validate all cross-references

### Phase 5: gitnexus-cli-usage Split ✅
- [x] Reduce SKILL.md from 736 to 137 lines
- [x] Create 2 new reference files (commands.md, workflows.md)
- [x] Add UID format table
- [x] Add Common Pitfalls table (Wrong vs Right)
- [x] Validate all cross-references

### Phase 6: jira-integration Split ✅
- [x] Reduce SKILL.md from 743 to 209 lines
- [x] Create 5 new reference files
- [x] Add Hard Rules section
- [x] Add Smart Commits Quick Reference
- [x] Add Branch Naming conventions
- [x] Validate all cross-references

### Phase 7: gitlab-glab Split ✅
- [x] Reduce SKILL.md from 704 to 253 lines
- [x] Link 3 existing reference files
- [x] Add Critical Rules section
- [x] Add Decision Trees (3 trees)
- [x] Add Multi-Agent Identity Note
- [x] Validate all cross-references

### Phase 8: Verification ✅
- [x] All 6 SKILL.md files under 500 lines (max: 253, min: 137)
- [x] All 28 reference files exist and are non-empty
- [x] All YAML frontmatter valid
- [x] No broken cross-references within split skills
- [x] Content preserved (no data loss)
- [x] Openspec spec.md created

## Results Summary

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Total SKILL.md lines | 4,958 | 1,261 | 75% |
| Reference files | 22 (pre-existing) | 28 (6 new) | +6 |
| Skills with valid frontmatter | 4/6 | 6/6 | +2 |
| Skills with Critical Rules | 2/6 | 6/6 | +4 |

### Phase 9: Bug Fixes & Deduplication ✅
- [x] scraper-builder: Add missing Quick Reference table
- [x] scraper-builder: Remove 6 duplicate reference links (plain text in phases, links in Reference Files section)
- [x] kanban-board-from-spreadsheet: Fix broken openspec archive links (`../../openspec/` -> `../../../openspec/`)
- [x] kanban-board-from-spreadsheet: Remove 20 duplicate reference links
- [x] jira-integration: Remove 11 duplicate reference links
- [x] acli: Add Critical Rules section before Team Setup
- [x] Final verification: 6/6 PASS, 0 issues, 0 duplicates, 0 broken links

## Final Verification (Post-Bug-Fix)

| Skill | Lines | Refs | Dups | Issues |
|-------|-------|------|------|--------|
| acli | 223 | 6 | 0 | 0 |
| scraper-builder | 229 | 6 | 0 | 0 |
| kanban-board-from-spreadsheet | 210 | 6 | 0 | 0 |
| gitnexus-cli-usage | 137 | 2 | 0 | 0 |
| jira-integration | 209 | 5 | 0 | 0 |
| gitlab-glab | 253 | 3 | 0 | 0 |
| **TOTAL** | **1,261** | **28** | **0** | **0** |
