# Agent Skill Distribution

## Purpose

Define canonical, reproducible, multi-agent project skill surfaces and safe
synchronization, repair, compatibility, verification, and rollback behavior
across the outer and nested Git roots.

## Requirements

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

### Requirement: Native Claude surface is preserved

The repository SHALL keep `.claude/skills` as a real directory unless the
compatibility fixture has explicitly authorized symlink mode. Claude-native
Graphify, GitNexus, OpenSpec, and hand-authored skills MUST remain discoverable.

#### Scenario: Native GitNexus layout is installed

- **WHEN** GitNexus generates project skills
- **THEN** `.claude/skills/gitnexus` and any generated subdirectory remain
  present and are not redirected to `.agents/skills`

#### Scenario: A root directory symlink is present without approval

- **WHEN** diagnostics find `.claude/skills` is a symlink and fixture approval
  is absent
- **THEN** setup fails before mutation and reports the required remediation

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

### Requirement: Non-destructive repair

The integration SHALL detect broken, escaping, absolute, and unknown skill links
and SHALL repair only destinations owned by the manifest with an unambiguous
canonical source.

#### Scenario: A broken link has a canonical source

- **WHEN** `.claude/skills/<name>` is broken and `.agents/skills/<name>` is
  manifest-owned
- **THEN** repair replaces only that link with a verified copy or approved
  relative link and records the action

#### Scenario: A link is ambiguous or hand-authored

- **WHEN** no unique manifest-owned source exists
- **THEN** repair reports the path and requires review without deleting it

### Requirement: Symlink compatibility gate

The integration SHALL provide a disposable fixture test before enabling a
repository-level `.claude/skills -> ../.agents/skills` symlink. The gate SHALL
test discovery, both official installers, lock restoration, archive/fresh-clone
behavior, and coexistence with Claude-only skills.

#### Scenario: Fixture passes

- **WHEN** every compatibility assertion passes on supported filesystems
- **THEN** symlink mode may be explicitly enabled and its target, platform, and
  fixture evidence are recorded

#### Scenario: Fixture fails

- **WHEN** any installer, agent, archive, or cloud-sync assertion fails
- **THEN** symlink mode remains disabled and the real-directory layout is
  retained

### Requirement: Scoped verification and rollback

Setup, status, repair, and rollback SHALL support `outer`, `nested`, and `both`, emit machine-readable evidence, and preserve unrelated configuration, Agentmemory hooks, indexes, credentials, and dirty worktree changes. Rollback of `official-cli-rolling` skill updates SHALL restore from recoverable `current` or `previous` accepted byte and registry snapshots rather than relying on `computedHash` digests alone.

#### Scenario: Rollback is applied

- **WHEN** rollback is explicitly confirmed
- **THEN** only manifest-owned files, links, hooks, and registrations are
  removed or restored from the verified accepted snapshot, with snapshots proving unrelated files are unchanged

#### Scenario: Hash digest alone is rejected as a rollback source

- **WHEN** rollback or recovery is requested for an `official-cli-rolling` skill whose accepted byte snapshot is missing or corrupted
- **THEN** the recovery tool SHALL fail closed and report that `skills-lock.json` `computedHash` alone cannot reconstruct skill content

### Requirement: Managed product roots MUST NOT duplicate the canonical shared surface

A managed product-specific skill root SHALL NOT hold content that is already available through the canonical shared `.agents/skills` surface. When a product root exists only to expose shared or workspace skills to one agent, that exposure SHALL be provided by supported standard `.agents/skills` discovery or by a link, not by copied files. Removing a product-specific root SHALL proceed only when every entry is either already available through standard discovery or is deliberately promoted, and the removal SHALL be reversible.

#### Scenario: A product-specific root is a subset of the canonical surface

- **GIVEN** a managed product root such as `~/.pi/agent/skills` contains only entries that also exist in the canonical shared surface
- **WHEN** the product root is evaluated for removal
- **THEN** the evaluation SHALL confirm that no entry is unique to the product root
- **AND** removal SHALL be performed only after that confirmation

#### Scenario: A product root holds a unique entry

- **GIVEN** a managed product root contains an entry that does not exist in the canonical shared surface
- **WHEN** removal is evaluated
- **THEN** the unique entry SHALL be promoted or explicitly reported before removal
- **AND** the entry MUST NOT be discarded silently

#### Scenario: Relocation preserves provenance

- **GIVEN** an entry is promoted from a product-specific root into the canonical shared surface
- **WHEN** the promotion is recorded
- **THEN** the resulting surface SHALL distinguish lockfile-tracked skills from untracked local additions
- **AND** a pre-change copy of both surfaces SHALL be retained until verification passes

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

