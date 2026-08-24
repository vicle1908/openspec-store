## ADDED Requirements

### Requirement: Container bind mappings preserve canonical TDT home semantics

Every supported Docker deployment SHALL distinguish the host TDT home source from the container TDT home target. When the host `TDT_HOME` value is absent or empty, the host bind source SHALL resolve to the same canonical default selected by tdt-core. Bind targets SHALL preserve the `$TDT_HOME/<kind>/<app>/<name>` layout, and least-privilege services MUST NOT receive unrelated credential or state subtrees.

#### Scenario: Host root is unset

- **WHEN** Compose renders while host `TDT_HOME` is absent
- **THEN** the host bind source SHALL resolve below the canonical user-home TDT root
- **AND** it SHALL not resolve to `/home/agent/tdt` or another container-only path on the host

#### Scenario: Isolated verification root is explicit

- **WHEN** a verification run supplies a disposable absolute host TDT root
- **THEN** every selected bind source SHALL remain below that root
- **AND** the container's canonical kind-first paths SHALL map back to the corresponding host subtrees

#### Scenario: Observability services receive least-privilege mounts

- **WHEN** health-poller or log-collector mounts are rendered
- **THEN** required `state/observability`, `config/observability`, `logs`, and approved deployment-log paths SHALL retain canonical meanings
- **AND** the services SHALL not mount the host `credentials` subtree or the complete TDT home

#### Scenario: Unsupported relative host root is supplied

- **WHEN** a deployment receives a non-empty relative host TDT root
- **THEN** preflight SHALL fail before Docker mutation
- **AND** it SHALL identify the invalid path without printing secret-shaped file contents

