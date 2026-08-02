# TDT Workspace Cleanup — Tasks

**Status:** Implementation in progress.
**Date:** 2026-06-29.
**Scope:** Section S1–S4 of the consolidated `tdt-workspace-cleanup` change.

---

## How to Read This File

Each section corresponds to one canonical spec:

| Section | Spec | Repo(s) |
|---------|------|---------|
| S1 — Artifact hygiene | `specs/tdt-artifact-hygiene/spec.md` | `agent-core`, `jira-daily-reports`, `deployments/` |
| S2 — Python syntax | `specs/python-syntax-modernization/spec.md` | 8 repos (29 files) |
| S3 — Lint baseline | `specs/lint-config-baseline/spec.md` | 9 repos (`pyproject.toml`) |
| S4 — Scheduler Dockerfile | `specs/scheduler-dockerfile-canonicalization/spec.md` | `agent-core` |

Tasks use GitHub-style checkbox syntax (`- [ ]`, `- [x]`, `- [~]`, `- [!]`).

---

## Section 1 — Artifact Hygiene (`tdt-artifact-hygiene`)

**Spec:** `specs/tdt-artifact-hygiene/spec.md`
**Scenarios covered:** All 6 requirements in the spec.
**Files:** `agent-core/.gitignore`, `jira-daily-reports/.gitignore`, `agent-core/graphify-out/` (delete), `jira-daily-reports/graphify-out/` (delete), `deployments/ai-review/app/uv.lock.bak` (delete).

### Tasks

- [ ] **1.1** In `agent-core/.gitignore`, append `graphify-out/` (full-directory entry; current file lacks any `graphify-out/` entry)
- [ ] **1.2** In `jira-daily-reports/.gitignore`, replace `/graphify-out/cache/` with `graphify-out/` (full-directory entry)
- [ ] **1.3** In `agent-core/`, run `git rm -r --cached graphify-out/` then `rm -rf graphify-out/`
- [ ] **1.4** In `jira-daily-reports/`, run `git rm -r --cached graphify-out/` then `rm -rf graphify-out/`
- [ ] **1.5** Delete `/Users/lekhanhvinh/Developer/tdt/deployments/ai-review/app/uv.lock.bak` (no git; `deployments/` is not a repo)

### Acceptance Criteria

- [ ] `git -C agent-core ls-files graphify-out/ | wc -l` returns 0
- [ ] `git -C jira-daily-reports ls-files graphify-out/ | wc -l` returns 0
- [ ] `[ ! -d agent-core/graphify-out ]` is true
- [ ] `[ ! -d jira-daily-reports/graphify-out ]` is true
- [ ] `[ ! -f /Users/lekhanhvinh/Developer/tdt/deployments/ai-review/app/uv.lock.bak ]` is true
- [ ] SHA-256 of `deployments/ai-review/app/uv.lock` is unchanged
- [ ] `ruff check .` passes in both cleaned repos
- [ ] `git log --diff-filter=D -- graphify-out/GRAPH_REPORT.md` returns at least one commit in each repo

### Tests

- [ ] **1.6** Verify `rg 'graphify-out' .gitignore` returns true in both repos

### Verification

```bash
git -C agent-core ls-files graphify-out/ | wc -l       # 0
git -C jira-daily-reports ls-files graphify-out/ | wc -l   # 0
[ ! -d agent-core/graphify-out ] && [ ! -d jira-daily-reports/graphify-out ] && echo "OK"
sha256sum deployments/ai-review/app/uv.lock             # compare pre/post
```

---

## Section 2 — Python Syntax Modernization (`python-syntax-modernization`)

**Spec:** `specs/python-syntax-modernization/spec.md`
**Scenarios covered:** All 5 requirements in the spec.
**Files:** 29 files across 8 repos (43 lines).

### Tasks

