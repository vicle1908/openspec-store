# Design: Skill Split Architecture

## Progressive Disclosure Pattern

```
SKILL.md (overview, <500 lines)
├── YAML Frontmatter (name, description, compatibility, metadata)
├── Critical Rules / Hard Rules (non-negotiable constraints)
├── Quick Reference Table (command -> reference file mapping)
├── Workflow Overview (ASCII diagram or table)
├── Key Decision Trees (when to use X vs Y)
├── Known Limitations & Workarounds
└── Links to Reference Files
    └── references/*.md (detailed commands, examples, troubleshooting)
```

## Reference File Organization

Each skill's references/ directory is organized by **topic**, not by chronological creation:

### acli/references/
- `jira-workitem-commands.md` — Issue CRUD, transitions, assignments, comments
- `sprint-commands.md` — Sprint lifecycle (create, start, complete, list items)
- `board-filter-field-commands.md` — Board operations, filter management, custom fields
- `project-admin-commands.md` — Project CRUD, user management, permissions
- `confluence-and-other-commands.md` — Confluence spaces/pages, Rovo Dev, feedback
- `troubleshooting.md` — Auth errors, JQL syntax, bulk failures, debugging

### scraper-builder/references/
- `site-analysis-guide.md` — Pre-scraping reconnaissance methodology
- `extraction-patterns.md` — 4 approaches (Unlocker+BS4, Unlocker+API, Browser+Playwright, Infinite Scroll)
- `pagination-patterns.md` — Cursor-based, page-number, infinite scroll, load-more
- `scraper-template.md` — Production-ready templates (single, concurrent, browser)
- `concurrency-guide.md` — ThreadPoolExecutor, asyncio, rate limiting, error handling
- `supported-domains.md` — Domain-specific selectors and quirks

### kanban-board-from-spreadsheet/references/
- `sprint-workflow.md` — 8-step pipeline from Sheets to Jira
- `agile-metrics.md` — WIP, throughput, cycle time, blocker detection, CFD
- `board-config.md` — Swimlanes, card colors, WIP limits, quick filters
- `acli-integration.md` — CLI command reference for this workflow
- `gws-integration.md` — Google Workspace CLI patterns
- `spreadsheet-template.md` — Column structure and gws read commands

### gitnexus-cli-usage/references/
- `commands.md` — Full reference for all 8 commands with jq parsing
- `workflows.md` — Real-world workflow examples and troubleshooting

### jira-integration/references/
- `smart-commits.md` — Full Smart Commit syntax and examples
- `branch-naming.md` — Conventions and validation rules
- `workflows.md` — Issue-driven, hotfix, daily standup patterns
- `metrics.md` — GitLab + Jira + Agile metrics definitions
- `troubleshooting.md` — Link failures, integration errors, Smart Commit issues

### gitlab-glab/references/
- `cheatsheet.md` — Quick command reference (pre-existing)
- `self-hosted.md` — Self-hosted GitLab specifics (pre-existing)
- `api-examples.md` — REST API examples (pre-existing)

## Cross-Skill Dependencies

```
gitnexus impact analysis → gitlab-glab MR creation → jira-integration Smart Commits
scraper-builder → concurrency-guide → kanban-board-from-spreadsheet (batch Sheets updates)
acli → kanban-board-from-spreadsheet (Jira filter/board operations)
```
