## Frozen Baseline

Review and implementation are based on `origin/main` commit `abdc7c12369bbc6b2ff3f10267793912832457ca`, not the stale working branch.

### Workflow inventory

- 8 root runtime workflows under `.github/workflows/`
- 3 order-service workflow templates under `services/order-service/.github/workflows/`
- 11 workflow files total
- 61 remote `uses:` occurrences
- 13 distinct remote actions
- 60 mutable tag references
- 1 immutable but incorrect Trivy tag-object SHA

The policy boundary is every tracked `**/.github/workflows/*.yml` and `**/.github/workflows/*.yaml`, not only root workflows.

### Exact action release locks

| Action | Exact release | Release commit SHA |
|---|---:|---|
| actions/checkout | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| actions/setup-go | v7.0.0 | `b7ad1dad31e06c5925ef5d2fc7ad053ef454303e` |
| actions/cache | v6.1.0 | `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` |
| actions/upload-artifact | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| actions/download-artifact | v8.0.1 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |
| actions/setup-node | v7.0.0 | `820762786026740c76f36085b0efc47a31fe5020` |
| actions/attest | v4.2.1 | `508db95dd578ae2727ebd6217d5ba78e4fbda05d` |
| actions/create-github-app-token | v3.2.0 | `bcd2ba49218906704ab6c1aa796996da409d3eb1` |
| docker/setup-buildx-action | v4.2.0 | `bb05f3f5519dd87d3ba754cc423b652a5edd6d2c` |
| docker/setup-qemu-action | v4.2.0 | `96fe6ef7f33517b61c61be40b68a1882f3264fb8` |
| docker/login-action | v4.6.0 | `dbcb813823bdd20940b903addbd779551569679f` |
| docker/build-push-action | v7.3.0 | `53b7df96c91f9c12dcc8a07bcb9ccacbed38856a` |
| aquasecurity/trivy-action | v0.36.0 | `ed142fd0673e97e23eac54620cfb913e5ce36c25` |

The current Trivy value `a9c7b0f06e461e9d4b4d1711f154ee024b8d7ab8` is an annotated-tag object SHA, not the release commit.

### Exact Go module set

`verification/go-module-roots.txt` will contain these 18 sorted paths:

```text
platform/go.mod
scripts/composeevidence/go.mod
scripts/validation/go.mod
services/catalog-service/go.mod
services/customer-service/go.mod
services/inventory-service/go.mod
services/notification-service/go.mod
services/order-service/go.mod
services/payment-service/go.mod
services/reporting-service/go.mod
services/shipping-service/go.mod
tests/cross-service-smoke/go.mod
tests/ecosystem-verification/go.mod
tests/platform/go.mod
tools/agentguide/go.mod
tools/doccheck/go.mod
tools/workflowaudit/go.mod
verification/fixtures/temporal-determinism/nondeterministic/go.mod
```

The negative Temporal fixture is intentionally included: module checksum integrity is independent of its behavioral purpose.

### Repository settings

- Visibility: private
- Owner type: personal account
- GitHub Advanced Security: not enabled
- Repository `allow_auto_merge`: false
- Branch protection: one approval plus required checks

## Phase 1 — Immutable Actions and Dependabot

### Lock manifest

Add `verification/github-actions-lock.json` with one entry per distinct remote action:

```json
{
  "schema": "go-microservices.github-actions-lock/v1",
  "actions": {
    "actions/checkout": {
      "version": "v7.0.1",
      "sha": "3d3c42e5aac5ba805825da76410c181273ba90b1"
    }
  }
}
```

The manifest records all 13 exact release tags and commit SHAs above. Every workflow comment uses the same exact version, for example:

