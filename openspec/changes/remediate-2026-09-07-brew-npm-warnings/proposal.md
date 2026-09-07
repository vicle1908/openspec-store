## Why

Homebrew 6.x deprecated the `verified` parameter in cask `url` stanzas (now a no-op per `cask/url.rb:79`) and the `postflight` block DSL (replaced by `postflight_steps`). Running `brew update && brew upgrade` produces repeated deprecation warnings from four third-party cask files across three taps. Additionally, `brew audit --online` triggers a concurrent self-update + vendor bundle rebuild that can transiently break brew's Ruby startup (JSON gem double-load). These warnings are cosmetic today but will become hard errors in a future Homebrew release.

## What Changes

- **Upstream cask PRs**: Remove deprecated `verified:` parameter from four cask files across three third-party taps, and migrate `postflight do` → `postflight_steps do` in cockpit-tools.
- **Upstream issue tracking**: Reference existing gitnexus issue #2194 (tree-sitter 0.25 upgrade readiness) for the tree-sitter-zig peerOptional conflict.
- **Workspace documentation**: Add `brew audit --online` hazard note to workspace CLAUDE.md to prevent recurrence of the transient brew breakage.
- **No local tooling changes**: All fixes are upstream contributions or documentation; no custom scripts, overrides, or forks.

## Capabilities

### New Capabilities

None. This is a tooling/documentation change with no spec-level behavior changes. `skip_specs: true`.

### Modified Capabilities

None.

## Impact

- **Third-party taps affected**: `jlcodes99/homebrew-cockpit-tools` (Casks/cockpit-tools.rb), `stablyai/homebrew-orca` (Casks/orca.rb, Casks/orca@rc.rb), `anomalyco/homebrew-trap` (Casks/hex.rb)
- **Upstream repos**: jlcodes99/cockpit-tools, stablyai/homebrew-orca, abhigyanpatwari/GitNexus
- **Workspace files**: `~/Developer/CLAUDE.md` (hazard note)
- **No code changes in workspace repos**: All fixes are upstream PRs/issues or documentation
- **Risk**: Low — deprecation removals are safe (`verified:` is a no-op); `postflight_steps` migration is a documented DSL rename; brew hazard note is additive
