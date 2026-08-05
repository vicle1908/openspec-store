# Tasks: Canonical OpenCode Configuration

## 1. Discovery and Backup

- [x] 1.1 Record effective configuration structure without exposing credentials.
- [x] 1.2 Create timestamped backups of active `opencode.json` and `opencode.jsonc`.

## 2. Consolidation

- [x] 2.1 Produce canonical valid JSON containing all user-owned effective settings.
- [x] 2.2 Remove `opencode.jsonc` from the active global configuration names while retaining its backup.

## 3. Static Verification

- [x] 3.1 Validate canonical JSON syntax.
- [x] 3.2 Verify model, small model, agent mappings, providers, LSP, formatter, instructions, compaction, watcher, and MCP states.
- [x] 3.3 Verify only `opencode.json` remains as an active global config.

## 4. Runtime Verification

- [x] 4.1 Run the default-model smoke test.
- [x] 4.2 Run `shopapikey/fable-5` smoke test.
- [x] 4.3 Run `cockpit/gpt-5.6-sol` smoke test.
- [x] 4.4 Run `cockpit/gpt-5.6-luna` smoke test.
- [x] 4.5 Verify Ruff and Basedpyright remain on PATH.

## 5. Documentation and Archive

- [x] 5.1 Record exact verification evidence.
- [x] 5.2 Validate and archive this change.
- [x] 5.3 Commit only this change's OpenSpec files and keep unrelated active work untouched.
