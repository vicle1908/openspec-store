## Context

POEMS Mobile 3 ships as two native apps — `poems-mobile3-android` (Kotlin/Gradle) and `poems-mobile3-ios` (Swift/Xcode). A system audit on 2026-06-13 (macOS arm64) found the local machine **cannot build either app**:

- **No JDK at all.** `/usr/bin/java` is the macOS stub and `/usr/libexec/java_home -V` finds nothing. Gradle therefore cannot run.
- **Android SDK present but unwired.** `~/Library/Android/sdk` exists (build-tools 36.1.0/37.0.0, platforms android-36.1/37.0, ndk 29.0.14206865, cmdline-tools `latest`), but `ANDROID_HOME`/`ANDROID_SDK_ROOT` are unset and Android Studio is not installed.
- **iOS has only Command Line Tools.** `xcode-select -p` → `/Library/Developer/CommandLineTools`; `xcodebuild` fails ("requires Xcode"). Swift 6.3.2 ships with the CLT. CocoaPods is missing (`pod` not found) though the `Gemfile` declares it; system Ruby is 2.6.10.

Pinned versions also lag current stable. Android: Gradle 8.9, AGP 8.7.3, Kotlin 1.9.23, Java/Kotlin target 17 (the `PoemsUIComponents` module intentionally stays on 11). iOS: `SWIFT_VERSION = 5.0`, mixed deployment targets (14.1/14.4/14.5/15.0). The root Android `build.gradle` is internally inconsistent: its `plugins {}` block declares `com.android.library` 7.4.2 and `kotlin.android` 1.8.0 (`apply false`) while `buildscript {}` uses AGP 8.7.3 and Kotlin 1.9.23.

Researched current-stable (2026-06-13, authoritative sources): Kotlin **2.4.0** (2026-06-03); AGP **9.2.x** (requires Gradle 9.4.1, JDK 17, SDK Build Tools 36.0.0, max API 37); Gradle 9.x runs on JVM 17–26 and is tested with Kotlin 2.0.0–2.3.20.

This is a developer-environment + build-config change. It touches the two mobile repos' build files and the local toolchain. It does **not** touch app source, Python services, or `tdt_core` — so the standard "use `tdt_core.clients` factories" rule does not apply here (no Jira/GitLab API calls are made by this change).

## Goals / Non-Goals

**Goals:**
- A documented, **pinned** toolchain matrix that makes a clean macOS machine build-ready for both apps.
- Android: a provisioned **JDK 21 LTS** as the runtime/toolchain baseline (with the latest LTS 25 supported via toolchain), SDK env vars wired to the existing SDK, and a **Gradle JVM toolchain** so builds stop depending on an ambient JDK. The Java/Kotlin **bytecode target stays at 17** (app compatibility) — the runtime JDK and the compile target are deliberately decoupled.
- iOS: full Xcode + Swift toolchain, a clear CocoaPods-vs-SPM decision, and Bundler-managed Ruby for Fastlane/CocoaPods.
- A **staged** upgrade path toward current stable, with every bump gated on a green build + test.
- Verification commands that double as the "build-ready" contract for engineers, agents, and CI.

**Non-Goals:**
- No app source, architecture, or runtime-dependency changes.
- No change to the intentional Java/Kotlin 11 target of `PoemsUIComponents`.
- No CocoaPods → SPM migration (only documenting which is authoritative).
- No IDE preference setup beyond what builds require.
- Phase B version bumps are **planned** here but executed only when explicitly scheduled; this change's setup scope is Phase A (make the current pinned stack buildable).

## Decisions

