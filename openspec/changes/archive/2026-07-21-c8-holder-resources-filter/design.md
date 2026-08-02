# Design: C8 holder.itemView.resources Post-Filter

## Context

The C8 rule catches `resources.` access after Fragment detach. But `holder.itemView.resources` is safe — the ViewHolder's itemView is always attached when `onBindViewHolder` is called. The current C8 post-filter (`suppress_c8_lifecycle_safe`) only checks for lifecycle methods within 30 lines, which doesn't catch this pattern because the ViewHolder binding happens inside the adapter, not in a Fragment lifecycle method.

## Decision

### D-1. Add holder.itemView.resources suppression

The new post-filter `suppress_c8_holder_view_resources` SHALL suppress C8 findings where the snippet contains `holder.itemView.resources` or `itemView.resources` — indicating the resources access is through a ViewHolder's itemView, which is always attached.

**Logic:**
1. Check if finding is C8 rule
2. Check if snippet contains `itemView.resources` or `holder.itemView.resources`
3. If yes, suppress the finding (safe path)

This is a targeted, low-risk filter that only affects the specific safe pattern.

## Risks

- **Low risk**: The filter only affects `itemView.resources` pattern, which is inherently safe
- **No rule changes**: The C8 rule itself remains correct — this is a post-filter for a known safe pattern
