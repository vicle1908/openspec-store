# Proposal: Align OMP Flash 3.8 Routing in Canonical Specs

## Why
Align the canonical `omp-provider-routing` specification with the live OMP configuration, where high-frequency background roles (`smol`, `tiny`, `vision`) and the `default` fallback chain terminal hop were upgraded from `google-antigravity/gemini-3.7-flash:high` to `google-antigravity/gemini-3.8-flash:high`.

## What Changes
- Spec delta: `specs/omp-provider-routing/spec.md` in this change updating 3 modified requirements (`Isolated profile validation`, `Capability-based role allocation`, and `Fallback chain composition and coverage`).
- Canonical spec sync: merge the delta into `openspec/specs/omp-provider-routing/spec.md`.
- Code changes: 0 executable code edits in the workspace (`/Users/androidteam/Developer`), as verified by auditing repository consumers.
- Live OMP configuration: verify `/Users/androidteam/.omp/agent/config.yml` already matches the 3.8 Flash selector across lines 2-4 and line 67, and that the authoritative `modelRoles.advisor` (`cockpit/gpt-5.6-sol:xhigh`) is preserved.

## Acceptance Criteria
- Delta spec validates strictly via `openspec validate align-omp-flash-3-8-routing --strict --store openspec-store`.
- Canonical spec contains 0 references to `google-antigravity/gemini-3.7-flash:high` and reflects `google-antigravity/gemini-3.8-flash:high`.
- Main spec passes `openspec validate --specs --store openspec-store`.
