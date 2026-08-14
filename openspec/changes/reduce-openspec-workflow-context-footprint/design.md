# Design: reduce-openspec-workflow-context-footprint

## Approach

Incremental relocation in small batches, each with its own validation gate.
After each batch: measure bytes/tokens, run lint, run gate, verify skill loading.

## Classification taxonomy

Every `**Pitfall**` block in the primary SKILL.md gets classified:

| Class | Definition | Destination |
|---|---|---|
| **Normative** | Defines a rule the agent must follow | Stays inline in SKILL.md |
| **Operational** | Practical guidance needed at decision time | Stays inline in SKILL.md |
| **Historical** | Documents a past incident or correction pattern | Relocates to `references/` with inline pointer |

## Relocation recipe

1. Read the block and its surrounding context.
2. Classify using the taxonomy above.
3. If historical: write a concise reference file under `references/`.
4. Replace the inline block with a one-line pointer: `See references/<name>.md`.
5. Validate: `openspec validate <name> --strict --store openspec-store`.
6. Measure: record bytes and estimated tokens before/after.

## Link repair

For each broken `references/...` link:
- Determine if the target was renamed, moved, or never created.
- Either create the missing file or update the reference path.
- Verify with a grep for orphaned references.

## Lint context-awareness

Add severity to lint findings:
- `actionable`: must fix before archive (masked exit status, unscoped staging).
- `informational`: historical example or warning against a pattern.
- `baseline`: pre-existing finding that is accepted.

Gate passes only when `actionable` count is 0.

## Regression tests

Not just Markdown scenarios — actual Python scripts that:
1. Call the lint with a file containing an anti-pattern → expect finding.
2. Call the lint with a file containing the negation/warning → expect no finding.
3. Run as part of the gate script.
