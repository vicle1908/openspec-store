# Spec: Client-Side Integration

## ADDED Requirements

### Requirement: Gradle publishes to Nexus
The system SHALL support Android AAR publishing via Gradle `maven-publish` plugin.

#### Scenario: Android library release
- **WHEN** Gradle `publish` task runs with Nexus credentials
- **THEN** AAR and POM upload to `maven-releases`
- **AND** artifact is versioned correctly

#### Scenario: Gradle credentials from environment
- **WHEN** `build.gradle.kts` reads `NEXUS_USER` and `NEXUS_PASS`
- **THEN** credentials are passed to `maven-publish` plugin
- **AND** build fails fast if credentials are missing
- **AND** credentials are never logged or written to build output

### Requirement: Gradle consumes from Nexus
The system SHALL support Android dependency resolution from Nexus group URL.

#### Scenario: Android app build
- **WHEN** Gradle sync references `maven-public`
- **THEN** internal and external dependencies resolve
- **AND** build succeeds

#### Scenario: Gradle repository ordering
- **WHEN** `repositories` block includes `maven-public`
- **THEN** Nexus is checked BEFORE Maven Central for cached dependencies
- **AND** Nexus falls back to proxy (Maven Central) for uncached artifacts

### Requirement: SPM publishes to Nexus
The system SHALL support Swift package publishing to Nexus registry.

#### Scenario: iOS library release
- **WHEN** CI uploads ZIP to `swift-hosted` with scope/name/version
- **THEN** package is available via SPM registry API
- **AND** manifest endpoint returns Package.swift content


#### Scenario: Swift package archive-source command
- **WHEN** developer runs `swift package archive-source`
- **THEN** a ZIP file is created with correct structure
- **AND** the ZIP contains Package.swift at root
- **AND** the ZIP is ready for upload to swift-hosted

#### Scenario: Swift package ZIP structure
- **WHEN** ZIP is prepared for upload
- **THEN** it contains `Package.swift` at root
- **AND** for binary targets: `.xcframework` directory at root
- **AND** ZIP is created with `swift package archive-source` or manually

### Requirement: SPM consumes from Nexus
The system SHALL support Swift package resolution from Nexus group URL.

#### Scenario: iOS app build
- **WHEN** SPM resolves dependency from `swift-group`
- **THEN** correct package version is downloaded
- **AND** build succeeds

#### Scenario: SPM registry authentication
- **WHEN** developer runs `swift package-registry set`
- **THEN** registry URL is `https://nexus/repository/swift-group/`
- **AND** credentials are stored in `~/.swiftpm/config/registries.json`
- **AND** `swift package-registry login` stores credentials securely
- **NOTE** HTTPS is required per SPM Registry spec; HTTP is rejected by SPM clients

### Requirement: Swift scope naming documented
The system SHALL document the scope naming constraint.

#### Scenario: Invalid scope
- **WHEN** upload uses dots in scope (e.g., `com.example`)
- **THEN** Nexus rejects with validation error
- **AND** documentation shows valid alternatives (underscores/hyphens)

---

## MODIFIED Requirements

### Requirement: Gradle Nexus publishing configuration
The system SHALL document complete Gradle KTS configuration.

#### Scenario: Publisher build script
- **WHEN** `build.gradle.kts` includes publishing configuration
- **THEN** it declares `maven` repository with `maven-releases` URL
- **AND** credentials are read from environment variables
- **AND** `MavenPublication` includes AAR artifact with POM metadata
- **AND** publication name is descriptive (e.g., `release`)

#### Scenario: Consumer build script
- **WHEN** `build.gradle.kts` declares dependency
- **THEN** `repositories` includes `maven { url = uri(...) }`
- **AND** dependencies use standard Maven coordinates
- **AND** transitive dependencies resolve through proxy cache
