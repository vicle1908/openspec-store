## Context

The outer repository and `mcp-router/` are separate Git roots. The outer root
already has `.agents/skills`, `.claude/skills`, and a project
`skills-lock.json`; the Claude surface contains both real directories and
broken links. The lockfile currently describes Agentmemory and Redis skills,
while Graphify and GitNexus are installed by their own CLIs.

The current `npx skills` implementation recognizes `.agents/skills` as the
universal project surface and restores project lock entries there. Project
installation defaults to symlinks; `--copy` is the explicit alternative.
Global installation and project lock restoration have different semantics, so
the bootstrap must not treat them as interchangeable.

## Decisions

### Canonical ownership

`.agents/skills` is the canonical shared project source. A managed manifest
records each entry's owner (`npx-skills`, `graphify`, `gitnexus`, `openspec`,
or `hand-authored`), source, version/commit, hash, and destination.
Each Git root persists this portable manifest separately. Lock-backed entries
retain their reviewed repository commit, native entries retain their owning
tool version, and approved Claude links retain their exact relative target.

`.claude/skills` remains a real directory. Claude-specific Graphify bundles,
GitNexus's `.claude/skills/gitnexus` and `generated` layout, OpenSpec skills,
and hand-authored Claude skills remain there. No tool may silently replace this
directory with a symlink.

### `npx skills` boundary

The lockfile is authoritative only for skills installed from package/repository
sources through `npx skills`. Restoring it installs to `.agents/skills` and
must be run separately in each Git root. The wrapper invokes explicit
`--agent` selections and `--copy` for managed generated destinations; it never
uses an unpinned `npx` package in a hook.

Git-backed entries additionally carry the reviewed full commit SHA in `ref`.
Ordinary `sync` rejects a missing, branch, or tag ref. Moving to another commit
uses the explicit `add-copy` review path with `owner/repository#<40-hex-sha>`;
the wrapper verifies a detached checkout at that exact commit, invokes the
pinned official CLI against the local checkout, and records the reviewed source,
ref, and computed folder hashes together. This also avoids the current CLI's
attempt to interpret a raw commit SHA as a clone branch while separating
reproducible restoration from an intentional upstream update.

Content verification reads every file and uses bounded retries for delayed
cloud hydration. A timeout remains a failure: inode metadata, a previous
receipt, or an upstream hash is not accepted as evidence for unread local
content.

Graphify's and GitNexus's own CLIs remain authoritative for their native skill
bundles, MCP configuration, and hooks. `npx skills` may distribute a reviewed
mirror only after the generated content and owner metadata are verified.

### Symlink policy

The desired root link is an opt-in compatibility mode, not the default
architecture. Before enabling it, a disposable fixture must prove Claude
discovery, `npx skills ls`, Graphify installation, GitNexus `analyze --skills`,
archive/fresh-clone behavior, and coexistence with a Claude-only skill. The
fixture must also prove installers do not replace or traverse the link
unexpectedly. Until then, the bootstrap rejects a repository-level
`.claude/skills` directory symlink with an actionable message.

### Repair and rollback

Repair is non-destructive: broken links are reported and replaced only when a
matching canonical `.agents/skills/<name>` source exists and the manifest owns
the destination. Unknown, hand-authored, or ambiguous paths require review.
Rollback removes only manifest-owned copies, links, and registrations and
restores snapshots byte-for-byte; it never removes `.agents/skills` entries
owned by another tool or Agentmemory hooks.
Rollback candidates are the union of repair-journal entries and currently
valid lock-owned Claude links. Before and after fingerprints cover canonical
skills, lock and hook configuration, guidance, and local index/output trees.

### Two-root execution

Every command accepts `outer`, `nested`, or `both`. `both` is implemented as
two independent runs with root-specific snapshots, lockfiles, and status. A
failure in one root does not mutate or claim success for the other.

## Compatibility matrix

| Surface | Owner | Default form | Symlink allowed |
| --- | --- | --- | --- |
| `.agents/skills` | shared manifest / `npx skills` | real files | no |
| `.claude/skills` | Claude-native tools/OpenSpec | real directory | no |
| Graphify project skill | Graphify CLI | native bundle per platform | no |
| GitNexus project skills | GitNexus CLI | `.claude/skills/gitnexus` | no |
| Global agent skills | tool-specific installer | tool-managed | outside change |

## Failure and security policy

- Missing `npx`/network/credentials produces a bounded diagnostic; ordinary
  application verification remains usable.
- A lock hash mismatch, untracked generated skill, invalid JSON, or unexpected
  symlink is a hard setup failure before mutation.
- A floating Git ref is a hard failure; GitHub sources use reviewed full commit
  SHAs.
- Sources and tokens are redacted from logs. No hook fetches packages or
  network content.
- Symlink targets must remain inside the owning Git root; absolute or escaping
  targets are rejected.
