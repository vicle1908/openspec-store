# Tasks

## 1. Keychain Diagnosis, Recovery & Antigravity 2.0 Verification

- [x] 1.1 Diagnose macOS Keychain failure in Cockpit Tools (`v1.4.2`) by reproducing `errSecAuthFailed` (`-25293`) across `security show-keychain-info`, `find-generic-password -w`, and `add-generic-password -U` alongside `SecKeychainGetStatus == 0x7` and `securityd` `-25337` (`CSSMERR_CSP_INVALID_DATA`) logs.
- [x] 1.2 Recover `~/Library/Keychains/login.keychain-db` unlock state (`security lock-keychain` + `security unlock-keychain`) and verify `security show-keychain-info ~/Library/Keychains/login.keychain-db` reports `no-timeout`.
- [x] 1.3 Verify Cockpit Tools (`v1.4.2`) **Switch only** (`gemini`/`antigravity` Keychain `mdat` updated to `20261123095139Z`) and **Switch and launch** with Antigravity 2.0 (`v2.34.0`, PID `75977`) via `computer-use` and `~/.antigravity_cockpit/logs/app.log.2026-11-23`.

## 2. OpenSpec, Runbook & Multi-Store Knowledge Synchronization

- [x] 2.1 Document the `SecKeychainGetStatus == 0x7` vs `SecKeychainCopySettings` (`-25293`) / `securityd` (`-25337`) diagnostic and recovery procedure in `platform/openspec-store/docs/mac-development-setup.md`.
- [x] 2.2 Validate the OpenSpec change and specs (`openspec validate reconcile-cockpit-antigravity-keychain-unlock --strict --store openspec-store` and `openspec validate --all --strict --store openspec-store`), sync delta spec to `workstation-remote-and-agent-permissions`, and archive the change.
- [x] 2.3 Update `~/Developer/wiki/` (`concepts/workstation-terminal-and-storage-resilience.md`, `log.md`, `index.md`) and sync updated concepts and OpenSpec catalog to Notion (`scripts/knowledge-refresh/sync-notion-knowledge.sh`).
- [x] 2.4 Record durable operational lessons in AgentMemory (`:3111`) and OMP long-term memory (`learn`), review diffs, and commit selective changes in `platform/openspec-store` and `wiki`.
