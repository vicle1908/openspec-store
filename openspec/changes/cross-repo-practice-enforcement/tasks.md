# Tasks: Cross-Repo Practice Enforcement

## Phase 1: Create Template and Scripts (3 tasks)

- [ ] 1.1 Create workspace-python-template/ at ~/Developer/ with canonical pyproject.toml, .pre-commit-config.yaml, and check-enforcement.sh script
- [ ] 1.2 Verify template passes all gates: ruff check, ruff format --check, mypy --strict, pytest
- [ ] 1.3 Commit template to openspec-store as reference artifact

## Phase 2: Standardize Tool Versions (4 tasks)

- [ ] 2.1 Update ruff version to >=0.16.0 in all 16 repos' [dependency-groups]
- [ ] 2.2 Update mypy version to >=2.3.0 in all 16 repos' [dependency-groups]
- [ ] 2.3 Update pytest version to >=9.1.1 in all 16 repos' [dependency-groups]
- [ ] 2.4 Run `uv lock` in each repo to regenerate lockfiles with new versions

## Phase 3: Standardize Ruff Config (3 tasks)

- [ ] 3.1 Update ruff lint select rules to canonical set in repos with drift: agent-core, agent-docs-sync, browser-cli, tdt-observability, tdt-sheets, ai-harness-skills
- [ ] 3.2 Normalize ruff ignore rules to canonical baseline (E501 only) — evaluate per-repo overrides case by case
- [ ] 3.3 Verify `uv run ruff check .` passes in all 16 repos after rule changes

## Phase 4: Add Pre-Commit to Missing Repos (2 tasks)

- [ ] 4.1 Create .pre-commit-config.yaml from template in: ai-harness-skills, code-daily-scan, tdt-observability, tdt-sheets
- [ ] 4.2 Install and verify pre-commit hooks pass in those 4 repos

## Phase 5: Standardize Existing Pre-Commit Configs (2 tasks)

- [ ] 5.1 Update 12 repos with pre-commit to use canonical template (add mypy+pytest hooks where missing, standardize hook IDs from `ruff` to `ruff-check`)
- [ ] 5.2 Verify `pre-commit run --all-files` passes in all 12 repos

## Phase 6: Cross-Repo Dependency Contracts (2 tasks)

- [ ] 6.1 Audit tdt-core version constraints across 12 consumers — ensure >=X.Y,<X.(Y+1) pattern
- [ ] 6.2 Add workspace-level enforcement script at ~/Developer/scripts/check-enforcement.sh

## Phase 7: Validation and Documentation (3 tasks)

- [ ] 7.1 Run full enforcement script across all 16 repos — verify zero drift
- [ ] 7.2 Update AGENTS.md store stats and workspace documentation
- [ ] 7.3 Commit all changes per-repo and archive openspec change
