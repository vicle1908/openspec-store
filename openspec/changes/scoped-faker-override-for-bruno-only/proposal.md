# Proposal: Scoped Faker Override for the Bruno Consumer Only

## Why
A prior finding concluded the `@faker-js/faker` advisory was unreachable by upgrade because
raising faker broke `newman`; that conclusion was too broad — it is true for
`postman-collection` but not for `@usebruno/requests`, whose only faker dependency is a nested
copy, so the advisory can be cleared for the Bruno consumer alone.

## What Changes
- Add a **scoped** override in `~/.local/share/home-toolchain/package.json`:
  `"@usebruno/requests": { "@faker-js/faker": ">=10.5.0" }`, raising faker under the Bruno
  consumer only, while leaving `postman-collection` on its compatible `5.5.3`.
- Reinstall and record the audit delta from 12 high to 10 high.
- Record why the deeper override (faker under `postman-collection`) is rejected: it reaches 7
  but breaks `postman-collection` at `faker.address.city`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `npm-audit-remediation`: Extends the upgrade-only override constraint with a **scoping**
  requirement: where a shared transitive package is consumed by multiple parents with differing
  API compatibility, the override SHALL be scoped to the consumer that tolerates the newer
  version, and SHALL NOT be applied globally. Adds the requirement that the consumer's runtime
  API usage be exercised before the scoped override is retained.

## Non-Goals
- Applying a global `@faker-js/faker` override; it breaks `newman` and is already recorded as a
  rejected remedy.
- Overriding faker under `postman-collection`; it breaks `postman-collection`.
- Clearing `braces` or `node-forge`; no non-vulnerable version is published.
- Removing any dependency.

## Affected Ownership Boundaries
- `~/.local/share/home-toolchain/package.json` — one scoped override added
- `~/.local/share/home-toolchain/package-lock.json` — faker resolution for the Bruno subtree
- `platform/openspec-store` — spec delta, change artifacts, evidence
