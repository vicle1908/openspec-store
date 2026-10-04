# Tasks

## 1. Establish What Can Still Be Upgraded

- [x] 1.1 Confirm all six direct dependencies are already at their latest published versions
- [x] 1.2 Enumerate transitive dependencies behind latest, separating in-range from out-of-range
- [x] 1.3 Exclude `MISSING` optional platform binaries from the upgrade candidate set
- [x] 1.4 Confirm none of the 20 existing override pins is behind its package's latest

## 2. Apply the In-Range Refresh

- [x] 2.1 Capture the pre-change manifest and lockfile for rollback
- [x] 2.2 Run `npm update` to raise every dependency the parent ranges already permit
- [x] 2.3 Record the version deltas applied

## 3. Verify No Downgrade Occurred

- [x] 3.1 Diff the name@version set before and after the refresh
- [x] 3.2 Confirm each disappeared version was replaced by its own newer version
- [x] 3.3 Confirm apparent top-level drops were hoisting relocations, with the higher version still present in the tree

## 4. Raise the Exact-Pinned Stragglers

- [x] 4.1 Identify `aws4` and `extsprintf` as unresolvable by range
- [x] 4.2 Add upgrade-only overrides `aws4: >=1.13.2` and `extsprintf: >=1.4.1`
- [x] 4.3 Install and confirm `aws4@1.13.2` and `extsprintf@1.4.1`

## 5. Verify the Tools and the Residual Set

- [x] 5.1 Confirm `bru`, `yaml-language-server`, `newman-reporter-htmlextra`, `newman`, and `gitnexus` all execute
- [x] 5.2 Confirm our own `yaml-language-server` and `bru` still work from `~/.local/bin` symlinks
- [x] 5.3 Confirm `npm outdated` and `npm outdated --all` report no remaining in-range moves
- [x] 5.4 Record that `npm audit` remains at 12 high and why

## 6. Evidence and Spec Sync

- [x] 6.1 Author `evidence.md` in the change directory from output read back from disk
- [x] 6.2 Run `openspec validate --all` and confirm the delta spec validates
- [x] 6.3 Sync the delta spec into the main `npm-audit-remediation` spec at archive time
- [x] 6.4 Archive the change and commit the store
