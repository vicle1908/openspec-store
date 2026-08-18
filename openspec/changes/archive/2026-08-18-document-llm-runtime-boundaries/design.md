# Design: document-llm-runtime-boundaries

## Context

See proposal.md — Why. Hermes and omp both consume the same three providers as the
canonical TDT ecosystem but through their own config schemas. The divergence is
intentional (each runtime owns its own config format), but no spec says so. This
change documents the boundaries; it changes no code or config.

## Goals / Non-Goals

**Goals:**
- Make the omp exclusion explicit in the CLI-profile boundary spec, matching the
  existing prime-agent and provider-adapter exclusions.
- State that Hermes provider configuration is a separate runtime surface, so its
  `providers.<name>.model` / `context_length` fields are not misread as canonical-schema drift.

**Non-Goals:**
- Migrating Hermes or omp onto the canonical TDT schema.
- Building a versioned bridge between runtimes (explicitly deferred by the existing
  boundary requirement).
- Changing any MoA preset topology.

## Decisions

### D1: Extend the existing boundary requirement rather than add a new one

The CLI-profile spec already has "Separate runtime boundaries remain explicit" with
prime-agent and provider-adapter scenarios. Adding an omp scenario keeps all runtime
exclusions in one place. Alternative considered: a new requirement — rejected as
fragmentation of the same concern.

### D2: Frame Hermes as a separate surface, not a superset/subset

The Hermes and canonical schemas share provider *names* but not field *structure*.
The delta states they MAY reference the same providers without one being a projection
of the other. This avoids implying either schema should converge. Alternative
considered: declaring Hermes fields a deprecated drift to fix — rejected because the
Hermes runtime requires its own schema and the MoA spec is validated against it.

## Risks / Trade-offs

- [Documenting separation may reduce pressure to ever converge] → Acceptable; the
  boundary requirement already allows a future versioned bridge if convergence is wanted.

## Migration Plan

None — spec-text-only. Rollback = revert the spec edits.

## Open Questions

None.
