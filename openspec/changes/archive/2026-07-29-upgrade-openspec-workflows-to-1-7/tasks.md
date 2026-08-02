## 1. Baseline and safety prerequisites

- [x] 1.1 Run `make workstation-tool-update-preflight`, verify `~/.local/state/microservices-workstation-tool-update/active.lock` is absent, inspect the latest successful redacted maintenance report, and prove two consecutive `openspec --version` probes resolve the approved 1.7.0 CLI before any generated-file mutation.
- [x] 1.2 Reconfirm the approved OpenSpec version, Node.js `>=20.19.0` engine, package integrity, release notes, customization contract, and supported-tool paths through npm and current official documentation; retain the checked date and sources.
- [x] 1.3 Inventory the exact eleven configured tools and twelve workflows, all 132 generator-managed skills, twelve canonical `.agents` copies, commands, prompts, workflows, legacy paths, generator versions, invocation forms, and manifest entries; separately record ambiguous or hand-authored files that migration MUST preserve.
- [x] 1.4 Add failing fixture coverage for the observed 1.6 baseline: stale `generatedBy`, unsupported `AskUserQuestion`/`TodoWrite`, Codex `/opsx:*` references, background archive sync, legacy managed `.kimi/` files, an incomplete tool refresh, unpinned CI installation, and optional validation skips.

## 2. Canonical version and controlled refresh

- [x] 2.1 Keep `scripts/config/agent-skill-surfaces.json#nativeVersions.openspec` as the validated exact version source, add an `openspec` policy block for `profile: custom`, `delivery: both`, the ordered twelve workflows, exact eleven tool IDs, managed and legacy roots, and invocation invariants, and expose the pin to local checks and CI without duplicating it.
- [x] 2.2 Add `scripts/openspec-surfaces.sh` with `scripts/openspec_surface_policy.py` support for a fail-closed refresh preflight that verifies Node compatibility, the installed CLI pin, stable repeated version probes, an absent updater lock, the exact profile, delivery, workflows, and tools before mutation.
- [x] 2.3 Parse `openspec config list --json` into only the redacted `profile`, `delivery`, and `workflows` fields for comparison and retained evidence; prove the raw telemetry identifier and unrelated personal global configuration are never logged or stored.
- [x] 2.4 Add bounded inventory and rollback-snapshot support for only OpenSpec-owned generated surfaces, canonical shared copies, policy, manifest, config, validators, documentation, and CI files; stop on ambiguous ownership.
- [x] 2.5 Add fixture tests proving every preflight mismatch, unsafe config extraction, and snapshot failure exits before workspace mutation and reports actionable remediation without changing personal global configuration.

## 3. Project guidance and authoring rules

- [x] 3.1 Add concise `operations.apply.guidance` and `operations.archive.guidance` to `openspec/config.yaml`, keeping advisory inputs separate from artifact rules, task state, user choices, and mandatory repository policy.
- [x] 3.2 Update root/OpenSpec guidance and owning documentation for the exact version-refresh workflow, current tool invocation forms, generator ownership, inline archive sync, new-capability Purpose text, and the permitted versus prohibited uses of `skip_specs: true`.
- [x] 3.3 Extend agent-guidance fixtures so required OpenSpec safety text and canonical commands are validated without embedding transient dependency versions in durable architectural guidance.

## 4. Regenerate and migrate managed surfaces

- [x] 4.1 Capture the approved snapshot, run `openspec update --force` exactly once with the verified 1.7.0 CLI and policy inputs, retain an owner/tool/workflow inventory of every generated addition, modification, move, and deletion, and independently verify complete output even if the updater reports a per-tool failure and continues.
- [x] 4.2 Verify OpenSpec's automatic ownership-safe `.kimi/` to `.kimi-code/` migration moved only managed `openspec-*` skills and `opsx-*` commands, retained and reported divergent destination copies, preserved hand-authored files, and changed no unrelated agent directory.
- [x] 4.3 Verify Codex is skills-only with `$openspec-*` references, verify every other configured tool uses its registered invocation syntax, and remove only obsolete OpenSpec-owned command or prompt files.
- [x] 4.4 After all eleven generator-managed surfaces pass validation, import the twelve regenerated Codex skills into the canonical `.agents/skills` OpenSpec entries, restore exact `.agents`/`.codex` parity, update the approved version policy, and regenerate `agent-skills-manifest.json` through repository support.
- [x] 4.5 Inspect the regenerated archive, bulk-archive, sync, propose, fast-forward, explore, and update workflows to prove runtime-neutral interaction guidance, current project-context loading, `skip_specs` handling, current instruction lookups, synchronous sync, and main-spec verification before move.

