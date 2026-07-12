---
guide_id: SKEL-DEPS-FLOWS
title: Dependency Contracts and Synchronous Flows
status: experimental
audience: human-and-ai
read_when:
  - Tracing or changing dependencies, commands, queries, transactions, cross-module calls, or error mapping.
  - Wiring an executable through a composition root.
skip_when:
  - The task changes only isolated presentation wording or documentation with no architecture claim.
depends_on:
  - README.md
  - 02-module-anatomy-and-public-contracts.md
  - 03-shared-kernel-and-platform.md
owns:
  - dependency-inversion matrix
  - cross-module contracts
  - cross-module data ownership and atomic write choices
  - command and query flows
  - transaction boundaries
  - typed application errors and transport mapping
---

# Dependency contracts and synchronous flows

> Loading rule: trace the actual call path, then verify every dependency crosses an intentional contract.

## Rule `DEP-DIRECTION-01`: dependencies point toward owned policy

| From | May depend on | Forbidden by default |
| --- | --- | --- |
| Presentation/entry adapter | Module public/application API, presentation libraries | Domain internals, persistence/vendor implementation |
| Module public surface | Public DTOs, application contracts | Concrete adapters, transport/runtime types |
| Application | Domain, owned ports, public APIs of other modules | Concrete I/O clients, other-module internals |
| Domain | Domain-local pure types and rules | Application, platform, framework, I/O |
| Port | Application/domain vocabulary | SDK, transport, storage-specific types |
| Module adapter | Its owned port, platform client mechanics | Product policy outside translation |
| Shared kernel | Pure language-level dependencies | Modules, platform, presentation |
| Shared UI | UI primitives and shared UI | Business modules, application commands, I/O |
| Platform | Runtime/external libraries | Business workflow or module internals |
| Composition root | Ports, application/public APIs, concrete adapters, platform | Business decisions |

Adapters depend inward on ports. Application policy must not import an adapter merely because both live in one process.

## Rule `DEP-XMODULE-01`: cross modules through public contracts

Allowed synchronous paths:

```text
Module A application -> Module B public query
Module A application -> Module B public command
Workflow coordinator -> public APIs of participating modules
```

Forbidden by default:

- importing another module's repository, domain entity, schema, or adapter;
- sharing mutable storage records as contracts;
- calling another module's presentation/transport endpoint from the same process;
- reaching around authorization or invariants for convenience.

A coordinator belongs to the module that owns the end-to-end business outcome. If coordinated writes constantly require one database transaction across modules, either the boundary is wrong or the exception needs an explicit consistency decision.

Use published events when temporal decoupling, fan-out, independent recovery, or deployment isolation is required. Do not replace a clear local call with messaging merely to appear decoupled.

## Rule `DEP-XMODULE-DATA-01`: preserve write ownership across module flows

Each authoritative table, collection, object namespace, or external record set has one module write owner. Sharing a database does not create shared write ownership.

Cross-module reads choose one explicit path:

- the data owner exposes a public query when its policy, authorization, or freshness contract matters;
- a dedicated read model combines module-owned sources without becoming a write authority;
- a read-only same-store join is a reviewed exception with named field owners, authorization, migration coupling, and no mutation capability.

A cross-module foreign key may protect integrity inside one store, but it does not authorize another module to write the referenced data. Record the migration/delete-order coupling and constraint owner.

For one business outcome that changes several modules, choose exactly one consistency design:

1. **Merge the boundary.** Use when the state must satisfy one invariant and changes together routinely.
2. **One same-store transaction.** The workflow coordinator opens one abstract unit of work. Each data-owning module exposes a narrow server-side transaction-participant contract that preserves its validation and write ownership. Participants share the transaction capability selected by the composition root; callers do not import repositories, pass raw driver handles, or invoke public commands that open independent transactions.
3. **Durable multi-step workflow.** Use explicit pending states, outbox/events, idempotent handlers, compensation/reconciliation, and observable recovery when resources cannot share a transaction or independent failure is desired.

Document the chosen owner, atomic boundary, partial-failure behavior, concurrency policy, and recovery path. Do not mix the three designs implicitly.

## Rule `FLOW-COMMAND-01`: commands express state-changing intent

```text
entry adapter
  -> parse transport + authenticate caller context
  -> public command
  -> application use case
     -> validate command and authorize intent
     -> load required state through ports
     -> apply domain rules/transitions
     -> persist inside owned transaction
     -> record events/outbox when required
  -> stable success or typed expected failure
  -> presentation maps safe result
```

Commands:

- use intent-revealing names;
- carry required input, not trusted server-derived identity claims;
- define idempotency and concurrency behavior where replay/races are possible;
- do not return storage/vendor objects;
- do not report success before committed state is known.

