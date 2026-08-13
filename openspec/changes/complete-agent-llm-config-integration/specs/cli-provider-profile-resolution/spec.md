## MODIFIED Requirements

### Requirement: Selection failure modes

The selector SHALL treat a requested CLI adapter identity and a selected canonical provider identity as distinct typed identities. Candidate discovery SHALL use only explicit `cli_provider` declarations and `defaults.cli_models` relationships in a valid canonical catalog; it SHALL NOT infer a canonical provider identity from a CLI name, protocol, model, endpoint, executable, or credential availability. A successful selection and its provider-neutral projection SHALL preserve both the requested CLI adapter identity and selected canonical provider ID, use the CLI identity for adapter capability and executable validation, and use the canonical provider ID for provider-owned credential metadata. The selector SHALL distinguish absence of an applicable canonical CLI mapping from a canonical configuration that declares a relationship for the requested CLI but cannot produce one valid selection. It SHALL return no selection only when the requested CLI provider is genuinely absent from a valid canonical catalog—meaning that no provider declaration or default mapping targets that CLI identity—or when the profile is valid and legacy-only. Once any canonical provider or default mapping declares a relationship for the requested CLI identity, a missing, undefined, ambiguous, mismatched, unsupported, or otherwise invalid provider/model relationship MUST fail closed before local fallback or process launch.

#### Scenario: CLI provider absent from valid catalog

- **GIVEN** a valid canonical catalog with `codex` and `claude` but no declaration for `kimi`
- **WHEN** selection is requested for `kimi`
- **THEN** the return value SHALL indicate no canonical selection
- **AND** the consumer MAY use its permitted local configuration

#### Scenario: Canonical config exists but is invalid

- **GIVEN** a canonical catalog maps `codex` to a nonexistent model
- **WHEN** the selector resolves for `codex`
- **THEN** selection SHALL fail before any process launch
- **AND** the error SHALL identify the invalid alias without exposing protected values
- **AND** the consumer SHALL NOT use local fallback

#### Scenario: Legacy-only profile returns None

- **GIVEN** a legacy-only profile with no per-CLI model mapping and no new-schema providers
- **WHEN** selection is requested for `codex`
- **THEN** the return value SHALL indicate no canonical selection
- **AND** the consumer MAY fall back to its local configuration

#### Scenario: Declared provider has no valid model selection

- **GIVEN** the canonical catalog declares a provider for `codex` but no model can be selected for it
- **WHEN** selection is requested for `codex`
- **THEN** selection SHALL fail before local fallback or process launch
- **AND** the error SHALL identify the provider and missing selection relationship

#### Scenario: Declared provider selection is ambiguous

- **GIVEN** the canonical catalog declares multiple eligible models for one CLI provider without an explicit disambiguating selection
- **WHEN** selection is requested for that provider
- **THEN** selection SHALL fail with the conflicting canonical aliases
- **AND** no model or credential from either candidate SHALL be passed to a process

#### Scenario: Canonical provider and CLI adapter identities remain distinct

- **GIVEN** canonical provider `tdt-codex` declares `cli_provider: codex`
- **WHEN** selection and provider-neutral projection are requested for CLI adapter identity `codex`
- **THEN** the result SHALL preserve `codex` as the CLI adapter identity and `tdt-codex` as the canonical provider ID
- **AND** adapter capability and executable validation SHALL use `codex`
- **AND** provider-owned credential metadata SHALL be filtered using `tdt-codex`
- **AND** neither identity SHALL be inferred from or replaced by the protocol, endpoint, model, executable, or credential availability

### Requirement: Consumer implementation claims require canonical API evidence

An enabled consumer SHALL NOT be described as integrated, wired, or functioning unless its invocation boundary resolves one canonical profile, consumes the resulting provider-neutral projection while preserving its CLI adapter and canonical provider identities, and constructs provider-specific arguments from that projection. An enabled consumer MAY use local configuration only after canonical profile resolution succeeds and the typed selector explicitly reports genuine mapping absence for that CLI identity. An unavailable or unreadable selected canonical source, canonical schema or relationship error, ambiguous selection, unsupported projection field, or other resolution/projection failure MUST fail before local fallback or process launch. A consumer bridge SHALL NOT convert such a failure into an empty override mapping, `None`, ordinary absence, or local configuration.

#### Scenario: ai-harness-skills canonical runtime wiring

- **WHEN** the harness runtime enables a supported native CLI provider with a canonical selection
- **THEN** the adapter invocation SHALL use the canonical wire model and supported behavior fields
- **AND** diagnostics SHALL preserve the canonical alias and redacted provenance
- **AND** native authentication SHALL remain within the adapter's approved boundary

#### Scenario: ai-review canonical reviewer wiring

- **WHEN** review orchestration enables supported native CLI reviewers with canonical selections
- **THEN** each reviewer SHALL receive only its own projected model and supported behavior fields
- **AND** a provider SHALL NOT receive another provider's model or credential-key metadata
- **AND** native authentication SHALL remain within each reviewer's approved boundary

#### Scenario: Consumer bridge preserves both provider identities

