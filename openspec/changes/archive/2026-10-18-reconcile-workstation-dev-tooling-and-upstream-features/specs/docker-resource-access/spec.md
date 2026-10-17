# docker-resource-access Specification Delta

## ADDED Requirements

### Requirement: Workspace Compose compliance with named database volumes and loopback port bindings

All active workspace `docker-compose*.yml` files—including `~/Developer/tdt/jira-skill/docker-compose.yml`, `~/Developer/tdt/bootstrap-nexus`, `~/Developer/tdt/realtime`, `~/Developer/vds/vds-root-assets`, and `~/Developer/ghtk/ghtk-training-cicd`—SHALL pass `~/Developer/scripts/docker-standardize-check.sh` with zero `FAIL` or unapproved wildcard port warnings by replacing host database directory mounts with named Docker volumes and prefixing published ports with `127.0.0.1:`.

#### Scenario: docker-standardize-check.sh passes across workspace Compose files
- **WHEN** `~/Developer/scripts/docker-standardize-check.sh` is executed across the workspace
- **THEN** `~/Developer/tdt/jira-skill/docker-compose.yml` SHALL mount database storage via a named Docker volume rather than a host path
- **AND** all published service ports across audited Compose files SHALL bind to `127.0.0.1:` (or be documented as explicitly approved exceptions), producing `0` `FAIL` results
