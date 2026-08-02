# Tasks: Dependency Checker Skill

## 1. Skill Setup

- [x] 1.1 Create skill directory structure `.agent/skills/dependency-checker/`
- [x] 1.2 Create SKILL.md with frontmatter and instructions
- [x] 1.3 Create scripts directory

## 2. Go Module Checking

- [x] 2.1 Create `scripts/check-go-deps.sh` script
- [x] 2.2 Implement go.mod parsing logic
- [x] 2.3 Implement pkg.go.dev API integration
- [x] 2.4 Implement version comparison logic
- [x] 2.5 Test Go module checking

## 3. Docker Image Checking

- [x] 3.1 Create `scripts/check-docker-images.sh` script
- [x] 3.2 Implement tools.env parsing logic
- [x] 3.3 Implement Docker Hub API integration
- [x] 3.4 Implement image version comparison
- [x] 3.5 Implement multi-architecture checking
- [x] 3.6 Test Docker image checking

## 4. Security Vulnerability Checking

- [x] 4.1 Create `scripts/check-security.sh` script
- [x] 4.2 Implement CVE database integration
- [x] 4.3 Implement Go vulnerability checking
- [x] 4.4 Implement Docker image vulnerability checking
- [x] 4.5 Test security vulnerability checking

## 5. Proposal Generation

- [x] 5.1 Create `scripts/generate-proposal.sh` script
- [x] 5.2 Implement openspec proposal generation
- [x] 5.3 Implement task generation
- [x] 5.4 Implement spec generation
- [x] 5.5 Implement design generation
- [x] 6.6 Test proposal generation

## 6. Rules

- [x] 6.1 Create `rules/go-version-check.md`
- [x] 6.2 Create `rules/docker-version-check.md`
- [x] 6.3 Create `rules/security-check.md`

## 7. Testing

- [x] 7.1 Test Go module checking end-to-end
- [x] 7.2 Test Docker image checking end-to-end
- [x] 7.3 Test security vulnerability checking end-to-end
- [x] 7.4 Test proposal generation end-to-end

## 8. Documentation

- [x] 8.1 Update README.md with skill usage
- [x] 8.2 Document API integrations
- [x] 8.3 Document configuration options