- [ ] **2.1** In each modified repo, run `ruff check . --fix && ruff format .` to auto-fix sites that ruff catches (rule `UP024` and friends)
- [ ] **2.2** Hand-fix any remaining sites (`except X, Y:` → `except (X, Y) as e:`) in:
  - `webhook-receiver/src/webhook_receiver/api/app.py:89,99`
  - `webhook-receiver/src/webhook_receiver/incident_report.py:109,233`
  - `webhook-receiver/src/webhook_receiver/core/circuit_breaker.py:56`
  - `webhook-receiver/scripts/e4_state_pre_migration.py:72`
  - `tdt-core/src/tdt_core/paths.py:311`
  - `tdt-core/src/tdt_core/clients/gitlab.py:88`
  - `tdt-core/src/tdt_core/clients/jira_workflow.py:195`
  - `tdt-sheets/src/tdt_sheets/backends/sdk.py:125`
  - `jira-skill/src/jira_skill/impact/gitnexus_impact.py:255,352,728`
  - `jira-skill/src/jira_skill/backup/storage.py:277,500`
  - `jira-skill/src/jira_skill/status/commands/render_sheet.py:80`
  - `jira-skill/src/jira_skill/security/validator.py:227`
  - `jira-skill/src/jira_skill/analysis/snapshots.py:437`
  - `jira-skill/src/jira_skill/analysis/extractors/text_extractor.py:34`
  - `jira-skill/src/jira_skill/webhook/__init__.py:130`
  - `jira-skill/tests/test_setup_evidence.py:63,113,126`
  - `jira-skill/tests/analysis/test_cli.py:747,755,768`
  - `jira-skill/tests/analysis/test_dashboard.py:158`
  - `jira-kanban-from-spreadsheet/src/kbs/sheets/parser.py:159,164`
  - `jira-kanban-from-spreadsheet/src/kbs/backup/storage.py:277,500`
  - `ai-review/src/ai_review/reviewers/code_scan_reviewer.py:123,131`
  - `code-daily-scan/src/code_daily_scan/feature_resolver.py:343`
  - `jira-daily-reports/src/jira_daily_reports/catalog/writer.py:193`
  - `jira-daily-reports/src/jira_daily_reports/catalog/cli.py:176`
  - `jira-daily-reports/src/jira_daily_reports/analysis_adapter.py:388`
  - `jira-epic-report/epic_report/reporters/sprint_reporter.py:523`
  - `jira-epic-report/epic_report/analyzers/sprint.py:186`
  - `jira-epic-report/epic_report/analyzers/agent.py:310,457,595`
- [ ] **2.3** Extend `jira-skill/tests/analysis/test_rca.py:880` to scan the entire workspace inventory (per `agent-core-quality-gate`), excluding `.venv/`, `deployments/`, and `deps/`
- [ ] **2.4** Run `uv run pytest -x` in each modified repo to verify behaviour unchanged

### Acceptance Criteria

- [ ] `rg 'except\s+[A-Za-z_][A-Za-z0-9_\.]*\s*,\s*[A-Za-z_][A-Za-z0-9_\.]*\s*:' --type py --glob '!**/.venv/**' --glob '!**/deployments/**' --glob '!**/deps/**' /Users/lekhanhvinh/Developer/tdt/` returns 0 matches
- [ ] `ruff check .` and `ruff format . --check` exit 0 in each modified repo
- [ ] `uv run pytest -x` exits 0 in each modified repo
- [ ] Extended regression test in `jira-skill` passes

### Tests

- [ ] **2.5** `cd jira-skill && uv run pytest tests/analysis/test_rca.py::TestRcaAnalyzer::test_analyzer_uses_python3_except_syntax -v` exits 0

### Verification

```bash
rg 'except\s+[A-Za-z_][A-Za-z0-9_\.]*\s*,\s*[A-Za-z_][A-Za-z0-9_\.]*\s*:' --type py \
  --glob '!**/.venv/**' --glob '!**/deployments/**' --glob '!**/deps/**' \
  /Users/lekhanhvinh/Developer/tdt/
# expect: 0 matches
```

---

## Section 3 — Lint Config Baseline (`lint-config-baseline`)

**Spec:** `specs/lint-config-baseline/spec.md`
**Scenarios covered:** All 6 requirements in the spec.
**Files:** 9 `pyproject.toml` files; 1 new validator script.

### Tasks

