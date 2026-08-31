## Context

The parent change `reconcile-omniroute-native-dialects` completed a real, verified apply (11/11 write-set surfaces live on disk, hash-verified value-blind against its frozen pre-apply manifest) but was archived on 2026-08-31 with closure defects: an unreleased credential-rotation gate (Kimi/Cline), a wrong SH model ID in the final evidence manifest's SH rows (`sh/Claude-Fable` where the routes require `sh/gpt-5.6-sol`), a post-apply manifest written at 11:09:42 that omits the Grok apply at 11:29:04, an omp mode tightening 0644→0600 without the named approval its own task 2.4 policy required, and a `new_files` label (`~/.Claude-Fable`) mapping to no verified target. The archived change's safety lock and the store's rules forbid editing archived artifacts in place; the supported remediation is a corrective active change that references the archive read-only and supersedes its defective closure records with new evidence. The workstation additionally has a documented session-history of token corruption on exactly these model-ID strings (`sh/Claude-Fable` vs `sh/gpt-5.6-sol`, `pm/Claude-Fable`), so every artifact that cites an ID is verified by grep after writing.

## Goals / Non-Goals

**Goals:**

- Make the archive's unresolved gates durable and explicit in an active ledger (rotation gate, omp mode ratification, cline live sentinel).
- Produce corrected closure registers under this change: model-ID register, complete applied-surface register (including Grok), target-label reconciliation, archive-invalidity report with line citations.
- Freeze a value-blind current-state register (sha256 + mode) reconciled against the archived baselines.
- Add durable spec requirements so future routing closures cannot archive over these gate classes.

**Non-Goals:**

- Re-applying, rolling back, or "fixing" the live applied configurations (verified applied; not in question here).
- Editing the archived change directory, canonical specs directly, or any credential value.
- The `add-ntu-ai-keynote-deck` change (external human gates only).
- Determining whether `sh/Claude-Fable` is a live catalog ID for other routes; this change only fixes the model-ID binding for THIS routing family's SH/PM rows and records the registry-spec question as an investigation task.

## Decisions

- **Corrective-change pattern instead of archive edit or `git mv`.** The archive safety lock forbids in-place edits; un-archiving is not a supported lifecycle operation and would desynchronize the spec sync already applied at archive. A new active change is the store's established pattern (archived changes recorded as historical inputs to follow-ups). Alternative rejected: editing the archived final-evidence-manifest in place (violates the lock and falsifies history).
- **ADDED-only spec delta to `omniroute-agent-cli-routing`.** MODIFIED requirements replace whole canonical blocks and must carry every scenario heading verbatim — high-risk under this workstation's token-corruption history; the four closure-integrity requirements are new behaviors, so ADDED is sufficient and safe. Registry-spec (`coding-cli-provider-registry`) scenarios citing `sh/Claude-Fable` are handled as an investigation task that may spawn a follow-up change, not a delta here.
- **Value-blind evidence only.** All registers record hashes, modes, byte counts, line numbers — never credential values or raw responses. New evidence gets a credential-shape scan before it is committed; any hit is redacted and re-scanned.
- **Gates stay blocked with recorded release conditions.** The Kimi/Cline rotation gate releases only on explicit user confirmation (rotation upstream or written authorization); the omp mode gate releases only on a recorded ratify-or-revert decision; cline's live sentinel requires a user-owned auth session. None of these can be cleared by the agent.
- **Verify-after-write ID discipline.** Model IDs in artifacts are grep-verified after writing: `sh/gpt-5.6-sol` present where normative; every `sh/Claude-Fable` occurrence confined to defect-description context with the archived citation.
- **Store-local, single-writer, pathspec-limited commit at closure only; no push.** Follows the store's standing commit discipline.

## Risks / Trade-offs

- [Live configs drift while this change is active (concurrent sessions)] → The current-state freeze is a snapshot; re-freeze at closure and reconcile against the archived baselines before archiving this change.
- [Token corruption on model-ID strings during authoring] → Copy IDs from authoritative artifacts (archived tasks.md 1.1, live grok overlay rows), verify each written file by grep, and treat a repeated wrong literal as generation corruption — stop and re-derive rather than retype.
- [The archived ledger's ticked-but-false tasks confuse later audits] → The archive-invalidity report enumerates each defect with file+line citations, so the corrective record is self-sufficient without editing the archive.
- [Scope creep into fixing the registry spec] → Explicitly bounded: investigation task with a follow-up change if contamination is confirmed; no MODIFIED edits in this change.

## Migration Plan

No system migration: this change writes only OpenSpec artifacts and evidence registers under its own directory. Rollback is deletion of the change directory (before commit) or a revert commit (after).

## Open Questions

None blocking. Whether `sh/Claude-Fable` is a live catalog ID for other routes is deferred to the investigation task (1.6) and does not affect this change's specs, approach, or tasks.
