# Design: Dependency Checker Skill

## Context

The platform has multiple services with dependencies (Go modules, Docker images) that need regular version checks and upgrades. Currently, this is done manually, which is time-consuming and error-prone. The dependency-checker skill will automate this process following the Agent Skills standard.

### Current State
- Go modules in `services/*/go.mod` and `platform/go.mod`
- Docker images in `deploy/tools.env`
- Manual version checking and upgrade proposals
- Integration with openspec workflow for tracking

### Constraints
- Must follow Agent Skills standard format
- Must integrate with existing openspec workflow
- Must work with Docker Hub API and GitHub API
- Must support macOS Apple Silicon and linux/arm64

## Goals / Non-Goals

**Goals:**
- Automate dependency version checking
- Generate upgrade proposals in openspec format
- Check security vulnerabilities
- Integrate with existing CI/CD workflows

**Non-Goals:**
- Automatic dependency updates (use Dependabot/Renovate for that)
- Real-time monitoring of dependency changes
- Complex dependency graph analysis

## Decisions

### Decision 1: Skill Structure
**Chosen:** Follow Agent Skills standard with SKILL.md, scripts/, and rules/
**Rationale:** Consistent with existing skills, easy to maintain, follows established patterns
**Alternatives considered:** Custom format, inline scripts (rejected for maintainability)

### Decision 2: Docker Hub API for Image Checking
**Chosen:** Use Docker Hub API for checking image versions
**Rationale:** Official API, returns JSON with tag names and metadata, supports pagination
**Alternatives considered:** Docker CLI (slower), Skopeo (additional dependency)

### Decision 3: pkg.go.dev for Go Module Checking
**Chosen:** Use pkg.go.dev for checking Go module versions
**Rationale:** Official Go module registry, returns version history
**Alternatives considered:** GitHub API (less complete), Go Proxy (less user-friendly)

### Decision 4: OpenSpec Integration
**Chosen:** Generate proposals in openspec format
**Rationale:** Consistent with existing workflow, easy to track and implement
**Alternatives considered:** Custom format, Markdown reports (less integrated)

## Risks / Trade-offs

**Risk:** API rate limiting from Docker Hub/GitHub
**Mitigation:** Implement caching and retry logic

**Risk:** API changes or deprecation
**Mitigation:** Use stable APIs, implement fallback mechanisms

**Risk:** False positives in version checking
**Mitigation:** Manual review before implementing upgrades

## Migration Plan

1. Create skill directory and files
2. Test dependency checking scripts
3. Test proposal generation
4. Deploy to production
5. Monitor and iterate

## Rollback Strategy

- Remove skill directory
- Remove generated proposals
- No impact on existing services
