## 1. Upstream Cask Fixes

- [ ] 1.1 File PR on jlcodes99/cockpit-tools: remove `verified:` line and rename `postflight do` → `postflight_steps do` with `run` verb in Casks/cockpit-tools.rb. Verify: PR created, diff shows verified removal + postflight_steps migration.
- [ ] 1.2 Comment on stablyai/homebrew-orca#245: confirm investigation findings, note that `verified:` is a no-op in Homebrew 6.x (url.rb:79), and suggest the one-line fix (delete line 9 in orca.rb, line 9 in orca@rc.rb). Verify: comment posted with investigation details.
- [ ] 1.3 File issue on anomalyco/homebrew-tap: document `verified:` deprecation for Casks/hex.rb, note that `verified:` is a no-op and safe to remove. Verify: issue created with correct repo reference.

## 2. Upstream Dependency Tracking

- [ ] 2.1 Comment on abhigyanpatwari/GitNexus#2194: note that `@tree-sitter-grammars/tree-sitter-zig@1.1.2` declares `peerOptional tree-sitter@^0.22.1` while gitnexus pins `tree-sitter@0.21.1`, and npm overrides the optional peer. Verify: comment posted referencing the peer dep conflict.

## 3. Workspace Documentation

- [ ] 3.1 Add `brew audit --online` hazard note to ~/Developer/CLAUDE.md under Gotchas: document that `brew audit --online` triggers concurrent self-update + vendor bundle rebuild, which can transiently break brew's Ruby startup via JSON gem double-load. Verify: CLAUDE.md updated, note is accurate.

## 4. Verification

- [ ] 4.1 Run `brew update && brew upgrade` and verify no deprecation warnings from cockpit-tools, orca, or hex taps (after upstream merges). Verify: clean output, no `verified` or `postflight` warnings.
