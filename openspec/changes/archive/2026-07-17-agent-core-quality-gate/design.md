# Design: Agent Core Quality Gate

## Architecture

### Current State (re-validated 2026-05-31)

```
tdt-core/                  webhook-receiver/           jira-daily-reports/    jira-epic-report/         jira-skill/             jira-kanban-from-spreadsheet/
clients/jira.py (315) ✅   api/app.py (466)            cli.py (597)            cli.py (1428) 🚨         field_config.py (768) 🟡 cli.py (732) 🚨
clients/gitlab.py (109)    jira_guard/ (4 files)        reports/sprint_       reporters/spread.py(642)  backup/manager.py (633)  backup/manager.py (634)
env.py (~50)               core/ (3)                     report_sheet.py(1255)🚨 epic_report/models(641) issue/crud.py (573)      backup/storage.py (510)
models/ (2 files)          config/ (2)                  cli.py (597)           collector.py (572)        board/configuration(564) jira/issue_updater (500)
tests (8 files, 77%) ✅    utils/ (2)                   work_item_fields(477)  analyzers/agent (549)     sprint/crud.py (557)     tests/ (40 pass, 73%, 117 mypy 🚨)
ruff: pass                  tests/ (15 files, 79%)       delivery/sheet (432)   reporters/per_epic(535)   sprint/reports.py (521)  ruff: pass
mypy: 0 ✅                  ruff: pass                   tests (22 fail 🚨, 56%)reporters/sprint_rep(501) issue/bulk.py (544)
                            mypy: 0                      ruff: pass            reporters/sprint_cli(485) issue/models.py (516)
                            tenacity: still declared     mypy: 0               tests (459 pass, 77%) ✅ tests (229 pass, 39% 🚨)
                                                                                mypy: 2 errors

agent-core/                 ai-review/                   browser-cli/         ops-automation-suite/
cli/app.py (722)            review_flow/orchestrator    cli.py (195)         engine.py (226)
agent_base/agent (546)        (676)                     tests (33 pass, 30%🚨)tests: 🔴 BROKEN_ENV
llm_gateway/gateway (515)   utils/health.py (365)       mypy: 0               mypy: 🔴 BROKEN_ENV
tests (84% ✅, 0 mypy ✅)  review_flow/context.py(342)
                            tests (81%, 0 mypy)
```

### Target State (after all phases)

```
tdt-core/  ── coverage 77% → 80%+, monoliths already split ✅
webhook-receiver/  ── tenacity removed, 79% → 80%+
jira-daily-reports/  ── 22 fails → 0, 56% → 80%+, sprint_report_sheet.py 1255 → <800 (split)
jira-epic-report/  ── mypy 2 → 0, cli.py 1428 → <400 (split into commands/), reporters tested
jira-skill/  ── 39% → 80%+ (sprint/, webhook/, security/* covered), field_config 768 → <400 (split)
jira-kanban/  ── mypy 117 → 0, cli.py 732 → <400 (split into commands/)
agent-core, ai-review/  ── stay PASS, watch-list managed via T3.12
browser-cli/  ── 30% → 80%+
ops-automation-suite/  ── venv rebuilt, audited, on-track to PASS
```

## Design Decisions

### D1: Rich ANSI test fix approach ✅ VALIDATED
Strip ANSI codes in test assertions instead of disabling Rich globally. Verified working in jira-epic-report (459 pass) and jira-kanban-from-spreadsheet (40 pass). The pattern `re.sub(r'\x1b\[[0-9;]*m', '', result.output)` is the production fix.

### D2: Mypy `no-any-return` fix strategy ✅ VALIDATED for tdt-core
Use `typing.cast()` for SDK methods returning `Any`, TypedDict for known shapes. Validated: tdt-core cleared all 13 errors (commit `a8d4f5e`). The same pattern is now mandated for the remaining 2 errors in jira-epic-report and the 117 errors in jira-kanban-from-spreadsheet.

### D3: PatchedJira split — single-file under flag ✅ SUPERSEDES MIXIN PLAN
Original plan: extract into `jira_compat.py` + `jira_dashboards.py` mixins. Actual outcome: incremental refactors brought `jira.py` from 680 → 315 lines, below the 400-line review flag, without needing mixins. The single-file design is preserved. T4.1 closed. Spec updated to reflect this.

### D4: Epic Report CLI split ⏳ STILL APPLIES
Split into `commands/` subpackage with one module per CLI subcommand. `cli.py` is still 1428 lines (above the 800 hard cap). T4.2 unchanged.

