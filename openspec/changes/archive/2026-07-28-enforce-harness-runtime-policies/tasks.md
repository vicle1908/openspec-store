## 1. Dependency, Pre-edit Safety, and Provider Telemetry Spike

- [x] 1.1 Confirm `harden-harness-provider-execution` is implemented and archived or explicitly coordinate its shared process-limit ownership before applying this change.
- [x] 1.2 In `ai-harness-skills`, run `openspec list`, confirm this change is active, and record the required `Refs: openspec/changes/enforce-harness-runtime-policies/` commit footer.
- [x] 1.3 Re-run upstream GitNexus impact for `parse_structured_result`, `WorkflowEngine._begin`, `WorkflowEngine.execute_headless`, provider event/envelope parsers, ledger provider-session methods, and reporting; stop for confirmation on HIGH or CRITICAL results.
- [x] 1.4 Capture fixture evidence for the supported Claude response-envelope usage fields and Codex event-stream usage fields without relying on model-authored stage output.
- [x] 1.5 Decide and document the database schema migration, backup, integrity-check, and rollback procedure before editing ledger schema.

## 2. RED Usage and Budget Checkpoint

- [x] 2.1 Add provider tests proving model-authored usage is advisory and cannot satisfy or bypass request, token, or cost policies.
- [x] 2.2 Add tests normalizing authoritative Claude/Codex telemetry with explicit provenance and leaving unavailable values null.
- [x] 2.3 Add workflow/ledger tests proving successful, invalid, failed, timed-out, cancelled, and interrupted attempts count exactly once when telemetry exists.
- [x] 2.4 Add concurrent request-reservation tests proving two processes cannot exceed the run request limit.
- [x] 2.5 Add cumulative budget tests proving exhausted runs fail before process start and Claude receives only the remaining hard cost budget.
- [x] 2.6 Add support-tier tests proving a provider with observed/unavailable hard cost or token control is not automated for that configuration.
- [x] 2.7 Add configuration tests rejecting dormant concurrency and retention settings before run creation with actionable migration diagnostics.
- [x] 2.8 Commit the failing policy regression suite as the required RED checkpoint without `--no-verify`.

## 3. Provider Invocation Outcome Contract

- [x] 3.1 Introduce a typed provider invocation outcome separating process/session telemetry, authoritative usage, diagnostics, and optional validated stage result.
- [x] 3.2 Remove enforcement authority from structured planning-result `usage`; retain it only as clearly advisory data or remove it from the model schema.
- [x] 3.3 Extract supported Claude envelope and Codex event usage into normalized finite non-negative values with provider/session/attempt provenance.
- [x] 3.4 Reconcile authoritative telemetry on every provider exit path without persisting prompts, protected bodies, or credentials.

## 4. Ledger Migration and Exactly-once Accounting

- [x] 4.1 Add versioned SQLite records for attempt reservation, reconciliation status, usage provenance, tokens, cost, outcome, and timestamps.
- [x] 4.2 Implement atomic request reservation before spawn and exactly-once reconciliation after every outcome.
- [x] 4.3 Implement cumulative run totals and remaining-policy queries that do not normalize unknown token/cost values to zero.
- [x] 4.4 Extend restart and stale-lease recovery to distinguish unreconciled attempts from free retries and preserve reported consumption.
- [x] 4.5 Add forward migration and integrity tests from the existing ledger schema, including interrupted migration and unsupported-version failure.

## 5. Cumulative Enforcement and Capability Quality

- [x] 5.1 Compute remaining request/token/cost policies before invocation and reject exhausted enforced policies without spawning a process.
- [x] 5.2 Pass the authoritative remaining hard budget to capable adapters rather than the full run cap per stage.
- [x] 5.3 Represent each policy as enforced, observed, or unavailable and integrate that quality with configured-profile support decisions.
- [x] 5.4 Ensure post-hoc overage detection records a contract failure but is never described as prevention.
- [x] 5.5 Reject inactive concurrency and retention fields before run creation, reserve their names, update configuration migrations, and prevent non-enforcing metadata acceptance.

## 6. Reporting, GREEN Integration, and Documentation

- [x] 6.1 Extend status/report output with authoritative cumulative totals, remaining limits, provenance, and enforcement quality while preserving existing run/stage fields.
- [x] 6.2 Update security, reference, operations, development, and architecture docs to remove unsupported concurrency/retention claims and distinguish hard enforcement from observation.
- [x] 6.3 Update fake providers and full guided/headless workflows for successful, failed, resumed, exhausted, unavailable, and downgraded policy paths.
- [x] 6.4 Commit the implementation and passing regression suite as the required GREEN checkpoint with the OpenSpec reference footer.

## 7. Verification and Rollback Evidence

- [x] 7.1 Run frozen sync, Ruff lint/format, strict mypy, full pytest/coverage, dependency audit, strict OpenSpec/schema validation, and all skill validators.
- [x] 7.2 Run `npx gitnexus detect-changes --scope staged -r ai-harness-skills` before each implementation commit and investigate unexpected workflow/ledger/provider flows.
- [x] 7.3 Exercise database backup, forward migration, interrupted reconciliation recovery, and rollback restoration against a temporary non-empty ledger.
- [x] 7.4 Live telemetry smoke checks deferred: no explicit finite-budget approval was provided; deterministic provider-native fixtures record Claude cost/token and Codex token/cost-unavailable quality without invoking models.
