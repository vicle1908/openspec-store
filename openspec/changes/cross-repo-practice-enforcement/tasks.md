# Tasks: Cross-Repo Practice Enforcement

## Phase 0: Pilot on 3 Repos (4 tasks)

- [x] 0.1 Apply full enforcement to **agent-core** (69 tests, GitHub Actions, Pattern A)
  - Update dependency-group versions: ruff>=0.16.1, mypy>=2.3.0, pytest>=9.1.1
  - Update pre-commit revs: ruff-pre-commit v0.15.15→v0.16.1, gitleaks v8.30.1
  - Add uv-pre-commit hook for lockfile sync
  - Run `uv lock` to regenerate lockfile
  - Verify: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`, `uv run pytest -q`
- [x] 0.2 Apply full enforcement to **tdt-core** (20 tests, GitLab CI, hub dependency)
  - Same gates as 0.1
  - Critical: any break here cascades to 12 consumers
  - Update pre-commit revs to match canonical
- [x] 0.3 Apply full enforcement to **jira-skill** (90 tests, GitLab CI, most cross-deps)
  - Same gates as 0.1
  - Fix missing version pins on tdt-core[all] and tdt-sheets (HIGH finding from review)
  - Update pre-commit revs: gitleaks v8.30.0→v8.30.1, ruff-pre-commit v0.16.0→v0.16.1
  - Keep shellcheck/shfmt/actionlint (Pattern C)
- [x] 0.4 Evaluate pilot results
  - Document violations found per repo (especially S rule violations)
  - Document time to fix
  - Document any rule adjustments needed for the canonical set
  - If mypy 2.3.0 surfaces many new errors, add `[[tool.mypy.overrides]]` for third-party gaps
  - **Triage S violations**: categorize as fix vs per-file-ignore (S603 subprocess in scripts, S108 hardcoded paths, S110 try-except-pass are common patterns)

## Phase 1: Create Template and Scripts (3 tasks)

- [ ] 1.1 Create `~/Developer/workspace-python-template/` with:
  - `pyproject.toml` — canonical [tool.ruff], [tool.mypy], [tool.pytest.ini_options], [dependency-groups]
  - `.pre-commit-config.yaml` — canonical hook layout (gitleaks v8.30.1, ruff v0.16.1, uv-pre-commit, mypy, pytest, pre-commit-hooks v6.0.0)
  - `scripts/check-enforcement.sh` — workspace-level drift checker
  - `README.md` — usage instructions and adoption checklist with override documentation
- [ ] 1.2 Verify template passes all gates: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`
- [ ] 1.3 Commit template

## Phase 2: Standardize Tool Versions (4 tasks)

- [ ] 2.1 Update ruff version floor to `>=0.16.1` in all 16 repos' `[dependency-groups]`
  - Run `uv lock` in each repo to regenerate lockfiles
  - Verify `uv run ruff check .` passes in each repo
- [ ] 2.2 Update mypy version floor to `>=2.3.0` in all 16 repos' `[dependency-groups]`
  - Run `uv lock` in each repo
  - Verify `uv run mypy .` passes (or add overrides for third-party gaps)
- [ ] 2.3 Update pytest version floor to `>=9.1.1` (and pytest-asyncio>=1.4.0) in all 16 repos
  - Run `uv lock` in each repo
  - Verify `uv run pytest -q` passes
  - **tdt-observability**: clean up duplicate pytest entries in dependency-groups
- [ ] 2.4 Run `uv run --frozen` in all repos to verify lockfile sync

## Phase 3: Standardize Ruff Config (3 tasks)

- [ ] 3.1 Update ruff lint select rules to canonical 19-rule set in repos with drift:
  - agent-core: already 19 rules — verify alignment with canonical
  - agent-docs-sync: 25 rules → 19 canonical + repo-specific extras
  - browser-cli: 8 rules → 19 canonical
  - tdt-observability: 9 rules → 19 canonical
  - ai-harness-skills: 7 rules → 19 canonical
  - agent-harness: 14 rules → 19 canonical (add ARG, SLF)
  - tdt-sheets: 13 rules → 19 canonical + keep repo-specific per-file-ignores
  - code-daily-scan: 12 rules → 19 canonical + keep repo-specific per-file-ignores
