# Evidence: Repair agent-core documentation links

## SHA Provenance

| Artifact | SHA | Repository |
|---|---|---|
| OpenSpec planning | `8168432` | openspec-store |
| Base (pre-fix) | `71f9c19` | agent-core |
| Clickable link repairs | `ded5fac` | agent-core |
| Stale reference repairs | `7a89372` | agent-core |

## Baseline CLI Validation (pre-fix)

```
Validation failed: 2 broken links
  - docs/README.md: model-resolution.md (File not found)
  - docs/extending.md: docs/scheduling.md (resolves to docs/docs/scheduling.md)
exit=1
```

## Post-fix CLI Validation

```
Validation passed: 37 links checked in 31 files
exit=0
```

## Stale Reference Sweep (post-fix)

Grep for `docs/scheduler/ARCHITECTURE.md`, `model-resolution.md`, and `](docs/scheduling.md)`
across `docs/` returned empty — no stale references remain.

## What Was Repaired

6 total repairs:
1. `docs/README.md`: `model-resolution.md` → `architecture.md` (file not found)
2. `docs/extending.md`: `docs/scheduling.md` → `scheduling.md` (double-path)
3. `docs/extending.md`: removed `docs/scheduler/ARCHITECTURE.md` reference (file not found)
4. `docs/scheduling.md`: removed stale `docs/scheduler/ARCHITECTURE.md` backtick reference
5. `docs/architecture.md`: removed stale `docs/scheduler/ARCHITECTURE.md` backtick reference
6. `docs/building-agents.md`: removed stale `docs/scheduler/ARCHITECTURE.md` backtick reference

## Notes

- `graphify-out/` modifications on agent-core main predate this repair and are not part of this change.
- No application code was modified. Documentation-only.
