# Design: Migrate Google Drive Source Code to Local Workspace

## Architecture & System Context

This design outlines the architecture, data flow, filtering rules, and verification mechanics for migrating source code repositories and configurations from Google Drive (`gdrive-tdt:`) to `~/Developer/`.

```text
Google Drive (Remote: gdrive-tdt:)
├── In-Scope Code Roots (Mobile, Go, Ops, Configs)
└── Out-of-Scope (Personal, Finance, Legal, ML Weights, Archives)
       │
       ▼ [rclone direct API engine with --filter-from rules]
       │
  ┌────┴───────────────────────────┬────────────────────────────┐
  │ Whitelisted Source & Manifests │ Detected Secrets/TLS Keys  │ Blacklisted Caches/Binaries
  ▼                                ▼                            ▼
~/Developer/                      ~/Developer/sensitive-quarantine/   [Ignored / Dropped]
├── mobile/                       ├── docker-traefik/ (0700/0600)     (Pods, xcframeworks,
│   ├── poems-mobile3-android/    │   └── acme.json                   .gradle, DerivedData,
│   └── poems-mobile3-ios/        └── mobile-keystores/               qi-gen-proxy)
├── qi-bridge/
├── ops-tools/
│   ├── tdt-tools/
│   └── bootstrap-nexus/
└── infra/
    ├── traefik/
    └── fpt-ingenico/
```

## Technical Decisions

### Decision 1: Direct API Transfer via rclone (Bypassing FileProvider)
- **Problem:** Traversing `~/Library/CloudStorage/GoogleDrive-*` blocks POSIX commands on kernel FileProvider IPC locks (`DFSFileProviderExtension`).
- **Solution:** Execute all queries, dry-runs, and transfers via `rclone` targeting the authenticated remote `gdrive-tdt:`. Local CloudStorage mount paths are explicitly bypassed.

### Decision 2: Strict Inclusion/Exclusion Filter Engine
- **Problem:** Native mobile repos (`poems-mobile3-android`, `poems-mobile3-ios`) contain multi-gigabyte build artifacts (`.xcframework`, `Pods/`, `.gradle/`, `build/`, `DerivedData/`). Transferring these unpruned exhausts APFS disk space and network bandwidth.
- **Solution:** Enforce a strict rclone filter file (`resources/gdrive-source-filter.txt`) that whitelists source extensions (`.kt`, `.java`, `.swift`, `.go`, `.py`, `.sh`, `.sql`) and project manifests while blacklisting all build outputs, binary frameworks, and virtual environments.

### Decision 3: Sensitive Credential Quarantining
- **Problem:** TLS keys (`acme.json`) and signing keystores stored in cloud folders risk permission leaks if copied directly to general development trees.
- **Solution:** Route any credential or private certificate into `~/Developer/sensitive-quarantine/<service>/` with directory mode `0700` and file mode `0600`, matching the established workspace security pattern.

### Decision 4: Non-Destructive Ingestion (Read-Only Remote)
- **Problem:** Destructive operations (`rclone move` or remote deletion) before thorough local verification risk data loss.
- **Solution:** Migration commands use `rclone copy --checksum`. Source files on Google Drive remain strictly read-only. Decommissioning is deferred to a future, separately authorized cleanup change.

### Decision 5: Two-Way Reconciliation & Local Authority for Python Repos
- **Problem:** `tdt/tdt-python-source-package/` contains 16 Python services that already exist in `~/Developer/`. Blindly copying could overwrite newer local git commits with stale cloud files.
- **Solution:** Local `~/Developer/<repo>` is the primary authority. Remote Python directories are inspected via diff comparison. Files matching local are skipped; divergence is flagged in an audit artifact.

## Local Directory Mapping

