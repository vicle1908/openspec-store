# Tasks

## 1. Record the immutability violation

- [x] 1.1 Identify the file added to the archived change `2026-10-03-add-phanmemvip-codex-x-provider` and the commit that introduced it, and confirm that the addition is the only deviation. Verify by showing the offending path, the introducing commit (`6f274f8d`), and that `git show --name-status` for that commit lists a single added file.
- [x] 1.2 Capture the current content of the added file and the archived revision reference before removing anything, so the content is recoverable. Verify the captured copy is readable and byte-count-matched against the file on disk.

## 2. Restore the archive

- [x] 2.1 Remove the added `evidence.md` from the archived change directory. Verify the archived directory contains exactly its original files (`proposal.md`, `design.md`, `tasks.md`, `specs/`, `.openspec.yaml`) and no `evidence.md`.
- [x] 2.2 Confirm no other archived change was touched, and that no archived file content was edited in place. Verify `git status` shows only the single removal plus this change's own files.

## 3. Preserve the recovered evidence

- [x] 3.1 Add the recovered evidence to this change's own `evidence.md` rather than creating a separate file, so the change complies with the single-evidence-file rule it establishes. Verify `evidence.md` contains the recovered content (task 4.1–4.3 results and the investigated 401 finding) under its own heading, and that no second evidence file or `evidence/` directory exists in this change.

## 4. Name the artifact in archive guidance

- [x] 4.1 Extend `operations.archive.guidance` in `openspec/config.yaml` to require a single `evidence.md` for changes that perform verification, and to state that existing `evidence/` directories are grandfathered and not migrated. Verify the added guidance lines are present and that the file still parses as YAML.
- [x] 4.2 Verify the guidance does not require evidence from changes that perform no verification. Verify the wording states the requirement conditionally on verification work.

## 5. Verification

- [x] 5.1 Validate the change artifacts against the store schema. Verify `openspec validate standardize-archive-evidence-convention --store openspec-store` reports no errors.
- [x] 5.2 Validate the whole store after the guidance edit and the archive restoration. Verify `openspec validate --specs --store openspec-store` reports zero failures and the archived change still resolves.
- [x] 5.3 Record this change's own verification evidence in `evidence.md`, following the standardized form this change establishes. Verify the file records the pre-edit archive state, the reversion, the guidance diff, and the validation results.

## 6. Commit

- [ ] 6.1 Commit the reversion, the recovered evidence, the guidance edit, and this change's artifacts as a single scoped commit whose message states explicitly that the archive was restored (not altered). Verify the commit lists only the affected archive path removal, this change's directory, and `openspec/config.yaml`, and that no other archived change appears in the diff.
- [ ] 6.2 Confirm the archived change matches its pre-edit content after the commit. Verify that diffing the archived directory against its state at the violation's parent commit `ed231341` (the pre-edit revision, i.e. `6f274f8d^`) reports no difference.
