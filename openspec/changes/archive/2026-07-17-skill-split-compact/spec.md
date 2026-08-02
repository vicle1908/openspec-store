# Skill Split — Compact SKILL.md Bodies

**Version:** 1.0
**Created:** 2026-05-18
**Status:** Approved
**Type:** Documentation Refactoring

---

## Overview

Split 6 oversized `.agents/skills/` SKILL.md files (bodies exceeding 500 lines) into compact SKILL.md + reference file pairs, complying with the Agent Skills spec's progressive disclosure pattern. SKILL.md bodies contain overview, critical rules, quick reference, and links to detailed reference files.

---

## Objectives

1. Reduce all SKILL.md bodies under 500 lines while preserving all technical content
2. Apply progressive disclosure: overview + rules in SKILL.md, details in references/
3. Maintain valid YAML frontmatter on all skill files
4. Preserve all cross-skill references and links
5. Verify broken references and fix pre-existing issues

---

## Skills Processed

| Skill | Original Lines | New Lines | Reference Files | Status |
|-------|---------------|-----------|-----------------|--------|
| acli | 621 | 223 | 6 | Complete (Critical Rules added) |
| scraper-builder | 708 | 229 | 6 | Complete (Quick Reference added) |
| kanban-board-from-spreadsheet | 1446 | 210 | 6 | Complete |
| gitnexus-cli-usage | 736 | 137 | 2 | Complete |
| jira-integration | 743 | 209 | 5 | Complete |
| gitlab-glab | 704 | 253 | 3 | Complete |

**Total:** 1,261 lines (down from 4,958) in SKILL.md files; 5,794 lines in reference files.

---

## Functional Requirements

### FR1: YAML Frontmatter

**Priority:** Critical
**Description:** Every SKILL.md must have valid YAML frontmatter with `name`, `description`, and optionally `license`, `compatibility`, `metadata`, `when_to_use`, `allowed-tools`.

**Acceptance Criteria:**
- [x] All 6 SKILL.md files have valid YAML frontmatter
- [x] `name` field matches directory name
- [x] `description` field covers trigger keywords and use cases
- [x] Frontmatter parses without errors

### FR2: SKILL.md Body Under 500 Lines

**Priority:** Critical
**Description:** SKILL.md body (after frontmatter `---` delimiter) must be under 500 lines.

**Acceptance Criteria:**
- [x] acli: 223 lines (Critical Rules added)
- [x] scraper-builder: 229 lines (Quick Reference added)
- [x] kanban-board-from-spreadsheet: 210 lines
- [x] gitnexus-cli-usage: 137 lines
- [x] jira-integration: 209 lines
- [x] gitlab-glab: 253 lines

### FR3: Progressive Disclosure Pattern

**Priority:** Critical
**Description:** SKILL.md must contain: Critical/Hard Rules, Quick Reference table, Workflow Overview, Key Decision Trees, and links to reference files. All detailed commands, full examples, and troubleshooting move to `references/*.md`.

**Acceptance Criteria:**
- [x] Each SKILL.md has Critical Rules section (or Hard Rules)
- [x] Each SKILL.md has Quick Reference table
- [x] Each SKILL.md links to all its reference files
- [x] Reference files contain detailed command syntax, examples, and troubleshooting

### FR4: Cross-Reference Integrity

**Priority:** Important
**Description:** All relative links in SKILL.md files must resolve to existing files.

**Acceptance Criteria:**
- [x] All 28 reference files exist and are non-empty
- [x] All `references/*.md` links resolve correctly
- [x] All `../other-skill/SKILL.md` links resolve correctly
- [ ] Pre-existing broken links noted but out of scope

### FR5: Content Preservation

**Priority:** Critical
**Description:** No technical content lost during split. All commands, examples, configuration values, and decision trees must be preserved either in SKILL.md or reference files.

**Acceptance Criteria:**
- [x] All acli commands preserved in references/
- [x] All Bright Data API patterns preserved in references/
- [x] All GitNexus CLI commands and UID formats preserved in references/
- [x] All Jira-GitLab integration patterns preserved in references/
- [x] All glab CLI commands and decision trees preserved in references/
- [x] All Kanban board workflow steps preserved in references/

