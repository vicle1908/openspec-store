# Agent Core Quality Gate — Execution Readiness Report

**Generated**: 2026-05-31 (re-audited)
**Status**: ✅ READY FOR EXECUTION
**Validators**: `openspec validate agent-core-quality-gate --strict --type spec` ✅ · `openspec validate agent-core-quality-gate --strict --type change` ✅

---

## 1. Artifact Structure — Re-audited and corrected

| # | Issue | Resolution | Status |
|---|---|---|---|
| 1 | Change had no deltas under `specs/` (validator failed) — `specs/spec.md` was a symlink at the wrong path | Replaced with proper delta file at `specs/agent-core-quality-gate/spec.md` using `## ADDED Requirements` headers per `openspec instructions specs` | ✅ Fixed |
| 2 | Empty `proposals/` orphan dir | Deleted | ✅ Fixed |
| 3 | Canonical spec at `openspec/specs/agent-core-quality-gate/spec.md` had stale metrics (61% tdt-core cov, 13 mypy, 680-line jira.py) | Rewrote against current reality (77%, 0 mypy, 315 lines); added 2 new requirements (repo inventory, working venv) | ✅ Fixed |
| 4 | `tasks.md` listed completed work as pending | Marked T1.1 (epic-report+kanban only), T2.1, T4.1 ✅ DONE; recorded actual remediation history | ✅ Fixed |
| 5 | `tasks.md` missing P1 regression for jira-daily-reports (74% → 56%, 5 → 22 fails) | Added T1.5 with explicit failing-test breakdown and triage steps | ✅ Fixed |
| 6 | Spec did not list browser-cli, ops-automation-suite, agent-core, ai-review | New `Workspace repo inventory` requirement pins the 10 repos | ✅ Fixed |
| 7 | Spec had no failure mode for broken venv (ops-automation-suite was reporting empty mypy → could pass naive parsing) | New `Working build environment prerequisite` requirement defines `BROKEN_ENV` as its own state | ✅ Fixed |
| 8 | New monolith `jira-daily-reports/reports/sprint_report_sheet.py` (1255 lines, hard cap exceeded) was not in spec | Added scenario `Sprint report sheet extraction` + task T4.4 | ✅ Fixed |
| 9 | `jira-skill/field_config.py` (768 lines, 96% of 800 cap) was not in spec | Added scenario `jira-skill field config extraction` + task T4.5 | ✅ Fixed |
| 10 | browser-cli 30% coverage was not in scope | Added task T3.10 (50pt gap) | ✅ Fixed |
| 11 | No watch-list for files between 400 (flag) and 800 (cap) | Added task T3.12 listing 23 files | ✅ Fixed |
| 12 | No regression-triggers-task pattern in spec | Added scenarios `Coverage regression triggers a triage task` and `Test regression triggers triage` so future drift is filed automatically | ✅ Fixed |

---

## 2. Drift between spec (as authored 2026-05-31) and re-audit (also 2026-05-31)

### Coverage

| Repo | Spec said | Actual | Δ | Notes |
|---|---|---|---|---|
| tdt-core | 61% | **77%** | +16 ✅ | additional tests merged after spec |
| webhook-receiver | 79% | 79% | 0 | unchanged |
| jira-daily-reports | 74% | **56%** | -18 🚨 | regression — see T1.5 |
| jira-epic-report | 77% | 77% | 0 | unchanged |
| jira-skill | 39% | 39% | 0 | unchanged (still critical) |
| jira-kanban-from-spreadsheet | 73% | 73% | 0 | unchanged |
| agent-core | TBD | 84% | new | added to inventory |
| ai-review | TBD | 81% | new | added to inventory |
| browser-cli | TBD | 30% | new | added to inventory |
| ops-automation-suite | TBD | 🔴 BROKEN_ENV | new | venv missing |

### Mypy

| Repo | Spec | Actual | Notes |
|---|---|---|---|
| tdt-core | 13 | **0** ✅ | T2.1 done |
| webhook-receiver | 0 | 0 | match |
| jira-daily-reports | 0 | 0 | match |
| jira-epic-report | 4 | 2 | partial fix already merged |
| jira-skill | 0 | 0 | match |
| jira-kanban-from-spreadsheet | 9 | **117** | regression on `backup/` (no annotations) |
| agent-core | n/a | 0 | new in scope |
| ai-review | n/a | 0 | new in scope |
| browser-cli | n/a | 0 | new in scope |
| ops-automation-suite | n/a | 🔴 | venv broken |

### Test failures

| Repo | Spec | Actual | Notes |
|---|---|---|---|
| tdt-core | 0 | 0 | clean |
| webhook-receiver | 0 | 0 | clean |
| jira-daily-reports | 5 | **22** | regression — see T1.5 |
| jira-epic-report | 2 | **0** ✅ | T1.1 done |
| jira-skill | 0 | 0 | clean |
| jira-kanban-from-spreadsheet | 9 | **0** ✅ | T1.1 done |
| agent-core | n/a | 0 | clean |
| ai-review | n/a | 0 | clean |
| browser-cli | n/a | 0 | clean |
| ops-automation-suite | n/a | 🔴 | unmeasurable |

