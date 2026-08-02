# agent-framework-documentation-evaluation Specification

## Purpose
Provides executable documentation and outcome-focused evaluations that stay aligned with current agent APIs, public CLIs, security boundaries, and meaningful evidence quality.
## Requirements
### Requirement: Executable documentation truth

Published agent documentation SHALL use current public API and CLI surfaces, uv-based setup instructions, and synthetic placeholders for all protected configuration.

#### Scenario: Documentation snippet runs

- **WHEN** a documented code or CLI snippet is executed in an isolated fixture
- **THEN** it SHALL complete against the current public surface or fail with an intentional migration diagnostic
- **AND** it SHALL not use `pip`, removed options, or ignored configuration

#### Scenario: API surface changes

- **WHEN** a public symbol or CLI option is removed or renamed
- **THEN** the documentation check SHALL fail until the reference is updated with migration guidance

### Requirement: Outcome-quality evaluation

Each ecosystem evaluation SHALL report process execution, outcome quality, policy compliance, and adversarial security as separate axes and SHALL bind results to a public boundary, synthetic fixture, source identity, and predeclared acceptance thresholds and baselines.

#### Scenario: Meaningful result

- **WHEN** docs-sync, harness, or core processes a quality fixture
- **THEN** the result SHALL verify non-empty required artifacts, evidence completeness, provenance, refusal behavior, and policy outcomes as applicable
- **AND** execution success alone SHALL not imply quality success

#### Scenario: Invalid result

- **WHEN** a fixture yields empty, fabricated, stale, or policy-invalid output
- **THEN** the quality metric SHALL fail with deterministic diagnostics
- **AND** the evidence SHALL identify the unmet outcome without recording secrets

### Requirement: Versioned evaluation fixtures

Evaluation datasets SHALL be versioned, synthetic, bounded, and reproducible from a clean checkout. Nondeterministic stages SHALL run repeated trials, report per-task results and uncertainty, and retain held-out or periodically refreshed adversarial cases.

#### Scenario: Fixture is executed

- **WHEN** CI runs an evaluation fixture
- **THEN** it SHALL record fixture version, repository revision, command, model/provider/version, prompt and policy revision, tool manifest, runtime and dependency versions, sampling settings, trial count, and separate execution/outcome/compliance/adversarial results

#### Scenario: Nondeterministic result is evaluated

- **WHEN** a model-backed case can vary across runs
- **THEN** the evaluation SHALL execute the predeclared number of independent trials and report per-task outcomes, uncertainty, thresholds, and baseline comparison
- **AND** readiness claims SHALL state the fixture scope and SHALL not generalize beyond the measured configuration

#### Scenario: Protected data appears

- **WHEN** a fixture or result would contain credentials, private prompts, or private repository data
- **THEN** the run SHALL redact or reject it before persistence

### Requirement: Adaptive indirect-injection evaluation

Security fixtures SHALL cover indirect prompt injection originating from documents, retrieved evidence, tool output, and checkpoint artifacts, including held-out or adaptively generated variants.

#### Scenario: Injected content requests authority

- **WHEN** untrusted fixture content attempts to invoke an invisible, denied, expired, mismatched, or unapproved high-authority tool
- **THEN** the execution boundary SHALL deny the invocation before side effects and record a deterministic safe reason
- **AND** the adversarial-security axis SHALL fail if model refusal occurs but execution-time enforcement is absent

#### Scenario: Static cases all pass

- **WHEN** the fixed regression set passes
- **THEN** the result SHALL remain qualified by held-out/adaptive trial outcomes and uncertainty
- **AND** it SHALL not claim production resistance from the static fixture alone

