# Design: Nexus OSS Mobile Artifact Infrastructure

## Architecture

```
Docker Host
  ┌──────────────────┐      ┌──────────────────┐
  │    nexus:8081    │──────│   nginx:80/443   │  Public
  │  Nexus 3.91.1    │      │  Reverse Proxy   │  Face
  │  Community Ed.   │      │  (placeholder)   │
  └────────┬─────────┘      └──────────────────┘
           │
  ┌────────▼──────────┐
  │   nexus-data      │  Docker Volume
  │  /nexus-data      │  (H2 DB + blobs + config)
  │                   │
  │  db/nexus.mv.db   │  Metadata + users + security
  │  blobs/default/   │  Artifact binary storage
  │  etc/             │  Custom properties
  └───────────────────┘

Repository Layout (validated live):
  maven-releases      [hosted]  Android AARs published by CI
  maven-snapshots     [hosted]  Android CI snapshot builds
  maven-central       [proxy]   Maven Central cache
  maven-public        [group]   Unified Android read URL

  swift-hosted        [hosted]  Swift packages published by CI
  swift-proxy         [proxy]   External Swift package cache
  swift-group         [group]   Unified iOS read URL
```

## Key Design Decisions

### 1. Docker Compose over Kubernetes
Single machine, small team. Docker Compose is simpler. No orchestration complexity. Easy backup via single volume.

### 2. Named Volume over Bind Mount
Docker manages permissions automatically. No UID 200 host filesystem issues. Easier restore operations.

### 3. Nexus 3.91.1 (Alpine-based)
Latest stable with Java 25. Smaller footprint than UBI variant. Community Edition sufficient (no Pro needed).

### 4. Repository Types
| Format | Hosted | Proxy | Group | Rationale |
|--------|--------|-------|-------|-----------|
| Maven2 | yes    | yes   | yes   | CE ships with these pre-configured |
| Swift  | yes    | yes   | yes   | Full SPM registry API support (validated) |

### 5. Anonymous Read Enabled
Internal network only. Nexus port 8081 is NOT exposed externally (internal Docker network only). nginx on 80/443 is the sole public interface. Write operations always require credentials.

### 6. CI User with nx-admin Role
Simpler than fine-grained RBAC for small team. Can be restricted later via content selectors. Password stored in CI environment variable.


### Version Compatibility Note

Swift repository support was added recently:
- **3.90.0**: Swift hosted repositories introduced
- **3.91.0**: Swift group repositories introduced (REQUIRED for our design)
- **3.91.1**: Latest stable with bug fixes

Using any version before 3.91.0 means NO Swift group repository, breaking the unified read endpoint for iOS.

### 7. EULA Acceptance via API
Required gate before any write operations. Automated in bootstrap script. Must echo back full disclaimer JSON from `GET /service/rest/v1/system/eula` into `POST /service/rest/v1/system/eula`.

## Configuration Files

### docker-compose.yml
- nexus service: official image, named volume, healthcheck (no external ports)
- nginx service: reverse proxy, dependency on healthy nexus
- shared network: isolated bridge

### nginx.conf
- proxy_pass to nexus:8081
- client_max_body_size 1G (for large AARs/Swift zips)
- SSL config placeholder (TLS hardening deferred)

### scripts/bootstrap-nexus.sh
- Accept EULA
- Create Swift repos (hosted/proxy/group)
- Create CI user
- Enable anonymous access
- Print endpoint summary

## Data Flow

CI Build (GitLab/Jenkins)
    |
    ├── Android ──┬──► gradle publish to maven-releases
    │             │    (auth: ci-user + NEXUS_PASS)
    │             │
    └── iOS ──────┴──► swift package archive-source + curl upload to swift-hosted
                       (auth: ci-user + NEXUS_PASS)

Developer Machine
    |
    ├── Android ──┬──► Gradle sync from maven-public (no auth)
    │             │
    └── iOS ──────┴──► SPM resolve from swift-group (no auth)
                       (swift package-registry set group URL)

## Validation Strategy

Every change tested against live container:
1. Start Nexus container
2. Run bootstrap script
3. Upload test AAR to maven-releases
4. Upload test Swift package to swift-hosted
5. Verify download via group URLs
6. Verify health checks pass

## Constraints

- Swift scope: no dots (use underscores/hyphens)
- Nexus shutdown: 120s grace period for DB consistency
- H2 database: 100K component limit (sufficient for normal scale)
- CE limits: no export/import tasks (Pro-only)


## Docker Compose Reference Implementation

