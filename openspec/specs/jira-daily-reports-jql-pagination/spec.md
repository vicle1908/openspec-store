# jira-daily-reports-jql-pagination Specification

## Purpose
TBD - created by archiving change jira-daily-reports-jql-pagination. Update Purpose after archive.
## Requirements
### Requirement: JQL Pagination

The JQL search in jira-daily-reports SHALL fetch the full result set regardless of size by following `nextPageToken` cursor pagination. Single-page truncation is not acceptable for reports that depend on complete issue sets.

#### Scenario: Pagination fetches all results across pages

- **WHEN** a JQL query matches more issues than a single page can return
- **THEN** the helper SHALL follow `nextPageToken` cursor until `isLast: true`
- **AND** it SHALL deduplicate issues by key across pages
- **AND** it SHALL log pagination progress with `client_jql_paginate`

