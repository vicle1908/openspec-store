## Why

Current source evidence contradicts archived green verification claims for the
three-repository agent framework: `agent-core` has 14 failures in a clean
credential-less and network-restricted test run, `agent-harness` has nine
errors under its documented strict source-plus-test type gate,
`agent-docs-sync` has one error under that same cross-repository gate, and
repository documentation reports stale test and coupling metrics. These
regressions must be corrected before `agent-core`, `agent-docs-sync`, and
`agent-harness` can be certified together from current source.

This is a corrective successor to the archived
`agent-ecosystem-hardening`, `agent-ecosystem-hardening-cleanup`,
`close-agent-ecosystem-hardening-verification-gaps`, and
`close-three-repo-e2e-verification-gaps` changes. It does not rewrite their
history; it records where their retained evidence no longer matches current
HEADs and produces a new reproducible baseline.

## What Changes

- Make `agent-core`'s full test suite hermetic without weakening production
  provider authentication or HTTP destination validation: model-construction
  tests use explicit test providers, and HTTP tests control DNS/destination
  resolution as well as transport.
- Restore the documented `agent-harness` strict `src` plus `tests` mypy gate by
  correcting test fixtures and annotations at the supported model/composition
  boundary. Production types MUST NOT be widened merely to silence tests.
- Restore the `agent-docs-sync` strict `src` plus `tests` mypy gate by adding
  the missing typed pytest fixture boundary, then re-run its full gates.
- Refresh README, `AGENTS.md`, and `SPEC_INDEX.md` evidence only from commands
  executed against the final source identities.
- Add a three-repository corrective ledger that maps each stale archived claim
  to its current evidence, sole remediation owner, required command, result,
  prerequisite classification, and final source manifest.
- Require final verification to include locked dependency resolution,
  formatting, Ruff, strict source-plus-test typing, full tests, per-repository
  coverage, tracked-file secret scanning, CLI subprocess probes, relevant
  OpenSpec validation, and exact HEAD plus dirty-state attribution.
- Preserve every unrelated tracked or untracked path. In particular, classify
  the untracked `agent-docs-sync/doc-sync/SKILL.md` scaffold and dirty
  `graphify-out/` files as external worktree state unless ownership is proven;
  they MUST NOT be deleted, staged, or used as passing evidence by this change.
- Keep code readiness separate from unavailable Docker, PostgreSQL, deployed
  scheduler, provider, or scanner-profile evidence. A blocked prerequisite is
  reported as blocked and never converted into a pass.

### Non-Goals

- Changing public runtime APIs, provider authentication, HTTP SSRF controls,
  agent authority, persistence, or workflow semantics.
- Rewriting `~/.tdt/config.yaml`, supplying credentials, inventing missing
  `android-scanner` skills, or promising an `8/8` profile result. The active
  scanner profile is owned outside these three repositories and its missing
  includes predate the August 9 coding-agent skill-distribution change.
- Modifying the workspace/user coding-agent skill manifests or the archived
  `standardize-workspace-agent-skill-discovery` change.
- Deleting tracked `agent-core/src/reports-out/` history, aligning independent
  Typer version floors, adding a workspace CHANGELOG policy, or collapsing
  adapter-specific `AGENTS.md` and `CLAUDE.md` surfaces.
- Resolving `align-jti-skill-runtime-contract`, `integrate-fable-5`, or any
  other active OpenSpec change with a different owner.
- Restarting Docker, mutating PostgreSQL, running deployed workflows, or
  refreshing GitNexus/Graphify indexes without separate authorization.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Existing `agent-core-quality-gate`, `agent-framework-verification`,
`documentation-currency`, and
`agent-framework-documentation-evaluation` requirements already mandate zero
failing tests, strict typing, current evidence, prerequisite truthfulness, and
source-identity attribution. This change restores implementation and evidence
to those contracts, so `.openspec.yaml` explicitly sets `skip_specs: true`.

If implementation discovers that a production contract must change rather
than a test or documentation regression being corrected, apply work MUST stop
and the change must be revised with the appropriate delta spec before that
production edit.

## Impact

- **`agent-core`:** test providers/fixtures and HTTP test isolation; measured
  documentation evidence. No production authentication or network-policy
  change is planned.
- **`agent-docs-sync`:** one test annotation correction, verification, and
  evidence-driven documentation; the tracked canonical
  `.agents/skills/doc-sync/SKILL.md` remains intact.
- **`agent-harness`:** test fixtures and strict typing corrections; production
  model/composition types remain unchanged unless a separately reviewed delta
  spec is added.
- **`openspec-store`:** this planning change and retained corrective evidence.
- **Dependencies:** no runtime dependency change is planned; existing locked
  environments remain authoritative.
- **Risk:** low for the intended test/documentation edits, with medium
  cross-repository evidence risk mitigated by independent per-repository gates,
  exact source manifests, and fail-closed scope review.
