# Proposal: Bootstrap Nexus OSS for Mobile Artifact Management

## Problem Statement

Our team needs a centralized artifact repository to store and distribute:
- Android: AAR libraries (via Gradle Maven2 publishing)
- iOS: Swift packages (via Swift Package Manager registry)

Current state: no internal artifact management. External dependencies pulled directly from Maven Central/GitHub, internal libraries shared manually.

## Goals

1. Deploy Sonatype Nexus Repository OSS 3.91+ via Docker Compose
2. Configure repositories for Maven2 (Android) and Swift (iOS SPM)
3. Enable CI/CD publishing via REST API with dedicated service accounts
4. Provide validated bootstrap automation (infrastructure-as-code)
5. Document client-side integration (Gradle, Package.swift, CI runners)

## Scope

| In Scope | Out of Scope |
|----------|-------------|
| Docker Compose deployment | SSL/TLS termination (nginx placeholder only, but HTTPS is REQUIRED for SPM clients — see ADR 005) |
| Maven2 + Swift repository setup | H2 to PostgreSQL migration |
| REST API bootstrap script | Full RBAC content selectors |
| CI user creation | Backup automation scripts |
| Gradle + SPM client docs | Prometheus monitoring |
| nginx reverse proxy config | High-availability clustering |

## Non-Goals

- Replacing all external dependencies with proxies
- npm/JS repository setup (not needed for pure native Android/iOS)
- Artifactory/Cloudsmith evaluation (already decided on Nexus OSS)
- Pro license features (ha-clustering, active-active)
- TLS certificate provisioning (self-signed cert acceptable for internal network; Let's Encrypt deferred)

## Success Criteria

- docker compose up starts Nexus with all configured repositories
- Android AAR can be published and consumed via maven-public
- iOS Swift package can be published and consumed via swift-group
- CI user has publish access to both formats
- Anonymous read access enabled for internal network clients
- EULA accepted programmatically at bootstrap via `POST /service/rest/v1/system/eula`
- Scope validation documented (underscores/hyphens, no dots)

## Risks

| Risk | Mitigation |
|------|------------|
| CE H2 limits (100K components) | Monitor via health check API; migration path to PostgreSQL documented |
| Swift scope naming (no dots) | Document convention: com_company_lib vs com.company.lib |
| SPM 5.7+ registry API version drift | Pin SPM tools version in CI; test against live Nexus container |
| EULA gating blocks automation | Validate EULA acceptance API before all write operations |
