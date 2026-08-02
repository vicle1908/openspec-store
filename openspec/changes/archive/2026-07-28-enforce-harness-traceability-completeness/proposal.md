## Why

The harness can currently report terminal planning verification as `complete` when the accepted graph omits applicable design, API, or implementation-task identifiers. This undermines the harness's central assurance claim and must be corrected before completed planning packages are trusted.

## What Changes

- Define applicability-aware, stage-owned stable identifier kinds for the 13-stage workflow.
- Require terminal verification to evaluate the complete required mapping chain, not only four reachability percentages.
- Report missing edge obligations with enough detail to explain why an outcome is `partial` or blocked.
- Pin the installed schema and verification-policy version at run creation so an active run cannot silently cross policy versions.
- Label legacy verification results with their original policy instead of silently re-certifying them.
- **BREAKING**: Planning packages that previously reached `complete` through a partial identifier chain will become `partial` or validation-blocked until their mappings are corrected.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `harness-workflow`: Tighten stable traceability, terminal completion, applicability, and schema/policy-version guarantees.

## Non-Goals

- Changing the exact 13-stage sequence or the four human gate locations.
- Verifying implemented source code or executed tests.
- Replacing SQLite, OpenSpec, provider adapters, or the planning-only product boundary.
- Retrofactively mutating immutable legacy revisions.

## Impact

- Repository: `ai-harness-skills`.
- Primary modules: traceability matrix/runtime, workflow verification, reporting, run schema-version capture, harness schema/templates, and traceability skills.
- GitNexus reports CRITICAL upstream impact for `authoritative_verification` (17 symbols and 13 execution processes) and LOW impact for `TraceabilityMatrix.coverage` (5 symbols and 2 execution processes).
- Existing CLI output remains structurally compatible where possible, but gains policy-version and missing-obligation detail.
- No new external dependency is required.
