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

### Track 1: Hermes-native ownership and provenance

The custom Hermes skills live in `~/.hermes/skills/` and are managed by Hermes Agent (`skill_manage`, `openspec init --tools`, `openspec update`). The OpenSpec store does not own these skills and must not become their canonical source.

| Surface | Purpose | Owner |
|---|---|---|
| `openspec-store/openspec/` | Specifications, changes, archives, change evidence | OpenSpec store |
| `~/.hermes/skills/` | Installed custom workflow and review skills | Hermes Agent |
| `openspec-store/.hermes/skills/` | Project-local adapters generated or loaded for that workspace | OpenSpec/Hermes integration |

Implementation actions:
1. Classify each tracked entry in `openspec-store/.hermes/skills/` as: generated OPSX adapter, intentional workspace integration, stale custom-skill copy, or unknown.
2. Do not delete or move repository-local `.hermes/skills/` files without resolution-precedence and parity verification — Hermes may currently load that directory via `skills.external_dirs`.
3. Add provenance markers (version, author, owning change) to installed custom skills in `~/.hermes/skills/`.
4. Any repository-local `.hermes/skills/` cleanup is a separate authorized migration with rollback.

### Track 2: Cross-skill contract consistency

Four independent custom skills (workflow, code-review, plan-review, review-governance) define overlapping lifecycle rules. The consistency matrix will be a planning artifact in the OpenSpec change; it will not become a new Hermes skill or be installed into the store's `.hermes/skills/` tree.

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

The primary workflow SKILL.md is 70KB. The historical incident pitfall sections dominate the operational path. Move them to separate reference files under the same Hermes-native skill directory:
- Pitfall sections that describe specific past incidents → `~/.hermes/skills/software-development/openspec-workflow/references/incident-cases.md`
- Pitfall sections that describe general anti-patterns → keep in the Hermes skill (they are operational)
- Reduce SKILL.md size (targeting ~30KB as initial hypothesis, not acceptance criterion) while preserving all operational guidance and verifying no rule is lost

This change does not move the skill directory into `openspec-store`.

## Non-goals

- No modification to OpenSpec CLI or installed behavior
- No immediate custom schema fork (schema commands remain experimental per official docs)
- No automatic archive mutation
- No assumption that structural validation proves runtime behavior
- No migration of Hermes runtime configuration
- No physical merge needed (provenance audit confirmed zero shared filenames between primary and secondary custom trees; they contain different logical skills, not duplicates)
