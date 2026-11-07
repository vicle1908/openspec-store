# workspace-index-freshness Specification Delta

## MODIFIED Requirements

### Requirement: Official provider identity

The workspace refresh mechanism SHALL use GitNexus `1.6.12` and Graphify from `https://github.com/Graphify-Labs/graphify`, package `graphifyy`, CLI `graphify`, pinned at `0.9.103`.

#### Scenario: Provider identity is verified

- **WHEN** the refresh script starts
- **THEN** it SHALL verify the installed GitNexus (`1.6.12`) and Graphify (`0.9.103`) executable versions
- **AND** it SHALL fail closed for a provider version mismatch unless the operation is explicitly diagnostic
- **AND** it SHALL NOT invoke an alternate Graphify package or provider

#### Scenario: Graphify 0.9.42 features are available

- **WHEN** a Graphify refresh runs on `0.9.103`
- **THEN** non-regular files SHALL be skipped without hanging extraction
- **AND** same-length rewrites SHALL be detected by incremental update
- **AND** graph provenance SHALL be derived from the analyzed repository
- **AND** canonical POSIX source paths SHALL be used
