## Context

The repository has a working local verification and deployment contract, but
documentation and older normative references were not updated when the
canonical lifecycle moved to `make dev-smoke`, timestamped smoke reports, and
the eight-service topology. Retained evidence already provides the authoritative
coverage, CDC, smoke, and deployment facts needed to refresh those references.

This is a documentation and specification maintenance change. It does not
change service binaries, public contracts, database schemas, deployment images,
or cloud promotion behavior.

## Goals / Non-Goals

**Goals:**

- Make documentation name the same commands, artifact schemas, and service
  inventories that local validation actually executes.
- Replace stale coverage values with values from the current
  `microservices.service-coverage/v1` summaries.
- Correct catalog CDC and runbook references.
- Align normative smoke and runbook requirements with the current local
  acceptance path.
- Add a small, deterministic currency contract for documentation, status
  annotations, and mirrored skill files.

**Non-Goals:**

- Implementing per-service root runbooks or cloud deployment readiness.
- Changing application code, APIs, event contracts, migrations, images, or
  runtime configuration.
- Turning source-level status annotations into cloud readiness claims without
  staging, production, and rollback evidence.
- Editing archived OpenSpec changes or hand-editing generated skill mirrors.

## Decisions

### Evidence sources are machine-readable artifacts

Documentation updates SHALL use retained coverage summaries, smoke reports,
CDC evidence, and deployment-validation manifests as inputs. Human-readable
tables may summarize those artifacts, but they must not invent independent
measurements or claim a clean commit when the evidence records an uncommitted
worktree.

### The canonical local acceptance path is explicit

The normative local smoke reference will be `make dev-smoke` followed by
`make dev-evidence` with the exact smoke report. Older `test-e2e` targets remain
compatibility aids and are documented as non-authoritative rather than removed.

### Service inventories distinguish topology from CDC ownership

The platform inventory contains eight deployable services. Local CDC ownership
contains seven services because reporting is a projection consumer rather than
an outbox owner. Documentation and validation must state those as separate
sets so neither count is silently substituted for the other.

### Status annotations retain two evidence levels

Source-level implementation status and deployed-readiness status remain
separate. Local evidence may support an implementation or local acceptance
annotation; cloud status remains unverified until the active cloud change
produces staging, production, and rollback evidence.

### Skill parity is checked, not manually maintained

The change will declare the twelve mirrored OpenSpec workflow skill pairs
currently present under `.agents/skills` and `.codex/skills`. A parity check
will compare those canonical/mirror pairs and fail on drift, while preserving
generator ownership and avoiding direct edits to mirrored files. Other
agentmemory and third-party skills are outside this mirror set.

### Documentation validation is a separate required gate

`make validate-documentation` owns evidence-schema, inventory, current-link,
retired-smoke-reference, and mirrored-skill checks. `make verify-pr` requires
that target after platform and service verification so freshly generated
coverage summaries are available. Agent-guidance validation remains focused on
instruction discovery and safety rules.

### Root per-service runbooks remain separately owned

This change indexes available shared and service-local guidance without
fabricating missing root per-service runbooks. The remaining root coverage is
explicitly partial and belongs to the operational-readiness owner in a later
change.

## Risks / Trade-offs

- **[Evidence expires]** → Record evidence timestamps, schema names, source
  worktree digest, and the exact command that produced each summary.
- **[The service topology changes again]** → Validate documented service lists
  against the repository's canonical service/connector inventories.
- **[Historical specs look contradictory]** → Keep dated archived audits
  explicitly historical and update only active canonical specs.
- **[Parity checks reject a legitimate generated update]** → Report the
  canonical and mirror paths and require the generator/bootstrap workflow to
  regenerate both before accepting the change.

## Migration Plan

1. Update the documentation and service README references.
2. Add the new documentation-currency spec and apply deltas to the three
   affected existing capabilities.
3. Add focused documentation/spec consistency and skill-parity checks.
4. Run strict OpenSpec validation, the documentation checks, and the existing
   local verification/deployment evidence checks.
5. Roll back by reverting only documentation/spec/check changes; runtime state
   and deployment data are unaffected.

## Open Questions

None. The implementation decisions above resolve the two questions raised
during proposal review.
