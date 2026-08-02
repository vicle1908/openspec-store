## Context

agent-core already supports multi-directory skill loading and deterministic shadowing. The current default directories are:

1. `.agents/skills` resolved against the workspace root
2. `~/.tdt/skills` as global fallback

That default solved discovery, but not selection. In the TDT workspace, `/Users/lekhanhvinh/Developer/tdt/.agents/skills/` currently contains 93 shared skills, including overlapping providers and task domains. The repo `/Users/lekhanhvinh/Developer/tdt/agent-core/` currently has no repo-local `.agents/skills/` directory. If every agent loads the whole workspace set, specialist agents get unnecessary matches and users see scattered ownership. If each repo copies skills locally, duplication and drift increase.

The right layer is not a new package manager. agent-core needs a profile/filter layer that becomes the canonical way skills are composed, replacing the flat `skills.directories` list entirely. Since agent-core is pre-release with no external consumers, this change makes the clean break now rather than carrying a compatibility shim.

Constraints:
- `SkillLoader` directory-scan and shadow semantics are reused internally but are no longer the public configuration surface.
- Existing SKILL.md files keep working without new required frontmatter (metadata is optional and additive).
- Profile selection must be deterministic and testable without external services.
- Missing profile metadata must not break loading.
- Profile selection must work per-agent, not only per-process, so multiple specialist agents can run in one process with different skill sets.
- Keep setup small: no registry server, remote installer, dependency solver, or separate manifest language unless config can no longer express the model.

## Goals / Non-Goals

**Goals:**
- Make named profiles the single canonical skill-composition model.
- Ship a built-in `default` profile so zero-config agents still load skills.
- Allow per-agent profile selection (`BaseAgent(skill_profile=...)`) independent of process-global config.
- Provide clear rules for global vs workspace vs repo-local vs specialist skills.
- Add diagnostics for duplicated, shadowed, conflicting, or stale skill definitions.
- Let generated agents declare a profile rather than hard-code many skill directories.
- Make agent composition explicit and auditable.

**Non-Goals:**
- No remote marketplace, registry service, or network skill discovery.
- No automatic dependency installation for skills.
- No semantic rewriting of skill descriptions or matching algorithms.
- No broad reorganization of all workspace skills in this change (metadata annotation is opt-in, incremental).
- No backward-compatibility shim for the removed `skills.directories` field.

## Decisions

1. **Profiles are the canonical skill config — `skills.directories` is removed**
   - Decision: Replace the flat `skills.directories` list with `skills.profiles` (a map of named profiles) and `skills.active_profile` (the default selection). The old `skills.directories` field is deleted, not deprecated.
   - Shape:
     ```yaml
     skills:
       active_profile: workspace
       profiles:
         workspace:
           directories:
             - .agents/skills
             - ~/.tdt/skills
           include: []
           exclude: []
           scopes: [workspace, global]
     ```
   - Rationale: One composition model, not two. Pre-release status means no migration cost. Directory lists become an implementation detail inside a profile.
   - Alternative considered: Keep `skills.directories` alongside profiles. Rejected — two precedence systems is exactly the confusion this change removes.

2. **A built-in `default` profile guarantees zero-config loading**
   - Decision: When `skills.profiles` is empty, agent-core synthesizes a built-in `default` profile equal to `directories: [".agents/skills", "~/.tdt/skills"]`, `scopes: [repo, workspace, global]`, no include/exclude. `active_profile` defaults to `default`.
   - Rationale: Zero-config agents still load skills. The default is expressed *as a profile*, so there is exactly one code path.
   - Alternative considered: Require an explicit profile. Rejected — needless friction for the common case.

3. **Scopes are optional metadata with conservative defaults**
   - Decision: SKILL.md frontmatter may include optional fields:
     - `scope`: `global`, `workspace`, `repo`, or `specialist`
     - `profiles`: list of profile names that should include the skill
     - `repositories`: list of repo names or paths the skill is intended for
     - `owners`: list of maintainers or teams
     - `conflicts_with`: list of skill names that should not be active together
     - `replaces`: list of older skill names this skill supersedes
   - Default: a skill with no metadata remains loadable and is filtered only by directory/profile rules.
   - Rationale: Current skills stay valid while diagnostics can become more useful over time.
   - Alternative considered: Required metadata. Rejected as too much churn for 90+ skills.

4. **Profile filtering happens after directory scan and before matching**
   - Decision: Load candidates using existing directory order, then apply profile filters and metadata checks to produce active skills.
   - Rationale: Keeps loader's file discovery simple and preserves shadow detection data for diagnostics.
   - Alternative considered: Skip directories based on profile before scanning. Rejected because diagnostics would miss hidden duplicates and shadows.

5. **Conflict handling is diagnostic-first, not auto-delete**
   - Decision: If active skills conflict by metadata, diagnostics report the issue. Runtime loading does not automatically remove either skill unless explicit profile excludes one.
   - Rationale: Silent conflict resolution can hide useful capabilities and confuse matching. Humans should choose exclusions.
   - Alternative considered: Highest-precedence wins for conflicts. Rejected because `conflicts_with` is semantic, not path shadowing.

6. **Precedence remains directory-order-based**
   - Decision: Name collisions still use existing rule: earlier directory wins. Profiles can change directory order only by declaring their `directories` order.
   - Rationale: Predictable and already documented.
   - Alternative considered: Scope priority (`repo > workspace > global`) independent of directory order. Rejected because it creates two precedence systems.

