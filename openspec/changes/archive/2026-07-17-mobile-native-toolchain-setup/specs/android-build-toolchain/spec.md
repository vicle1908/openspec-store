## ADDED Requirements

### Requirement: Pinned JDK provisioning
The Android build SHALL distinguish the JDK that *runs* Gradle (the launcher JDK) from the JDK that *compiles* the app (the bytecode-target JDK), and pin each independently. The launcher JDK baseline MUST be **Java 21 LTS** (because Oracle JDK 17 free premier support ends September 2026 and Gradle 8.9/9.x run on JVM 21), and the build MUST also run on a newer LTS launcher (Java 25) without changes. The compile/bytecode target MUST remain **Java 17** to satisfy the Android Gradle Plugin and preserve app runtime compatibility. A JDK MUST be installed and discoverable via `JAVA_HOME`, because the machine currently has no JDK (`/usr/bin/java` is a non-functional stub).

#### Scenario: Launcher JDK baseline is present and correct
- **WHEN** `java -version` is run after setup
- **THEN** it reports a working Java 21 LTS runtime (or a newer supported LTS such as 25)
- **AND** `JAVA_HOME` points at that distribution

#### Scenario: Compile target is independent of the launcher JDK
- **WHEN** the Android project is built on the Java 21 (or newer) launcher JDK
- **THEN** the Gradle JVM toolchain compiles against Java 17 bytecode regardless of the launcher JDK version
- **AND** the produced artifacts target the same Java 17 level as before this change

#### Scenario: Gradle does not depend on an ambient JDK
- **WHEN** the Android project is built
- **THEN** the build resolves its Java toolchain explicitly (Gradle JVM toolchain) rather than relying on whatever `java` happens to be on `PATH`
- **AND** a machine with no system JDK on `PATH` can still build once the launcher and toolchain JDKs are provisioned

### Requirement: Android SDK and NDK wiring
The Android build SHALL use the existing SDK installation at `~/Library/Android/sdk` with build-tools, platform, and NDK versions consistent with the pinned matrix. The setup MUST NOT require committing a machine-specific `local.properties`. SDK components MUST be provisioned via `sdkmanager` (from `cmdline-tools/latest`) with all required licences accepted, and the required components MUST be installed before the first build rather than relied upon to auto-download.

#### Scenario: The compileSdk platform is present (current gap)
- **WHEN** the Android build for the current pinned stack (`compileSdk`/`targetSdk` **35**) is prepared
- **THEN** SDK platform `android-35` MUST be installed via `sdkmanager "platforms;android-35"`
- **AND** the setup recognises that the installed SDK currently has only `android-36.1`/`android-37.0` platforms and no `android-35`, so this component is installed explicitly before building

#### Scenario: Build-tools and NDK satisfy the build
- **WHEN** the Android build runs
- **THEN** a build-tools version compatible with the pinned AGP is present (the SDK currently has `36.1.0` and `37.0.0`)
- **AND** the NDK version required by the build (`29.0.14206865`, installed) is present
- **AND** any missing component is reported by the verification script with the exact `sdkmanager` command to install it

#### Scenario: Licences are accepted non-interactively
- **WHEN** SDK components are provisioned on a clean machine
- **THEN** `sdkmanager --licenses` is run and all required licences are accepted
- **AND** an unaccepted licence is surfaced as an actionable setup failure, not a mid-build error

#### Scenario: SDK path is provided by environment
- **WHEN** Gradle needs the SDK location
- **THEN** it reads `ANDROID_HOME`/`ANDROID_SDK_ROOT` from the environment (no committed `local.properties` `sdk.dir`)
- **AND** the `cmdline-tools/latest/bin` and `platform-tools` directories are on `PATH` so `sdkmanager`/`adb` resolve

### Requirement: Gradle, AGP, and Kotlin version policy
The Android repository SHALL pin Gradle (wrapper), AGP, and Kotlin to a mutually compatible set, and the root build configuration MUST be internally consistent. The existing inconsistency — the root `plugins` block declaring `com.android.library` 7.4.2 and `org.jetbrains.kotlin.android` 1.8.0 while the `buildscript` block uses AGP 8.7.3 and Kotlin 1.9.23 — MUST be resolved so a single AGP and Kotlin version governs the build.

#### Scenario: Consistent plugin versions
- **WHEN** the root `build.gradle` is inspected
- **THEN** the AGP version and Kotlin version are declared consistently (no conflicting 7.4.2/1.8.0 vs 8.7.3/1.9.23 declarations)
- **AND** the Gradle wrapper version is compatible with the declared AGP version

#### Scenario: PoemsUIComponents toolchain is preserved
- **WHEN** the toolchain configuration is changed
- **THEN** the `PoemsUIComponents` module's intentional Java/Kotlin 11 target is left unchanged unless the change is explicit and verified

### Requirement: Staged upgrade path to current stable
The Android toolchain SHALL define a staged, verified upgrade path rather than a single big-bang bump. Phase A MUST make the current pinned stack build on a clean machine with no version changes, while establishing the **Java 21 LTS launcher baseline** and the Gradle JVM toolchain that decouples the launcher JDK from the Java 17 compile target. Phase B MUST perform incremental upgrades (Kotlin 1.9 → 2.x K2, Gradle 8.9 → newer 8.x, then AGP/Gradle 9.x and Kotlin 2.3/2.4), where each step is gated on a green build and test run before the next. Raising the launcher JDK to the latest LTS (e.g. Java 25) MUST be possible without changing the compile target. Version bumps are BREAKING and MUST be isolated to Phase B.

#### Scenario: Phase A is config-only
- **WHEN** Phase A completes
- **THEN** the existing AGP/Gradle/Kotlin versions and the Java 17 compile target are unchanged
- **AND** the app builds and tests pass on a freshly provisioned machine running the Java 21 LTS launcher baseline

#### Scenario: Latest LTS launcher is supported
- **WHEN** an engineer runs the build on a newer supported LTS launcher (e.g. Java 25) within Gradle's supported JVM range
- **THEN** the build succeeds because the Gradle JVM toolchain still compiles against Java 17
- **AND** no source or bytecode-target change is required

#### Scenario: Each Phase B upgrade is gated
- **WHEN** a Phase B version bump is applied
- **THEN** the build and test suite are run and must pass before the next bump proceeds
- **AND** a failed step can be rolled back to the previous pinned version
