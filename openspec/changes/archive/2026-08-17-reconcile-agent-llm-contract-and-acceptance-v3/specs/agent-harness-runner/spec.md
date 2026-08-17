# agent-harness-runner Delta Specification

## ADDED Requirements

### Requirement: Model-free runner configuration and operation-aware construction context

`agent-harness` SHALL keep one documented model-free domain configuration separate from operation-scoped canonical model-construction contexts. Harness domain configuration MAY define supported workflow controls, artifact roots, stage definitions, and gate policies but MUST NOT define or project model, fallback, provider, transport, protocol, endpoint, credential reference, model behavior, or settings-shaped LLM fields. Public `status` and `report` composition SHALL be model-free. Public `run` composition and graph-continuing approval paths SHALL resolve one canonical profile/context and reuse that captured context.

#### Scenario: Status and report are model-free

- **WHEN** a caller runs `harness status` or `harness report`
- **THEN** the command SHALL compose only the domain, retained-state, and result services required
- **AND** it SHALL NOT resolve a canonical profile, build a model-construction context, or fabricate model identity

#### Scenario: Run resolves one context

- **WHEN** a caller runs `harness run`
- **THEN** the composition boundary SHALL resolve exactly one canonical profile and build exactly one process-local construction context
- **AND** every agent-backed stage/retry SHALL use models constructed from that captured context

## REMOVED Requirements

### Requirement: Composed runner configuration

**Reason:** The requirement exposed removed model/settings projections through harness domain configuration and mixed canonical LLM selection with harness-owned domain loading.
