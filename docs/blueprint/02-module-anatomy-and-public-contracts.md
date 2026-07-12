---
guide_id: SKEL-APP-FEATURE
title: Module Anatomy and Public Contracts
status: experimental
audience: human-and-ai
read_when:
  - Creating or changing a business module, use case, domain rule, port, adapter, or presentation entry.
  - Defining what another module or external caller may import.
skip_when:
  - The task touches only platform configuration or AI guidance.
depends_on:
  - README.md
  - 01-foundations.md
owns:
  - module anatomy and optional layers
  - public module API
  - application and domain ownership
  - port, adapter, and presentation ownership
  - module-local dependency direction
---

# Module anatomy and public contracts

> Loading rule: choose logical owners first. A stack profile may map several roles into one folder or file, but it must preserve their contracts.

## Rule `MODULE-BOUNDARY-01`: organize by business capability

A module represents a cohesive business capability or bounded context, not a technical category such as controllers, tables, or utilities.

```text
modules/<module>/
├── public/          commands, queries, DTOs, published events
├── application/     use cases and orchestration
├── domain/          invariants and business model
├── ports/           capabilities required by application/domain
├── adapters/        database, vendor, messaging implementations
└── presentation/    HTTP, UI, CLI, worker, or other entry adapters
```

This is a logical map, not a required directory checklist. Keep each module internally cohesive and externally small.

Good module boundaries have:

- one business vocabulary and accountable owner;
- explicit commands and queries;
- clear data authority;
- few cross-module invariants;
- a failure and change cadence that can be reasoned about independently.

If two modules repeatedly need each other's internals or one transaction, reconsider the boundary before adding exceptions.

Data authority means one module is the write owner for each authoritative dataset even when several modules share one physical store. Other modules do not gain write permission from a foreign key, shared schema, or convenient join. Apply `DEP-XMODULE-DATA-01` from [04-dependency-contracts-and-sync-flows.md](04-dependency-contracts-and-sync-flows.md#rule-dep-xmodule-data-01-preserve-write-ownership-across-module-flows) for cross-module reads, constraints, and atomic workflows.

## Rule `MODULE-PUBLIC-01`: expose a stable module API

Other modules may use only the owning module's intentional public surface:

```text
public commands
public queries
public DTOs/value representations
published integration events
```

Public contracts must:

- use business names rather than storage or vendor vocabulary;
- validate inputs at the boundary;
- return explicit output DTOs, not ORM rows, SDK payloads, or mutable domain internals;
- document authorization, idempotency, consistency, and failure semantics;
- evolve compatibly or through an explicit migration/version policy.

An index/barrel is not sufficient by itself. Enforce no-deep-import rules with language/package tooling where possible. Internal helpers, domain entities, repositories, and adapter clients are private by default.

External HTTP/RPC/event versioning is separate from internal module organization. Do not version every internal function preemptively.

## Rule `MODULE-APPLICATION-01`: application owns use cases

Application code expresses what the system can do:

- commands and queries;
- caller/ownership authorization orchestration;
- input-to-domain mapping;
- transaction and idempotency boundaries;
- coordination of domain policy and ports;
- output DTO and expected-error normalization.

An application use case must not know framework widgets, transport headers, SQL syntax, queue SDK calls, or vendor payload details.

Name methods after intent—`approveEnrollment`, `reserveInventory`, `issueInvoice`—rather than generic persistence verbs when behavior has business meaning.

## Rule `MODULE-DOMAIN-01`: domain owns invariants and transitions

Use domain code when rules must remain true across entrypoints or persistence mechanisms. It may contain:

- entities and value objects;
- pure policies and specifications;
- state machines and transition guards;
- calculations and domain events;
- domain-specific expected errors.

Domain code is deterministic and infrastructure-free. It does not import databases, HTTP, environment variables, clocks, random generators, loggers, or vendor SDKs. When time, identity, or an external fact matters, the application supplies a value or calls an owned port.

Do not force a rich domain model onto simple data maintenance. A small CRUD module may use validation plus application rules without entity classes.

## Rule `MODULE-PORT-01`: the consumer owns volatile capability contracts

A port describes a capability the application needs, for example:

```text
CustomerStore
PaymentGateway
EventPublisher
Clock
IdGenerator
FileStore
```

Define the port beside the policy that consumes it, using application/domain terms. Keep it focused; do not mirror an entire SDK or database client.

Create a port when at least one applies:

- the dependency performs external I/O;
- protocol/vendor volatility must not leak inward;
- deterministic testing needs a controlled implementation;
- multiple implementations are real or planned by requirement;
- the boundary may become asynchronous or independently deployed.

Dependency inversion does not require a container or an interface for every pure helper.

## Rule `MODULE-ADAPTER-01`: adapters translate mechanisms

Adapters implement ports and own mechanism-specific behavior:

- persistence queries and row mapping;
- vendor SDK/HTTP requests and protocol parsing;
- message broker publication/consumption mechanics;
- filesystem, cache, email, clock, and identity implementations.

Adapters may depend on frameworks and external libraries. They must not decide product permissions, state transitions, user-facing copy, or business retry policy. Translate raw failures into typed dependency failures understood by the application boundary.

An anti-corruption adapter prevents an external model from becoming the module's domain model.

## Rule `MODULE-PRESENTATION-01`: presentation adapts entrypoints

Presentation includes web routes/controllers, UI composition, CLI commands, scheduled handlers, and queue consumers.

It owns:

- transport parsing and response/status mapping;
- rendering and interaction state;
- protocol authentication extraction;
- calling one or more public application contracts;
- localized/user-facing presentation of safe results.

It does not own domain invariants, persistence queries, cross-module transactions, or trusted authorization merely because a control is hidden.

Keep entrypoints thin. A worker, webhook, UI action, and HTTP endpoint may call the same application command without duplicating policy.

## Rule `MODULE-OPTIONAL-01`: add layers only when behavior needs them

Use the smallest module shape that preserves direction:

| Need | Minimum logical roles |
| --- | --- |
| Simple CRUD | public contract, application use case, persistence adapter, presentation entry |
| Business workflow | add domain policy/state machine |
| External dependency | add owned port plus adapter |
| Read-heavy projection | add query/read-model adapter |
| Async processing | add event contract and consumer/publisher adapters |
| No presentation in this process | expose public application contract only |

Folders may be omitted or combined when imports and ownership remain clear. Empty layers and pass-through classes add navigation cost without protection.

## Module-local dependency direction

```text
presentation -> public/application -> domain
                              └----> ports

adapters --------------------------> ports

composition root -> presentation/application + concrete adapters
```

Allowed exceptions must be explicit architecture decisions, narrow, tested, and time-bounded where possible.

## Contract checklist

- [ ] Module boundary follows a business capability.
- [ ] Public commands, queries, DTOs, events, and failures are explicit.
- [ ] Other modules cannot deep-import internals.
- [ ] Domain policy is deterministic and mechanism-free.
- [ ] Application owns use-case, authorization, and transaction orchestration.
- [ ] Ports use consumer vocabulary; adapters translate external mechanisms.
- [ ] Presentation maps transport/UI behavior without duplicating policy.
- [ ] Optional layers exist because behavior requires them.

Use [04-dependency-contracts-and-sync-flows.md](04-dependency-contracts-and-sync-flows.md) for cross-module calls, commands, queries, transactions, and error flow.
