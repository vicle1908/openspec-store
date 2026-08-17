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

**Before (lines 265–270):**
````
```

See `docs/scheduling.md` and `docs/scheduler/ARCHITECTURE.md` for full details.

See [docs/scheduling.md](docs/scheduling.md) for copy-paste examples of `scheduled_workflow`,
`queue`, and `debouncer`.
````

**After:**
````
```

See [Scheduling](scheduling.md) for full details and copy-paste examples of
`scheduled_workflow`, `queue`, and `debouncer`.
````

**Rationale:**
- `docs/scheduling.md` exists at `docs/scheduling.md`. Since `extending.md` lives
  inside `docs/`, the relative link should be `scheduling.md`, not `docs/scheduling.md`.
- `docs/scheduler/ARCHITECTURE.md` does not exist and is removed.
- The plain-text backtick reference and the Markdown link are consolidated into one
  truthful Markdown link.
