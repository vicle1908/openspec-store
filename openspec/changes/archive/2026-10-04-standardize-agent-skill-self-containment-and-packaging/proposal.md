# Proposal: Standardize Agent Skill Self-Containment, Modular Packaging, and Progressive Disclosure

## Why
While `workspace-openspec-skill-discovery` defines shared agent skill roots, discovery paths across multi-repository workspaces, and symlink synchronization mechanisms, it lacks normative requirements for:
1. **Skill Self-Containment**:
   - Skills frequently depend on ambient host tools, repository-specific Makefiles, or undocumented external shell scripts.
   - When an autonomous agent operates in an isolated repository (e.g. `shb-core` or clean Docker container), invoking such a skill fails because the prerequisite scripts or Makefiles are absent.
   - Standard: A modern agent skill must be self-contained, encapsulating its own portable CLI execution scripts under `scripts/`, reference documentation under `references/`, and configuration templates under `templates/`.
2. **Progressive Disclosure & Prompt Injection Economy**:
   - Agent runners inject skill descriptions directly into system prompts on every turn.
   - Verbose descriptions waste context window tokens and cause prompt truncation (in Hermes, descriptions over 60 characters are truncated; the active trigger must sit within the first 57 characters).
   - Skills without explicit negative counter-triggers ("When NOT to use") suffer from hallucinated or premature invocations.

## What Changes
- Add normative requirements to `workspace-openspec-skill-discovery/spec.md`:
  - `Shared Agent Skills SHALL be self-contained and modularly packaged`: Enforces bundling portable execution scripts (`scripts/`) and separating reference manuals (`references/`) directly within the skill directory.
  - `Shared Agent Skills SHALL conform to progressive disclosure and frontmatter standards`: Enforces strict YAML frontmatter, 57-character active triggers, total length $\le 60$ characters, explicit negative counter-triggers ("When NOT to use"), and native agent tool framing (`terminal`, `read_file`).
- Verify existing and newly created skills (including `github-actions-validation`) conform to these normative specifications.

## Impact
- **Specifications Affected**: `openspec/specs/workspace-openspec-skill-discovery/spec.md`.
- **Ecosystem Affected**: Shared agent skills in `~/Developer/.agents/skills/`.
- **Breaking Changes**: None. Zero runtime regressions; ensures all shared skills are portable across any workspace repository.
