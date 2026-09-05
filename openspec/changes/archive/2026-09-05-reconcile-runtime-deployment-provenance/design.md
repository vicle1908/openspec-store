## Context
Use read-only inspection of manifests, plists, processes, and ports. Treat launchd as runtime authority and manifests as provenance metadata.
## Decisions
- Never infer ownership from directory names alone.
- Record absolute paths, process IDs, plist paths, and observed timestamps.
- Correct metadata only after comparing with live process and LaunchAgent state.
## Risks / Trade-offs
- Live state can change during collection; record timestamps and recheck before any mutation.
