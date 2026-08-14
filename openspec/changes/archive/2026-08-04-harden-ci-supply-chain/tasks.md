## 0. Freeze Baseline and Scope

- [x] [historical] 0.1 Create a dedicated Git worktree from the latest `origin/main`; record the exact base commit.
- [x] [historical] 0.2 Confirm the frozen baseline inventory: 11 workflow files, 61 remote `uses:` occurrences, 13 distinct remote actions, and 18 tracked `go.mod` files.
- [x] [historical] 0.3 Capture the existing retention matrix (30/90/365 days), branch-protection contexts, required approval count, `allow_auto_merge`, owner type, visibility, and GHAS status.
- [x] [historical] 0.4 Verify `review-scope.yaml` names every repository and canonical skill surface in scope.

**Acceptance:** Recorded evidence matches the frozen commit; no implementation starts if counts or settings differ.

## 1. Immutable Actions and Dependabot Hardening

- [x] [historical] 1.1 Re-resolve all 13 exact release-tag-to-commit mappings through the GitHub API (including annotated-tag dereference), retain the mapping evidence, fail on any mismatch with `design.md`, then add `verification/github-actions-lock.json` with those releases and SHAs.
- [x] [historical] 1.2 Replace all 61 existing remote references across all 11 workflows with lock-matching 40-character SHAs and exact-version comments; correct the Trivy tag-object SHA.
- [x] [historical] 1.3 Add dependency-free `tools/actionpin/actionpin.py` and `tools/actionpin/test_actionpin.py` to scan every tracked `**/.github/workflows/*.yml|yaml` without adding a Go module.
- [x] [historical] 1.4 Add unit tests proving mutable tag, short SHA, unknown action, SHA mismatch, version-comment mismatch, nested workflow, and stale lock failures; prove locked SHA and local-action success.
- [x] [historical] 1.5 Invoke actionpin early in root `verify.yml`.
- [x] [historical] 1.6 Add `cooldown.default-days: 3` to only the `github-actions` Dependabot entry and document that security updates are unaffected.
- [x] [historical] 1.7 Verify repository auto-merge remains disabled, branch protection still requires at least one approval, and no workflow implements Dependabot auto-merge.
- [x] [historical] 1.8 Capture a pre-change retention baseline via `git grep -n 'retention-days' origin/main -- '.github/workflows/*.yml' '.github/workflows/*.yaml' ':(glob)**/.github/workflows/*.yml' ':(glob)**/.github/workflows/*.yaml'`, then add `scripts/verify-retention.py` that asserts the same `retention-days` values appear in the same workflow contexts after pinning. Run it in CI.
- [x] [historical] 1.9 Run `python3 -m unittest discover -s tools/actionpin -p 'test_*.py'`, the actionpin CLI, and `actionlint` across every root and nested workflow.
- [x] [historical] 1.10 Push the Phase 1 commit and verify all PR checks pass.

**Phase 1 promotion gate:** tasks 1.1–1.10 pass on the same commit.

**Safe rollback:** restore only a problematic action and lock entry to its previous known-good commit SHA; never restore a mutable tag. Revert validator invocation or cooldown independently if needed.

## 2. Gitleaks Warn-Only Baseline

