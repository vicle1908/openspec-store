# Post-change evidence (redacted)
Date: 2026-08-25

- ~/.zshrc sha256(prefix): `3edfdc241542a480` mode=0o600 owner=androidteam
- ~/.zshenv.secrets mode=0o600 owner=androidteam (value never printed)
- Secret exports remaining in .zshrc: **none** (all seven migrated)

## Shell gates
```text
zsh -n: PASS (SYNTAX_OK)
fresh zsh -ic source: PASS (SOURCE_OK, nvm=function, launchers OK)
secrets loaded interactively: yes (boolean only)
compaudit: no insecure paths reported (exit 0)
docker/grok/bun commands resolve: yes
```

## Startup after change (3x zsh -ic exit)
```text
]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zshreal 7.11
]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zshreal 6.90
]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zshreal 8.43
```
(baseline was 4.53-5.23s / 5.93-6.62s across runs; nvm dominates startup per zprof — see design D6)

## Node/npm/Claude ownership handoff for reconcile-node-global-package-topology
### login shell (exit 0)
```text
]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zsh/opt/homebrew/opt/nvm/versions/node/v22.23.2/bin/node
/opt/homebrew/opt/nvm/versions/node/v22.23.2/bin/npm
/opt/homebrew/Cellar/nvm/0.40.7/versions/node/v22.23.2/bin/node
v22.23.2
12.0.2
/Users/androidteam/.npmrc
/opt/homebrew/Cellar/nvm/0.40.7/versions/node/v22.23.2
/opt/homebrew/Cellar/nvm/0.40.7/versions/node/v22.23.2/lib/node_modules
/Users/androidteam/.local/bin/claude
/Users/androidteam/.npm-global/bin/claude
/Users/androidteam/.local/bin/claude
/Users/androidteam/.local/bin/claude
/Users/androidteam/.npm-global/bin/claude
```
### noninteractive shell (exit 0)
```text
/Users/androidteam/.hermes/node/bin/node
/Users/androidteam/.hermes/node/bin/npm
/Users/androidteam/.hermes/node/bin/node
v22.23.2
10.9.8
/Users/androidteam/.npmrc
/Users/androidteam/.local
/Users/androidteam/.local/lib/node_modules
/Users/androidteam/.local/bin/claude
/Users/androidteam/.npm-global/bin/claude
```

## Residual follow-ups
- Rotate the seven migrated credentials (shared OmniRoute/Copilot key pair first).
- CCE integration still eval()s external output — security follow-up.
- Node/npm topology mutation is owned by reconcile-node-global-package-topology.

## Targeted Homebrew repair (HZ 5.x)

```text
brew config: exit 0 (Homebrew 6.0.19-22-gb56087c)
antigravity-cli reinstall --cask --force: exit 0 (binary conflict warning for /opt/homebrew/bin/agy — pre-existing binary retained)
block-goose-cli link: exit 0 (1.47.0 linked)
goose resolves: /opt/homebrew/bin/goose -> 1.45.0
agy resolves: /opt/homebrew/bin/agy -> 1.1.20
brew outdated after change (unchanged, not upgraded per scope):
==> Auto-updating Homebrew...
Adjust how often this is run with `$HOMEBREW_AUTO_UPDATE_SECS` or disable with
`$HOMEBREW_NO_AUTO_UPDATE=1`. Hide these hints with `$HOMEBREW_NO_ENV_HINTS=1` (see `man brew`).
==> Auto-updated Homebrew!
Updated 2 taps (anomalyco/tap and homebrew/cask).
```

Note: `brew info --cask antigravity-cli` reports "Not installed" metadata even after forced
reinstall — recorded as-is; the binary itself works (agy 1.1.20). The outdated `antigravity`
cask was intentionally NOT upgraded (separately approved maintenance, task 5.4).
