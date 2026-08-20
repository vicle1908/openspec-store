## MODIFIED Requirements

### Requirement: VI-1: pydantic-ai Import Confinement

Pydantic AI runtime types SHALL remain isolated behind the designated internal
adapter boundary while remaining intentionally available through the documented
public SDK and composition modules that forward runtime option and capability
types. The vendor boundary SHALL be enforced by the public import contract and
focused lint/tests; it SHALL not claim that every runtime import outside
`src/agent_core/_ai/` is invalid when public SDK modules intentionally forward
those types.

#### Scenario: Public SDK runtime type import

- **WHEN** a consumer imports a documented runtime option or typed capability from the public SDK
- **THEN** the import SHALL succeed through the supported facade
- **AND** the facade SHALL preserve the upstream type identity required by the public composition boundary

#### Scenario: Internal implementation remains isolated

- **WHEN** an internal module needs a Pydantic AI primitive
- **THEN** it SHALL use the designated internal adapter boundary where applicable
- **AND** it SHALL not expose a second undocumented vendor abstraction

#### Scenario: Focused lint reflects actual boundary

- **WHEN** the repository runs the configured focused lint checks
- **THEN** the result SHALL enforce the actual import boundary
- **AND** it SHALL not report the obsolete blanket TC002 guarantee as a product contract

#### Scenario: Import outside _ai/ triggers lint

- **GIVEN** a non-public internal module bypasses the designated vendor boundary
- **WHEN** the focused repository lint runs
- **THEN** an actionable boundary diagnostic SHALL be raised
- **AND** an intentional documented public SDK import SHALL remain accepted

#### Scenario: Import inside _ai/ is allowed

- **GIVEN** an internal adapter imports a Pydantic AI primitive inside `src/agent_core/_ai/`
- **WHEN** the focused repository lint runs
- **THEN** the import SHALL be accepted

### Requirement: VI-2: TC002 Ruff Enforcement

The repository SHALL retain deterministic focused checks for the documented
Pydantic AI boundary and public SDK exports. Those checks MAY use Ruff or AST
validation where appropriate, but SHALL not promise a TC002 configuration that
forbids intentional public runtime-type forwarding or bypasses the internal
adapter boundary.

#### Scenario: Public export check

- **GIVEN** a documented runtime option is exported from the SDK facade
- **WHEN** the focused vendor-boundary check runs
- **THEN** the export and import path SHALL be accepted

#### Scenario: Undocumented internal import is detected

- **GIVEN** an internal module bypasses the designated boundary
- **WHEN** the focused vendor-boundary check runs
- **THEN** the check SHALL fail with a stable actionable diagnostic

#### Scenario: TC002 configuration exists

- **GIVEN** the repository's focused lint configuration is inspected
- **WHEN** the vendor-boundary check is run
- **THEN** it SHALL contain only rules compatible with intentional public SDK forwarding
- **AND** it SHALL not assert the obsolete blanket TC002 prohibition
