# Spec: Docker Compose Hygiene Baseline

## ADDED Requirements

### Requirement: No hardcoded admin credentials

No `docker-compose*.yml` file under version control in the TDT ecosystem
SHALL contain a default admin password in plaintext for any monitoring or database
service. Credentials MUST be sourced from environment variables with a
non-default sentinel default that forces the operator to set them explicitly.

**WHY**: Hardcoded credentials are a security vulnerability. Any developer who
clones the repo can access monitoring dashboards without any additional setup.

#### Scenario: Grafana starts with env-driven credentials

**GIVEN** `jira-skill/docker-compose.yml` has `GF_SECURITY_ADMIN_PASSWORD=${GF_ADMIN_PASSWORD:-changeme}`
**WHEN** the operator runs `docker compose up` without setting `GF_ADMIN_PASSWORD`
**THEN** Grafana starts with `admin`/`changeme` credentials
**AND** the operator is forced to set `GF_ADMIN_PASSWORD` to use a non-default password.

#### Scenario: No hardcoded credentials in any compose file

**GIVEN** a developer runs `grep -r "GF_SECURITY_ADMIN_PASSWORD=admin" .` across the repo
**WHEN** all compose files have been updated per this requirement
**THEN** no file contains the hardcoded default `admin` password for Grafana.

---

### Requirement: Compose file metadata follows modern conventions

Every active `docker-compose*.yml` file in the TDT ecosystem MUST:
1. Include a top-level `name:` field.
2. NOT include a deprecated `version:` field.
3. NOT include `container_name:` on any service unless an external tool
   documents a hard dependency on that exact container name.

**WHY**: The `name:` field makes project identification unambiguous. The `version:`
field is deprecated in Docker Compose v2 and triggers linter warnings.
`container_name:` bypasses Compose's naming scheme and breaks `docker compose exec <service>`.

#### Scenario: Service exec via service name works after container_name removal

**GIVEN** `jira-skill/docker-compose.yml` has `name: jira-skill` and no `container_name:`
**WHEN** a script runs `docker compose -f jira-skill/docker-compose.yml exec -T postgres psql ...`
**THEN** the command resolves correctly via the Compose service name `postgres`
**AND** the container name is derived from `jira-skill_postgres_1`.

---

### Requirement: Healthchecks must be self-consistent

If a service requires authentication, its healthcheck command MUST
include the necessary credentials or flags so the healthcheck accurately reflects
service health.

**WHY**: A healthcheck that always passes (or always fails) because auth is
missing provides no operational value and masks real failures.

#### Scenario: Redis healthcheck passes with requirepass

**GIVEN** `jira-skill/docker-compose.yml` has `command: redis-server --requirepass redis_pass`
**AND** the healthcheck is `["CMD", "redis-cli", "--no-auth-warning", "-a", "redis_pass", "ping"]`
**WHEN** `docker compose up` starts the redis service
**THEN** `docker compose ps` shows redis as `healthy`
**AND** the healthcheck correctly authenticates before pinging.
