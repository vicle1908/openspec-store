# TDT Workspace Cleanup — Proposal

**Status:** Ready for implementation.
**Date:** 2026-06-29.
**Scope:** Single consolidated change. Four sections, four new canonical specs, one archive event.

## Why

A research pass across `/Users/lekhanhvinh/Developer/tdt/` on 2026-06-29 produced 50+ findings across code, configuration, docs, skills, and Docker infrastructure. The most severe are:

1. **319 tracked files in `graphify-out/` directories** across `agent-core` (219) and `jira-daily-reports` (100). These are auto-generated GitNexus/Graphify artifacts that should never have been committed, and the repos' `.gitignore` files do not list them.
2. **43 Python 2-style `except X, Y:` clauses** across 29 files in 8 repos. `jira-skill/tests/analysis/test_rca.py:880` already enforces modern syntax for `analyzer.py`; the regression test is being violated by every other file.
3. **Ruff and mypy config drift** across 9 Python repos — `A`, `SIM`, `TCH`, `RUF` rules missing in some, `strict=true` disabled in others, blanket `disable_error_code` lists.
4. **Two scheduler Dockerfiles**, where the active one (workspace-root `deployments/scheduler/Dockerfile`) is the *worse* of the two: it lacks `tzdata` and runs the wrong username vs. what the running container actually does.

Today, no canonical OpenSpec spec exists for any of these four areas. The cleanup creates 4 new canonical specs (`tdt-artifact-hygiene`, `python-syntax-modernization`, `lint-config-baseline`, `scheduler-dockerfile-canonicalization`) so the cleanup cannot regress after archive.

The full research narrative is preserved in [plan.md](plan.md) (16,614 bytes, written earlier in this session). This proposal summarises the validated items and tracks them as 4 sections in tasks.md.

## What Changes

### Section S1 — `tdt-artifact-hygiene` (P1, safe)

A new canonical spec `tdt-meta/openspec/specs/tdt-artifact-hygiene/spec.md` declares that auto-generated artifacts (`graphify-out/`, `*.lock.bak`, `*.lock.orig`, `*.lock~`) MUST NOT appear in `git ls-files` for any repo. Today:

| Path | Tracked files | Action |
|------|---------------|--------|
| `agent-core/graphify-out/` | 219 | `git rm -r --cached`, add `graphify-out/` to `.gitignore`, delete the dir |
| `jira-daily-reports/graphify-out/` | 100 + 57 untracked | same; current `.gitignore` only ignores `/graphify-out/cache/` |
| `deployments/ai-review/app/uv.lock.bak` | 0 (not a git repo) | plain `rm` |

Reversibility: prior content remains reachable via `git log --diff-filter=D` for 30 days.

### Section S2 — `python-syntax-modernization` (P1, safe)

A new canonical spec `tdt-meta/openspec/specs/python-syntax-modernization/spec.md` declares the parenthesized `except` form as mandatory and `UP` rules as required in every TDT Python repo's `[tool.ruff.lint] select`. Today, 43 clauses across 29 files violate this. The breakdown:

| Repo | Lines | Files |
|------|-------|-------|
| `webhook-receiver` | 5 | `api/app.py:89,99`; `incident_report.py:109,233`; `core/circuit_breaker.py:56`; `scripts/e4_state_pre_migration.py:72` |
| `tdt-core` | 3 | `paths.py:311`; `clients/gitlab.py:88`; `clients/jira_workflow.py:195` |
| `tdt-sheets` | 1 | `backends/sdk.py:125` |
| `jira-skill` (src) | 11 | `impact/gitnexus_impact.py:255,352,728`; `backup/storage.py:277,500`; `status/commands/render_sheet.py:80`; `security/validator.py:227`; `analysis/snapshots.py:437`; `analysis/extractors/text_extractor.py:34`; `webhook/__init__.py:130` |
| `jira-skill` (tests) | 8 | `tests/test_setup_evidence.py:63,113,126`; `tests/analysis/test_cli.py:747,755,768`; `tests/analysis/test_dashboard.py:158` |
| `jira-kanban-from-spreadsheet` | 4 | `src/kbs/sheets/parser.py:159,164`; `src/kbs/backup/storage.py:277,500` |
| `ai-review` | 2 | `src/ai_review/reviewers/code_scan_reviewer.py:123,131` |
| `code-daily-scan` | 1 | `src/code_daily_scan/feature_resolver.py:343` |
| `jira-daily-reports` | 3 | `src/jira_daily_reports/catalog/writer.py:193`; `catalog/cli.py:176`; `analysis_adapter.py:388` |
| `jira-epic-report` | 5 | `reporters/sprint_reporter.py:523`; `analyzers/sprint.py:186`; `analyzers/agent.py:310,457,595` |

Conversion: `except X, Y:` → `except (X, Y) as e:` (preserve the trailing colon; ruff handles whitespace).

The existing regression test at `jira-skill/tests/analysis/test_rca.py:880` is extended to scan the workspace, not just `analyzer.py`.

### Section S3 — `lint-config-baseline` (P2, medium)

A new canonical spec `tdt-meta/openspec/specs/lint-config-baseline/spec.md` pins the canonical ruff rule set `["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "RUF"]` and the canonical mypy setting `strict = true` + `disallow_untyped_defs = true`. Repos whose config drifts are brought into line:

