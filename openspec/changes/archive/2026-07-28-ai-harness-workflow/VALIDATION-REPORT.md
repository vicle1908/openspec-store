# Validation Report: AI Harness Workflow

## Validated decisions

- The implementation is a standalone `ai-harness-skills` repository with Python
  package `ai_harness` and command `harness`.
- The portable interface is exactly three passive, feature-based Agent Skills:
  `harness-workflow`, `harness-gates`, and `harness-traceability`.
- Skills guide CLI use. They do not orchestrate, validate, render, persist state,
  write artifacts, or duplicate authoritative OpenSpec templates.
- The Python CLI owns the state machine, gates, provider invocation, validation,
  immutable revisions, and current artifact materialization.
- Claude Code and Codex are the initial headless adapters; support depends on live
  capability probes and conformance tests rather than version strings alone.
- Runtime state is a versioned SQLite ledger under `$TDT_HOME/ai-harness/` and is
  never placed in `.openspec.yaml`.

## Agent Skills contract

Each skill has standard `SKILL.md` metadata and focused references. Core skills do
not depend on Claude-only context, agent, model, argument, or invocation fields.
The workflow skill obtains stage instructions and schemas from the CLI. Gate and
traceability skills invoke CLI validation and mutation commands instead of carrying
shell implementations.

Installation with `npx skills` is independent of installing the Python CLI or
running `harness init`.

## OpenSpec 1.6 contract

The project schema is installed at:

```text
openspec/schemas/harness-13/
  schema.yaml
  templates/<13 stage templates>.md
```

Stage instructions are inline YAML strings. The dependency graph uses immediate
predecessor edges. `apply.requires` lists all thirteen artifacts and the apply
instruction explicitly hands off a planning-only package.

`openspec schema validate harness-13` must run from the logical project root because
schema commands are working-directory based. The harness also validates the exact
stage order, output containment, apply list, stable-ID/evidence instructions, and
template semantics that the OpenSpec structural validator does not enforce.

For symlinked projects, the initializer preserves both the logical project root and
canonical OpenSpec root. Conflict detection, locks, and writes use the canonical
destination; OpenSpec commands use the logical root.

## Security and state findings

- Providers receive read-only authority and untrusted structured output is accepted
  only through the CLI.
- Subprocesses use argument arrays, bounded stdin/files, explicit working
  directories, minimal environment inheritance, timeouts, cancellation, and output
  limits; `shell=True` is prohibited.
- Trusted actor identity comes from the operating system, optionally restricted by
  an approver allowlist. Self-asserted actor values do not grant authority.
- Gate and explicit backtrack actions bind to the current revision and artifact
  digest and fail closed for stale, replayed, mismatched, or unauthorized input.
- Human clarification answers can support requirements, decisions, and assumption
  resolution, but cannot prove observed current-code facts without collected
  evidence.
- Provider event retention defaults to 30 days and completed-run metadata to 365
  days. Immutable artifact revisions are never deleted automatically.

## Verification status

- `openspec validate --strict ai-harness-workflow`: passing after reconciliation.
- Deterministic unit, adapter-contract, integration, security, initializer, and
  full-workflow tests are required before completion.
- Live Claude/Codex smoke tests are opt-in, finite-budget, read-only checks; an
  unconfigured environment records a documented skip rather than failing
  deterministic CI.

*Reconciled: 2026-07-28 against the installed OpenSpec 1.6.0 CLI and current local
Claude Code/Codex capability surfaces.*
