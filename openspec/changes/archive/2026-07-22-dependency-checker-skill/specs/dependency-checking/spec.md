# dependency-checking

## Purpose

Automated dependency version checking for Go modules and Docker images across all services.

## ADDED Requirements

### Requirement: DC-001: Go Module Version Checking

The system SHALL check Go module versions in all service `go.mod` files against the latest available versions.

#### Scenario: Check Go Module Versions
Given Go modules in `services/*/go.mod`
When the dependency checker runs
Then it shall parse each go.mod file
And it shall check latest versions via pkg.go.dev API
And it shall generate a version comparison report

#### Scenario: Version Comparison Report
Given current and latest versions for Go modules
When the report is generated
Then it shall show current version, latest version, and upgrade status
And it shall highlight security advisories if any

### Requirement: DC-002: Docker Image Version Checking

The system SHALL check Docker image versions in `deploy/tools.env` against the latest available tags.

#### Scenario: Check Docker Image Versions
Given Docker images in `deploy/tools.env`
When the dependency checker runs
Then it shall parse each image:tag pair
And it shall check latest tags via Docker Hub API
And it shall generate an image version report

#### Scenario: Image Version Report
Given current and latest versions for Docker images
When the report is generated
Then it shall show current version, latest version, and upgrade status
And it shall check for security patches

### Requirement: DC-003: Dependency Matrix

The system SHALL maintain a dependency matrix showing all dependencies and their versions across services.

#### Scenario: Generate Dependency Matrix
Given all services and their dependencies
When the matrix is generated
Then it shall show dependencies grouped by type (Go modules, Docker images)
And it shall show version consistency across services

### Requirement: DC-004: Scheduled Checking

The system SHALL support scheduled dependency checking via CI/CD pipeline.

#### Scenario: Scheduled Check
Given a CI/CD pipeline with scheduled triggers
When the dependency checker runs on schedule
Then it shall check all dependencies
And it shall generate a report
And it shall notify stakeholders if updates are available

### Requirement: DC-005: On-Demand Checking

The system SHALL support on-demand dependency checking via manual trigger.

#### Scenario: Manual Check
Given a developer requesting dependency check
When the dependency checker runs
Then it shall check all dependencies
And it shall generate a report
And it shall display results immediately
