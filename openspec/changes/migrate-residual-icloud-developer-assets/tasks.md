# Tasks: Migrate Residual iCloud Developer Assets

## 1. Pre-flight Checks & Target Destination Preparation

- [x] 1.1 Verify APFS storage capacity on `/Users/androidteam/Developer` (assert >30 GB free space: verified 40 GiB free).
- [x] 1.2 Verify or scaffold target directories: `~/Developer/mcp-router-backup-20260722`, `~/Developer/docs`, `~/Developer/lending-miniapp-docs`, `~/Developer/study-examples/investing-for-programmers`, `~/Developer/study-examples/docker-in-a-month-of-lunches`, `~/Developer/study-examples/kotlin-coroutine-confidence`, and `~/Developer/scripts`.
- [x] 1.3 Verify `~/Developer/content-migration-manifests/` directory exists and is prepared for new manifest artifacts.

## 2. Cocoa Hydration & Atomic Migration

- [ ] 2.1 Trigger Cocoa hydration and migrate `Documents/Codex/2026-07-22/try/work/mcp-router-src` (393 files, 391 dataless) to `~/Developer/mcp-router-backup-20260722`, generating `manifest-mcp-router-backup-20260722.json`.
- [ ] 2.2 Migrate `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md` (dataless, 5.5 KB) to `~/Developer/docs/PRODUCTION_SECRETS_SECURITY_GUIDE.md`, generating `manifest-production-secrets-guide.json`.
- [ ] 2.3 Trigger Cocoa hydration and migrate `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe` (14 files, 12 dataless) to `~/Developer/lending-miniapp-docs`, generating `manifest-lending-miniapp-docs.json`.
- [x] 2.4 Migrate `books/ai/2025/Investing for Programmers/investing-for-programmers-main` (59 files) to `~/Developer/study-examples/investing-for-programmers`, preserving companion notebooks and scripts.
- [x] 2.5 Quarantine `Downloads/setup-fable-5.sh` (6.3 KB script with embedded API key) to `~/Developer/sensitive-quarantine/downloads/setup-fable-5.sh` (`0600`).
- [x] 2.6 Extract and migrate Docker study code (`books/.../code.zip`) to `~/Developer/study-examples/docker-in-a-month-of-lunches` (3,932 files verified).
- [x] 2.7 Extract and migrate Kotlin coroutines study code (`books/.../sckotlin-code.zip`) to `~/Developer/study-examples/kotlin-coroutine-confidence` (1,535 files verified).
- [x] 2.8 Migrate and quarantine GHTK credentials and configurations: `ghtk/soft/charlesKey.rtf` (`0600`) and `ghtk/zshrc/.zshrc` (`0600` in quarantine and `~/Developer/ghtk-scripts/zshrc/.zshrc`).
- [x] 2.9 Migrate Ascend localization configs and MM config zip (`localized_strings_ph.json`, `LoyaltyApp/config`, `config-20201218T045722Z-001.zip`) to `~/Developer/ascend-configs`.

## 3. Read-Back Verification & Destination Audit

- [ ] 3.1 Execute `--verify-only` across all generated manifests asserting 100% SHA-256 digest and byte-count equality with 0 failures.
- [x] 3.2 Audit target directories to verify 1:1 internal directory hierarchy and that no `.venv`, `.git`, or build caches were copied.
- [x] 3.3 Confirm active repository `~/Developer/mcp-router` remains completely unaffected.

## 4. Controlled Cloud Purge & Cleanup

- [ ] 4.1 Execute fail-closed bounded deletion of `Documents/Codex/2026-07-22/try/work/mcp-router-src` from iCloud and bottom-up prune empty parent directories up to `Codex/`.
- [ ] 4.2 Delete `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md` from iCloud.
- [ ] 4.3 Execute fail-closed bounded deletion of `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe` from iCloud and prune empty parent directory `Desktop - Cuong’s iMac - 1`.
- [x] 4.4 Execute fail-closed bounded deletion of `books/.../investing-for-programmers-main` and companion zip from iCloud, verifying parent PDF/ePub book files remain intact.
- [x] 4.5 Delete `Downloads/setup-fable-5.sh` from iCloud after quarantine verification.
- [x] 4.6 Purge extracted study code archives (`code.zip`, `sckotlin-code.zip`) from iCloud `books/`.
- [x] 4.7 Purge `ghtk/soft/` and `ghtk/zshrc/` from iCloud after verified quarantine copy.
- [x] 4.8 Verify that personal directories (`SHB/`, `TDT/`, `candidate/`, `che/`, `family/`, `fcfc/`, etc.) remain completely untouched.

## 5. Closure & Specification Synchronization

- [x] 5.1 Run full post-purge verification confirming 0 code or config files remain stranded in iCloud Drive user directories (excluding offline HTML docs).
- [ ] 5.2 Validate and archive change `migrate-residual-icloud-developer-assets` in `openspec-store` once remaining Documents/Desktop items hydrate and complete migration.
