# Plan Review Round 2: harden-ci-supply-chain

**Reviewed:** 2026-08-04
**Frozen target:** `origin/main` at `abdc7c12369bbc6b2ff3f10267793912832457ca`
**Verdict:** FAIL — semantic and testability corrections remain

## Provider Results

- Hermes: **FAIL**
- Claude Code 2.1.220: **PARTIAL** (exit 0)
- Codex CLI 0.146.0: **FAIL** (read-only equivalent invocation exit 0; requested unsupported flag invocation exit 2)
- Antigravity 1.1.10 / gemini-3.1-pro-high: **PARTIAL** (exit 0, JSON SUCCESS)
- fable-5 slot: requested `/opt/homebrew/bin/fable-5` unavailable (exit 127); genuine installed `/opt/homebrew/bin/kimi` 0.31.1 used instead: **FAIL** (exit 0)

## Agreed Blocking Findings

1. The action inventory is wrong: the frozen repository has 11 workflow files, 60 remote `uses:` occurrences, and 13 distinct remote actions. Root workflows alone have 50 occurrences. Three order-service workflow files were omitted from scope.
2. The proposed Gitleaks action placeholder is not executable and the review disagreed on its release version. Live upstream verification now confirms `gitleaks/gitleaks-action` v3.0.0 exists at commit `e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e`, but a pinned Gitleaks CLI is preferable for deterministic reports and licensing independence.
3. The Go module inventory is wrong: the frozen target has 18 tracked `go.mod` files, including `verification/fixtures/temporal-determinism/nondeterministic/go.mod`.
4. Dynamic module discovery alone cannot detect a deleted expected module; use a committed expected-set manifest and compare exact sets before running `go mod verify`.
5. Scorecard needs a dedicated report-only workflow, exact CLI version/checksum, token mapping, least privileges, expected JSON schema, artifact assertion, and explicit failure semantics.
6. Dependabot needs an exact cooldown value/schema and acceptance evidence. “No automerge” must be grounded in branch protection/repository settings, not asserted as a Dependabot setting.
7. The repository has no `github-actions-ci` skill. The actual canonical skill is the active-profile skill at `~/.hermes/skills/software-development/github-actions-ci/`; scope and verification must name that path explicitly.
8. The proposed four phases drift between proposal, design, tasks, and rollback. Enforcement and rollback targets are inconsistent.
9. Rollback to mutable tags is unsafe. A bad action update must roll back to a previous known-good commit SHA while retaining the pin policy.
10. Acceptance criteria are not executable enough: add positive/negative pin tests, retention preservation checks, synthetic Gitleaks detection, exact module-set failure tests, Scorecard JSON/artifact checks, Dependabot policy checks, documentation currency checks, and rollback rehearsal.
11. The implementation scope omits `.gitleaksignore`, verification manifests, tooling/scripts, global skill, and order-service workflow templates.

## Required Round-3 Shape

- Phase 1: pin all 60 existing remote references, add a committed action lock manifest, add a repository-owned pin validator with tests, and configure Dependabot cooldown.
- Phase 2: add pinned Gitleaks CLI in a dedicated warn-only workflow, retain a redacted report for 30 days, and prove detection with a runtime-generated synthetic secret.
- Phase 3: add pinned/checksummed Scorecard CLI v5.5.0 in a dedicated report-only workflow, authenticate with read-only `GITHUB_TOKEN`, validate JSON, and retain it 30 days.
- Phase 4: add exact 18-module-set verification, update docs/currency/global skill, and promote Gitleaks to blocking only after clean baseline evidence. Scorecard remains informational.
- Every phase must have exact acceptance criteria and independent safe rollback.
