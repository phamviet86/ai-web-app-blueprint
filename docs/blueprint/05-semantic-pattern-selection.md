---
guide_id: SKEL-PATTERNS
title: Semantic Pattern Selection
status: experimental
audience: human-and-ai
read_when:
  - Selecting a module or workflow archetype before implementation.
  - Deciding which detailed query, data, reliability, security, or refactor owner to load next.
skip_when:
  - The task already has an established semantic pattern and changes no architecture contract.
depends_on:
  - README.md
  - 01-foundations.md
  - 02-module-anatomy-and-public-contracts.md
  - 04-dependency-contracts-and-sync-flows.md
owns:
  - semantic archetype selection signals and anti-signals
  - pattern-to-rule-owner routing
---

# Semantic pattern selection

> Choose by business semantics, consistency, failure, and scale. This guide selects a pattern; linked guides own its detailed implementation contract.

## Selection matrix

| Dominant need | Start with | Detailed owner |
| --- | --- | --- |
| Maintain records with local validation and few invariants | `PAT-SIMPLE-CRUD` | Guides `02`, `04`, and `09` for flexible reads |
| Enforce transitions or rules across operations | `PAT-DOMAIN-WORKFLOW` | Guides `02`, `04`, and `13` for races/idempotency |
| Serve a projection whose shape/grain differs from writes | `PAT-READMODEL` | Guide `09` |
| Decouple latency, retry, fan-out, scheduling, or load | `PAT-ASYNC-EVENT` | Guide `13` |
| Isolate an external system/protocol | `PAT-INTEGRATION` | Guides `02`, `11`, and `13` |
| Process a large submitted dataset with controlled partial failure | `PAT-BATCH-IMPORT` | Guides `11`, `12`, and `13` as applicable |
| Compare systems and repair drift | `PAT-RECONCILIATION` | Guides `12`, `13`, and `16` by ownership/migration mode |

Combine patterns only when each solves a separate proven concern. Route each concern to its owner instead of accumulating all linked guides in one context.

## Archetype `PAT-SIMPLE-CRUD`: straightforward record lifecycle

**Select when:** one module owns the data; behavior is mostly record maintenance; validation, authorization, and state changes remain local and simple.

**Do not select when:** valid changes depend on a transition graph, multi-record invariant, durable side effect, or custom recovery policy.

**Apply next:** module/application boundaries from [02-module-anatomy-and-public-contracts.md](02-module-anatomy-and-public-contracts.md), command/transaction/error flow from [04-dependency-contracts-and-sync-flows.md](04-dependency-contracts-and-sync-flows.md), and bounded query rules from [09-query-cache-and-read-models.md](09-query-cache-and-read-models.md) only when list/search behavior exists.

## Archetype `PAT-DOMAIN-WORKFLOW`: explicit invariant and state machine

**Select when:** legality depends on prior state, actor, ordered transition, money/inventory/entitlement, or a rule reused across entrypoints.

**Do not select when:** a schema plus a small application validation function expresses the complete behavior; do not create entity classes for ceremony.

**Apply next:** `MODULE-DOMAIN-01` and `MODULE-APPLICATION-01` in [02-module-anatomy-and-public-contracts.md](02-module-anatomy-and-public-contracts.md), `FLOW-COMMAND-01`/`TX-BOUNDARY-01` in [04-dependency-contracts-and-sync-flows.md](04-dependency-contracts-and-sync-flows.md), and `CONCURRENCY-01`/`IDEMPOTENCY-01` in [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md) when replay or concurrent writers are possible.

## Archetype `PAT-READMODEL`: projection optimized for a read contract

**Select when:** a query needs a different shape, grain, calculation, index, or freshness policy without changing the authoritative write model.

**Do not select when:** an ordinary bounded relation query and application DTO are sufficient, or when the projection would become a second implicit write authority.

**Apply next:** the decision matrix and `READMODEL-ENTITY-01`, `READMODEL-AGGREGATE-01`, and `READMODEL-FRESHNESS-01` in [09-query-cache-and-read-models.md](09-query-cache-and-read-models.md).

## Archetype `PAT-ASYNC-EVENT`: durable deferred work

**Select when:** work must survive caller/process failure, exceed an interactive deadline, absorb bursts, fan out, schedule, or retry independently.

**Do not select when:** a bounded local call is simpler, an inefficient query is merely being hidden, or no owner can operate backlog/replay/failure state.

**Apply next:** `SYNC-ASYNC-GATE-01`, `ASYNC-STATE-01`, `EVENT-ENVELOPE-01`, `OUTBOX-INBOX-01`, and `ORDER-DLQ-REPLAY-01` in [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md).

## Archetype `PAT-INTEGRATION`: anti-corruption boundary

**Select when:** the system depends on a vendor, partner, device, protocol, or legacy model it does not control.

**Do not select when:** the capability is an owned business module in the same system; call its public API rather than disguising it as platform/vendor infrastructure.

**Apply next:** port/adapter ownership from [02-module-anatomy-and-public-contracts.md](02-module-anatomy-and-public-contracts.md), trust controls from [11-security-identity-and-privacy.md](11-security-identity-and-privacy.md), and `DEADLINE-CANCEL-01`, `RETRY-BUDGET-01`, `DEGRADE-01`, and `VENDOR-WEBHOOK-01` from [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md).

## Archetype `PAT-BATCH-IMPORT`: staged bulk processing

**Select when:** a submitted dataset cannot safely complete as one bounded interactive command and needs preview, progress, checkpoint, or partial-result semantics.

**Do not select when:** the operation is a small atomic command, or when “batch” would bypass normal authorization and invariants with raw writes.

**Apply next:** input/upload controls from [11-security-identity-and-privacy.md](11-security-identity-and-privacy.md), durable job/idempotency rules from [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md), and migration/backfill rules from [12-data-lifecycle-migrations-and-recovery.md](12-data-lifecycle-migrations-and-recovery.md) only when authoritative stored data is being transformed.

## Archetype `PAT-RECONCILIATION`: detect and repair drift

**Select when:** two representations may diverge and the system must compare, explain, and repair from a declared authority.

**Do not select when:** source of truth, identity matching, or conflict authority is unknown; automatic repair would make ambiguity destructive.

**Apply next:** data ownership/lifecycle from [12-data-lifecycle-migrations-and-recovery.md](12-data-lifecycle-migrations-and-recovery.md), integration/replay recovery from [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md), and shadow/cutover rules from [16-refactor-and-evolution.md](16-refactor-and-evolution.md) when reconciliation is part of a brownfield migration.

## Cross-cutting selection gates

Before implementation, state:

- selected archetype and the signal that justified it;
- rejected simpler archetype and why it cannot meet the contract;
- module/public owner and consistency boundary;
- detailed rule owner to load for the current workstream;
- removal trigger for any temporary pattern or compatibility path.

## Stop conditions

Stop and reclassify when a pattern is chosen from screen/framework shape, CRUD accumulates workflow branches, messaging has no operational owner, a projection becomes a write authority, an integration leaks vendor vocabulary inward, a batch bypasses invariants, or reconciliation lacks an authoritative source.
