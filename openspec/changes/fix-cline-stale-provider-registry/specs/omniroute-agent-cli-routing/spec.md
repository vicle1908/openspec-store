## ADDED Requirements

### Requirement: Cline custom provider entries SHALL be registry-backed

Every custom Cline provider entry used for OmniRoute SHALL have a matching provider registry entry in `~/.cline/data/settings/models.json` with the same provider ID, a non-empty model registry, and compatible endpoint metadata. Entries that are absent from the registry SHALL NOT remain as selectable OmniRoute settings entries.

#### Scenario: stale entry is removed

- **WHEN** a Cline settings provider ID has no matching `models.json` registry entry
- **THEN** the stale settings entry SHALL be removed
- **AND** unrelated providers SHALL remain unchanged
- **AND** the existing default selection SHALL remain unchanged unless it points to the removed stale entry, in which case it SHALL be repaired to the verified working provider.

#### Scenario: registry-backed entry is exercised

- **WHEN** a Cline custom provider is treated as a supported route
- **THEN** its ID SHALL resolve through the installed CLI
- **AND** an explicit sentinel call SHALL pass before the route is reported as verified.

### Requirement: The retained Cline OmniRoute provider SHALL use the canonical source-derived model

When the Cline OmniRoute cleanup retains `openai-compatible` as the working provider, its model SHALL be the source-derived canonical model `sh/gpt-5.6-sol`, and its endpoint SHALL remain `http://localhost:20128`.

#### Scenario: noncanonical retained model is corrected

- **WHEN** the retained `openai-compatible` entry uses a noncanonical model
- **THEN** the entry SHALL be updated to `sh/gpt-5.6-sol`
- **AND** a cleanup4-specific live sentinel through the final provider/model pair SHALL be recorded before closure.