**Decision 1 — JDK distribution: Eclipse Temurin 21 (LTS) baseline, pinned; latest LTS (25) supported via toolchain.**
The machine needs a real JDK to *run* Gradle. We pin **JDK 21 LTS** as the baseline rather than 17 for three reasons: (a) Oracle JDK 17 premier support ends Sept 2026 and its free-license updates already moved to the OTN license, so 17 is a poor forward-looking baseline; (b) Gradle 8.9 runs fine on JDK 21 and Gradle 9.x runs on JVM 17–26, so 21 is comfortably inside the supported runtime window through Phase B; (c) AGP only constrains the *bytecode/compile* JDK (17), **not** the JDK that runs Gradle — these are separate concerns. Engineers already on a newer JDK (25 LTS, or up to JVM 26 that Gradle 9.4 supports) are not blocked: the Gradle JVM toolchain selects the correct compile JDK regardless of the launcher JDK. Temurin is vendor-neutral and Homebrew-installable (`brew install --cask temurin@21`). *Alternatives:* JDK 17 baseline (rejected — nearing end of free premier support, no upside since the compile target is independent); Android Studio's bundled JBR (rejected as canonical CLI/CI JDK — couples builds to an IDE that isn't installed); jumping straight to non-LTS 26 (rejected — not an LTS, only a 6-month support window). `JAVA_HOME` points at the Temurin 21 baseline and the Gradle build declares a JVM toolchain so the *compile* JDK is reproducible independent of the launcher JDK.

**Decision 2 — Gradle JVM toolchain + foojay resolver, decoupling launcher JDK from compile JDK.**
Pinning the toolchain (`kotlin { jvmToolchain(17) }` / `java.toolchain.languageVersion = JavaLanguageVersion.of(17)`) plus the `foojay-resolver-convention` plugin lets Gradle locate or download the exact **compile** JDK (17 bytecode target) regardless of which JDK *launched* Gradle (the 21 LTS baseline, or a newer 25). This both removes "works on my machine" drift and is precisely what lets us raise the runtime baseline to 21 and support the latest JDK without touching the app's bytecode target. *Alternative:* rely only on `JAVA_HOME` (rejected — that is exactly the current fragile state, and it conflates launcher and compile JDK).

**Decision 3 — Environment variables in a dedicated `~/.tdt/mobile-env.sh`, sourced from `~/.zshrc` via an idempotent marker block.**
Verified state (2026-06-14): the shell is **zsh** (`$SHELL=/bin/zsh`, oh-my-zsh). `~/.zshrc` adds `~/.tdt/bin` to `PATH` and sets the UV vars, but it does **not** source `~/.tdt/.env`, and `~/.tdt/.env` (mode 600, secrets only — GITLAB_PAT, ATLASSIAN_ACCESS_TOKEN, etc.) contains **no** `JAVA_HOME`/`ANDROID_HOME`/`ANDROID_SDK_ROOT`. So the build env needs a concrete home. Put the non-secret build exports in a new `~/.tdt/mobile-env.sh` and source it from `~/.zshrc` — keeping them **out** of the secrets `.env` (which is not sourced anyway) and out of the repos. The sourcing line is wrapped in an **idempotent marker block** matching the convention already in `~/.zshrc` (e.g. the `# >>> grok installer >>>` / `# <<< grok installer <<<` blocks), so re-running setup updates the block in place instead of appending duplicates. There is no committed `local.properties` and `local.properties` is gitignored (twice), with no `sdk.dir` anywhere, so Gradle relies entirely on `ANDROID_HOME`/`ANDROID_SDK_ROOT` from the environment — confirming the env-based approach. *Alternatives:* putting build vars in `~/.tdt/.env` (rejected — it's a 600 secrets file and isn't sourced by the rc); appending raw `export` lines straight into `~/.zshrc` (rejected — not idempotent, drifts on re-run); a per-repo `local.properties` (rejected as the canonical source — gitignored and machine-specific, though Gradle will still honor one if present).

**Decision 4 — Fix the Android root `build.gradle` inconsistency as Phase A (no behavior change).**
Align the stale `plugins {}` declarations (AGP 7.4.2 / Kotlin 1.8.0) to the versions the build actually resolves (AGP 8.7.3 / Kotlin 1.9.23). This is a correctness fix, not an upgrade — it removes a latent trap before any Phase B bump. *Alternative:* defer to Phase B (rejected — it muddies the upgrade diff and the current declarations are already misleading).

