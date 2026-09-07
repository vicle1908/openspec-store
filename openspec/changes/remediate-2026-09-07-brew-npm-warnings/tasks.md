## 1. Workspace Documentation

- [ ] 1.1 Add `brew audit --online` hazard note to ~/Developer/CLAUDE.md under Gotchas: document that `brew audit --online` triggers concurrent self-update + vendor bundle rebuild, which can transiently break brew's Ruby startup via JSON gem double-load. Recovery: wait for self-heal or run `brew update-reset`. Verify: CLAUDE.md updated, note is accurate.
- [ ] 1.2 Add deprecation warning limitations to ~/Developer/CLAUDE.md: document that `verified:` deprecation warnings (4 casks across 3 taps) and `postflight` deprecation (cockpit-tools) are cosmetic now but will become hard errors in a future Homebrew release. Depend on upstream tap maintainers to resolve. Verify: limitations section added.

## 2. Verification

- [ ] 2.1 Run `brew update && brew upgrade` and confirm completion without new warnings. Verify: clean output.
- [ ] 2.2 Run `npm update -g` and confirm completion without new peer dep conflicts. Verify: clean output.