### File sizes

| File | Spec | Actual | Δ | Notes |
|---|---|---|---|---|
| `tdt-core/.../jira.py` | 680 | **315** ✅ | -365 | T4.1 effectively done |
| `webhook-receiver/.../app.py` | 469 | 466 | -3 | within noise |
| `jira-daily-reports/.../cli.py` | 609 | 597 | -12 | within noise |
| `jira-daily-reports/.../sprint_report_sheet.py` | (not listed) | **1255** | new | hard-cap break — T4.4 added |
| `jira-epic-report/.../cli.py` | 1428 | 1428 | 0 | T4.2 still applies |
| `jira-epic-report/.../spreadsheet_reporter.py` | 163 | **642** | +479 | grew significantly |
| `jira-skill/.../sprint/crud.py` | 557 | 557 | 0 | unchanged |
| `jira-skill/.../field_config.py` | (not listed) | **768** | new | 96% of cap — T4.5 added |
| `jira-kanban-from-spreadsheet/.../cli.py` | 732 | 732 | 0 | T4.3 still applies |

---

## 3. Updated artifact inventory

| Artifact | Path | Status |
|---|---|---|
| `.openspec.yaml` manifest | `changes/agent-core-quality-gate/.openspec.yaml` | ✅ unchanged |
| `proposal.md` | `changes/agent-core-quality-gate/proposal.md` | ✅ unchanged |
| `design.md` | `changes/agent-core-quality-gate/design.md` | ✅ rewritten with re-audited metrics |
| `tasks.md` | `changes/agent-core-quality-gate/tasks.md` | ✅ rewritten with status + 5 new tasks |
| `specs/agent-core-quality-gate/spec.md` | `changes/agent-core-quality-gate/specs/agent-core-quality-gate/spec.md` | ✅ NEW — proper delta file |
| canonical spec | `openspec/specs/agent-core-quality-gate/spec.md` | ✅ rewritten to match delta |
| `VALIDATION_REPORT.md` | `changes/agent-core-quality-gate/VALIDATION_REPORT.md` | ✅ this file |

---

## 4. Updated task inventory

| Phase | Tasks | Status |
|---|---|---|
| Phase 1 | T1.1 ✅ (epic + kanban), T1.2, T1.3, T1.4, **T1.5 NEW** (P1 regression) | Ready |
| Phase 2 | T2.0, T2.1 ✅, T2.2, T2.3 (117 errors) | Ready |
| Phase 3 | T3.1–T3.6, **T3.10 NEW** (browser-cli) | Ready |
| Phase 3.5 | T3.7, T3.8, T3.9, **T3.11 NEW** (rebuild venv), **T3.12 NEW** (watch list) | Ready |
| Phase 4 | T4.1 ✅, T4.2, T4.3, **T4.4 NEW** (sprint_report_sheet), **T4.5 NEW** (field_config) | Ready |
| Phase 5 | T5.1–T5.3 | Ready |

**5 new tasks** beyond the original spec, all driven by the re-audit.

---

## 5. Validators

```
$ cd tdt-meta && openspec validate agent-core-quality-gate --strict --type spec
Specification 'agent-core-quality-gate' is valid

$ cd tdt-meta && openspec validate agent-core-quality-gate --strict --type change
Change 'agent-core-quality-gate' is valid
```

Both pass strict mode. All requirements have at least one `#### Scenario:` block. Delta file under `specs/<capability>/spec.md` uses `## ADDED Requirements` per OpenSpec convention.

---

## 6. Estimated timeline (updated)

| Phase | Duration | Risk | Notes |
|---|---|---|---|
| Phase 1 | 2–4 hours | Low for T1.2–T1.4; **Medium for T1.5** | T1.5 is a real bug triage, not just an assertion fix |
| Phase 2 | 4–8 hours | Medium (kanban scope) | T2.1 ✅ already done |
| Phase 3 | 1.5–2.5 days | Low | T3.10 (browser-cli 30 → 80) is the largest add |
| Phase 3.5 | parallel with Phase 3 | Low | T3.11 is a single `uv sync --reinstall` |
| Phase 4 | 1.5–2 days | Medium | T4.4 (sprint_report_sheet split) needs T1.5 first |
| Phase 5 | 2–3 days | Medium (planning only) | Independent |

**Total**: 5–8 working days for Phases 1–4 (with T2.1, T4.1, partial T1.1 already done), 1–2 weeks for Phase 5 planning.

---

## 7. What an executor should do first

1. Run **T3.11** first (5 min): `cd ops-automation-suite && rm -rf .venv && uv sync --reinstall` so the audit stops being blind on that repo.
2. Run **T1.5** triage next (2–4h): root-cause the 22 jira-daily-reports failures, fix or revert. Coverage will partly recover by itself.
3. Then **T1.2, T1.3, T1.4** in parallel — each is mechanical.
4. Phase 2 + Phase 3 in parallel after that.
5. Phase 4 once tests are green and coverage is enforced.