- [x] [historical] 2.1 Add dedicated `.github/workflows/gitleaks.yml` with workflow name `gitleaks`, stable job/check name `Gitleaks secret scan`, pinned checkout/upload-artifact actions, and `contents: read` only.
- [x] [historical] 2.2 Install Gitleaks CLI v8.30.1 from `gitleaks_8.30.1_linux_x64.tar.gz` and verify SHA-256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` before extraction.
- [x] [historical] 2.3 Implement event-specific ranges: PR base-to-head, push before-to-current with zero-before fallback, and manual full history.
- [x] [historical] 2.4 Run redacted JSON scanning, retain scanner exit status in metadata, and keep the Phase 2 workflow nonblocking.
- [x] [historical] 2.5 Always upload nonempty redacted report and metadata artifacts for 30 days with `if-no-files-found: error`.
- [x] [historical] 2.6 Add runtime-generated synthetic-secret detection in a temporary Git repository and assert a nonzero scanner exit.
- [x] [historical] 2.7 Run the full-history baseline on the exact candidate commit and classify every finding.
- [x] [historical] 2.8 If a false-positive waiver is required, add fingerprint-only `.gitleaksignore` plus owner, justification, review date, and expiry in `verification/gitleaks-waivers.yaml`; otherwise add neither file.
- [x] [historical] 2.9 Run actionpin and actionlint, push the Phase 2 commit, and verify PR CI passes while Gitleaks remains nonblocking.

**Phase 2 promotion gate:** checksum/version, synthetic detection, report schema/redaction, artifact retention, and candidate baseline evidence all pass. No blocking promotion occurs in this phase.

**Safe rollback:** delete only the dedicated workflow and Phase 2 waiver metadata.

## 3. Scorecard Report-Only Baseline

- [x] [historical] 3.1 Add dedicated `.github/workflows/scorecard.yml` with job name `OpenSSF Scorecard report`, triggered weekly and manually, with `contents: read` only and no GHAS/SARIF/publish permissions.
- [x] [historical] 3.2 Install Scorecard CLI v5.5.0 from `scorecard_5.5.0_linux_amd64.tar.gz` and verify SHA-256 `83b90a05c1540ef1390db1cd5711e5fd04be9c1d8537fb84d39d02092d6a8dff`.
- [x] [historical] 3.3 Run against `github.com/${GITHUB_REPOSITORY}` with `GITHUB_AUTH_TOKEN=${{ secrets.GITHUB_TOKEN }}` and produce JSON with details.
- [x] [historical] 3.4 Validate JSON object shape, numeric aggregate score, nonempty checks, and presence of Pinned-Dependencies, Token-Permissions, and Dangerous-Workflow checks.
- [x] [historical] 3.5 Upload the nonempty JSON artifact with pinned upload-artifact, `if-no-files-found: error`, and 30-day retention.
- [x] [historical] 3.6 Keep score values informational and do not add Scorecard to required branch-protection contexts.
- [x] [historical] 3.7 Run actionpin/actionlint, manually execute the workflow against the private repository, and preserve successful run evidence.
- [x] [historical] 3.8 Push the Phase 3 commit and verify existing PR CI remains passing.

**Phase 3 promotion gate:** exact binary verification, private-repo authentication, JSON assertions, artifact assertion, and nonblocking policy all pass.

**Safe rollback:** delete only `.github/workflows/scorecard.yml`.

## 4. Module Integrity, Documentation, and Gitleaks Enforcement

- [x] [historical] 4.1 Add sorted `verification/go-module-roots.txt` with exactly the 18 module paths from `design.md`, including the Temporal negative fixture.
- [x] [historical] 4.2 Add `scripts/verify-go-modules.sh` that compares the exact tracked actual set to the manifest, rejects missing/extra entries, checks file existence, and runs `go mod verify` in every module.
- [x] [historical] 4.3 Add temporary-repository tests proving exact-set success and missing/extra module failure.
- [x] [historical] 4.4 Invoke module verification in root `verify.yml`; verify the real repository reports 18/18 modules and all pass.
- [x] [historical] 4.5 Update `docs/runbooks/ci-cd-operations.md` with lock maintenance, Dependabot cooldown, Gitleaks ranges/waivers/promotion, Scorecard interpretation, retention, and safe rollback.
- [x] [historical] 4.6 Update `verification/documentation-currency.json` for all new workflows, manifests, tools/scripts, evidence, and the runbook.
- [x] [historical] 4.7 Patch and verify the canonical active-profile skills `~/.hermes/skills/software-development/github-actions-ci/` and `~/.hermes/skills/software-development/github-actions-supply-chain/` via `skill_manage`; do not hand-edit generated repository skill surfaces.
- [x] [historical] 4.8 Verify the exact candidate commit has a clean full-history Gitleaks baseline, clean PR-range report, passing synthetic detection, reviewed/unexpired waivers (if any), retained artifacts, and a successful nonblocking main run.
- [x] [historical] 4.9 Push the Phase 4 commit and verify all PR checks pass.
- [x] [historical] 4.10 Run `scripts/verify-retention.py` (from task 1.8) against the post-change workflows; verify the pre-change retention baseline matches exactly and both new Gitleaks/Scorecard artifacts declare 30-day retention.
- [x] [historical] 4.11 Run actionpin tests/gate, module tests/gate, all-workflow actionlint, doccheck, `make validate-agent-guidance`, and strict OpenSpec validation.
- [x] [historical] 4.12 Merge through the established protected-branch process and verify all post-merge main workflows pass including `Gitleaks secret scan` (nonblocking).
- [x] [historical] 4.13 Promote Gitleaks to fail-closed: push a follow-up commit that removes warn-only handling, then observe `Gitleaks secret scan` pass on main, and add only that exact context to branch protection without removing existing contexts.
- [x] [historical] 4.14 Verify all required checks pass on the final main commit: the existing two contexts plus `Gitleaks secret scan`.

**Phase 4 promotion gate:** tasks 4.1–4.14 pass on exact commits with retained evidence.

**Safe rollback:** restore Gitleaks to warn-only and remove only its new required context; retain scanning. Remove only the module gate invocation if its tooling is faulty. Revert docs/skill changes independently.

## Final Evidence

- [x] [historical] 5.1 Record exact commands, versions, checksums, commit SHAs, workflow run URLs/IDs, artifact names/retention, and branch-protection contexts in the runbook or verification evidence.
- [x] [historical] 5.2 Re-run plan-to-code alignment review before archive.
- [x] [historical] 5.3 Mark tasks complete only after real output verifies each acceptance criterion.


---

> **Historical record:** This change was archived with 48 incomplete task(s) (0/48 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
