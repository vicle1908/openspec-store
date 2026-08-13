# Proposal: optimize-openspec-workflow-governance

## Why

The shared OpenSpec workflow skill infrastructure has grown organically over many change cycles and now carries several operational risks that cannot be resolved by correcting individual examples. The root issues are structural: no automated regression detection, no cross-skill consistency contract, no standardized pre-archive gate, and a 70KB primary skill file that creates significant cumulative prompt cost and increases contradiction risk when combined with review skills and change artifacts.

The custom workflow skills live under `~/.hermes/skills/` and are managed by Hermes Agent. The OpenSpec store contains only specifications, active changes, and archives. This separation of concerns is correct and must not be changed.

A structured planning investigation reveals six evidence-backed optimization tracks that, taken together, would make the workflow governance system deterministic, auditable, and self-protecting against regression.

## What Changes

This change creates the planning infrastructure for six optimization tracks. It implements no changes to skills, scripts, or processes — it proposes them and provides evidence for their prioritization.

### Optimization Tracks (priority ordered)

**Track 1: Hermes-native ownership and provenance**
- **Problem:** Custom Hermes skills lack provenance tracking in their native `~/.hermes/skills/` location. No recorded mapping exists from each installed skill to its owning change, last-modified date, or intended state. Store-tracked `.hermes/skills/` files (generated OPSX adapters) are mixed with custom governance skills at the filesystem level.
- **Evidence:** `skill_manage(action='patch')` modifies local files without source attribution. The provenance inventory JSON previously proposed as durable artifact contains machine-local absolute paths and hashes that become stale on any Hermes update — it must not be committed as canonical.
- **Proposal:** Document the Hermes-native skill ownership model, add provenance markers (version, author, owning change) to installed skills, and ensure store-tracked `.hermes/skills/` are only generated adapters. Keep all custom skill management through `skill_manage` in `~/.hermes/skills/`.

**Track 2: Cross-skill contract consistency**
- **Problem:** Four independent skills (workflow, code-review, plan-review, review-governance) independently define overlapping lifecycle rules, state models, and archive gate conditions. Semantic drift between them is undetected.
- **Evidence:** Primary skill defines a 4-plane state model; review-governance defines its own lifecycle rules; plan-review has its own archive gate. These are not formally linked.
- **Proposal:** Build a cross-skill consistency matrix and a lightweight contract definition that all three skills reference.

**Track 3: Canonical pre-archive verifier**
- **Problem:** Pre-archive verification is performed ad-hoc each time, repeating the same validation commands with varying arguments. This is a recurring contributor to verification loops — agents re-run identical checks because the verification recipe is not standardized.
- **Evidence:** The `openspec-workflow` skill references `references/pre-archive-validation.md` with a bash loop, but the actual verification sequence varies per session.
- **Proposal:** A single read-only script (`scripts/openspec_change_gate.py`) that standardizes the pre-archive gate sequence, preserves child exit codes, and reports pass/fail per gate.

**Track 4: Documentation regression lint**
- **Problem:** Known unsafe patterns (masked exit codes, `git add -A` in shared stores, status-as-implementation conflation) reappear after correction because there is no automated detection.
- **Evidence:** The `openspec-progress-exit-status-correction` change (this session) fixed four instances of the same pattern. Without detection, they risk reappearing.
- **Proposal:** A grep-based lint check that detects known anti-patterns in workflow guidance files and fails if any are found.

**Track 5: Shared-store concurrent ownership**
- **Problem:** The shared store has unrelated dirty paths during change closures. Scope-only staging works but is manual and not enforced.
- **Evidence:** `git status` consistently shows unrelated untracked files during closure sequences. The workflow references scoped staging but never formalizes it as a gate.
- **Proposal:** A pre-archive ownership check that compares `git status` against owned paths and blocks closure if unrelated changes are staged.

**Track 6: Primary skill size reduction**
- **Problem:** The primary workflow skill is 70KB (approximately 17,500 tokens at 4 chars/token), approaching context-window limits for models with 128K context windows. Historical incident pitfall sections dominate the operational path.
- **Evidence:** `wc -c` reports 70,010 bytes for the primary SKILL.md. The secondary review-governance skill is 66KB. Together they exceed 136KB of workflow guidance.
- **Proposal:** Move historical incident pitfall sections to separate reference files and reduce the primary skill to under 30KB while preserving all operational guidance.

### Non-goals

- No modification to OpenSpec CLI or its installed behavior
- No immediate custom schema fork (schema commands remain experimental per official docs)
- No automatic archive mutation
- No migration of Hermes runtime configuration (covered by the existing `optimize-hermes-agent-configuration` change)
- No assumption that structural validation proves runtime behavior
- **No moving or copying custom skills into `openspec-store`** — `~/.hermes/skills/` is the canonical home for custom Hermes skills; the OpenSpec store records plans and evidence only
- No changing `skills.external_dirs` in Hermes config as part of this change
- No deleting repository-local `.hermes/skills/` files without resolution-precedence and parity verification

## Evidence

All findings are backed by concrete experiments and official documentation:

| Finding | Source | Evidence |
|---|---|---|
| Primary skill not version-controlled | Filesystem | `test -d ~/.hermes/skills/.git` → NO |
| Four custom skills, no overlapping relative paths | Provenance audit | Primary: 144 files (70KB + 759KB refs), Secondary: 17 files (11KB), 0 shared filenames |
| Generated OPSX skills are 12 lifecycle commands | `init --tools hermes,agents` | Creates `.hermes/skills/` and `.agents/skills/` with 12 SKILL.md files, `generatedBy: "1.8.0"` |
| `instructions archive` is read-only | Official docs + experiment | Returns `changeName`, `context`, `operationGuidance`, `root`; does not merge or move |
| Root precedence is 5-level | Official agent-contract.md | `--store` > nearest root > defaultStore > registered stores > scaffolding |
| `schema fork` creates project-local schema | Experiment | Forks `spec-driven` into `openspec/schemas/test-fork/` with 4 templates |
| `schema which --all --json` returns schema list | Experiment | 1 schema (`spec-driven`) from `package` source, no shadows |
| Existing optimization change is Hermes runtime | Task inventory | `optimize-hermes-agent-configuration` (22/59) covers approvals, memory, browser, delegation |
| `instructions archive` context is opaque text | Experiment | `context` is a string (2,642 chars), not structured JSON — not machine-parseable |
