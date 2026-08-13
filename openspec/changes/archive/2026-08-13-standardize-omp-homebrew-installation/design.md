# Design: standardize-omp-homebrew-installation

## Two installations

| Property | Bun (current default) | Homebrew (target) |
|---|---|---|
| Path | `~/.bun/bin/omp` | `/opt/homebrew/bin/omp` |
| Real binary | `~/node_modules/@oh-my-pi/.../cli.js` (12 MB) | `/opt/homebrew/Cellar/omp/17.2.15/bin/omp` (122 MB) |
| Version | 17.2.15 | 17.2.15 |
| Codebase | Node.js wrapper | Standalone native binary |
| Fresh shell | resolves first (PATH order) | resolves second |

Both report v17.2.15. The Bun installation is a thin Node wrapper behind 3
`@oh-my-pi/*` packages in `~/package.json`. The Homebrew installation is a
standalone native binary managed by Homebrew's upgrade lifecycle.

## Why Homebrew is preferred

- Standalone native binary, not a Node.js wrapper behind a dependency tree.
- Managed by Homebrew's version lifecycle (`brew upgrade omp`).
- No coupling to Bun's global package state.
- Already passes default-role and explicit-selector smoke tests.
- No stale `node_modules` residue after removal.

## Removal scope

Remove exactly three direct dependencies from `~/package.json` through
Bun's package manager:

- `@oh-my-pi/pi-coding-agent` — provides the Bun symlink
- `@oh-my-pi/pi-natives` — native bindings for omp
- `@oh-my-pi/pi-natives-darwin-arm64` — platform-specific native bindings

**Do not** manually delete `~/node_modules`, `~/.bun/bin`, or any
unrelated packages. The Bun package manager handles tree cleanup.

## Packages preserved (verified zero om-pi dependency)

- `gitnexus` (53 deps, no om-pi)
- `pyright` (no om-pi)
- `yaml-language-server` (no om-pi)
- `newman-reporter-html`
- `npx`

## What does NOT change

- `~/.omp/agent/models.yml` — providers, models, equivalence
- `~/.omp/agent/config.yml` — modelRoles, display settings
- Homebrew omp version (stays 17.2.15)
- Any credential values
- Any other agent configuration

## Risk

The Bun global root at `~/node_modules` may lose the `@oh-my-pi/*`
tree after package removal. This is expected and correct — it is the
intended cleanup. No other package depends on these three.
