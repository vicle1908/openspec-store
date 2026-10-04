# Tasks: Standardize Agent Skill Self-Containment, Modular Packaging, and Progressive Disclosure

## 1. OpenSpec Change Specification & Delta Specs

- [x] 1.1 Author `proposal.md`, `design.md`, and `tasks.md` under `openspec/changes/standardize-agent-skill-self-containment-and-packaging/`
- [x] 1.2 Author delta specification in `specs/workspace-openspec-skill-discovery/spec.md`:
  - Add requirement: `Shared Agent Skills SHALL be self-contained and modularly packaged`
  - Add requirement: `Shared Agent Skills SHALL conform to progressive disclosure and frontmatter standards`
- [x] 1.3 Validate change strictly using `openspec validate standardize-agent-skill-self-containment-and-packaging --strict --store openspec-store`
- [x] 1.4 Commit OpenSpec change proposal to `openspec-store` `main`

## 2. Skill Refinement & Verification

- [x] 2.1 Verify `.agents/skills/github-actions-validation/` conforms to the new specification:
  - Validated frontmatter trigger $\le 57$ characters (`"Validate GitHub Actions workflows locally before pushing."`)
  - Validated self-contained execution script under `scripts/validate_workflows.py`
  - Validated failure taxonomy reference under `references/failure-taxonomy.md`
  - Validated `--json` machine-readable CLI interface
  - Validated tool framing via native Hermes tools (`terminal`, `read_file`)
- [x] 2.2 Verify workspace skill catalog discovery via `sync-workspace-agent-skills.py --check`

## 3. OpenSpec Archival & Specification Merge

- [x] 3.1 Mark all tasks completed in `tasks.md`
- [x] 3.2 Validate strict compliance with `openspec validate --strict`
- [x] 3.3 Archive change via `openspec archive standardize-agent-skill-self-containment-and-packaging --store openspec-store --yes`
- [x] 3.4 Confirm delta specifications are cleanly merged into `openspec/specs/workspace-openspec-skill-discovery/spec.md`
- [x] 3.5 Commit and push archived change to `openspec-store` `main`

## 4. Knowledge Persistence & Notion Synchronization

- [x] 4.1 Save durable learnings in `agentmemory`
- [x] 4.2 Update Notion architecture guide via `ntn` CLI
