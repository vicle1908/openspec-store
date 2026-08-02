# Spec Evolution Log

## 2026-05-05: Initial Proposal
- Created base proposal with scope, goals, success criteria
- Identified CE limits, scope naming risks

## 2026-05-05: Design Document
- Added architecture diagram with Docker host layout
- Key decisions: Docker Compose, named volume, Alpine image
- Data flow for CI builds and developer machines
- Validation strategy: live container testing

## 2026-05-05: Specification Enhancements

### nexus-deployment spec (v2)
- ADDED: Graceful shutdown scenario (120s grace period)
- ADDED: Named volume UID handling
- ADDED: Port isolation (nexus internal, nginx external)
- ADDED: JVM memory tuning (-Xms/-Xmx, 2/3 RAM rule)
- ADDED: File handle limits (ulimits 65536)
- ADDED: Restart policy (unless-stopped)

### repository-setup spec (v2)
- ADDED: SNAPSHOT support scenario
- ADDED: Idempotent bootstrap scenario
- ADDED: Swift proxy remote URL configuration
- ADDED: Write policies for releases vs snapshots

### ci-integration spec (v2)
- ADDED: Jenkins credential management pattern
- ADDED: GitLab CI variable management pattern
- ADDED: Least-privilege role scenario

### client-configuration spec (v2)
- ADDED: Gradle credentials from environment
- ADDED: Gradle repository ordering
- ADDED: Swift package ZIP structure
- ADDED: SPM registry authentication

### ci-pipelines spec (NEW)
- Jenkins Declarative Pipeline for Android
- GitLab CI for Android
- Jenkins Pipeline for iOS
- GitLab CI for iOS
- Version derivation from Git tags

### environment-secrets spec (NEW)
- .env.template requirement
- .gitignore safety rules
- CI credential injection patterns
- Admin password lifecycle

## 2026-05-05: Tasks Expansion

### Original: 28 tasks
### After first update: 45 tasks
### After second update: 62 tasks

New sections added:
- Section 8: CI/CD Pipeline Configuration (Jenkins + GitLab)
- Section 9: Environment and Secrets
- Section 10: Advanced Topics (optional)

## Research Sources
1. Sonatype Nexus Help: System Requirements, Memory Overview
2. Apple Developer: Binary Frameworks in Swift Packages
3. SwiftLee: Binary Targets in SPM
4. Gradle User Manual: Maven Publish Plugin
5. GitLab Docs: CI/CD Maven publishing
6. Jenkins Docs: Credentials Plugin
7. Live container validation: All API calls tested
