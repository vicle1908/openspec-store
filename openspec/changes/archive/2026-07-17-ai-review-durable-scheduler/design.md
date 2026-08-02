# ai-review Durable Scheduler: Design

## Context

The TDT ecosystem standard for durable workflow execution is DBOS,
exposed through `tdt-core.scheduler` (the `SchedulerEngine`,
`DebouncerWrapper`, `QueueWrapper`, and `ScheduleRegistry`).

`webhook-receiver` already follows this pattern: it creates a
`SchedulerEngine` in its FastAPI lifespan, registers a
`DebouncerWrapper` keyed by `mr-{mr_iid}`, and falls back to an
inline `asyncio.create_task` only when the debouncer is None or
disabled (i.e., DBOS init failed or was skipped).

`ai-review` was using raw `asyncio.create_task` as its only path.
This change aligns it to the same pattern.

## Decisions

### D1: Use the same env-var naming as `SchedulerSettings.from_env()`

The TDT-standard env var names are `SCHEDULER_ENABLED`,
`SCHEDULER_DBOS_DATABASE_URL`, `SCHEDULER_APP_NAME`. We expose them
as `Settings.scheduler_*` fields with sensible defaults
(`enabled=False`, `app_name="ai-review"`).

`review_debounce_seconds` uses the existing TDT convention
`<SERVICE>_<KEY>` → `AI_REVIEW_REVIEW_DEBOUNCE_SECONDS` with a
fallback to the generic `REVIEW_DEBOUNCE_SECONDS` and a default of
60s.

### D2: Module-level singletons, not FastAPI Depends

The scheduler engine and debouncer are tied to the application
lifecycle (init on startup, shutdown on exit), not to a request.
We use module-level globals (`_SCHEDULER_ENGINE`, `_REVIEW_DEBOUNCER`)
mirroring the `_REGISTRY` and `_ORCHESTRATOR` singletons already
in `app.py`. This is the same pattern `webhook-receiver` uses.

### D3: Re-bind the orchestrator on lifespan startup

The orchestrator is constructed lazily via `get_orchestrator()`
on the first request. If we initialize the debouncer in the
lifespan and then the orchestrator is constructed for the first
time, the debouncer must be visible. Solution: clear the
`_ORCHESTRATOR` singleton in the lifespan after binding the
debouncer, so the next `get_orchestrator()` call constructs a
new orchestrator that holds the debouncer.

### D4: Debouncer key is `mr-{mr_iid}`

Same key shape as `webhook-receiver`. Per-MR debounce window
means rapid-fire GitLab webhook events for the same MR get
collapsed into one dispatch, matching the existing `IdempotencyRegistry`
semantics from the request side.

### D5: `loop.run_in_executor` wrapper for the debouncer call

DBOS's `Debouncer.debounce()` is a sync call that internally
calls `DBOS.send()`. `DBOS.send()` raises
`DBOS Error 22` ("DBOS cannot be used from within an asyncio
event loop") if the calling thread already has a running loop.
We push the call onto the default executor (a worker thread
with no running loop), which is exactly what
`webhook-receiver`'s `schedule_merge_request` does (lines
399-400 of `webhook-receiver/src/webhook_receiver/api/app.py`).

### D6: Passthrough mode is acceptable when DBOS is disabled

The passthrough path (`asyncio.create_task` with a task set) is
NOT the same as a fire-and-forget bug: the orchestrator's
`run_sync` method is idempotent (it goes through
`IdempotencyRegistry` upstream), so a duplicate dispatch is
harmless. This matches the precedent set by
`webhook-receiver`'s `mr_debounce_inline` log line.

### D7: Per-service `SCHEDULER_APP_NAME` is required

The first deploy after this change exposed a gap the spec did not
anticipate: **all TDT services share the same DBOS postgres
database** (single `tdt_scheduler` / `tdt_scheduler_dbos_sys`
instance). When two services use the same `app_name`, DBOS
treats them as the same app and may route a workflow to either
process. The pickled workflow args reference classes from the
originating service's module path (e.g.
`webhook_receiver.config.settings.Settings`), and the destination
process cannot unpickle them → `ModuleNotFoundError`.

Fix: each service's runtime launcher exports a service-specific
`SCHEDULER_APP_NAME`:

  * `ai-review`        → `tdt-ai-review`
  * `webhook-receiver` → `tdt-webhook-receiver`

