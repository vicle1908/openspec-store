# Tasks

## 1. Establish the Constraint

- [x] 1.1 Establish that the remedy must be upgrade-only, with no downgrade for any package
- [x] 1.2 Enumerate the current audit residual set on `/Users/androidteam/package.json` (12 high)
- [x] 1.3 Confirm every remedy `npm audit` proposes is a downgrade, and therefore prohibited

## 2. Forward-Fix Sweep

- [x] 2.1 Determine the latest published version of each of the 12 affected packages
- [x] 2.2 Compare each latest version against the advisory's vulnerable range
- [x] 2.3 Record a verdict per package: latest selected / no fix in range / no fix all versions / forward fix available
- [x] 2.4 Trace the `@budibase/handlebars-helpers → micromatch → braces` chain at latest versions
- [x] 2.5 Confirm the `braces` chain is unresolvable by any version change at any level

## 3. Test the Sole Forward Fix

- [x] 3.1 Validate the `@faker-js/faker@>=10.5.0` override in an isolated sandbox
- [x] 3.2 Confirm the sandbox audit falls from 12 high to 7 high with no `ERESOLVE`
- [x] 3.3 Capture pre-state copies of `package.json` and `package-lock.json`
- [x] 3.4 Apply the override to `/Users/androidteam/package.json` and install
- [x] 3.5 Confirm the real audit falls to 7 high with no dependency downgraded
- [x] 3.6 Execute `newman` and `bru` against the changed tree

## 4. Determine and Record Incompatibility

- [x] 4.1 Record the `newman` failure and its `TypeError` at `faker.address.city`
- [x] 4.2 Trace the failure to faker v10's removal of the legacy API used by both consumers
- [x] 4.3 Conclude no faker version is both non-vulnerable and API-compatible
- [x] 4.4 Classify the override as a rejected remedy despite clearing 5 advisories

## 5. Restore the Verified Pre-Change State

- [x] 5.1 Restore `package.json` and `package-lock.json` from the captured pre-state copies
- [x] 5.2 Reinstall and confirm the audit returns to 12 high
- [x] 5.3 Confirm `newman --version` → `6.2.2` and `bru --version` → `4.2.0` both execute
- [x] 5.4 Confirm the manifest is byte-identical to its pre-research state

## 6. Irreducible Residual Recording

- [x] 6.1 Record `braces` and `node-forge` as irreducible with latest-published-version proof
- [x] 6.2 Attribute the residual set to its root causes rather than 12 node counts
- [x] 6.3 Record the conclusion that no upgrade-only remedy exists

## 7. Evidence and Spec Sync

- [x] 7.1 Author `evidence.md` in the change directory from output read back from disk
- [x] 7.2 Run `openspec validate --all` and confirm the delta spec validates
- [x] 7.3 Sync the delta spec into the main `npm-audit-remediation` spec at archive time
- [x] 7.4 Archive the change and commit the store
