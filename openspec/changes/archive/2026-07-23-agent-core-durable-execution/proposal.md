## Why

agent-core needs durable execution to preserve agent progress across failures, restarts, and long waits. Currently:

- DBOS is installed and used for cron scheduling (`scheduler_setup.py`)
- `StepPersistence` is wired for per-step persistence
- `ContinuableSnapshot` is referenced in `run_resume()` but not fully wired
- No durable agent runs exist — agents lose context on restart

Pydantic AI provides 4 official durable execution solutions: `TemporalDurability`, `DBOSDurability`, `PrefectDurability`, and Restate. Since DBOS is already installed and working, it's the natural default.

## What Changes

- Add `durable_execution` config key to `harness_config`
- Wire `DBOSDurability` as default durable execution backend
- Make Temporal/Prefect optional via extras
- Wire `ContinuableSnapshot` for resume support
- Document in `harness-integration.md`

## Capabilities

### New Capabilities

- `agent-durable-execution`: Durable agent runs via DBOS/Temporal/Prefect

### Modified Capabilities

- `harness-integration`: Add durable_execution config section
- `agent-runtime`: Add durable execution wiring

## Impact

- **Files modified**: 3 (agent.py, harness-integration.md, config.py)
- **Files created**: 1 (test_durable_execution.py)
- **Dependencies**: None new (DBOS already installed)
- **Breaking changes**: None — opt-in via config
