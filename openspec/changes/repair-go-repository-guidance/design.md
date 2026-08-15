# Design

The owning surface is `~/Developer/go-microservices/AGENTS.md`. The file is a hand-maintained outer guide with nested repository-specific guides under `deploy/`, `platform/`, `scripts/`, and `services/`. The repair removes the generated oversized GitNexus block and keeps a compact knowledge-tooling pointer; GitNexus semantic index state remains in `.gitnexus/` and is not committed.

Verification uses the repository-native `make validate-agent-guidance` gate, shell/diff checks, and a scoped commit. No source code, generated indexes, or unrelated dirty files are changed.
