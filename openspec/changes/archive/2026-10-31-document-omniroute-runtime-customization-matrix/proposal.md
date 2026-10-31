# Proposal: OmniRoute Capability and Customization Operating Contract

## Why

The existing plan conflates supported capabilities with verified deployment behavior and contains incorrect settings, routing, installation, and performance claims. This change documents an accurate operating baseline and independent evaluation gates so additional resources increase useful OmniRoute capability without weakening existing behavior.

## What Changes

- Record source revision, deployed image identity, configuration authority, local overlays, and evidence status separately; clean source tracking does not imply an unmodified runtime.
- Replace the Lean/Enterprise bundle with a feature-rich native baseline and independently assessed extensions. Preserve current Qdrant-backed hybrid memory, reranking, native multi-account routing, and prose-preserving compression pending approved evaluation.
- Define quality, isolation, resource, failure, and recovery criteria for local hybrid retrieval, optional model-based compression, browser-backed providers, relay-only Bifrost, Codex app-server, and relevant native multimodal/MCP/A2A controls. A candidate is not a selected or deployed component.
- Correct configuration and package-lifecycle guidance using the versioned source: retrieval strategy differs from vector backend; indexed local packs differ from registry installation; package resolution differs from model/browser readiness.
- Require comparable end-to-end retrieval evidence and traceable compression estimates. Withdraw the earlier keyword-versus-dummy-vector speedup as a basis for architecture; do not impose lifetime token-saving floors or fixed unmeasured RAM predictions.
- Replace whole-script retirement after three fixes with a per-modification ledger and clean-image behavioral gates. Describe failed-upgrade rollback as operator-driven unless automation is separately established.

## Capabilities

### New Capabilities

- `omniroute-runtime-customization`: Versioned operating evidence, recovery boundaries, patch retirement gates, hybrid-retrieval evaluation, and independent optional capability readiness.

### Modified Capabilities

- `omniroute-compression-and-routing`: Add accounting provenance, optional-compressor quality gates, embedding timeout-path evidence, and cache/coordination isolation evaluation. Existing runtime defaults remain unchanged by this planning work.

## Non-Goals

- Editing application code, deployment files, credentials, database rows, main specs, archives, wiki pages, or client configuration during this update.
- Installing packages, downloading models/browsers, starting services, consuming provider quota, or performing a live cutover without separate scoped authorization.
- Removing Qdrant, changing Redis eviction, enabling lossy prose compression, forcing Bifrost into native inference, or retiring the compatibility script based on this document alone.
- Guaranteeing a universal latency multiplier, compression ratio, memory footprint, zero-downtime update, or corruption-free storage.

## Impact

- Planning owner: `/Users/androidteam/Developer/platform/openspec-store`; only the five existing approved change artifacts are in this revision's save scope.
- External read-only evidence: `/Users/androidteam/Omniroute` and observed deployment results. Future implementation belongs to that deployment surface under a separate approved scope.
- Wiki synchronization and upstream contributions are future documentation/submission boundaries, not permissions granted by this update. No new artifact or capability file is introduced.
