# Proposal: C8 holder.itemView.resources Post-Filter

## Why

MR !23873 analysis revealed 3 false positive C8 findings where `holder.itemView.resources` is flagged as a detached-fragment risk. The C8 rule catches `resources.` access after detach, but `holder.itemView.resources` is safe — the ViewHolder's itemView is always attached when `onBindViewHolder` is called.

Current C8 findings with this pattern:
- `DialogOption.kt:149` — `itemView.resources,`
- `DialogSwitchAccount.kt:97` — `itemView.resources,`
- `DialogSwitchTransferAccount.kt:110` — `itemView.resources,`

These are all adapter ViewHolder bindings — safe by design.

## What Changes

Add `suppress_c8_holder_view_resources` post-filter that suppresses C8 findings where `resources` access is through `holder.itemView` or `itemView` — a safe path that's always attached when the adapter is binding.

## Capabilities

### Modified Capabilities

- `android-code-scan-rules`: C8 post-filter for holder.itemView.resources

## Impact

- `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py`: Add `suppress_c8_holder_view_resources`
- No rule file changes needed
- No external dependencies

## Non-Goals

- Modifying C7/C8 rules (they're correct — code should be fixed)
- Adding new rules
- Changing iOS rules
