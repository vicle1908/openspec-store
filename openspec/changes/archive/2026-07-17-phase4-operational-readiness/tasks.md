# Phase 4: Operational Readiness — Tasks

## Task 1: Add kafbat/kafka-ui to tools overlay

- [x] 1.1 Read current `deploy/docker-compose.tools.yaml`
- [x] 1.2 Add `kafka-ui` service block with pinned image, port 8080, `tools` profile, kafka health dependency
- [x] 1.3 Add `KAFKA_UI_VERSION` to `deploy/tools.env`

## Task 2: Create rollback rehearsal script

- [x] 2.1 Create `scripts/rehearse-rollback.sh` with 5-step rehearsal flow
- [x] 2.2 Make script executable (`chmod +x`)

## Task 3: Create operational runbooks

- [x] 3.1 Create `docs/runbooks/` directory
- [x] 3.2 Create `docs/runbooks/README.md` with template and conventions
- [x] 3.3 Document runbook structure and contribution guide

## Task 4: Create payment-service Dockerfile improvements

- [x] 4.1 Read current `Dockerfile.payment-service`
- [x] 4.2 Add `--platform=$BUILDPLATFORM` and `TARGETOS`/`TARGETARCH` args
- [x] 4.3 Add `-pgo=auto` to build command
- [x] 4.4 Add cache mounts for Go modules and build cache
- [x] 4.5 Add `HEALTHCHECK` to runtime stage
- [x] 4.6 Add OTEL and GOMEMLIMIT environment variables

## Task 5: Create openspec specs

- [x] 5.1 Create `openspec/specs/kafka-ui-tools-overlay/spec.md`
- [x] 5.2 Update `openspec/specs/rollback-rehearsal/spec.md` with Phase 4 requirements
- [x] 5.3 Create `openspec/specs/operational-runbooks/spec.md`
- [x] 5.4 Create `openspec/specs/payment-dockerfile-maturity/spec.md`

## Task 6: Wire agent config files

- [ ] 6.1 Add `.agent/`, `.claude/`, `.cursor/` to `.gitignore` tracked patterns
- [ ] 6.2 Document agent config directory conventions in README

## Task 7: Phase 4 proposal and design

- [x] 7.1 Create `openspec/changes/phase4-operational-readiness/proposal.md`
- [x] 7.2 Create `openspec/changes/phase4-operational-readiness/design.md`

## Verification Checklist

- [x] `deploy/docker-compose.tools.yaml` updated with kafka-ui service
- [x] `deploy/tools.env` contains KAFKA_UI_VERSION
- [x] `scripts/rehearse-rollback.sh` is executable
- [x] `docs/runbooks/README.md` exists with template
- [x] `services/payment-service/Dockerfile.payment-service` updated to canonical pattern
- [x] All 4 openspec specs created/updated
