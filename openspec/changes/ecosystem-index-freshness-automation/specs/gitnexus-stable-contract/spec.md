## ADDED Requirements

### Requirement: Authorized scheduled workspace index recovery

A workspace-local scheduler SHALL perform bounded GitNexus index-only recovery only for an explicit reviewed repository inventory and SHALL NOT expose mutation through the consumer MCP adapter.

#### Scenario: Scheduled recovery is approved

- **WHEN** an operator explicitly approves installation of the workspace scheduler for a reviewed inventory
- **THEN** the scheduler MAY run the already installed pinned GitNexus `1.6.9` CLI with `analyze --index-only --default-branch <inventory-branch>` only for the exact inventory entries
- **AND** each run SHALL record the normalized inventory digest, canonical repository root, target HEAD, provider identity, and result status
- **AND** the scheduler SHALL reject `--force`, embeddings, PDG, setup, clean, group operations, package fallback, and repositories outside the inventory

#### Scenario: Inventory changes after approval

- **WHEN** the inventory is added to, removed from, or changed after scheduler approval
- **THEN** the scheduler SHALL fail closed until the changed inventory is explicitly reviewed and approved
- **AND** it SHALL not infer authorization from dynamic repository discovery or group membership

#### Scenario: Consumer adapter requests mutation

- **WHEN** a consumer requests refresh, analyze, or another mutation through the stable GitNexus adapter
- **THEN** the adapter SHALL continue to reject the request before provider execution
- **AND** the workspace scheduler's separate operator path SHALL not be exposed as an MCP mutation tool
