## 1. Pre-edit Safety and Policy Decisions

- [x] 1.1 In `ai-harness-skills`, run `openspec list`, confirm this change is active, and record the required `Refs: openspec/changes/enforce-harness-traceability-completeness/` commit footer.
- [x] 1.2 Re-run upstream GitNexus impact for `authoritative_verification`, `TraceabilityMatrix.coverage`, `WorkflowEngine._complete_stage`, `Ledger.create_run`, and runtime schema resolution; stop for confirmation on HIGH or CRITICAL results.
- [x] 1.3 Enforce the finalized policy-v2 applicability set: only an evidence-backed accepted `api_contract` revision may be `not_applicable` and authorize `DES -> TASK`; reject `not_applicable` for every other identifier-owning stage.
- [x] 1.4 Implement exact-match active-run compatibility for the pinned schema/policy pair, while preserving read-only version-1 historical outcomes with legacy-policy warnings.

## 2. RED Traceability Checkpoint

- [x] 2.1 Add `tests/traceability/test_matrix.py` regressions proving `REQ -> AC -> TC -> ATP -> VER` is incomplete when applicable `DES`, `API`, or `TASK` layers are absent.
- [x] 2.2 Add tests for stage-owned identifier kinds, duplicate IDs, wrong-stage IDs, reverse links, unknown links, and missing applicable-stage identifiers.
- [x] 2.3 Add tests for every required obligation: `REQ -> DES`, `REQ/AC -> TC`, `DES -> API|TASK`, `API -> TASK`, `TASK -> TC`, `TC -> ATP`, and `ATP -> VER`.
- [x] 2.4 Add tests proving an evidence-backed API `not_applicable` revision permits only the approved `DES -> TASK` bypass.
- [x] 2.5 Add workflow/report tests proving provider-supplied percentages cannot override missing obligations and missing categories are deterministic.
- [x] 2.6 Commit the failing regression suite as the required RED checkpoint without `--no-verify`.

## 3. Versioned Traceability Policy

- [x] 3.1 Add a focused policy module under `src/ai_harness/traceability/` defining identifier ownership, required transitions, allowed applicability bypasses, and policy version.
- [x] 3.2 Refactor `TraceabilityMatrix` to return graph-validity and missing-obligation results separately from presentation percentages.
- [x] 3.3 Enforce stage ownership using accepted artifact stage identity and reject invalid identifiers before terminal materialization.
- [x] 3.4 Update `authoritative_verification` to derive `complete` only from the versioned policy, accepted applicability, graph validity, and absence of unresolved assumptions.
- [x] 3.5 Preserve existing coverage keys while adding deterministic missing-obligation categories and policy provenance.

## 4. Schema and Policy Pinning

- [x] 4.1 Add tests proving `harness start` records the actual installed schema version and verification-policy version rather than default constants.
- [x] 4.2 Add tests proving runtime resume fails unchanged on an incompatible installed schema/policy version.
- [x] 4.3 Add tests proving legacy verification reports retain immutable outcomes with an explicit legacy-policy warning.
- [x] 4.4 Update run creation, ledger records/schema as needed, runtime composition, stage requests, and reporting to carry pinned versions.
- [x] 4.5 Version the managed `harness-13` resources compatibly and update initializer clean/repeat/upgrade/conflict fixtures.

## 5. GREEN Integration and Documentation

- [x] 5.1 Update the verify result schema/template and traceability skill references with stage ownership, required obligations, bypass rules, and policy versions.
- [x] 5.2 Update evidence/traceability, reference, security, architecture, and operations documentation without claiming implementation or test execution.
- [x] 5.3 Update guided and fake-provider headless fixtures so all applicable stages create correctly owned identifiers and the full chain reaches completion.
- [x] 5.4 Add full workflow tests for complete, partial, blocked-invalid, API N/A, restart, supersession, and legacy-policy reporting.
- [x] 5.5 Commit the implementation and passing regression suite as the required GREEN checkpoint with the OpenSpec reference footer.

## 6. Verification and Rollback Evidence

- [x] 6.1 Run `uv sync --frozen`, Ruff lint/format checks, strict mypy, the full pytest suite with coverage, dependency audit, schema validation, skill validation, and strict validation of this change.
- [x] 6.2 Run `npx gitnexus detect-changes --scope staged -r ai-harness-skills` before each implementation commit and investigate unexpected flows.
- [x] 6.3 Exercise an initializer schema upgrade and incompatible active-run resume in a temporary project; preserve output as implementation evidence.
- [x] 6.4 Document rollback behavior for new-policy runs, legacy reports, managed schema resources, and any ledger migration; do not rewrite immutable revisions.
