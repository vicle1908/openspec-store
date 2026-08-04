# ADR 004: Anonymous Read Access Enabled

## Status

Accepted

## Context

Mobile developers need to resolve dependencies during local builds. Each developer machine runs Gradle (Android) or Swift Package Manager (iOS). We need to decide whether read access requires authentication.

Security context:
- Internal network only (nginx blocks external access)
- Write operations always require authentication
- CI user has separate credentials for publishing

## Decision

We will **enable anonymous read access** for all repository group URLs.

## Consequences

### Positive

- **Zero-friction developer experience**: No credentials needed for `gradle sync` or `swift package resolve`
- **Faster CI builds**: No auth overhead for dependency resolution
- **Simpler onboarding**: New devs don't need credentials to build
- **Read-only by design**: Anonymous role has no write permissions

### Negative

- **Slightly broader attack surface**: Anyone on internal network can read artifacts
- **No download tracking**: Cannot attribute artifact downloads to users
- **Potential data leakage**: If network is compromised, artifacts are readable

## Mitigations

- nginx is the only external interface; nexus:8081 is internal Docker network only
- Network segmentation isolates Nexus from public internet
- Sensitive artifacts can use content selectors for additional restrictions
- CI credentials are separate and scoped

## Alternatives Considered

| Alternative | Rejected Because |
|------------|-----------------|
| Require auth for all reads | Friction for developers; credential management overhead |
| Per-user read credentials | Complex for small team; no benefit at this scale |
| IP-based access control | Brittle; VPN/mobile dev machines have changing IPs |

## Validation

- ✅ `curl http://localhost/repository/maven-public/.../mylib.aar` works without auth
- ✅ `curl http://localhost/repository/swift-group/...` works without auth
- ✅ Write operations (upload) require `ci-user` credentials