Source change in each repo's `scripts/deploy.sh` heredoc template
that generates the runtime launcher. The env-var is
service-specific because it cannot live in the shared
`~/.tdt/config.yaml` (which has no notion of "which service am I
in"). This is the same pattern that the OpenSpec change
`deployable-env-loading` uses for `JIRA_GUARD_POLICIES_PATH`.

### D8: `tdt-scheduler cancel-stale-errors` for DBOS ERROR recovery

DBOS only auto-recovers PENDING/ENQUEUED rows on app startup;
once a workflow transitions to ERROR it stays there forever. After
a deploy that renames or removes a registered workflow function,
every recovered workflow errors at module import time with
`ModuleNotFoundError` / `AttributeError` and holds the per-key
debouncer lock indefinitely.

The `tdt-scheduler cancel-stale-errors` CLI in
`tdt-core/src/tdt_core/scheduler/cli.py` (commit `54f689c`)
cancels these stale ERROR rows. It pulls all ERROR rows from a
previous `application_version`, decodes the base64-pickled `error`
column (SQL `LIKE` cannot match the class name), and cancels
rows whose exception class is one of `ModuleNotFoundError` /
`AttributeError` / `ImportError` / `UnpicklingError` OR whose
workflow name is one of `_dbos_debouncer_workflow`,
`_dispatch_review_workflow`, `_dispatch_mr_workflow`. Operationally:
run after any deploy that changes registered workflow functions,
or when an ERROR row has the typical "stale registered function"
signature.

## Implementation

### 1. Settings (`ai-review/src/ai_review/config/settings.py`)

```python
@dataclass(slots=True)
class Settings:
    # ... existing fields ...
    scheduler_enabled: bool
    scheduler_database_url: str
    scheduler_app_name: str
    review_debounce_seconds: int

    @classmethod
    def from_env(cls) -> Settings:
        # ... existing assignments ...
        scheduler_enabled=get_bool_env("SCHEDULER_ENABLED", False),
        scheduler_database_url=get_env(
            "SCHEDULER_DBOS_DATABASE_URL",
            get_env("DBOS_DATABASE_URL", ""),
        ),
        scheduler_app_name=get_env("SCHEDULER_APP_NAME", "ai-review"),
        review_debounce_seconds=get_int_env(
            "AI_REVIEW_REVIEW_DEBOUNCE_SECONDS",
            get_int_env("REVIEW_DEBOUNCE_SECONDS", 60),
        ),
```

### 2. App lifespan (`ai-review/src/ai_review/api/app.py`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _SCHEDULER_ENGINE, _REVIEW_DEBOUNCER, _ORCHESTRATOR
    settings = get_settings()
    app.state.settings = settings
    _SCHEDULER_ENGINE = None
    _REVIEW_DEBOUNCER = None
    if settings.scheduler_enabled:
        try:
            engine = SchedulerEngine.from_env()
            engine.initialize()
            _SCHEDULER_ENGINE = engine
            if engine.enabled:
                _REVIEW_DEBOUNCER = engine.debouncer(
                    _dispatch_review_workflow,
                    timeout_sec=float(settings.review_debounce_seconds),
                )
        except Exception as exc:
            logger.warning(
                "scheduler_engine_init_failed", error=str(exc),
                detail="DBOS debouncer disabled; ai-review will use passthrough mode",
            )
    _ORCHESTRATOR = None  # force re-bind with the now-initialized debouncer
    try:
        yield
    finally:
        if _SCHEDULER_ENGINE is not None:
            _SCHEDULER_ENGINE.shutdown()
```

### 3. Orchestrator constructor + enqueue (`ai-review/src/ai_review/review_flow/orchestrator.py`)

```python
class ReviewOrchestrator:
    def __init__(self, settings, *, debouncer=None):
        # ... existing init ...
        self.debouncer = debouncer
        # ... existing init ...

    async def enqueue(self, payload, handoff_id):
        if self.debouncer is not None and self.debouncer.enabled:
            debounce_call = functools.partial(
                self.debouncer.debounce,
                f"mr-{payload.mr_iid}",
                payload, handoff_id,
                period_sec=float(self.settings.review_debounce_seconds),
            )
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, debounce_call)
            return
        # Passthrough fallback
        task = asyncio.create_task(self._run(payload, handoff_id))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
```

### 4. Tests (`ai-review/tests/test_orchestrator.py`)

Three new tests:
- `test_enqueue_dispatches_via_dbos_debouncer_when_enabled`
- `test_enqueue_falls_back_to_passthrough_when_debouncer_disabled`
- `test_enqueue_falls_back_to_passthrough_when_no_debouncer`

Each uses a stub debouncer that records its call signature. The
DBOS-enabled test asserts the debounce key is `mr-{mr_iid}` and
the period matches the configured `review_debounce_seconds`. The
passthrough tests assert the debouncer was not called and the
tracked task runs the stub `_run`.

## Testing Strategy

1. **Unit tests** — see above.
2. **Type checks** — `mypy` is happy because the debouncer
   parameter is typed `DebouncerWrapper | None`.
3. **Integration** — `bash scripts/deploy.sh` from the dev tree
   restarts the LaunchAgent and `/health` reports scheduler state.

## Risks & Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| DBOS init failure leaves the service in degraded state | Medium | Init is wrapped in try/except; failure logs `scheduler_engine_init_failed` and service continues in passthrough mode |
| Debouncer key collision across concurrent MRs for same `mr_iid` | Low | Same pattern as webhook-receiver; debouncer is by-key with `period_sec` collapsing |
| `functools.partial` + `run_in_executor` adds latency | Negligible | Same pattern as webhook-receiver; measured at <1ms overhead |
| `SchedulerEngine.from_env()` reads `SCHEDULER_DBOS_DATABASE_URL`; if missing, engine is `enabled=False` | Low | Default behavior matches the spec; passthrough mode is correct |

## Open Questions

None — design follows the precedent set by
`webhook-receiver/src/webhook_receiver/api/app.py` lines 459-527.