| Source Path (`gdrive-tdt:`) | Target Local Path | Target Ownership & Mode |
| :--- | :--- | :--- |
| `tdt/poems-mobile3-android/` | `~/Developer/mobile/poems-mobile3-android/` | Standard workspace (`0755` dir, `0644` file) |
| `tdt/poems-mobile3-ios/` | `~/Developer/mobile/poems-mobile3-ios/` | Standard workspace (`0755` dir, `0644` file) |
| `tdt/qi-bridge/` | `~/Developer/qi-bridge/` | Standard workspace (`0755` dir, `0644` file) |
| `tdt/tdt-tools/` | `~/Developer/ops-tools/tdt-tools/` | Executable scripts (`0755` dir, `0755` scripts) |
| `tdt/bootstrap-nexus-for-mobile/` | `~/Developer/ops-tools/bootstrap-nexus/` | Standard workspace (`0755` dir, `0644` file) |
| `Docker/traefik/` | `~/Developer/infra/traefik/` | Standard workspace (excluding `acme.json`) |
| `Docker/traefik/acme.json` | `~/Developer/sensitive-quarantine/traefik/acme.json` | Restricted quarantine (`0700` dir, `0600` file) |
| `Fpt/Ingenico/` | `~/Developer/infra/fpt-ingenico/` | Standard workspace (`0755` dir, `0644` file) |

## Filter Ruleset Specification

```text
# --- INCLUDE PATTERNS: Source Code, Manifests, Schemas, Docs ---
+ *.kt
+ *.java
+ *.swift
+ *.go
+ *.py
+ *.sh
+ *.sql
+ *.c
+ *.cpp
+ *.h
+ *.puml
+ *.md
+ AGENTS.md
+ CLAUDE.md
+ go.mod
+ go.sum
+ pyproject.toml
+ uv.lock
+ build.gradle*
+ settings.gradle*
+ gradle.properties
+ gradlew
+ gradlew.bat
+ Package.swift
+ *.xcodeproj/project.pbxproj
+ *.xcworkspace/contents.xcworkspacedata
+ Dockerfile*
+ docker-compose*.yml
+ Makefile
+ *.patch
+ *.toml
+ *.yaml
+ *.yml
+ *.json
+ *.xml

# --- EXCLUDE PATTERNS: Compiled Binaries & Packages ---
- qi-gen-proxy
- *.xcframework/**
- *.framework/**
- Pods/**
- *.apk
- *.aab
- *.ipa
- *.pt
- *.onnx
- *.tar.gz
- *.zip
- *.so
- *.dylib
- *.bin
- *.exe

# --- EXCLUDE PATTERNS: Build Outputs, Virtualenvs & Caches ---
- .gradle/**
- build/**
- DerivedData/**
- .venv/**
- node_modules/**
- __pycache__/**
- *.pyc
- .pytest_cache/**
- .gitnexus/**

# --- EXCLUDE PATTERNS: Isolated Secrets (Transferred Separately) ---
- acme.json
- *.jks
- *.keystore
- *.pem
- *.p12
- *.p8

# Catch-all
- *
```

## Verification & Integrity Protocol

1. **Pre-Flight Dry-Run:**
   Execute `rclone copy --dry-run` with filter rules against each target project. Record planned file count and payload size in `evidence/preflight-dryrun.json`. Assert payload size < 400 MB.
2. **Checksum Verification:**
   Execute ingestion using `rclone copy --checksum`. Generate post-transfer SHA-256 manifest of local files and compare against remote object sizes.
3. **Build & Syntax Verification:**
   - Go: Run `go vet ./...` in `~/Developer/qi-bridge/`.
   - Python: Run `python3 -m py_compile` across all scripts in `~/Developer/ops-tools/tdt-tools/`.
   - Shell: Run `bash -n` on all migrated `.sh` scripts.
4. **Credential Quarantine Audit:**
   Assert zero private key headers or `.jks`/`.keystore` files exist in general code directories. Verify `stat -f "%Lp" ~/Developer/sensitive-quarantine/traefik/acme.json` returns `600`.