```yaml
uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

### Repository-owned validator

Add a dependency-free Python-stdlib validator at `tools/actionpin/actionpin.py` with `unittest` coverage in `tools/actionpin/test_actionpin.py`. It scans every tracked `**/.github/workflows/*.yml|yaml` and enforces:

1. Local references beginning `./` are allowed without a lock entry.
2. Every remote reference uses a lowercase 40-character hexadecimal SHA.
3. The action owner/name exists in `verification/github-actions-lock.json`.
4. The workflow SHA equals the lock entry SHA.
5. The same-line exact-version comment equals the lock entry version.
6. Every lock entry is referenced at least once; stale lock entries fail.
7. The scan discovers all workflow files, including nested order-service templates.

Unit tests use temporary workflow fixtures and cover:

- mutable tag rejected;
- short SHA rejected;
- unknown action rejected;
- SHA mismatch rejected;
- version-comment mismatch rejected;
- locked SHA accepted;
- local action accepted;
- nested workflow discovered;
- stale lock entry rejected.

CI runs `python3 tools/actionpin/actionpin.py --root . --lock verification/github-actions-lock.json` before the rest of `verify.yml`. Dependabot SHA updates therefore require a reviewed lock update; they cannot merge silently. The Python implementation deliberately avoids adding a nineteenth Go module, so the final Go-module contract remains the frozen 18-entry set.

### Dependabot policy

Update only the `github-actions` ecosystem entry:

```yaml
cooldown:
  default-days: 3
```

This delays version updates by 72 hours; Dependabot security updates are not delayed. No workflow performs automatic dependency merging. Acceptance re-reads repository settings and branch protection to confirm `allow_auto_merge=false` and at least one required approval.

### Phase 1 acceptance

- Lock contains exactly 13 distinct action entries.
- Validator reports all existing/new workflow files and all remote references as locked.
- All nine positive/negative tests pass via `python3 -m unittest discover -s tools/actionpin -p 'test_*.py'`.
- `actionlint` passes across every root and nested workflow.
- Dependabot YAML parses and `cooldown.default-days == 3`.
- Auto-merge remains disabled and one approval remains required.
- Existing retention matrix is unchanged.
- PR CI passes at the Phase 1 commit.

### Phase 1 rollback

Restore a problematic action and its lock entry to the previous known-good commit SHA. Never restore a mutable tag. If only the validator is faulty, revert its CI call while retaining pins. The cooldown can be reverted independently.

## Phase 2 — Gitleaks Warn-Only Baseline

Use the open-source Gitleaks CLI rather than `gitleaks-action`, eliminating wrapper licensing and PR-comment permissions.

- Version: `v8.30.1`
- Linux x64 archive: `gitleaks_8.30.1_linux_x64.tar.gz`
- SHA-256: `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`

Add dedicated `.github/workflows/gitleaks.yml` with workflow name `gitleaks`, stable job/check name `Gitleaks secret scan`, `contents: read`, pinned checkout/upload-artifact actions, and triggers for PR, push to main, and manual dispatch.

Execution rules:

- Checkout uses `fetch-depth: 0`.
- Download the exact archive, verify SHA-256 before extraction, and assert `gitleaks version` contains `8.30.1`.
- PR scan range: pull-request base SHA through head SHA.
- Push scan range: `before` through current SHA; a zero/missing `before` falls back to full history.
- Manual dispatch performs a full-history baseline.
- Run with `gitleaks git --redact=100 --report-format json --report-path <path>` and the event-specific `--log-opts` above.
- Capture the scanner exit code explicitly: `0` means clean, `1` means findings, and any other nonzero value is an operational error that fails the workflow even in Phase 2.
- Keep exit code `1` nonblocking only in Phase 2, record it in metadata, and ensure a valid JSON report exists (write an empty `[]` report only after a confirmed clean exit if the CLI emitted no file).
- Always upload the redacted JSON report and scan metadata for 30 days with `if-no-files-found: error`.
- Disable comments and request no write permission.

A detection control creates a temporary Git repository under `$RUNNER_TEMP`, generates a known synthetic secret from split runtime fragments (nothing secret-like is committed to the source repository), commits it, and asserts Gitleaks exits nonzero.

No `.gitleaksignore` is created unless the baseline finds a false positive. Any waiver requires:

- exact fingerprint in `.gitleaksignore`;
- owner, justification, review date, and expiry in `verification/gitleaks-waivers.yaml`;
- redacted evidence;
- reviewer approval.

### Phase 2 acceptance

- Archive checksum and version assertions pass.
- Synthetic detection control exits nonzero as expected.
- Candidate repository scan produces schema-valid, redacted JSON.
- Warn-only mode does not block the PR while preserving the scanner exit status in metadata.
- Artifact exists and retention is 30 days.
- No unreviewed waiver file is added.
- PR CI passes at the Phase 2 commit.

### Phase 2 rollback

Delete only `.github/workflows/gitleaks.yml` and any Phase 2 waiver metadata. No required check or other workflow is changed yet.

## Phase 3 — Scorecard Report-Only Baseline

Add dedicated `.github/workflows/scorecard.yml` with workflow name `scorecard` and job name `OpenSSF Scorecard report`; do not embed Scorecard in `verify.yml`.

- Version: `v5.5.0`
- Linux amd64 archive: `scorecard_5.5.0_linux_amd64.tar.gz`
- SHA-256: `83b90a05c1540ef1390db1cd5711e5fd04be9c1d8537fb84d39d02092d6a8dff`
- Triggers: weekly schedule and manual dispatch
- Permissions: `contents: read` only
- Authentication: `GITHUB_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` at the scan step
- No `id-token`, `security-events`, GHAS, SARIF, badge, or published results

The workflow downloads the exact archive, verifies the checksum, asserts version 5.5.0, then runs:

```text
scorecard --repo=github.com/${GITHUB_REPOSITORY} --format=json --show-details
```

The workflow validates with `jq` that output is an object with numeric `score` and a nonempty `checks` array; it asserts the critical named checks are present. Structural/runtime errors fail the Scorecard workflow, but score values never fail it and the workflow is not a required merge check. The JSON artifact uses pinned `actions/upload-artifact`, `if-no-files-found: error`, and 30-day retention.

### Phase 3 acceptance

- Checksum and version assertions pass.
- Manual run scans the private repository using read-only `GITHUB_TOKEN`.
- JSON schema and critical-check presence assertions pass.
- Artifact exists, is nonempty, and retains for 30 days.
- Score values remain informational and no branch-protection context is added.
- PR CI remains unchanged/passing at the Phase 3 commit.

### Phase 3 rollback

Delete `.github/workflows/scorecard.yml`. No other workflow, permission, or branch-protection setting changes.

## Phase 4 — Module Integrity, Documentation, and Gitleaks Enforcement

### Exact module verification

Add `scripts/verify-go-modules.sh` and `verification/go-module-roots.txt`.

The script accepts repository root and manifest arguments, then:

1. Reads and validates the sorted, unique 18-entry expected manifest.
2. Computes the sorted tracked actual set using Git, not untracked filesystem files.
3. Fails with a diff if expected and actual sets differ (missing or extra module).
4. Fails if any listed file is missing.
5. Runs `go mod verify` in each listed module directory and reports per-module status.
6. Exits nonzero if any module fails.

Script tests create temporary Git repositories and prove missing and extra module entries fail while an exact set passes. The real-repository invocation must report 18/18 verified.

### Documentation and skill alignment

- Update `docs/runbooks/ci-cd-operations.md` with lock maintenance, Dependabot cooldown, Gitleaks baseline/waiver ownership, Scorecard report interpretation, promotion criteria, and safe rollback.
- Update `verification/documentation-currency.json` for the new workflows, manifests, runbook, and retained evidence.
- Patch and verify the canonical active-profile skills `~/.hermes/skills/software-development/github-actions-ci/` and `~/.hermes/skills/software-development/github-actions-supply-chain/` using `skill_manage`. Do not hand-edit generated repository `.agents/skills/` surfaces.
- Verify `make validate-agent-guidance` and doccheck.

### Gitleaks promotion gate

Promotion from warn-only to fail-closed occurs only when all are true on the exact candidate commit:

- full-history manual baseline report has zero unwaived findings;
- PR-range scan report has zero unwaived findings;
- synthetic detection control passes;
- waiver metadata, if any, has owner/justification/expiry and review approval;
- Phase 2 artifact and metadata are retained;
- a successful nonblocking run exists on main.

After the Phase 4 commit merges to main, observe a successful `Gitleaks secret scan` on main. Then push a follow-up commit that removes warn-only handling, makes `Gitleaks secret scan` fail on scanner exit 1, and adds only that exact context to branch protection without removing existing required checks.

Scorecard remains report-only.

### Phase 4 acceptance

- Exact module-set positive, missing, and extra tests pass.
- Real repository reports 18/18 modules and every `go mod verify` passes.
- Gitleaks promotion criteria are documented and evidenced at the candidate commit.
- Required checks include the existing two contexts plus the stable Gitleaks context; none are removed.
- Runbook, documentation currency, and both active-profile skills describe the implemented behavior.
- `actionlint`, actionpin tests/gate, module tests/gate, doccheck, agent guidance, strict OpenSpec validation, PR CI, and post-merge main CI pass.

### Phase 4 rollback

- If Gitleaks blocks incorrectly, restore warn-only handling and remove only its newly added required context; keep scanning and evidence.
- If module-set logic is faulty, remove only its `verify.yml` invocation while fixing the script; do not alter module files.
- Revert documentation or skill edits independently if inaccurate.

## Retention Contract

| Evidence class | Retention | Change |
|---|---:|---|
| Verification evidence | 30 days | Preserve |
| Deployment/image evidence | 90 days | Preserve |
| Release evidence | 365 days | Preserve |
| Gitleaks redacted diagnostic | 30 days | New |
| Scorecard JSON diagnostic | 30 days | New |

An acceptance check inventories every `retention-days:` value and fails if an existing artifact tier changes unexpectedly.
