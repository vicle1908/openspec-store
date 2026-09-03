# Design: Canonical Spec Alignment for OMP Flash 3.8

## Context
The live `/Users/androidteam/.omp/agent/config.yml` on this workstation binds `smol`, `tiny`, and `vision` to `google-antigravity/gemini-3.8-flash:high` and concludes `retry.fallbackChains.default` with the same selector. The canonical specification at `openspec/specs/omp-provider-routing/spec.md` previously captured the 3.7 Flash state.

## Approach
1. Author delta specification under `specs/omp-provider-routing/spec.md` with:
   - `## MODIFIED Requirements`
   - Preserving every scenario heading name verbatim from canonical spec to satisfy OpenSpec validator rules.
   - Updating scenario bodies to cite `google-antigravity/gemini-3.8-flash:high`.
2. Author `design.md` and `tasks.md` to complete planning.
3. Sync the delta into canonical `openspec/specs/omp-provider-routing/spec.md` following `openspec-sync-specs`.
4. Validate with strict schema and spec validation.
