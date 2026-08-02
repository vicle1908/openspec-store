## Purpose

Ensure deployment documentation covers the full compose model including security overlays, container hardening, and validation.

## ADDED Requirements

### Requirement: Deploy README covers security overlays

`deploy/README.md` SHALL document security-related compose overlays.

#### Scenario: Production-contract overlay documented
- **WHEN** a developer reads `deploy/README.md`
- **THEN** they find documentation for production-contract overlay (hardened containers, mTLS, workload identities)

#### Scenario: Local-fast overlay documented
- **WHEN** a developer reads `deploy/README.md`
- **THEN** they find documentation for local-fast overlay (non-evidentiary local development)

### Requirement: Deploy README covers container hardening

`deploy/README.md` SHALL document container hardening configuration.

#### Scenario: Hardening section exists
- **WHEN** a developer reads `deploy/README.md`
- **THEN** they find documentation for hardened-role anchor, security labels, and read-only containers

### Requirement: Deploy README covers runtime contract

`deploy/README.md` SHALL document the runtime contract and validation scripts.

#### Scenario: Runtime contract documented
- **WHEN** a developer reads `deploy/README.md`
- **THEN** they find documentation for verification/runtime-contract.json and validation scripts
