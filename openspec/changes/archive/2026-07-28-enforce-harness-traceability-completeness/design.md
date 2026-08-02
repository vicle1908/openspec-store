## Context

`ai-harness-skills` derives the terminal traceability matrix from accepted structured revisions. The current matrix verifies link direction and reports four reachability percentages, but `complete` is calculated only from those percentages and the absence of terminal assumptions. A graph containing `REQ -> AC -> TC -> ATP -> VER` can therefore reach 100 percent without applicable design, API, or task identifiers.

Run metadata contains `schema_name` and `schema_version`, but run creation currently uses default values and runtime composition loads the currently installed schema without comparing it with the recorded run version. Tightening verification without pinning the policy could silently change an active or historical run's meaning.

Only `ai-harness-skills` implementation and its `harness-workflow` contract are modified. There is no service deployment, external API, mobile application, `agent-core`, or `agent-harness` integration.

## Goals / Non-Goals

**Goals:**

- Make `complete` mean that every applicable planning layer has stage-owned identifiers and all required downstream obligations are satisfied.
- Preserve explicit `not_applicable` stages without letting an applicable layer disappear from coverage.
- Produce deterministic, actionable missing-obligation output.
- Pin schema and verification-policy versions for the lifetime of a run.
- Preserve immutable legacy revisions and report their policy provenance.

**Non-Goals:**

- Change the 13-stage order or gate topology.
- Prove implementation or test execution.
- Introduce a graph database, distributed state, or new dependency.
- Rewrite accepted legacy artifacts.

## Decisions

### 1. Separate graph validity, mapping obligations, and presentation metrics

The traceability layer will model three independent results:

1. Graph validity: identifiers are known, unique, stage-owned, and links move downstream.
2. Required obligations: every applicable source identifier reaches the required next planning kind.
3. Presentation metrics: percentages and missing identifiers derived from those obligations.

`complete` depends on graph validity and zero missing required obligations. Percentages are descriptive output, not the authority by themselves.

Alternative considered: only add design/API/task percentages. Rejected because percentages still permit wrong-stage identifiers and ambiguous bypass paths.

### 2. Define stage ownership and applicability-aware obligations centrally

A versioned traceability policy will map stable kinds to owning stages and define required transitions. At minimum it enforces:

- each `REQ` reaches `DES` and `TC`;
- each `AC` reaches `TC`;
- each applicable `DES` reaches `API`, or reaches `TASK` when API is accepted as `not_applicable`;
- each `API` reaches `TASK`;
- each `TASK` reaches `TC`;
- each `TC` reaches `ATP`;
- each `ATP` reaches `VER`;
- at least one stage-owned `VER` exists.

The policy uses accepted artifact applicability, not provider assertions from outside the accepted revision set. Policy version 2 permits `not_applicable` only for `api_contract`, matching the managed `harness-13` instruction. Its evidence-backed accepted revision contributes the single `DES -> TASK` bypass. Every other identifier-owning stage is required and must emit its owned identifier kind; the common provider-result schema does not grant additional bypass authority merely because it exposes the `not_applicable` enum.

Alternative considered: hard-code checks inside `authoritative_verification`. Rejected because policy, traversal, reporting, and tests would remain coupled in a CRITICAL function.

### 3. Treat stage ownership violations as invalid input

An identifier created by the wrong stage, a duplicate identifier, a reverse edge, or an unknown reference blocks acceptance. A valid graph with missing required mappings produces terminal `partial`. This keeps malformed data distinct from an incomplete but inspectable plan.

### 4. Pin schema and verification policy at run creation

The start path will resolve the installed `harness-13` schema metadata and verification-policy version and pass both explicitly to the ledger. Active advancement uses exact-match compatibility: the installed runtime must support the run's exact pinned schema and verification-policy pair before beginning another stage. Policy version 2 ships the version-2 handler; an active legacy run pinned to version 1 fails closed and must be completed with its compatible earlier runtime or restarted as a new version-2 run. Historical version-1 revisions remain readable and reportable but are never reinterpreted. The run request and terminal report include policy provenance.

Alternative considered: reinterpret every stored run under the newest policy. Rejected because immutable artifacts would acquire a different assurance meaning without a new revision.

### 5. Preserve legacy history without preserving false assurance

Legacy verification revisions remain byte-identical. Reports identify their legacy policy version and warn that they were not evaluated by the stronger policy. A legacy run requires an explicit new verification revision or a new run to obtain current-policy completion; the CLI does not mutate old evidence automatically.

### 6. Keep output backward-friendly

Existing coverage fields remain. `missing_mappings` gains deterministic obligation categories such as `requirement_to_design` and `task_to_test_case`, and report output gains policy-version fields. This avoids removing existing machine-readable fields while correcting their authority.

## Risks / Trade-offs

- **Previously complete runs may no longer qualify under the new policy** -> Preserve historical results with an explicit legacy-policy warning and require intentional re-verification.
- **Applicability bypasses can become another weak path** -> Define bypasses centrally and accept them only from evidence-backed, accepted N/A revisions.
- **Stage ownership may reject previously tolerated claim placement** -> Document the ownership table in templates and skills and add targeted validation messages.
- **CRITICAL blast radius in terminal verification** -> Preserve separate RED and GREEN commits, keep policy logic outside the workflow engine, and execute full guided/headless integration suites.
- **Schema upgrade during an active run** -> Pin versions and fail closed rather than silently using the newly installed schema.

## Migration Plan

1. Add failing tests for the known false-complete graph, wrong-stage identifiers, missing applicable kinds, API N/A bypass, and policy-version mismatch.
2. Add the versioned traceability policy and obligation result without changing terminal orchestration.
3. Integrate the policy with authoritative verification and reporting.
4. Resolve and persist actual schema/policy versions at run creation; fail closed on incompatible resume.
5. Update schema templates, traceability skill references, CLI/reference documentation, and legacy-report messaging.
6. Run the full frozen validation suite and opt-in real-provider checks only if separately authorized.

Rollback restores the earlier package version. New-policy runs remain in the ledger but cannot be advanced by a binary that does not support their pinned version. Immutable artifacts are never rewritten during rollback.

## Open Questions

None. Policy version 2 has one applicability bypass (`api_contract`) and exact-match compatibility for active advancement.
