# Proposal: reduce-openspec-workflow-context-footprint

## Why

The primary `openspec-workflow` SKILL.md is 73,669 bytes (~18,417 tokens). When combined with review skills and change artifacts, cumulative context cost approaches ~30K tokens per invocation. The file contains 57 `**Pitfall**` blocks, 21 subsections under `## Workflow`, 9 broken internal reference links, and 42 lint findings — all in reference files. The `optimize-openspec-workflow-governance` change measured the baseline and removed exact duplicates but deferred the full historical-content relocation.

## What Changes

This follow-up change reduces the primary SKILL.md context footprint by:

1. **Classifying all 57 pitfall blocks** as normative (must stay inline), operational (should stay for discoverability), or historical (can move to references).
2. **Relocating historical incidents** into Hermes-native reference files under `~/.hermes/skills/software-development/openspec-workflow/references/`, keeping concise normative pointers in SKILL.md.
3. **Repairing 9 broken internal reference links** that point to non-existent files.
4. **Making documentation lint context-aware** — distinguishing actionable findings from historical examples/warnings, introducing severity classification and an approved baseline.
5. **Adding executable regression tests** — not only descriptive Markdown fixtures, but actual test scripts that verify the lint catches real anti-patterns.
6. **Measuring before/after** byte and token counts consistently after each relocation batch.

## Non-Goals

- Rewriting operational guidance or normative rules.
- Changing the skill's public interface or loading behavior.
- Modifying other skills (openspec-review-governance, openspec-code-review, openspec-plan-review).
- Archiving this change before all relocation tasks are genuinely complete.
