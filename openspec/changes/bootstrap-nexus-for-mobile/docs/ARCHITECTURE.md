# Architecture: Nexus OSS Mobile Artifact Infrastructure

## System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MOBILE DEVELOPMENT TEAM                             │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────┐  │
│  │  Android    │    │    iOS      │    │         CI/CD                   │  │
│  │ Developers  │    │ Developers  │    │   (Jenkins / GitLab CI)         │  │
│  │             │    │             │    │                                 │  │
│  │ Gradle sync │    │ SPM resolve │    │  gradle publish                 │  │
│  │ from        │    │ from        │    │  swift package archive-source   │  │
│  │ maven-public│    │ swift-group │    │  curl upload to swift-hosted    │  │
│  └──────┬──────┘    └──────┬──────┘    └────────────┬────────────────────┘  │
│         │                  │                        │                        │
│         │                  │                        │                        │
│         └──────────────────┼────────────────────────┘                        │
│                            │                                               │
│                            ▼                                               │
│         ┌──────────────────────────────────────────────────────┐          │
│         │              NEXUS ARTIFACT REPOSITORY                │          │
│         │              (Docker Compose Deployment)              │          │
│         └──────────────────────────────────────────────────────┘          │
│                            │                                               │
│         ┌──────────────────┴──────────────────┐                           │
│         │           INTERNAL NETWORK            │                           │
│         └───────────────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Container Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DOCKER HOST                                        │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Docker Bridge: nexus-net                        │   │
│  │                                                                      │   │
│  │   ┌──────────────────────┐         ┌──────────────────────────┐     │   │
│  │   │   nexus:8081         │         │   nginx:80 / 443         │     │   │
│  │   │   sonatype/nexus3    │◄───────►│   Reverse Proxy          │     │   │
│  │   │   Community Edition  │         │   (Public Interface)     │     │   │
│  │   │   Java 25 / Alpine   │         │                          │     │   │
│  │   └──────────┬───────────┘         └──────────────────────────┘     │   │
│  │              │                                ▲                      │   │
│  │              │                                │                      │   │
│  │              │           ┌────────────────────┘                      │   │
│  │              │           │ Proxy to nexus:8081                       │   │
│  │              │           │ client_max_body_size 1G                   │   │
│  │              │           │ proxy_*_timeout 600s                      │   │
│  │              ▼           │                                           │   │
│  │   ┌─────────────────────────────────────────┐                        │   │
│  │   │   nexus-data (Docker Named Volume)      │                        │   │
│  │   │                                          │                        │   │
│  │   │   ┌─────────────┐  ┌─────────────┐     │                        │   │
│  │   │   │ db/         │  │ blobs/      │     │                        │   │
│  │   │   │ nexus.mv.db │  │ default/    │     │                        │   │
│  │   │   │ (H2 DB)     │  │ (Artifacts) │     │                        │   │
│  │   │   └─────────────┘  └─────────────┘     │                        │   │
│  │   │   ┌─────────────┐  ┌─────────────┐     │                        │   │
│  │   │   │ etc/        │  │ keystores/  │     │                        │   │
│  │   │   │ nexus.prop  │  │ node/       │     │                        │   │
│  │   │   └─────────────┘  └─────────────┘     │                        │   │
│  │   └─────────────────────────────────────────┘                        │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   External Access: nginx on port 80/443 only                                │
│   Internal Only: nexus:8081 (not exposed to host)                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Repository Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REPOSITORY LAYOUT                                     │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        ANDROID (Maven2)                              │   │
│   │                                                                       │   │
│   │   maven-releases    [hosted]  ← CI publishes AARs + POM             │   │
│   │        │                                                              │   │
│   │   maven-snapshots   [hosted]  ← CI publishes SNAPSHOT builds        │   │
│   │        │                                                              │   │
│   │   maven-central     [proxy]   ← Caches Maven Central                │   │
│   │        │                                                              │   │
│   │   maven-public      [group]   ← Unified read endpoint               │   │
│   │        │                                                              │   │
│   │        └──────────────────────► Android apps read from here         │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        iOS (Swift SPM)                               │   │
│   │                                                                       │   │
│   │   swift-hosted      [hosted]  ← CI publishes ZIP (Package.swift)    │   │
│   │        │                                                              │   │
  │   │   swift-proxy       [proxy]   ← Caches upstream Swift registry (env-specific) │   │
