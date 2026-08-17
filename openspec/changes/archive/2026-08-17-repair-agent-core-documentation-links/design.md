# Design: Agent-core documentation link repair

## Repair 1: README.md → architecture.md

**File:** `docs/README.md` line 19

**Before:** `- [Model Resolution](model-resolution.md) — Provider model strings, FallbackModel, create_model`
**After:** `- [Model Resolution](architecture.md) — Provider model strings, FallbackModel, create_model`

**Rationale:** `docs/architecture.md` lines 78–80 already document `create_model()`,
`FallbackModel`, and provider model string construction. No `## Model Resolution`
heading exists in that file, so use the file link directly.

## Repair 2: extending.md scheduling section

**File:** `docs/extending.md` lines 265–270

**Before:** Two paragraphs referencing `docs/scheduling.md` and `docs/scheduler/ARCHITECTURE.md`
**After:** One paragraph with link `[Scheduling](scheduling.md)`

**Rationale:** `extending.md` lives inside `docs/`, so the relative link should be
`scheduling.md`, not `docs/scheduling.md`. `docs/scheduler/ARCHITECTURE.md` does not exist.

## Repair 3: scheduling.md stale backtick

**File:** `docs/scheduling.md` line 59

**Before:** `` All active schedules are listed in `docs/scheduler/ARCHITECTURE.md`. ``
**After:** `Use 'agent-core schedules list' to inspect registered schedules when scheduling is enabled.`

**Rationale:** `docs/scheduler/ARCHITECTURE.md` does not exist. The `schedules list`
CLI command is the correct reference.

## Repair 4: architecture.md stale backtick

**File:** `docs/architecture.md` line 124

**Before:** `` All scheduling documentation is in `docs/scheduler/ARCHITECTURE.md`. ``
**After:** `See [Scheduling](scheduling.md) for the current scheduling architecture and CLI examples.`

**Rationale:** Points to the actual scheduling documentation file.

## Repair 5: building-agents.md stale backtick

**File:** `docs/building-agents.md` line 370

**Before:** `` See `docs/scheduler/ARCHITECTURE.md` for full details on the scheduling system. ``
**After:** `See [Scheduling](scheduling.md) for full details on the scheduling system.`

**Rationale:** Points to the actual scheduling documentation file.
