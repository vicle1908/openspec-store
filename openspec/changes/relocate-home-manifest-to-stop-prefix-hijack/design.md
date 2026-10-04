# Design: Relocate the Home-Directory Manifest to Stop Prefix Hijack

## Context
See `proposal.md`. The manifest at `$HOME` is the root cause of the original incident. Removing
it outright would have destroyed three tools that exist nowhere else, so the change relocates
first, verifies, then removes.

## Diagnosis (measured)

| Fact | Evidence |
|---|---|
| `npm prefix` from `~/Developer` (before) | `/Users/androidteam` |
| Manifest at `$HOME` | `package.json` (998 B) + `package-lock.json` (387 KB) |
| Home `node_modules` | 599 entries, **3.1 GB** |
| Sanctioned global prefix | `~/.npm-global` (used by `workstation-daily-update.sh`) |
| `gitnexus` installs | triplicated: `~/.npm-global`, `~/.local`, and `~/node_modules` |
| Tools unique to the home manifest | `bru`, `yaml-language-server`, `newman-reporter-htmlextra` |
| Tools NOT unique | `newman` → `/opt/homebrew/bin`, `pyright` → `/opt/homebrew/bin`, `gitnexus` → `~/.local/bin` |

### Why removal alone was unsafe
`@usebruno/cli` (`bru`), `yaml-language-server`, and `newman-reporter-htmlextra` are provided
only by the home manifest. Deleting the manifest would have silently removed them. Conversely,
`newman` and `pyright` resolve to Homebrew, and `gitnexus` is also installed under
`~/.npm-global` and `~/.local`, so those three were redundant in the home tree.

### The hijack, demonstrated live
Before the fix, running from `~/Developer`:

```console
$ npx --no-install bru --version
npm notice run 'bru' --version
4.2.0
```

`bru` was resolved through the home manifest despite the command being issued in `~/Developer`.
After the fix, `npm prefix` resolves to the invoking directory.

## Goals / Non-Goals

**Goals:**
- Eliminate the `$HOME` prefix hijack.
- Preserve all tooling functionality, reachable by name.
- Reclaim the 3.1 GB stray tree.
- Leave `~/.npm-global` untouched.

**Non-Goals:**
- Changing any dependency version.
- Remediating the 12 irreducible advisories.
- Touching any repository under `~/Developer`.

## Decisions

### Decision 1: Relocate, verify, then remove — in that order
- **Rationale**: The manifest has no git history, so a destructive-first sequence would be
  unrecoverable. Copying and verifying first makes the removal reversible by copying back.
- **Transaction boundary**: Old manifest and tree are removed only after the new location is
  proven to resolve an identical audit result and execute all three tools.

### Decision 2: `~/.local/share/home-toolchain/` as the destination
- **Rationale**: It is outside any repository, contains no manifest that npm would adopt for
  `~/Developer` (npm walks *upward* from the invoked directory, and `~/Developer` is not an
  ancestor of `~/.local/share`, nor vice versa), and matches the XDG data convention already
  implied by `~/.local/bin` being on PATH.
- **Reference to existing pattern**: Continues the `~/.local` convention already used for
  `gitnexus` on PATH.

### Decision 3: Explicit symlinks rather than PATH reordering
- **Rationale**: Symlinks in the already-on-PATH `~/.local/bin` keep the three tools reachable
  by name without relying on npm's implicit resolution. This preserves usability while removing
  the hijack — the two goals are independent and this satisfies both.
- **Transaction boundary**: Symlinks are created after the new install is verified, so a broken
  link can never point at a non-existent target.

### Decision 4: Preserve `~/.npm-global`
- **Rationale**: `~/Developer/scripts/workstation-daily-update.sh` installs globals with
  `--prefix "${HOME}/.npm-global"`. That is the sanctioned location and is unrelated to the
  stray home manifest; disturbing it would break the daily update pipeline.

## Risks / Trade-offs

- **Risk: some tool relied on `npx bru` resolving from a repo directory** → *Mitigation*: a
  search of `~/Developer/scripts` and `~/.agents/skills` for `bru`/`newman`/`yaml-language-server`
  invocations found none; the tools remain on PATH via `~/.local/bin` regardless.
- **Risk: the 3.1 GB tree contained a package used by something outside the manifest** →
  *Mitigation*: only three packages were unique to it, all relocated and verified; the rest
  (`newman`, `pyright`, `gitnexus`) resolve from Homebrew and `~/.npm-global` independently.
- **Risk: reversibility** → *Mitigation*: the original manifest and lockfile are preserved at
  the relocation target and the pre-state was recorded, so the change can be undone by copying
  back.
