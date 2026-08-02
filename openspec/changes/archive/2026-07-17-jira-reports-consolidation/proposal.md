# Jira Reports Consolidation - Proposal

**Status:** ✅ Finalized → See [spec.md](spec.md) for full architecture  
**Date:** 2026-05-20  
**Author:** Kiro  
**Decision:** Ecosystem with `tdt-core` shared package (Option B+)

---

## Context

Three reporting/Jira components exist in the tdt workspace:

| Project | Language | Maturity | LOC | Tests | Purpose |
|---------|----------|----------|-----|-------|---------|
| `jira-skill` | Python | v1.1.0 | ~3K | 76 | Jira/GitLab management library (JQL, boards, sprints, issues, webhooks) |
| `jira-epic-report` | Python | v2.0.0 | 8,904 | 368 (80% cov) | Epic analysis CLI with 8 analyzers + 5 reporters |
| `jira-daily-reports-skill` | Bash/acli | v1.1 | ~600 | 0 | 9 cron-ready daily report scripts |

All three load credentials from `~/.tdt/.env` and target the same Jira instance (psplit.atlassian.net / POEMS2).

---

## Question

Should we merge `jira-epic-report` (and the bash daily reports) into `jira-skill` to create a single full-Python project?

---

## Options Evaluated

### Option A: Merge Everything into jira-skill (Monorepo)

```
jira-skill/
├── src/jira_skill/
│   ├── config.py          # Shared JiraConfig
│   ├── gitlab/            # GitLab integration
│   ├── jql/               # JQL builder
│   ├── board/             # Board management
│   ├── sprint/            # Sprint operations
│   ├── issue/             # Issue management
│   ├── reports/           # NEW: merged from jira-epic-report
│   │   ├── analyzers/    # 8 analyzers
│   │   ├── reporters/    # 5 output formats
│   │   ├── daily/        # 9 daily reports (migrated from bash)
│   │   └── collector.py
│   └── ...
└── pyproject.toml         # Single dependency tree
```

**Pros:**
- Single auth/config (JiraConfig already exists)
- Reports can use JQL builder, board/sprint models directly
- One dependency tree, one CI pipeline
- Daily bash scripts get type safety, tests, error handling
- Easier cross-feature integration (e.g., epic report uses sprint velocity from sprint module)
- Single `pip install` for everything

**Cons:**
- jira-epic-report is mature (v2.0.0, 368 tests, 80% coverage) — migration risk
- Coupling: changes to JQL builder could break reports
- Larger test suite (444+ tests) — slower CI
- Different release cadences forced into one version
- jira-epic-report has its own CLI entry point (typer) — needs coexistence
- Merge effort: ~2-3 days of refactoring + test migration

---

### Option B: Multi-Repo Ecosystem with Shared Core (Recommended)

```
tdt/
├── jira-skill/            # Library: JQL, boards, sprints, issues, GitLab
├── jira-epic-report/      # CLI: Epic analysis (depends on jira-skill)
├── jira-daily-reports/    # NEW Python project: 9 daily reports (replaces bash)
└── tdt-jira-core/         # OPTIONAL: shared auth/config if needed
```

Or simpler (no extra package):

```
tdt/
├── jira-skill/            # Library + shared config (JiraConfig, GitlabConfig)
├── jira-epic-report/      # CLI: depends on jira-skill for auth + JQL
└── jira-daily-reports/    # NEW: Python daily reports, depends on tdt-core[jira]
```

**Pros:**
- Each project stays focused (single responsibility)
- jira-epic-report keeps its maturity, tests, coverage untouched
- Independent versioning and release cycles
- Smaller, faster test suites per project
- Lower risk — no big-bang migration
- jira-skill becomes a reusable library other tools depend on
- Daily reports get a clean Python rewrite without legacy baggage

**Cons:**
- Multiple `pyproject.toml` files to maintain
- Cross-project dependency management (version pinning)
- Slightly more complex dev setup (multiple venvs or workspace install)
- Some code duplication possible if not careful

---

### Option C: Merge Only Daily Reports into jira-skill, Keep epic-report Separate

```
tdt/
├── jira-skill/            # Library + daily reports (migrated from bash)
│   └── src/jira_skill/
│       └── daily_reports/ # 9 Python daily reports
├── jira-epic-report/      # Stays independent (mature, stable)
```

**Pros:**
- Daily bash scripts get proper Python rewrite inside jira-skill
- jira-epic-report stays untouched (no migration risk)
- jira-skill gains useful reporting features
- Moderate effort (~1-2 days)

**Cons:**
- jira-skill grows in scope (library + reports)
- epic-report still has its own config/auth (duplication)

---

## Recommendation: Option B (Ecosystem with jira-skill as shared library)

### Rationale

1. **jira-epic-report is too mature to merge safely.** 8,904 LOC, 368 tests, 80% coverage, v2.0.0. Merging risks regressions for zero functional gain. The effort-to-value ratio is poor.

2. **jira-skill is a natural shared library.** It already has `JiraConfig`, `JiraClientFactory`, JQL builder, and typed models. Other projects should *depend on it*, not absorb into it.

3. **Daily bash reports should become a new Python project** that depends on `tdt-core[jira]` for auth and Jira API access. This gives them type safety, tests, and proper error handling without bloating jira-skill.

4. **Separation enables independent evolution.** Epic reports might add PDF generation or new analyzers. Daily reports might add Slack webhooks. Neither should block the other.

5. **The workspace IS the monorepo.** The tdt workspace already provides the monorepo benefits (shared .env, co-located code, cross-project visibility) without forcing a single Python package.

### Migration Path

```
Phase 1 (Now): Make jira-skill installable as a library
  - Add proper package exports for JiraConfig, JQL builder
  - Publish as path dependency: jira-skill = {path = "../jira-skill"}

Phase 2 (1-2 days): Create jira-daily-reports Python project
  - New project: tdt/jira-daily-reports/
  - Depends on jira-skill for auth + JQL
  - Migrate 9 bash scripts → Python with typer CLI
  - Add tests, cron integration

Phase 3 (Optional): Wire jira-epic-report to use jira-skill
  - Replace AppConfig.from_env() with JiraConfig.from_env()
  - Use jira-skill's JQL builder instead of raw JQL strings
  - Gradual, non-breaking changes
```

### Dependency Graph

```
jira-skill (library)
    ↑              ↑
    |              |
jira-epic-report   jira-daily-reports
(CLI tool)         (CLI tool / cron)
```

---

## Decision Criteria Summary

| Criterion | Merge (A) | Ecosystem (B) | Partial (C) |
|-----------|-----------|---------------|-------------|
| Migration risk | 🔴 High | 🟢 Low | 🟡 Medium |
| Code reuse | 🟢 Maximum | 🟢 Good (via deps) | 🟡 Partial |
| Maintenance burden | 🟡 One project | 🟡 Multiple projects | 🟡 Mixed |
| Test isolation | 🔴 Coupled | 🟢 Independent | 🟡 Mixed |
| Release flexibility | 🔴 Locked | 🟢 Independent | 🟡 Mixed |
| Effort to implement | 🔴 3+ days | 🟢 1-2 days | 🟢 1-2 days |
| Future extensibility | 🟡 Monolith risk | 🟢 Composable | 🟡 OK |

---

## Next Steps (if approved)

1. Make jira-skill installable as path dependency
2. Create `tdt/jira-daily-reports/` project scaffold
3. Migrate first 3 critical bash reports to Python
4. Wire jira-epic-report to optionally use jira-skill's JiraConfig
5. Update openspec with implementation tasks
