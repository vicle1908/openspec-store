# Design: Reconcile MoA Documentation Surfaces

## Contract Under Review

The live and canonical contract is:

- primary route: `model.provider: moa`, `model.default: default`;
- `moa.default_preset: default`, `privacy_filter: display`;
- `default` aggregator: `shopapikey:fable-5`, `reasoning_effort: max`;
- `deep` aggregator: `giaoduc:Advance`, `reasoning_effort: max`;
- `fast` aggregator: `shopapikey:fable-5`, `reasoning_effort: high`;
- all provider contexts: `1000000` at `providers.cockpit`, `providers.shopapikey`, and `providers.giaoduc`;
- no `context_length` inside any MoA reference or aggregator slot;
- fallback order: `shopapikey`, `giaoduc`, then `cockpit`.

## Correction

The maintained OpenSpec reference is generic and should teach the current native contract:

1. show provider/model context ownership outside MoA slots;
2. remove slot-level `context_length` from the canonical example;
3. describe slot-level context duplication as an anti-pattern for this profile;
4. retain provider health, role, cadence, privacy, and rollback guidance;
5. state that Hermes leaf setters are preferred for scalar edits;
6. reserve atomic YAML replacement for an agent recovery path only when a complex setter corrupts mapping shape, with backup and immediate re-validation.

This avoids two contradictions: the old reference's “set context on every slot” versus the canonical spec's provider-level ownership, and the generic reference's direct hand-edit example versus the Hermes hub skill's user-facing no-hand-edit invariant.

## Review Boundary

No source implementation is involved. The canonical spec and governance runbook are reviewed against the live YAML and normalized CLI output. Archived changes are not edited; old model names in them are historical records.

## Verification

- Parse live YAML and assert every contract field.
- Run `hermes config check`, `hermes moa list`, and `hermes fallback list`.
- Run direct non-streaming inference for all three real provider/model routes.
- Run focused and strict main-spec validation, full-store validation, store doctor, and `git diff --check`.
- Search maintained docs, current specs, active changes, and skills for stale selected aggregator or context-slot guidance.
- Review the exact diff and confirm only the owned skill reference plus OpenSpec archive are committed.
