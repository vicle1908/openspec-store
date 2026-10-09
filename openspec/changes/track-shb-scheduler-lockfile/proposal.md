# Proposal

## Why

The live `shb-schedule` repository declares a frozen `uv.lock`, but its broad `*.lock` ignore rule causes `uv.lock` to be ignored and absent from Git tracking. A clean clone can therefore lose the reproducible dependency lock required by the container build's `uv sync --frozen` contract.

## What Changes

- Add an explicit negation rule so `shb-schedule/uv.lock` is tracked despite the generic local-state `*.lock` rule.
- Verify `uv.lock` is tracked, present in the container build context, and usable by `uv sync --frozen`.
- Preserve all other local lock/database/cache ignore behavior.

## Capabilities

### New Capabilities

- `shb-schedule-reproducible-dependencies`: Guarantees that the scheduler's committed dependency lock participates in clean-clone and container builds.

### Modified Capabilities

- `shb-schedule-engine`: Strengthens the existing container build reproducibility contract without changing runtime behavior or dependency versions.

## Non-Goals

- Do not change dependency versions or regenerate `uv.lock` unless verification proves it is stale.
- Do not alter Docker, Compose, runtime code, workflow behavior, or scheduler configuration.
- Do not remove unrelated `*.lock` ignore behavior for local runtime state.
- Do not modify generated Graphify output, unrelated active OpenSpec changes, or remote repositories.

## Impact

- Clean clones retain the exact lockfile required by `uv sync --frozen`.
- Docker builds remain reproducible and fail early if the lockfile is stale.
- Local runtime lock files remain ignored.

## Affected Ownership Boundaries

- Implementation repository: `/Users/androidteam/Developer/shb/shb-schedule`.
- Central planning/specification: `/Users/androidteam/Developer/platform/openspec-store`.
