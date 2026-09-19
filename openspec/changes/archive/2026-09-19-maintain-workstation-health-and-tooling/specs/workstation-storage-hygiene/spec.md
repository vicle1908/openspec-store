# Spec Delta: Workstation Storage Hygiene

## MODIFIED Requirements

### Requirement: Cleanup candidates have explicit safety classifications

Every cleanup candidate SHALL be classified as rebuildable ephemeral cache (Tier 1), review-first build artifacts or completed installers (Tier 2), or protected stateful assets (Tier 3) before an action is proposed or executed.

#### Scenario: Rebuildable cache is classified

- **WHEN** the audit identifies Go build cache, npm npx cache, pnpm orphaned
  packages, Docker build cache, or simulator dyld cache
- **THEN** the plan identifies its owning tool, estimated recovery,
  regeneration cost, prerequisites, and supported cleanup command

#### Scenario: Stateful or personal data is classified

- **WHEN** the audit identifies Photos, Downloads projects, source,
  verification evidence, Docker volumes or images, active kind clusters, IDE
  settings, cloud-provider state, Android packages or AVDs, local models, or
  simulator runtimes
- **THEN** the plan marks the item protected until a complete verified-unused
  eligibility record exists
- **AND** it MUST NOT include the item in a bulk cleanup action

#### Scenario: Multi-tier safety classification
- **WHEN** the storage audit discovers candidate targets across system, developer, and application caches
- **THEN** it categorizes package manager caches, temporary staging files, and purgeable memory under Tier 1
- **AND** it categorizes local build caches and completed installer DMGs under Tier 2 requiring explicit user confirmation
- **AND** it MUST classify Docker raw virtual disks, persistent database volumes, active browser databases, and active project virtual environments as protected Tier 3 assets excluded from deletion.

## ADDED Requirements

### Requirement: Verified post-reclamation headroom and state verification

The workflow SHALL measure and record total reclaimed capacity, resulting free disk space, and application integrity following any multi-tier cleanup action.

#### Scenario: Reclaimed space and integrity verification
- **WHEN** approved Tier 1 and Tier 2 cleanups are completed
- **THEN** the workflow verifies that total available disk space increases accordingly
- **AND** it validates that installed application binaries, IDE configurations, and developer repositories remain undamaged and operational.
