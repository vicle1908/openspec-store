## Context

`ai-harness-skills` invokes Claude Code and Codex CLI as native subprocesses. The harness controls a core set of command-line arguments, but configuration currently accepts any non-NUL extra argument that is not on a short reserved-option denylist. This permits MCP, plugin, settings, profile, custom-agent, and permission-bypass options to reach a provider invocation.

The Claude adapter restricts built-in tools but does not disable MCP or other loaded customizations. The Codex adapter requests a read-only sandbox but does not request ephemeral execution or ignore user configuration and execution rules. `SafeProcessRunner` also applies `output_limit` separately to stdout and stderr, despite the documented shared bound.

Only the local `ai-harness-skills` package is deployed. Distribution remains an internal `uv tool` install plus explicit schema/skill initialization; no Docker, launchd, cloud service, or new dependency is introduced.

## Goals / Non-Goals

**Goals:**

- Make the automated headless profile isolated from operator-configurable provider extensions and permission bypasses, with explicit residual provider-managed and project-instruction boundaries.
- Replace open-ended provider arguments with a fail-closed typed contract.
- Make isolation capabilities observable and required for the `automated` tier.
- Enforce one combined subprocess output bound.
- Preserve guided skills and optional native helpers without allowing them to weaken automated execution.

**Non-Goals:**

- Manage provider credentials, installation, or authentication.
- Eliminate all provider implementation risk or indirect prompt injection.
- Add write-capable or implementation stages.
- Replace native CLIs with SDKs, LangGraph, or another runtime.
- Implement cumulative usage and retention policy; those belong to `enforce-harness-runtime-policies`.

## Decisions

### 1. Replace arbitrary arguments with typed provider settings

Provider configuration will expose named settings with explicit types and bounded values. Initial safe settings are limited to model selection through the existing `model_alias`, reasoning/effort controls supported by the adapter, and harness-owned finite turn/budget controls. The adapter constructs every option affecting tools, permissions, sandboxing, working directories, configuration, plugins, MCP, agents, sessions, schemas, and output.

Unknown settings and legacy `extra_args` fail closed with migration guidance. A provider-specific semantic allowlist may be used internally, but the public configuration is not a raw argv escape hatch.

Alternative considered: extend the existing denylist. Rejected because new provider options can create authority before the harness is updated.

### 2. Define a customization-isolated Claude automated profile

The Claude automated profile uses non-interactive structured output together with plan/read-only permissions, `--bare`, `--safe-mode`, `--strict-mcp-config`, `--no-session-persistence`, `--disable-slash-commands`, an explicit read-only built-in tool set, a finite turn bound, and the existing finite process/budget limits. Bare mode is required because it skips hooks, plugin synchronization, skill-directory walks, auto-memory, and keychain reads. It requires `ANTHROPIC_API_KEY` or an approved `apiKeyHelper`; OAuth- or keychain-only installations are guided or experimental rather than automated.

Safe mode disables ordinary custom agents and provider customizations, while provider-managed policy settings remain part of the host boundary. The harness reports that boundary and classifies the profile as automated only when its bounded no-model conformance checks show that the effective policy cannot add execution authority beyond the explicit built-in tool and permission set. Otherwise the provider is downgraded. Direct custom-agent selection is removed from the automated profile. Managed agent templates remain guided helpers. A future explicitly customized headless profile can be experimental, but it cannot inherit the automated label.

Alternative considered: retain `--agent` and attempt to audit every loaded customization. Rejected because effective permissions would depend on mutable provider-owned files outside the run contract.

### 3. Define an isolated Codex automated profile

The Codex automated profile uses `codex exec` with `--sandbox read-only`, explicit cwd and output schema, `--ephemeral`, `--ignore-user-config`, and `--ignore-rules`. Because `--ignore-user-config` skips `$CODEX_HOME/config.toml` but the current loader still resolves project configuration from cwd, the initial automated profile fails closed when an active `.codex/config.toml` exists in the project configuration chain. The harness owns schema, JSON event mode, model selection, working directory, sandbox options, and every `-c` override.

Codex user and project instruction documents that cannot be disabled by the installed CLI remain part of the documented provider boundary: they are untrusted instructions operating within a read-only, non-persistent process and do not grant additional tools. The harness continues to validate the final result and all accepted evidence locally.

### 4. Probe effective isolation capabilities

Provider capabilities gain explicit isolation signals rather than inferring automation from structured output and a read-only token alone. Doctor and execution re-probe the installed CLI for required flags, bare-mode authentication eligibility, provider-managed policy constraints, and active Codex project configuration. They construct bounded checks that fail without model execution when the profile is unavailable.

Version strings are recorded for diagnostics but are not the sole authority. A capability that is present syntactically but fails a deterministic no-model conformance check downgrades the provider.

### 5. Enforce a combined process-output counter

The process runner will coordinate stdout and stderr drains through one synchronized byte counter. Crossing the shared limit kills the child, drains/joins safely, discards content beyond the bound, and reports one bounded provider error. Neither stream receives an independent full allowance.

### 6. Keep provider usage accounting separate

This change may adjust event parsing only where required for isolation/conformance. Authoritative cumulative cost and token accounting remains in the dependent runtime-policy change so two changes do not implement competing budget models.

## Risks / Trade-offs

- **Bare and safe modes remove useful Claude customization and exclude OAuth/keychain-only authentication** -> Keep native agents and those authentication modes for guided/experimental use, and include all authoritative stage instructions in the bounded automated request.
- **Provider flags evolve** -> Probe capabilities at runtime, record the version diagnostically, and fail closed rather than silently dropping isolation.
- **Strict typed settings reduce operator flexibility** -> Add reviewed typed options when a concrete use case appears instead of restoring arbitrary argv.
- **Codex instruction documents may still influence reasoning** -> Treat them as untrusted context, retain the read-only sandbox, and validate output/evidence locally; reject project configuration that could add execution authority.
- **CRITICAL configuration blast radius** -> Land RED/GREEN checkpoints separately and run every CLI/config/provider integration path.
- **Overlap with runtime-policy output limiting** -> This change owns the shared process-bound implementation; the runtime-policy change consumes and tests that contract without reimplementing it.

## Migration Plan

1. Add failing configuration tests for MCP/plugin/profile/permission-bypass options and legacy arbitrary arguments.
2. Add failing adapter tests for the required Claude and Codex isolation argv, bare-mode authentication, active project-configuration rejection, and capability probes.
3. Add a failing combined stdout/stderr limit test.
4. Introduce typed provider settings and actionable migration errors.
5. Implement the two automated profiles and support-tier downgrade behavior.
6. Implement the shared output counter and bounded termination path.
7. Update doctor, reference/security documentation, adapters, skills guidance, and fake-provider fixtures.
8. Run the deterministic suite. Run real-provider smoke tests only with explicit finite-budget authorization.

Rollback restores the previous package. Configurations migrated away from `extra_args` remain readable only if the rolled-back version supports the new keys, so rollback instructions must preserve the prior config file. No runtime database migration is required.

## Open Questions

- A follow-up can decide whether an experimental customized headless profile is valuable; it is not required for this change to be apply-ready.