### D5: Test coverage priority — NEW PRIORITIES
Re-prioritized after re-audit:
1. **jira-daily-reports** (T1.5) — P1 regression: 22 fails, -18pt coverage drop. Blocks T3.4 and T4.4.
2. **ops-automation-suite** (T3.11) — BROKEN_ENV unblocks audit visibility.
3. **kanban-spreadsheet mypy** (T2.3) — 117 errors are still the biggest mypy pile.
4. **jira-skill coverage** (T3.2) — 39% with 2533 lines untested in sprint/ + webhook/ remains the largest single gap.
5. **browser-cli** (T3.10) — newly in scope, 30% coverage.
6. **tdt-core / webhook-receiver / jira-epic-report** — all close to 80%, low effort.

### D6: ECC/CCG consolidation approach (unchanged from original)
Capability matrix first, file deletions deferred to a follow-up change. T5.1–T5.3 are unchanged.

### D7: Module-level coverage enforcement ✅ ENCODED in T3.9
Per-module 0% gates land via `coverage.json` parsing in CI. Spec scenarios `Module-level coverage enforcement in CI` and `Zero-coverage module detection` make this normative.

### D8: New spec requirements added during re-audit
Two requirements were added when re-auditing exposed gaps the original spec missed:

- **Workspace repo inventory and scope** — pins the 10 repos and their `<package>` roots so coverage/mypy/ruff use the same target. Prevents drift like ops-automation-suite getting a different package layout silently.
- **Working build environment prerequisite** — codifies that `BROKEN_ENV` is its own failure class. ops-automation-suite was reporting `mypy: …` (empty) which a naive parser could misread as PASS.

### D9: Regression-triggers-task pattern
Spec scenario `Coverage regression triggers a triage task` formalizes how `jira-daily-reports` 74% → 56% becomes T1.5 automatically. Future regressions follow the same path: -3pts → P1 task → identify commit range → triage.

## Test Strategy

