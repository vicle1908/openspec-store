# Jira Kanban From Spreadsheet (Python) - Specification

**Status:** Implemented (All Phases)  
**Version:** 0.1.0  
**Date:** 2026-05-22

---

## 1. Overview

Python CLI that syncs a Google Sheets sprint planning tab to a Jira filter, which feeds an existing Kanban board. Replaces bash skill at `.agents/skills/kanban-board-from-spreadsheet/`.

---

## 2. Functional Requirements

### FR1: Spreadsheet Reading via gspread

**Priority:** Critical  
**Status:** Pending

**Description:** Read sprint planning data from Google Sheets using `gspread` library with service account authentication.

**Acceptance Criteria:**
- [ ] `SheetsReader.read_spreadsheet(spreadsheet_id, sheet_name)` returns `SheetData`
- [ ] Auto-discover sheet name from spreadsheet title if `sheet_name` not provided
- [ ] Service account JSON at `~/.tdt/google-service-account.json` (configurable)
- [ ] Env var `GOOGLE_SERVICE_ACCOUNT_PATH` for override
- [ ] Clear error if credentials missing or invalid
- [ ] Tests: mock gspread, verify auth path

**Verification:**
```bash
uv run kbs preview --spreadsheet 1WQE0DOPVgRVdBraMVJWO9BfuPtwwmQD6aCziVMLliSA
# Expected: print spreadsheet metadata + first 5 rows
```

### FR2: Spreadsheet Parsing with Pydantic Validation

**Priority:** Critical  
**Status:** Pending

**Description:** Parse rows into typed `SprintRow` models with validation.

**Acceptance Criteria:**
- [ ] `SprintRow` Pydantic model with all 16 columns from sheet
- [ ] Issue key validation: regex `^[A-Z][A-Z0-9]+-\d+$`
- [ ] Case-insensitive column header matching (Team/team/TEAM all work)
- [ ] Skip rows with invalid issue keys, warn but don't fail
- [ ] Tests: valid row, invalid issue key, missing columns

**Verification:**
```bash
uv run kbs validate --spreadsheet <id>
# Expected: "65 valid rows, 2 skipped (invalid keys)"
```

### FR3: Cross-Project JQL Generation

**Priority:** Critical  
**Status:** Pending

**Description:** Generate JQL spanning all unique projects from issue keys.

**Acceptance Criteria:**
- [ ] `build_cross_project_jql(issue_keys: list[str]) -> str`
- [ ] Output format: `key in (KEY1, KEY2, ...)` for ≤50 keys
- [ ] For >50 keys: `project in (P1, P2) AND key in (...)` (groups by project)
- [ ] Deduplicates input keys
- [ ] Sorts deterministically (for diff-friendly output)
- [ ] Tests: ≤50 keys, >50 keys, duplicates, empty input

### FR4: Filter Update

**Priority:** Critical  
**Status:** Pending

**Description:** Update an existing Jira filter with new JQL via atlassian-python-api.

**Acceptance Criteria:**
- [ ] `FilterSync.update_filter(filter_id, jql, name)` returns success bool
- [ ] Default filter ID: 15113 (configurable via YAML/CLI)
- [ ] Filter name pattern: `Sprint-Board-Update` or `<sprint_name>` from metadata
- [ ] Dry-run mode prints what WOULD be sent without calling Jira
- [ ] Permissions error → clear message + exit 1
- [ ] Tests: mock jira.update_filter, verify args

**Verification:**
```bash
uv run kbs sync --spreadsheet <id> --dry-run
# Expected: "Would update filter 15113 with JQL: ..."

uv run kbs sync --spreadsheet <id> --live
# Expected: "Updated filter 15113. Filter URL: ..."
```

### FR5: Board Verification

**Priority:** High  
**Status:** Pending

**Description:** After filter update, verify the linked board shows the expected issues.

**Acceptance Criteria:**
- [ ] `BoardVerifier.verify_count(board_id, expected, tolerance=2)` returns `VerifyResult`
- [ ] Tolerance: ±2 issues acceptable (Jira sometimes has caching delay)
- [ ] Returns: `VerifyResult(matched: bool, actual: int, expected: int, diff: int)`
- [ ] Default board ID: 1067
- [ ] Tests: exact match, within tolerance, outside tolerance

### FR6: Workflow Configuration via YAML

**Priority:** High  
**Status:** Pending

**Description:** Workflow defaults loaded from YAML, overridable per-call.

**Acceptance Criteria:**
- [ ] `WorkflowConfig.from_yaml(path)` returns Pydantic instance
- [ ] Default config at `config/workflow.yaml` in project root
- [ ] Fields: filter_id, board_id, spreadsheet_id, sheet_name, google_credentials_path, dry_run
- [ ] CLI flags override YAML values
- [ ] Env vars override both: `JIRA_FILTER_ID`, `JIRA_BOARD_ID`, etc.
- [ ] Tests: load YAML, override via env, override via CLI

