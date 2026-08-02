## Context

`jira-epic-report` is a Python Typer CLI that generates comprehensive Jira epic status reports (`epic-report generate <keys>`). Today it is invoked manually. The user wants daily, automatic analysis of a curated set of epics — configurable via `~/.tdt` — landing in the existing dedicated epic-report Google Sheets workbook.

The TDT ecosystem already has a proven pattern for this: `code-daily-scan` reads `~/.tdt/code-daily-scan.yaml`, runs on a cron, and writes results via a thin DBOS workflow. `jira-daily-reports` does the same via a manifest generator reading `_CRON_*` constants. This change replicates that pattern for `jira-epic-report` so operators do not learn a new scheduling model **and so the new schedule conforms to the contract established by the `scheduler-cli`, `scheduler-cron-migration`, and `jira-daily-reports` specs already in `openspec/specs/`.**

The host already exposes the dedicated epic-report workbook at `~/.tdt/epic-report-config.toml [output].spreadsheet_url = "https://docs.google.com/spreadsheets/d/1cEPOWIJehpv83WVshYKTu-kBHc0wBTlZT887i6RdLUQ/edit?gid=1993853812"`. The existing comment in that file says "Dedicated epic-report workbook; keep this separate from the sprint workbook." The scheduled run reuses this same workbook — there is no manual-vs-scheduled collision risk because the workbook's *purpose* is "latest epic-report truth." The URL flows into `generate()`'s `spreadsheet_url` parameter via the existing `EPIC_REPORT_SPREADSHEET_URL` env-var override mechanism in `epic_report.config` (config.py:232-234), so the scheduled-run subprocess sets this env var rather than passing a new CLI flag.

## Goals / Non-Goals

**Goals:**
- A new `epic-report scheduled-run` CLI subcommand that is self-configuring (reads its own TOML via `AppConfig.from_env()`).
- A new `[schedule]` section in `~/.tdt/epic-report-config.toml` with an explicit allow-list of epic keys, the `tdt-schedule/v1`-valid cron, an explicit cron timezone (defaulting to the `jira_daily_reports.config.workspace_timezone_name()` resolver per `scheduler-cron-migration`), and the spreadsheet URL override (falling back to `[output].spreadsheet_url`).
- A new schedule manifest generator module at `agent-core/deployments/scheduler/generators/jira_epic_report.py` that registers itself into the existing `generators.GENERATORS` registry via the existing `register()` call and is picked up by the entrypoint loop.
- A thin `@_dbos.DBOS.workflow()` in `agent_core.scheduler_setup` that is a subprocess launcher — no Jira/Sheets logic, same env-var forwarding pattern as `_run_platform_scan`. The workflow is named `daily_epic_report` and the schedule that references it is named `daily-epic-report`.
- Daily cadence by default; cron override per environment.
- Backward compatibility: existing TOML files without `[schedule]` continue to work unchanged.
- The new schedule conforms to the existing `scheduler-cron-migration` contract: `automatic_backfill=False`, no missed-tick replay via a host-local fallback, explicit cron timezone matching the workspace resolver.

**Non-Goals:**
- JQL-driven epic discovery (Phase 2 — operator-driven JQL filter ingestion is deferred).
- Cutoff date derivation from sprint ends (Phase 2).
- LM/dep-analysis depth (scheduled runs always use the fast heuristic path).
- Per-project or per-epic independent schedules (one schedule, many epics).
- Migrating or refactoring the existing `epic-report generate` CLI surface.
- Cursor-pagination refactor of `epic_report.collector` (inherited as a soft obligation from the `jira-daily-reports` spec; out of scope for this change).
- A new `jira-epic-report` first-party dependency on `jira-daily-reports` (the `workspace_timezone_name()` reference is a runtime helper, not a hard dep — see Decision 6 below).

## Decisions

### Decision 1: Allow-list of epic keys, not JQL

An explicit allow-list of epic keys (e.g., `epics = ["RMD-4160", "PUB-1234"]`) is the configuration model rather than a JQL filter.