```yaml
services:
  nexus:
    image: sonatype/nexus3:3.91.1
    container_name: nexus
    # No external ports - internal only via Docker network
    expose:
      - "8081"
    volumes:
      - nexus-data:/nexus-data
    environment:
      INSTALL4J_ADD_VM_PARAMS: >
        -Xms2g -Xmx2g
        -XX:MaxDirectMemorySize=2g
        -Djava.util.prefs.userRoot=/nexus-data/javaprefs
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:8081/service/rest/v1/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    networks:
      - nexus-net
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
    stop_grace_period: 120s
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: nexus-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      nexus:
        condition: service_healthy
    networks:
      - nexus-net
    restart: unless-stopped

volumes:
  nexus-data:

networks:
  nexus-net:
    driver: bridge
```

## nginx.conf Reference

```nginx
server {
    listen 80;
    server_name nexus.local;

    location / {
        proxy_pass http://nexus:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Required for large uploads (AARs, Swift ZIPs)
        client_max_body_size 1G;
        proxy_request_buffering off;

        # Timeouts for long-running operations
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

## Bootstrap Script Flow

```
1. GET /service/rest/v1/system/eula -> save JSON response
2. Modify JSON: accepted = true (echo full disclaimer back)
3. POST /service/rest/v1/system/eula with modified JSON
4. Verify all Maven2 repos exist
5. Create Swift hosted repository
6. Create Swift proxy repository
7. Create Swift group repository (members: hosted, proxy)
8. Create CI user with ci-publisher role
9. Enable anonymous read access
10. Print all endpoint URLs
```

## File Structure

```
tdt/
├── docker-compose.yml          # Infrastructure definition
├── .env.template               # Environment variable template
├── .gitignore                  # Excludes nexus-data, .env, backups
├── nginx.conf                  # Reverse proxy config
├── scripts/
│   └── bootstrap-nexus.sh      # Post-deploy automation
├── docs/
│   └── research/               # Validated findings
└── openspec/
    └── changes/
        └── bootstrap-nexus-for-mobile/
```


## Additional Specifications

Beyond the core deployment, the following were researched and added:

### CI/CD Pipeline Patterns

**Jenkins (Declarative Pipeline)**
```groovy
pipeline {
    agent any
    stages {
        stage('Build AAR') {
            steps {
                sh './gradlew :library:assembleRelease'
            }
        }
        stage('Publish') {
            when { branch 'main' }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'nexus-publish',
                    usernameVariable: 'NEXUS_USER',
                    passwordVariable: 'NEXUS_PASS'
                )]) {
                    sh './gradlew :library:publishReleasePublicationToNexusRepository'
                }
            }
        }
    }
}
```

**GitLab CI**
```yaml
stages:
  - build
  - publish

build:
  stage: build
  script:
    - ./gradlew :library:assembleRelease
  artifacts:
    paths:
      - library/build/outputs/aar/

publish:
  stage: publish
  only:
    - main
    - tags
  script:
    - ./gradlew :library:publishReleasePublicationToNexusRepository
```

### Swift Package ZIP Structure

For binary Swift packages distributed via Nexus:

```
MyLib-1.0.0.zip
├── Package.swift          # Swift tools version 5.9+
└── MyLib.xcframework/     # Binary framework
    ├── Info.plist
    ├── ios-arm64/
    └── ios-arm64_x86_64-simulator/
```

Package.swift must declare the binary target:
```swift
// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "MyLib",
    products: [.library(name: "MyLib", targets: ["MyLib"])],
    targets: [.binaryTarget(name: "MyLib", path: "MyLib.xcframework")]
)
```

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXUS_ADMIN_PASS` | Yes | Initial admin password (from admin.password) |
| `NEXUS_USER` | Yes | CI service account username |
| `NEXUS_PASS` | Yes | CI service account password |
| `NEXUS_URL` | No | Default: http://localhost |
| `NEXUS_DATA_VOLUME` | No | Docker volume name (default: nexus-data) |

### Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `admin.password` is deleted after bootstrap
- [ ] CI credentials use least-privilege role
- [ ] Anonymous access is read-only
- [ ] Jenkins Credentials Plugin stores secrets
- [ ] GitLab CI variables are masked
- [ ] Custom encryption key configured in nexus.properties



## docker-compose.yml Reference Implementation

