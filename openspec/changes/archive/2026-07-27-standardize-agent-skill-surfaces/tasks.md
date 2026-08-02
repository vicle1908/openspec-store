## 1. Baseline and ownership

- [x] 1.1 Inventory outer and nested `.agents/skills`, `.claude/skills`,
  `skills-lock.json`, agent guidance, MCP configuration, and existing links.
- [x] 1.2 Define the manifest schema, owner vocabulary, version/hash rules, and
  generated-file markers.
- [x] 1.3 Add diagnostics for escaping, absolute, broken, duplicate, and
  unowned links without changing any files.

## 2. Lockfile-backed synchronization

- [x] 2.1 Pin or policy-validate the `skills` CLI and add a wrapper that runs
  lockfile restoration per Git root.
- [x] 2.2 Use explicit agent selection and `--copy` for managed generated
  surfaces; prohibit network installs from Git hooks.
- [x] 2.3 Verify computed hashes after restoration and fail before overwrite on
  mismatch.
- [x] 2.4 Make synchronization idempotent and produce redacted JSON evidence.

## 3. Native Graphify and GitNexus integration

- [x] 3.1 Preserve official Graphify `agents` and Claude installation paths and
  record their ownership separately from `npx skills`.
- [x] 3.2 Preserve GitNexus's native project `.claude/skills/gitnexus` and
  generated-skill layout while keeping global setup separate.
- [x] 3.3 Add outer/nested selectors and independent snapshots to all skill
  setup and rollback operations.

## 4. Repair and symlink fixture

- [x] 4.1 Implement non-destructive repair for the current broken per-skill
  links, requiring a manifest-owned canonical source.
- [x] 4.2 Build a disposable fixture for Claude discovery, `npx skills`,
  Graphify, GitNexus, archive/fresh-clone, and Claude-only coexistence.
- [x] 4.3 Gate optional root `.claude/skills` symlink mode on fixture evidence
  and filesystem compatibility; default to real directories.

## 5. Verification and documentation

- [x] 5.1 Add focused tests for both roots, lock/hash mismatch, invalid JSON,
  duplicate installation, symlink safety, and rollback preservation.
- [x] 5.2 Document the canonical layout, commands, ownership boundaries,
  troubleshooting, and explicit symlink decision in the knowledge runbook.
- [x] 5.3 Run OpenSpec validation and the focused knowledge-tool test suite;
  retain evidence for the implementation handoff.

## 6. Verification warning remediation

- [x] 6.1 Resolve and record immutable upstream commit refs for every Git-backed
  project lock entry.
- [x] 6.2 Enforce full commit refs before synchronization or verification and
  require the explicit reviewed `add-copy` path for updates.
- [x] 6.3 Add bounded cloud hydration retries while retaining fail-closed
  content-hash verification.
- [x] 6.4 Refresh the pinned skill surfaces and rerun lock, fixture, OpenSpec,
  guidance, and knowledge-tool verification.

## 7. Final verification alignment

- [x] 7.1 Add the declared `developer-code-intelligence` delta and align the
  persistent native ownership metadata contract.
- [x] 7.2 Make inventory and native setup fail closed without flagging approved
  manifest-owned relative links or hidden filesystem metadata.
- [x] 7.3 Cover every manifest-owned Claude link during rollback and retain
  before/after preservation fingerprints.
- [x] 7.4 Add successful non-empty restore, metadata-drift, terminal hydration,
  exact fixture-result, and snapshot rollback regression coverage.
- [x] 7.5 Refresh both manifests and rerun focused, repository, OpenSpec, and
  graph verification.
