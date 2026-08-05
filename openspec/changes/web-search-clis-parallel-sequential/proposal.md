# Proposal: Add Parallel vs Sequential Search Strategy

## Why

The web-search-clis skill documents 6 tools and their commands but lacks guidance on **when to run searches in parallel vs sequentially**. This is the most common operational mistake — running sequential searches when parallel would be faster, or running parallel when one search depends on another's results.

Without this guidance, research workflows are suboptimal: wasted round-trips on sequential calls that could be batched, or broken workflows when parallel calls depend on unresolved state.

## What Changes

1. **SKILL.md** — Add a new `## Search Strategy` section between Decision Matrix and Command Reference covering:
   - Parallel search patterns (independent queries, triangulation, multi-tool)
   - Sequential search patterns (dependent queries, refine-extract, two-step workflows)
   - Hybrid patterns (parallel discovery → sequential deep dive)
   - Rate limit awareness for parallel execution
   - `execute_code` for programmatic batching
   - `delegate_task` for multi-subagent parallel research
   - Concrete workflow examples

2. **Decision Matrix** — Add strategy guidance row
3. **Pitfalls** — Add parallel/sequential anti-patterns

## Non-Goals

- Modifying tool internals or CLI behavior
- Creating scripts (the skill documents patterns, not executables)
- Changing other research skills

## Affected Ownership

- Skill file: `~/.hermes/skills/research/web-search-clis/SKILL.md`
