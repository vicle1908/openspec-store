# Platform Subtask Breakdown

## ADDED Requirements

### Requirement: Android Task Breakdown

All feature tasks SHALL have separate Android (Kotlin) subtasks with specific implementation requirements.

#### Scenario: Android subtask structure
- **WHEN** creating Android implementation tasks for SR-3588
- **THEN** each feature SHALL have subtasks for: UI implementation, data layer integration, state management, testing

#### Scenario: Android branch naming
- **WHEN** creating feature branches for Android
- **THEN** branch name SHALL follow pattern: `feature/SR3588-<feature>-android`

### Requirement: iOS Task Breakdown

All feature tasks SHALL have separate iOS (Swift) subtasks with specific implementation requirements.

#### Scenario: iOS subtask structure
- **WHEN** creating iOS implementation tasks for SR-3588
- **THEN** each feature SHALL have subtasks for: SwiftUI/UIKit implementation, Combine/reactive layer, ViewModel, testing

#### Scenario: iOS branch naming
- **WHEN** creating feature branches for iOS
- **THEN** branch name SHALL follow pattern: `feature/SR3588-<feature>-ios`

### Requirement: Shared Code Identification

Tasks SHALL identify which code is shared between platforms and which is platform-specific.

#### Scenario: Shared data models
- **WHEN** implementing data models for Single Ledger
- **THEN** shared domain models SHALL be extracted to shared/module layer

#### Scenario: Platform-specific UI
- **WHEN** implementing UI components
- **THEN** Android and iOS SHALL have separate UI implementations following platform conventions

### Requirement: Cross-Platform Testing Coordination

Each platform task SHALL define testing requirements including unit tests, integration tests, and manual verification steps.

#### Scenario: Android testing requirements
- **WHEN** Android feature task is created
- **THEN** task SHALL include requirements for: Espresso tests, unit tests with 80% coverage

#### Scenario: iOS testing requirements
- **WHEN** iOS feature task is created
- **THEN** task SHALL include requirements for: XCTest, UI tests, code coverage targets

### Requirement: Task Dependencies

Android and iOS tasks SHALL clearly document their dependencies on backend API contracts.

#### Scenario: API contract dependency
- **WHEN** mobile task references backend API
- **THEN** task description SHALL link to the relevant API contract spec

#### Scenario: Feature-to-feature dependency
- **WHEN** Feature B depends on Feature A
- **THEN** Feature B task SHALL list Feature A task as a blocker
