# Proposal: Migrate poems-mobile3-ios and Purge Google Drive Stale Deployments

## Why

During the initial Google Drive migration (`migrate-gdrive-source-code-to-local`), the native iOS codebase `tdt/poems-mobile3-ios` was skipped due to API listing timeouts caused by heavy precompiled dependency trees (`Pods/`, `*.xcframework/`). Additionally, obsolete runtime deployment bundles (`tdt/deployments/ai-review` and `tdt/deployments/webhook-receiver`) containing heavy virtualenvs, wheels, and runtime logs remain on Google Drive. To complete clean-break migration, `poems-mobile3-ios` must be ingested to `~/Developer/mobile/poems-mobile3-ios/` with strict exclusion of build artifacts, and the stale cloud deployment folders must be purged to reclaim cloud storage and eliminate split-brain confusion.

## What Changes

1. **Ingest Native iOS Repository:**
   - Migrate `tdt/poems-mobile3-ios` from Google Drive to `~/Developer/mobile/poems-mobile3-ios/`.
   - Apply strict filtering: whitelist Swift sources (`.swift`), Xcode project files (`.xcodeproj`, `.xcworkspace`), tests (`Pmobile3Tests`, `Pmobile3UITests`), `LocalPackages`, `Gemfile`, and `fastlane/`.
   - Blacklist and prune `Pods/`, `Framework/`, `ENETSLib.xcframework/`, and `ThreeDS_SDK.xcframework/`.
   - Initialize a clean local Git baseline (`git init -b main`) and commit the ingested code.
2. **Purge Stale Google Drive Deployments:**
   - Safely purge obsolete deployment directories on Google Drive: `tdt/deployments/ai-review/`, `tdt/deployments/webhook-receiver/`, and `tdt/deployments/bifrost/`.
   - Confirm active production deployments continue running unhindered on local macOS LaunchAgent.
3. **Verify Integrity & OpenSpec Governance:**
   - Run syntax and project structure validation.
   - Record audit evidence in `evidence/`.
   - Complete and archive the change in `openspec-store`.

## Scope Boundaries

- **In Scope:**
  - `tdt/poems-mobile3-ios/` source and configuration migration.
  - `tdt/deployments/ai-review/`, `tdt/deployments/webhook-receiver/`, and `tdt/deployments/bifrost/` cloud cleanup.
- **Out of Scope (Protected):**
  - All 18 personal/financial document folders in Google Drive.
  - Machine learning weights (`YoloV8`) and cold Git archives (`git-bundles/`, `git-remotes/`).
  - Active local production services in `~/Developer/`.
