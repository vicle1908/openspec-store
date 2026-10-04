# Spec Delta: npm-audit-remediation

## ADDED Requirements

### Requirement: Upgrade-Only Override Compatibility Gate

A transitive-dependency override proposed as a security remedy SHALL be validated against the
runtime API of every installed consumer before it is retained. When a forward-only override
clears an advisory but breaks a consumer's execution, it SHALL be reverted to the pre-change
state and recorded as a rejected remedy, not as a remediation.

#### Scenario: faker override clears the advisory but breaks the consumer

- **WHEN** `"@faker-js/faker": ">=10.5.0"` is added to `overrides` in
  `/Users/androidteam/package.json`, resolving `@faker-js/faker` from the vulnerable `9.9.0`
  to `10.6.0` and reducing the audit from 12 high to 7 high
- **THEN** `npx newman --version` fails with `TypeError: Cannot read properties of undefined
  (reading 'city')` originating in `postman-collection`'s `faker.address.city` call, the
  override is reverted, and the override is recorded as rejected despite reducing the count

#### Scenario: a rejected remedy is not reported as a remediation

- **WHEN** the override has been reverted
- **THEN** the audit total is recorded as restored to 12 high, and the manifest is verified
  byte-identical to its pre-research state

### Requirement: Forward-Fix Sweep Across All Affected Packages

Before concluding that an advisory set is irreducible, the remediation SHALL evaluate the
latest published version of every affected package against the advisory's vulnerable range,
and SHALL record the verdict per package.

#### Scenario: forward-fix sweep recorded per package

- **WHEN** the sweep is performed across `newman`, `newman-reporter-htmlextra`,
  `@usebruno/cli`, `@usebruno/requests`, `braces`, `micromatch`, `node-forge`,
  `postman-collection`, `postman-runtime`, `postman-sandbox`,
  `@budibase/handlebars-helpers`, and `@faker-js/faker`
- **THEN** each package is recorded with its latest published version and one of the verdicts:
  latest already selected, no fix (latest within vulnerable range), no fix (all versions), or
  forward fix available-but-incompatible

#### Scenario: nested chains are shown to be unresolvable

- **WHEN** `@budibase/handlebars-helpers@0.14.3` (latest) is found to depend on
  `micromatch@^4.0.5`, which depends on `braces@^3.0.3`, and `braces@3.0.3` is itself the
  latest published version and within the vulnerable range
- **THEN** the `braces` inheritance chain is recorded as unresolvable by any version change at
  any level

### Requirement: Irreducible Residual Determination

An advisory SHALL be classified as irreducible when the latest published version of the
responsible package is within the advisory's vulnerable range, or when the only non-vulnerable
version is runtime-incompatible with an installed consumer.

#### Scenario: braces and node-forge are irreducible

- **WHEN** `braces` is vulnerable at `<=3.0.3` with latest published `3.0.3`, and `node-forge`
  is vulnerable at `<=1.4.0` with latest published `1.4.0`
- **THEN** both are recorded as irreducible unpatched-upstream residuals citing the latest
  published version as evidence, and no version change is applied

#### Scenario: residual count attributed to root causes

- **WHEN** the 12 residual advisories are recorded
- **THEN** they are attributed to their root causes (`braces`, `node-forge`,
  `@faker-js/faker`, and the `newman`/`postman-*` chain) rather than reported as 12
  independent findings
