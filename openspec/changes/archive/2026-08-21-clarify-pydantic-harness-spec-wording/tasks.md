## 1. Scope and source evidence

- [x] 1.1 Confirm the supplied verification report and prior correction archive are readable; verify the change scope names only `agent-compaction`, `agent-core-capabilities`, and `vendor-isolation`.
- [x] 1.2 Capture the pre-archive branch, full HEAD, raw dirty inventory, active-change names, and prior archive paths; verify unrelated paths are preserved.

## 2. Documentation contract correction

- [x] 2.1 Update `agent-compaction` with the projection-versus-automatic-read historical wording and named `compaction_enabled=false` semantics; verify every existing scenario label remains present in the delta and archived main spec.
- [x] 2.2 Replace `agent-core-capabilities` Purpose TBD and add `compaction_enabled` to supported public runtime options while keeping private legacy aliases separate; verify the public-options and compatibility-only scenarios remain present.
- [x] 2.3 Keep `vendor-isolation` purpose and complete VI-1/VI-2 blocks consistent with intentional public SDK forwarding and internal adapter isolation; verify all existing VI-1/VI-2 scenario labels remain present.

## 3. CLI validation and archive

- [x] 3.1 Run `openspec validate clarify-pydantic-harness-spec-wording --strict --store openspec-store` and `openspec validate --all --strict --store openspec-store`; record exact output and exit codes before archive.
- [x] 3.2 Archive only with `openspec archive clarify-pydantic-harness-spec-wording --yes --store openspec-store`; verify the new dated archive exists and prior dated archives remain untouched.
- [x] 3.3 Run `openspec validate --all --strict --store openspec-store` after archive and verify active status excludes this change; inspect main-spec content and scenario-label preservation.

## 4. Evidence and commit boundary

- [x] 4.1 Write `/Users/androidteam/Developer/openspec-store/.superpowers/sdd/2026-08-20-pydantic-harness-contract/spec-wording-report.md` with exact commands, exit codes, full commit SHA, changed paths, preservation evidence, and any CLI limitation.
- [x] 4.2 Stage and commit only CLI-created correction/archive/main-spec paths plus the requested report; verify `reports/` and unrelated active changes are unstaged and report the commit SHA.