│   │        │                                                              │   │
│   │   swift-group       [group]   ← Unified read endpoint               │   │
│   │        │                                                              │   │
│   │        └──────────────────────► SPM resolves from here              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Write Path: CI user (authenticated) → hosted repositories                 │
│   Read Path:  Anonymous (unauthenticated) → group repositories              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Android AAR Publish Flow
```
┌──────────┐    gradle publish          ┌──────────────┐    HTTP POST
│ Android  │ ──────────────────────────► │  CI Pipeline │ ──────────────────────
│ Library  │                             │ (Jenkins/    │    multipart/form-data
│ Module   │                             │  GitLab CI)  │    maven2.asset=@.aar
└──────────┘                             └──────────────┘
                                                  │
                                                  │ auth: ci-user + NEXUS_PASS
                                                  ▼
                                         ┌──────────────────┐
                                         │  maven-releases  │
                                         │  [hosted]        │
                                         │                  │
                                         │  AAR + POM       │
                                         │  stored in blobs/│
                                         └──────────────────┘
                                                  │
                                                  │ group aggregation
                                                  ▼
                                         ┌──────────────────┐
                                         │  maven-public    │
                                         │  [group]         │
                                         │                  │
                                         │  Unified read    │
                                         │  endpoint        │
                                         └──────────────────┘
```

### iOS Swift Package Publish Flow
```
┌──────────┐    swift build / archive    ┌──────────────┐    HTTP POST
│ iOS      │ ──────────────────────────► │  CI Pipeline │ ──────────────────────
│ Library  │                             │ (Jenkins/    │    multipart/form-data
│ Package  │                             │  GitLab CI)  │    swift.asset=@.zip
└──────────┘                             └──────────────┘
                                                  │
                                                  │ auth: ci-user + NEXUS_PASS
                                                  ▼
                                         ┌──────────────────┐
                                         │  swift-hosted    │
                                         │  [hosted]        │
                                         │                  │
                                         │  ZIP with        │
                                         │  Package.swift   │
                                         │  stored in blobs/│
                                         └──────────────────┘
                                                  │
                                                  │ group aggregation
                                                  ▼
                                         ┌──────────────────┐
                                         │  swift-group     │
                                         │  [group]         │
                                         │                  │
                                         │  Unified read    │
                                         │  endpoint        │
                                         └──────────────────┘
```

### Developer Read Flow
```
┌──────────────┐     ┌──────────────┐     ┌────────────────────┐
│   Android    │     │     iOS      │     │   gradle / SPM      │
│  Developer   │     │  Developer   │     │   (no auth needed)  │
│              │     │              │     │                     │
│ gradle sync  │     │ swift package│     │                     │
│ implementation│────►│ resolve      │────►│  maven-public       │
│ "com.ex:lib" │     │ my_org.Lib   │     │  swift-group        │
└──────────────┘     └──────────────┘     └────────────────────┘
                                                   │
                                                   │ proxy if not cached
                                                   ▼
                                          ┌────────────────────┐
                                          │  maven-central     │
                                          │  swift-proxy       │
                                          │  (external cache)  │
                                          └────────────────────┘
```

