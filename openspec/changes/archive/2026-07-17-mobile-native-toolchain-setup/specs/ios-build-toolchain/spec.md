## ADDED Requirements

### Requirement: Full Xcode and Swift toolchain provisioning
The iOS build SHALL run against a full Xcode installation, not just the Command Line Tools. The machine currently has only `/Library/Developer/CommandLineTools` (so `xcodebuild` fails); setup MUST install a current-stable Xcode and select it via `xcode-select`. The Swift toolchain version MUST be recorded in the version matrix.

#### Scenario: Xcode is installed and selected
- **WHEN** `xcode-select -p` is run after setup
- **THEN** it points at a full `Xcode.app` developer directory (not `CommandLineTools`)
- **AND** `xcodebuild -version` reports the pinned Xcode version

#### Scenario: iOS project builds from the command line
- **WHEN** `xcodebuild` is run against the `Pmobile3` scheme
- **THEN** the project configures and compiles without a missing-toolchain error

### Requirement: Swift Package Manager is the authoritative dependency strategy
The iOS repository SHALL use Swift Package Manager (SPM) as its single authoritative dependency manager, and CocoaPods MUST NOT be reintroduced. This reflects the verified repo state: the Xcode project declares 29 `XCRemoteSwiftPackageReference` entries (e.g. Alamofire, firebase-ios-sdk, MoEngage-iOS-SDK, GoogleSignIn-iOS) with 56 pinned packages in `Pmobile3.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved`, plus the local package `LocalPackages/PoemsUIComponents`; there is no `Podfile`, no `Podfile.lock`, and no `Pods/Manifest.lock`, and the `Pods/` directory holds only a 0-byte `.nosync` placeholder. SPM resolution MUST be driven by the project's committed `Package.resolved` so dependency versions are reproducible.

#### Scenario: SPM is the documented source of truth
- **WHEN** an engineer or agent looks up how iOS dependencies are managed
- **THEN** the documentation states SPM is authoritative and CocoaPods is not used
- **AND** the toolchain matrix records SPM (not CocoaPods) as the dependency manager

#### Scenario: Dependencies resolve reproducibly from Package.resolved
- **WHEN** the project is opened or built after a clean checkout
- **THEN** Xcode/`xcodebuild` resolves packages from the committed `Package.resolved` (29 remote references, plus the local `PoemsUIComponents` package)
- **AND** no `pod install` step is required to produce a buildable workspace

#### Scenario: Vestigial CocoaPods artifacts are removed, not provisioned
- **WHEN** the stale CocoaPods remnants are evaluated
- **THEN** the empty `Pods/` directory and the `cocoapods` (and deprecated `xcode-install`) `Gemfile` entries are flagged for removal
- **AND** setup does NOT run `pod install` or recreate a `Podfile`

### Requirement: Ruby and Bundler setup for Fastlane
The iOS tooling SHALL use a Ruby managed for the project rather than the macOS system Ruby. The system Ruby is 2.6.10 (2022) while the `Gemfile` targets Ruby 3.0.0; setup MUST provide a compatible Ruby and install gems via Bundler so Fastlane runs reproducibly. Because the project is SPM-authoritative, the gem set is needed for Fastlane (release automation) only — not for dependency resolution.

#### Scenario: Bundler installs the gem set
- **WHEN** `bundle install` is run in the iOS repo
- **THEN** it succeeds against a Ruby compatible with the `Gemfile`
- **AND** `bundle exec fastlane` resolves to the pinned gem versions

#### Scenario: CocoaPods gem is not required for the build
- **WHEN** the iOS app is built or its dependencies are resolved
- **THEN** no `bundle exec pod` step is involved (SPM handles dependencies)
- **AND** the `cocoapods` Gemfile entry is treated as removable per the SPM policy

### Requirement: Single deployment-target policy
The iOS project SHALL define one documented minimum deployment target, and that minimum MUST be **iOS 15.0**. The project currently mixes `IPHONEOS_DEPLOYMENT_TARGET` values (14.1, 14.4, 14.5, 15.0) across targets; iOS 15.0 is chosen because it is a hard floor — the linked local Swift package `LocalPackages/PoemsUIComponents` declares `platforms: [.iOS(.v15)]`, so the app cannot deploy below 15.0 — and because 15.0 is already the dominant value (18 of 34 build-config lines). Setup MUST document the 15.0 minimum and flag the lower values (14.1, 14.4, 14.5) for alignment.

#### Scenario: Deployment target is documented and consistent
- **WHEN** the deployment-target policy is applied
- **THEN** the toolchain matrix documents the minimum iOS version as 15.0
- **AND** the targets still set below 15.0 (14.1, 14.4, 14.5) are listed for reconciliation

#### Scenario: Minimum is not set below the SPM package floor
- **WHEN** a deployment target is chosen or changed
- **THEN** it is never set below iOS 15.0
- **AND** the rationale references the `PoemsUIComponents` `.iOS(.v15)` platform requirement
