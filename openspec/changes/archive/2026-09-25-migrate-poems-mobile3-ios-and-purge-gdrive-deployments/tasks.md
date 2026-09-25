# Tasks: Migrate poems-mobile3-ios and Purge Google Drive Stale Deployments

## Phase 1: Filter Ruleset & Staging Configuration

- [x] 1.1 Create rclone filter configuration artifact `resources/ios-source-filter.txt`
- [x] 1.2 Verify filter excludes `Pods/`, `Framework/`, `*.xcframework/`, `DerivedData/`, and includes `.swift`, `.xcodeproj`, Fastlane, and configs
- [x] 1.3 Ensure target directory `~/Developer/mobile/poems-mobile3-ios/` exists

## Phase 2: iOS Codebase Ingestion & Integrity Assertion

- [x] 2.1 Ingest `tdt/poems-mobile3-ios` from Google Drive to `~/Developer/mobile/poems-mobile3-ios/` using filter ruleset
- [x] 2.2 Verify zero `Pods/` or `*.xcframework/` directories were transferred
- [x] 2.3 Record transferred file count and payload size in `evidence/ios-ingestion-audit.json`

## Phase 3: Google Drive Stale Deployment Purge

- [x] 3.1 Verify production services continue running locally under macOS LaunchAgent
- [x] 3.2 Purge obsolete directory `tdt/deployments/ai-review` from Google Drive
- [x] 3.3 Purge obsolete directory `tdt/deployments/webhook-receiver` from Google Drive
- [x] 3.4 Purge obsolete directory `tdt/deployments/bifrost` from Google Drive
- [x] 3.5 Recheck Google Drive `tdt/deployments/` and record evidence in `evidence/gdrive-deployments-purge.md`

## Phase 4: Git Baseline Initialization & Syntax Check

- [x] 4.1 Initialize clean Git repository (`git init -b main`) in `~/Developer/mobile/poems-mobile3-ios/`
- [x] 4.2 Create `.gitignore` ignoring `Pods/`, `build/`, `DerivedData/`, `*.xcuserstate`, `.DS_Store`
- [x] 4.3 Commit initial baseline (`feat: initial baseline from Google Drive iOS migration`)
- [x] 4.4 Validate Swift file syntax with `swift -version` and linting rules

## Phase 5: OpenSpec Archival & Verification

- [x] 5.1 Run strict validation on change `migrate-poems-mobile3-ios-and-purge-gdrive-deployments`
- [x] 5.2 Archive change in `openspec-store` and synchronize canonical specs
- [x] 5.3 Commit store changes to Git repository