7. **Doctor command is the primary guardrail**
   - Decision: Add `agent-core skills doctor` with profile-aware diagnostics. It reports:
     - missing directories;
     - invalid profile names;
     - duplicates and shadowed skills;
     - conflicts in active profile;
     - metadata references to missing skills/profiles;
     - repo-scoped skills loaded outside intended repo.
   - Rationale: Avoids bloated setup while giving concrete safety checks before agents run.
   - Alternative considered: Fail startup on every issue. Rejected because existing skill sets are mixed and should migrate gradually.

8. **Agent scaffolding declares profile intent**
   - Decision: `agent-core init` templates include config with an `active_profile` and starter repo-local skill location. Specialist templates can create a profile stub but not a large copied skill bundle.
   - Rationale: New agents should be explicit about composition without duplicating workspace skills.
   - Alternative considered: Copy selected workspace skills into generated repos. Rejected because it causes drift.

9. **Profile selection is per-agent, with config as the default**
   - Decision: `BaseAgent` accepts an optional `skill_profile: str | None`. When set, the agent resolves skills through that profile; when `None`, it falls back to `settings.skills.active_profile`. The profile resolver is a pure function of `(profiles_config, profile_name, workspace_root)` so it can be called per-agent without global state.
   - Rationale: A reviewer and an explorer can run in the same process with different skill sets. Process-global `active_profile` alone breaks orchestration and multi-agent workflows. This mirrors the existing composition-first pattern (flavors, tools, hooks are all per-agent).
   - Alternative considered: Process-global `active_profile` only. Rejected — incompatible with the multi-agent execution the orchestration capability already supports.

10. **Profiles govern selection; the matcher governs runtime relevance**
    - Decision: Profiles decide *which skills exist* for an agent (governance, ownership, scope). `SkillMatcher` continues to decide *which loaded skills are relevant* to a given task (relevance × effectiveness, threshold). The two are orthogonal and both apply: profile filters first, matcher ranks the survivors.
    - Rationale: Without this boundary, teams would try to use profiles for relevance tuning (wrong tool) or the matcher for governance (can't express ownership/conflicts). Stating it prevents misuse and keeps each mechanism focused.
    - Consequence: A profile reduces the candidate set the matcher sees, lowering token cost and false matches; it does not replace threshold tuning.


## Current-Code Integration Notes

Implementation should touch the smallest set of modules:

- `SkillLoader` remains responsible for filesystem scan, parsing, cache, and shadow resolution — but these are now *internal* mechanics invoked by the profile resolver, not the public config surface.
- Add profile/filter/diagnostic behavior in new skill-system modules (`profiles.py`, `diagnostics.py`) instead of bloating `loader.py`.
- Extend `SkillFrontmatter` in `models.py`; do not create a second metadata parser.
- Remove `SkillsSettings.directories`. All call sites that read it (`skills list`, `skills reload`, health checks, `_resolve_skill_directories`, and the agent run helper) must resolve through the profile resolver instead.
- `BaseAgent.__init__` gains `skill_profile: str | None = None`; the run loop resolves the active skill set via the profile resolver using that value or the configured default.
- Keep `skills reload` as a cache refresh/listing operation; it resolves through the same profile path as `skills list` but holds no persistent state.
- Scaffolding templates add a minimal starter `config.yaml` containing an `active_profile` and one matching profile, since profiles are now the only skill-config surface.

## Risks / Trade-offs

- **[Risk] Profiles become another source of confusion if too expressive.**
  **Mitigation:** Keep profile schema limited to `directories`, `include`, `exclude`, and optional `scopes`. No expression language.

- **[Risk] Removing `skills.directories` breaks any code reading it directly.**
  **Mitigation:** Pre-release status means no external consumers. A repo-wide grep for `skills.directories` / `_resolve_skill_directories` is part of the task list; all call sites move to the profile resolver in the same change.

- **[Risk] Metadata may drift or become stale.**
  **Mitigation:** `skills doctor` validates references and repo/profile mismatches; tests cover metadata parsing.

- **[Risk] Directory scanning all candidates before filtering costs startup time.**
  **Mitigation:** Reuse the existing TTL cache. Profile filtering is in-memory over parsed metadata. Revisit only if measured slow.

- **[Risk] Users may expect profile selection to install missing skills.**
  **Mitigation:** Explicit docs: profiles select from local directories only; installation remains separate.

## Implementation Plan

1. Add profile data models and the built-in `default` profile; remove `skills.directories`.
2. Add optional metadata parsing (`scope` in v1) with `extra="ignore"` tolerance.
3. Add the pure-function profile resolver and filtering, with tests.
4. Wire `BaseAgent(skill_profile=...)` and move all `skills.directories` call sites onto the resolver.
5. Add `agent-core skills doctor` + JSON output + `--profile` selection.
6. Update scaffolding templates to ship a starter `config.yaml` with an `active_profile`.
7. Update docs (configuration, extending, building-agents) and workspace placement guidance.
8. Optionally annotate a small set of high-value workspace skills with `scope`; do not bulk-edit all 90.

## Resolved Decisions (formerly open questions)

11. **Specialist profiles are defined locally by each agent; no canonical `tdt` profile in v1.**
    - Each specialist agent declares its own profile in its `config.yaml`. A shared workspace profile can be revisited later if duplication appears, but is out of scope here.

12. **`repositories` matches by basename OR explicit path string.**
    - The resolver compares the metadata entry against both the workspace-root basename and its absolute path. This avoids overengineering while supporting monorepo paths.

13. **`skills doctor` is advisory everywhere; CI-gating is opt-in per repo.**
    - Doctor exits non-zero only on errors that prevent loading (invalid profile, unparseable config). Warnings (shadows, conflicts, scope mismatch) exit zero. A repo may wrap `doctor --strict` in CI to escalate warnings, but the workspace default stays advisory while metadata coverage grows.