- [ ] 3.2 Add canonical per-file-ignores to all repos:
  - `"__init__.py" = ["F401"]`
  - `"tests/**/*.py" = ["F841", "B007", "E402", "S101", "S108", "ARG001", "ARG002", "SLF001"]`
  - Keep existing repo-specific overrides (document in template README)
- [ ] 3.3 Run `uv run ruff check . --fix` then `uv run ruff check .` in all 16 repos
  - First pass: `--fix` auto-fixes safe violations
  - Second pass: triage remaining S violations — fix real issues (S603 subprocess, S108 hardcoded paths), add per-file-ignores for known-safe patterns (S105/S106 test fixtures, S110 intentional try-except-pass)
  - Record triage decisions in commit messages

## Phase 4: Add Pre-Commit to Missing Repos (2 tasks)

- [ ] 4.1 Create `.pre-commit-config.yaml` from canonical template in: ai-harness-skills, code-daily-scan (add shellcheck for bash scripts), tdt-observability, tdt-sheets
- [ ] 4.2 Install and verify: `uv run pre-commit install && uv run pre-commit run --all-files`

## Phase 5: Standardize Existing Pre-Commit Configs (3 tasks)

- [ ] 5.1 Update Pattern A repos (agent-core, docs-sync, harness) — update revs to canonical:
  - ruff-pre-commit v0.15.15 → v0.16.1
  - Add uv-pre-commit hook
  - Add pre-commit-hooks v6.0.0
  - Keep local mypy/pytest hooks with `uv run --frozen`
  - Hook ID already correct (`ruff-check`) — no change needed
- [ ] 5.2 Update Pattern B repos (ai-review, tdt-core, webhook-receiver) — add local mypy/pytest hooks:
  - Add uv run --frozen mypy + pytest local hooks
  - Add uv-pre-commit hook
  - Update ruff-pre-commit to v0.16.1
  - **Normalize hook ID**: `ruff` (legacy) → `ruff-check` (official current ID per astral-sh/ruff-pre-commit)
  - **ai-review**: update pre-commit-hooks v5.0.0 → v6.0.0
- [ ] 5.3 Update Pattern C repos (jira-\*, browser-cli, ops-auto) — update revs:
  - Update gitleaks v8.30.0 → v8.30.1
  - Update ruff-pre-commit v0.16.0 → v0.16.1
  - Add uv-pre-commit hook
  - **Normalize hook ID**: `ruff` (legacy) → `ruff-check` (official current ID)
  - Keep shellcheck/shfmt/actionlint

## Phase 6: Cross-Repo Dependency Contracts (2 tasks)

- [ ] 6.1 Audit and fix missing version pins across ALL cross-repo dependencies:
  - **jira-skill**: add `>=0.3,<0.4` to tdt-core[all] and `>=0.1,<0.2` to tdt-sheets
  - **code-daily-scan**: add `>=0.3,<0.4` to tdt-core[gitlab] and agent-core, `>=0.1,<0.2` to tdt-sheets
  - **webhook-receiver**: add `>=0.3,<0.4` to tdt-core[gitlab,scheduler] and jira-skill
  - **agent-harness**: add `>=0.2,<0.3` to agent-core, `>=0.3,<0.4` to tdt-core[scheduler,jira]
  - **ai-review**: add `>=0.3,<0.4` to tdt-core[gitlab,scheduler]
  - **jira-daily-reports**: add `>=0.3,<0.4` to jira-skill (currently unpinned)
  - **agent-docs-sync**: verify agent-core pin uses proper range (has >=0.2.0 but no upper bound)
  - Ensure `>=X.Y,<X.(Y+1)` pattern for ALL cross-repo deps
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
