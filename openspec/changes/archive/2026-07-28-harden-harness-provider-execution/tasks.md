## 1. Pre-edit Safety and Compatibility Baseline

- [x] 1.1 In `ai-harness-skills`, run `openspec list`, confirm this change is active, and record the required `Refs: openspec/changes/harden-harness-provider-execution/` commit footer.
- [x] 1.2 Re-run upstream GitNexus impact for `validate_config`, `load_config`, `ProviderCapabilities.missing_headless`, `ClaudeAdapter.invoke`, `CodexAdapter.invoke`, and `SafeProcessRunner.run`; stop for confirmation on HIGH or CRITICAL results.
- [x] 1.3 Reconfirm bounded `--version` and relevant `--help` evidence for the supported Claude Code and Codex CLI versions without invoking a model, including Claude bare-mode authentication and Codex project-config loading boundaries.
- [x] 1.4 Finalize the typed provider-setting schema and migration mapping for every currently documented `extra_args` use.

## 2. RED Configuration and Isolation Checkpoint

- [x] 2.1 Add `tests/test_domain_config.py` cases rejecting legacy arbitrary arguments and MCP, plugin, settings, profile, agent, tool, permission-bypass, sandbox, cwd, session, schema, and output-control options.
- [x] 2.2 Add positive configuration tests for bounded typed model/effort/turn settings and actionable migration diagnostics.
- [x] 2.3 Add Claude adapter tests requiring bare and safe modes, strict MCP isolation, disabled slash commands, no session persistence, finite turns, read-only built-in tools, bare-compatible authentication, managed-policy downgrade, and absence of custom-agent authority.
- [x] 2.4 Add Codex adapter tests requiring read-only, ephemeral execution, ignored user configuration/rules, explicit cwd/schema, rejection of active project `.codex/config.toml`, untrusted instruction-document treatment, and absence of harness-overriding options.
- [x] 2.5 Add conformance/doctor tests downgrading providers that lack any required isolation or non-persistence capability.
- [x] 2.6 Add a process-runner test where combined stdout and stderr exceed one shared bound even though neither stream exceeds it independently.
- [x] 2.7 Commit the failing security regression suite as the required RED checkpoint without `--no-verify`.

## 3. Typed Provider Configuration

- [x] 3.1 Replace `ProviderConfig.extra_args` with typed provider settings in `src/ai_harness/config.py`; reject unknown and legacy raw options before run creation.
- [x] 3.2 Add provider-specific value validation, arity-independent serialization, finite bounds, and secret-safe error handling.
- [x] 3.3 Update runtime composition, configuration examples, CLI/reference output, and fixtures to use only typed settings.
- [x] 3.4 Confirm no compatibility path reconstructs arbitrary argv or permits a provider option to override a harness-owned setting.

## 4. Isolated Provider Profiles and Capabilities

- [x] 4.1 Extend `ProviderCapabilities` and support-tier logic with explicit configuration-isolation, MCP isolation, non-persistence, bounded-turn, bare-mode authentication, managed-policy, and project-config isolation capabilities.
- [x] 4.2 Implement the Claude automated profile with bare and safe modes, strict MCP isolation, disabled slash commands, no session persistence, finite turns, read-only tools, structured output, fresh invocation identity, and fail-closed managed-policy handling.
- [x] 4.3 Remove direct custom-agent selection from the Claude automated profile while preserving managed agents as guided helpers and documenting experimental customization semantics.
- [x] 4.4 Implement the Codex automated profile with read-only sandbox, ephemeral session, ignored user config/rules, explicit cwd/schema, structured JSON events, and fail-closed active project-config detection.
- [x] 4.5 Update doctor and execution-time probes so capability changes between diagnosis and invocation fail closed before model execution.

## 5. Shared Process-output Enforcement

- [x] 5.1 Implement one synchronized stdout-plus-stderr byte counter in `SafeProcessRunner.run` with race-safe child termination and thread cleanup.
- [x] 5.2 Preserve secret redaction, protected-value rejection, timeout semantics, process status, and bounded diagnostics across the new drain path.
- [x] 5.3 Add stress regressions for simultaneous streams, exact-bound output, multibyte UTF-8 truncation, timeout during drain, cancellation, and non-zero exit.

## 6. GREEN Integration and Documentation

- [x] 6.1 Update fake-provider fixtures and full headless workflows for the expanded automated capability baseline.
- [x] 6.2 Update security, architecture, reference, getting-started, development, and adapter documentation to distinguish automated customization-isolated, guided, and experimental customized profiles and document residual managed-policy/instruction boundaries.
- [x] 6.3 Update managed Claude/Codex helper documentation so guided helpers never imply authority over the headless isolation profile.
- [x] 6.4 Commit the implementation and passing regression suite as the required GREEN checkpoint with the OpenSpec reference footer.

## 7. Verification and Rollback Evidence

- [x] 7.1 Run frozen sync, Ruff lint/format, strict mypy, full pytest/coverage, dependency audit, strict OpenSpec/schema validation, and all skill validators.
- [x] 7.2 Run `npx gitnexus detect-changes --scope staged -r ai-harness-skills` before each implementation commit and investigate unexpected CLI/provider flows.
- [x] 7.3 Live smoke checks deferred: no explicit finite-budget approval was provided; the two live tests remain explicitly skipped and deterministic verification is authoritative.
- [x] 7.4 Document rollback for typed configuration, provider profiles, and managed helper files; preserve the prior config before deployment.
