# Design

## Context

OmniRoute combines multiple accounts under unified model names. When one account stalls, healthy accounts should serve traffic. Stalling accounts caused failover targets to record contaminated latency, shared model metrics poisoned untried accounts, and every candidate was rejected before dispatch.

## Goals / Non-Goals

### Goals
- Isolate per-attempt latency across all direct and helper paths.
- Evaluate predictive latency per target; admit bounded recovery probes after cooldown and re-seed the latency window on fast success.
- Prevent predictive-only rejection when eligible candidates remain.
- Restrict startup replacements to intended files and verify matches.
- Document complete image-recreation rollback.

### Non-Goals
- Edit tracked upstream source files.
- Change account pools, credentials, or existing higher-latency timeout tiers.
- Alter cache, lease, or model-turn behavior.

## Decisions

### 1. Attempt-Local Timing
Capture a timestamp immediately before each attempt. Use it for direct metric updates and pass it to helper retry paths such as `handleEmptyContentRetry`. Keep request-level timing separate.

### 2. Connection-Scoped Predictive Latency and Bounded Recovery
Evaluate predictive latency against target-specific metrics without falling back to shared model averages. When predictive cooldown elapses, reserve at most one in-flight probe per target. Release the reservation on success, failure, abort, or timeout. A fast successful probe re-seeds the predictive latency window without erasing lifetime request/error history.

### 3. Eligibility-Aware Starvation Guard
If eligible candidates remain, predictive filtering alone must not reject every candidate. Ordinary eligibility gates remain authoritative; the guard does not bypass authentication, quota, lockout, or cooldown.

### 4. Scoped Replacement Execution and Verification
The patch engine must execute replacements only against intended files or use unique surrounding context. Marker checks must verify each expected target file and fail closed on mismatches.

### 5. Conditional Metrics-Store Unification
Verify active route linkage before patching metrics ownership. Unify state across module boundaries only if active routes demonstrate separate live stores.

### 6. Deployment and Rollback
Capture running image identity and original settings before deployment. Recreate the container from that image and restore script/settings during rollback, preserving the named data volume.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Concurrent recovery probes overload an account | Reserve at most one in-flight probe in authoritative target state |
| Historical average blocks recovered account | Re-seed predictive latency window on fast probe success |
| Patch collision across sibling chunks | Restrict replacements to intended files or unique surrounding text |
| Rollback leaves patched container contents | Recreate container from captured image; do not rely on restart |
