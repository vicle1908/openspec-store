# MCP Router implementation setup evidence

- Repository: `/Users/androidteam/Developer/mcp-router`
- Isolated worktree: `/Users/androidteam/Developer/.worktrees/mcp-router-coding-agent-adapter`
- Base/head before implementation: `ad389663d31cfddad246dd0d2d43a86175b08774`
- Branch: `feat/coding-agent-mcp-adapter`
- Nearest guidance: `mcp-router/AGENTS.md`
- Package manager: `pnpm@10.22.0`; lockfile: `pnpm-lock.yaml`
- Runtime observed: Node `v26.6.0`
- Original checkout user change preserved: `.gitignore` modified; not copied or touched.
- Isolated worktree initially clean and had no `node_modules`.

## Initial baseline

Before lockfile installation:

- shared test: nonzero; global TypeScript 6 rejected deprecated `baseUrl` and
  `moduleResolution=node10`, with local dependencies absent.
- Electron typecheck: nonzero; Electron type definitions absent and global
  TypeScript 6 deprecation errors.
- Electron package: nonzero; `electron-forge` absent.
- Electron format check: nonzero; seven pre-existing files differ from Prettier.

These are environment/repository baselines, not implementation regressions.
The first frozen install under Node 26 failed building `macos-alias@0.2.12` and
was terminated after the native build failure. Partial `node_modules` was
removed; package and lock files remained unchanged. A second frozen install
under isolated Node `v22.23.2` and pnpm `10.22.0` completed, including Electron
native rebuilds.

Post-install baseline under Node 22:

- shared package tests: PASS, 4/4;
- Electron typecheck: nonzero because dependent workspaces were not built and
  two pre-existing renderer callback parameters are implicit `any`;
- Electron aggregate format: same seven pre-existing drift files;
- Electron arm64 package: recorded separately after completion.

Implementation verification will first build dependent workspaces, then rerun
Electron typecheck. Pre-existing format drift is retained separately; this
change will format-check owned files and report the aggregate repository result.

No running app, installed bundle, live database/shared config, client config,
provider state, process, or credential was mutated.