**Decision 5 — Staged upgrades, not big-bang, with exact pinned targets.** Phase A: make the current pinned stack build on a clean machine (provision toolchains, wire env, fix Decision 4 inconsistency) with **zero version bumps**. Phase B (scheduled separately): incremental, each gated on green build+tests — (B1) Kotlin 1.9.23 → 2.3.x K2 (latest 2.4.0 is newest stable but **not yet in Gradle's tested compat table** — newest listed is 2.3.20/Gradle 9.5 — so we pin Kotlin 2.3.x and revisit 2.4 once the matrix catches up); (B2) Gradle 8.9 → 8.14.5 (latest 8.x, stays AGP-8-compatible); (B3) AGP 8.7.3 → 9.2.1 + Gradle 8.14.5 → 9.5.1 + Kotlin → 2.3.x; iOS Swift 5 mode → Swift 6 language mode. *Alternative:* jump straight to AGP 9.2 / Kotlin 2.4 (rejected — couples three breaking migrations and a JDK assumption into one unverifiable step).

**Decision 6 — iOS is SPM-authoritative; CocoaPods is retired.** Verified repo state (2026-06-13): the Xcode project declares **29 `XCRemoteSwiftPackageReference`** entries with **56 pins** in `Pmobile3.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved`, plus the local `LocalPackages/PoemsUIComponents` package. There is **no `Podfile`, no `Podfile.lock`, no `Pods/Manifest.lock`**, and `Pods/` holds only a 0-byte `.nosync` placeholder. So the earlier "confirm Pods vs SPM" gate is resolved decisively in favor of **SPM**: dependencies resolve from the committed `Package.resolved`, no `pod install` is run, and the vestigial `Pods/` dir + the `cocoapods`/`xcode-install` `Gemfile` entries are flagged for removal. *Alternative:* keep CocoaPods alongside SPM (rejected — there is no Podfile/lockfile to drive it; reintroducing it would add a second, unpinned dependency path).

**Decision 7 — Ruby via a version manager, gems via Bundler.** System Ruby 2.6.10 is too old for the `Gemfile`'s Ruby 3.0.0 target. Provide Ruby 3.x (rbenv/asdf or Homebrew) and run Fastlane through `bundle exec` so versions match `Gemfile.lock`. With SPM authoritative (Decision 6), the gem set is needed for **Fastlane release automation only**, not dependency resolution. *Alternative:* `sudo gem install` on system Ruby (rejected — pollutes system Ruby, needs sudo, drifts from the lockfile).

**Decision 8 — Pin Xcode 26.5 (current stable).** Xcode 26.5 is the latest released stable (26.6 is RC-only); it bundles a Swift 6.x toolchain, matching the audited CLT Swift 6.3.2 and the project's macOS 26 / arm64 host. Pin 26.5 and install via the Mac App Store or `xcodes install 26.5`. *Alternative:* a 26.6 RC (rejected — not GA; release builds should not depend on a release candidate).

**Decision 9 — iOS minimum deployment target: 15.0.** Verified repo state (2026-06-13): `IPHONEOS_DEPLOYMENT_TARGET` is mixed across build-config lines — 18×`15.0`, 6×`14.5`, 6×`14.4`, 4×`14.1`. 15.0 is both the dominant value and a **hard floor**: the local SPM package `LocalPackages/PoemsUIComponents` declares `platforms: [.iOS(.v15)]`, so the app (which links it) cannot deploy below 15.0 regardless of preference. Converge all targets to **iOS 15.0**. The sub-15 values (14.1/14.4/14.5) are stale and raise no minimum-OS-support concern (they are *below* the effective floor, so raising them to 15.0 drops no currently-supported device beyond what SPM already requires). *Alternative:* converge to 14.x (rejected — impossible while linking a `.v15` package); raise above 15.0 (rejected — out of scope; would drop device support without product sign-off). The actual `IPHONEOS_DEPLOYMENT_TARGET` rewrite is a Phase B task (8.1); Phase A documents the policy.

## Finalized Configuration

### Canonical pinned version matrix

The **launcher JDK** runs Gradle; the **compile target** is the bytecode level the toolchain compiles to — they are pinned independently (Decisions 1–2).

| Tool | Phase A (build the current stack as-is) | Phase B (verified upgrade target) |
| --- | --- | --- |
| Launcher JDK (runs Gradle) | Temurin **21 LTS** (min); 25 LTS also supported | Temurin **21 LTS** (unchanged; 25 supported) |
| Compile / bytecode target | **17** (`:app`); **11** (`PoemsUIComponents`) | **17** (`:app`); **11** (`PoemsUIComponents`) |
| Gradle (wrapper) | **8.9** | **9.5.1** (B3); 8.14.5 interim (B2) |
| Android Gradle Plugin | **8.7.3** | **9.2.1** |
| Kotlin | **1.9.23** | **2.3.x** (revisit 2.4.0 when in Gradle compat) |
| Android SDK build-tools | **36.1.0** (installed) | track AGP-required min |
| compileSdk / targetSdk | **35** | **35** (API bump is a separate change) |
| Android platform | `android-35` (install; SDK has 36.1/37.0) | per compileSdk |
| NDK | **29.0.14206865** (installed) | per AGP requirement |
| Xcode | **26.5** | **26.5** |
| Swift language mode | **5** | **6** |
| iOS min deployment target | **15.0** (SPM `.v15` floor; converge in B) | **15.0** (targets aligned) |
| Ruby | **3.x** (Gemfile targets 3.0.0) | 3.x |
| CocoaPods / SPM | **SPM** (authoritative; 29 remote pkgs, 56 pins) | **SPM** (unchanged) |

Versions are exact, never "latest". The matrix lives in `docs/mobile-toolchain.md` (task 1.1) and is asserted by the verification script (task 2.1).

### Android config snippets (Phase A — reproducibility, no version bumps)

`settings.gradle` — foojay resolver so Gradle can locate/provision the toolchain JDK:

```groovy
plugins {
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}
```

`app/build.gradle` — keep the compile target at 17 regardless of the launcher JDK (replaces relying on an ambient `JAVA_HOME`):

```groovy
kotlin {
    jvmToolchain(17)   // compile target stays 17 even on a JDK 21/25 launcher
}
```

`~/.tdt/mobile-env.sh` (new file holding the non-secret build exports):

```sh
# Launcher JDK baseline (21 LTS); 25 also works — the Gradle toolchain pins the compile JDK.
export JAVA_HOME="$(/usr/libexec/java_home -v 21)"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
```

`~/.zshrc` — append an idempotent marker block (the rc does NOT currently source any `~/.tdt` env file). This matches the existing marker-block convention in the file (e.g. the `# >>> grok installer >>>` block), so re-running setup must not duplicate lines:

```sh
# >>> tdt mobile toolchain >>>
[ -f "$HOME/.tdt/mobile-env.sh" ] && . "$HOME/.tdt/mobile-env.sh"
# <<< tdt mobile toolchain <<<
```

Notes: this is **zsh-specific** (`~/.zshrc`, the workspace's login shell); keep the exports in `mobile-env.sh`, NOT in `~/.tdt/.env` (that file is mode-600 secrets and is not sourced by the rc). Setup must check for an existing `# >>> tdt mobile toolchain >>>` block and update it in place rather than appending a second copy.

### Provisioning commands (Phase A)

```sh
# JDK 21 launcher baseline
brew install --cask temurin@21
# Android SDK: the installed SDK has ONLY platforms android-36.1/37.0 + build-tools 36.1.0/37.0.0
# (verified) — the repo's compileSdk/targetSdk 35 platform is MISSING and must be installed.
sdkmanager --licenses
sdkmanager "platforms;android-35" "build-tools;35.0.0"
# iOS toolchain
xcodes install 26.5            # or install Xcode 26.5 from the Mac App Store
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
# iOS dependencies: SPM is authoritative — resolve packages (no `pod install`)
xcodebuild -resolvePackageDependencies -project poems-mobile3-ios/Pmobile3.xcodeproj -scheme Pmobile3
# Ruby + gems for Fastlane only (CocoaPods gem is vestigial — see Decision 6)
(cd poems-mobile3-ios && bundle install)
```

## Risks / Trade-offs

- **Xcode install is large and version-sensitive** → document the exact Xcode version and pin it; allow install via Apple Developer downloads or `xcodes`; treat as the slowest setup step.
- **A clean machine with no JDK can't even run `./gradlew` to self-verify** → Phase A installs Temurin 21 LTS first, then relies on the Gradle toolchain for the compile JDK; verification script checks `java -version` before invoking Gradle.
- **Phase B Kotlin 2.x K2 / AGP 9 migrations can surface source-level breakages** → each bump is isolated, gated on green build + unit tests, and reversible via git; `PoemsUIComponents` (Java/Kotlin 11) is explicitly held back.
- **Vestigial CocoaPods artifacts could mislead a reader into running `pod install`** → Decision 6 declares SPM authoritative on hard evidence (29 `XCRemoteSwiftPackageReference`, 56-pin `Package.resolved`, empty `Pods/`, no `Podfile`/lockfiles); the empty `Pods/` and `cocoapods` Gemfile entry are flagged for cleanup, not relied upon.
- **Mixed iOS deployment targets** → policy set to 15.0 (Decision 9, a hard SPM `.v15` floor) and documented in Phase A; the actual `IPHONEOS_DEPLOYMENT_TARGET` rewrite is deferred to Phase B (8.1) so the minimum-OS change is a deliberate, reviewed diff rather than a silent edit.
- **`brew`/`xcodes` versions move** → the version matrix pins exact versions and the verification commands fail loudly on drift.

## Migration Plan

1. **Phase A (this change):** install Temurin 21 LTS (runtime/launcher baseline); export `JAVA_HOME`/`ANDROID_HOME`/`ANDROID_SDK_ROOT` from `~/.tdt`; add Gradle JVM toolchain (compile target 17) + foojay resolver; fix root `build.gradle` plugin-version inconsistency; install full Xcode + select it; resolve SPM packages (SPM is authoritative — Decision 6) and provision Ruby/Bundler for Fastlane. Verify: `java -version`, `./gradlew :app:assembleDevDebug` (or `tasks`), `xcodebuild -version`, `xcodebuild -resolvePackageDependencies` for the `Pmobile3` scheme, and an `xcodebuild` configure of that scheme.
2. **Phase B (scheduled separately):** B1 Kotlin 2.3.x, B2 Gradle 8.14.5, B3 AGP 9.2.1 + Gradle 9.5.1 + Kotlin 2.3.x, iOS Swift 6 mode — each on a branch, gated on green build + tests, merged only when verification passes.
- **Rollback:** Phase A toolchain installs are additive (no repo behavior change beyond Decision 4, which is revertable via git). Phase B bumps are per-branch and revert by restoring the pinned version files.

## Resolved Questions

- **CI wiring — deferred to Phase B (resolved).** The verification script (`scripts/check-mobile-toolchain.sh`, task 2.1) is delivered in Phase A as a **local/Fastlane-invocable** check, not a CI gate. Wiring it into a CI runner is deferred to Phase B because Phase A's goal is making a *developer machine* build-ready; there is no evidence in-repo of a CI runner that builds these apps today, so adding a CI gate now would be speculative. Phase B (tasks 7.4/8.3) re-runs the script against the upgraded matrix and is the natural point to add a CI job once the target stack is green.
- **Vestigial CocoaPods cleanup — flag now, remove in a separate change (resolved).** This change only **flags** the empty `Pods/` directory and the `cocoapods`/deprecated `xcode-install` Gemfile entries (Decision 6, task 6.4). Actually deleting them is out of scope here: this change is additive/setup-only (no repo behavior change beyond the Decision 4 correctness fix), and removing a tracked directory + editing the `Gemfile`/`Gemfile.lock` is a separate, reviewable cleanup with its own diff. Keeping it separate preserves a clean "setup vs. cleanup" boundary and avoids coupling a delete to the toolchain bring-up.
