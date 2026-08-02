## 1. Contract Definition

- [x] 1.1 Create `$WORKSPACE/tdt-meta/docs/agent-core/integration-contract.md` with normative ownership boundaries (agent-core runtime vs repo-local adapter vs skill/tool policy). Use `$WORKSPACE`-relative paths throughout — no hardcoded home directory.
- [x] 1.2 Document composition-first specialization contract (`BaseAgent`, flavors, tools, hooks, `skill_profile`) and explicitly reject subclass-driven domain behavior. Mark `ai-review`/`webhook-receiver` adoption examples as non-normative Phase 2 illustrations.
- [x] 1.3 Document profile-based skill contract (`skills.profiles`, `skills.active_profile`, `skills doctor`) and profile ownership guidance (global/workspace/repo/specialist).
- [x] 1.4 Document durable scheduling startup contract (import schedule modules -> initialize durable engine -> `apply_schedules()`); link `agent-core/scheduler_setup.py` as the canonical reference.
- [x] 1.5 Record that the consumer invocation contract (input schema, result shape, error semantics) is a Phase 2 deliverable and is intentionally undefined in Phase 1.

## 2. CLI and Runtime Doc Alignment

- [x] 2.1 Update `/Users/lekhanhvinh/Developer/tdt/agent-core/docs/cli.md` so schedule commands use `trigger` (not `run`) and skills docs include profile and doctor usage.
- [x] 2.2 Verify CLI JSON examples in `/Users/lekhanhvinh/Developer/tdt/agent-core/docs/cli.md` match current output shape or mark illustrative examples clearly.
- [x] 2.3 Update `/Users/lekhanhvinh/Developer/tdt/agent-core/docs/building-agents.md` composition guidance if any stale inheritance wording remains.

## 3. Skill Guidance Alignment

- [x] 3.1 Update `/Users/lekhanhvinh/Developer/tdt/tdt-meta/.agents/skills/agent-core-usage/SKILL.md` to remove stale API patterns and align examples to current `BaseAgent` and profile APIs.
- [x] 3.2 Ensure `agent-core-usage` troubleshooting guidance uses `skills doctor` and profile-based diagnostics.

## 4. Verification

- [x] 4.1 Run grep checks across `agent-core/docs`, `tdt-meta/docs/agent-core`, and `tdt-meta/.agents/skills/agent-core-usage/SKILL.md` to ensure no stale command/API references remain (`skills.directories`, `SkillLoader.from_config()`, `MemoryFacade.from_config()`, `schedules run`).
- [x] 4.2 Prove recommended APIs are runnable: execute a minimal snippet against the current agent-core build exercising `BaseAgent(..., skill_profile=...)`, a `skills.profiles` config load, and `engine.apply_schedules()` startup order. Capture the result so the contract recommends only validated signatures.
- [x] 4.3 Run `openspec validate agent-core-integration-contract-phase1 --strict`.
- [x] 4.4 Review changed docs/skills/specs for consistency and non-duplication with existing `agent-core-skill-scope-profiles` outputs.
