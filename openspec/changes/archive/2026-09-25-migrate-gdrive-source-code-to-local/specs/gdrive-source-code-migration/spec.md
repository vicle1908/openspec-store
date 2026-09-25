# Specification: Google Drive Source Code Migration

## Purpose

Establish normative requirements and testable acceptance scenarios for migrating verified source code repositories, tools, and developer configurations from Google Drive (`gdrive-tdt:`) to the local `~/Developer/` workspace while enforcing strict exclusion of build caches, binary frameworks, and personal data.

## ADDED Requirements

### Requirement: Direct API Migration Engine SHALL Bypass macOS FileProvider Mounts

The migration toolchain SHALL execute all remote discovery, dry-runs, and file ingestion via direct authenticated Google Drive API calls (using `rclone` with remote `gdrive-tdt:`). The system SHALL NOT use POSIX file operations (`ls`, `stat`, `find`) on macOS CloudStorage mount points (`~/Library/CloudStorage/GoogleDrive-*`) to prevent kernel FileProvider IPC deadlocks.

#### Scenario: Discovery and dry-run execution
- **WHEN** directory inventory or file copying is initiated
- **THEN** the command invokes `rclone` directly targeting `gdrive-tdt:` without referencing `~/Library/CloudStorage/` paths.

### Requirement: Strict Filter Ruleset SHALL Exclude Binary Frameworks and Build Caches

The file transfer engine SHALL apply an explicit inclusion and exclusion filter file during all ingestion passes. The engine SHALL strictly exclude compiled binary frameworks (`*.xcframework/**`, `*.framework/**`), dependency directories (`Pods/**`, `.gradle/**`, `.venv/**`, `node_modules/**`), compiled binaries (`qi-gen-proxy`, `*.apk`, `*.ipa`, `*.pt`, `*.onnx`), and build output trees (`build/**`, `DerivedData/**`).

#### Scenario: Mobile repository file ingestion
- **WHEN** `poems-mobile3-android` or `poems-mobile3-ios` is copied from `gdrive-tdt:` to `~/Developer/`
- **THEN** only source files (`.kt`, `.java`, `.swift`, etc.) and configuration manifests (`build.gradle*`, `project.pbxproj`, etc.) are created locally, and zero `.xcframework` or `Pods/` files are written.

### Requirement: Sensitive Credentials and TLS Certificates SHALL Route to Dedicated Quarantine

Any discovered sensitive credential, TLS certificate, private key, or keystore (`acme.json`, `*.jks`, `*.keystore`, `*.pem`, `*.p12`, `*.p8`) SHALL be routed exclusively to `~/Developer/sensitive-quarantine/<service>/`. The destination directory SHALL have POSIX permissions set to `0700` and regular files SHALL have permissions set to `0600`. Credential files SHALL NOT be placed inside general workspace code repositories.

#### Scenario: Traefik TLS configuration ingestion
- **WHEN** `Docker/traefik/acme.json` is retrieved from Google Drive
- **THEN** the file is placed at `~/Developer/sensitive-quarantine/traefik/acme.json` with mode `0600` and its parent directory has mode `0700`.

### Requirement: Ingestion SHALL Be Non-Destructive and Checksum-Verified

The migration process SHALL preserve all remote source files in Google Drive in a read-only state throughout the migration lifecycle. The engine SHALL NOT issue `rclone delete`, `rclone purge`, or `rclone move` commands against the remote source. 100% of copied local files SHALL match the remote source file sizes and SHALL be verified against a local SHA-256 manifest.

#### Scenario: Checksum and byte-count verification
- **WHEN** file transfer completes for a target project
- **THEN** a post-copy verification script confirms that local file count and byte sizes match the remote manifest, and remote files remain untouched.

### Requirement: Python Services SHALL Enforce Local Workspace Authority

The migration workflow SHALL treat existing local repositories under `~/Developer/` (`agent-core`, `tdt-core`, `ai-review`, etc.) as authoritative. The system SHALL NOT blindly overwrite local files with remote files from `tdt/tdt-python-source-package/`. The workflow SHALL generate a two-way delta report detailing file differences before any remote changes may be staged.

#### Scenario: Python repository comparison
- **WHEN** reconciling `tdt/tdt-python-source-package/` against `~/Developer/`
- **THEN** an audit manifest is generated reporting matched, modified, and remote-only files, and zero existing local files are overwritten without explicit confirmation.