## Security Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYERS                                     │
│                                                                              │
│  Layer 1: Network Isolation                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Host: Only nginx ports 80/443 exposed                               │    │
│  │  Internal: nexus:8081 on Docker bridge only                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Layer 2: Authentication                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Read:    Anonymous (no credentials) → group repositories            │    │
│  │  Write:   ci-user (basic auth) → hosted repositories                 │    │
│  │  Admin:   admin user (initial password, then changed)                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Layer 3: Role-Based Access                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  anonymous role:  nx-anonymous → browse, read                        │    │
│  │  ci-publisher role: repository-view-*-add,edit → publish             │    │
│  │  admin role:      nx-admin → full control                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Layer 4: Repository Boundaries                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Hosted:  Write-protected, immutable releases (allow_once)           │    │
│  │  Proxy:   Read-only, caches external                                 │    │
│  │  Group:   Read-only, aggregates hosted + proxy                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Layer 5: Data Protection                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Encryption: Custom key in nexus.properties                          │    │
│  │  Backup:     Weekly tar.gz of nexus-data volume                      │    │
│  │  Secrets:    .env excluded from Git                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            COMPONENTS                                        │
│                                                                              │
│   External                                                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                                │
│   │ Android  │  │ iOS      │  │ CI/CD    │                                │
│   │ Gradle   │  │ Xcode/   │  │ Jenkins/ │                                │
│   │          │  │ SPM      │  │ GitLab   │                                │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘                                │
│        │             │             │                                       │
│   ┌────┴─────────────┴─────────────┴─────┐                                │
│   │         nginx Reverse Proxy           │                                │
│   │  (HTTP 80, HTTPS 443 placeholder)     │                                │
│   └──────────────────┬────────────────────┘                                │
│                      │                                                      │
│   ┌──────────────────┴────────────────────┐                                │
│   │      Sonatype Nexus Repository 3.91   │                                │
│   │      Community Edition                │                                │
│   │                                       │                                │
│   │   ┌────────┐  ┌────────┐  ┌────────┐│                                │
│   │   │ Maven2 │  │ Swift  │  │ npm    ││  (npm for React Native if     │
│   │   │ Format │  │ Format │  │ Format ││   needed in future)           │
│   │   └────────┘  └────────┘  └────────┘│                                │
│   │                                       │                                │
│   │   ┌────────┐  ┌────────┐  ┌────────┐│                                │
│   │   │ Hosted │  │ Proxy  │  │ Group  ││                                │
│   │   │ Repos  │  │ Repos  │  │ Repos  ││                                │
│   │   └────────┘  └────────┘  └────────┘│                                │
│   │                                       │                                │
│   │   ┌────────────────────────────────┐ │                                │
│   │   │ H2 Database (nexus.mv.db)      │ │                                │
│   │   │ Blob Store (artifact binaries) │ │                                │
│   │   │ Config (nexus.properties)      │ │                                │
│   │   └────────────────────────────────┘ │                                │
│   └───────────────────────────────────────┘                                │
│                      │                                                      │
│   ┌──────────────────┴────────────────────┐                                │
│   │         Docker Named Volume           │                                │
│   │            nexus-data                 │                                │
│   └───────────────────────────────────────┘                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ADR Index

All architectural decisions are documented in `docs/adr/`:

| ADR | Decision | Status | Key Justification |
|-----|----------|--------|-------------------|
| [001](docs/adr/001-docker-compose-over-kubernetes.md) | Docker Compose over Kubernetes | Accepted | Single host, small team, simple backup |
| [002](docs/adr/002-named-volume-over-bind-mount.md) | Named volume over bind mount | Accepted | UID 200 handled automatically, portable |
| [003](docs/adr/003-nexus-oss-ce-over-alternatives.md) | Nexus OSS CE over alternatives | Accepted | Only free option with native Swift SPM |
| [004](docs/adr/004-anonymous-read-access.md) | Anonymous read enabled | Accepted | Zero-friction developer experience |
| [005](docs/adr/005-nginx-reverse-proxy.md) | nginx over direct exposure | Accepted | SSL-ready, upload size control, isolation |
| [006](docs/adr/006-swift-scope-naming.md) | Underscore-based scopes | Accepted | Nexus validation requires it |
