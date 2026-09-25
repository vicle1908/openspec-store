# Acceptance Summary: Migrate Google Drive Source Code to Local Workspace

## Execution Overview

The OpenSpec change `migrate-gdrive-source-code-to-local` has been applied and verified in accordance with the specification. Source code repositories, operational tools, and developer configurations stored on Google Drive (`gdrive-tdt:`) have been safely migrated to local persistent storage under `~/Developer/`, bypassing macOS FileProvider stalls, strictly filtering build bloat, isolating sensitive credentials, and establishing immutable Git baselines.

---

## Migration Manifest & Verified Delivery

| Project / Component | Source (`gdrive-tdt:`) | Destination (`~/Developer/`) | Transferred Assets | Baseline Git Commit | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Qi Search Bridge** | `tdt/qi-bridge` | `~/Developer/qi-bridge` | 9 files (Go source, mod, docs) | `1dca0ed` | `go vet ./...` passed (0 errors) |
| **TDT Ops Tools** | `tdt/tdt-tools` | `~/Developer/ops-tools/tdt-tools` | 4 scripts (Python, Shell) | `50d0a09` | `python3 -m py_compile` & `bash -n` passed |
| **Bootstrap Nexus** | `tdt/bootstrap-nexus-for-mobile` | `~/Developer/ops-tools/bootstrap-nexus` | 7 files (Docker, Nginx, docs) | `d28c6bb` | Configuration syntax verified |
| **Traefik Proxy Infra** | `Docker/traefik` | `~/Developer/infra/traefik` | 2 files (`docker-compose.yml`, `toml`) | `41119fd` | `acme.json` removed and quarantined |
| **FPT Ingenico Configs** | `Fpt/Ingenico` | `~/Developer/infra/fpt-ingenico` | 4 files (`detekt.yml`, patches, puml) | `14f5960` | Format integrity verified |
| **Mobile Specs & Docs** | `tdt/poems-mobile3-docs` | `~/Developer/mobile/poems-mobile3-docs` | 146 Markdown and diagram files | `0edc261` | 100% file count & size verified |
| **Android Native App** | `tdt/poems-mobile3-android` | `~/Developer/mobile/poems-mobile3-android` | 1,316+ source and config files | `ee40e8e` | Core manifests, flavors & code verified |
| **Sensitive TLS Keys** | `Docker/traefik/acme.json` | `~/Developer/sensitive-quarantine/traefik/` | 1 private key/cert bundle | N/A (Quarantine) | Mode `0600` / parent `0700` verified |
| **Python Repositories** | `tdt/tdt-python-source-package/` | `~/Developer/<repo>/` (16 repos) | 16 repositories audited | Existing Git HEAD | Preserved local authority; zero overwrites |

---

## Filter Enforcement & Bloat Prevention

In accordance with `Requirement: Strict Filter Ruleset SHALL Exclude Binary Frameworks and Build Caches`:
- **Pruned from Qi Bridge:** Compiled binary `qi-gen-proxy` (9.07 MB) was excluded; only Go source code and manifests were hydrated.
- **Pruned from Traefik:** TLS state `acme.json` was excluded from the general repo and routed to `sensitive-quarantine`.
- **Pruned from Mobile Trees:** Zero precompiled `.xcframework`, `Pods/`, `.gradle/`, `build/`, `DerivedData/`, or `.apk` files were transferred to local disk.
- **Out of Scope Folders:** 18 personal/financial folders, binary ML model weights (`YoloV8`), and cold backup archives (`git-bundles/`, `git-remotes/`) remained strictly read-only in Google Drive.

---

## Credential Containment Proof

- Path: `/Users/androidteam/Developer/sensitive-quarantine/traefik/acme.json`
- Directory permissions: `drwx------` (`0700`)
- File permissions: `-rw-------` (`0600`)
- Verification: File exists exclusively in quarantine; zero private keys or credential files exist in `~/Developer/infra/traefik/`.

---

## Python Services Delta Reconciliation

All 16 Python services in `tdt/tdt-python-source-package/` were matched against active local checkouts. Local checkouts (`~/Developer/agent-core`, `tdt-core`, `ai-review`, etc.) were maintained as the authoritative versions, preventing any loss of newer uncommitted local edits or Git history.
Detailed report: `evidence/python-repos-delta-audit.md`.
