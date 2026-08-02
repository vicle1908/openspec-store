## Context

agent-core is now a composition-first runtime: `BaseAgent` is specialized with flavors, profile-scoped skills, tools, hooks, and optional durable scheduling. The workspace has several repos that could consume agent-core (`ai-review`, `webhook-receiver`, Jira/reporting repos), but there is no single contract that says what belongs in agent-core versus what stays repo-local.

Recent research found stale docs/skills examples (`skills.directories`, `SkillLoader.from_config()`, old schedule command names) and no adapter guidance for sibling repos. This phase prevents more drift before broader integration begins.

Constraints:
- Keep Phase 1 documentation/spec-only unless validation finds a blocking API mismatch.
- Do not split agent-core or move code between repos in this change.
- Do not add consumer repo adapters yet; those belong to Phase 2.
- Treat current `agent-core` code as source of truth for APIs and CLI commands.

## Goals / Non-Goals

**Goals:**
- Define a canonical integration contract for consumer repos.
- Standardize composition-over-inheritance guidance.
- Standardize profile-based skill selection and diagnostics guidance.
- Standardize durable scheduling startup ownership.
- Remove stale examples from docs/skills that contradict current agent-core behavior.

**Non-Goals:**
- No runtime refactor.
- No repo split.
- No new package or adapter implementation.
- No adoption work in `ai-review`, `webhook-receiver`, or Jira repos.

## Decisions

1. **Contract lives in `tdt-meta/docs/agent-core/`**
   - Rationale: It is workspace-level guidance for sibling repos, not only agent-core internals.
   - Alternative: Put it only in `agent-core/docs/`. Rejected because consuming repos need a cross-repo contract.

2. **agent-core remains one runtime repo in Phase 1**
   - Rationale: Runtime modules remain coupled and are still evolving together. Splitting now would increase coordination cost.
   - Split candidates can be revisited after adapter adoption and release metrics exist.

3. **Repo-local adapters are the extension boundary**
   - Rationale: Consumer repos should translate their domain concepts into `BaseAgent` config (flavor/profile/tools/hooks), not subclass agent-core or duplicate runtime logic.

4. **Docs must use only current public API**
   - Current patterns: `BaseAgent(..., skill_profile=...)`, `skills.profiles`, `agent-core skills doctor`, `schedules trigger`, `engine.apply_schedules()`.
   - Removed/stale patterns must not appear as recommendations: `skills.directories`, `SkillLoader.from_config()`, `MemoryFacade.from_config()`, `schedules run`.

5. **Recommended APIs are validated as runnable, not just free of stale strings**
   - Decision: A verification task executes a minimal snippet exercising the exact recommended signatures (`BaseAgent(skill_profile=...)`, `skills.profiles` load, `apply_schedules()` order) against the current build.
   - Rationale: Removing old references does not prove the new ones are correct. Grep catches stale patterns; execution catches a contract that is wrong in the opposite direction.

6. **Forward-looking adoption examples are non-normative**
   - Decision: `ai-review`/`webhook-receiver` adoption scenarios are illustrative Phase 2 examples, not Phase 1 `SHALL` requirements, because no consumer adopts in Phase 1 and the scenarios are not testable now.
   - Rationale: A docs-only phase should not carry normative requirements that cannot be verified within the phase.

7. **The invocation contract is a Phase 2 deliverable**
   - Decision: Phase 1 records — but does not define — the consumer invocation contract (input schema, result shape, error semantics).
   - Rationale: Phase 2 adapters depend on it; defining it prematurely without an adapter to validate against risks guessing. Explicitly deferring prevents adapters being built against an undefined interface.

8. **Contract document uses `$WORKSPACE`-relative paths**
   - Decision: The shipped contract under `tdt-meta/docs/agent-core/` uses `$WORKSPACE`-relative paths, not a hardcoded home directory.
   - Rationale: It is cross-repo guidance read by other developers; hardcoded `/Users/<name>/...` paths are non-portable.

## Risks / Trade-offs

- **[Risk] Contract is treated as optional prose.**
  **Mitigation:** Add normative MUST/SHALL requirements in OpenSpec and link docs/skills to the contract.

- **[Risk] Consumer repos still duplicate runtime logic.**
  **Mitigation:** Phase 2 should add repo-local adapters and smoke tests; Phase 1 explicitly sets the boundary.

- **[Risk] Docs drift again after CLI/API changes.**
  **Mitigation:** Tasks require command/API grep checks AND a runnable API-validation snippet before closeout.

- **[Risk] New contract recommends an API that is itself wrong.**
  **Mitigation:** Task 4.2 executes the recommended signatures against the current build, so the contract cannot ship recommending a non-runnable pattern.
