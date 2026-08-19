## Why

The current freshness surface is split: `knowledge-status.sh` often reports repositories as **FRESH** based on recent index timestamps, while `refresh-knowledge-indexes.sh --check` reports many repositories as **STALE** because the recorded index commit does not equal the current repository HEAD. That split means workspace freshness status is optimistic and inconsistent, and agents cannot trust dashboard-only evidence that a knowledge index reflects the latest committed code.

## What Changes

- Align the workspace freshness contract so **commit equality is the primary freshness signal** for GitNexus and Graphify, with timestamp-based freshness used only when recorded commit identity is unavailable.
- Update `knowledge-status.sh` to expose both the recorded indexed revision and the current HEAD, and to classify freshness primarily from commit equality.
- Update `refresh-knowledge-indexes.sh --check` to present the same authoritative freshness view and repository-level summary that the status command uses.
- Update the relevant OpenSpec specs so the documented contract matches the enforced behavior.

## Capabilities

### New Capabilities

- `freshness-reporting-contract`: defines the authoritative freshness classification for workspace knowledge-index status reporting.

### Modified Capabilities

- `workspace-index-freshness`: modify the observable refresh-status requirement to make commit equality the primary freshness signal and to expose indexed revision identity consistently.
- `developer-code-intelligence`: modify the verification and freshness expectation so repository readiness reflects recorded index commit equality, not only recent refresh activity.

## Non-Goals

- Changing GitNexus or Graphify CLI internals.
- Performing a batch refresh in this change.
- Changing repository inventory approvals or nightly automation schedule.

## Affected Ownership Boundaries

- **openspec-store**: new delta specs and planning artifacts for the freshness alignment.
- **Workspace scripts**: `~/Developer/scripts/knowledge-refresh/knowledge-status.sh` and `refresh-knowledge-indexes.sh`.
- **Workspace documentation/specs**: `openspec/specs/workspace-index-freshness/spec.md` and `openspec/specs/developer-code-intelligence/spec.md`.

## Impact

- Status command output will become stricter for correctness.
- Some repositories that currently appear **FRESH** on the dashboard will be reported as **STALE** or **UNAVAILABLE** until their indexes match HEAD.
- Agents and readiness checks that consume status output will get a more accurate freshness signal.
