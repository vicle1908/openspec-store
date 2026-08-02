---
isComplete: true
---

## 1. Docker Compose Infrastructure

- [ ] 1.1 Create `docker-compose.yml` with nexus + nginx services
  NOTE: Only nginx exposes ports (80/443); nexus is internal-only
- [ ] 1.1a Add `.env.template` with NEXUS_ADMIN_PASS, volume path
- [ ] 1.1b Add `.gitignore` for `nexus-data/`, `.env`, `admin.password`, backups
- [ ] 1.2 Create `nginx.conf` reverse proxy configuration (proxy to nexus:8081)
  NOTE: Prepare SSL config section — HTTPS is required for SPM clients even if cert provisioning is deferred
- [ ] 1.4 Validate `docker compose up` starts cleanly
- [ ] 1.5 Verify healthcheck passes within 120s
  NOTE: Use `wget --spider` (not curl — Alpine image has no curl). Use `/service/rest/v1/status` endpoint (returns 200/503, no auth required for anonymous healthcheck)
- [ ] 1.6 Configure JVM memory settings (-Xms2g -Xmx2g, MaxDirectMemorySize)
- [ ] 1.7 Set ulimits (nofile 65536) for Nexus process

## 2. Repository Bootstrap Automation

- [ ] 2.1 Create `scripts/bootstrap-nexus.sh` with EULA acceptance
  NOTE: GET `GET /service/rest/v1/system/eula`, echo full disclaimer into POST `/service/rest/v1/system/eula` with `accepted: true`
- [ ] 2.2 Add Swift repository creation (hosted/proxy/group)
- [ ] 2.3 Add Maven repository verification (pre-configured in CE)
- [ ] 2.4 Add snapshot writePolicy configuration (maven-snapshots)
- [ ] 2.5 Add CI user creation with `ci-publisher` role (least privilege)
  NOTE: Create custom role `ci-publisher` with privileges: `nx-component-upload`, `nx-repository-view-maven-*-*`, `nx-repository-admin-maven-*-*`, `nx-repository-view-swift-*-*`, `nx-repository-admin-swift-*-*`
- [ ] 2.6 Add anonymous read access enablement
- [ ] 2.7 Validate bootstrap script is idempotent

## 3. Android CI/CD Integration

- [ ] 3.1 Document Gradle `maven-publish` plugin configuration (KTS)
- [ ] 3.2 Create sample `build.gradle.kts` publisher snippet (env credentials)
- [ ] 3.3 Create sample `build.gradle.kts` consumer snippet (maven-public)
- [ ] 3.4 Document Jenkins pipeline for Android AAR publish (Credentials Plugin)
- [ ] 3.5 Document GitLab CI configuration for Android AAR publish (CI/CD Variables)
- [ ] 3.6 Validate AAR upload and download via group URL
- [ ] 3.7 Document SNAPSHOT versioning strategy

## 4. iOS CI/CD Integration

- [ ] 4.1 Document Swift Package Registry setup for SPM
- [ ] 4.2 Create sample `Package.swift` consumer snippet (swift-group)
- [ ] 4.3 Document Swift package ZIP preparation (Package.swift + XCFramework)
- [ ] 4.4 Document Jenkins pipeline for Swift package publish
- [ ] 4.5 Document GitLab CI configuration for Swift package publish
- [ ] 4.6 Document Swift scope naming convention (underscores/hyphens)
- [ ] 4.7 Validate Swift package upload and SPM resolution via group URL
- [ ] 4.8 Document `swift package archive-source` vs manual ZIP creation

## 5. Documentation

- [ ] 5.1 Create `README.md` with quick start guide
- [ ] 5.2 Document all repository endpoints
- [ ] 5.3 Document CI credentials setup (Jenkins + GitLab patterns)
- [ ] 5.4 Document backup strategy (weekly tar.gz, local disk)
- [ ] 5.5 Document CE limits and monitoring
- [ ] 5.6 Add troubleshooting section with common issues

