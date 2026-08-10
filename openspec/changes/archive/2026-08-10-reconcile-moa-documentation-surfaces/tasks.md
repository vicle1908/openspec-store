# Tasks: Reconcile MoA Documentation Surfaces

## Audit

- [x] 1.1 Inspect current live YAML, normalized MoA output, fallback output, provider contexts, canonical spec, runbook, and Hermes MoA skill references.
- [x] 1.2 Enumerate active and archived MoA-related changes; classify historical references and unrelated active changes without editing them.
- [x] 1.3 Verify direct provider availability for `shopapikey:fable-5`, `giaoduc:Advance`, and `cockpit:gpt-5.6-luna` without exposing credentials.
- [x] 1.4 Create this isolated `skip_specs: true` documentation-reconciliation change before editing the maintained reference.

## Documentation synchronization

- [x] 2.1 Update the maintained MoA reference's example and tuning guidance to keep `context_length` at provider/model configuration, not MoA slots.
- [x] 2.2 Clarify safe scalar setters versus the agent-only atomic recovery path for malformed complex MoA writes.
- [x] 2.3 Record the unchanged canonical-spec/runbook review and sanitized audit evidence.

## Review and closure

- [x] 3.1 Run strict change validation and inspect the exact artifact set.
- [x] 3.2 Run structural, runtime, stale-reference, and documentation consistency checks; classify the unrelated full-store baseline failure.
- [x] 3.3 Obtain an independent read-only review of the final diff and evidence; Claude approved, while unavailable native lenses remain explicitly NOT_REVIEWED.
- [x] 3.4 Archive readiness: exact owned paths, review disposition, validation evidence, preservation boundary, and rollback path are recorded; archive/commit/push remain the execution gate.
