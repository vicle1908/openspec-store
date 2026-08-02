# CLI Interface — Specification

**Capability:** cli-interface


## ADDED Requirements

### Requirement: cli-interface specification applies unchanged

The cli-interface contract documented below SHALL apply unchanged for
this delta. The OpenSpec delta section above is the canonical delta
declaration; the FR-N items and SDK Contract Requirements below are
preserved verbatim from the pre-delta-era authoring of this
specification.

#### Scenario: cli-interface is implemented per the FR-N contract below

The cli-interface is implemented per the FR-N contract below.

---

### FR-2: List Epics Command

**Description:** List Jira epics with summary status.

**Requirements:**
- SHALL accept optional filters:
  - `--project, -p`: Filter by project key
  - `--status, -s`: Filter by epic status
  - `--limit, -l`: Maximum results (default: 50)
- SHALL display results in rich table format
- SHALL include columns: key, summary, status, project, task count, completion%

---

### FR-3: Configuration Management

**Description:** Load and validate runtime configuration.

**Requirements:**
- SHALL read environment variables:
  - `JIRA_BASE_URL` (required)
  - `JIRA_EMAIL` (required)
  - `JIRA_API_TOKEN` (required)
  - `EPIC_REPORT_CACHE_TTL` (default: 300)
  - `EPIC_REPORT_STALENESS_DAYS` (default: 60)
  - `EPIC_REPORT_RATE_LIMIT` (default: 10)
  - `EPIC_REPORT_LOG_LEVEL` (default: INFO)
  - `EPIC_REPORT_OVERLOAD_THRESHOLD` (default: 8)
- SHALL support `.env` file loading via python-dotenv
- SHALL validate required variables at startup
- SHALL display clear error messages for missing configuration

---

### FR-4: Error Handling and User Feedback

**Description:** Provide clear error messages and progress feedback.

**Requirements:**
- SHALL use rich panels for error display
- SHALL distinguish between user errors (invalid epic key) and system errors (API failure)
- SHALL support `--verbose` flag for detailed error traces
- SHALL display spinner during long-running operations
- SHALL use colored output: red for errors, yellow for warnings, green for success

---

### FR-5: Entry Points

**Requirements:**
- SHALL provide `epic-report` CLI entry point via pyproject.toml `[project.scripts]`
- SHALL support `python -m epic_report` as alternative entry point
- SHALL display help text with `--help` flag

---

### Dependencies

- `typer>=0.15.1` - CLI framework
- `rich>=13.9.4` - Terminal formatting
- `python-dotenv>=1.0.1` - Environment loading
- `epic_report.collector` - Data source
- `epic_report.orchestrator` - Report generation

---

### FR-6: Per-Project Thresholds

**Description:** Support per-project configuration overrides via TOML.

**Requirements:**
- SHALL load per-project thresholds from `~/.tdt/epic-report-config.toml`
- SHALL support `[projects.<KEY>]` sections with overridable values:
  - `overload_threshold`: max items per assignee (default: 8)
  - `staleness_days`: days before item flagged stale (default: 60)
  - `risk_cutoff_buffer`: days before cutoff to escalate risk (default: 7)
  - `completion_weights`: dict of status → weight overrides
  - `risk_weights`: dict of risk type → weight overrides
- SHALL fall back to `[defaults]` section when no per-project config exists
- SHALL accept `--config <path>` global option for custom config file location
- SHALL display per-project settings via `show-config --project-config <PROJECT>`

**Example:**
```toml
# ~/.tdt/epic-report-config.toml
[defaults]
overload_threshold = 8
staleness_days = 60

[projects.PDS]
overload_threshold = 10
staleness_days = 45

[projects.AM.completion_weights]
"Develop" = 50
"Deploy in Dev" = 40
```

---

### FR-7: Configuration Display

**Description:** Display current runtime configuration including per-project overrides.

**Requirements:**
- SHALL provide `show-config` command displaying all configuration
- SHALL support `--project-config <PROJECT>` to show per-project overrides
- SHALL support `--verbose` for full configuration details
- SHALL display config file path when non-default config is loaded
- SHALL show Jira credentials masked (***) for security

---

### FR-8: Insights Command

**Description:** Generate per-epic insight reports analyzing comments, changelogs, and activity.

**Requirements:**
- SHALL accept epic keys as positional arguments
- SHALL support options:
  - `--output, -o`: Output directory (default: reports/epics/)
  - `--deep-analysis`: Enable AI agent CLI deep analysis
  - `--agent, -a`: Specify agent CLI to use (codex, claude, kimi, pi)
  - `--multi-agent`: Run ALL available agents in parallel (consensus mode)
  - `--all-tickets`: Analyze every ticket, not just flagged
  - `--batch-size N`: Concurrent agent processes for batch mode (default: 4)
  - `--full`: Convenience flag — enables --deep-analysis + --all-tickets
  - `--verbose`: Enable debug output
- SHALL analyze each epic's child tasks for comments, changelogs, linked issues
- SHALL output per-epic insights markdown (`{KEY}_insights.md`) and JSON (`{KEY}_insights.json`)
- SHALL display summary table with: Epic, Tasks, Comments, Risk Flags, Deep Analysis count
- SHALL run comment/changelog analysis with `ThreadPoolExecutor` (4 workers)
- SHALL generate cross-epic key insight statements

**Example:**
```bash
epic-report insights PDS-81 AM-2054
epic-report insights PDS-81 --deep-analysis --agent codex
```

---

### FR-9: Dashboard Command

**Description:** Generate comprehensive project command center dashboard.

**Requirements:**
- SHALL accept epic keys as positional arguments
- SHALL support options:
  - `--output, -o`: Output file path
  - `--format, -f`: Output format: markdown, html (default: markdown)
  - `--cutoff, -c`: Cut-off date (YYYY-MM-DD)
  - `--no-bugs`: Skip bug collection for faster generation
  - `--verbose`: Enable debug output
- SHALL collect ALL work items: epics → tasks → subtasks → bugs via `WorkItemCollector`
- SHALL generate 6 dashboard sections:
  1. Executive Dashboard — per-project metrics
  2. Complete Activity List — per-epic work tree with indented hierarchy
  3. Sprint Planning — items grouped by sprint with completion %
  4. Progress Tracking — per-epic on/off-track status
  5. Escalation Register — stale, unassigned, resource overload
  6. Bug Radar — per-project bug counts by status
- SHALL auto-create stable `dashboard.md` / `dashboard.html` symlinks in reports directory
- SHALL support 232+ item collections across multiple projects

**Example:**
```bash
epic-report dashboard PDS-81 AM-2054 AM-2025 TJ-1656 TJ-1683 --cutoff 2026-05-25
epic-report dashboard PDS-81 AM-2054 --format html
```

