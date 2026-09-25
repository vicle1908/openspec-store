# Design: Migrate poems-mobile3-ios and Purge Google Drive Stale Deployments

## Architectural Context

This design covers:
1. Selective migration of the native iOS repository `tdt/poems-mobile3-ios` to `~/Developer/mobile/poems-mobile3-ios/` with strict exclusion of third-party frameworks and CocoaPods caches.
2. Bounded deletion of dead deployment bundles (`tdt/deployments/ai-review/`, `tdt/deployments/webhook-receiver/`, `tdt/deployments/bifrost/`) from Google Drive.

```text
Google Drive (gdrive-tdt:)
├── tdt/poems-mobile3-ios/
│   ├── Source & Manifests (Swift, xcodeproj, tests) ──[rclone copy with filter]──> ~/Developer/mobile/poems-mobile3-ios/
│   └── Frameworks & Caches (Pods, *.xcframework)   ──[ignored / dropped]
└── tdt/deployments/
    ├── ai-review/         ──[rclone purge]──> (Purged from Drive)
    ├── webhook-receiver/  ──[rclone purge]──> (Purged from Drive)
    └── bifrost/           ──[rclone purge]──> (Purged from Drive)
```

## Technical Decisions

### Decision 1: Dedicated Swift/iOS Filter Configuration
- **Rule:** Whitelist Swift source (`*.swift`), Xcode project descriptors (`*.pbxproj`, `*.xcworkspacedata`), Ruby/CocoaPods specs (`Gemfile`, `Gemfile.lock`, `Podfile`), Fastlane configs, and documentation.
- **Rule:** Blacklist `Pods/**`, `Framework/**`, `*.xcframework/**`, `DerivedData/**`, `.gitnexus/**`, `*.ipa`, `*.zip`.
- **Target Location:** `~/Developer/mobile/poems-mobile3-ios/`.

### Decision 2: Bounded Deletion of Obsolete Drive Deployments
- **Context:** Production services (`ai-review`, `webhook-receiver`) run locally under macOS LaunchAgent (standardized in archived change `2026-09-05-migrate-ai-review-deployment`).
- **Policy:** The directories in Google Drive (`tdt/deployments/ai-review/`, `tdt/deployments/webhook-receiver/`, `tdt/deployments/bifrost/`) contain dead runtime logs, virtualenvs, and wheel artifacts. Purging them reclaims cloud storage and removes split-brain ambiguity.

### Decision 3: Local Git Baseline & Syntax Check
- **Action:** Initialize Git repository (`git init -b main`), write standard `.gitignore` (ignoring `Pods/`, `build/`, `DerivedData/`), and commit the initial baseline.
- **Action:** Validate Swift file syntax with `swift -version` and linting rules.
