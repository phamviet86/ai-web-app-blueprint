---
guide_id: SKEL-FOUNDATIONS
title: Architecture Foundations, Risk, and Topology
status: experimental
audience: human-and-ai
read_when:
  - Orienting to the blueprint or defining a new system architecture.
  - Choosing quality priorities, repository topology, or deployment topology.
skip_when:
  - The task has an established module owner and changes no architecture decision.
depends_on:
  - README.md
owns:
  - portable architecture principles
  - system and risk profiles
  - quality-attribute decisions
  - modular-monolith default and topology gates
  - module cohesion principle
---

# Architecture foundations, risk, and topology

> Loading rule: establish the system profile and topology before choosing folders, frameworks, or implementation patterns.

## Target outcome

Build a system in which:

- business capabilities have explicit owners;
- dependencies point toward stable policy rather than volatile mechanisms;
- public contracts are smaller than internal implementations;
- security, data integrity, and failure behavior are designed at trust boundaries;
- architecture can evolve without a big-bang rewrite.

Physical folders are a stack profile. The portable model is made of logical roles:

```text
entrypoints and presentation
  -> application use cases
       -> domain policy
       -> owned ports
            <- infrastructure adapters

composition root selects and wires concrete adapters
```

## Portable principles

1. **Own by business capability.** A module owns its vocabulary, invariants, use cases, data authority, and public contracts.
2. **Depend toward policy.** Domain policy knows no framework, database, transport, queue, or vendor SDK.
3. **Keep internals private.** Other modules depend on commands, queries, DTOs, or published events—not internal repositories or schemas.
4. **Separate policy from mechanism.** Application/domain code decides what should happen; adapters decide how external I/O happens.
5. **Make trade-offs explicit.** Optimize for stated quality attributes and risk, not fashionable architecture.
6. **Prefer reversible evolution.** Add seams and migrate vertical slices before replacing established internals.
7. **Automate mechanical boundaries.** Import, cycle, runtime, and public-API rules should become fitness checks where possible.

## Rule `ARCH-SYSTEM-01`: profile the system before tailoring the skeleton

Capture the decision in [templates/system-profile.md](templates/system-profile.md); keep it short enough to revisit when risk or topology changes.

Classify the dominant complexity. Multiple profiles may apply, but name the primary one:

| System profile | Dominant concern | Architecture emphasis |
| --- | --- | --- |
| Transactional application | Correct state changes and permissions | Use cases, transactions, audit, concurrency |
| Workflow/domain system | Rich rules and state transitions | Explicit domain model and state machine |
| Data/read-heavy system | Query volume, projections, reporting | Query contracts, indexes, read models, freshness |
| Integration hub | External protocols and partial failure | Ports, anti-corruption adapters, idempotency, retries |
| Event/worker system | Asynchronous delivery and recovery | Event contracts, outbox/inbox, replay, observability |
| Content/interaction system | Rendering, accessibility, latency | Presentation boundaries and measured client/runtime cost |

Then classify material risk:

- authorization or tenant isolation;
- irreversible data loss or corruption;
- money, inventory, entitlement, or legal state;
- personal, confidential, or regulated data;
- external side effects that cannot be rolled back;
- high availability, throughput, or latency commitments;
- migration from behavior that cannot change silently.

Higher risk requires stronger contracts and evidence. It does not require more layers everywhere.

## Rule `ARCH-QUALITY-01`: quality attributes drive decisions

Every architecture initiative must name:

1. baseline qualities that cannot be traded away: correctness, security, operability, and maintainability;
2. the two or three differentiating qualities for this system;
3. a measurable scenario for each differentiating quality;
4. accepted trade-offs and a review trigger.

Example scenarios:

```text
Changeability: add a payment provider without changing domain policy.
Reliability: retry a delivered event without applying the command twice.
Performance: keep a representative list query below the agreed latency at target cardinality.
Recoverability: resume an import from its last committed checkpoint.
```

Do not claim an architecture is "scalable", "clean", or "fast" without a scenario that could disprove the claim.

## Consequential decisions

Apply `ADR-DECISION-01` from [07-ai-operating-system-and-governance.md](07-ai-operating-system-and-governance.md#rule-adr-decision-01-record-consequential-choices-not-routine-edits) when a choice:

- changes module or deployment boundaries;
- introduces a shared abstraction or infrastructure dependency;
- commits to a data consistency, cache, event, or compatibility policy;
- is expensive to reverse.

The governance guide owns the record shape, exceptions, and revisit policy.

## Rule `TOPOLOGY-DEFAULT-01`: start with a modular monolith

Default to one deployable application with explicit modules when requirements do not prove a stronger need. A modular monolith provides:

- local calls and simpler transactions;
- one operational surface;
- enforceable module seams that can later become package or service boundaries.

`Monorepo` and `modular monolith` are not alternatives:

- **repository topology** decides where source and packages live;
- **deployment topology** decides what deploys and fails independently.

A monorepo may contain one modular monolith, multiple applications, services, or all three.

## Rule `TOPOLOGY-GATE-01`: split only at a proven boundary

Use these gates:

| Decision | Evidence required |
| --- | --- |
| Extract an internal package | Stable public API plus multiple real consumers, independent release/tooling need, or boundary enforcement unavailable in one source tree |
| Adopt a monorepo | Multiple applications/packages benefit from atomic changes, shared tooling, and one dependency graph |
| Extract a service | Independent deployment, scaling, failure isolation, security/data ownership, or team autonomy outweighs distributed-system cost |
| Add a separate data store | Independent data authority or workload requires it; convenience alone is insufficient |

Before extracting a service, prove ownership, API/event compatibility, data consistency, observability, deployment, on-call, and recovery capability. Frequent cross-service transactions or chatty calls indicate the boundary is not ready.

## Rule `MODULE-COHESION-01`: split by reason to change

Keep behavior together when it enforces one invariant or use case. Split when parts have different:

- business ownership or vocabulary;
- runtime/trust boundaries;
- volatility or release cadence;
- failure/recovery policy;
- independent verification needs.

File length is a navigation signal, not an architecture rule. Do not create empty layers, one-line facades, packages, or services merely to make a diagram symmetrical.

## Logical repository map

```text
repo/
├── app/ or entrypoints/       startup, transport entry, composition
├── modules/                   business capabilities
├── shared/                    small stable kernel and optional shared UI
├── platform/                  config and technical runtime mechanisms
├── tests/                     contract, integration, architecture evidence
└── docs/                      decisions, guides, operations
```

Names may change in a stack profile. Ownership and dependency direction must not.

## Exit criteria

The agent can state:

- primary system profile and material risks;
- prioritized quality scenarios;
- repository and deployment topology;
- evidence for every boundary stronger than a modular monolith;
- which module owns the requested capability;
- which next guide owns the implementation decision.
