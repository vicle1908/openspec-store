# Tasks: Migrate Google Drive Source Code to Local Workspace

## Phase 1: Preparation & Dry-Run Auditing

- [x] 1.1 Generate rclone filter configuration artifact `resources/gdrive-source-filter.txt` containing explicit whitelists and blacklists
- [x] 1.2 Run hierarchical dry-run discovery on mobile project roots (`tdt/poems-mobile3-android`, `tdt/poems-mobile3-ios`) to compute candidate file counts
- [x] 1.3 Run dry-run discovery on Go proxy and ops tools (`tdt/qi-bridge`, `tdt/tdt-tools`, `tdt/bootstrap-nexus-for-mobile`, `Docker/traefik`, `Fpt/Ingenico`)
- [x] 1.4 Validate pre-flight payload budget assertion: confirm eligible transfer size is < 400 MB and zero `.xcframework` or `Pods/` leak into candidate manifests
- [x] 1.5 Record pre-flight dry-run manifest in `evidence/preflight-dryrun-manifest.json`

## Phase 2: Sensitive Credential Quarantining

- [x] 2.1 Create destination quarantine directories under `~/Developer/sensitive-quarantine/` with `0700` POSIX permissions
- [x] 2.2 Retrieve `Docker/traefik/acme.json` from Google Drive and place into `~/Developer/sensitive-quarantine/traefik/acme.json` with `0600` permissions
- [x] 2.3 Scan candidate mobile roots for `.jks` or `.keystore` files; isolate any signing keystores into `~/Developer/sensitive-quarantine/mobile-keystores/` (`0700`/`0600`)
- [x] 2.4 Verify zero credentials, private keys, or `.env` secrets remain in general staging manifests

## Phase 3: Selective Source Ingestion & Integrity Verification

- [x] 3.1 Ingest `tdt/poems-mobile3-android` into `~/Developer/mobile/poems-mobile3-android/` applying filter ruleset
- [x] 3.2 Ingest `tdt/poems-mobile3-docs` into `~/Developer/mobile/poems-mobile3-docs/` applying filter ruleset
- [x] 3.3 Ingest `tdt/qi-bridge` into `~/Developer/qi-bridge/` (excluding compiled `qi-gen-proxy` binary)
- [x] 3.4 Ingest `tdt/tdt-tools` into `~/Developer/ops-tools/tdt-tools/` and set `0755` executable permissions on scripts
- [x] 3.5 Ingest `tdt/bootstrap-nexus-for-mobile` into `~/Developer/ops-tools/bootstrap-nexus/`
- [x] 3.6 Ingest `Docker/traefik` into `~/Developer/infra/traefik/` (excluding `acme.json`)
- [x] 3.7 Ingest `Fpt/Ingenico` configs into `~/Developer/infra/fpt-ingenico/`
- [x] 3.8 Generate post-transfer local SHA-256 manifest and verify 100% byte count match against remote Drive object sizes
- [x] 3.9 Run syntax verification: execute `go vet ./...` in `~/Developer/qi-bridge/` and `python3 -m py_compile` on ops scripts

## Phase 4: Python Services Delta Reconciliation

- [x] 4.1 Perform two-way diff comparison between remote `tdt/tdt-python-source-package/` and local `~/Developer/` checkouts for all 16 Python services
- [x] 4.2 Assert that existing local files are protected from blind overwrites
- [x] 4.3 Record reconciliation findings in `evidence/python-repos-delta-audit.md`

## Phase 5: Workspace Integration & Git Baseline

- [x] 5.1 Initialize clean Git baselines (`git init -b main`) for newly ingested standalone projects lacking local `.git`
- [x] 5.2 Generate initial `.gitignore` files for mobile and Go projects to prevent future tracking of local build caches
- [x] 5.3 Register newly ingested repositories in `~/Developer/AGENTS.md`
- [x] 5.4 Run GitNexus index analysis on `qi-bridge` and newly created standalone repositories
- [x] 5.5 Update and record final migration acceptance evidence in `evidence/acceptance-summary.md`