## 6. Security

- [ ] 6.1 Document custom encryption key setup in nexus.properties
- [ ] 6.2 Verify admin.password is removed after first login
- [ ] 6.3 Verify anonymous role has read-only access

## 7. Validation

- [ ] 7.1 End-to-end test: Android AAR publish + consume
- [ ] 7.2 End-to-end test: iOS Swift package publish + consume
- [ ] 7.3 Verify health checks all pass
- [ ] 7.4 Verify blob store metrics update correctly
- [ ] 7.5 Document known limitations (CE vs Pro)


## 8. CI/CD Pipeline Configuration

- [ ] 8.1 Create Jenkins Declarative Pipeline for Android AAR publish
  NOTE: Use Jenkins Credentials Plugin (usernamePassword, ID: nexus-publish)
- [ ] 8.2 Create GitLab CI `.gitlab-ci.yml` for Android AAR publish
  NOTE: Use CI/CD Variables with NEXUS_USER and NEXUS_PASS masked
- [ ] 8.3 Create Jenkins Pipeline for iOS Swift package publish
  NOTE: Build XCFramework, create ZIP, upload via REST API
- [ ] 8.4 Create GitLab CI `.gitlab-ci.yml` for iOS Swift package publish
  NOTE: Use macOS runner, `swift package archive-source`
- [ ] 8.5 Document version derivation from Git tags (semantic versioning)
- [ ] 8.6 Document snapshot versioning for feature branches

## 9. Environment and Secrets

- [ ] 9.1 Create `.env.template` with all required variables
- [ ] 9.2 Update `.gitignore` with nexus-data, .env, admin.password, backups
- [ ] 9.3 Document Jenkins credential injection (env vars from Credentials Plugin)
- [ ] 9.3 Document GitLab CI variable injection (masked + protected)
- [ ] 9.4 Document admin.password lifecycle (read → bootstrap → delete)
- [ ] 9.5 Verify no secrets are committed to Git

## 10. Advanced Topics (Optional)

- [ ] 10.1 Document Swift binary target packaging (XCFramework structure)
  NOTE: Package.swift + .xcframework at root of ZIP
- [ ] 10.2 Document Gradle KTS signing configuration (optional)
- [ ] 10.3 Document Nexus blob store cleanup policies (CE available)
- [ ] 10.4 Document health check monitoring via REST API
- [ ] 10.5 Document H2 database size monitoring


## 11. Validation and Verification

- [ ] 11.1 Add Docker Compose config validation to Makefile or script
  NOTE: `docker compose config` parses and validates YAML
- [ ] 11.2 Create pre-flight check script (Docker, ports, disk, RAM)
- [ ] 11.3 Add Nexus version check to bootstrap script
  NOTE: Must be >= 3.91.0 for Swift group support
- [ ] 11.4 Add `--dry-run` mode to bootstrap script
- [ ] 11.5 Verify bootstrap idempotency (run twice, same result)
- [ ] 11.6 Create post-startup health verification script
- [ ] 11.7 Add YAML schema verification step in CI/CD
- [ ] 11.8 Document all validation commands in README

## 12. Operations and Maintenance (Future)

- [ ] 12.1 Document H2 to PostgreSQL migration path
  NOTE: CE supports PostgreSQL since 3.77.2; migrator tool required
- [ ] 12.2 Document nexus.properties customization guide
  NOTE: Custom encryption key, application-port, context-path
- [ ] 12.3 Add Docker Compose logging configuration (rotation)
  NOTE: Use `logging` driver options in compose to prevent unbounded growth
- [ ] 12.4 Create weekly backup automation script (cron)
  NOTE: `docker stop` + `docker run alpine tar` + `docker start`
- [ ] 12.5 Document CE limit monitoring (component count, request rate)
  NOTE: Use `/service/rest/v1/status/check` to track metrics
