# Spec Delta: npm-audit-remediation

## ADDED Requirements

### Requirement: No Package Manifest Directly in the Home Directory

A `package.json` SHALL NOT reside directly in `$HOME`, because npm resolves its prefix upward
from the current directory and will adopt such a manifest for any invocation made from a
directory beneath `$HOME` that lacks its own.

#### Scenario: prefix resolution no longer hijacked

- **WHEN** `/Users/androidteam/package.json` has been removed and `npm prefix` is executed from
  `/Users/androidteam/Developer`
- **THEN** the command reports `/Users/androidteam/Developer`, not `/Users/androidteam`

#### Scenario: nested directories resolve to themselves

- **WHEN** `npm prefix` is executed from `/Users/androidteam/Developer/platform`
- **THEN** the command reports that directory, confirming the upward walk terminates at the
  invoked directory rather than at `$HOME`

### Requirement: Tooling Relocation Before Manifest Removal

Where a home-directory manifest provides tooling that is not available elsewhere, that tooling
SHALL be relocated to an explicit location outside the `$HOME` resolution path and verified
functional BEFORE the original manifest and dependency tree are removed.

#### Scenario: relocated tooling executes at the new location

- **WHEN** the manifest is copied to `~/.local/share/home-toolchain/` and installed
- **THEN** `bru --version` reports `4.2.0`, `yaml-language-server --version` reports `1.24.0`,
  and `newman-reporter-htmlextra` executes, each with exit status 0

#### Scenario: relocation is faithful

- **WHEN** the relocated tree is audited
- **THEN** `npm audit` reports the same 12 high advisories as the original location, and the
  `@faker-js/faker` resolution is unchanged at `9.9.0` for `@usebruno/requests` and `5.5.3`
  nested under `postman-collection`

#### Scenario: tools remain reachable by name without a manifest in $HOME

- **WHEN** symlinks for `bru`, `yaml-language-server`, and `newman-reporter-htmlextra` are added
  to `~/.local/bin`
- **THEN** each command resolves and reports its version when invoked by name, with no
  `package.json` present in `$HOME`

### Requirement: Sanctioned Global Prefix Preservation

Relocation SHALL NOT disturb `~/.npm-global`, the sanctioned global npm prefix used by the
workspace's daily update script, nor any tool installed within it.

#### Scenario: global prefix tooling unaffected

- **WHEN** the home-directory manifest is removed
- **THEN** `gitnexus --version` still reports `1.6.12`, and `~/.npm-global/lib/node_modules`
  retains its contents
