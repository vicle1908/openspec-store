## 1. Workspace Documentation

- [x] 1.1 Add `brew audit --online` hazard note to ~/Developer/CLAUDE.md under Gotchas: document that `brew audit --online` triggers concurrent self-update + vendor bundle rebuild, which can transiently break brew's Ruby startup via JSON gem double-load. Recovery: delete corrupted json gem from vendor bundle. Verify: CLAUDE.md updated at line 69, note is accurate.
- [x] 1.2 Add deprecation warning limitations to ~/Developer/CLAUDE.md: document that `verified:` deprecation warnings (4 casks across 3 taps) and `postflight` deprecation (cockpit-tools) are cosmetic now but will become hard errors in a future Homebrew release. Depend on upstream tap maintainers to resolve. Verify: limitations section added at line 70.

## 2. Verification

- [x] 2.1 Run `brew update && brew upgrade` and confirm completion. Verify: 5 packages upgraded (pnpm, omp, pi-coding-agent, chatgpt, postman). Deprecation warnings documented as known limitations.
- [x] 2.2 Run `npm update -g` and confirm completion. Verify: 689 packages updated. tree-sitter peerOptional conflict documented as upstream issue #2194.
