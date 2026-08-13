## MODIFIED Requirements

### Requirement: Single config loading function

The system SHALL expose one canonical agent-profile resolution boundary that returns an immutable effective profile containing model, fallbacks, model behavior, provider metadata, runtime values, environment-key metadata, and redacted source provenance. Before resolving any effective field, one resolution request SHALL capture as one coherent immutable input snapshot the agent identity; effective root and environment profile; selected dotenv, global-configuration, and agent-overlay identities; non-secret source fingerprints; overlay-key policy; a detached copy of explicit overrides; the presence and values of every relevant registered non-secret environment input; and only redacted presence and provider-binding metadata for relevant registered secret inputs. The resolver, typed result, and compatibility projection SHALL consume only that captured snapshot and SHALL NOT reread files, process environment, caller-owned override objects, or loader identity during the request. Source fingerprints SHALL identify non-secret configuration material and MUST NOT contain or be derived from protected values. Existing mapping-based loading SHALL remain only as a compatibility projection of that same snapshot and SHALL NOT implement a second precedence chain. Every primary or fallback identifier declared through the compatibility path MUST pass the same canonical grammar, provider-registration, and fail-closed validation as the typed profile before a mapping is returned. Any cached effective profile or compatibility projection MUST be reused only when its complete captured request identity and effective input state are equivalent; reuse SHALL NOT cross agent, root, environment-profile, selected-path, source-fingerprint, overlay-policy, explicit-override, registered-environment, or secret-availability/provider-binding boundaries.

#### Scenario: Resolved profile is internally consistent

- **WHEN** a consumer resolves its agent profile
- **THEN** the profile's effective model, fallbacks, behavior settings, providers, runtime values, provenance, root identity, and source fingerprints SHALL describe the same resolution snapshot
- **AND** downstream consumers SHALL NOT need to reload YAML or dotenv files

#### Scenario: Compatibility mapping uses the same sources

- **WHEN** a legacy caller requests the mapping projection for an agent
- **THEN** the projection SHALL be derived from the canonical loading primitives and captured source snapshot
- **AND** equivalent fields SHALL match the typed resolved profile

#### Scenario: Function returns merged config

- **WHEN** the compatibility mapping is requested for an agent
- **THEN** it SHALL contain the merged model and runtime projection from the same secure source snapshot

#### Scenario: Explicit agent config path overrides the standard overlay

- **GIVEN** a caller supplies an explicit agent-overlay path
- **WHEN** the profile and source-preserving overlay are loaded
- **THEN** both SHALL use that path instead of the standard agent YAML path
- **AND** the compatibility mapping SHALL pass the same explicit path into canonical validation
- **AND** diagnostics SHALL identify the explicit source path without exposing values

#### Scenario: Function is idempotent within a process

- **WHEN** the compatibility mapping is requested twice with unchanged effective inputs
- **THEN** both returned mappings SHALL be value-equivalent

#### Scenario: Unknown agent name returns global config only

- **GIVEN** no overlay exists for a valid unknown agent name
- **WHEN** its compatibility mapping is requested
- **THEN** global configuration and defaults SHALL remain available without error

#### Scenario: Default strict key policy

- **WHEN** `load_agent_config("agent-core")` is called without `allowed_overlay_keys`
- **AND** the agent YAML contains a top-level key `gate: {approvers: ["x"]}`
- **THEN** a `ConfigError` SHALL be raised (the default `{"model", "runtime"}` policy applies)

#### Scenario: Harness-expanded key policy accepts domain keys without error

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate", "persistence", "authority"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}` and `persistence: {durable: true}`
- **THEN** the call SHALL succeed without `ConfigError`
- **AND** the returned dict SHALL retain unrelated global sections unchanged; only `model` and `runtime` are affected by the overlay merge; domain keys validated by the allowed set SHALL not cause `ConfigError` but SHALL not be merged

#### Scenario: Cache isolation by allowed-key set

- **GIVEN** `load_agent_config("agent", allowed_overlay_keys={"model", "runtime"})` is called
- **WHEN** `load_agent_config("agent", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **THEN** both calls SHALL resolve independently with no cache collision

#### Scenario: Domain keys excluded from merged result

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}`
- **THEN** the returned dict SHALL retain unrelated global sections unchanged
- **AND** the agent overlay's `gate` section SHALL NOT be merged into or override any global section
- **AND** agent-harness SHALL obtain `gate` from `load_agent_overlay()`