### FR7: CLI Commands

**Priority:** Critical  
**Status:** Pending

**Description:** typer CLI with sync, preview, validate, verify commands.

**Acceptance Criteria:**
- [ ] `kbs sync` — full sync workflow (default dry-run)
- [ ] `kbs preview` — show parsed data + JQL without writing
- [ ] `kbs validate` — only validate spreadsheet format, no Jira calls
- [ ] `kbs verify` — check board/filter alignment without updating
- [ ] `kbs --version` — show version
- [ ] All commands accept `--config <path>` for YAML override
- [ ] `--dry-run/--live` flag (default: dry-run)
- [ ] Rich terminal output (tables, colors)
- [ ] Exit codes: 0 success, 1 error, 2 partial (some rows skipped)

**Verification:**
```bash
uv run kbs --help               # shows 4 commands
uv run kbs sync --help          # shows sync-specific options
uv run kbs validate --spreadsheet <id>  # no Jira calls
```

### FR8: Backwards Compatibility with Bash Skill

**Priority:** High  
**Status:** Pending

**Description:** Output JQL must match bash skill's output for the same input.

**Acceptance Criteria:**
- [ ] Run bash skill on Sprint 14 spreadsheet → record JQL
- [ ] Run Python `kbs sync --dry-run` on same spreadsheet → record JQL
- [ ] JQL strings must be equivalent (same set of keys, same project clause)
- [ ] Same filter name format (or documented as superset)
- [ ] Tests: golden file test with Sprint 14 data

### FR9: Type Safety + Lint

**Priority:** High  
**Status:** Pending

**Description:** Strict typing and linting matching ecosystem standard.

**Acceptance Criteria:**
- [ ] `mypy --strict src/` passes clean
- [ ] `ruff check .` passes clean (rules: E,W,F,I,N,UP,B,A,C4,SIM,TCH,RUF)
- [ ] `ruff format --check .` passes clean
- [ ] line-length 100, target Python 3.14

### FR10: Test Coverage

**Priority:** High  
**Status:** Pending

**Description:** ≥80% coverage with mocked Sheets and Jira.

**Acceptance Criteria:**
- [ ] `pytest --cov=src/kbs --cov-fail-under=80` passes
- [ ] Unit tests for: parser, jql_builder, filter_sync, board_verify
- [ ] CLI tests via typer.testing.CliRunner
- [ ] Integration test markers (skipped by default in CI)
- [ ] Mock fixtures for gspread + atlassian.Jira

---

## 3. Non-Functional Requirements

### NFR1: Performance
- Full sync (read sheet + parse + JQL + filter update + verify) completes in < 30 seconds for 100 rows
- Single Google Sheets API call (entire sheet, not per-row)
- Single Jira API call to update filter

### NFR2: Reliability
- Retry on transient Jira errors (3x with backoff via tdt-core resilience)
- Idempotent: re-running same input produces same filter contents
- Graceful degradation: if board verify fails, filter is still updated (warn, don't rollback)

### NFR3: Observability
- Structured logging (stdlib logging, JSON output for cron)
- Rich terminal output for interactive use
- Summary at end: rows read, valid keys, filter updated, board verified

### NFR4: Security
- No secrets in YAML config (only file paths)
- Google service account JSON file-permissions checked (warn if world-readable)
- Jira credentials from `~/.tdt/.env` only (via tdt-core)

### NFR5: Cron-friendliness
- Zero color codes when not a TTY (`--no-color` auto-detected)
- Exit codes documented and stable
- Logs written to stderr, summary to stdout

---

## 4. Out of Scope (Phase 1)

- Creating new filters or boards (reuse existing IDs)
- Modifying Jira issue fields (assignee, labels, estimates) — keep `acli` for that until Phase 4
- Scrum boards (kanban only)
- Reverse sync (Jira → spreadsheet)
- Multi-spreadsheet aggregation
- Slack/email summary
- Web UI

---

## 5. Migration Strategy

**Week 1:** Implement Phase 1 MVP. Run alongside bash skill (parallel) for one sprint. Compare outputs.

**Week 2:** Operator validates Python output matches bash. Switch primary to Python.

**Week 3:** Bash skill marked deprecated in `.agents/skills/kanban-board-from-spreadsheet/SKILL.md`.

**Week 4+:** Bash skill remains for emergency fallback. Phase 2 (templates) begins.

---

## 6. Success Metrics

After 1 sprint cycle:
- Operator time per sync: bash 30 min → Python ≤ 5 min (target)
- Failed syncs (manual intervention): 0
- New operator onboarding time: under 30 min (vs 2+ hours for bash + acli + gws)
- Test coverage: ≥80%
- Mypy strict: passing
