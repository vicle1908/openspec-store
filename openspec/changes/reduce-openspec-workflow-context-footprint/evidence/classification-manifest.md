# Classification Manifest

| Class | Count | Bytes | Action |
|---|---|---|---|
| Normative | 20 | 40,568 | Stay inline |
| Operational | 6 | 5,924 | Stay inline |
| Historical | 4 | 6,779 | Relocate to references/ |
| **Total** | **30** | **53,271** | |

## Normative Blocks

| # | Lines | Bytes | Title |
|---|---|---|---|
| 1 | L129-L229 | 5,794 | **Pitfall (archived overlap name):** A prior change may be referenced in prose but have al |
| 2 | L230-L233 | 1,408 | **Pitfall (store-connected repos + `openspec init --tools`):** Repos that use an external  |
| 3 | L234-L239 | 1,528 | **Pitfall:** When writing multiple files to a change directory via `write_file`, the `.ope |
| 4 | L240-L243 | 590 | **Pitfall:** For tooling/config-only changes (new skills, CLI setup, agent wiring), use `s |
| 5 | L244-L247 | 1,000 | **Pitfall:** Change proposals may contain fabricated or outdated factual claims (version n |
| 6 | L248-L251 | 855 | **Pitfall:** When implementing changes that update tool versions or APIs, ALWAYS update te |
| 7 | L252-L255 | 1,217 | **Pitfall:** Tool upgrades can silently change output directory layouts. After upgrading a |
| 11 | L277-L280 | 1,148 | **Pitfall:** Archive fails when MODIFIED delta spec headers don't exactly match existing s |
| 14 | L289-L292 | 1,367 | **Pitfall:** When deleting source packages (e.g. `llm_gateway/`, `resilience/`), always ch |
| 16 | L297-L300 | 782 | **Pitfall:** Knowledge tools can return stale data — always verify freshness before using  |
| 17 | L301-L304 | 1,009 | **Pitfall:** After large code changes (API migrations, package deletions), sweep ALL of: ` |
| 18 | L305-L308 | 991 | **Pitfall (model_names vs prefix ambiguity):** When adding provider configs with `model_na |
| 19 | L309-L425 | 13,951 | **Pitfall:** GitNexus MCP tools have specific parameter schemas that differ from CLI flags |
| 20 | L426-L429 | 1,758 | **Pitfall (MoA variant proposals and role switches):** Before creating/applying a MoA chan |
| 21 | L430-L433 | 2,018 | **Pitfall:** `hermes config set moa.presets.<name> '{...}'` stores the value as a JSON str |
| 22 | L434-L443 | 1,096 | **Pitfall:** `hermes moa delete` refuses to delete the only preset ("Cannot delete the onl |
| 23 | L444-L447 | 1,072 | **Pitfall (OpenSpec worktree vs store path confusion):** When creating changes with `opens |
| 24 | L448-L452 | 1,070 | **Pitfall (phase boundaries — explore/propose/execute):** Distinguish explore, propose, an |
| 25 | L453-L456 | 1,128 | **Pitfall (disposable profiles for model-selection tests):** When testing explicit `--mode |
| 27 | L461-L464 | 786 | **Pitfall (overlap ownership):** Before modifying a file or port, search active OpenSpec c |

## Operational Blocks

| # | Lines | Bytes | Title |
|---|---|---|---|
| 12 | L281-L284 | 1,433 | **Pitfall — delegate_task reviews crash with vars() serialization bug (USE CLI AGENTS INST |
| 13 | L285-L288 | 722 | **Pitfall:** ALWAYS pass inline content in the `context` parameter to delegate_task, NEVER |
| 26 | L457-L460 | 844 | **Pitfall (per-file atomic rollback, not pair-atomic):** For two-file changes (e.g. `model |
| 28 | L465-L468 | 1,054 | **Pitfall (role-selector validation completeness):** Validate every unique selector throug |
| 29 | L469-L472 | 1,091 | **Pitfall (installation inventory before omp changes):** When an omp task involves the bin |
| 30 | L473-L474 | 780 | **Pitfall (delta spec scenario preservation — verbatim baseline):** When writing `## MODIF |

## Historical Blocks

| # | Lines | Bytes | Title |
|---|---|---|---|
| 8 | L256-L269 | 2,368 | **Pitfall:** Retrospective changes (work already done, spec after) still require the full  |
| 9 | L270-L273 | 1,047 | **Pitfall (user correction — verification order):** When creating changes for new tool int |
| 10 | L274-L276 | 2,044 | **Pitfall (retrospective desktop-agent live-integration closure):** When documenting a fix |
| 15 | L293-L296 | 1,320 | **Pitfall (context compaction loops):** After context compaction, the agent may lose track |

## Baseline

- Total SKILL.md: 73,669 bytes / 493 lines / ~18,417 tokens
- Pitfall blocks: 30 (53,271 bytes)
- Relocatable: 4 (6,779 bytes)
- Expected post-relocation: ~66,890 bytes / ~16,722 tokens
