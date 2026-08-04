## Why

The frozen target (`origin/main` at `abdc7c12369bbc6b2ff3f10267793912832457ca`) has concrete GitHub Actions supply-chain gaps:

1. Eleven workflow files contain 61 remote `uses:` occurrences across 13 distinct actions. Sixty occurrences use mutable tags; the remaining Trivy reference uses an immutable tag-object SHA instead of the release commit SHA.
2. No repository-owned policy rejects mutable action references or verifies exact release-tag-to-commit provenance.
3. No secret scan runs before merge.
4. No OpenSSF Scorecard baseline is retained for the private repository.
5. Eighteen tracked Go modules have no exact-set dependency-integrity gate.
6. GitHub Actions Dependabot updates have no cooldown.

This change hardens CI tooling and configuration only. It does not alter service runtime behavior, APIs, data contracts, or deployment topology, so `skip_specs: true` remains appropriate.

## Decisions

- Pin every remote action reference in all 11 existing workflow files, including the three order-service workflow templates.
- Add a repository-owned `tools/actionpin` validator and committed `verification/github-actions-lock.json`; do not depend on an unpinned runtime installer for pin policy.
- Use Gitleaks CLI v8.30.1 verified by the upstream SHA-256 checksum, not the licensed wrapper Action. This provides deterministic redacted JSON reports without account-license ambiguity.
- Use OpenSSF Scorecard CLI v5.5.0 verified by the upstream SHA-256 checksum in a dedicated report-only workflow. The private repository has no GitHub Advanced Security, so Scorecard Action/SARIF publishing is out of scope.
- Treat all 18 tracked `go.mod` files—including the Temporal negative fixture—as the expected module set.
- Set Dependabot `cooldown.default-days: 3` for `github-actions`. Security updates remain unaffected. Existing branch protection (one approval) and `allow_auto_merge=false` remain the no-automerge controls.
- Preserve existing artifact retention tiers: verification 30 days, deployment/image evidence 90 days, release evidence 365 days. New security diagnostic reports retain for 30 days.

## Implementation Phases

1. **Immutable action policy and Dependabot hardening**
   - Pin all 61 existing remote references.
   - Add the action lock manifest and tested validator.
   - Add the 3-day GitHub Actions cooldown.
2. **Gitleaks warn-only baseline**
   - Add a dedicated `gitleaks.yml` using pinned/checksummed CLI v8.30.1.
   - Retain redacted reports for 30 days; do not block merges yet.
3. **Scorecard report-only baseline**
   - Add a dedicated `scorecard.yml` using pinned/checksummed CLI v5.5.0.
   - Run on schedule/manual dispatch, validate JSON, retain it 30 days, and keep it outside required merge checks.
4. **Module integrity, documentation, and evidence-based enforcement**
   - Add exact 18-module-set verification.
   - Update the runbook, documentation currency, and canonical active-profile skill.
   - Promote Gitleaks to a required fail-closed check only after a clean baseline and synthetic detection proof on the exact candidate commit.

Each phase is one focused commit. PR CI is observed after every phase commit; main CI is verified after merge.

## Scope

Repository-owned surfaces:

- `.github/workflows/`
- `services/order-service/.github/workflows/`
- `.github/dependabot.yml`
- `tools/actionpin/`
- `scripts/verify-go-modules.sh`
- `verification/github-actions-lock.json`
- `verification/go-module-roots.txt`
- `verification/documentation-currency.json`
- optional `.gitleaksignore` and `verification/gitleaks-waivers.yaml` only if baseline findings require reviewed waivers
- `docs/runbooks/ci-cd-operations.md`

Aligned external procedural surface:

- `~/.hermes/skills/software-development/github-actions-ci/` and `~/.hermes/skills/software-development/github-actions-supply-chain/` through `skill_manage`; generated repository `.agents/skills/` surfaces are not hand-edited.

## Out of Scope

- Enabling GitHub Advanced Security
- Scorecard Action, SARIF upload, badge publication, or Scorecard-based merge blocking
- Service source changes
- Reducing existing retention periods
- Automatic merging of dependency updates

## Success Metrics

- All remote `uses:` references under every `**/.github/workflows/*.yml|yaml` are 40-character SHAs present in the lock manifest; local actions remain allowed.
- Validator negative tests reject mutable refs and lock/comment mismatches; positive tests accept locked SHAs and local actions.
- Dependabot config contains `cooldown.default-days: 3`; repository auto-merge remains disabled and branch protection still requires one approval.
- Gitleaks baseline report is redacted, retained 30 days, and clean of unwaived findings; a runtime-generated synthetic secret is detected.
- Scorecard produces schema-valid JSON for the private repository and uploads a 30-day artifact without GHAS permissions.
- The actual tracked `go.mod` set exactly equals the committed 18-entry manifest and `go mod verify` succeeds in every listed module.
- `actionlint`, focused tool/script tests, doccheck, agent guidance, OpenSpec strict validation, PR CI, and post-merge main CI pass.

## Safe Rollback

- **Phase 1:** For a bad action release, restore that action and lock entry to the prior known-good commit SHA; never restore mutable tags. If the validator itself is faulty, revert only its CI invocation while retaining immutable pins. Revert the cooldown independently if GitHub rejects the schema.
- **Phase 2:** Remove the dedicated warn-only workflow and its optional waiver files. No merge gate exists yet.
- **Phase 3:** Delete `.github/workflows/scorecard.yml`; other CI remains unchanged.
- **Phase 4:** Revert Gitleaks from fail-closed to warn-only without removing scanning. Remove module verification independently if its exact-set logic is faulty. Documentation changes can be reverted separately.

Existing 30/90/365-day evidence retention is preserved throughout.
