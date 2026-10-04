# Tasks: Comprehensive Local GitHub Actions Validation CLI, Pre-Push Enforcement, and Agent Skill

## 1. OpenSpec Change Authoring & Proposal

- [ ] 1.1 Author `proposal.md`, `design.md`, and `tasks.md` in `openspec-store` under `openspec/changes/implement-github-actions-local-validation-cli-and-skill/`
- [ ] 1.2 Validate change strictly using `openspec validate implement-github-actions-local-validation-cli-and-skill --strict --store openspec-store`
- [ ] 1.3 Commit and push the OpenSpec proposal to `openspec-store` `main`

## 2. CLI Tool Implementation & Makefile Integration (`go-microservices`)

- [ ] 2.1 Implement `scripts/validate-workflows.py` executing 8-point pre-flight checks:
  - Check 1: YAML structural syntax & duplicate key parsing via `yaml.SafeLoader`
  - Check 2: AST expression checking and embedded shell script linting via `actionlint` + `shellcheck`
  - Check 3: 40-character commit SHA action pinning enforcement via `tools/actionpin/actionpin.py`
  - Check 4: Artifact retention days baseline verification via `scripts/verify-retention.py`
  - Check 5: PR-scoped concurrency block validation (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`)
  - Check 6: Explicit PR trigger lifecycle validation (`branches: [main]`, `types: [opened, synchronize, reopened]`)
  - Check 7: Branch protection invariant check preserving `PR gate (verify-pr)` in `verify.yml`
  - Check 8: Optional security scan via `zizmor` (offline mode) if available
- [ ] 2.2 Add `validate-workflows` target to root `Makefile` and wire directly into `make pre-push`
- [ ] 2.3 Wire `python3 scripts/validate-workflows.py` into `.github/workflows/verify.yml` preflight tier for self-referential enforcement

## 3. Reusable Agent Skill Authoring & Synchronization

- [ ] 3.1 Author `.agents/skills/github-actions-validation/SKILL.md` detailing the 5-stage pre-flight pipeline, CLI commands, and failure prevention runbooks
- [ ] 3.2 Synchronize workspace skills via `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` and verify with `--check`

## 4. Documentation & Local Verification

- [ ] 4.1 Update `docs/runbooks/ci-cd-operations.md` and `docs/README.md` to document `make validate-workflows` and the pre-push gate
- [ ] 4.2 Run `make pre-push` locally in `go-microservices` and verify 0 violations

## 5. Pull Request Lifecycle & Pipeline Monitoring

- [ ] 5.1 Create feature branch `feat/github-actions-local-validation-cli-and-skill` in `go-microservices`
- [ ] 5.2 Commit changes, push to origin, and open GitHub Pull Request with auto-merge armed
- [ ] 5.3 Monitor PR check runs live on GitHub Actions until all required status checks pass green and auto-merge completes
- [ ] 5.4 Pull `main` in `go-microservices` and delete feature branch locally and remotely

## 6. OpenSpec Archival & Knowledge Synchronization

- [ ] 6.1 Mark all tasks completed in `openspec-store`
- [ ] 6.2 Validate strict OpenSpec compliance and archive change to `openspec/changes/archive/2026-10-04-implement-github-actions-local-validation-cli-and-skill`
- [ ] 6.3 Commit and push archived change in `openspec-store`
- [ ] 6.4 Save durable learnings in `agentmemory` and update Notion architecture guide via `ntn` CLI
