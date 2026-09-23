# Tasks

## 1. Pre-flight Checks & Target Destination Preparation

- [ ] 1.1 Verify APFS storage capacity on `/Users/androidteam/Developer` (assert >30 GB free space).
- [ ] 1.2 Verify or scaffold target directories: `~/Developer/mcp-router-backup-20260722`, `~/Developer/docs`, `~/Developer/lending-miniapp-docs`, `~/Developer/study-examples/investing-for-programmers`, and `~/Developer/scripts`.
- [ ] 1.3 Verify `~/Developer/content-migration-manifests/` directory exists and is prepared for new manifest artifacts.

## 2. Cocoa Hydration & Atomic Migration

- [ ] 2.1 Trigger Cocoa hydration and migrate `Documents/Codex/2026-07-22/try/work/mcp-router-src` (393 files) to `~/Developer/mcp-router-backup-20260722`, generating `manifest-mcp-router-backup-20260722.json`.
- [ ] 2.2 Migrate `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md` to `~/Developer/docs/PRODUCTION_SECRETS_SECURITY_GUIDE.md`, generating `manifest-production-secrets-guide.json`.
- [ ] 2.3 Trigger Cocoa hydration and migrate `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe` (14 files) to `~/Developer/lending-miniapp-docs`, generating `manifest-lending-miniapp-docs.json`.
- [ ] 2.4 Trigger Cocoa hydration and migrate `books/ai/2025/Investing for Programmers/investing-for-programmers-main` (30 files) to `~/Developer/study-examples/investing-for-programmers`, generating `manifest-investing-for-programmers.json`.
- [ ] 2.5 Migrate `Downloads/setup-fable-5.sh` to `~/Developer/scripts/setup-fable-5.sh`, generating `manifest-setup-fable-5.json`.

## 3. Read-Back Verification & Destination Audit

- [ ] 3.1 Execute `--verify-only` across all 5 generated manifests asserting 100% SHA-256 digest and byte-count equality with 0 failures.
- [ ] 3.2 Audit target directories to verify 1:1 internal directory hierarchy and that no `.venv`, `.git`, or build caches were copied.
- [ ] 3.3 Confirm active repository `~/Developer/mcp-router` remains completely unaffected.

## 4. Controlled Cloud Purge & Cleanup

- [ ] 4.1 Execute fail-closed bounded deletion of `Documents/Codex/2026-07-22/try/work/mcp-router-src` from iCloud and bottom-up prune empty parent directories up to `Codex/`.
- [ ] 4.2 Delete `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md` from iCloud.
- [ ] 4.3 Execute fail-closed bounded deletion of `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe` from iCloud and prune empty parent directory `Desktop - Cuong’s iMac - 1`.
- [ ] 4.4 Execute fail-closed bounded deletion of `books/.../investing-for-programmers-main` from iCloud, verifying parent PDF/ePub book files remain intact.
- [ ] 4.5 Delete `Downloads/setup-fable-5.sh` from iCloud.
- [ ] 4.6 Verify that personal directories (`SHB/`, `TDT/`, `candidate/`, `che/`, `family/`, `fcfc/`, etc.) remain completely untouched.

## 5. Closure & Specification Synchronization

- [ ] 5.1 Run full post-purge verification confirming 0 code or config files remain stranded in iCloud Drive.
- [ ] 5.2 Validate and archive change `migrate-residual-icloud-developer-assets` in `openspec-store`.
