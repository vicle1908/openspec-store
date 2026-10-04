# Spec Delta

## MODIFIED Requirements

### Requirement: Cleanup candidates have explicit safety classifications

Every cleanup candidate SHALL be classified as read-only evidence,
rebuildable cache, operator-reviewed irreversible data, or protected stateful
data before an action is proposed. Tool-installation duplication and
Git-backed snapshot-store object accumulation SHALL be classified as candidate
categories with an owning-tool command, and SHALL NOT be treated as direct
filesystem deletion targets.

#### Scenario: Rebuildable cache is classified

- **WHEN** the audit identifies Go build cache, npm npx cache, pnpm orphaned
  packages, Docker build cache, or simulator dyld cache
- **THEN** the plan identifies its owning tool, estimated recovery,
  regeneration cost, prerequisites, and supported cleanup command

#### Scenario: Tool-installation duplication is classified

- **WHEN** the audit identifies the same tool installed in more than one
  location, such as a global npm command and a toolbelt dependency of the same
  name
- **THEN** the plan identifies the tool, each installation path, each measured
  size, the authoritative copy resolved on the path, and the verification
  required before the duplicate is reclaimable
- **AND** the plan MUST NOT treat duplication alone as authorization to delete
  a copy

#### Scenario: Git snapshot-store object accumulation is classified

- **WHEN** the audit identifies a Git-backed snapshot store whose loose objects
  materially outweigh its packed history
- **THEN** the plan classifies the loose objects as reclaimable-by-repack and
  names the owner command that performs the repack
- **AND** it MUST NOT propose direct deletion of Git object files

#### Scenario: Stateful or personal data is classified

- **WHEN** the audit identifies Photos, Downloads projects, source,
  verification evidence, Docker volumes or images, active kind clusters, IDE
  settings, cloud-provider state, Android packages or AVDs, local models, or
  simulator runtimes
- **THEN** the plan marks the item protected until a complete verified-unused
  eligibility record exists
- **AND** it MUST NOT include the item in a bulk cleanup action