#### Scenario: Compatibility primary or fallback is invalid

- **GIVEN** a selected compatibility source declares a malformed, localized, or unregistered primary or fallback identifier
- **WHEN** the mapping projection is requested
- **THEN** canonical resolution SHALL fail with the logical model field and redacted source identity
- **AND** no partially validated mapping SHALL be returned
- **AND** resolution SHALL NOT fall through to a lower-priority model

#### Scenario: Captured snapshot remains coherent

- **GIVEN** one resolution request has captured its selected source identities and registered environment inputs
- **WHEN** a source changes before a downstream constructor consumes the returned profile or mapping
- **THEN** that returned result SHALL remain internally consistent with its captured fingerprints
- **AND** a later resolution request SHALL observe the changed source as a new snapshot

#### Scenario: Registered environment inputs are captured once

- **GIVEN** one resolution request has captured its registered consumer-specific and shared non-secret environment inputs
- **AND** it has captured only redacted availability and provider-binding metadata for relevant registered secret inputs
- **WHEN** one of those process-environment inputs changes before the returned profile or compatibility projection is consumed
- **THEN** the in-flight result SHALL continue to use only the state captured for that request
- **AND** no field in the result SHALL combine values, provenance, or availability metadata from the later process-environment state
- **AND** a later resolution request SHALL observe the changed registered input as a new snapshot

#### Scenario: Unregistered environment changes do not alter profile identity

- **GIVEN** the effective root, environment profile, selected source identities, explicit overrides, allowed overlay keys, and all relevant registered environment inputs are unchanged
- **WHEN** an unrelated unregistered process-environment value changes
- **THEN** the effective profile and compatibility projection SHALL remain value-equivalent
- **AND** the unrelated value SHALL NOT appear in configuration identity, provenance, source fingerprints, diagnostics, or cache eligibility

#### Scenario: Explicit overrides are detached at capture

- **GIVEN** a caller supplies a mutable explicit-override mapping
- **WHEN** the caller mutates that mapping after the resolution request captures its inputs
- **THEN** the in-flight profile and compatibility projection SHALL retain the originally captured override values and provenance
- **AND** they SHALL retain no mutable reference through which the caller can alter the captured snapshot
- **AND** a later request supplied with the modified mapping SHALL resolve it as a distinct input state

#### Scenario: Protected inputs do not become source fingerprints

- **GIVEN** the selected environment file or process environment contains protected provider credential material
- **WHEN** the resolver produces source fingerprints, configuration identity, diagnostics, provenance, cache metadata, or a compatibility projection
- **THEN** none of those surfaces SHALL contain a raw, encoded, hashed, or otherwise value-derived representation of the protected material
- **AND** they MAY retain only the non-secret source identity, registered key-name metadata, availability state, and canonical provider binding needed by the public contract
- **AND** fingerprints for non-secret YAML or explicit configuration material SHALL remain distinguishable from protected-input metadata

#### Scenario: Cache reuse requires complete effective identity

- **GIVEN** an effective profile or compatibility projection is eligible for caching
- **WHEN** a later request differs in agent identity, root, environment profile, selected dotenv or YAML path, non-secret source fingerprint, allowed overlay keys, explicit overrides, relevant registered non-secret environment state, or secret availability/provider binding
- **THEN** the prior effective result SHALL NOT be reused for the later request
- **AND** the later request SHALL resolve and validate its own coherent snapshot
- **AND** cache metadata SHALL NOT expose protected values

#### Scenario: Concurrent resolutions keep captured inputs isolated

- **GIVEN** two simultaneous requests use different roots, environment profiles, selected paths, explicit overrides, allowed overlay keys, or registered environment states
- **WHEN** both requests resolve typed profiles or compatibility projections
- **THEN** each result SHALL contain only its own captured effective values, provenance, source identities, fingerprints, and redacted credential metadata
- **AND** neither request SHALL overwrite, supply, or cache-substitute any input or result belonging to the other