## Rule `FLOW-QUERY-01`: queries return data without business side effects

```text
entry adapter or another module
  -> public query
  -> application read policy + trusted scope
  -> query/read-model port
  -> adapter selects and maps minimal data
  -> public DTO with freshness/page metadata when relevant
```

A query may use a persistence model optimized for reading and need not hydrate a rich domain object. It must still enforce trusted authorization scope and bounded query capabilities.

Telemetry and cache population are operational side effects, not permission to mutate business state. A read that changes business state is a command.

## Rule `TX-BOUNDARY-01`: one application use case owns the transaction

The owning use case decides:

- atomic write set;
- isolation/concurrency strategy;
- retry and idempotency behavior;
- event/outbox recording;
- rollback and result semantics.

Rules:

- repositories/adapters participate through a transaction-scoped capability supplied by the composition/wiring layer;
- do not open uncoordinated nested transactions;
- keep remote network calls outside a database transaction unless a documented consistency requirement proves otherwise;
- use optimistic versioning, uniqueness, locking, or another explicit strategy when concurrent commands can violate an invariant;
- never claim atomicity across resources without a protocol that provides it;
- use an outbox when a committed database change and durable event publication must agree.

Long-running workflows use checkpoints/compensation rather than holding one transaction open.

## Composition-root runtime flow

Apply `COMPOSITION-ROOT-01` from [03-shared-kernel-and-platform.md](03-shared-kernel-and-platform.md#rule-composition-root-01-wire-concrete-dependencies-at-entrypoints):

```text
process starts
  -> validate config
  -> initialize platform clients
  -> construct concrete adapters
  -> inject adapters into module application factories
  -> mount presentation/worker/CLI entrypoints
  -> serve work
  -> drain and close dependencies on shutdown
```

Construction order and lifetimes belong here. Runtime business branching does not.

## Rule `ERROR-TAXONOMY-01`: expected failures have typed semantics

Use stable machine-readable error codes grouped by category:

| Category | Meaning | Normally retryable |
| --- | --- | --- |
| `validation` | Input violates boundary schema | No |
| `unauthenticated` / `forbidden` | Caller identity or authority is insufficient | No |
| `not_found` | Requested owned resource is absent or intentionally hidden | No |
| `conflict` | Version, uniqueness, or concurrent-state conflict | Only by explicit policy |
| `domain` | Business invariant or transition rejects intent | No |
| `rate_limited` | Capacity/policy asks caller to wait | Often, with bounded guidance |
| `dependency_unavailable` | Required external mechanism failed | Sometimes, by adapter/application policy |

At a public module boundary, expected failures use one discriminated logical contract. A stack profile may change syntax, not semantics:

```ts
type AppErrorCategory =
  | "validation"
  | "unauthenticated"
  | "forbidden"
  | "not_found"
  | "conflict"
  | "domain"
  | "rate_limited"
  | "dependency_unavailable";

type AppError = {
  code: string;
  category: AppErrorCategory;
  safeDetails?: Record<string, string | number | boolean>;
  retryable?: boolean;
};

type Result<T> =
  | { ok: true; value: T; meta?: Record<string, unknown> }
  | { ok: false; error: AppError };
```

Error `code` is stable; localized copy is a presentation concern. Do not use one generic message as the only machine contract.

Unexpected programming/infrastructure failures retain their cause and propagate to the executable error boundary. Do not disguise them as empty successful data.

## Rule `ERROR-MAP-01`: entry adapters map errors without leaking internals

Presentation/transport adapters map typed application errors to HTTP/RPC/UI/CLI semantics. They may add localized messages and a correlation/reference ID.

The executable boundary:

- logs unexpected causes with approved structured context;
- returns a safe generic internal failure;
- never exposes stack traces, SQL, credentials, raw vendor payloads, or unnecessary identifiers;
- preserves the difference between authentication, permission, validation, conflict, absence, and dependency failure;
- emits metrics/traces that make category, owner, and dependency visible without recording sensitive payloads.

Do not infer retryability solely from a transport status. The owning application/adapter contract decides it.

## Verification prompts

- Which module owns the command/query and final business outcome?
- Does every cross-module import use a public contract?
- Does application code depend on ports rather than mechanisms?
- What is atomic, and what happens under replay or concurrency?
- Are remote side effects outside the transaction or protected by a deliberate protocol?
- Which expected errors are part of the public contract?
- Where are concrete adapters wired and safely shut down?

Use [05-semantic-pattern-selection.md](05-semantic-pattern-selection.md) to choose the semantic archetype before extending the flow.
