## Why

The local development machine cannot currently build either mobile app. There is **no JDK installed** (`/usr/bin/java` is a stub; `java_home` finds nothing), so the Android Gradle build cannot run at all, and **only the Xcode Command Line Tools are present** (no full Xcode, `xcodebuild` fails), so the iOS app cannot be built or archived. On top of that, the toolchain versions the repos pin are well behind current stable releases (Android: AGP 8.7.3 / Gradle 8.9 / Kotlin 1.9.23; iOS: Swift 5.0 mode), and the prerequisites that exist are unpinned and undocumented (`ANDROID_HOME` is unset, CocoaPods is missing despite the iOS `Gemfile` declaring it). We need a documented, reproducible toolchain setup so any engineer or agent can build, test, and release POEMS Mobile 3 on macOS, and a safe, staged path toward current-stable versions.

## What Changes

- Establish a documented, pinned **native build toolchain baseline** for both mobile repos: exact JDK, Android SDK, Gradle/AGP/Kotlin, Xcode, Swift, and CocoaPods/SPM versions, plus the environment variables and verification commands that prove the setup works.
- Define **Android toolchain setup**: install a pinned **JDK 21 LTS** as the runtime/toolchain baseline (the JDK that *runs* Gradle), while keeping the app's Java/Kotlin **bytecode target at 17** for compatibility; wire `ANDROID_HOME`/`ANDROID_SDK_ROOT` to the existing SDK at `~/Library/Android/sdk`, adopt Gradle JVM toolchain pinning (foojay resolver) so builds don't depend on an ambient JDK, and resolve the root `build.gradle` version inconsistency (plugins block declares AGP 7.4.2 / Kotlin 1.8.0 while buildscript uses AGP 8.7.3 / Kotlin 1.9.23).
- Support building/running on the **latest JDK** (25 LTS, up to the Gradle-supported JVM 26) via the Gradle JVM toolchain, without changing the bytecode target — so engineers on a newer system JDK are not blocked. JDK 21 is the *minimum* and the pinned default; JDK 17 is the *floor* the bytecode targets, not the runtime baseline (Oracle JDK 17 premier support ends Sept 2026).
- Define **iOS toolchain setup**: install full Xcode (current stable, Swift 6 toolchain) over the existing Command Line Tools, install CocoaPods via Bundler (the `Gemfile` already declares it) or confirm SPM-only, and document a single deployment-target policy (currently mixed across 14.1/14.4/14.5/15.0).
- Define a **staged version-upgrade policy** toward current stable rather than a big-bang jump: Phase A makes the *current* pinned stack buildable on a clean machine (no version bumps), Phase B performs incremental, verified upgrades (Kotlin 1.9 → 2.x K2, Gradle 8.9 → 8.14, then AGP/Gradle 9.x and Kotlin 2.3/2.4). **BREAKING** version bumps are isolated to Phase B and gated on a green build + test run.
- Add verification scripts/commands so toolchain health can be checked in-session and in CI.

## Capabilities

### New Capabilities
- `mobile-toolchain-baseline`: cross-cutting requirements for a documented, pinned, verifiable native toolchain — the canonical version matrix, required environment variables (sourced from `~/.tdt`), and the verification commands that must pass before a machine is considered build-ready.
- `android-build-toolchain`: requirements for the Android build environment — JDK provisioning and pinning, Android SDK/NDK wiring, Gradle/AGP/Kotlin version policy, the JVM toolchain strategy, and the staged upgrade path.
- `ios-build-toolchain`: requirements for the iOS build environment — full Xcode and Swift toolchain provisioning, CocoaPods-vs-SPM dependency management, Ruby/Bundler setup for Fastlane + CocoaPods, and the deployment-target policy.

### Modified Capabilities
<!-- No existing OpenSpec specs govern mobile build tooling today; all capabilities are new. -->

## Impact

- **Repos:** `poems-mobile3-android` (root `build.gradle`, `gradle.properties`, `gradle/wrapper/gradle-wrapper.properties`, version catalog, `app/build.gradle` toolchain blocks) and `poems-mobile3-ios` (`Pmobile3.xcodeproj`, `Gemfile`/`Gemfile.lock`, Podfile if CocoaPods is used). Phase A changes are additive/config-only; Phase B changes are version bumps gated on verification.
- **Developer environment:** new local prerequisites — a pinned JDK (Temurin 21 LTS baseline; latest LTS 25 supported via toolchain), full Xcode, CocoaPods, and a modern Ruby for Bundler; new exported env vars (`JAVA_HOME`, `ANDROID_HOME`, `ANDROID_SDK_ROOT`) managed via `~/.tdt`.
- **CI/release:** Fastlane lanes and any CI runners must use the same pinned versions; the verification commands become the contract for "build-ready."
- **Non-goals:** not changing app source code, architecture, or runtime dependencies; not altering the intentional Java/Kotlin 11 target of the `PoemsUIComponents` Android module; not migrating CocoaPods → SPM (only documenting which is authoritative); not setting up Android Studio / Xcode IDE preferences beyond what builds require; not performing the Phase B upgrades within this change's setup scope unless explicitly scheduled.
