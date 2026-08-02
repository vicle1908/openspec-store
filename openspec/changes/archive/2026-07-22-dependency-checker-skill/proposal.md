# Dependency Checker Skill Proposal

## Why

The platform has multiple services with dependencies (Go modules, Docker images) that need regular version checks and upgrades. Currently, this is done manually, which is time-consuming and error-prone. A dedicated agent skill would automate dependency checking, generate upgrade proposals, and ensure consistency across all services.

## What Changes

- **New Agent Skill**: Create a `dependency-checker` skill following the Agent Skills standard
- **Go Module Checking**: Automated checking of Go module versions across all services
- **Docker Image Checking**: Automated checking of Docker image versions in `deploy/tools.env`
- **Security Vulnerability Checking**: Automated checking for known vulnerabilities
- **Proposal Generation**: Automatic generation of openspec proposals for upgrades
- **Integration**: Integration with existing openspec workflow for tracking and implementation

## Capabilities

### New Capabilities

- `dependency-checking`: Automated dependency version checking for Go modules and Docker images
- `docker-image-checking`: Docker image version checking via Docker Hub API
- `security-vulnerability-checking`: Security vulnerability checking for dependencies
- `upgrade-proposal-generation`: Automatic generation of openspec upgrade proposals

### Modified Capabilities

- (None - this is a new skill)

## Impact

### Affected Code
- `.agent/skills/dependency-checker/` — New skill directory
- `scripts/check-deps.sh` — Dependency checking script
- `scripts/check-docker-images.sh` — Docker image checking script

### Affected Infrastructure
- Docker Hub API integration
- GitHub API integration
- OpenSpec workflow integration

### Dependencies
- Docker Hub API (for image version checking)
- GitHub API (for release information)
- OpenSpec CLI (for proposal generation)

### Compatibility
- **Non-breaking** — New skill does not affect existing functionality
- Complements existing dependency update workflows (Dependabot, Renovate)

### Rollout
1. Create skill directory and files
2. Test dependency checking
3. Test proposal generation
4. Deploy to production

### Rollback
- Remove skill directory
- Remove generated proposals
- No impact on existing services