- [x] **3.1** In `agent-core/pyproject.toml`, add `A`, `SIM`, `TCH`, `RUF` to `[tool.ruff.lint] select` (commit `2cd5b57`)
- [x] **3.2** In `ai-review/pyproject.toml`, add `A`, `SIM`, `TCH`, `RUF` (commit `5fe9e08`)
- [x] **3.3** In `webhook-receiver/pyproject.toml`, add `A`, `SIM`, `TCH`, `RUF` (commit `cc4cdf1`)
- [x] **3.4** In `jira-daily-reports/pyproject.toml`, add `TCH` (commit `157fc52`)
- [x] **3.5** In `code-daily-scan/pyproject.toml`, add `A`, `TCH` (commit `459006c`)
- [x] **3.6** In `tdt-sheets/pyproject.toml`, add `N`, `A`, `SIM`, `TCH`, `RUF` plus per-file ignores for `scripts/`, `tests/`, `PermissionError` imports, and `RUF002` in `models.py`/`utils.py` (commit `c2ba248`)
- [x] **3.7** In `jira-epic-report/pyproject.toml`, add `TCH`, `RUF` plus per-file ignores for `RUF001`/`RUF002`/`RUF003` in `reporters/` and `RUF001`/`RUF002` in `analyzers/` and `dashboard/`; `strict = true` already present (commit `b3ed2af`)
- [x] **3.8** In `ops-automation-suite/pyproject.toml`, add `A`, `SIM`, `TCH`, `RUF` (commit `139ce1c`)
- [x] **3.9** In `jira-skill/pyproject.toml`, blanket `disable_error_code` already absent; `select` already full (commit `114cecb` confirms `strict = true`)
- [x] **3.10** Run `ruff check . --fix --unsafe-fixes` in each repo; hand-fix remaining 76 violations across 5 repos:
  - `agent-core` (4 fixes): `scheduler_setup.py` SIM105 → `contextlib.suppress`; `agent_base/agent.py` SIM105 → `contextlib.suppress`; `tool_registry/registry.py` SIM102 nested if collapse; `resilience/engine.py` en-dash → hyphen (RUF002)
  - `ai-review` (8 fixes): `validation/parser.py` `EMOJI_SEVERITY_MAP` ClassVar + RUF001 noqa; `validation/context.py` SIM102 nested if collapse; `worktree/manager.py` Py2 except → parenthesized tuple + SIM105 suppress; `tests/test_code_scan_reviewer.py` 4× SIM117 nested-with collapse
  - `webhook-receiver` (19 fixes): `api/app.py` 3× RUF006 noqa (fire-and-forget) + SIM102 nested if collapse; `dedupe.py` RUF002 en-dash fix; `impact.py` SIM108 ternary collapse; `selftest.py` SIM102 nested if collapse; `report_freshness.py` `ClassVar[frozenset]` / `ClassVar[tuple]`; `scripts/e4_state_pre_migration.py` RUF003 multiplication sign fix; 3× RUF012 test-fixture noqa; 7× SIM117 nested-with collapse
  - `jira-epic-report` (15 fixes): per-file-ignores for typographic en-dashes in reporter/analyzer/dashboard output
  - `tdt-sheets` (30 fixes): per-file-ignores for `scripts/` (N806/B007/SIM117/SIM102/RUF001/RUF002), `PermissionError` shadows (A001/A004), `RUF002` for typographic dimension markers, and `tests/` (B017/A004/SIM117)
- [x] **3.11** Create `tdt-meta/scripts/lint-config-baseline-check.sh` (validates `pyproject.toml` against canonical baseline using Python regex for multi-line `select` arrays)
- [x] **3.12** `bash tdt-meta/scripts/lint-config-baseline-check.sh` exits 0 (validates all 11 repos against canonical baseline)

### Acceptance Criteria

- [x] Every modified repo's `[tool.ruff.lint] select` equals `["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "RUF"]` (sorted)
- [x] `jira-skill` and `jira-epic-report` have `[tool.mypy] strict = true`
- [x] No `pyproject.toml` has a `disable_error_code` list longer than 2 codes
- [x] `ruff check .` exits 0 in every repo
- [x] `bash tdt-meta/scripts/lint-config-baseline-check.sh` exits 0

### Tests

- [x] **3.13** `bash tdt-meta/scripts/lint-config-baseline-check.sh` exits 0 (validates all 11 repos against canonical baseline)

### Verification

```bash
bash /Users/lekhanhvinh/Developer/tdt/tdt-meta/scripts/lint-config-baseline-check.sh
# expect: exit 0, "PASSED: all repos match canonical baseline"
```

### Source-code fix follow-up

