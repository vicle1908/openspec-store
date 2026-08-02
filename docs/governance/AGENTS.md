# OpenSpec Guidelines

## Workflow

This repository uses the `spec-driven` OpenSpec schema. When creating,
continuing, applying, updating, verifying, syncing, or archiving a change, use
the corresponding OpenSpec workflow or skill when available. Otherwise use the
OpenSpec CLI to discover the active change, status, instructions, and concrete
context files. Do not guess artifact paths or assume the current list of active
changes.

Read every context file returned by the CLI before implementation. Keep
proposal, design, delta specs, and tasks coherent. Mark a task complete only
after its implementation and focused verification succeed. Do not edit
archived changes unless the request explicitly targets historical correction.

## Specification Rules

Follow `openspec/config.yaml` (relative to store root, at `../../openspec/config.yaml` from this file):

- Use one canonical Capabilities section with exact kebab-case IDs.
- State goals, non-goals, affected ownership boundaries, contracts,
  compatibility, rollout, and rollback.
- Use `SHALL` or `MUST` for every normative requirement.
- Give every requirement at least one testable `#### Scenario:` section.
- Cover success, failure, retry, idempotency, and observability when relevant.
- Define transaction boundaries, delivery guarantees, ordering, event
  versioning, security, configuration, migration, and recovery where affected.
- Verify dependency versions and platform compatibility against current
  official documentation rather than relying on remembered versions.
- Confirm every selected local image supports `linux/arm64` or document the
  approved fallback and trade-off.

Keep specifications externally observable. Prescribe internal implementation
only when it is itself a required contract.

`skip_specs: true` is permitted only for a change with no spec-level behavior
impact. Changes to agent behavior, instruction governance, generated workflow
contracts, CI enforcement, or externally relied-on tooling require capability
deltas. A new-capability delta must include a meaningful `## Purpose` section
that satisfies strict validation and can become the archived main-spec purpose.

## Generated OpenSpec Surfaces

OpenSpec skills, commands, prompts, and workflows are generator-owned. Never
hand-edit a file declaring `generatedBy`; update the repository policy or
project guidance and run the reviewed `make openspec-surfaces-refresh` flow.
The exact version, profile, workflows, tools, paths, and invocation contracts
live in `scripts/config/agent-skill-surfaces.json`. Codex uses
`$openspec-*`, Claude uses `/opsx:*`, filename-based tools use `/opsx-*`, and
Kimi Code uses `/skill:openspec-*`. The repository-owned `.agents/skills`
copies are synchronized only after all generator-managed tools validate.

Archive and bulk-archive work must load current runtime inputs, complete an
approved spec sync inline, validate the resulting main specs, and only then
move the change. Never delegate sync into a background task that can remain in
flight while archival proceeds.

## Validation

Validate the affected change during authoring, then run the repository gate
before handoff:

```bash
openspec validate --strict --all
```

Do not claim an OpenSpec change is complete when artifacts are missing,
requirements lack scenarios, implementation tasks remain open, or verification
has not succeeded.

## Store Git Tracking

This store is a git repository. All specs, archived changes, active changes,
and reports are committed. Per official openspec.dev/docs/stores:

> "A store is just a git repo. You commit, push, pull, and review it yourself."

### Post-Archive Workflow

After archiving a change, commit the store:

```bash
cd ~/Developer/openspec-store
git add openspec/
git commit -m "archive: <change-name> — merged delta specs into main specs"
```

### Post-Sync Workflow

After syncing from external sources (GDrive, team repos), commit the store:

```bash
cd ~/Developer/openspec-store
git add openspec/
git commit -m "sync: pulled specs/archives from <source>"
```

### Health Check

```bash
openspec store doctor openspec-store    # verify store health
git status                               # check for uncommitted work
openspec validate --all --store openspec-store  # validate all specs
```
