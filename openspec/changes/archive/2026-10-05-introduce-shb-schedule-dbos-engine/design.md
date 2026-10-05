# Design

## Context

See `proposal.md` for motivation. The implementation is a new repository under `~/Developer/shb/`, while the 12 existing SHB repositories and their workload tools remain independently owned. Existing TDT scheduler code is a reference for failure modes and operational patterns only; it is not a runtime dependency.

## Goals / Non-Goals

**Goals:**

- Provide one canonical SHB scheduler process with durable DBOS execution.
- Keep schedule definitions declarative and portable across macOS, Linux, SQLite, and PostgreSQL.
- Preserve the existing SHB-native `shb-tools` documentation synchronizer.
- Reconcile persisted scheduler state safely when manifests change.
- Make reload, health, duplicate-daemon, retry, and dirty-worktree behavior observable and testable.
- Enforce modern Python practices: PEP 621 packaging with `hatchling`, Pydantic v2 `ConfigDict`, Typer `Annotated`, ASGI `lifespan`, and strict DBOS workflow/step determinism.

**Non-Goals:**

- Importing `tdt-core`, `tdt-scheduler`, TDT paths, or TDT workload commands.
- Replacing workload implementations in `shb-tools`.
- Automatic backfill of missed runs or automatic commits in target repositories.
## Decisions

### 1. Repository and dependency boundary

`shb-schedule` is an independent `uv` project with `requires-python = ">=3.14"`, packaged using standard PEP 621 `[project]` metadata with the `hatchling` build backend and `uv.lock`. Runtime dependencies strictly enforce modern versions and interfaces:
- **Durable Orchestration**: `dbos>=3.1.0` (DBOS Transact SDK with dynamic workflow schedules via the database `workflow_schedules` table).
- **Validation & Settings**: `pydantic>=2.10.0` and `pydantic-settings>=2.7.0` using modern Pydantic v2 idioms:
  ```python
  from pydantic import BaseModel, ConfigDict, Field, field_validator
  from pydantic_settings import BaseSettings, SettingsConfigDict

  class ScheduleManifest(BaseModel):
      model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

      name: str
      cron: str
      timezone: str = "Asia/Ho_Chi_Minh"
      workflow: str
      queue: str = "default"
      timeout_seconds: int = Field(default=300, ge=1)
      automatic_backfill: bool = False
  ```
  Deprecated Pydantic v1 patterns (`class Config:`, `@validator`, `@root_validator`, `.dict()`, `.parse_obj()`) are strictly prohibited.
- **CLI & Formatting**: `typer>=0.15.0` with `typing.Annotated` and `rich>=13.9.0`:
  ```python
  from typing import Annotated
  from pathlib import Path
  import typer

  app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")

  @app.command()
  def serve(
      port: Annotated[int, typer.Option("--port", "-p", help="Health probe listen port")] = 9110,
      config_path: Annotated[Path | None, typer.Option("--config", "-c", help="Path to config")] = None,
  ) -> None:
      ...
  ```
  Legacy unannotated default options (`port: int = typer.Option(9110)`) are rejected.
- **Schedules & Parsing**: `pyyaml>=6.0.2` and `croniter>=6.0.0`.
- **Health Server**: `starlette>=0.45.0` and `uvicorn>=0.34.0` using the modern ASGI `lifespan` context manager:
  ```python
  from contextlib import asynccontextmanager
  from starlette.applications import Starlette

  @asynccontextmanager
  async def lifespan(app: Starlette):
      # Initialize DBOS engine, verify database leader lock
      yield
      # Clean shutdown: destroy DBOS engine, release leader lock

  app = Starlette(lifespan=lifespan, routes=...)
  ```
  Deprecated `@app.on_event("startup")` and `@app.on_event("shutdown")` are rejected.

Only SHB-owned packages may be imported; TDT packages and filesystem roots are rejected by dependency and import checks.

### 2. Configuration and persistence

Configuration is loaded using the existing `shb-core` `~/.shb/.env` convention with explicit process-environment precedence documented in the implementation. Defaults are derived from `Path.home()`:

- database: `Path.home() / ".shb" / "scheduler.db"`
- schedules: `Path.home() / ".shb" / "schedules"`
- logs: `Path.home() / ".shb" / "logs"`
- health port: `9110`
- default timezone: `Asia/Ho_Chi_Minh`

SQLite uses modern Python 3.12+ connection management (`sqlite3.connect(db_path, autocommit=False)`) with strict permissions (parent directory `0700`, database file `0600`) and the following PRAGMAs:
- `PRAGMA journal_mode = WAL;`
- `PRAGMA synchronous = NORMAL;`
- `PRAGMA foreign_keys = ON;`
- `PRAGMA busy_timeout = 5000;`

PostgreSQL uses the `shb_scheduler` database/schema contract defined by configuration. The engine must not silently switch persistence backends.

### 3. Workflow Determinism and Step Boundaries

