## 1. Fix is_dirty() exclusions

- [x] 1.1 Add exclusion for tracked graphify-out modifications: `grep -v '^ M graphify-out/'` and `grep -v '^M  graphify-out/'`
- [x] 1.2 Add exclusion for LSP state: `grep -v '^?? \.omp/'`
- [x] 1.3 Add exclusion for gitnexus-generated files (tracked AND untracked): `grep -v 'AGENTS\.md'` and `grep -v 'CLAUDE\.md'` (covers both ` M` and `??` prefixes)
- [x] 1.4 Add exclusion for gitnexus-generated skills: `grep -v '^?? \.claude/skills/gitnexus/'`
- [x] 1.5 Add comment block documenting each exclusion's purpose

## 2. Add --force flag

- [x] 2.1 Add `--force` to usage() help text
- [x] 2.2 Parse `--force` in main() arg loop, store as script-level `_FORCE` variable
- [x] 2.3 In process_target(), check `[[ "${_FORCE:-}" == "true" ]]` to skip is_dirty check
- [x] 2.4 Restrict --force to --repo mode only (error if used with batch)

## 3. Add freshness check

- [x] 3.1 Add `--check` flag to usage() and main() arg loop
- [x] 3.2 Implement check_inventory() that compares BOTH GitNexus (meta.json lastCommit) AND Graphify (graph.json built_at_commit) freshness
- [x] 3.3 Support --repo mode for single-repo freshness check
- [x] 3.4 Report stale repos with tool-specific status (which tool is stale)

## 4. Verify and test

- [x] 4.1 Test is_dirty() fix: verify 8 previously-skipped repos now refresh
- [x] 4.2 Test --force: verify it works on a genuinely dirty repo
- [x] 4.3 Test batch mode: verify dirty repos are still skipped
- [x] 4.4 Test --check: verify it reports both GitNexus and Graphify freshness
- [x] 4.5 Test --repo --check: verify single-repo freshness check works
- [x] 4.6 Verify script syntax: `bash -n refresh-knowledge-indexes.sh`
