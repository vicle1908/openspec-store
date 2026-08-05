# Review Plan: Cross-Repo Practice Enforcement

## Reviewer Summary

| # | Lens | Provider | Status | Key Finding |
|---|------|----------|--------|-------------|
| 1 | Tool Version & Config Consistency | hermes | ✅ Complete (auth error on final) | mypy strict flags redundant; versions confirmed latest |
| 2 | Security & Dependency Risks | hermes | ✅ Complete (auth error on final) | S rules safe; missing version pins in jira-* repos |
| 3 | Task Completeness & Execution | hermes | ✅ Complete (auth error on final) | Missing pilot phase, rollback, CI template |
| 4 | Architecture & Cross-Repo Impact | hermes | ✅ Complete (auth error on final) | CI platforms vary; prek available on PyPI |
| 5 | Product Scope & OpenSpec Compliance | hermes | ✅ Complete (auth error on final) | skip_specs appropriate; scope well-bounded |

## 8-Edge Alignment Matrix

| Edge | Status | Notes |
|------|--------|-------|
| Spec ↔ Code | ✅ PASS | skip_specs: true; no spec deltas needed |
| Code ↔ Tests | ✅ PASS | 507 tests across 16 repos; enforcement adds test gates |
| Code ↔ Docs | ✅ PASS | proposal/design/tasks are the docs |
| Skills ↔ Code | ✅ PASS | python-project-maintenance skill aligns with approach |
| Skills ↔ Specs | ✅ PASS | No spec deltas |
| Specs ↔ Docs | ✅ PASS | N/A (skip_specs) |
| Security ↔ All | ⚠️ PARTIAL | Missing version pins in jira-*; S rules need per-file-ignores for tests |
| CI ↔ Code | ⚠️ PARTIAL | CI platforms vary (GitHub/GitLab/neither); no CI template in tasks |

## Consolidated Findings

### CRITICAL (0)
None.

### HIGH (3)

**H1: Missing version pins in cross-repo dependencies**
- `jira-skill`: `tdt-core[all]` and `tdt-sheets` have NO version pin
- `jira-daily-reports`: `jira-skill` has NO version pin
- `jira-epic-report`: `jira-skill` has NO version pin
- `jira-kanban-from-spreadsheet`: `tdt-core`, `tdt-sheets` have NO version pin
- **Resolution**: Task 6.1 must audit and add `>=X.Y,<X.(Y+1)` to ALL cross-repo deps

**H2: Ruff S rules need per-file-ignores for tests**
- `S101` (assert) fires in every test file
- `agent-harness` already has the correct pattern: `"tests/**/*.py" = ["S101"]`
- **Resolution**: Canonical template must include test-specific S ignores

**H3: Missing pilot phase**
- Applying all 16 repos simultaneously is high-risk
- Ruff rule additions + mypy version jumps may surface hundreds of new violations
- **Resolution**: Add Phase 0 (pilot on 2-3 repos: agent-core, tdt-core, jira-skill)

### MEDIUM (5)

**M1: mypy strict config is partially redundant**
- `strict = true` already enables: `warn_return_any`, `disallow_untyped_defs`, `disallow_any_generics`, `check_untyped_defs`, `no_implicit_reexport`, `warn_redundant_casts`, `warn_unused_ignores`
- Only `warn_unused_configs` is NOT in strict mode
- **Resolution**: Simplify to `strict = true` + `warn_unused_configs = true`

**M2: CI platform variation**
- agent-core/agent-docs-sync/agent-harness: GitHub Actions
- jira-daily-reports/jira-epic-report/jira-skill/jira-kanban: GitLab CI
- ai-harness-skills/ai-review/browser-cli/code-daily-scan: Neither
- **Resolution**: Add task for CI workflow template (or document that enforcement is local-only)

**M3: pre-commit rev versions need real values**
- Design uses `v8.x.x`, `v5.x.x` placeholders
- Actual latest: gitleaks v8.30.0, pre-commit-hooks v6.0.0, ruff-pre-commit v0.16.0
- **Resolution**: Update design with real rev values

**M4: Shellcheck removal may leave gap**
- jira-* repos have bash scripts (deploy.sh, etc.)
- Shellcheck is currently enforced via pre-commit
- However, jira-* bash scripts are in scripts/ not src/, and are deployment-only
- **Resolution**: Keep shellcheck in jira-* repos; add it to canonical template for repos with bash scripts

**M5: `uv run --frozen` correctness**
- `--frozen` = use lockfile without checking if up-to-date (correct for hooks)
- `--locked` = check lockfile is up-to-date, error if not (better for CI)
- Existing agent-core hooks already use `--frozen` (validated)
- **Resolution**: Keep `--frozen` for hooks; recommend `--locked` for CI

### LOW (3)

**L1: prek is available on PyPI**
- Can be installed via `uv tool install prek`
- Drop-in replacement for pre-commit
- Workspace-aware hooks
- **Resolution**: Note as future option; not in scope for this change

**L2: Bash scripts exist in multiple repos**
- agent-core: 4 scripts (docker-dev.sh, etc.)
- code-daily-scan: 2 scripts
- jira-daily-reports: 1 script
- jira-skill: 1 script (deploy.sh)
- **Resolution**: Canonical template should include shellcheck for repos with bash scripts

**L3: .python-version files are consistent**
- All checked repos use 3.14.5
- **Resolution**: No action needed; already aligned

## Artifact Updates Required

1. **design.md**: Update mypy config to simplified strict mode; add real pre-commit rev values; add S per-file-ignores for tests; note shellcheck for repos with bash scripts
2. **tasks.md**: Add Phase 0 (pilot); add task for missing version pins; add CI template task; update ruff config task to include S per-file-ignores
3. **proposal.md**: Add H1 finding about missing version pins

## Archive Readiness

**NOT READY** — 3 HIGH findings require artifact updates before execution:
1. Missing version pins (H1) — must be in tasks
2. Ruff S per-file-ignores (H2) — must be in design
3. Pilot phase (H3) — must be in tasks

After updates: READY for execution.