| Repo | Ruff additions | Mypy change |
|------|----------------|-------------|
| `agent-core` | add A, SIM, TCH, RUF | — |
| `ai-review` | add A, SIM, TCH, RUF | — |
| `webhook-receiver` | add A, SIM, TCH, RUF | — |
| `jira-daily-reports` | add TCH | — |
| `code-daily-scan` | add A, TCH | — |
| `tdt-sheets` | add N, A, SIM, TCH, RUF | — |
| `jira-epic-report` | add TCH, RUF | enable strict; remove blanket `disable_error_code` |
| `ops-automation-suite` | add A, SIM, TCH, RUF | — |
| `jira-skill` | (already full) | enable strict; remove blanket `disable_error_code` |

Pre-existing violations surfaced by adding rules are fixed inline in the same change (no `# noqa` without justification).

A validator script `tdt-meta/scripts/lint-config-baseline-check.sh` is added so future drift can be detected by name.

### Section S4 — `scheduler-dockerfile-canonicalization` (P2, medium + redeploy)

A new canonical spec `tdt-meta/openspec/specs/scheduler-dockerfile-canonicalization/spec.md` declares the canonical scheduler Dockerfile lives at `agent-core/deployments/scheduler/Dockerfile` (single source of truth). Today:

- **Active:** `deployments/scheduler/Dockerfile` — `USER agent`, no tzdata, no `/etc/timezone`. Built into `tdt-scheduler:local` (last build Jun 26).
- **Orphan:** `agent-core/deployments/scheduler/Dockerfile` — `USER scheduler`, tzdata + `Asia/Ho_Chi_Minh` set. Never built.

The change merges the active Dockerfile with the orphan's tzdata block, writes the merged result to the canonical location, updates `agent-core/compose.yaml` to use `context: .`, rebuilds the image, redeploys, verifies, and only then deletes the now-superseded `deployments/scheduler/Dockerfile`.

Verify-before-delete protocol (mandatory, encoded in the spec):
1. `docker compose -f agent-core/compose.yaml build scheduler` exits 0.
2. `docker compose -f agent-core/compose.yaml up -d scheduler` exits 0.
3. `curl -fsS http://127.0.0.1:9100/scheduler/health` returns 200 within `start_period`.
4. At least one top-of-hour scheduled job (e.g., `jira-sprint-sheet`) runs successfully post-redeploy.
5. Only then `rm deployments/scheduler/Dockerfile`.

## Non-Goals

- `poems-mobile3-{ios,android}-*` perf/release branches — `graphify-out/` left in place per user direction.
- `jira-skill/Dockerfile` migration to `uv` — broken CI/CD but no active deployment.
- `jira-skill/scripts/deploy.sh` rewrite — no active deployment.
- `code-daily-scan` ripgrep skip tests — functional, just a coverage gap.
- `qi-bridge`, `mcp-router` — different languages.
- `deployments/.venv` — runtime venv, intentional.
- `_runtime_root()` full removal at `webhook-receiver/src/webhook_receiver/settings.py:175-183` and `ai-review/src/ai_review/config/settings.py:190-191` — no live callers in the scheduler's PYTHONPATH-resolvable modules; deferred as a follow-up change.

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Mass `git rm` of `graphify-out/` clobbers useful historical state | Low | Reversibility scenario in the spec guarantees 30-day retention via `git log --diff-filter=D` |
| Adding `RUF`/`TCH` exposes hundreds of pre-existing violations | Medium | Tasks explicitly require fixing inline; `# noqa` forbidden without a `# reason:` comment |
| Scheduler redeploy fails and breaks the live container | High | Verify-before-delete protocol + rollback procedure in spec; orphan Dockerfile preserved until verification |
| `agent-core` directory becomes inconsistent with `tdt-core` after pyproject changes | Low | Per-repo pytest + mypy verification in tasks.md |

## Acceptance Criteria

- [ ] All 4 canonical specs (`tdt-artifact-hygiene`, `python-syntax-modernization`, `lint-config-baseline`, `scheduler-dockerfile-canonicalization`) created under `tdt-meta/openspec/specs/`
- [ ] `openspec validate --strict tdt-workspace-cleanup` exits 0
- [ ] `agent-core/graphify-out/` and `jira-daily-reports/graphify-out/` removed from git tree; `.gitignore` updated; no tracked files in either
- [ ] `deployments/ai-review/app/uv.lock.bak` deleted; SHA-256 of `uv.lock` unchanged
- [ ] Zero `except X, Y:` lines outside `.venv/`, `deployments/`, `deps/`
- [ ] `ruff check .` and `ruff format . --check` pass in every updated repo
- [ ] `jira-skill` and `jira-epic-report` pass `uv run mypy . --strict`
- [ ] `agent-core/deployments/scheduler/Dockerfile` is the only scheduler Dockerfile; `compose.yaml` uses `context: .`; scheduler healthcheck returns 200; at least one scheduled job completes successfully post-redeploy

## OpenSpec Validation Caveat

The `openspec` CLI lives at `/Users/lekhanhvinh/.npm-global/bin/openspec` (not on default `$PATH`; install via `npm i -g @openspec/cli` or use the direct path). Validation may run from the host. The earlier research pass erroneously reported the CLI as unavailable — it is in fact present, but `~/.npm-global/bin` must be added to PATH or the absolute path used.

## References

- `tdt-meta/openspec/plan.md` — research narrative (preserved for continuity)
- `tdt-meta/.agents/modules/openspec.md` — `/opsx:*` workflow conventions
- `tdt-meta/openspec/specs/agent-core-quality-gate/spec.md` — repo inventory baseline
- `tdt-meta/openspec/specs/host-deploy-script-consistency/spec.md` — related deploy-script spec
- `tdt-meta/openspec/specs/tdt-env-loader-tdt-home/spec.md` — related TDT_HOME spec
- `tdt-meta/openspec/specs/scheduler-engine/spec.md` — related scheduler spec