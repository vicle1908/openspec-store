# Tasks

## 1. Investigate Consumer-Specific Faker Compatibility

- [x] 1.1 Identify which consumers depend on `@faker-js/faker`
- [x] 1.2 Determine which faker copy each consumer resolves at runtime
- [x] 1.3 Establish that `postman-collection` uses the legacy API removed in faker v10
- [x] 1.4 Establish that `@usebruno/requests` bundles its own faker internally
- [x] 1.5 Test parent upgrades to latest to confirm they cannot substitute for the override

## 2. Build the Scoping Ladder in Sandboxes

- [x] 2.1 Reproduce the baseline (12 high) in an isolated copy
- [x] 2.2 Test the global faker override and confirm it breaks `newman`
- [x] 2.3 Test the `@usebruno/requests`-scoped override and confirm it reaches 10 high
- [x] 2.4 Test the `postman-collection`-scoped override and confirm it breaks that package
- [x] 2.5 Confirm the Bruno-only scope is the safe maximum

## 3. Apply the Scoped Override

- [x] 3.1 Capture the pre-change manifest and lockfile
- [x] 3.2 Add `"@usebruno/requests": { "@faker-js/faker": ">=10.5.0" }` to `overrides`
- [x] 3.3 Install without `--force` and confirm exit code 0
- [x] 3.4 Record the audit delta (12 high → 10 high)

## 4. Verify Both Consumers

- [x] 4.1 Confirm `node_modules/@faker-js/faker` resolves to `10.6.0`
- [x] 4.2 Confirm `postman-collection`'s nested faker remains at `5.5.3`
- [x] 4.3 Run `bru --version` and `bru --help` and confirm exit 0
- [x] 4.4 Require `postman-collection/lib/superstring/dynamic-variables.js` and confirm it loads
- [x] 4.5 Confirm `newman`, `yaml-language-server`, and `newman-reporter-htmlextra` still execute
- [x] 4.6 Confirm no dependency was downgraded

## 5. Record the Rejected Deeper Scope

- [x] 5.1 Record that the `postman-collection` scope reaches 7 but breaks the package
- [x] 5.2 Record the remaining roots (`braces`, `node-forge`) as having no published clean version
- [x] 5.3 Record that the latest parents still pin the vulnerable versions

## 6. Evidence and Spec Sync

- [x] 6.1 Author `evidence.md` in the change directory from output read back from disk
- [x] 6.2 Run `openspec validate --all` and confirm the delta spec validates
- [x] 6.3 Sync the delta spec into the main `npm-audit-remediation` spec at archive time
- [x] 6.4 Archive the change and commit the store