### Unit Tests
- **PatchedJira delegates**: Mock `atlassian.Jira` parent, verify parameter translation and return passthrough (already 77% covered).
- **jira-skill sprint module**: Test CRUD operations, model validation, planning algorithms, report generation.
- **jira-skill webhook**: Test HMAC verification, replay protection, IP allowlist, retry logic — security-critical.
- **jira-skill security/***: Test encryption/decryption round-trips, RBAC policy enforcement, vault key management.
- **jira-skill state/manager**: Test checkpoint save/restore, recovery from corrupted state.
- **browser-cli**: Mock Playwright async API, test CDP-attach flow, document extraction (PDF/DOCX → markdown).
- **kanban backup/**: Type all functions first (T2.3), then add tests for storage/manager/changelog round-trips.

### Integration Tests
- **jira-skill API server**: Test real HTTP endpoints with mocked Jira backend.
- **webhook dispatch**: Test end-to-end webhook → ai-review handoff with circuit breaker.
- **CLI commands**: Test full command execution with mocked API responses.

### Coverage Enforcement
- Global: `--cov-fail-under=80` per repo's CI pipeline.
- Per-module: parse `coverage.json` and fail if any source file at 0% (T3.9).
- Pre-commit: `pytest --cov --cov-fail-under=80 --cov-report=term-missing`.

## Migration Path

| Phase | What | Risk | Dependency |
|---|---|---|---|
| 1 (1–2h) | T1.1 ✅ + T1.2 + T1.3 + T1.4 + T1.5 (regression triage) | Low for T1.2-T1.4; Medium for T1.5 | None |
| 2 (4–8h) | T2.1 ✅ + T2.2 + T2.3 (117 errors), then T2.0 enable strict | Medium (kanban scope) | After Phase 1 |
| 3 (1–2 days) | T3.1–T3.6 + T3.10 + T3.11 + T3.12 watch-list | Low (only adds tests + venv rebuild) | T3.4 after T1.5 |
| 3.5 | T3.7 (SDK audit) + T3.8 (sys.path) + T3.9 (per-module CI) | Low | Parallel with Phase 3 |
| 4 (1–2 days) | T4.1 ✅ + T4.2 + T4.3 + T4.4 + T4.5 | Medium | T4.4 after T1.5 |
| 5 (2–3 days) | T5.1–T5.3 (consolidation plans only) | Medium | Independent |

**Total**: 5–8 working days for Phases 1–4 (most of Phase 1 + 2.1 + 4.1 already done), 1–2 weeks for Phase 5 planning.

## Validated Metrics (re-audited 2026-05-31)

### Original 6 Repos (in scope at spec creation)

| Repo | Cov claim | Cov actual | Mypy claim | Mypy actual | Test fails | Max file claim | Max file actual | Status |
|---|---|---|---|---|---|---|---|---|
| tdt-core | 60% | **77%** ↑ | 13 | **0** ✅ | 0 | 680 | **315** ✅ | NEAR PASS |
| webhook-receiver | 78% | 79% | 0 | 0 | 0 | 469 | 466 | NEAR PASS |
| jira-daily-reports | 75% | **56%** 🚨 | 0 | 0 | 5 | **22** 🚨 | 609 → **1255** 🚨 | FAIL — regression |
| jira-epic-report | 77% | 77% | 4 | 2 | 2 | **0** ✅ | 1428 | FAIL |
| jira-skill | 39% | 39% | 0 | 0 | 0 | 557 | **768** 🟡 | FAIL |
| jira-kanban-from-spreadsheet | 73% | 73% | 9 | 117 | **0** ✅ | 732 | 732 | FAIL |

### Newly Discovered Repos (added in this revision)

| Repo | Coverage | Mypy | Test fails | Max file | Status |
|---|---|---|---|---|---|
| agent-core | 84% | 0 | 0 | 722 | **PASS** (watch list) |
| ai-review | 81% | 0 | 0 | 676 | **PASS** (watch list) |
| browser-cli | **30%** 🚨 | 0 | 0 | 195 | FAIL (cov) |
| ops-automation-suite | 🔴 | 🔴 | 🔴 | 226 | **BROKEN_ENV** |

### Module-Level Gap Detail (validated)

| Repo | Module | Coverage | Severity |
|---|---|---|---|
| jira-skill | sprint/ (5 files) | 0% | CRITICAL (~2157 lines untested) |
| jira-skill | webhook/__init__.py | 0% | CRITICAL (376 lines, security-sensitive) |
| jira-skill | security/encryption.py | 29% | HIGH (Fernet + AES-256-CBC) |
| jira-skill | security/vault.py | 26% | HIGH (key management) |
| jira-skill | security/auth.py | 36% | HIGH |
| jira-skill | security/validator.py | 36% | HIGH |
| jira-skill | state/manager.py | 32% | HIGH |
| jira-epic-report | reporters/docx_reporter.py | 0% | MEDIUM (333 lines) |
| jira-epic-report | reporters/spreadsheet_reporter.py | 0% | MEDIUM (642 lines) |
| jira-epic-report | cli.py | 57% | MEDIUM |
| jira-epic-report | dashboard/reporter.py | 56% | MEDIUM |
| webhook-receiver | __main__.py | 0% | LOW (20 lines) |
| webhook-receiver | cli.py | 0% | LOW (39 lines) |
| webhook-receiver | utils/logging.py | 45% | MEDIUM |
| kanban-spreadsheet | cli.py | 39% | MEDIUM |
| kanban-spreadsheet | backup/ (6 files) | 0% | CRITICAL (~700 lines, 117 mypy errors) |
| daily-reports | reports/sprint_report_sheet.py | new + regressed | CRITICAL (1255 lines, 17 fails) |
| daily-reports | schedule.py | 48% | MEDIUM |
| daily-reports | reminders/suppression.py | 52% | MEDIUM |
| browser-cli | (most modules) | mostly 0–30% | HIGH (438 stmt, 307 missing) |

### Re-audit commands (reproducible)

```bash
# File sizes
wc -l tdt-core/src/tdt_core/clients/*.py \
      webhook-receiver/src/webhook_receiver/api/app.py \
      jira-daily-reports/src/jira_daily_reports/cli.py \
      jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py \
      jira-epic-report/epic_report/cli.py \
      jira-epic-report/epic_report/reporters/{docx,spreadsheet}_reporter.py \
      jira-skill/src/jira_skill/field_config.py \
      jira-skill/src/jira_skill/sprint/crud.py \
      jira-kanban-from-spreadsheet/src/kbs/cli.py \
      agent-core/src/agent_core/cli/app.py \
      ai-review/src/ai_review/review_flow/orchestrator.py \
      browser-cli/src/browser_cli/cli.py \
      ops-automation-suite/src/ops_automation/engine.py

# Mypy per repo
for d in tdt-core webhook-receiver jira-daily-reports jira-epic-report jira-skill jira-kanban-from-spreadsheet agent-core ai-review browser-cli ops-automation-suite; do
  pkg=…  # see inventory in spec
  cd $d && uv run mypy $pkg 2>&1 | tail -1
done

# Coverage per repo
for d in …; do
  pkg=…
  cd $d && uv run pytest --cov=$pkg --cov-report=term -q 2>&1 | grep -E "^TOTAL"
done
```
