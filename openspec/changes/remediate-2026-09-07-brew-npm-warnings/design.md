## Context

Four third-party Homebrew cask files use deprecated DSL (`verified:` parameter, `postflight` block). Homebrew 6.x treats `verified:` as a no-op (url.rb:79) and prints deprecation warnings on every `brew update`/`brew upgrade` invocation. The `postflight` block is replaced by `postflight_steps` with a declarative step DSL (`run` verb for system commands). Additionally, `brew audit --online` triggers a concurrent self-update + vendor bundle rebuild that can transiently break brew's Ruby startup via JSON gem double-loading.

## Goals / Non-Goals

**Goals:**
- Remove deprecated `verified:` from four cask files (safe — it's a no-op)
- Migrate `postflight do` → `postflight_steps do` with `run` verb in cockpit-tools
- Document `brew audit --online` hazard in workspace CLAUDE.md
- Reference existing gitnexus issue #2194 for tree-sitter-zig peer dep

**Non-Goals:**
- Fork or maintain custom cask taps (all fixes go upstream)
- Create custom brew maintenance scripts
- Fix npm transitive deprecated packages (boolean, node-domexception) — these are upstream
- Modify workspace dependency trees or override peer dependencies

## Decisions

### 1. Remove `verified:` from all four casks (including hex with R2 URL)

**Rationale:** `verified:` is a no-op in Homebrew 6.x (url.rb:79: "accepted as a no-op for compatibility"). Removing it is safe regardless of URL domain. Homebrew's default verification now handles all URL types.

**Alternative considered:** Keep `verified:` for hex (R2 URL doesn't match homepage). Rejected — it's a no-op; keeping it just delays the inevitable deprecation removal and continues producing warnings.

### 2. Migrate cockpit-tools `postflight` → `postflight_steps` with `run` verb

**Rationale:** Homebrew 6.x deprecated `postflight` in favor of `postflight_steps` (dsl.rb:856: generic `#{dsl_key}` → `#{dsl_key}_steps` rename). The new DSL uses `Homebrew::InstallSteps::DSL` with a `run` verb for system commands (install_steps.rb:710).

**Migration:**
```ruby
# Before (deprecated)
postflight do
  system_command "/usr/bin/xattr",
                 args: ["-cr", "#{appdir}/Cockpit Tools.app"],
                 sudo: true
end

# After (current)
postflight_steps do
  run "/usr/bin/xattr",
      args: ["-cr", "#{appdir}/Cockpit Tools.app"],
      sudo: true
end
```

**Alternative considered:** Remove the postflight entirely (Homebrew strips quarantine by default). Rejected — the maintainer added it for a specific reason (their caveats mention Gatekeeper issues); removing it changes behavior.

### 3. File upstream issues/PRs, not local workarounds

**Rationale:** The workspace doesn't own any of these taps. Local edits to tap files are clobbered by `brew update`. The correct approach is upstream contributions.

### 4. Reference gitnexus #2194 instead of filing a new issue

**Rationale:** Issue #2194 ("Tree-sitter 0.25 upgrade readiness", filed 2026-09-06) already encompasses the tree-sitter-zig peerOptional conflict. Filing a duplicate would be noise.

## Risks / Trade-offs

- **[Upstream PR rejection]** → Tap maintainers may not merge quickly. Mitigation: warnings are cosmetic; casks still install fine. The deprecation-to-removal timeline is typically months.
- **`postflight_steps` syntax unverified in cockpit-tools context** → The `run` verb signature is confirmed in install_steps.rb, but `appdir` availability inside `postflight_steps` block scope is not verified against the new DSL. Mitigation: test locally after PR merge, or verify against Homebrew docs before submitting.
- **`brew audit --online` hazard note is additive only** → Doesn't prevent the issue, just documents it. Mitigation: sufficient for a workspace-level guard; preventing it would require Homebrew upstream changes.

## Migration Plan

1. File PR on jlcodes99/cockpit-tools: remove `verified:`, rename `postflight` → `postflight_steps` with `run`
2. Comment on stablyai/homebrew-orca#245: confirm investigation, suggest PR if maintainer is unresponsive
3. File issue on anomalyco/homebrew-tap: document `verified:` deprecation for hex.rb
4. Comment on abhigyanpatwari/GitNexus#2194: note tree-sitter-zig peerOptional conflict as part of upgrade readiness
5. Add hazard note to ~/Developer/CLAUDE.md
6. Verify: `brew update && brew upgrade` produces no deprecation warnings from these taps after upstream merges

## Open Questions

None. All technical decisions are resolved by the research findings.