In DBOS (>=3.1.0), workflows must be strictly deterministic to ensure crash recovery and durable execution replay:
- `@DBOS.workflow` is strictly pure and deterministic: it only coordinates step execution, handles flow control, and logs high-level workflow state. Scheduled workflows MUST accept the two positional arguments provided by the DBOS scheduler: `(scheduled_at: datetime, context: DBOSContext)` (or `*args, **kwargs`). Workflows MUST NOT perform direct filesystem I/O, subprocess invocations, network requests, or query system clocks (`datetime.now()`).
- `@DBOS.step` encapsulates all non-deterministic side-effects: Git status inspection (`git status --porcelain`), execution of `shb-docs-sync check --root <path>` or `DocsSynchronizer.audit_and_sync`, system time measurements (`datetime.now(timezone.utc)`), and filesystem writes.
- Subprocess execution must always use vector arguments without shell interpolation: `subprocess.run(["shb-docs-sync", "check", "--root", str(shb_root)], shell=False, check=False, text=True, timeout=180, capture_output=True)`. Concatenated shell strings and `shell=True` are prohibited. The workflow inspects stdout/stderr and audit report contents rather than relying solely on process exit codes.
### 4. Canonical ownership and duplicate-daemon protection

The daemon runs with a stable scheduler identity, `app_name="shb-schedule"`. Only that process may apply the recurring schedule set. Single-owner enforcement is guaranteed by acquiring a non-blocking kernel lock via `fcntl.flock` on `~/.shb/shb-schedule.lock`. If the lock cannot be acquired, the second daemon MUST exit cleanly with an informative log message without attempting to bind to the primary daemon's HTTP health port (9110), avoiding TCP port collision errors (`Errno 48 Address already in use`). A test-only ownership bypass, if retained, is disabled by default and cannot be enabled by production service templates.

### 5. Manifest contract and safe reload

Manifests under `~/.shb/schedules/*.yaml` use `shb-schedule/v1`. Each schedule declares owner, version, cron, timezone, workflow, queue, timeout, retry policy, and `automatic_backfill: false` unless a future capability explicitly opts in.

The loader performs environment substitution (non-evaluating regex strictly matching `${VAR}` and `${VAR:-default}`), strict schema validation, timezone validation, callable resolution, and queue collection before changing runtime state. `.reload` mtime changes and `SIGUSR1` request a transaction:

1. load all manifests into a candidate registry;
2. validate every manifest and resolve every callable;
3. pre-register declared queues;
4. reconcile the candidate registry with persisted DBOS state;
5. atomically apply the candidate schedule set.

Any validation, import, queue, or reconciliation failure leaves the last known-good registry active and records the failed reload reason.

### 6. Persisted-state reconciliation

At startup and before an accepted schedule-set replacement, compare persisted DBOS schedule/workflow rows in `workflow_schedules` with the canonical registry. Because `DBOS.apply_schedules(...)` is upsert-only, schedules present in the database but absent from the loaded YAML manifests MUST be explicitly deleted via `DBOS.delete_schedule(schedule_name)`. Stale enqueued/error work from obsolete application versions is cancelled or quarantined according to the runtime contract. Active valid runs are not cancelled. Reconciliation is transactional where the backend supports it and emits an audit record sufficient to explain the decision.

### 7. Flagship workload

The workflow invokes the existing SHB-native `shb-docs-sync` capability from `shb-tools`, not TDT's `agent-docs-sync`. The execution model supports both direct Python API invocation (`DocsSynchronizer.audit_and_sync(shb_root)`) and CLI invocation (`shb-docs-sync check --root <shb_root>`):

1. executes `@DBOS.step` checking `git status --porcelain` across SHB repository roots;
2. skips mutation or drift remediation on dirty worktrees and records the skip reason;
3. executes `@DBOS.step` running documentation audit with a 180-second overall timeout;
4. inspects the structured audit result (`report.status`, missing READMEs, missing SPEC_INDEXes) rather than relying on exit code (as `shb-docs-sync` returns exit code 0);
5. records structured success, skip, and drift findings.
### 8. Service and health surface

`serve` initializes the runtime, performs reconciliation, loads the last-known-good registry, and starts the polling loop. `list`, `validate`, `reload`, and `run-now` operate through the same registry and ownership contract. `service install` generates idempotent macOS LaunchAgent and Linux systemd user-service definitions.

The HTTP surface exposes `/scheduler/health`, `/scheduler/schedules`, `/scheduler/schedules/{name}`, and `/scheduler/schedules/{name}/trigger`. Triggering a job remains subject to ownership and durable execution rules.

## Risks / Trade-offs

- SQLite is intentionally lightweight but can encounter lock contention; WAL, bounded connections, single-daemon ownership, and retryable busy handling are required.
- Dynamic callable resolution is powerful but expands the local configuration trust boundary; imports must be restricted to approved SHB scheduler/workflow modules.
- Reconciliation can cancel obsolete work incorrectly if identity/version rules are weak; it requires explicit tests for rename, deletion, restart, and concurrent reload cases.
- “Exactly once” is an acceptance target for durable workflow identity and step replay, not a claim that arbitrary external side effects are inherently transactional. External commands must remain idempotent or be guarded by durable step identity.

## Open Questions Resolved

- **Stable `shb-tools` integration boundary**: Resolved against `/Users/androidteam/Developer/shb/shb-tools/src/shb_tools/cli.py` (`shb-docs-sync check --root <path>`) and `shb_tools.docs_sync.engine.DocsSynchronizer.audit_and_sync(shb_root)`. The command is `check`, not `sync`, and audits all 12 SHB repositories under `--root /Users/androidteam/Developer/shb`.
- **Database isolation**: SQLite in WAL mode (`~/.shb/scheduler.db`) is the canonical local engine. PostgreSQL 18 operates in a dedicated `shb_scheduler` schema for enterprise deployments.
- **Python version pinning**: Standardized on `requires-python = ">=3.14"` to conform with `shb-core`, `shb-tools`, and ecosystem-wide specifications.
