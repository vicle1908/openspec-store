# Tasks: Cross-Repo Practice Enforcement

## Phase 0: Pilot on 3 Repos (3 tasks)

- [ ] 0.1 Apply full enforcement to **agent-core** (69 tests, GitHub Actions, already has S rules)
  - Verify ruff 0.16.0 + canonical rules pass
  - Verify mypy 2.3.0 --strict passes
  - Verify pre-commit hooks pass
- [ ] 0.2 Apply full enforcement to **tdt-core** (20 tests, GitLab CI, hub dependency)
  - Same gates as 0.1
  - Critical: any break here cascades to 12 consumers
- [ ] 0.3 Apply full enforcement to **jira-skill** (90 tests, GitLab CI, most cross-deps)
  - Same gates as 0.1
  - Fix missing version pins (H1 finding)
- [ ] 0.4 Evaluate pilot results: document violations found, time to fix, rule adjustments needed

## Phase 1: Create Template and Scripts (3 tasks)

- [ ] 1.1 Create `~/Developer/workspace-python-template/` with:
  - `pyproject.toml` — canonical [tool.ruff], [tool.mypy], [tool.pytest.ini_options], [dependency-groups]
  - `.pre-commit-config.yaml` — canonical hook layout (gitleaks v8.30.0, ruff v0.16.0, mypy, pytest, pre-commit-hooks v6.0.0)
  - `check-enforcement.sh` — workspace-level drift checker (version audit + gate runner)
  - `README.md` — usage instructions and adoption checklist
- [ ] 1.2 Verify template passes all gates: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`
- [ ] 1.3 Commit template to openspec-store as reference artifact

## Phase 2: Standardize Tool Versions (4 tasks)

- [ ] 2.1 Update ruff version floor to `>=0.16.0` in all 16 repos' `[dependency-groups]`
  - **Risk**: ruff 0.16 may flag new violations in repos currently on 0.5.0/0.8.4
  - **Mitigation**: Pilot results from Phase 0 guide ignore list additions
- [ ] 2.2 Update mypy version floor to `>=2.3.0` in all 16 repos' `[dependency-groups]`
  - **Risk**: mypy 2.x has different strict behavior vs 1.x
  - **Mitigation**: Pilot results from Phase 0; add `[[tool.mypy.overrides]]` for third-party gaps
- [ ] 2.3 Update pytest version floor to `>=9.1.1` in all 16 repos' `[dependency-groups]`
  - **Risk**: Low — pytest 9.x is backward compatible
- [ ] 2.4 Run `uv lock` in each repo to regenerate lockfiles with new versions

## Phase 3: Standardize Ruff Config (3 tasks)

- [ ] 3.1 Update ruff lint select rules to canonical 17-rule set in repos with drift:
  - agent-core (EMPTY → full set)
  - agent-docs-sync (25 rules → 17 canonical + evaluate extras)
  - browser-cli (8 rules → 17 canonical)
  - tdt-observability (9 rules → 17 canonical)
  - tdt-sheets (EMPTY → full set)
  - ai-harness-skills (7 rules → 17 canonical)
  - agent-harness (14 rules → 17 canonical, add S, PTH, PIE, PT)
- [ ] 3.2 Add per-file-ignores to canonical template:
  - `"__init__.py" = ["F401"]`
  - `"tests/**/*.py" = ["F841", "B007", "E402", "S101"]`
  - Evaluate per-repo ignores from pilot results
- [ ] 3.3 Run `uv run ruff check . --fix` then `uv run ruff check .` in all 16 repos

## Phase 4: Add Pre-Commit to Missing Repos (2 tasks)

- [ ] 4.1 Create `.pre-commit-config.yaml` from template in: ai-harness-skills, code-daily-scan, tdt-observability, tdt-sheets
- [ ] 4.2 Install and verify: `uv run pre-commit install && uv run pre-commit run --all-files`

## Phase 5: Standardize Existing Pre-Commit Configs (2 tasks)

- [ ] 5.1 Update 12 repos with pre-commit to canonical template:
  - Normalize hook IDs: `ruff` → `ruff` (already correct in some)
  - Add `uv run --frozen` prefix to mypy/pytest entries
  - Add mypy+pytest hooks where missing (ai-review, browser-cli, tdt-core, webhook-receiver)
  - Keep shellcheck for repos with bash scripts (jira-skill, jira-daily-reports)
  - Add pre-commit-hooks: trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-added-large-files, detect-private-key
- [ ] 5.2 Run `uv run pre-commit run --all-files` in all 12 repos

## Phase 6: Cross-Repo Dependency Contracts (2 tasks)

- [ ] 6.1 Audit and fix missing version pins across all cross-repo dependencies:
  - jira-skill: add version pins to `tdt-core[all]` and `tdt-sheets`
  - jira-daily-reports: add version pin to `jira-skill`
  - jira-epic-report: add version pin to `jira-skill`
  - jira-kanban-from-spreadsheet: add version pins to `tdt-core`, `tdt-sheets`
  - Ensure `>=X.Y,<X.(Y+1)` pattern for ALL cross-repo deps
  - Ensure extras are explicitly declared (e.g., `[jira,scheduler]`)
- [ ] 6.2 Verify `uv run --frozen` works in all repos (lockfile sync check)

## Phase 7: Validation and Documentation (3 tasks)

- [ ] 7.1 Run `check-enforcement.sh` across all 16 repos — verify zero drift
- [ ] 7.2 Update workspace documentation (AGENTS.md if needed)
- [ ] 7.3 Commit all changes per-repo, then archive openspec change:
  ```
  cd ~/Developer/openspec-store
  openspec archive cross-repo-practice-enforcement --store openspec-store --yes
  git add openspec/
  git commit -m "archive: cross-repo-practice-enforcement"
  ```
