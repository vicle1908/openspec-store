# ADR 003: Sonatype Nexus Repository OSS Community Edition

## Status

Accepted

## Context

We need an artifact manager supporting both Android (Maven2/AAR) and iOS (Swift Package Manager). The solution must be free, self-hosted, and support both formats natively.

Key requirements:
- Maven2 repository for Android AAR artifacts
- Swift Package Manager registry for iOS packages
- Self-hosted (data stays on-premise)
- Free (no license cost)

## Decision

We will use **Sonatype Nexus Repository OSS Community Edition 3.91.1**.

## Consequences

### Positive

- **Free and unlimited**: No license cost; unlimited artifacts within CE limits
- **Self-hosted**: Full data control; no cloud dependency
- **Native Swift SPM support**: Only artifact manager with native Swift Package Registry API (validated)
- **Mature ecosystem**: Extensive documentation, large community
- **Docker official image**: `sonatype/nexus3` with regular updates
- **REST API**: Full automation support for bootstrap and CI/CD

### Negative

- **CE limits**: 100K components, 200K requests/day (acceptable for small team)
- **No HA**: Single-node only (can migrate to PostgreSQL later)
- **No export/import**: Pro-only feature (workaround: `rsync` for blobs)
- **H2 database risk**: Corruption if not shut down gracefully (mitigated by 120s timeout)

## Alternatives Considered

| Alternative | Swift SPM | Maven2 | Self-Hosted | Cost | Rejected Because |
|------------|-----------|--------|-------------|------|-----------------|
| **JFrog Artifactory OSS** | ❌ No native | ✅ Full | ✅ Yes | Free (limited) | No Swift SPM support |
| **GitHub Packages** | ❌ No native | ⚠️ Limited | ❌ No | Team plan | No Swift SPM; cloud-hosted |
| **Cloudsmith** | ⚠️ Limited | ✅ Yes | ❌ No | Free tier (5GB) | Not self-hosted; Swift limited |
| **AWS CodeArtifact** | ❌ No native | ✅ Yes | ❌ No | Pay per request | No Swift SPM; cloud cost |
| **Nexus Pro** | ✅ Yes | ✅ Yes | ✅ Yes | License cost | Free CE meets requirements |
| **Raw HTTP server** | ❌ No | ⚠️ Manual | ✅ Yes | Free | No repository features |

## Validation

- ✅ Swift hosted/proxy/group repositories created via REST API
- ✅ Swift Package Registry API endpoints respond correctly (validated live)
- ✅ Maven2 repositories pre-configured in CE
- ✅ AAR upload and download validated

## Migration Path

If CE limits are reached:
1. Migrate H2 to PostgreSQL (CE supports this since 3.77.2)
2. Consider Nexus Pro for HA clustering if needed