```yaml
services:
  nexus:
    image: sonatype/nexus3:${NEXUS_IMAGE_TAG:-3.91.1}
    container_name: nexus
    hostname: nexus
    expose:
      - "8081"
    volumes:
      - ${NEXUS_DATA_VOLUME:-nexus-data}:/nexus-data
    environment:
      INSTALL4J_ADD_VM_PARAMS: >
        -Xms${NEXUS_JVM_HEAP:-2g}
        -Xmx${NEXUS_JVM_HEAP:-2g}
        -XX:MaxDirectMemorySize=${NEXUS_JVM_MAXDIRECT:-2g}
        -Djava.util.prefs.userRoot=/nexus-data/javaprefs
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:8081/service/rest/v1/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
    networks:
      - nexus-net
    stop_grace_period: 120s
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: nexus-proxy
    ports:
      - "${NEXUS_HTTP_PORT:-80}:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      nexus:
        condition: service_healthy
    networks:
      - nexus-net
    restart: unless-stopped

volumes:
  nexus-data:

networks:
  nexus-net:
    driver: bridge
```

## nginx.conf Reference Implementation

```nginx
server {
    listen 80;
    server_name _;  # wildcard

    location / {
        proxy_pass http://nexus:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Large uploads (AARs, Swift ZIPs)
        client_max_body_size 1G;
        proxy_request_buffering off;
        
        # Timeouts for long operations
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://nexus:8081/service/rest/v1/status/check;
    }
}
```

## .env.template

```bash
# Nexus Docker image tag
# Minimum: 3.91.0 (Swift group support introduced)
# Recommended: 3.91.1 (latest stable)
NEXUS_IMAGE_TAG=3.91.1

# JVM Memory Settings
# Set Xms = Xmx for stable performance
NEXUS_JVM_HEAP=2g
NEXUS_JVM_MAXDIRECT=2g

# Docker volume name for Nexus data
NEXUS_DATA_VOLUME=nexus-data

# External port for nginx
NEXUS_HTTP_PORT=80

# Nexus URL (for bootstrap script)
NEXUS_URL=http://localhost
```

## .gitignore

```
# Nexus data (Docker volume backup)
nexus-data/

# Environment variables (secrets)
.env

# Initial admin password
admin.password

# Backup files
*.tar.gz
*.zip

# macOS
.DS_Store
```



## Validation Strategy

### Pre-Flight Checks (Before Start)

```bash
#!/bin/bash
# preflight.sh - Verify prerequisites

echo "=== Nexus Deployment Pre-Flight ==="

# 1. Docker running
docker info > /dev/null 2>&1
if [ $? -ne 0 ]; then echo "ERROR: Docker not running"; exit 1; fi
echo "✓ Docker running"

# 2. Docker Compose v2+
docker compose version > /dev/null 2>&1
if [ $? -ne 0 ]; then echo "ERROR: Docker Compose not available"; exit 1; fi
echo "✓ Docker Compose available"

# 3. Port available (or configured)
PORT=${NEXUS_HTTP_PORT:-80}
if lsof -i :$PORT > /dev/null 2>&1; then
  echo "WARNING: Port $PORT already in use"
fi
echo "✓ Port $PORT check complete"

# 4. Disk space
DISK_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$DISK_GB" -lt 5 ]; then
  echo "WARNING: Only ${DISK_GB}GB free (5GB recommended)"
fi
echo "✓ Disk check: ${DISK_GB}GB free"

# 5. Docker Compose YAML valid
docker compose config > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: docker-compose.yml is invalid"
  docker compose config  # Show errors
  exit 1
fi
echo "✓ docker-compose.yml valid"

echo ""
echo "All pre-flight checks passed. Ready to deploy."
```

### Docker Compose Config Validation

```bash
# Validate syntax (built into Docker Compose)
docker compose config

# Output shows resolved configuration with env vars substituted
```

### Bootstrap Verification

```bash
# Dry run (show what would happen)
./scripts/bootstrap-nexus.sh --dry-run

# Normal run (with actual API calls)
NEXUS_ADMIN_PASS=$(docker exec nexus cat /nexus-data/admin.password)   ./scripts/bootstrap-nexus.sh

# Verify after bootstrap
curl -u ci-user:$NEXUS_PASS http://localhost/service/rest/v1/repositories | jq .[].name
curl -u ci-user:$NEXUS_PASS http://localhost/service/rest/v1/security/users | jq .[].userId
```

### Version Verification

```bash
# Check Nexus version
curl -s http://localhost:8081/service/rest/v1/status/check | jq .

# Expected: nexusVersion >= "3.91.0"
# If lower: Swift group repository creation will fail
```
