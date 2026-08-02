## ADDED Requirements

### Requirement: Canonical pinned version matrix
The project SHALL maintain a single canonical, version-pinned matrix that defines the exact native build toolchain versions for both mobile repositories. The matrix MUST cover the JDK (recording both the **launcher JDK** that runs Gradle and the **compile/bytecode target**), Android SDK platform/build-tools/NDK, Gradle, Android Gradle Plugin (AGP), Kotlin, Xcode, Swift language mode, CocoaPods, and Ruby/Bundler. The launcher JDK baseline MUST be **Java 21 LTS** and the matrix MUST record which newer LTS launchers (e.g. Java 25) are also supported; the compile target MUST be recorded separately (Java 17). Every pinned version MUST be mutually compatible according to the upstream compatibility matrices (AGP↔Gradle↔JDK, Gradle↔Kotlin).

#### Scenario: Reading the authoritative toolchain versions
- **WHEN** an engineer or agent needs to know which toolchain version to install or pin
- **THEN** a single documented matrix in the repositories states the exact pinned version for each tool
- **AND** the launcher JDK (21 LTS baseline) and the compile target (17) are listed as distinct entries
- **AND** each pinned pair (AGP/Gradle/compile-JDK, Gradle/Kotlin, Gradle/launcher-JDK) is consistent with the published upstream compatibility tables

#### Scenario: Versions are pinned, not floating
- **WHEN** the matrix specifies a toolchain version
- **THEN** it is an exact version (e.g. launcher JDK `21`, compile target `17`, Gradle `8.9`, Kotlin `1.9.23`), never an open range or "latest"
- **AND** any change to a pinned version is made deliberately through this change's upgrade policy

### Requirement: Required environment variables
The toolchain SHALL define the environment variables required to build both apps, and these MUST be sourced from the `~/.tdt` configuration area rather than hard-coded in repository files. At minimum `JAVA_HOME`, `ANDROID_HOME`, and `ANDROID_SDK_ROOT` MUST be defined for the Android build, and the active developer directory MUST point at a full Xcode for the iOS build. Because the current shell environment defines none of these (the audited `~/.tdt/.env` has no `JAVA_HOME`/`ANDROID_HOME`/`ANDROID_SDK_ROOT`, and `~/.zshrc` only adds `~/.tdt/bin` to `PATH` and sets the `UV_*` vars — it does not source an SDK env file), setup MUST introduce a concrete sourcing mechanism: a dedicated `~/.tdt`-managed shell snippet (`~/.tdt/mobile-env.sh`) that exports the variables, sourced from `~/.zshrc` (the verified interactive shell is zsh). The `~/.zshrc` edit MUST be idempotent, delimited by a marker block (the same `# >>> ... >>>` / `# <<< ... <<<` convention `~/.zshrc` already uses for the grok and Antigravity installers), so re-running setup does not append duplicate lines.

#### Scenario: Environment is documented and sourced from ~/.tdt via ~/.zshrc
- **WHEN** a developer configures a new machine
- **THEN** the required variables (`JAVA_HOME`, `ANDROID_HOME`, `ANDROID_SDK_ROOT`) are documented with their expected values
- **AND** they are exported by `~/.tdt/mobile-env.sh`, which is sourced from `~/.zshrc` via a delimited marker block, so no secret or machine-specific path is committed to a repo

#### Scenario: The ~/.zshrc edit is idempotent
- **WHEN** the setup that wires the environment into `~/.zshrc` is run more than once
- **THEN** the `# >>> tdt mobile toolchain >>>` … `# <<< tdt mobile toolchain <<<` marker block appears exactly once
- **AND** re-running setup updates the block in place rather than appending duplicate `source` or `export` lines

#### Scenario: A new shell session has the toolchain environment
- **WHEN** a developer opens a fresh zsh session after running setup
- **THEN** `JAVA_HOME` resolves to the pinned launcher JDK (via `/usr/libexec/java_home -v 21`) and `ANDROID_HOME`/`ANDROID_SDK_ROOT` resolve to the SDK
- **AND** the SDK `platform-tools` and `cmdline-tools/latest/bin` are prepended to `PATH` without clobbering the existing `~/.tdt/bin` and `UV_*` setup already in `~/.zshrc`

#### Scenario: Android SDK location is wired
- **WHEN** `ANDROID_HOME` / `ANDROID_SDK_ROOT` are evaluated
- **THEN** they resolve to the installed SDK at `~/Library/Android/sdk`
- **AND** the Gradle build locates the SDK without a committed `local.properties` absolute path (the repo `.gitignore` already excludes `local.properties`)

### Requirement: Build-readiness verification commands
The toolchain SHALL provide a documented set of verification commands that confirm a machine is build-ready, and these commands MUST be runnable in-session and in CI. The verification MUST fail with an actionable message when a prerequisite (JDK, Android SDK, Xcode, CocoaPods) is missing or mismatched.

#### Scenario: Verifying a build-ready machine
- **WHEN** the verification commands are run on a correctly configured machine
- **THEN** they confirm the presence and version of the JDK, Android SDK, Gradle, Xcode, and Swift
- **AND** they confirm the launcher JDK is at least the Java 21 LTS baseline (accepting a newer supported LTS such as 25)
- **AND** they exit successfully

#### Scenario: Detecting a missing prerequisite
- **WHEN** a required tool is absent or a version does not match the pinned matrix
- **THEN** the verification reports which tool is missing or mismatched and the expected version
- **AND** it exits non-zero so CI fails fast
