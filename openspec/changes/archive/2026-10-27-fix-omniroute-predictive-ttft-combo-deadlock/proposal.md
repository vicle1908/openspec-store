# Proposal

## Why

Recorded incident diagnostics show that the `gemini-3.8-flash-high` combo (and `muse-spark-1.3`, which nests it as its primary step) entered an HTTP 503 deadlock where all candidate targets were skipped before dispatch. In recorded observations, 10 of the 11 accounts still had quota and direct non-combo calls succeeded (average 4,493 ms), while `muse-spark-1.3` masked the outage by falling back to `agy/gemini-3.8-flash-medium`.

The incident investigation identifies four primary defect areas:
1. **Per-attempt timing contamination:** `executeTargetAttempt` measures target duration from whole-combo start time, and also passes that start time to `handleEmptyContentRetry`. A failover target is recorded with prior timeout duration included, poisoning healthy target metrics.
2. **Shared model-metric fallback and recovery defects:** Targets sharing a model inherit `byModel` averages when connection metrics are absent, rejecting untried accounts. Zero-attempt HTTP 503 responses refresh `combo.lastUsedAt`, preventing metric TTL eviction. A timestamp-only cooldown admits concurrent probes, a single fast probe still leaves a high historical average, and an array-index starvation check fails when the final candidate is rejected by earlier gates.
3. **Scoring inputs:** Candidate scoring reads model-wide metrics instead of target-specific metrics when computing latency and error terms.
4. **Disabled lockout on timeout:** Repeated 504 timeouts did not trigger exact-model lockouts because lockout defaults to disabled and does not enforce exact-model scope for these accounts.

Duplicate webpack modules appeared during investigation, but active-route separation remains an unverified hypothesis. State unification is conditional on demonstration of separate live state.

## What Changes

- Measure attempt duration from an attempt-local timestamp across direct metrics and retry helpers, while preserving outer request timing.
- Scope predictive TTFT metrics to individual connection targets.
- After predictive cooldown, reserve at most one in-flight recovery probe per target, re-seed the predictive latency window on success, and release the reservation on any terminal outcome.
- Protect otherwise eligible targets from predictive-only starvation without bypassing ordinary eligibility gates.
- Prioritize per-target metrics in candidate scoring.
- Enable exact-model lockout on timeout for these accounts.
- Restrict compatibility replacements to intended files or unique context, and fail startup if per-file markers are missing.
- Roll back by restoring the script and changed settings and recreating from the captured image while preserving the data volume.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `omniroute-compression-and-routing`: Restores failover, bounded recovery, exact-model lockout, and startup verification.

## Impact

- **Operational reliability:** Eliminates self-sustaining routing deadlocks on multi-account pools.
- **Risk control:** Rollback recreation and explicit verification prevent unproven or colliding patches from persisting.