**Rationale:**
- `generate()` already accepts positional `epic_keys` (cli.py:193), so no new selection surface is required on the CLI itself.
- The allow-list spans projects naturally — a single list can hold `RMD-4160`, `PUB-1234`, `PDS-81` without per-project reconfiguration. This matters because the user explicitly called out [RMD-4160](https://psplit.atlassian.net/browse/RMD-4160) (project `RMD`) as a target, and the existing config is project-agnostic.
- Operators update the list by editing one well-known file, with no JQL syntax risk.
- The cost is manual list maintenance — an accepted trade-off (deferred JQL ingestion covers this in Phase 2).

**Alternatives considered:**
- *JQL filter* — more dynamic but requires a new resolver between config and `generate()` (no `--jql` flag exists today) and introduces blast-radius risk (a broad filter could analyze dozens of epics silently). Deferred.
- *Hybrid (pinned + JQL union)* — combines both, but doubles the surface area for v1.

### Decision 2: Reuse `[output].spreadsheet_url` as default target, via `EPIC_REPORT_SPREADSHEET_URL` env var

The scheduled run writes to `[output].spreadsheet_url` by default; an optional `[schedule].spreadsheet_url` overrides it. The chosen URL is **propagated to the `generate()` subprocess via the existing `EPIC_REPORT_SPREADSHEET_URL` env var**, not via a new CLI flag.

**Rationale:**
- The existing comment in `~/.tdt/epic-report-config.toml` calls that workbook "Dedicated epic-report workbook." It is *already* the single source of truth for "latest epic-report output."
- The `EPIC_REPORT_SPREADSHEET_URL` env var is the **existing extension point** for spreadsheet override (`epic_report.config` lines 232-234 — `if epic_spreadsheet_url: output.spreadsheet_url = epic_spreadsheet_url`). The `generate()` Typer command already reads `output.spreadsheet_url` from `AppConfig.output` (cli.py:540-541). Using the env var keeps `scheduled-run` as a thin launcher with no new CLI surface.
- This means **zero changes to `spreadsheet_reporter.py`**. The existing `generate_spreadsheet(spreadsheet_url=...)` path handles the rest.
- Manual and scheduled runs sharing one workbook is intentional: the workbook is meant to always reflect the latest state.

**Alternatives considered:**
- *Dedicated scheduled workbook* — would require operators to manage a second spreadsheet and a second URL. Rejected as unnecessary complexity.
- *Tab-prefix namespacing* (`[Auto] Executive Summary`, etc.) in the same workbook — would require modifying `_sync_sheet_structure()` to stop deleting non-prefixed tabs. Rejected because the simpler "one workbook, always-current" semantics already exist.
- *New `--spreadsheet-url` CLI flag on `scheduled-run`* — would duplicate the env-var mechanism and force operators to think about flag-vs-env precedence. Rejected; the env var is already the canonical seam.

### Decision 3: `epic-report scheduled-run` lives inside `jira-epic-report`, not `agent-core`

The new CLI subcommand is added to `jira-epic-report` rather than as a standalone launcher in `agent-core`.

**Rationale:**
- The tool that owns the config (`jira-epic-report`) also owns the command that consumes it. The workflow stays a dumb subprocess launcher.
- Mirrors `code-daily-scan`: `code-daily-scan scan --platform android` reads its own `~/.tdt/code-daily-scan.yaml`. We use the same seam.
- The `tdt_core.clients.jira.JiraClientFactory` rule is naturally honored — JQL/Jira calls already happen inside `jira-epic-report`, not inside `agent-core`.
- Reusable for manual `epic-report scheduled-run` invocations outside the scheduler (debugging, on-demand refresh).

### Decision 4: Manifest factory returns empty `schedules: []` when disabled; raises when enabled-invalid

The manifest factory follows two distinct error semantics depending on the disabled/enabled state.

**Rationale:**
- **`enabled = false` or section absent** → factory returns `{"schedules": []}`. The dispatcher (`dispatch_manifest_generation.py:81-86`) treats zero schedules as "skip the write" and returns 0. The existing `~/.tdt/schedules/jira-epic-report.yaml` (if any) is left untouched — no spurious DBOS registration, no accumulating paused schedules.
- **`enabled = true` but invalid** (e.g., empty `epics`, bad cron) → factory raises `RuntimeError` BEFORE returning the dict. The dispatcher's outer `except Exception` (line 153-156) exits non-zero, `entrypoint.sh` aborts the container startup via `set -euo pipefail`, and the container restart policy surfaces a visible restart loop instead of a silent tick-time crash. This mirrors the "refuse to write empty manifest" intent in the existing `jira.py` generator's `_main()` shim.
- The split matters because "operator hasn't configured scheduling yet" (disabled, no-op) is **not** a deployment failure — it is the documented default. But "operator enabled scheduling with a broken config" (enabled, invalid) **is** a deployment failure.
- The CLI subcommand ALSO pre-flights the same condition (returns non-zero on empty `epics`). The two fail paths are independent: the CLI check protects manual `epic-report scheduled-run` invocations; the generator check protects the scheduled container startup path.

### Decision 5: Schedule name `daily-epic-report`, not `jira-epic-report`

The schedule is named `daily-epic-report` (matching the `code-daily-scan` `daily-<platform>-scan` convention) rather than `jira-epic-report` (matching the `jira-daily-reports` `jira-*` prefix convention).

**Rationale:**
- The workflow function `daily_epic_report` lives in `agent_core.scheduler_setup` — same pattern as `daily_android_scan` and `daily_ios_scan`. Naming the schedule the same way lets `tdt-scheduler schedules list` show a consistent `daily-*` shape for all `agent-core`-hosted workflows.
- The `scheduler-cli` spec's naming rule ("All schedule name arguments MUST match the registered name exactly, including the service prefix") describes a *service-prefix convention*, but `code-daily-scan` already shows the ecosystem uses two prefixes: `jira-*` for jira-daily-reports (which has 16 schedules) and `daily-<platform>-scan` for code-daily-scan (which has 2 schedules). The "service" here is "scheduled daily analysis" — the existing `daily-*` shape fits.
- `jira-daily-reports` requires "no duplicate schedule names across reporting suites" (`scheduler-cron-migration` Requirement). Using `daily-epic-report` rather than `jira-epic-report` keeps the names disjoint from `jira-daily-reports`'s `jira-*` set.

**Alternatives considered:**
- *`jira-epic-report` as the schedule name* — collides with the `jira-*` set visually and risks future overlap if `jira-daily-reports` adds a `jira-epic-report` block.
- *`jira-epic-report-daily`* — combines both; ambiguous and not used anywhere else.

### Decision 6: `ScheduleConfig.timezone` defaults to `jira_daily_reports.config.workspace_timezone_name()`

The `[schedule].timezone` field is **optional** in the TOML. When omitted, the loader resolves it via the canonical workspace-timezone helper already used by every other migrated schedule (`jira_daily_reports.config.workspace_timezone_name()`, which honors `PERSON_CAPACITY_TIMEZONE` / `TDT_TIMEZONE` / `TZ` then host then UTC per `scheduler-cron-migration`).

**Rationale:**
- `scheduler-cron-migration` explicitly requires "Cron timezone is consistent across all migrated schedules" — every schedule MUST carry the same resolved `cron_timezone` value, and no schedule MAY register with `cron_timezone=None`.
- Hardcoding `"Asia/Ho_Chi_Minh"` in `ScheduleConfig.timezone` would violate that contract for operators who have changed their workspace timezone env var.
- Importing `jira_daily_reports.config.workspace_timezone_name` inside `epic_report.config` would introduce a new first-party dependency on `jira-daily-reports`. To avoid that, the loader implements the same env-var resolution chain itself (`PERSON_CAPACITY_TIMEZONE` → `TDT_TIMEZONE` → `TZ` → host tzdata → `UTC`) with a docstring citing the canonical helper for review. The implementation MUST stay functionally equivalent to `workspace_timezone_name()`; if the canonical helper changes, this implementation MUST be updated in lockstep.
- The fixture `timezone = "Asia/Ho_Chi_Minh"` shown in the spec's "Valid enabled schedule" scenario is an example value, not a hardcoded default.

**Alternatives considered:**
- *Hardcode `"Asia/Ho_Chi_Minh"`* — violates the cross-spec contract.
- *Add `jira-daily-reports` as a `jira-epic-report` first-party dep* — bloats the dep closure for a single helper function. Rejected; the inline resolver is 5 lines.

### Decision 7: Subprocess launcher mirrors `_run_platform_scan`

The `daily_epic_report` workflow is `subprocess.run([sys.executable, "-m", "epic_report", "scheduled-run"], env=...)` with the same env-var forwarding shape as `_run_platform_scan` (scheduler_setup.py:223-274): `os.environ.copy()` plus the relevant env vars (here: `JIRA_*`, `GOOGLE_APPLICATION_CREDENTIALS`, `EPIC_REPORT_SPREADSHEET_URL`).

**Rationale:**
- Stays consistent with the existing thin-launcher pattern in `scheduler_setup.py`.
- Keeps `agent-core` free of Jira/Sheets code paths (matches the rule "factory-only API clients" — there are no API clients in `agent-core` for this workflow, only a subprocess).
- Error semantics match: non-zero exit becomes a `subprocess.CalledProcessError` that DBOS records for retries and observability.
- This decision is **independent** of the timezone decision (Decision 6): env-var forwarding is about *credentials*, not *scheduling*.

## Risks / Trade-offs

- **[Risk] Stale epic list** → Operator must remember to remove closed/added epics from `[schedule].epics`. *Mitigation*: documented as a known limitation in the config example; Phase 2 adds JQL ingestion to auto-discover.

- **[Risk] Daily run collides with manual investigation** → If an operator is mid-edit in the epic-report workbook at 7am, the scheduled run overwrites their edits. *Mitigation*: documented behavior — the workbook's purpose is "latest epic-report truth." If this becomes painful, Phase 2 can introduce a tab-prefix `[Auto]` mode or a dedicated scheduled workbook without breaking the v1 contract.

- **[Risk] New `[schedule]` table extends TOML schema** → Existing files without `[schedule]` must continue to parse cleanly. *Mitigation*: `ScheduleConfig` loader returns `enabled=False` on missing section; spec scenario "Existing TOML without [schedule]" pins this behavior.

- **[Risk] Container restart required to pick up TOML edits** → Changing the allow-list in `~/.tdt/epic-report-config.toml` requires restarting the scheduler container (or touching the `.reload` sentinel) for the new manifest to be regenerated. *Mitigation*: documented; consistent with `code-daily-scan` operator UX.

- **[Risk] `jira-epic-report` is not yet installed in the scheduler venv** → The container's venv and PYTHONPATH currently have no `epic_report` package. *Mitigation*: three edits (Dockerfile COPY + sed rewrite + editable install) wire the source into the image; compose bind-mount lets host edits propagate without rebuild. The editable-install MUST be placed after `jira-skill` and `jira-daily-reports` in the Dockerfile chain because `jira-epic-report/pyproject.toml:21` declares `jira-skill` as a first-party dep. The `dependency_integrity_gate` is extended to verify `epic_report.cli` imports under the venv.

- **[Risk] ScheduleSpec Pydantic validation rejects the cron** → `tdt_core.scheduler.schedule_manifest.ScheduleSpec._validate_cron` (line 145-152) does a structural regex check and rejects non-matching values. *Mitigation*: an invalid cron in `[schedule].cron` causes the manifest factory to raise (Decision 4) and aborts startup, surfacing the error to the operator instead of silently dropping the schedule.

- **[Risk] `DispatchManifest` skips the write when `len(schedules) == 0`** → Operators who disable scheduling cannot tell from the manifest file whether the generator ran. *Mitigation*: the dispatcher prints `"generator for 'jira-epic-report' returned no schedules — skipping write"` to stderr, which is visible in `~/.tdt/logs/scheduler-entrypoint.log` via the entrypoint's `tee -a LOG_FILE`.

- **[Risk] `workspace_timezone_name()` resolver drift** → The inline resolver in `epic_report.config` (Decision 6) MUST stay functionally equivalent to `jira_daily_reports.config.workspace_timezone_name()`. *Mitigation*: code comment cites the canonical helper; a regression test asserts the inline resolver returns the same value as `workspace_timezone_name()` for the standard env-var chain (both unset → `UTC`).

- **[Risk] Schedule name conflict with future jira-daily-reports additions** → If `jira-daily-reports` later adds an `epic`-prefixed schedule (e.g. `jira-epic-overview`), `daily-epic-report` remains disjoint. *Mitigation*: the name choice (Decision 5) explicitly avoids the `jira-*` prefix set.

- **[Trade-off] No cutoff date** → Fast heuristic path uses no `--cutoff`, so the TIMELINE_AT_RISK factor may underreport for long-running epics. *Accepted*: matches "keep current logic, enhance later" principle; explicitly noted as non-goal.

- **[Trade-off] No LM/dep-analysis** → Scheduled runs never spawn codex/claude/kimi/pi agents. *Accepted*: explicit user decision to start with fast path; documented in proposal non-goals.

## Migration Plan

This is a purely additive change. No migration is required.

**Deployment steps:**
1. Land the `jira-epic-report` changes (new `ScheduleConfig`, `scheduled-run` CLI, README config example, new tests).
2. Land the `agent-core` changes (new generator module, generator registration, scheduler_setup workflow, entrypoint + Dockerfile + compose + gate wiring).
3. Rebuild and redeploy the scheduler container: `docker compose up --build -d scheduler`.
4. Operator creates or edits `~/.tdt/epic-report-config.toml` to add a `[schedule]` table with `enabled = true` and the desired `epics` list.
5. Restart the scheduler container to trigger manifest regeneration, or `touch ~/.tdt/schedules/.reload`.
6. Verify the manifest at `~/.tdt/schedules/jira-epic-report.yaml` contains one `daily-epic-report` schedule with `automatic_backfill: false` and the expected `cron_timezone`.
7. (Optional) Trigger a one-shot by invoking `epic-report scheduled-run` manually inside the container to verify end-to-end before the first cron tick.

**Rollback:**
- Set `[schedule].enabled = false` in the TOML and restart the container → factory returns `{"schedules": []}` → dispatcher skips the write → DBOS drops the schedule on the next `apply_from_yaml` cycle.
- Revert code commits and rebuild the container.

**No data migration:** existing TOML files without `[schedule]` continue to parse and run unchanged.

## Open Questions

None. All design decisions were resolved during the exploration phase. The two threads deferred (JQL ingestion and cutoff derivation) are explicit non-goals for v1.