---

## Non-Functional Requirements

### NFR1: Agent Skills Spec Compliance
- Valid YAML frontmatter on all SKILL.md files
- Progressive disclosure pattern applied
- No content duplication between SKILL.md and references/

### NFR2: Readability
- SKILL.md should be scannable in under 2 minutes
- Reference files comprehensive enough to use without SKILL.md context
- Consistent formatting across all 6 skills

### NFR3: Maintainability
- Reference files organized by topic (not by chronological creation)
- Cross-skill dependencies documented (e.g., gitnexus -> gitlab-glab for pre-MR analysis)

---

## Reference Files Created

### acli (6 reference files)
- `references/jira-workitem-commands.md` — 30+ work item commands
- `references/sprint-commands.md` — Sprint lifecycle commands
- `references/board-filter-field-commands.md` — Board, filter, field commands
- `references/project-admin-commands.md` — Project and admin commands
- `references/confluence-and-other-commands.md` — Confluence + Rovo Dev
- `references/troubleshooting.md` — Error handling and debugging

### scraper-builder (6 reference files)
- `references/site-analysis-guide.md` — Pre-scraping reconnaissance
- `references/extraction-patterns.md` — 4 extraction approaches (NEW)
- `references/pagination-patterns.md` — Pagination handling
- `references/scraper-template.md` — Production templates (NEW)
- `references/concurrency-guide.md` — 50+ URL concurrent scraping
- `references/supported-domains.md` — Domain-specific notes

### kanban-board-from-spreadsheet (6 reference files)
- `references/sprint-workflow.md` — 8-step pipeline
- `references/agile-metrics.md` — WIP, throughput, CFD metrics
- `references/board-config.md` — Board display settings
- `references/acli-integration.md` — CLI command reference
- `references/gws-integration.md` — Google Workspace CLI patterns
- `references/spreadsheet-template.md` — Column structure

### gitnexus-cli-usage (2 reference files)
- `references/commands.md` — Full command reference (NEW)
- `references/workflows.md` — Workflow examples and troubleshooting (NEW)

### jira-integration (5 reference files)
- `references/smart-commits.md` — Smart Commit syntax (NEW)
- `references/branch-naming.md` — Branch naming conventions (NEW)
- `references/workflows.md` — Workflow patterns (NEW)
- `references/metrics.md` — Agile metrics definitions (NEW)
- `references/troubleshooting.md` — Integration error resolution (NEW)

### gitlab-glab (3 existing reference files)
- `references/cheatsheet.md` — Quick command reference
- `references/self-hosted.md` — Self-hosted GitLab specifics
- `references/api-examples.md` — REST API examples

---

### Phase 9: Bug Fixes & Deduplication
- [x] scraper-builder: Added missing Quick Reference table
- [x] scraper-builder: Removed 6 duplicate reference links (plain text in phase sections)
- [x] kanban-board-from-spreadsheet: Fixed broken openspec archive links (relative path correction)
- [x] kanban-board-from-spreadsheet: Removed 20 duplicate reference links
- [x] jira-integration: Removed 11 duplicate reference links
- [x] acli: Added Critical Rules section
- [x] Final verification: 0 duplicates, 0 broken links across all 6 skills

## Constraints

- Must follow Agent Skills spec format
- Must not modify reference files that pre-exist (only create new ones)
- Must preserve all technical accuracy
- Documentation must be text-based (Markdown)

---

## Success Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| SKILL.md files under 500 lines | 6/6 | 6/6 |
| Reference files created | 28 | 28 |
| Broken cross-references in split skills | 0 | 0 |
| YAML frontmatter valid | 6/6 | 6/6 |
| Content preserved (no data loss) | 100% | 100% |
| Total SKILL.md line reduction | >60% | 75% (4958 -> 1261) |

---

## Approval

**Specification Status:** Approved
**Approved By:** Project Lead
**Approval Date:** 2026-05-18

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-18 | ekhanhvinh | Initial specification |
