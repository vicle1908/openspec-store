# Spec Delta: npm-audit-remediation

## MODIFIED Requirements

### Requirement: Upgrade-Only Override Compatibility Gate

A transitive-dependency override proposed as a security remedy SHALL be validated against the
runtime API of every installed consumer before it is retained. When a forward-only override
clears an advisory but breaks a consumer's execution, it SHALL be reverted to the pre-change
state and recorded as a rejected remedy, not as a remediation. Where a shared transitive package
is consumed by multiple parents with differing API compatibility, the override SHALL be **scoped
to the consumer that tolerates the newer version** rather than applied globally, and the scoped
consumer's entry point SHALL be exercised after installation.

#### Scenario: faker override clears the advisory but breaks the consumer

- **WHEN** `"@faker-js/faker": ">=10.5.0"` is added as a **global** `overrides` entry in the
  workstation toolchain manifest, resolving `@faker-js/faker` from the vulnerable `9.9.0`
  to `10.6.0` and reducing the audit from 12 high to 7 high
- **THEN** `newman --version` fails with `TypeError: Cannot read properties of undefined
  (reading 'city')` originating in `postman-collection`'s `faker.address.city` call, the
  override is reverted, and the global form is recorded as rejected despite reducing the count

#### Scenario: a rejected remedy is not reported as a remediation

- **WHEN** the global override has been reverted
- **THEN** the audit total is recorded as restored to 12 high, and the manifest is verified
  unchanged by that reverted experiment

#### Scenario: scoping the override to the compatible consumer retains the fix

- **WHEN** the override is instead scoped as
  `"@usebruno/requests": { "@faker-js/faker": ">=10.5.0" }` in
  `~/.local/share/home-toolchain/package.json`
- **THEN** `node_modules/@faker-js/faker` resolves to `10.6.0` while
  `node_modules/postman-collection/node_modules/@faker-js/faker` remains at the compatible
  `5.5.3`, the audit falls from 12 high to 10 high, and no dependency is downgraded

#### Scenario: scoped consumer is exercised before retention

- **WHEN** the scoped override is installed
- **THEN** `bru --help` and `bru --version` both exit 0, and requiring
  `postman-collection/lib/superstring/dynamic-variables.js` succeeds, confirming neither
  consumer is broken

#### Scenario: the deeper scope is rejected when it breaks the other consumer

- **WHEN** the override is scoped further to
  `"postman-collection": { "@faker-js/faker": ">=10.5.0" }`
- **THEN** the audit falls to 7 high but `postman-collection` fails to load with
  `Cannot read properties of undefined (reading 'city')`, so that scope is rejected and the
  Bruno-only scope is retained as the safe maximum
