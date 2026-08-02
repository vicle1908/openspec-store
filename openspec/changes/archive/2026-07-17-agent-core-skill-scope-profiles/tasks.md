## 1. Settings and Profile Models

- [x] 1.1 Add `SkillProfileSettings` model with `directories`, `include`, `exclude`, and `scopes` fields.
- [x] 1.2 Replace `SkillsSettings.directories` with `skills.active_profile` and `skills.profiles`; remove the `directories` field entirely.
- [x] 1.3 Implement the built-in `default` profile (`[".agents/skills", "~/.tdt/skills"]`, scopes `[repo, workspace, global]`, no filters) used when `skills.profiles` is empty.
- [x] 1.4 Implement active-profile resolution, including env override via `SKILLS_ACTIVE_PROFILE`.
- [x] 1.5 Add validation that rejects a missing/unknown active profile name with `ConfigError`.
- [x] 1.6 Grep the codebase for `skills.directories` and `_resolve_skill_directories`; migrate every call site (`skills list`, `skills reload`, health checks, agent run helper) onto the profile resolver.
- [x] 1.7 Add tests for built-in default profile, explicit active profile, unknown profile error, env override, and relative directory resolution against workspace root.

## 2. Skill Metadata Parsing

- [x] 2.1 Extend skill frontmatter model with optional `scope`, `profiles`, `repositories`, `owners`, `conflicts_with`, and `replaces` fields.
- [x] 2.2 Validate known scope values while keeping unknown extra metadata ignored.
- [x] 2.3 Add tests for metadata parsing, missing metadata defaults, list fields, and unknown-field tolerance.

## 3. Profile Resolution and Filtering

- [x] 3.1 Add a profile resolver module (for example `agent_core/skill_system/profiles.py`) that scans configured directories using existing loader behavior and returns the active skill set.
- [x] 3.2 Apply profile filters in order: shadow resolution, include, exclude, then scopes.
- [x] 3.3 Preserve existing directory-order precedence for duplicate skill names.
- [x] 3.4 Make the resolver a pure function of `(profiles_config, profile_name, workspace_root)` with no global state, so it is callable per-agent.
- [x] 3.5 Add `skill_profile: str | None = None` to `BaseAgent.__init__`; resolve the agent's skill set via the resolver using that value or `settings.skills.active_profile`.
- [x] 3.6 Confirm profile/matcher orthogonality: profile filters the candidate set, then `SkillMatcher` ranks survivors. Add a test that an excluded skill never appears even if highly relevant.
- [x] 3.7 Add tests for include-only, exclude-only, include+exclude, scope filters, duplicate shadowing, excluded shadow winners, per-agent selection, and two-agents-one-process isolation.

## 4. Skill Diagnostics

- [x] 4.1 Add diagnostic models and helpers (for example `agent_core/skill_system/diagnostics.py`) for errors, warnings, and info messages with stable JSON shape.
- [x] 4.2 Implement diagnostics for missing directories, duplicate/shadowed skills, invalid profile references, missing metadata references, active conflicts, and repository scope mismatches.
- [x] 4.3 Add `agent-core skills doctor` CLI command with human-readable output.
- [x] 4.4 Add `--json` support for doctor output and deterministic ordering.
- [x] 4.5 Add `--profile` support for `skills list`, `skills reload`, and `skills doctor`.
- [x] 4.6 Add tests for CLI help output, doctor JSON output, exit codes, and unknown profile handling.

## 5. Scaffolding Updates

- [x] 5.1 Update `agent-core init` templates to include a minimal agent-core config file with `skills.active_profile` and a matching profile definition.
- [x] 5.2 Ensure generated projects include `.agents/skills/` before global fallback in their profile.
- [x] 5.3 Add a narrow reviewer-template profile stub without copying workspace skills.
- [x] 5.4 Add tests that generated projects contain the expected profile config and pass `skills doctor` without errors.

## 6. Documentation and Workspace Guidance

- [x] 6.1 Update `agent-core/docs/configuration.md` with profile schema, precedence, environment override, and examples.
- [x] 6.2 Update `agent-core/docs/extending.md` with global/workspace/repo/specialist placement rules.
- [x] 6.3 Update `agent-core/docs/building-agents.md` with specialist-agent profile examples.
- [x] 6.4 Update workspace docs under `tdt-meta/docs/` to clarify when skills belong in global, workspace, repo-local, or specialist profiles.
- [x] 6.5 Add or update a compact skill authoring checklist that avoids duplicating provider-specific skills.

## 7. Verification

- [x] 7.1 Run `uv run ruff check src tests` in `/Users/lekhanhvinh/Developer/tdt/agent-core`.
- [x] 7.2 Run `uv run ruff format --check src tests` in `/Users/lekhanhvinh/Developer/tdt/agent-core`.
- [x] 7.3 Run `uv run mypy src/agent_core/ tests/` in `/Users/lekhanhvinh/Developer/tdt/agent-core`.
- [x] 7.4 Run `uv run pytest tests/ -q` in `/Users/lekhanhvinh/Developer/tdt/agent-core`.
- [x] 7.5 Run `openspec validate agent-core-skill-scope-profiles --strict` in `/Users/lekhanhvinh/Developer/tdt/tdt-meta`.
- [x] 7.6 Review generated docs/spec/code for duplicated or outdated skill guidance before committing.
