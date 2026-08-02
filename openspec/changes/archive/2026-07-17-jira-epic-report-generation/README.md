# Jira Epic Report Generation

> Automated Jira epic analysis and report generation with risk identification and actionable recommendations

**Status:** ✅ Implemented
**Version:** 0.1.0
**Tests:** 181/181 passing, 92% coverage
**Last Updated:** 2026-05-18

---

## Quick Start

```bash
# Generate report for specific epics (auto-saved to tdt/reports/epics/)
epic-report generate PDS-81 AM-2054 AM-2025

# Markdown, JSON, HTML, PDF formats
epic-report generate PDS-81 --format html
epic-report generate PDS-81 --format pdf

# With cutoff date and risk analysis
epic-report generate PDS-81 AM-2054 --cutoff 2026-05-25 --format markdown

# List epics
epic-report list-epics --project PDS

# Show configuration
epic-report show-config --verbose
```

---

## What is This?

An automated system that:

- 📊 Analyzes Jira epics and their child tasks
- 🔍 Identifies 8+ risk types (unassigned, blocked, timeline, resource overload, cross-project)
- 👥 Tracks resource utilization across projects
- 📝 Generates comprehensive reports in Markdown, JSON, HTML, and PDF
- 💡 Provides prioritized, actionable recommendations
- 📁 Auto-saves reports to **`tdt/reports/epics/`** by default

---

## Features

### Risk Analysis
- ⚠️ Unassigned tasks near deadlines
- 👥 Resource overload detection (>5 tasks per person)
- 📅 Timeline risk assessment
- 🚧 Blocked tasks and dependencies
- 📋 Missing information detection
- 🔀 Cross-project conflict detection

### Status Tracking
- 📊 Task status breakdown per epic
- 🎯 Weighted completion percentage
- 📈 Overall completion metrics
- 🗓️ Sprint allocation visibility
- 🏢 Cross-project analysis

### Report Formats
- 📝 **Markdown** (GitHub/GitLab compatible, jinja2 templates)
- 📄 **JSON** (machine-readable, Pydantic serialization)
- 🌐 **HTML** (standalone, embedded CSS, responsive design)
- 📕 **PDF** (via weasyprint, professional styling)

### CLI Interface
- `generate` — Full epic report generation
- `list-epics` — List epics with filters
- `show-config` — Display current configuration
- Rich terminal output with progress indicators

---

## Installation

### Prerequisites
- Python 3.12+
- Jira Cloud credentials

```bash
cd openspec/changes/jira-epic-report-generation
uv sync
```

### Jira Credentials
Set in `~/.tdt/.env`:
```bash
JIRA_BASE_URL=https://psplit.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

---

## Usage

### Basic Usage

```bash
# Single epic
epic-report generate PDS-81

# Multiple epics
epic-report generate PDS-81 AM-2054 AM-2025 TJ-1656 TJ-1683

# Save to specific file
epic-report generate PDS-81 --output my_report.md
```

### Report Formats

```bash
# Markdown (default)
epic-report generate PDS-81 --format markdown

# JSON for automation
epic-report generate PDS-81 --format json

# HTML with embedded CSS
epic-report generate PDS-81 --format html

# PDF (requires brew install glib cairo pango)
epic-report generate PDS-81 --format pdf
```

### Options

```
--output, -o    Output file path (auto: tdt/reports/epics/{project}_{date}_epic_report.{ext})
--format, -f    Output format: markdown, json, html, pdf (default: markdown)
--cutoff, -c    Cut-off date (YYYY-MM-DD) for timeline analysis
--no-risks      Disable risk analysis
--no-resources  Disable resource utilization analysis
--verbose       Verbose output with debug info
```

### Default Output Path

Reports are automatically saved to `tdt/reports/epics/` with the naming pattern:
```
{project}_{date}_epic_report.{ext}
```

Example: `PDS_2026-05-18_epic_report.md`

---

## Architecture

```
CLI (typer) → EpicCollector → Risk/Resource/Timeline Analyzers → Report → MarkdownReporter/JSONReporter/HTML/PDF
```

Built with: Python 3.12+, typer, rich, pydantic, jinja2, weasyprint
SDK: atlassian-python-api (Jira Cloud)
Config: ~/.tdt/.env auto-loaded

---

## Testing

```bash
# Full test suite
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=epic_report --cov-report=term-missing

# Specific module
uv run pytest tests/test_models.py -v
```

---

## Spec vs Code Alignment

| Requirement | Status |
|------------|--------|
| FR-1: Epic data collection | ✅ |
| FR-2: Risk analysis (8 types) | ✅ |
| FR-3: Status aggregation | ✅ |
| FR-4.1: Markdown report | ✅ |
| FR-4.2: JSON output | ✅ |
| FR-4.3: HTML report | ✅ (Phase 2 complete) |
| FR-4.4: Output destinations (stdout, file) | ✅ |
| FR-5: CLI interface | ✅ |
| FR-6: Configuration (env + TOML) | ✅ |
| NFR-1: Performance (<30s for 10 epics) | ✅ |
| NFR-2: Test coverage >80% | ✅ (92%) |
| PDF output | ✅ (via weasyprint) |
| Default reports path | ✅ (tdt/reports/epics/) |

---

*Built with uv + typer + rich + pydantic + jinja2 | atlassian-python-api SDK*
