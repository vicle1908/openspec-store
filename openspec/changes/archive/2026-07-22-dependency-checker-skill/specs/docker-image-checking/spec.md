# docker-image-checking

## Purpose

Docker image version checking via Docker Hub API for all images in the platform.

## ADDED Requirements

### Requirement: DIC-001: Docker Hub API Integration

The system SHALL integrate with Docker Hub API to check image versions.

#### Scenario: Query Docker Hub API
Given a Docker image name (e.g., `postgres`, `redis`)
When the system queries Docker Hub API
Then it shall return JSON with tag names, last updated, and architectures
And it shall support pagination for large tag lists

#### Scenario: Parse Image Tags
Given Docker Hub API response
When the response is parsed
Then it shall extract tag names, last updated timestamps, and architecture information
And it shall filter for relevant tags (e.g., `-alpine`, `-slim`)

### Requirement: DIC-002: Image Version Comparison

The system SHALL compare current image versions with latest available versions.

#### Scenario: Compare Versions
Given current version in `tools.env` (e.g., `POSTGRES_VERSION=18.4-alpine`)
And latest version from Docker Hub API
When the comparison is made
Then it shall show current version, latest version, and whether upgrade is available
And it shall check for security patches

#### Scenario: Multi-Architecture Check
Given a Docker image with multiple architectures
When the version is checked
Then it shall verify that the required architectures are available (linux/amd64, linux/arm64)
And it shall report if any required architecture is missing

### Requirement: DIC-003: Image Report Generation

The system SHALL generate a comprehensive report of Docker image versions.

#### Scenario: Generate Image Report
Given all Docker images in `deploy/tools.env`
When the report is generated
Then it shall show current version, latest version, and upgrade status for each image
And it shall highlight security patches
And it shall check for multi-architecture support

### Requirement: DIC-004: Cache Management

The system SHALL cache Docker Hub API responses to avoid rate limiting.

#### Scenario: Cache API Responses
Given a Docker Hub API query
When the response is received
Then it shall cache the response for a configurable duration (e.g., 1 hour)
And it shall use the cached response for subsequent queries within the duration

#### Scenario: Cache Invalidation
Given a cached response that has expired
When a new query is made
Then it shall fetch fresh data from Docker Hub API
And it shall update the cache

### Requirement: DIC-005: Error Handling

The system SHALL handle Docker Hub API errors gracefully.

#### Scenario: API Rate Limiting
Given Docker Hub API returns rate limiting error
When the error is received
Then it shall retry after the specified delay
And it shall use cached data if available

#### Scenario: API Unavailable
Given Docker Hub API is unavailable
When the error is received
Then it shall log the error
And it shall use cached data if available
And it shall report the issue
