# ADR 006: Underscore-Based Swift Scope Naming

## Status

Accepted

## Context

Nexus Swift repository validation rejects dots in scope names (`com.example`). SPM convention typically uses reverse-domain notation (`com.company.lib`). We need a naming convention that works with Nexus while remaining readable.

## Decision

We will use **underscores** as the separator for Swift scopes in Nexus (e.g., `com_company_lib`).

## Consequences

### Positive

- **Nexus-compatible**: Passes Nexus's validation (tested: `com_example` → HTTP 204)
- **Readable**: `com_example_mylib` is still human-readable
- **Consistent**: Single convention across all packages

### Negative

- **SPM Registry spec allows only hyphens in scopes**: The [Swift Package Registry spec](https://github.com/apple/swift-package-manager/blob/main/Documentation/PackageRegistry/Registry.md) defines scope as `[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}` — **no underscores, no dots**
- **Deviates from SPM convention**: SPM allows dots in package identifiers
- **Migration friction**: If moving to a different registry that supports dots

### Scope vs Package Name (per SPM Registry spec)

| Component | Allowed Characters | Example |
|-----------|------------------|---------|
| **Scope** | Alphanumeric + hyphens only (no underscores, no dots) | `com-example` |
| **Package Name** | Alphanumeric + underscores + hyphens | `my_lib` |

Nexus's internal validation (`^[a-zA-Z0-9_-]+$`) is **more permissive** than the SPM spec. Use live validation to confirm behavior before committing to a convention.

## Alternatives Considered

| Alternative | SPM Spec | Nexus | Rejected Because |
|------------|---------|-------|-----------------|
| Dots (`com.example`) | ✅ Allowed in package name only | ❌ HTTP 500 | Not valid in scope |
| Underscores (`com_example`) | ❌ Prohibited in scope | ✅ HTTP 204 | Doesn't match SPM spec; use hyphens instead |
| Hyphens (`com-example`) | ✅ Allowed in scope | ✅ Works | Recommended per SPM spec |
| Flat names (`mylib`) | ✅ Allowed | ✅ Works | No namespace protection; collision risk |

## Validation

- ✅ `swift.scope=com-example` → HTTP 204 (SPM spec compliant)
- ⚠️ `swift.scope=com_example` → HTTP 204 (Nexus accepts, but SPM spec prohibits underscores in scope)
- ❌ `swift.scope=com.example` → HTTP 500 (Nexus rejects dots in scope)
- ✅ Package manifest can still declare `com.example.MyLib` as package ID (dots allowed in package name)

## Documentation

Scope naming will be documented in:
- README.md (quick reference)
- client-configuration spec (detailed rules)
- CI pipeline docs (automation conventions)

## See Also

- [Swift Package Registry Service Specification](https://github.com/apple/swift-package-manager/blob/main/Documentation/PackageRegistry/Registry.md) — Official SPM spec (scopes allow only hyphens)
- [Configure Swift with Nexus](https://help.sonatype.com/en/configure-spm-registry.html) — Sonatype docs (HTTPS required for SPM registry)
