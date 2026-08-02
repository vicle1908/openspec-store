# CHANGELOG

## v1.0.0 (2026-05-19)

### ✅ Spec-Code-Docs Alignment Complete

Full audit and synchronization of specification, codebase, and documentation.
All 7 functional + 5 non-functional requirements met (181 tests, 91.4% coverage).

### Added
- **PDF reporter** via weasyprint — HTML→PDF conversion with embedded styling
- **HTML reporter** — standalone HTML with embedded CSS, responsive design, progress bars
- **Default reports path** — auto-detects workspace root, saves to `tdt/reports/epics/`
- **Version breakdown** section in markdown reports (v53/v54 grouping)
- **Child task detail tables** in every epic section (Key, Summary, Status, Assignee, SP)
- **TaskStatus aliases** (`_missing_` classmethod) for Jira quirk handling
- **`--no-risks` / `--no-resources`** CLI flags
- **`show-config --verbose`** command

### Changed
- CLI: `generate` command wired to full orchestrator pipeline
- CLI: `generate` now returns 3 CLI commands (`generate`, `list-epics`, `show-config`)
- CLI: format flag supports `markdown|json|html|pdf` (was just markdown|json)
- Markdown reporter: 312-line rich output vs 243 (task tables, resource projects, version breakdown)
- Resource table: `total_count` key in utilization dict (was `task_count` mismatch)
- Timeline: `TimelineAnalyzer` now receives `cutoff_date` in constructor
- Report model: `timeline_analysis` field populated from `analyze_all()`
- Links: pipe-delimited garbage cleaned (`split("|")[0]`)

### Fixed
- Resource utilization showing zeros — fixed to use `total_count` key
- Timeline showing "N/A" for all days-remaining — fixed `cutoff_date` propagation
- Action items generic ("Assign task immediately") — now CRITICAL/IMPORTANT/PLANNED labels
- Config test error messages aligned with code
- `_find_workspace_root()` uses `.agents/` marker (was `.git`)

### Documentation
- spec.md: Status → ✅ Implemented, actual package layout, 4 output formats, v1.0.0
- design.md: Actual architecture diagram, real file structure, key decisions section
- INDEX.md: Feature matrix, implementation stats, test counts updated
- SUMMARY.md: Implementation summary with live Jira data
- README.md: Status, tests, format list, reports path, spec alignment table

---

## v0.5.0 (2026-05-18)

### Added
- EpicCollector using atlassian-python-api SDK
- 9 risk detection rules
- Resource utilization tracking
- Timeline analysis with days-remaining
- Status-weighted completion (Done=100, In Progress=70, etc.)
- Markdown reporter via jinja2
- JSON reporter via Pydantic serialization
- CLI with typer + rich (generate, list-epics, show-config)
- TTL caching (cachetools)
- Config from env + ~/.tdt/.env
- Full test suite 177/177, 97% coverage
- GLB IPO analysis section in deep analysis report

### Changed
- Switched from jira_mgmt wrapper to atlassian-python-api SDK directly
- Analyzers use constructor injection (not global state)
- TaskStatus uses StrEnum with _missing_ alias handler
- Flat package layout (epic_report/ not src/epic_report/)

---

## v0.1.0 (2026-05-17)

### Added
- Project scaffold: pyproject.toml, uv.lock, ruff config
- Pydantic data models (TaskStatus, Task, Epic, Risk, Report)
- Basic CLI stubs
- Spec, design, and proposal documents
