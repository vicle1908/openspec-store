## Validated Gap Audit (Aug 2026)

### Already Closed (no action needed)

| Gap | Validation | Status |
|-----|-----------|--------|
| Coverage config alignment | All 3 repos have `[tool.coverage.run]` in pyproject.toml | ✅ Closed |
| Typer version alignment | All 3 repos pin `typer>=0.25.1` | ✅ Closed |
| docs-sync `[tool.coverage]` | Present at lines 98-100 | ✅ Closed |
| Ruff version alignment | All 16 repos pin `ruff>=0.16.1` (uniform) | ✅ Closed |
| mypy version alignment | All 16 repos pin `mypy>=2.3.0` (uniform) | ✅ Closed |
| pytest version alignment | All 16 repos pin `pytest>=9.1.1` (uniform) | ✅ Closed |
| graphify-out/ tracking | Intentionally tracked per .gitignore comments; contains graph.json, reports, labels | ✅ Closed (not a gap) |

### Remaining Gaps

| Gap | Severity | Repo | Action |
|-----|----------|------|--------|
| `src/reports-out/` build artifacts | Medium | agent-core | Remove 324 tracked daily report files (`blocked-*.md`, `wip-age-*.md`), add to .gitignore |

## Tasks

- [x] **T1: Remove `src/reports-out/` from agent-core** — ALREADY DONE (directory empty, .gitignore present)
  - Remove 324 tracked daily report files (`blocked-*.md`, `wip-age-*.md`)
  - Add `src/reports-out/` to agent-core `.gitignore`
  - Commit with message: `chore: remove orphaned build artifacts from src/reports-out/`
  - Verify: `git status` clean, no references to reports-out in source code

- [x] **T2: Final verification and archive**
  - Run `openspec validate --all`
  - Confirm `git status` clean after T1
  - Archive change and commit store
