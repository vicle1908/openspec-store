## ADDED Requirements

### Requirement: Symlink-safe artifact root validation

`validate_artifact_root()` SHALL scan user-supplied path components for symlinks before canonical resolution. The validation SHALL reject paths where any component is a symlink, using the expanded (not resolved) path.

#### Scenario: Symlink component rejected

- **GIVEN** an artifact root path containing a symlink component
- **WHEN** `validate_artifact_root()` is called
- **THEN** a `ValueError` SHALL be raised identifying the symlink component

#### Scenario: Direct symlink root rejected

- **GIVEN** the artifact root itself is a symlink
- **WHEN** `validate_artifact_root()` is called
- **THEN** a `ValueError` SHALL be raised

#### Scenario: Clean path accepted

- **GIVEN** an artifact root path with no symlink components
- **WHEN** `validate_artifact_root()` is called
- **THEN** the canonical resolved path SHALL be returned


### Requirement: Deny-only authority profile

AuthorityConfig fields `allowed_shell`, `allowed_code_execution`, `allowed_external_mutation`, and `allowed_source_write` SHALL accept only `False`. Construction with `True`, `1`, `"true"`, `"1"`, or any other coercion candidate SHALL raise `ValidationError`. Post-construction assignment SHALL also be rejected. Nested `HarnessConfig(authority={...})` overlays containing truthy values SHALL fail validation.

#### Scenario: Literal False is accepted

- **GIVEN** an `AuthorityConfig` instance with all deny-only fields set to `False`
- **WHEN** the instance is constructed
- **THEN** construction SHALL succeed

#### Scenario: Truthy value rejected at construction

- **GIVEN** a deny-only authority field
- **WHEN** `AuthorityConfig` is constructed with value `True`, `1`, `"true"`, or `"1"` for that field
- **THEN** a `ValidationError` SHALL be raised

#### Scenario: Truthy value rejected in nested overlay

- **GIVEN** a `HarnessConfig` with an authority overlay
- **WHEN** the overlay contains `allowed_shell: true`
- **THEN** a `ValidationError` SHALL be raised during nested construction

#### Scenario: Post-construction assignment rejected

- **GIVEN** an `AuthorityConfig` instance with all deny-only fields set to `False`
- **WHEN** post-construction assignment `allowed_shell = True` is attempted
- **THEN** a `ValidationError` SHALL be raised and the value SHALL remain `False`

#### Scenario: Structural read-only boundaries (Jira, GitLab)

- **GIVEN** the `JiraTool` class definition
- **WHEN** inspecting its public method set
- **THEN** it SHALL expose only `get_ticket`, `search`, and `get_links` — no mutation methods

- **GIVEN** the `read_only_targets` field in `AuthorityConfig`
- **WHEN** `"jira"` and `"gitlab"` are present in the list
- **THEN** structural safety is enforced by code design, not by dedicated config fields

### Requirement: Deny-only stage composition policy

`StageCompositionContext` SHALL reject caller-supplied `CapabilityAuthorityPolicy` values that contain any filesystem roots, shell commands, network hosts, runtime-authoring roots, authority grants, or disabled audit mode. The default empty policy with audit enabled SHALL remain accepted.

#### Scenario: Permissive capability policy rejected

- **GIVEN** a stage composition context with a non-empty filesystem, shell, network, runtime-authoring, or grant policy
- **WHEN** the context is constructed
- **THEN** construction SHALL raise `ValueError` identifying the deny-only boundary

#### Scenario: Disabled audit policy rejected

- **GIVEN** a stage composition context with `audit_enabled=False`
- **WHEN** the context is constructed
- **THEN** construction SHALL raise `ValueError`

#### Scenario: Default capability policy accepted

- **GIVEN** a stage composition context with the default capability policy
- **WHEN** the context is constructed
- **THEN** construction SHALL succeed
