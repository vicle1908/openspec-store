# Closure evidence (redacted)
Date: 2026-08-25

## Claude package removal (RN 3.x)
```text
command used: npm_config_prefix=$HOME/.npm-global npm uninstall -g @anthropic-ai/claude-code
result: "removed 2 packages", exit 0
stale tree absent after: yes (~/.npm-global/lib/node_modules/@anthropic-ai/claude-code gone)
native Claude verified before and after: 2.1.245 at ~/.local/bin/claude (absolute path)
whence -a claude after removal: single resolution -> ~/.local/bin/claude
```

## Topology decision (RN 2.x)
See evidence-topology-decision.md — nvm-managed interactive runtime;
no npm prefix mutation performed or required.

## Runtime recheck (RN 4.2)
```text
]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zsh/opt/homebrew/opt/nvm/versions/node/v22.23.2/bin/node
v22.23.2
/opt/homebrew/Cellar/nvm/0.40.7/versions/node/v22.23.2/lib/node_modules
/Users/androidteam/.local/bin/claude
```

## Rollback rehearsal (RN 4.3)
```text
config scope/value to restore: none captured (interactive env had no prefix setting; no config was mutated)
package reinstall if needed:
  npm_config_prefix=$HOME/.npm-global npm install -g @anthropic-ai/claude-code@2.1.241
(exact prior version recorded in evidence-inventory.md)
```
