## Why

Homebrew 6.x deprecated the `verified` parameter in cask `url` stanzas (now a no-op per `cask/url.rb:79`) and the `postflight` block DSL (replaced by `postflight_steps`). Running `brew update && brew upgrade` produces repeated deprecation warnings from four third-party cask files across three taps. Additionally, `brew audit --online` triggers a concurrent self-update + vendor bundle rebuild that can transiently break brew's Ruby startup (JSON gem double-load). These warnings are cosmetic today but will become hard errors in a future Homebrew release.

## What Changes

- **Workspace documentation**: Add `brew audit --online` hazard note and deprecation warning limitations to workspace CLAUDE.md.
- **No upstream contributions**: All fixes depend on third-party tap maintainers and upstream package authors. We follow official upgrade paths (`brew upgrade`, `npm update -g`) and document limitations where upstream has not yet resolved issues.
- **No local tooling changes**: No custom scripts, overrides, or forks.

## Capabilities

### New Capabilities

None. This is a tooling/documentation change with no spec-level behavior changes. `skip_specs: true`.

### Modified Capabilities

None.

## Impact

- **Third-party taps affected**: `jlcodes99/homebrew-cockpit-tools` (Casks/cockpit-tools.rb), `stablyai/homebrew-orca` (Casks/orca.rb, Casks/orca@rc.rb), `anomalyco/homebrew-tap` (Casks/hex.rb)
- **Upstream repos**: jlcodes99/cockpit-tools, stablyai/homebrew-orca, abhigyanpatwari/GitNexus
- **Workspace files**: `~/Developer/CLAUDE.md` (hazard note + limitations)
- **No code changes in workspace repos**: Documentation only
- **Risk**: None — documentation is additive; no behavior changes
