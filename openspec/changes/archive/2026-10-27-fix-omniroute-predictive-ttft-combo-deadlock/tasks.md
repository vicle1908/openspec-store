# Tasks

## 1. Baseline and Compatibility Patching

- [x] 1.1 Capture the running image identity, entrypoint backup/hash, original affected settings, and per-combo timeout configuration. Record rollback by restoring the script/settings and recreating from the captured image while preserving the named data volume.
- [x] 1.2 Trace active inference/metrics-route dependencies and every direct or helper-propagated attempt-time consumer. Establish whether metrics-state unification is necessary; duplicate module IDs alone are not evidence of split live state.
- [x] 1.3 Implement the approved compatibility-entrypoint changes: attempt-local timing including retry-helper dependencies; connection-scoped predictive metrics; bounded recovery and eligibility-aware starvation protection; per-target scoring; exact-model lockout; and strict per-file startup checks. Restrict replacements to intended files or unique surrounding context. Unify metrics state only if task 1.2 demonstrates a need.
- [x] 1.4 Verify expected replacement matches per file, correct chunk-specific helpers, idempotent patch-only execution, and nonzero startup failure for missing per-file markers against the captured build. Preserve tracked upstream source.

## 2. Deployment and State Recovery

- [x] 2.1 Confirm rollback inputs are complete, load the verified patch through the established deployment procedure, and verify startup markers, container health, and unchanged timeout tiers.
- [x] 2.2 Apply and read back the approved exact-model lockout settings. Reset only affected combo metrics when needed; verify unrelated telemetry and periodic cleanup remain intact.

## 3. Behavioral Verification

- [x] 3.1 Exercise a delayed/timed-out first target followed by failover, including direct and empty-response-helper metrics. Verify attempt-only latency, isolation from poisoned sibling metrics, and target-specific candidate scoring.
- [x] 3.2 Exercise predictive cooldown, concurrent probe admission, reservation release on every terminal outcome, successful recovery despite poisoned history, and starvation protection when the final raw candidate is independently ineligible. Verify ordinary eligibility gates remain authoritative and lifetime request/error counts are preserved.
- [x] 3.3 Verify synthetic 504 timeout and 429 failures produce exact-model lockouts without family-wide exclusion, preserve model-turn 400 exclusions, and remove isolated verification state.
- [x] 3.4 Exercise both existing inference endpoints against both incident combos. Verify successful response content, actual upstream target attribution, and request-local expected versus unexpected failure outcomes rather than global lifetime zero-failure counts.

## 4. Documentation

- [x] 4.1 After behavioral proof, update the existing OmniRoute wiki entry with verified invariants, limitations, and rollback steps. Check links/index status and use the established knowledge synchronization workflow subject to publication permissions.

## Later Workflow Guidance

After implementation and verification are complete, use the separate synchronization/archive workflow for main-spec synchronization, archive-readiness validation, archival, and the required store commit. This planning update performs none of those actions.
