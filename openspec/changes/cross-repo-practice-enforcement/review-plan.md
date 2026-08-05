# Plan Review: Cross-Repo Practice Enforcement (v2)

**Reviewed:** 2026-08-05 (5-provider parallel review)
**Providers:** 5 parallel reviewers (factual accuracy, security, task completeness, architecture, scope)
**Context:** Updated artifacts after initial review found factual errors in v1 proposal

## Alignment Summary

| Edge | Status | Evidence |
|------|--------|----------|
| Spec ↔ Code | ✅ PASS | skip_specs: true; no spec deltas needed |
| Code ↔ Tests | ✅ PASS | 24 tasks across 8 phases; all repos have test suites |
| Code ↔ Docs | ✅ PASS | proposal/design/tasks align; accurate version tables |
| Skills ↔ Code | ✅ PASS | python-project-maintenance skill aligns with approach |
| Skills ↔ Specs | ✅ PASS | N/A (skip_specs) |
| Specs ↔ Docs | ✅ PASS | N/A (skip_specs) |
| Security ↔ All | ⚠️ PARTIAL | S rule violations across all repos; unpinned deps in 7 repos |
| CI ↔ Code | ⚠️ PARTIAL | CI platforms vary (GitHub/GitLab/neither); no CI template in scope |

## Consolidated Findings

### CRITICAL (1)

**C1: Ruff S rule violations across ALL repos will block execution**
- Enabling `select = [..., "S", ...]` fires violations in every repo's source code
- Non-S101 violations per repo: agent-core: 24, ai-review: 62, jira-skill: 48, code-daily-scan: 24, jira-epic-report: 22, tdt-core: 19, jira-daily-reports: 15, ai-harness-skills: 12, browser-cli: 10, jira-kanban: 7
- **Examples**: S603 (subprocess injection), S310 (URLlib open), S108 (hardcoded paths), S110 (try-except-pass), S324 (md5), S105/S106 (hardcoded passwords)
- These are REAL security findings, not false positives
- **Resolution**: Task 3.3 must include `uv run ruff check . --fix` first pass, then triage remaining violations: fix real issues, add targeted per-file-ignores for known-safe patterns

### HIGH (4)

**H1: Hook ID discrepancy across repos**
- agent-core, agent-docs-sync, agent-harness use hook ID `ruff-check`
- All other repos use hook ID `ruff`
- Canonical template uses `ruff`
- **Resolution**: Task 5.1 must normalize agent-* repos from `ruff-check` → `ruff`

**H2: Unpinned cross-repo dependencies (more repos than initially identified)**
- agent-harness: agent-core (no version), tdt-core[scheduler,jira] (no version)
- ai-review: tdt-core[gitlab,scheduler] (no version)
- code-daily-scan: agent-core (no version), tdt-core[gitlab] (no version), tdt-sheets (no version)
- jira-daily-reports: jira-skill (no version)
- webhook-receiver: tdt-core[gitlab,scheduler] (no version), jira-skill (no version)
- **Resolution**: Task 6.1 must cover ALL 7 repos with unpinned deps (not just the 4 initially listed)

**H3: tdt-observability has outdated tool config**
- Missing `target-version = "py314"` in ruff config (uses default)
- Has `mypy>=1.14.0` in dev deps (should be >=2.3.0)
- Has duplicate pytest entries in dependency-groups
- No pre-commit hooks
- **Resolution**: Task 0.4 (pilot evaluation) should also check tdt-observability as a edge case

**H4: ai-review uses older pre-commit-hooks**
- ai-review uses pre-commit-hooks v5.0.0 (not v6.0.0)
- **Resolution**: Task 5.2 must update ai-review's pre-commit-hooks rev

### MEDIUM (3)

**M1: Per-file-ignores need more granular handling**
- The canonical `"tests/**/*.py"` ignore list is a good base
- But repos have source-specific ignores (e.g., tdt-sheets scripts/, jira-epic-report reporters/)
- Template README must document the override pattern clearly
- **Resolution**: Task 3.2 should reference the template README for override documentation

**M2: ruff --fix may not resolve all S violations**
- Some S violations (S603, S108) are real issues requiring code changes
- Others (S105, S106 in test fixtures) are acceptable patterns
- Task 3.3 should distinguish between auto-fixable and manual-fix violations
- **Resolution**: Add guidance to task 3.3: `ruff check . --fix` first, then manual triage

**M3: code-daily-scan has bash scripts but no pre-commit**
- Has deploy.sh, scan-ewallet-android.sh, scan-ewallet-ios.sh
- Should get shellcheck in its pre-commit config
- **Resolution**: Task 4.1 should include shellcheck for code-daily-scan

### LOW (2)

**L1: tdt-observability has duplicate pytest entries**
- `pytest>=9.0.0` and `pytest>=9.1.1` both in dependency-groups
- Should be cleaned up during version standardization
- **Resolution**: Task 2.3 should clean duplicate entries

**L2: Enforcement script grep pattern may need refinement**
- The canonical version check uses exact string matching (`"ruff>=0.16.1"`)
- Some repos use different formatting (spaces, quotes)
- **Resolution**: Task 7.1 should verify the script works across all formatting variants

## Recommended Actions

1. **Before execution**: Create a S violation triage plan — decide which violations to fix vs ignore
2. **Phase 0 pilot**: Include tdt-observability as a 4th edge-case repo (not just agent-core, tdt-core, jira-skill)
3. **Task 6.1**: Expand scope to cover ALL 7 unpinned repos (agent-harness, ai-review, code-daily-scan, jira-daily-reports, webhook-receiver + jira-skill)
4. **Task 5.1**: Normalize hook IDs from `ruff-check` → `ruff` in agent-* repos
5. **Task 3.3**: Add S violation triage step after `ruff --fix`
