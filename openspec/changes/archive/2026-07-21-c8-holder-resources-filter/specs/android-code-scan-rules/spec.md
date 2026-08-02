# android-code-scan-rules C8 Holder Resources Delta

## ADDED Requirements

### Requirement: C8 rule SHALL suppress holder.itemView.resources findings

The C8 post-filter SHALL suppress `resources` findings where the access is through a ViewHolder's itemView (`holder.itemView.resources` or `itemView.resources`). This path is safe because the ViewHolder's itemView is always attached when `onBindViewHolder` is called.

#### Scenario: holder.itemView.resources is suppressed

- **WHEN** a C8 finding targets `holder.itemView.resources.getDimensionPixelSize(...)` in an adapter's `onBindViewHolder`
- **THEN** the post-filter SHALL suppress the finding

#### Scenario: requireContext() in Fragment is NOT suppressed

- **WHEN** a C8 finding targets `requireContext()` inside a Fragment method
- **THEN** the post-filter SHALL NOT suppress the finding (handled by lifecycle filter)
