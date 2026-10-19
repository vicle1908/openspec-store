# agent-skill-distribution Specification

## MODIFIED Requirements

### Requirement: Canonical shared skill surface

The repository SHALL maintain `.agents/skills` as the canonical shared project-scoped skill surface in each Git root and the workspace root. Every managed entry SHALL record a manifest owner, source, installation mode (`pinned-git` with full commit SHA or `official-cli-rolling` with verified revision or `"unknown"`), and content hash, with `~/Developer/skills-lock.json` as sole writable CLI registry and `~/Developer/.agents/skills-lock.json` as its generated read-only replica.

#### Scenario: Shared skill is restored

- **WHEN** a developer runs the supported restore command in a Git root
- **THEN** the exact lockfile entries are restored into that root's
  `.agents/skills` and the manifest records their ownership and hashes

#### Scenario: Two roots are restored

- **WHEN** restore is requested for `both`
- **THEN** outer and nested roots are processed independently and each reports
  its own result, without writing skill files across the Git boundary

#### Scenario: Provenance distinguishes pinned Git entries from rolling CLI vendor entries

- **WHEN** the canonical shared skill surface in `~/Developer/.agents/skills` is audited
- **THEN** each tracked entry SHALL declare whether it is governed by `pinned-git` mode or `official-cli-rolling` mode
- **AND** `official-cli-rolling` entries SHALL record an upstream commit SHA only when independently verified, or `"unknown"` otherwise, and MUST NOT fabricate a commit SHA from a folder hash

### Requirement: Reproducible npx skills synchronization

The supported `npx skills` workflow SHALL use a pinned or policy-approved CLI, the project `skills-lock.json`, explicit agent selection, and `--copy` when materializing into a managed generated surface. Hooks MUST NOT run unbounded `npx` installation or network fetches. `pinned-git` entries MUST record an immutable full commit SHA, whereas `official-cli-rolling` vendor entries MAY use native CLI lock entries when paired with recoverable accepted snapshots and local-byte verification.

#### Scenario: Lockfile restoration is requested

- **WHEN** the supported managed restore is invoked in a root with a lockfile
- **THEN** only lockfile-declared project skills are restored to `.agents/skills`
  from verified detached checkouts of their recorded commits or from the recoverable accepted content snapshot for `official-cli-rolling` entries, and the resulting
  hashes are verified

#### Scenario: A skill source is changed

- **WHEN** a source, version, commit, or computed hash differs from the manifest
- **THEN** synchronization stops with a reviewable diff and does not overwrite
  the prior managed content without verified acceptance

#### Scenario: A Git-backed lock entry is unpinned

- **WHEN** synchronization or verification encounters a custom `pinned-git` entry
  without a 40-character hexadecimal commit ref, or an `official-cli-rolling` entry without a valid recoverable accepted snapshot and explicit provenance record
- **THEN** it fails before mutation and identifies the non-compliant skill

#### Scenario: Cloud-backed content is slow to hydrate

- **WHEN** content hashing encounters a cloud placeholder or delayed read
- **THEN** verification performs bounded retries and either verifies the exact
  content hash or fails explicitly without accepting cached metadata as proof

#### Scenario: Local byte integrity is verified independently of CLI up-to-date output

- **WHEN** `skills update` or `npx skills update` reports that project skills are already up to date
- **THEN** verification SHALL still compare the installed local bytes in `~/Developer/.agents/skills/<name>` against the accepted snapshot digests
- **AND** the CLI's upstream-versus-lockfile `computedHash` comparison MUST NOT be treated as proof that local installed files are uncorrupted or unmodified

#### Scenario: Unapproved source or skill name collision stops synchronization

- **WHEN** a refresh or manifest reconciliation encounters an unapproved upstream source change, unexpected skill path, or skill name collision with an existing entry owned by another source
- **THEN** synchronization SHALL fail closed without overwriting the existing skill or publishing the `.agents/skills-lock.json` replica
- **AND** all unrelated entries in `~/Developer/skills-lock.json` and `~/Developer/.agents/skills-lock.json` SHALL remain intact

### Requirement: Scoped verification and rollback

Setup, status, repair, and rollback SHALL support `outer`, `nested`, and `both`, emit machine-readable evidence, and preserve unrelated configuration, Agentmemory hooks, indexes, credentials, and dirty worktree changes. Rollback of `official-cli-rolling` skill updates SHALL restore from recoverable `current` or `previous` accepted byte and registry snapshots rather than relying on `computedHash` digests alone.

#### Scenario: Rollback is applied

- **WHEN** rollback is explicitly confirmed
- **THEN** only manifest-owned files, links, hooks, and registrations are
  removed or restored from the verified accepted snapshot, with snapshots proving unrelated files are unchanged

#### Scenario: Hash digest alone is rejected as a rollback source

- **WHEN** rollback or recovery is requested for an `official-cli-rolling` skill whose accepted byte snapshot is missing or corrupted
- **THEN** the recovery tool SHALL fail closed and report that `skills-lock.json` `computedHash` alone cannot reconstruct skill content

## ADDED Requirements

### Requirement: Recoverable accepted snapshots and read-only lockfile replica gating

Rolling official Skills CLI updates SHALL maintain recoverable `current` and `previous` accepted snapshots containing allowlisted skill bytes, validated registry copies, and per-file SHA-256 digests. `~/Developer/skills-lock.json` SHALL remain the sole writable CLI registry, while `~/Developer/.agents/skills-lock.json` SHALL be published as a generated read-only replica only after refresh or manual native CLI changes pass local-byte and postcheck validation.

#### Scenario: Verified refresh rotates accepted snapshots and publishes the lockfile replica

- **WHEN** an automated or manual `skills` refresh completes and postcheck verification confirms valid `SKILL.md` frontmatter, clean local byte digests, and zero unapproved collisions
- **THEN** the prior `current` accepted snapshot SHALL rotate to `previous`, the newly verified allowlisted skill bytes and `~/Developer/skills-lock.json` copy SHALL be recorded as `current`, and `~/Developer/.agents/skills-lock.json` SHALL be regenerated as a byte-identical read-only replica

#### Scenario: Failed or partial refresh withholds replica publication and reports mutations

- **WHEN** a refresh run fails, times out, or leaves partial or unverified mutations in `~/Developer/.agents/skills/` or `~/Developer/skills-lock.json`
- **THEN** the system SHALL NOT publish `~/Developer/.agents/skills-lock.json` or advance the `current` accepted snapshot
- **AND** it SHALL report the integrity failure and any detected installed mutations, and SHALL either restore only the exact allowlisted snapshot bytes or remain visibly degraded
- **AND** informational path-ambiguity skips on unrelated entries SHALL NOT block acceptance or replica publication when refreshed and already-current entries pass local-byte and postcheck verification

#### Scenario: Manual native CLI update requires explicit acceptance postcheck

- **WHEN** an operator runs `skills add` or `skills update` directly in `~/Developer/` outside the managed wrapper
- **THEN** `~/Developer/skills-lock.json` changes SHALL be flagged as unaccepted drift until the explicit acceptance and postcheck command validates local bytes, updates the accepted snapshot, and regenerates `~/Developer/.agents/skills-lock.json`

#### Scenario: Verified no-op refresh reconciles a stale lockfile replica

- **WHEN** a refresh run reports no upstream updates (`already_current`) and local byte integrity matches the `current` accepted snapshot, but `~/Developer/.agents/skills-lock.json` is stale
- **THEN** postcheck validation SHALL reconcile `~/Developer/.agents/skills-lock.json` from the validated `~/Developer/skills-lock.json`
