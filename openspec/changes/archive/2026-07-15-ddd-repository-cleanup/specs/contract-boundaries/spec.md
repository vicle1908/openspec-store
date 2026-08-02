# contract-boundaries Specification

## Purpose

Define clear ownership model for Protobuf/REST contracts across the platform and domain layers. Establish boundaries that prevent circular dependencies and maintain separation between infrastructure contracts and domain contracts.

## ADDED Requirements

### Requirement: Contract package hierarchy

The monorepo SHALL maintain a strict contract hierarchy:

```
platform/contracts/        # Infrastructure contracts (envelopes, registries)
services/*/contracts/     # Domain contracts (business events, entities)
```

- **Platform contracts** MUST NOT import domain contracts
- **Domain contracts** MAY import platform contracts
- Platform contracts define the infrastructure envelope for all events

#### Scenario: Platform contract does not import domain contract
- **WHEN** `platform/contracts/event_envelope.go` is examined
- **THEN** it SHALL NOT contain any imports from `services/*/contracts/`
- **AND** it SHALL only use types from `platform/contracts/` or Go standard library

#### Scenario: Domain contract imports platform contract
- **WHEN** `services/catalog-service/contracts/catalog/` is implemented
- **THEN** it MAY import from `platform/contracts/`
- **AND** it SHALL use the platform envelope for event publishing

### Requirement: Platform contract ownership

`platform/contracts/` SHALL contain:

1. **Event envelope** (`event_envelope.go`): Canonical wrapper for all Kafka/Temporal events
2. **Validation** (`validate.go`): Cross-service validation utilities
3. **Registry** (`registry/`): Type registry for polymorphic event handling
4. **Time helpers** (`time_helpers.go`): Time utilities for event timestamps

Platform contracts MUST NOT contain domain-specific types (Order, Customer, etc.).

#### Scenario: Platform contracts remain domain-agnostic
- **WHEN** `platform/contracts/` is reviewed
- **THEN** it SHALL NOT contain types named after business entities (Order, Customer, Product)
- **AND** it SHALL only contain infrastructure-agnostic types

### Requirement: Service/domain contract ownership

Each service SHALL own its domain contracts in `services/<service-name>/contracts/`:

```
services/
├── catalog-service/
│   └── contracts/
│       └── catalog/         # Catalog domain events
├── customer-service/
│   └── contracts/
│       └── customer/        # Customer domain events
├── notification-service/
│   └── contracts/
│       └── notification/    # Notification domain events
└── ...
```

#### Scenario: Domain contract located with its service
- **WHEN** a developer looks for Order events
- **THEN** they SHALL find them in `services/order-service/contracts/order/`
- **AND** not in `platform/contracts/`

### Requirement: Migration of legacy contracts

Legacy contracts in `order-service/contracts/` SHALL be migrated:

| Current Location | Target Location | Action |
|-----------------|-----------------|--------|
| `order-service/contracts/order/` | `services/order-service/contracts/order/` | Move entire directory |
| `order-service/contracts/platform/` | `platform/contracts/` | Merge or deprecate re-exports |
| `services/*/contracts/platform/` | `platform/contracts/` | Merge or deprecate re-exports |

#### Scenario: Migrating order contracts to services structure
- **WHEN** `order-service/contracts/order/` is migrated
- **THEN** it SHALL become `services/order-service/contracts/order/`
- **AND** `order-service/contracts/` SHALL be updated to import from new location or removed

### Requirement: Contract documentation

Each contract package SHALL include a `README.md` documenting:

1. Purpose of the contract package
2. List of all message/event types
3. Ownership (which team/service owns this contract)
4. Version history and migration notes

#### Scenario: Contract package has documentation
- **WHEN** a developer examines any `contracts/` directory
- **THEN** they SHALL find a `README.md` explaining the contract surface
- **AND** the README SHALL list all public types with brief descriptions

### Requirement: Protobuf package naming

All Protobuf packages SHALL follow the naming convention:

```
<domain>.<service>.<message>
```

Examples:
- `order.v1.OrderCreated`
- `catalog.v1.ProductUpdated`
- `customer.v1.AddressChanged`

#### Scenario: Protobuf packages follow naming convention
- **WHEN** a new Protobuf message is defined
- **THEN** its package SHALL follow `<domain>.<service>.<version>` format
- **AND** message names SHALL use PascalCase
