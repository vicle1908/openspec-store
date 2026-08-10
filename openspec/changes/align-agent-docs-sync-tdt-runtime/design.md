## Context

See `proposal.md` for motivation. The current docs-sync consumer already depends on the public `agent_core.sdk` model and settings facade, while the active TDT home contains a primary model, ordered fallback identifiers, a provider registry, and a separate secret file. The repository configuration also contains consumer-specific write roots and runtime limits. The implementation must compose these surfaces without changing agent-core or protected TDT ownership.

The full sync path returns a workflow state whose report is nested under `results.report`. Generation requests return a structured completion/reason/iteration result, but the report and CLI must preserve that state across the workflow boundary. Existing Graphify/GitNexus output and the untracked `doc-sync/` scaffold are unrelated and remain untouched.

## Goals / Non-Goals

**Goals:**

- Establish one explicit precedence function for consumer overrides, repository runtime fields, TDT settings, and safe defaults.
- Pass the resolved model object or identifier and resolved generation limits into the existing canonical generation builder.
- Use the public agent-core factory for ordered fallback construction and keep unavailable credential routes fail-closed.
- Normalize the workflow report once, expose redacted generation metadata, and select exit status from the normalized report.
- Keep documentation, the canonical skill, tests, and disposable live verification synchronized with the behavior.

**Non-Goals:**

- No provider registry edits, credential provisioning, secret copying, or endpoint migration.
- No changes to agent-core fallback exception policy or pydantic-ai provider implementation.
- No changes to docs-sync write authorization, allowed roots, OpenSpec sync authority, or approval lifecycle.
- No attempt to make a provider route succeed when its required credential is intentionally absent.

## Decisions

1. **TDT is the shared runtime source; repository configuration is a consumer overlay.**
   `agent_core.sdk.load_settings()` remains the only shared settings entry point. The repository `runtime` block may override model, max iterations, and timeout when explicitly set; omitted values inherit the TDT-derived profile. `DOCS_SYNC_*` values are applied last for process-local overrides. This preserves local testability without duplicating provider credentials or maps.

2. **Provider resolution stays behind the SDK facade.**
   Docs-sync calls the public fallback factory with the effective primary and TDT fallback IDs. It does not import agent-core internals or reconstruct provider URLs/keys. If construction fails because a route is unconfigured, the consumer logs a redacted diagnostic and uses only a constructible primary when policy allows; it never silently rewrites a model ID to another provider.

3. **Runtime limits are part of the generation profile.**
   The generation profile accepts resolved iteration and wall-clock limits. This keeps the agent's actual loop consistent with `DocsSyncConfig` and makes synthetic fixtures able to bound real LLM acceptance tests.

4. **Report normalization precedes presentation and exit selection.**
   The CLI extracts `results.report` first, then legacy `report`, then the returned object. Execution status is read from the normalized report before the outer state. Exit code `2` denotes execution/infrastructure failure; exit code `1` denotes completed execution with provider/generation or documentation non-compliance; zero is reserved for a compliant sync (and commands whose documented contract permits informational findings).

5. **Generation metadata is additive and redacted.**
   The workflow preserves `completed`, `reason`, `error`, `iterations`, and approval status without storing request bodies, API keys, or raw authorization headers. Existing report fields remain available for compatibility.

6. **Evidence uses deterministic and live gates.**
   Full pytest, Ruff, strict mypy, diff checks, TDT_HOME precedence probes, model-construction probes, and a disposable full sync are required. The live run must record the exact source HEAD, dirty fingerprint, report result, exit code, and fixture path while leaving the source checkout untouched.

## Risks / Trade-offs

- [Missing fallback credentials] → Construct only available routes, emit a redacted diagnostic, and classify failover as unavailable rather than claiming three-route readiness.
- [Model/provider accepts tool calls but does not finish within the configured cap] → Preserve `max_iterations` and `reason` in the report and return a nonzero compliance exit; do not count an empty result as generated documentation.
- [Outer workflow and nested report disagree] → Give the normalized report precedence for report fields and exit classification; retain the outer execution state only as a fallback for legacy shapes.
- [TDT config schema changes] → Validate provider/model identifiers through agent-core and keep a disposable synthetic `TDT_HOME` precedence test; do not duplicate the schema in docs-sync.
- [Concurrent generated/index edits] → Use a single source writer, capture status fingerprints, and never stage or reset unrelated Graphify/GitNexus/doc-sync paths.

## Migration Plan

1. Apply the code and test tasks in the docs-sync checkout owned by the implementation agent.
2. Update configuration/CLI docs and the canonical `.agents/skills/doc-sync/SKILL.md`; leave the untracked generic scaffold unchanged.
3. Run deterministic gates and synthetic TDT_HOME probes before any live request.
4. Run the disposable full sync with the current TDT credential surface. If a fallback credential is missing or generation returns an incomplete reason, retain that as an explicit readiness warning and do not provision credentials as part of this change.
5. Rollback is a source-tree revert of only the focused implementation/docs/spec commits; protected TDT files and unrelated generated state are outside the transaction.

