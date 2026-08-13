# Proposal: reconcile-canonical-cli-fail-closed-acceptance-v1

## Why

The parent and successor changes (`standardize-agent-llm-environment-resolution-v2`
and `integrate-canonical-cli-projections-v1`) were archived via commits `9565197`
(archive content) and `466e8f2` (active directory removal) before two implementation
gaps were identified by post-archive review:

1. **ai-review fail-closed gap**: `resolve_canonical_overrides()` in
   `ai_review.providers.tdt_projection` caught `ProfileResolutionError` and
   returned `{}`, suppressing invalid canonical configs that the spec requires
   to fail before process launch. The fix (`26ed9f9`) removed the catch,
   leaving only the `OSError` fallback for missing/unavailable config.

2. **Durable acceptance evidence**: The live dual-consumer acceptance harness
   lived at `/private/tmp/tdt-phase6-acceptance-*` (ephemeral) rather than
   under version control. The hardened script
   `ai-review/scripts/verify_phase6_live_acceptance.py` was committed at
   `26ed9f9` (initial), refined at `51b55b1` (formatting), and finalized at
   `f1b6e0f` (cleanup ordering + post-finally verification).

## What Changes

This is an implementation-conformance and evidence correction, not a new feature.
The canonical spec already mandates fail-closed semantics. No delta spec is
needed.

- **ai-review** (`f1b6e0f`): fail-closed fix + durable acceptance script + cleanup
  verification.
- **ai-harness-skills** (`02d0410`): no change needed — already propagates
  `ProfileResolutionError` without catching it.
- **openspec-store**: reconcile implementation metadata (SHAs, evidence paths).
