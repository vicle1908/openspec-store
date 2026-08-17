# agent-docs-sync Delta Specification

## ADDED Requirements

### Requirement: Model-free configuration and operation-aware context truthfulness

`agent-docs-sync` SHALL keep one documented model-free domain configuration separate from operation-scoped canonical model-construction contexts. Repository configuration MAY define supported docs-sync discovery, validation, generation-policy, persistence, write-approval, timeout, iteration, and reporting controls, but MUST NOT define or project model, fallback, provider, transport, protocol, endpoint, credential reference, model behavior, or settings-shaped LLM fields. Generation-capable `update` and `sync`, an actually implemented LLM-enabled discovery mode, and `resume` SHALL be model-backed operations. Standalone `validate`, `check`, `audit`, default/non-LLM discovery, `pending`, `list`, `approve`, and `deny` SHALL be model-free operations and MUST NOT resolve, require, or fabricate model identity.

#### Scenario: Model-free public commands do not resolve LLM context

- **WHEN** a caller runs standalone `validate`, `check`, `audit`, default/non-LLM discovery, `pending`, `list`, `approve`, or `deny`
- **THEN** the command SHALL compose only the domain, retained-state, and result services required by that command
- **AND** it SHALL NOT resolve or require a canonical profile, build a model-construction context, construct a model, or fabricate model identity

#### Scenario: Generation-capable operations use one context

- **WHEN** a caller runs generation-capable `update`, generation-capable `sync`, an actually implemented LLM-enabled discovery mode, or `resume`
- **THEN** the operation SHALL resolve and capture one canonical construction context before model-backed execution
- **AND** every model-backed nested path and retry SHALL reuse that context

## REMOVED Requirements

### Requirement: Canonical configuration and CLI truthfulness

**Reason:** Replaced by model-free configuration requirement that properly separates model-free from model-backed operations.