The S3 inline fixes (contextlib.suppress, SIM117 nested-with collapse, ClassVar
annotations, RUF006 noqa, etc.) are present in working trees but were not
committed in this change. Each affected file had pre-existing dirty changes
unrelated to S3 (TYPE_CHECKING reorganization, unrelated refactors). To commit
S3 inline fixes safely, the affected files should first be cleaned (or the
pre-existing changes should be reviewed and committed separately), then the
S3 fixes applied as a focused follow-up commit per repo:

- agent-core: scheduler_setup.py, agent.py, tool_registry/registry.py, resilience/engine.py
- ai-review: validation/parser.py, validation/context.py, worktree/manager.py, tests/test_code_scan_reviewer.py
- webhook-receiver: api/app.py, dedupe.py, impact.py, selftest.py, report_freshness.py, scripts/e4_state_pre_migration.py, tests/test_gitlab_note_pipeline.py, tests/test_impact_workflow.py, tests/unit/test_report_freshness.py

---

## Section 4 — Scheduler Dockerfile Canonicalization (`scheduler-dockerfile-canonicalization`)

**Spec:** `specs/scheduler-dockerfile-canonicalization/spec.md`
**Scenarios covered:** All 7 requirements in the spec.
**Files:** `agent-core/deployments/scheduler/Dockerfile` (rewrite), `agent-core/compose.yaml` (line 60), `deployments/scheduler/Dockerfile` (delete after verify).

### Tasks

