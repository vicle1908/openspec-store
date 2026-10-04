# Design: Upgrade Outdated Homebrew Casks and Remote Agent Releases

## Context
See `proposal.md`. A survey of upstream release channels identified 8 outdated Homebrew casks and 1 upstream fast-forwardable commit in `platform/prime-agent`. Upgrading these components ensures consistency between workstation tools and remote distributions.

## Goals / Non-Goals

**Goals:**
- Upgrade CLI casks: `copilot-cli@1.0.91`, `droid@0.233.0`, `zed@1.22.0`, `gcloud-cli@587.0.0`, `postman-cli@1.69.0`.
- Upgrade remaining casks: `google-drive`, `lark`, `teamviewer`.
- Fast-forward `platform/prime-agent` to remote head `c24ac227f`.
- Verify CLI execution and version reporting.

**Non-Goals:**
- Upgrading Homebrew formulae (all 189 installed formulae are already up to date).
- Force-updating tools that require interactive OAuth logins.

## Decisions

### Decision 1: Target CLI casks first followed by background application casks
- Upgrading developer CLI tools (`copilot-cli`, `droid`, `zed`, `gcloud-cli`, `postman-cli`) ensures command-line pipelines and editors are immediately current without interrupting GUI desktop state.

### Decision 2: Fast-forward git merge for prime-agent
- `platform/prime-agent` has a clean working tree tracking `origin/main`. Upstream commit `c24ac227f` fixes client detachment and detached daemon cleanup in `pa-cli`. Running `git merge origin/main --ff-only` applies the commit cleanly without merge commits.
