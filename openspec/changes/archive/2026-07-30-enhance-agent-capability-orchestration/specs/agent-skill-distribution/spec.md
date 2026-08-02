## MODIFIED Requirements

### Requirement: Canonical shared skill surface

The repository SHALL maintain `.agents/skills` as the canonical shared
project-scoped skill surface in each Git root. Every managed entry SHALL have a
manifest owner, source, version or commit, content hash, and installation mode;
the orchestration skill SHALL be included in this inventory and SHALL not
duplicate native GitNexus, Graphify, OpenSpec, or Agentmemory-owned surfaces.
The policy MUST identify which configured clients receive a shared copy,
native adapter, or an explicit unsupported result.

#### Scenario: Shared skill is restored

- **WHEN** a developer runs the supported restore command in a Git root
- **THEN** the exact lockfile entries, including the reviewed orchestration
  skill, are restored and the manifest records ownership and hashes

#### Scenario: Two roots are restored

- **WHEN** restore is requested for `both`
- **THEN** outer and nested roots are processed independently and each reports
  its own orchestration-skill result without crossing the Git boundary

#### Scenario: Configured client surfaces are verified

- **WHEN** the orchestration skill is distributed to the reviewed client
  inventory
- **THEN** every selected client reports the intended invocation/discovery
  contract and every unsupported client is explicit rather than silently
  omitted

#### Scenario: Native and shared skills overlap

- **WHEN** a client already has native GitNexus, Graphify, OpenSpec, or
  Agentmemory guidance
- **THEN** the orchestration skill routes to that native surface without
  copying or redefining its generated instructions

### Requirement: Scoped verification and rollback

Setup, status, repair, and rollback SHALL support `outer`, `nested`, and
`both`, emit machine-readable evidence for the orchestration skill and native
surfaces, and preserve unrelated configuration, Agentmemory hooks, indexes,
credentials, and dirty worktree changes. Repeated setup and rollback MUST
remain duplicate-free and MUST perform no unbounded network installation from
agent or Git hooks. Managed-skill rollback SHALL remove only repair-owned or
currently valid lock-owned client links and SHALL preserve canonical shared
skills, lockfiles, native/generated skills, hooks, and registrations.

#### Scenario: Rollback is applied

- **WHEN** rollback is explicitly confirmed
- **THEN** only repair-owned or currently valid lock-owned client links are
  removed, canonical orchestration and native/generated surfaces remain, and
  snapshots prove unrelated files remain unchanged

#### Scenario: Setup is repeated

- **WHEN** orchestration-skill setup runs twice for the same root and client
- **THEN** manifest ownership, hashes, invocation contracts, and discovery
  results remain stable without duplicate skills, hooks, or registrations
