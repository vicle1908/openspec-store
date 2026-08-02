## ADDED Requirements

### Requirement: Canonical shared skill surface

The repository SHALL maintain `.agents/skills` as the canonical shared
project-scoped skill surface in each Git root. Every managed entry SHALL have a
manifest owner, source, version or commit, content hash, and installation mode.

#### Scenario: Shared skill is restored

- **WHEN** a developer runs the supported restore command in a Git root
- **THEN** the exact lockfile entries are restored into that root's
  `.agents/skills` and the manifest records their ownership and hashes

#### Scenario: Two roots are restored

- **WHEN** restore is requested for `both`
- **THEN** outer and nested roots are processed independently and each reports
  its own result, without writing skill files across the Git boundary

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

The supported `npx skills` workflow SHALL use a pinned or policy-approved CLI,
the project `skills-lock.json`, explicit agent selection, and `--copy` whenever
files are materialized into a managed generated surface. Hooks MUST NOT run
unbounded `npx` installation or network fetches. Every Git-backed lock entry
MUST record an immutable full commit SHA rather than a floating branch or tag.

#### Scenario: Lockfile restoration is requested

- **WHEN** the supported managed restore is invoked in a root with a lockfile
- **THEN** only lockfile-declared project skills are restored to `.agents/skills`
  from verified detached checkouts of their recorded commits, and the resulting
  hashes are verified

#### Scenario: A skill source is changed

- **WHEN** a source, version, commit, or computed hash differs from the manifest
- **THEN** synchronization stops with a reviewable diff and does not overwrite
  the prior managed content

#### Scenario: A Git-backed lock entry is unpinned

- **WHEN** synchronization or verification encounters a Git-backed entry
  without a 40-character hexadecimal commit ref
- **THEN** it fails before mutation and identifies the unpinned skill

#### Scenario: Cloud-backed content is slow to hydrate

- **WHEN** content hashing encounters a cloud placeholder or delayed read
- **THEN** verification performs bounded retries and either verifies the exact
  content hash or fails explicitly without accepting cached metadata as proof

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

Setup, status, repair, and rollback SHALL support `outer`, `nested`, and
`both`, emit machine-readable evidence, and preserve unrelated configuration,
Agentmemory hooks, indexes, credentials, and dirty worktree changes.

#### Scenario: Rollback is applied

- **WHEN** rollback is explicitly confirmed
- **THEN** only manifest-owned files, links, hooks, and registrations are
  removed, with snapshots proving unrelated files are unchanged
