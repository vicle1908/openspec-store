# Design: TDT_HOME Provider Release and Rollout

## Context

The provider candidate has a clean local wheelhouse and installed smoke
evidence, while consumers and the operator root remain outside its ownership.
The rollout change turns that evidence into a gated operational sequence without
blurring a local artifact check into a deployment claim.

## Decisions

### Decision 1: Qualify an immutable release candidate

The candidate consists of a provider wheel, locked dependency closure, hash
inventory, runtime version, and source revision. Qualification installs it in a
fresh environment with no checkout and no `PYTHONPATH`, then runs base CLI,
packaged-resource, doctor, and provider contract checks. A failed gate blocks
rollout and retains the prior artifact.

### Decision 2: Stage before rollout

Deployment proceeds through a disposable/staging target whose identity,
principal, package source, and configuration are recorded. The stage must prove
provider-only startup and diagnostics before a consumer or scheduler target is
considered. No live `~/.tdt` mutation is part of staging.

### Decision 3: Approval and rollback are explicit

A rollout record names the release candidate, target, operator, approval
reference, pre-change artifact, health evidence, and rollback command. Missing
or contradictory ownership/approval facts keep the rollout blocked. Rollback
restores the exact pre-change artifact and does not delete operator data.

### Decision 4: Consumer readiness is a separate gate

Provider rollout may publish readiness evidence, but it cannot mark a consumer
ready. Each consumer must supply its own source-conformance, dependency, and
runtime evidence in a successor change.

## Evidence Gates

- Clean wheelhouse install and hash/version/resource checks.
- Staging health and provider-only diagnostics with redacted output.
- Explicit owner/principal and approval evidence.
- Rollback rehearsal or an operator-accepted bounded reason for deferral.
- Strict OpenSpec and repository verification with a final dirty-state review.

## Rollback

Rollback is artifact-level: restore the retained provider artifact and its
locked closure in the staging/deployment target. It does not rewrite consumer
source, databases, credentials, schedules, or the real `~/.tdt`.
