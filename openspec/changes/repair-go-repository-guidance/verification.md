# Verification

- Repository: `~/Developer/go-microservices`
- Commit: `64278e1 docs(knowledge): align repository guidance`
- `make validate-agent-guidance` — exit 0; 5 guides, 50 checks, 0 violations.
- `git diff --check` — exit 0.
- Scoped commit contains only `AGENTS.md`; generated Graphify output and unrelated `.tool-versions`, `.gitnexusrc`, and `.omp` state remain uncommitted.