- **GIVEN** a canonical projection selects CLI adapter identity `codex` through canonical provider `tdt-codex`
- **WHEN** `ai-harness-skills` or `ai-review` constructs the native adapter invocation
- **THEN** adapter selection and executable validation SHALL use `codex`
- **AND** diagnostics and retained evidence SHALL preserve `tdt-codex` as the canonical provider ID
- **AND** any credential-key metadata SHALL already be filtered for `tdt-codex`
- **AND** no credential value or another provider's key metadata SHALL be passed to the adapter

#### Scenario: Canonical resolution failure is not mapping absence

- **GIVEN** an enabled consumer selected a canonical source or catalog for its operation
- **WHEN** that source is unavailable or unreadable, or profile resolution, selection, or projection fails
- **THEN** the consumer bridge SHALL propagate a redacted failure before adapter construction or process launch
- **AND** it SHALL NOT return an empty override mapping or `None`
- **AND** it SHALL NOT preserve or activate local model configuration as though the CLI mapping were genuinely absent

## ADDED Requirements

### Requirement: Identity-bound live CLI acceptance evidence

Live CLI acceptance SHALL be recorded in a durable, credential-safe ledger bound to the exact integrated planning, consumer, and resolved dependency identities that produced the result. The required acceptance matrix SHALL contain exactly two required rows: one `ai-harness-skills` row through its true contained generation boundary and one `ai-review` row through its true reviewer boundary. Each required row SHALL be executed, evaluated, and retained independently, even when one reusable mechanism invokes both boundaries. Every row SHALL bind the exact consumer Git SHA, resolved canonical-library Git SHA, dependency source and lock identity, complete product/test/acceptance-script dirty-state disposition, CLI adapter identity, canonical provider ID, canonical alias, wire model, supported behavior fields, non-secret canonical source fingerprints, redacted command shape, monotonic duration, process result, nested result or report outcome, nonce or generated artifact, target-preservation result, and non-secret shell/provider prerequisite identity and outcome. The ledger MUST distinguish process reachability from successful nested consumer behavior and MUST contain no credential value. A required row MUST be invalidated when its planning identity, participating source identity, resolved dependency identity, unaccounted product/test/acceptance-script diff, canonical source fingerprint, or selected shell/provider prerequisite state changes.

#### Scenario: Successful consumer-boundary acceptance is recorded

- **WHEN** a live native-CLI call succeeds through a participating consumer boundary
- **THEN** the durable record SHALL identify the consumer, exact consumer and canonical-library Git SHAs, dirty-state disposition, CLI provider, canonical alias, wire model, supported behavior fields, redacted command shape, monotonic duration, process exit, nested result or report outcome, and nonce or generated artifact
- **AND** the record SHALL contain no credential value

#### Scenario: Reachable process has an unsuccessful nested result

- **WHEN** the native CLI process starts or exits successfully but the consumer's nested result reports a provider error, incomplete generation, missing nonce, or missing artifact
- **THEN** acceptance SHALL fail
- **AND** the ledger SHALL preserve the process result and nested failure as distinct fields

#### Scenario: Untracked script is not durable acceptance evidence

- **GIVEN** an acceptance script exists without a retained result bound to exact integrated SHAs and dirty-state disposition
- **WHEN** implementation readiness is evaluated
- **THEN** the script SHALL be treated as a test mechanism rather than proof of a successful run
- **AND** the consumer SHALL remain unaccepted until a current durable result is captured

#### Scenario: Source identity changes after acceptance

- **GIVEN** a live result was accepted for exact source identities
- **WHEN** a participating repository advances or gains an unaccounted product diff
- **THEN** the prior live result SHALL be marked stale for release acceptance
- **AND** the affected deterministic and live gates SHALL be rerun

#### Scenario: Two required consumer rows are retained independently

- **WHEN** the minimum live-acceptance matrix is materialized
- **THEN** it SHALL contain exactly one required `ai-harness-skills` row and exactly one required `ai-review` row
- **AND** each row SHALL name one currently supported and enabled provider and one true contained consumer boundary
- **AND** each row SHALL have its own prerequisite status, process result, nested outcome, nonce or generated artifact, target-preservation result, and final row status
- **AND** a shared script MAY execute both rows but SHALL NOT collapse them into one result
- **AND** an optional additional row SHALL NOT replace either required row
- **AND** both required rows MUST pass independently before live acceptance is complete

#### Scenario: Resolved dependency identity changes after acceptance

- **GIVEN** a live row was accepted for exact consumer and canonical-library identities
- **WHEN** the consumer's dependency path, editable-source binding, lock identity, installed module origin, or resolved canonical-library Git SHA changes
- **THEN** the prior row SHALL be marked stale even when the consumer Git SHA is unchanged
- **AND** affected deterministic projection checks and the live consumer row SHALL be rerun against the new resolved dependency
- **AND** a stale candidate, wheel, cache, or editable checkout SHALL NOT satisfy exact-dependency acceptance

#### Scenario: Shell or provider prerequisite changes after acceptance

- **GIVEN** a live row was accepted with one non-secret shell and provider prerequisite identity
- **WHEN** the selected launcher or executable identity, executable version, canonical source fingerprint, provider availability, credential-availability status, environment-loading prerequisite, or owned shell/provider configuration changes
- **THEN** the prior live row SHALL be marked stale
- **AND** presence-only prerequisite checks and the affected live row SHALL be rerun
- **AND** no credential value SHALL be printed, compared, copied, rotated, or retained while recapturing the row
