# Spec: Nexus OSS Deployment

## ADDED Requirements

### Requirement: Nexus runs via Docker Compose
The system SHALL deploy Sonatype Nexus Repository OSS 3.91+ as a Docker Compose service.

#### Scenario: Fresh start
- **WHEN** user runs `docker compose up -d`
- **THEN** Nexus container starts with healthcheck
- **AND** Nexus UI is accessible on port 8081 within 120 seconds

#### Scenario: Graceful shutdown
- **WHEN** user runs `docker compose down` or system reboots
- **THEN** Nexus receives 120s grace period for database flush
- **AND** no data corruption occurs on restart

### Requirement: Data persists across restarts
The system SHALL store all Nexus data in a named Docker volume.

#### Scenario: Container restart
- **WHEN** Docker container is restarted
- **THEN** all repositories, users, and artifacts are preserved
- **AND** no re-configuration is required

#### Scenario: Named volume vs bind mount
- **WHEN** Docker manages the `nexus-data` volume
- **THEN** UID 200 permissions are handled automatically
- **AND** no manual `chown -R 200:200` is needed on restore

### Requirement: Reverse proxy available
The system SHALL include an nginx reverse proxy service.

#### Scenario: Proxy routing
- **WHEN** request arrives at port 80
- **THEN** nginx forwards to Nexus on port 8081
- **AND** response returns correctly

#### Scenario: External port isolation
- **WHEN** inspecting exposed ports
- **THEN** only nginx ports (80/443) are bound to host
- **AND** nexus port 8081 is internal-only (not host-bound)

---

## MODIFIED Requirements

### Requirement: Environment configuration
The system SHALL use an `.env` file for configuration variables.

#### Scenario: Environment setup
- **WHEN** user copies `.env.template` to `.env`
- **THEN** variables are loaded by Docker Compose
- **AND** secrets are excluded from Git via `.gitignore`

### Requirement: Healthcheck endpoint
The system SHALL use `/service/rest/v1/status` for Docker health verification.

#### Scenario: Docker healthcheck (liveness)
- **WHEN** Docker healthcheck runs in docker-compose.yml
- **THEN** it queries `/service/rest/v1/status` (returns HTTP 200 if Nexus can serve reads, 503 otherwise)
- **AND** uses `wget --spider` because the Alpine-based image includes wget
- **AND** anonymous access is sufficient — this endpoint requires no authentication

#### Scenario: Validation healthcheck (detailed)
- **WHEN** validation script checks detailed health
- **THEN** it queries `/service/rest/v1/status/check` (returns JSON with per-check healthy fields)
- **AND** parses response to verify all checks report healthy

### Requirement: JVM memory configuration
The system SHALL configure JVM heap and direct memory with production values.

#### Scenario: Memory tuning
- **WHEN** Docker Compose starts Nexus
- **THEN** `INSTALL4J_ADD_VM_PARAMS` sets:
  - `-Xms` equal to `-Xmx` (prevents heap resizing)
  - `-Xmx` + `MaxDirectMemorySize` less than or equal to 2/3 of host RAM
  - Default: `-Xms2g -Xmx2g -XX:MaxDirectMemorySize=2g`
- **AND** JVM ergonomics detect container limits (Java 21 included)

### Requirement: File handle limits
The system SHALL configure file descriptor limits for the Nexus process.

#### Scenario: File handle exhaustion prevention
- **WHEN** Nexus processes many concurrent requests
- **THEN** ulimits are set to `nofile: 65536 soft, 65536 hard`
- **AND** no `Too many open files` errors occur

### Requirement: Restart policy
The system SHALL automatically restart Nexus on failure or reboot.

#### Scenario: Service resilience
- **WHEN** Nexus process crashes or host reboots
- **THEN** Docker restart policy `unless-stopped` restarts the service
- **AND** nginx depends on nexus health before starting


## Additional Production Scenarios

### Requirement: Docker Compose version compatibility
The system SHALL use features compatible with Docker Compose 3.8+.

#### Scenario: Compose file syntax
- **WHEN** `docker-compose.yml` is validated
- **THEN** it uses `services` instead of legacy `version` field
- **AND** `depends_on` with `condition` works in Compose 3.8+
- **AND** `healthcheck` block uses correct syntax

### Requirement: `.env` template provided
The system SHALL include a `.env.template` file with all required variables.

#### Scenario: Template variables
- **WHEN** user copies `.env.template` to `.env`
- **THEN** all variables are documented with defaults:
  - `NEXUS_ADMIN_PASS` - initial admin password (read from container)
  - `NEXUS_DATA_VOLUME` - Docker volume name (default: nexus-data)
  - `NEXUS_JVM_HEAP` - JVM heap size (default: 2g)
  - `NEXUS_JVM_MAXDIRECT` - JVM max direct memory (default: 2g)
  - `NEXUS_HTTP_PORT` - external HTTP port (default: 80)
  - `NEXUS_IMAGE_TAG` - Docker image tag (default: 3.91.1)

### Requirement: `nexus.properties` custom configuration
The system SHALL support custom properties via volume mount.

#### Scenario: Custom properties file
- **WHEN** `nexus-data/etc/nexus.properties` contains custom settings
- **THEN** they take effect on container restart
- **AND** settings include:
  - `application-port=8081`
  - `nexus-context-path=/`
  - `nexus.security.encryption.key=<custom-key>`

### Requirement: Container startup dependencies
The system SHALL ensure correct service startup order.

#### Scenario: Startup ordering
- **WHEN** `docker compose up` runs
- **THEN** Nexus starts first and passes healthcheck
- **AND** nginx starts AFTER Nexus reports healthy
- **AND** no requests reach Nexus before it's ready

### Requirement: Log management
The system SHALL handle Nexus container logs.

#### Scenario: Log rotation
- **WHEN** Nexus generates logs in `/nexus-data/log/`
- **THEN** Docker Compose `logging` driver rotates logs
- **AND** logs are accessible via `docker logs nexus`
- **AND** no unbounded disk growth from logs


## Cross-References

- ADR 001: Docker Compose over Kubernetes → `docs/adr/001-docker-compose-over-kubernetes.md`
- ADR 002: Named volume → `docs/adr/002-named-volume-over-bind-mount.md`
- ADR 003: Nexus OSS CE selection → `docs/adr/003-nexus-oss-ce-over-alternatives.md`