## 5. Drift validation and regression coverage

- [x] 5.1 Extend documentation/surface validation to compare the approved pin with every managed generator version, policy record, manifest entry, documented install, and CI-resolved version.
- [x] 5.2 Add tool-aware validation for the exact eleven-tool inventory, 132 generator-managed skills plus twelve canonical copies, Codex skills-only delivery, per-adapter invocation syntax, the Kimi Code path, absence of unsupported runtime-specific tools, complete twelve-workflow coverage, and safe archive/sync sequencing.
- [x] 5.3 Add negative fixtures for version, profile, tool inventory, partial generator success, redaction, manifest, parity, path, invocation, ownership, archive-race, and unpinned-install drift; prove diagnostics identify the exact affected surface and never auto-repair it.
- [x] 5.4 Run the focused validator and fixture suites after each validation change and retain exact passing commands and outputs before marking the corresponding task complete.

## 6. Deterministic CI enforcement

- [x] 6.1 Update release evidence to set up Node.js 22, read the approved pin through the validated repository helper, install `@fission-ai/openspec@<approved-pin>`, assert the resolved version, and run `openspec validate --strict --all --no-interactive` without an unversioned bootstrap.
- [x] 6.2 Update normal verification to use the same pin and fail closed on missing installation, version drift, or strict validation failure instead of emitting a successful skip.
- [x] 6.3 Add static workflow/fixture checks proving both CI paths derive the same version source, contain no floating OpenSpec install, and preserve the distinction between spec validity and deployment readiness.

## 7. Documentation, rollback, and handoff

- [x] 7.1 Update the repository/OpenSpec documentation and skill-distribution runbook with prerequisites, supported profile, regeneration, review, Kimi/Codex migration, validation, upgrade-check, and non-destructive rollback procedures.
- [x] 7.2 Rehearse rollback in a disposable fixture, proving the pin, generated surfaces, canonical copies, manifest, config, validators, and CI return to one coherent prior version while unrelated files remain byte-for-byte unchanged.
- [x] 7.3 Retain a final redacted migration summary listing the approved version, Node runtime, eleven configured tools, twelve workflows, 132 generated skills, twelve canonical copies, generated-path changes, exact checks, skipped checks, rollback evidence, and unresolved upstream beta features without claiming service or deployment readiness.

## 8. Final verification

- [x] 8.1 Assert no managed OpenSpec surface retains `generatedBy: "1.6.0"`, obsolete tool invocations, unsafe background archive sync, or OpenSpec-owned legacy Kimi paths, and verify manifest hashes against the final files.
- [x] 8.2 Run `make validate-agent-guidance` and the focused agent-surface/validator fixture suites; correct every in-scope failure.
- [x] 8.3 After the final implementation diff is stable, run `make validate-deployment`, retain the exact new manifest, and update `verification/documentation-currency.json#currentDeploymentManifest` to that retained path without interpreting the result as cloud, staging, production, or service deployment readiness.
- [x] 8.4 Run `make validate-documentation`; correct every OpenSpec version, inventory, parity, path, invocation, manifest, workflow, evidence-digest, and link failure.
- [x] 8.5 Run `openspec validate upgrade-openspec-workflows-to-1-7 --strict --no-interactive` and `openspec validate --strict --all --no-interactive`; distinguish unrelated baseline findings without weakening either gate.
- [x] 8.6 Run `make verify-pr` for the repository-wide validator and workflow changes, recording any unavailable external environment separately rather than marking an unrun check as passing.
- [x] 8.7 Run `graphify update .` after implementation code or validation logic changes and inspect the affected guidance, generator, manifest, and CI paths before final handoff.
