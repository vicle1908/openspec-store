# Design: optimize-openspec-workflow-governance

## Current state (three-layer architecture)

The OpenSpec workflow governance system operates across three distinct layers with different owners, mutation methods, and version-control status:

| Layer | Location | Owner/Mutation | Version-controlled | Role |
|---|---|---|---|---|
| **Generated lifecycle** | `openspec-store/.hermes/skills/`, `Developer/.agents/skills/` | OpenSpec CLI `init --tools`, `update` | No (regenerated) | 12 OPSX slash commands (propose, apply, verify, archive, etc.) |
| **Custom workflow** | `~/.hermes/skills/software-development/openspec-workflow/` | `skill_manage` | No | Single SKILL.md (70KB) + 143 reference files (759KB) |
| **Custom review** | `~/.hermes/skills/openspec-workflow/` | `skill_manage` | No | 3 sub-skills: review-governance (66KB), plan-review (12KB), code-review (13KB) |

### Key findings from official v1.8.0 docs

- Root precedence: `--store` > nearest root > `defaultStore` > registered stores > scaffolding
- `instructions archive` is **read-only**: returns `{changeName, context, operationGuidance, root}`. It does not merge specs, move changes, or prove task completion.
- `schema fork` is experimental: creates project-local schemas in `openspec/schemas/`. One schema exists: `spec-driven` from the package source.
- `schema which --all --json` returns the schema resolution chain. Useful for auditing which schema a change inherits.
- Stores, references, working context, and worksets are beta — command names, flags, and JSON output may change between releases.
- `init --tools hermes,agents` generates 12 OPSX lifecycle skills in both `.hermes/skills/` and `.agents/skills/`, all with `generatedBy: "1.8.0"` and `author: "openspec"`.

### Existing overlap with other changes

- `optimize-hermes-agent-configuration` (22/59): Hermes runtime config (approvals, memory, browser, delegation). No overlap with OpenSpec workflow governance.
- `scheduler-stale-workflow-hardening` (15/21): DBOS scheduler self-healing. Unrelated.

## Proposed architecture

### Track 1: Skill ownership and provenance markers

Add frontmatter `version`, `author`, and `source` metadata to all four custom skills. Create a provenance manifest (JSON) that records:
- Which skill file corresponds to which logical layer
- The SHA-256 hash of the canonical version
- The last-modified date and the change that last touched it
- Whether the skill is generated, custom, or a hybrid

The canonical source MUST be version-controlled. The manifest creates a machine-readable inventory for session-start verification and parity checks, but version control is the primary durability mechanism.

### Track 2: Cross-skill consistency matrix

A lightweight document (not a custom schema) that maps:
- State model definitions across all four skills
- Archive gate conditions
- Validation commands referenced
- Review dispatch rules
- Closure-task sequencing rules

Any inconsistency between the four skills becomes a concrete task.

### Track 3: Canonical pre-archive verifier script

A single Python script (`scripts/openspec_change_gate.py`) that:
1. Accepts `--change <name> --store <store-id> --mode [pre-archive|post-archive]`
2. Runs focused validation, full validation, doctor, git diff check, progress check
3. Parses the output and reports structured JSON with pass/fail per gate
4. Preserves child process exit codes
5. Reports `root.store_id` from the JSON output
6. Does NOT invoke archive — it is read-only preparation

This replaces the ad-hoc bash loops in `pre-archive-validation.md` and `implementation-pitfalls.md`.

### Track 4: Documentation regression lint

A grep-based check that detects known anti-patterns in all workflow guidance files:
- `| python3` without temp-file status preservation
- `git add -A` in shared-store closure examples
- `status.isComplete` used as implementation completion
- `archive --json` described as preview/readiness
- Unrestricted reviewer permissions in read-only review guidance
- Missing `--store openspec-store` in validation commands

Runs as a one-shot check; does not modify files.

### Track 5: Shared-store concurrent ownership gate

Formalize the existing ad-hoc practice:
1. Freeze `HEAD`, branch, dirty-file inventory before closure
2. Declare owned paths for the current change
3. Detect concurrent changes via `git status`
4. Stage only owned paths
5. Block closure if baseline shifted or unrelated paths are staged

This is already partially implemented in the workflow guidance but never formalized as a script or gate.

### Track 6: Primary skill size reduction

The primary workflow SKILL.md is 70KB. The historical incident pitfall sections dominate the operational path. Move them to separate reference files:
- Pitfall sections that describe specific past incidents → `references/incident-cases.md`
- Pitfall sections that describe general anti-patterns → keep in SKILL.md (they are operational)
- Reduce SKILL.md size (targeting ~30KB as initial hypothesis, not acceptance criterion) while preserving all operational guidance and verifying no rule is lost

The review-governance skill (66KB) is a separate concern addressed in Track 2 (consistency matrix).

## Non-goals

- No modification to OpenSpec CLI or installed behavior
- No immediate custom schema fork (schema commands remain experimental per official docs)
- No automatic archive mutation
- No assumption that structural validation proves runtime behavior
- No migration of Hermes runtime configuration
- No physical merge needed (provenance audit confirmed zero shared filenames between primary and secondary custom trees; they contain different logical skills, not duplicates)