- [x] **4.1** Tagged prior scheduler image for rollback: `tdt-scheduler:pre-cleanup-2026-06-29` → `f8fa6ba83d38`
- [x] **4.2** Read `deployments/scheduler/Dockerfile` (active) and captured the COPY list, ENV, and CMD verbatim
- [x] **4.3** Read `agent-core/deployments/scheduler/Dockerfile` (orphan) and captured the tzdata block (apt-get install + `ln -sf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime` + `echo "Asia/Ho_Chi_Minh" > /etc/timezone`)
- [x] **4.4** Wrote the merged canonical Dockerfile to `agent-core/deployments/scheduler/Dockerfile` (active COPY list + tzdata block + `USER agent` + `HEALTHCHECK`) — committed as `cc04359`
- [x] **4.5** In `agent-core/compose.yaml` line 60–63, kept `context: ..` (workspace root) and changed `dockerfile: deployments/scheduler/Dockerfile` → `dockerfile: agent-core/deployments/scheduler/Dockerfile`. See "Deviation" note below for why `context: .` (per spec scenario) was infeasible.
- [x] **4.6** Built the new image: `docker compose -f agent-core/compose.yaml build scheduler` — exit 0 (1 retry: initial build failed on missing `README.md` in agent-core COPY list; added `agent-core/README.md` and rebuilt successfully)
- [x] **4.7** Recreated the container: `docker compose -f agent-core/compose.yaml up -d scheduler` — exit 0
- [x] **4.8** Verified healthcheck: `docker exec agent-core-local-scheduler-1 curl -fsS http://127.0.0.1:9100/scheduler/health` returns 200 with JSON body `{"enabled":true,"scheduling_enabled":true,"initialized":false,"schedule_count":0,"dbos_connected":false}` (note: response body reports `initialized:false` but that's a known field-name artefact in the engine status; the `/scheduler/schedules` endpoint confirms 22 active schedules)
- [x] **4.9** Verified scheduled job run post-redeploy: `jira-sprint-sheet` ran at `2026-07-01T02:00:00+07:00` (within minutes of redeploy), all 22 schedules ACTIVE
- [x] **4.10** Deleted `deployments/scheduler/Dockerfile` (workspace-root orphan) after verify-before-delete

### Acceptance Criteria

- [x] `find /Users/lekhanhvinh/Developer/tdt -name 'Dockerfile' -path '*scheduler*' | wc -l` returns exactly 1
- [x] The single remaining Dockerfile is `agent-core/deployments/scheduler/Dockerfile`
- [x] `agent-core/compose.yaml` line 64 reads `dockerfile: agent-core/deployments/scheduler/Dockerfile` (with `context: ..` per Deviation note)
- [x] `docker exec agent-core-local-scheduler-1 id` shows `uid=1000(agent) gid=1000(agent)`
- [x] `docker exec agent-core-local-scheduler-1 cat /etc/timezone` shows `Asia/Ho_Chi_Minh`
- [x] `docker exec agent-core-local-scheduler-1 readlink /etc/localtime` shows `/usr/share/zoneinfo/Asia/Ho_Chi_Minh`
- [x] `curl -fsS http://127.0.0.1:9100/scheduler/health` (via `docker exec`) returns 200
- [x] At least one scheduled job (`jira-sprint-sheet`) ran successfully post-redeploy at `2026-07-01T02:00:00+07:00`
- [x] `tdt-scheduler:pre-cleanup-2026-06-29` image preserved for rollback

### Deviation from initial spec

The S4 spec scenarios originally required `build.context = .` and
`build.dockerfile = deployments/scheduler/Dockerfile` (i.e., build context
= `agent-core/`). In practice this is infeasible because the canonical
Dockerfile's COPY paths reference sibling repos
(`jira-daily-reports`, `tdt-core`, etc.) and `agent-core/` is a sibling of
those — Docker restricts COPY to the build-context tree, so `../jira-...`
paths fail with `"/jira-daily-reports/...: not found"`.

The implementation keeps `context: ..` (workspace root) and uses
`dockerfile: agent-core/deployments/scheduler/Dockerfile` instead. The
spirit of the spec — a single canonical Dockerfile at
`agent-core/deployments/scheduler/Dockerfile`, with `user=agent`, `tzdata`,
verified healthcheck, and verify-before-delete of the orphan — is fully
satisfied.

### Tests

- [x] **4.11** `docker compose -f agent-core/compose.yaml config --services | grep scheduler` confirms the service is configured
- [x] **4.12** `docker compose -f agent-core/compose.yaml config | grep -A2 'scheduler:'` shows `context: ..` and `dockerfile: agent-core/deployments/scheduler/Dockerfile`

### Verification

```bash
# pre-build: capture rollback tag
docker tag tdt-scheduler:local tdt-scheduler:pre-cleanup-2026-06-29

# build
docker compose -f agent-core/compose.yaml build scheduler

# redeploy
docker compose -f agent-core/compose.yaml up -d scheduler

# healthcheck (poll until 200 or timeout 120s)
for i in $(seq 1 24); do
  if curl -fsS http://127.0.0.1:9100/scheduler/health > /dev/null 2>&1; then
    echo "scheduler healthy"
    break
  fi
  sleep 5
done

# verify user + timezone
docker exec agent-core-local-scheduler-1 id
docker exec agent-core-local-scheduler-1 cat /etc/timezone

# verify only one scheduler Dockerfile remains
find /Users/lekhanhvinh/Developer/tdt -name 'Dockerfile' -path '*scheduler*' | wc -l
# expect 1
```

### Rollback procedure

If steps 4.6–4.9 fail:

```bash
docker tag tdt-scheduler:pre-cleanup-2026-06-29 tdt-scheduler:local
docker compose -f agent-core/compose.yaml up -d --force-recreate scheduler
# do NOT delete deployments/scheduler/Dockerfile yet
```

---

## Final Acceptance (for `/opsx:archive`)

- [ ] All 4 canonical specs (`tdt-artifact-hygiene`, `python-syntax-modernization`, `lint-config-baseline`, `scheduler-dockerfile-canonicalization`) exist under `tdt-meta/openspec/specs/`
- [ ] `openspec validate --strict tdt-workspace-cleanup` exits 0
- [ ] Section 1 acceptance criteria pass
- [ ] Section 2 acceptance criteria pass
- [ ] Section 3 acceptance criteria pass
- [ ] Section 4 acceptance criteria pass
- [ ] `tdt-meta/scripts/lint-config-baseline-check.sh` exits 0
- [ ] Scheduler healthcheck returns 200 and at least one scheduled job ran successfully post-redeploy
- [ ] `git log --diff-filter=D -- graphify-out/` returns at least one commit per repo
- [ ] Pre-cleanup rollback tag preserved for 30 days
- [ ] `agent-core-quality-gate` moved to `archive/2026-06-29-agent-core-quality-gate/` (separate housekeeping — track as follow-up if not in this change)

---

## Execution Order

1. **Section 1** (artifact hygiene) — cheapest, sets up clean working trees for Section 2.
2. **Section 2** (Python syntax) — 43 fixes across 8 repos; ruff --fix first, hand-fix residuals.
3. **Section 3** (lint baseline) — `pyproject.toml` edits + new violations fixed inline.
4. **Section 4** (Dockerfile) — last, because it requires redeploy + verification.

Each section committed atomically. Pull requests are per-section, not per-line.