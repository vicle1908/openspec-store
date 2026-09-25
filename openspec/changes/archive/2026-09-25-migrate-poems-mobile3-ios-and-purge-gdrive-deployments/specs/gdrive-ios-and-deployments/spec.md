# Specification: Ingest iOS Source and Purge Obsolete Cloud Deployments

## Purpose

Define normative requirements and acceptance criteria for ingesting the unmigrated native iOS application codebase from Google Drive (`tdt/poems-mobile3-ios`) to local workspace storage, while purging obsolete, non-authoritative deployment bundles on Google Drive.

## ADDED Requirements

### Requirement: iOS Codebase Ingestion SHALL Exclude Third-Party Frameworks and CocoaPods

The migration toolchain SHALL ingest `tdt/poems-mobile3-ios` into `~/Developer/mobile/poems-mobile3-ios/` using explicit filter rules. The transfer engine SHALL strictly exclude precompiled frameworks (`ENETSLib.xcframework/**`, `ThreeDS_SDK.xcframework/**`, `Framework/**`), CocoaPods dependency trees (`Pods/**`), and build output caches (`DerivedData/**`). Only Swift sources, tests, Xcode project files, Fastlane configurations, and manifests SHALL be transferred to local disk.

#### Scenario: iOS repository ingestion
- **WHEN** file transfer from `tdt/poems-mobile3-ios` executes
- **THEN** Swift sources (`.swift`), tests (`Pmobile3Tests/`, `Pmobile3UITests/`), and project manifests (`Pmobile3.xcodeproj/project.pbxproj`) are created locally, and zero `.xcframework` or `Pods/` files are written.

### Requirement: Obsolete Cloud Deployments SHALL Be Purged from Google Drive

The migration process SHALL permanently purge dead runtime deployment directories on Google Drive: `tdt/deployments/ai-review/`, `tdt/deployments/webhook-receiver/`, and `tdt/deployments/bifrost/`. The engine SHALL NOT delete or modify active local LaunchAgent configurations or local application checkouts under `~/Developer/`.

#### Scenario: Cloud deployment directory purge
- **WHEN** the deployment purge task runs
- **THEN** `rclone purge` executes against `gdrive-tdt:tdt/deployments/ai-review`, `gdrive-tdt:tdt/deployments/webhook-receiver`, and `gdrive-tdt:tdt/deployments/bifrost/`, and post-purge verification confirms their absence on Google Drive.

### Requirement: Ingested iOS Project SHALL Establish Local Git Baseline

Following ingestion, the local `~/Developer/mobile/poems-mobile3-ios/` directory SHALL be initialized as a standalone Git repository (`git init -b main`). The repository SHALL include a `.gitignore` ignoring `Pods/`, `build/`, and `DerivedData/`, and SHALL record an initial commit of the ingested source code.

#### Scenario: Git baseline initialization
- **WHEN** source transfer and file validation complete
- **THEN** `git status --porcelain` in `~/Developer/mobile/poems-mobile3-ios/` reports a clean working tree after the initial baseline commit.
