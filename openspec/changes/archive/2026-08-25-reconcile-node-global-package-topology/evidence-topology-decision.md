# Topology decision evidence
Date: 2026-08-25

## Decision: Topology A — nvm-managed (no prefix mutation)

Evidence:
- Interactive/login shell: node and npm resolve to /opt/homebrew/opt/nvm/versions/node/v22.23.2;
  npm root -g already points at the nvm Cellar tree. There is no forced prefix in the
  interactive environment (no NPM_CONFIG_PREFIX/PREFIX env; ~/.npmrc contains only an
  unrelated script-execution flag).
- Non-interactive shells use Hermes bundled node (~/.hermes/node) with prefix ~/.local —
  this is Hermes-managed and out of scope; it does not affect the interactive runtime.
- The observed `npm config get prefix` -> ~/.local mismatch from the original audit was an
  artifact of non-interactive capture, not an interactive misconfiguration.

Consequences:
- No npm config mutation is required or permitted (task 2.2 satisfied by evidence: nothing to remove).
- ~/.npm-global remains a legacy global tree kept on PATH; its stale claude-code copy is removed in task 3.x.
