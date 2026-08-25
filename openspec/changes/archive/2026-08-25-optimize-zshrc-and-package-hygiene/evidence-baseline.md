# Baseline evidence (redacted)
Date: 2026-08-25

- ~/.zshrc sha256: `25d2694a56470415e7bb5516210927627805062aa3444a2e818043134a9bb316` bytes=12598 mode=0o600 owner=androidteam
- Startup baseline (3x zsh -ic exit): ]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zshreal 5.23, ]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zshreal 6.62, ]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zshreal 5.93
### node_identity_login (exit 0)
```text
]1337;RemoteHost=androidteam@Macmini]1337;CurrentDir=/Users/androidteam/Developer]1337;ShellIntegrationVersion=13;shell=zsh/opt/homebrew/opt/nvm/versions/node/v22.23.2/bin/node
/opt/homebrew/opt/nvm/versions/node/v22.23.2/bin/npm
/opt/homebrew/Cellar/nvm/0.40.7/versions/node/v22.23.2/bin/node
v22.23.2
12.0.2
/Users/androidteam/.npmrc
/opt/homebrew/Cellar/nvm/0.40.7/versions/node/v22.23.2
/opt/homebrew/Cellar/nvm/0.40.7/versions/node/v22.23.2/lib/node_modules
/opt/homebrew/opt/nvm
/Users/androidteam/.local/bin/claude
/Users/androidteam/.npm-global/bin/claude
/Users/androidteam/.local/bin/claude
/Users/androidteam/.local/bin/claude
/Users/androidteam/.npm-global/bin/claude
```
### node_identity_noninteractive (exit 0)
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
### npm global tree (via explicit prefix override)
```text
@agentmemory/agentmemory@0.9.29
@agentmemory/mcp@0.9.29
@anthropic-ai/claude-code@2.1.241
@augmentcode/auggie@0.36.0
@brightdata/cli@0.3.5
@firecrawl/anydoc@0.2.3
@fission-ai/openspec@1.10.0
@grepai/cli@0.9.4
@kilocode/cli@7.4.23
@mcp_router/cli@0.2.0
@openai/codex@0.149.0
@qoder-ai/qodercli@1.1.28
@seflless/deepwiki@0.1.8
codexuse-cli@6.0.2
exa-cli@0.1.5
gitnexus@1.6.9
happy@1.2.0
node-gyp@13.0.1
opencode-ai@1.18.21
pi-gitnexus@0.6.4
pi-intercom@0.12.0
pi-lens@4.1.1
pi-mcp-adapter@2.27.0
pi-subagents@0.54.0
pi-web-access@0.24.2
tree-sitter-dart@1.0.0
```
### Targeted Homebrew state
```text
==> antigravity-cli (Google Antigravity CLI): 1.1.19,4894004681244672 (auto_updates)
Terminal interface for Antigravity agents
https://antigravity.google/product/antigravity-cli
Not installed
From: https://github.com/Homebrew/homebrew-cask/blob/HEAD/Casks/a/antigravity-cli.rb
---
/opt/homebrew/Cellar/block-goose-cli/1.47.0/INSTALL_RECEIPT.json
/opt/homebrew/Cellar/block-goose-cli/1.47.0/LICENSE
/opt/homebrew/Cellar/block-goose-cli/1.47.0/bin/generate_manpages
---
Usage: brew link, ln [options] installed_formula [...]

Symlink all of formula's installed files into Homebrew's prefix. This is done
automatically when you install formulae but can be useful for manual
installations.

      --overwrite                  Delete files that already exist in the prefix
                                   while linking.
  -n, --dry-run                    List files which would be linked or deleted
                                   by brew link --overwrite without actually
                                   linking or deleting any files.
  -f, --force                      Allow keg-only formulae to be linked.
      --HEAD                       Link the HEAD version of the formula if it is
      
```
