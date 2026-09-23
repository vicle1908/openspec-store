# icloud-full-code-migration Specification

## Purpose
Define fail-closed migration, verification, quarantine, and bounded deletion requirements for migrating all confirmed code projects, microservices, utility scripts, study code, Android projects, MCP servers, and developer credentials/configs from iCloud Drive (`com~apple~CloudDocs`) to local storage (`~/Developer`).

## Requirements

### Requirement: Discovery and exclusion pruning protect APFS volume headroom

The migration pipeline SHALL prune transient directories (`node_modules`, `.venv`, `.gradle`, `build`, `dist`, `__pycache__`, and generated vector databases) and non-code book documents (`.epub`, `.pdf`, `.mobi`, `.azw3`, `.rar`, `.zip`) at the directory traversal level and SHALL assert minimum APFS volume free space before triggering hydration.

#### Scenario: APFS headroom is verified before hydration

- **WHEN** the migration pipeline initiates pre-flight checks
- **THEN** it checks root volume capacity and asserts that free space exceeds 20 GB before issuing any hydration requests.

#### Scenario: Directory-level pruning prevents sync daemon saturation

- **WHEN** the directory enumerator encounters an excluded folder name (`node_modules`, `.venv`, `.gradle`, `build`, `target`, `__pycache__`, or `qdrant_storage`)
- **THEN** it skips the directory and all its descendants without querying individual child items or requesting ubiquitous downloads.

#### Scenario: Non-code book documents are excluded from code migration

- **WHEN** traversing `books/` for code migration
- **THEN** only source code files and their containing subdirectories (`Go by Example Source Code`, `Learning-Spring-Boot-4-main`) are targeted for migration
- **AND** all book documents (`.epub`, `.pdf`, `.mobi`, etc.) remain untouched in iCloud Drive.

### Requirement: Asynchronous Cocoa hydration handles dataless files safely

The migration pipeline SHALL trigger materialization of dataless APFS files (`SF_DATALESS` / `st_blocks == 0`) using asynchronous Cocoa APIs and SHALL verify materialization via `os.lstat` before reading or copying file content.

#### Scenario: Dataless file is detected and materialized

- **WHEN** a candidate source file has `st_flags & 0x40000000` or (`st_blocks == 0` and `st_size > 0`)
- **THEN** the pipeline triggers ubiquitous item download via the Cocoa helper
- **AND** polls `os.lstat` until `st_blocks > 0` before any read or digestion occurs.

#### Scenario: Materialization fails or times out

- **WHEN** a dataless file cannot be materialized within the bounded timeout period
- **THEN** the error is recorded in the project manifest, the source file is left untouched, and the migration gate marks the file as unmigrated.

### Requirement: Sensitive file classification and quarantine isolation

The migration pipeline SHALL identify sensitive files (`.env*`, credentials, private keys, certificates, recovery codes) during discovery, isolate them in a dedicated quarantine directory under `0700` directory and `0600` file permissions, and exclude them from public manifest artifacts.

#### Scenario: Sensitive file is detected during migration

- **WHEN** a source file name matches `.env*`, `credentials*`, `secrets*`, `id_rsa*`, `*recovery-codes*`, or ends in `.pem`, `.key`, `.p12`, `.pfx`, `.crt`, or `.cer`
- **THEN** the file is copied to `sensitive-quarantine/<project>/` rather than the general destination
- **AND** the directory mode is set to `0700` and the file mode is set to `0600` without dereferencing symlinks.

#### Scenario: Sensitive credential in root or utility directory is quarantined

- **WHEN** discovering credentials like `github/github-recovery-codes.txt` or `ascend/AWS/KeyPair/*.pem` or `.vds/.env`
- **THEN** they are transferred exclusively to `~/Developer/sensitive-quarantine/` with `0700` directory and `0600` file modes.

### Requirement: Atomic copy and manifest verification

The migration pipeline SHALL copy files using temporary sibling files (`.<filename>.tmp`) with flush and fsync, atomically install them via rename, compute SHA-256 digests, and record entries in a persistent JSON manifest.

#### Scenario: File is copied and verified atomically

- **WHEN** a source file is readable and materialized
- **THEN** it is written to a temporary file in the destination directory, flushed and synced to disk, and renamed to the target path
- **AND** the size and SHA-256 digest are recorded in the migration manifest.

#### Scenario: Destination already exists with identical digest

- **WHEN** the destination file already exists and its size and SHA-256 digest match the source file
- **THEN** the pipeline accepts the existing destination file as verified without re-copying.

### Requirement: Two-way reconciliation audit gate precedes deletion

The migration pipeline SHALL perform a two-way reconciliation audit comparing 100% of source files against destination files, quarantined files, and canonical exclusions before granting deletion authorization.

#### Scenario: All source files are accounted for

- **WHEN** every file in the iCloud source tree is accounted for as verified in destination, quarantined, or canonically excluded
- **THEN** the reconciliation audit asserts `unaccounted_missing == 0` and `size_mismatches == 0`, and grants deletion readiness.

#### Scenario: Unaccounted or mismatched files exist

- **WHEN** any source file is missing from destination/quarantine or exhibits a size/checksum mismatch
- **THEN** the reconciliation audit halts, deletion authorization is withheld, and the exact gaps are reported.

### Requirement: Fail-closed bounded deletion

The deletion tool SHALL enforce per-file destination presence checks immediately prior to unlinking any iCloud source file, prune empty directories bottom-up, and leave parent sibling directories untouched.

#### Scenario: Verified file is safely unlinked

- **WHEN** `(dest_root / rel).exists()` or `os.path.lexists(quarantine_root / rel)` is confirmed immediately prior to unlinking
- **THEN** the source file is unlinked and logged.

#### Scenario: Destination file is missing at unlinking time

- **WHEN** the destination file is absent when an unlinking operation is attempted
- **THEN** the deletion pipeline aborts execution immediately (`sys.exit(1)`) without unlinking the source file.

#### Scenario: Root debris is purged without affecting personal directories

- **WHEN** root debris items (`_internal/`, `base64/`, `METADATA`, `.vds`, etc.) are confirmed as non-source packaging artifacts
- **THEN** they are unlinked while personal directories (`SHB/`, `TDT/`, `candidate/`, `books/*.epub`, etc.) remain strictly untouched.

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
