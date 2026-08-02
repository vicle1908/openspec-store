# Jira Realtime Transition Guard

## ADDED Requirements

### Requirement: Real-time Jira transition events are guarded consistently
The workspace SHALL expose a Jira transition webhook guard that verifies HMAC signatures, detects status transitions, applies reminder policies, suppresses duplicates, supports dry-run mode, and reports health.

#### Scenario: A valid transition event is received
- **WHEN** Jira sends a signed `jira:issue_updated` webhook with a status change in the changelog
- **THEN** the guard verifies the signature, evaluates matching reminder policies, and returns HTTP 200

#### Scenario: A request fails signature verification
- **WHEN** the webhook signature is invalid or missing
- **THEN** the guard rejects the request with HTTP 401 and does not process the payload

#### Scenario: A reminder is suppressed or deduplicated
- **WHEN** the matching policy is already satisfied, suppressed, or deduplicated within the cooldown window
- **THEN** the guard returns HTTP 200 without posting a Jira comment

#### Scenario: Health and dry-run state are exposed
- **WHEN** the guard health endpoint is queried
- **THEN** the response reports whether the guard is enabled, dry-run is active, policies are loaded, and the database path is configured
