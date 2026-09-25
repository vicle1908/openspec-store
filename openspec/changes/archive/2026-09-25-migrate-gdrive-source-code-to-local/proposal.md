# Proposal: Migrate Google Drive Source Code to Local Workspace

## Summary

Migrate confirmed, uncorrupted source code projects from Google Drive (`gdrive-tdt:`) to local persistent storage under `~/Developer/`, while strictly excluding non-code assets (personal documents, financial spreadsheets, media, binary weights, build outputs, and dependency caches). This change follows a strict read-only discovery, dry-run manifest budgeting, credential isolation, and checksum-verified ingestion lifecycle.

## Problem Statement

Historically, multiple software projects and configuration bundles were uploaded or synchronized to Google Drive. These include:
- Native mobile client applications (`tdt/poems-mobile3-android` and `tdt/poems-mobile3-ios`) and their release branch checkouts.
- Infrastructure and proxy services (`tdt/qi-bridge`, `tdt/bootstrap-nexus-for-mobile`, `Docker/traefik`).
- Operational tools and developer configurations (`tdt/tdt-tools`, `Fpt/Ingenico`).
- 16 Python repositories in `tdt/tdt-python-source-package/` that were previously synchronized via `rclone bisync`.

Storing active source code exclusively in cloud drives introduces significant failure modes:
1. **FileProvider IPC lockups:** Traversing macOS CloudStorage mounts (`~/Library/CloudStorage/GoogleDrive-*`) stalls local command-line tools due to background daemon sync locks.
2. **Build and cache bloat:** Cloud sync directories accumulate heavy build artifacts (`.xcframework`, `Pods/`, `build/`, `.gradle/`, `DerivedData/`) consuming tens of gigabytes of disk and network quota.
3. **Repository corruption risk:** Cloud syncing of active `.git/` object trees across distributed devices causes dangling commits, zero-byte packfiles, and index desynchronization.
4. **Credential sprawl:** Production TLS configuration (`acme.json`) and signing keystores remain stored in unquarantined shared cloud storage folders.

## Proposed Solution

Implement a 5-phase OpenSpec migration workflow:

### Phase 1: Read-Only Discovery, Inventory & Dry-Run Manifest
- Enumerate candidate source roots across `gdrive-tdt:` bypassing macOS FileProvider via direct `rclone` API commands.
- Partition all 36 root Google Drive directories into **In-Scope (Source Code & Tooling)** and **Out-of-Scope (Personal, Financial, Legal, ML Weights)**.
- Apply a strict inclusion/exclusion filter ruleset to calculate exact eligible file counts and payload sizes (< 400 MB target).

### Phase 2: Sensitive Credential Quarantining
- Detect, isolate, and route any private certificates or TLS configurations (e.g. `Docker/traefik/acme.json`, `.jks`, `.keystore`, `.pem`) into `~/Developer/sensitive-quarantine/` with `0700` directory and `0600` file permissions.
- Reject storing raw credentials inside normal code repository paths.

### Phase 3: Selective Source Ingestion & Integrity Verification
- Ingest approved source code trees into designated `~/Developer/` paths using `rclone copy --checksum`:
  - `tdt/poems-mobile3-android` -> `~/Developer/mobile/poems-mobile3-android/`
  - `tdt/poems-mobile3-ios` -> `~/Developer/mobile/poems-mobile3-ios/`
  - `tdt/qi-bridge` -> `~/Developer/qi-bridge/`
  - `tdt/tdt-tools` -> `~/Developer/ops-tools/tdt-tools/`
  - `tdt/bootstrap-nexus-for-mobile` -> `~/Developer/ops-tools/bootstrap-nexus/`
  - `Docker/traefik` -> `~/Developer/infra/traefik/`
  - `Fpt/Ingenico` -> `~/Developer/infra/fpt-ingenico/`
- Assert 100% byte count and SHA-256 integrity match between remote files and local copies.
- Exclude all `.gradle/`, `build/`, `Pods/`, `*.xcframework/`, and compiled binaries (`qi-gen-proxy`).

### Phase 4: Python Service Delta Reconciliation
- Compare remote `tdt/tdt-python-source-package/` against existing local checkouts (`~/Developer/agent-core`, etc.).
- Prevent blind overwrites; identify and report any uncommitted remote-only commits or divergence.

### Phase 5: Workspace Wiring & Baseline Commit
- Initialize clean Git baselines (`git init -b main`) for newly ingested standalone projects that lack version control.
- Register new projects in workspace `AGENTS.md` and index in GitNexus.
- Decommission stale `rclone bisync` loops for TDT repositories.

## Scope Boundaries

### In Scope
- Mobile native repositories (`poems-mobile3-android`, `poems-mobile3-ios`).
- Go proxy services and infrastructure scripts (`qi-bridge`, `bootstrap-nexus-for-mobile`, `tdt-tools`).
- Traefik configurations and mobile linting rules (`Docker/traefik`, `Fpt/Ingenico`).
- TLS certificates and keystores routed to restricted quarantine.

### Out of Scope (Retain Untouched in Google Drive)
- Personal, financial, and legal records (18 folders: `Bien lai`, `Binance`, `CV`, `CheFC`, `Coins`, `Loan`, `Lucidchart`, `NTU AI Keynote`, `Nha Thue HHT`, `Picture`, `SGpolice`, `Shb`, `SingPost`, `Takeout`, `Training`, `Uy quyền`, `VicDoc`, `invest`, `pay`).
- Binary model weights and ML datasets (`AI`, `YoloV8`, `Colab Notebooks`, `ColabNotebooks`).
- Git cold backup archives (`tdt/git-bundles`, `tdt/git-remotes`) — kept as immutable cold remote archives.
- Destructive deletion of remote files in Google Drive — source files remain read-only during migration.

## Success Criteria

1. **Zero FileProvider stalls:** 100% of discovery and transfer operations execute via direct rclone API calls.
2. **Strict filtering:** Zero compiled frameworks (`.xcframework`), dependency directories (`Pods/`, `.gradle/`, `.venv`), or build outputs hydrate locally.
3. **Verified integrity:** All transferred regular files pass post-copy SHA-256 and byte-size verification against the remote manifest.
4. **Credential containment:** 100% of discovered credentials (`acme.json`, keystores) reside in `~/Developer/sensitive-quarantine/` with `0700`/`0600` permissions.
5. **Syntax & build verification:** Transferred projects pass language syntax checks (`go vet ./...`, `python3 -m py_compile`).

## Risks & Mitigations

- **Risk:** Cloud rate limiting (`429 Too Many Requests`) during bulk file metadata inspection.
  *Mitigation:* Hierarchical directory discovery (`--max-depth 1`) and bounded transfers with paced retry backoff.
- **Risk:** Accidental ingestion of gigabytes of precompiled frameworks in iOS/Android repos.
  *Mitigation:* Pre-flight dry-run gate asserting total payload size < 400 MB before any file write.
- **Risk:** Overwriting newer local edits in Python repos with older Google Drive snapshots.
  *Mitigation:* Treat local `~/Developer/` as authoritative; run two-way diff comparison before staging remote Python files.
