## Context

Four third-party Homebrew cask files use deprecated DSL (`verified:` parameter, `postflight` block). Homebrew 6.x treats `verified:` as a no-op (url.rb:79) and prints deprecation warnings on every `brew update`/`brew upgrade` invocation. The `postflight` block is replaced by `postflight_steps` with a declarative step DSL (`run` verb for system commands). Additionally, `brew audit --online` triggers a concurrent self-update + vendor bundle rebuild that can transiently break brew's Ruby startup via JSON gem double-loading.

## Goals / Non-Goals

**Goals:**
- Document `brew audit --online` hazard in workspace CLAUDE.md
- Document deprecation warning limitations (cosmetic now, hard errors later)
- Document npm dependency warnings as known upstream issues

**Non-Goals:**
- File upstream PRs or issues (follow official upgrade paths)
- Fork or maintain custom cask taps
- Create custom brew/npm maintenance scripts
- Fix npm transitive deprecated packages (boolean, node-domexception)
- Modify workspace dependency trees or override peer dependencies

## Decisions

### 1. Follow official upgrade paths, not upstream contributions

**Rationale:** The workspace doesn't own these taps or packages. Local edits to tap files are clobbered by `brew update`. Filing upstream PRs requires maintainer review cycles and is outside our control. The correct approach: run `brew upgrade` and `npm update -g` to get the latest versions, and document limitations where upstream hasn't resolved issues yet.

### 2. Document limitations, not workarounds

**Rationale:** Creating custom scripts, overrides, or forks to suppress warnings introduces maintenance burden and divergence from official channels. Better to document the known state and let upstream resolve on their timeline.

### 3. Hazard note for `brew audit --online`

**Rationale:** The transient brew breakage (JSON gem double-load) is a real risk that can recur. Documenting it in CLAUDE.md prevents future incidents. The note should explain the mechanism (concurrent self-update + vendor bundle rebuild) and the recovery (wait for self-heal or run `brew update-reset`).

## Limitations

| Warning | Source | Will Resolve When |
|---------|--------|-------------------|
| `verified:` deprecated (4 casks) | Third-party taps | Tap maintainers remove `verified:` from cask files |
| `postflight` deprecated (cockpit-tools) | Third-party tap | Maintainer migrates to `postflight_steps` |
| tree-sitter-zig peerOptional | gitnexus@1.6.11 | gitnexus bumps tree-sitter to ^0.22.1 or drops zig grammar |
| boolean@3.2.0 deprecated | gitnexus → onnxruntime → global-agent | upstream drops global-agent dependency |
| node-domexception@1.0.0 deprecated | cline → google-auth → node-fetch → fetch-blob | upstream drops node-fetch 3.x or fetch-blob drops domexception |

## Migration Plan

1. Add hazard note + limitations to ~/Developer/CLAUDE.md
2. Verify: `brew update && brew upgrade` completes without new warnings
3. Verify: `npm update -g` completes without new peer dep conflicts
