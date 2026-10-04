# Exploration Report: Agent Skill Self-Containment, Progressive Disclosure, and Specification Standardization

**Date:** 2026-10-04  
**Workspace Root:** `~/Developer`  
**OpenSpec Store:** `~/Developer/platform/openspec-store`  
**Target Specification:** `openspec/specs/workspace-openspec-skill-discovery/spec.md`  

---

## 1. Executive Summary & Problem Space

As autonomous coding agents (Hermes, Claude Code, OpenAI Codex, Pi, Goose) increasingly drive software development across the multi-repository workspace, **Agent Skills** have emerged as the primary procedural memory and operational interface layer.

However, an audit of the current workspace skills ecosystem and the authoritative specification `workspace-openspec-skill-discovery` revealed two significant structural shortcomings:

1. **Ambient Dependency Leakage & Incomplete Self-Containment**:
   - Many historical skills rely on implicit ambient tools installed in particular user shells, repository-specific Makefiles, or machine-specific directory structures.
   - When an agent is operating in an isolated repository (e.g. `shb-core`, `agent-core`, or a clean Docker runner), invoking such a skill fails because the prerequisite scripts or Makefiles are absent.
   - Standard: A modern agent skill must be **self-contained**: bundling its own portable execution scripts (`scripts/`), operational references (`references/`), and configuration templates (`templates/`) directly within the skill directory.
2. **Context Window Inefficiencies & Unbounded Frontmatter Descriptions**:
   - Modern agent runners (Hermes, Claude Code, Codex) inject skill descriptions directly into system prompts or catalog summaries on every turn.
   - Verbose, narrative, or marketing-heavy descriptions consume critical context window tokens and cause description truncation.
   - In Hermes, descriptions over 60 characters are truncated in compact listings; the active trigger must sit within the first 57 characters.
   - Furthermore, skills lacking explicit negative counter-triggers ("When NOT to use") suffer from hallucinated or premature invocations.

To address these shortcomings, this exploration formalizes the **Self-Containment and Progressive Disclosure Standards** for shared agent skills and proposes updating `workspace-openspec-skill-discovery` in `openspec-store`.

---

## 2. Benchmark Evaluation: Newly Created `github-actions-validation` Skill

We benchmarked the newly created `github-actions-validation` skill against modern agent skill standards:

### Layout
```text
.agents/skills/github-actions-validation/
├── SKILL.md                          # Standardized skill guide (4,642 bytes)
├── scripts/
│   └── validate_workflows.py         # Portable standalone Python CLI validator (15,246 bytes)
└── references/
    └── failure-taxonomy.md           # Failure modes & mitigation reference (6,013 bytes)
```

### Evaluation Results

| Standard Dimension | Requirement | Implementation in `github-actions-validation` | Score |
|---|---|---|---|
| **Frontmatter Trigger** | Trigger within first 57 characters, total $\le 60$ chars | `"Validate GitHub Actions workflows locally before pushing."` (57 chars) | **10/10** |
| **Self-Containment** | Bundled scripts & docs; zero external script dependencies | Bundles standalone `scripts/validate_workflows.py` and `references/failure-taxonomy.md` | **10/10** |
| **Tool Framing** | Frame execution via native agent tools (`terminal`, `read_file`) | Documented using `terminal(command="python3 <skill>/scripts/validate_workflows.py ...")` | **10/10** |
| **Machine-Readable I/O** | Exposes `--json` interface for programmatic parsing | CLI outputs structured JSON with `success`, `workflows_count`, `passed_checks`, and `violations` | **10/10** |
| **Progressive Disclosure** | Quick Start $	o$ When to Use $	o$ Procedure $	o$ Pitfalls $	o$ Verification | Structured into concise operational sections with deep references separated into subfiles | **10/10** |
| **Catalog Discoverability** | Walkable `SKILL.md`, zero `.claude-plugin` subdirs | Verified via `sync-workspace-agent-skills.py --check`: 96 roots, 0 malformed, 0 broken | **10/10** |

---

## 3. Specification Gaps in `workspace-openspec-skill-discovery`

The governing specification `openspec/specs/workspace-openspec-skill-discovery/spec.md` currently covers:
1. `Shared Agent Skills SHALL be discoverable across independent repositories`
2. `Product-native skill surfaces MUST preserve distinct capabilities without shared-content drift`
3. `Skill provenance and discovery SHALL be independently verifiable`
4. `Skill placement SHALL follow a global-versus-workspace ownership rule`

It **does not define normative requirements** for:
- **Modular Self-Containment**: Mandatory bundling of portable scripts and references inside the skill root.
- **Frontmatter Budget & Trigger Density**: Strict length bounds and prompt injection economy.
- **Machine-Readable Interfaces**: Requirement for bundled tools to expose structured output (e.g. `--json`) alongside human-readable text.

---

## 4. Proposed OpenSpec Change

We propose opening an OpenSpec change with delta specifications:
- **Change Name:** `standardize-agent-skill-self-containment-and-packaging`
- **Target Spec:** `workspace-openspec-skill-discovery`
- **Added Requirements:**
  1. `### Requirement: Shared Agent Skills SHALL be self-contained and modularly packaged`
     - Bundling portable execution scripts under `scripts/`.
     - Bundling reference documentation and taxonomies under `references/`.
     - Providing machine-readable `--json` interfaces for agent orchestration.
  2. `### Requirement: Shared Agent Skills SHALL conform to progressive disclosure and frontmatter standards`
     - Self-contained trigger in the first 57 characters of `description`.
     - Explicit negative counter-triggers ("When NOT to use").
     - Framing execution via native agent tools (`terminal`, `read_file`).
