# Spec Delta: icloud-full-code-migration

## ADDED Requirements

### Requirement: Residual developer asset migration preserves directory structure and live repositories

The migration pipeline SHALL copy the identified residual developer assets from `Documents/`, `Desktop/`, `books/`, and `Downloads/` into designated local directories under `~/Developer/`, preserving internal directory hierarchy without mutating or overwriting active development repositories.

#### Scenario: Historical MCP Router trial snapshot is migrated to an isolated backup root
- **WHEN** migrating `Documents/Codex/2026-07-22/try/work/mcp-router-src`
- **THEN** all 393 files and nested subdirectories (`apps/`, `packages/`, `docs/`, `tools/`) SHALL be transferred to `~/Developer/mcp-router-backup-20260722/`
- **AND** the active checkout at `~/Developer/mcp-router` SHALL NOT be overwritten or modified.

#### Scenario: Lending miniapp architecture documentation is preserved with subdirectories
- **WHEN** migrating `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe`
- **THEN** all 14 documentation files and the nested `diagrams/` subdirectory SHALL be migrated to `~/Developer/lending-miniapp-docs/` matching source names verbatim.

#### Scenario: Production secrets security guide is migrated to central docs
- **WHEN** migrating `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md`
- **THEN** the file SHALL be installed at `~/Developer/docs/PRODUCTION_SECRETS_SECURITY_GUIDE.md` with mode `0644`.

#### Scenario: Study source code is isolated from book reading documents
- **WHEN** migrating `books/ai/2025/Investing for Programmers/investing-for-programmers-main`
- **THEN** only the 30 Python, README, and configuration files SHALL be transferred to `~/Developer/study-examples/investing-for-programmers/`
- **AND** all parent and sibling PDF/ePub book files in `books/` SHALL remain untouched in iCloud Drive.

#### Scenario: Utility setup script is quarantined if secrets are detected
- **WHEN** inspecting `Downloads/setup-fable-5.sh` and detecting embedded credentials or API keys
- **THEN** the script SHALL be isolated in `~/Developer/sensitive-quarantine/downloads/setup-fable-5.sh` with mode `0600`.

#### Scenario: Study code zip archives are extracted and purged from books directory
- **WHEN** migrating study code archives `books/.../code.zip` and `books/.../sckotlin-code.zip`
- **THEN** the archives SHALL be extracted into `~/Developer/study-examples/` subdirectories
- **AND** the source zip archives SHALL be purged from iCloud while preserving all book documents (.pdf, .epub).

#### Scenario: Residual workplace credentials and environment configs are quarantined
- **WHEN** migrating `ghtk/soft/charles/charlesKey.rtf` and `ghtk/zshrc/.zshrc`
- **THEN** the credential assets SHALL be installed in `~/Developer/sensitive-quarantine/ghtk/` with file permissions `0600`.

### Requirement: Residual cloud source purge is bounded and gated on 100% digest verification

The migration pipeline SHALL gate the deletion of residual cloud source directories on a successful `--verify-only` pass confirming 100% SHA-256 digest and byte-count equality for all manifest entries, and SHALL strictly protect all personal non-code directories from deletion.

#### Scenario: Residual cloud sources are safely purged after verification
- **WHEN** read-back verification against the migration manifests passes with 0 missing files and 0 checksum mismatches
- **THEN** the pipeline SHALL delete only the confirmed source paths in `Documents/Codex/.../mcp-router-src`, `Desktop/.../lending-miniapp-fe`, `books/.../investing-for-programmers-main`, `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md`, and `Downloads/setup-fable-5.sh`
- **AND** bottom-up prune empty parent directories without traversing into personal folders.

#### Scenario: Deletion is rejected if destination verification fails
- **WHEN** destination verification reports any missing file or digest mismatch
- **THEN** cloud source deletion SHALL be aborted immediately
- **AND** all iCloud files SHALL remain unmutated.
