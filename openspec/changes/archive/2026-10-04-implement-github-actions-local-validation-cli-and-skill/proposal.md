# Proposal: Comprehensive Local GitHub Actions Validation CLI, Pre-Push Enforcement, and Agent Skill

## Why
While PRs #43 through #51 established a 4-tier parallel matrix DAG, native setup-go caching, and pre-push hooks for agent guidance, docs, and coverage parity, an operational blind spot remains:
- `make pre-push` and `.githooks/pre-push` do NOT validate GitHub Actions workflow modifications.
- If a developer or autonomous agent modifies `.github/workflows/*.yml`—introducing YAML syntax errors, unpinned actions, retention day deviations, malformed expressions, invalid triggers, or renaming the branch protection anchor `PR gate (verify-pr)`—`make pre-push` passes locally.
- The failure is only discovered after pushing to GitHub and waiting minutes for the remote runner.

## What Changes
1. **Unified CLI Tool (`scripts/validate-workflows.py`)**:
   - Create a comprehensive, deterministic Python CLI tool validating all repository workflows:
     - Check 1: Structural YAML parsing & duplicate key check.
     - Check 2: AST and shell validation via `actionlint` and `shellcheck`.
     - Check 3: 40-character commit SHA action pinning via `tools/actionpin/actionpin.py`.
     - Check 4: Artifact retention days baseline verification via `scripts/verify-retention.py`.
     - Check 5: PR-scoped concurrency block validation (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`).
     - Check 6: Explicit PR trigger lifecycle validation (`branches: [main]`, `types: [opened, synchronize, reopened]`).
     - Check 7: Branch protection invariant check preserving `PR gate (verify-pr)`.
     - Check 8: Security scanning via `zizmor` (offline mode) if available.
2. **Makefile & Pre-Push Integration**:
   - Add target `make validate-workflows` to root `Makefile`.
   - Wire `validate-workflows` directly into `make pre-push` so any workflow edit is verified locally in < 2 seconds before push.
3. **Reusable Agent Skill (`github-actions-validation`)**:
   - Author `.agents/skills/github-actions-validation/SKILL.md` in workspace skills.
   - Synchronize via `scripts/sync-workspace-agent-skills.py`.
4. **Documentation**:
   - Update `docs/runbooks/ci-cd-operations.md` and `docs/README.md`.

## Impact
- **Services Affected**: Tooling and documentation in `go-microservices`.
- **Breaking Changes**: None. Zero runtime impact.
