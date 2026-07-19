---
guide_id: SKEL-REFACTOR-EVOLUTION
title: Brownfield Refactor and Architecture Evolution
status: experimental
audience: human-and-ai
read_when:
  - Refactoring a weak or legacy repo toward the target skeleton without a big-bang rewrite.
  - Migrating module, public contract, schema, data ownership, dependency direction, or runtime flow.
skip_when:
  - Building a greenfield repo or making a local behavior change with an established owner and no architecture migration.
depends_on:
  - README.md
  - 14-testing-and-architecture-fitness.md
  - 15-delivery-observability-and-operations.md
owns:
  - brownfield discovery and target-delta planning
  - frozen structural baselines and candidate disposition
  - characterization, seams, strangler, branch-by-abstraction, and anti-corruption workflow
  - brownfield data cutover coordination and comparison policy
  - migration rollout gates, formal contract deprecation, transitional debt, and decommission proof
---

# Brownfield refactor and architecture evolution

> Preserve required behavior, not accidental structure. Move one measurable seam at a time and keep the system releasable throughout the migration.

## Rule `REFACTOR-SCOPE-01`: separate structural change from product change

Classify each proposed behavior as:

- **preserve:** externally observable contract must remain compatible;
- **fix deliberately:** known defect changes with explicit acceptance evidence;
- **retire:** obsolete behavior or consumer is removed through a deprecation plan;
- **unknown:** characterize before deciding.

Do not hide a feature change inside a refactor. If structure and behavior must change together, document both contracts, independent evidence, rollout gates, and reversal limits.

## Rule `REFACTOR-BASELINE-01`: bind structural claims to a frozen source

A structural-only slice pins the exact source content revision and declares every applicable frozen boundary: callable/wire behavior, routes and entrypoints, authorization, persistence schema/history/data ownership, public facades, external effects, dependency manifests/locks, and runtime/build configuration. Each boundary is frozen or has a separately authorized delta; omission is not permission.

Compare the pinned baseline with final target evidence through a reproducible manifest/digest or exact immutable diff/check over every declared artifact group. Unauthorized drift or evidence bound to a mismatched/stale declared revision is `FAIL`; a missing prerequisite or unavailable frozen source is `BLOCKED`; a skipped, unreadable, excluded, or unparsed check scope is `NOT_EXECUTED`. None is a passing structural claim. Separate pre-existing checkout differences from the selected refactor delta.

Export lists, digests, and snapshots prove identity or topology only. They do not replace behavioral, wire-shape, authorization, data-effect, or interaction characterization.

## Rule `BROWNFIELD-INVENTORY-01`: map reality before choosing the seam

Build a focused inventory for the migration scope:

- public routes, APIs, jobs, events, exports, and user workflows;
- callers, consumers, dependency cycles, and runtime boundaries;
- data owner, read/write paths, constraints, volume, retention, and sensitive fields;
- authorization, tenancy, audit, and external side effects;
- latency, error, throughput, query, queue, and cost baselines;
- current tests, observability, deployment topology, and recovery path;
- hotspots, repeated changes, operational incidents, and known debt;
- undocumented manual workflows and external consumers.

Use code/graph inspection, runtime evidence, schema/config/history, and responsible-owner interviews when available. A clean static import graph alone is not a behavior inventory.

## Rule `REFACTOR-CANDIDATE-01`: metrics nominate candidates, not solutions

Clone, line-count, complexity, dependency, and change-frequency tools produce investigation candidates, not an automatic extraction queue. Classify every in-scope finding with one disposition:

- `REFACTOR_CONFIRMED`: semantic equivalence, mixed ownership, or another actionable architecture cause is proved; observable behavior is characterized, the target owner is clearer, and a measurable fitness delta is declared;
- `INTENTIONAL_OWNER_LOCAL`: similar shape carries distinct policy, ownership, or change cadence and remains local;
- `FALSE_POSITIVE`: the signal does not represent reusable production behavior;
- `RECORD_ONLY`: evidence is insufficient or the slice is deferred with a reason and owner.

No finding remains unclassified. `RECORD_ONLY` is unresolved inventory, not completed remediation. Similar syntax, a large file, multiple consumers, or a score alone is insufficient for extraction. Shared promotion additionally requires [`SHARED-PROMOTION-01`](03-shared-kernel-and-platform.md#rule-shared-promotion-01-promote-semantic-stability-not-repetition) and all affected consumers' behavior evidence.

## Rule `REFACTOR-CHARACTERIZE-01`: freeze observable contracts first

Apply `TEST-CHARACTERIZATION-01` from the testing guide at the narrowest stable boundary. Cover positive, negative, permission, data-effect, and failure behavior that migration could change.

Record:

- normalized input/output/error examples;
- persisted and emitted side effects;
- meaningful `false`, `null`, zero, empty and omitted values, defaults, real identifiers, and relevant timezone behavior;
- validation, authorization, callback, reset/close, error and effect ordering;
- dependency-call cardinality, transaction span, idempotency, retry, fencing, and ambiguous-result behavior when they protect a safety/effect contract;
- invariants, timing, import/startup behavior, and tolerated nondeterminism;
- representative cardinality and performance baseline;
- known bugs classified as preserve/fix/retire;
- missing evidence and risk owner.

Capture a behavior/effect-equivalence matrix for the material observable and safety/effect axes above. A stable public facade may protect consumers while internals split, but unchanged export names do not prove callable, wire, authorization, lifecycle, or effect equivalence; apply `PUBLIC-CONTRACT-PROOF-01`. Private implementation order belongs in architecture fitness unless it protects the declared effect contract. Every omitted material axis names a risk owner. Measure success at the seam—dependency direction, cycle/import closure, effect isolation, complexity, testability, or operational risk—not by total line reduction. Characterization is a temporary safety net, not proof that the legacy design is correct.

## Rule `TARGET-DELTA-01`: define the destination independently

For one migration slice, state:

```text
Current owner/contract/dependencies:
Target owner/contract/dependencies:
Portable rules and quality attributes applied:
Behavior preserved, fixed, or retired:
Allowed transitional boundaries:
Fitness baseline and target:
Out of scope:
```

Use current code as evidence, not as the target pattern. The destination should reduce ownership ambiguity, dependency violations, operational risk, or change cost measurably.

## Rule `MIGRATION-SEAM-01`: move through an explicit seam

Choose a seam that can route, adapt, compare, or disable one coherent capability:

- route/API/resolver or callable application boundary;
- module public surface or feature facade;
- service/use-case interface;
- repository/data-access interface;
- vendor/infrastructure port;
- job/event boundary;
- stable database view or compatibility projection.

Prefer the smallest seam that preserves a useful release. Do not split a transaction, invariant, or ownership decision across old and new implementations without an explicit coordinator.

## Migration strategies

| Strategy | Use when | Required control |
| --- | --- | --- |
| Strangler | Traffic/capability can move incrementally | Routing seam, comparison, staged exposure |
| Branch by abstraction | Callers need a stable interface while implementation changes | Facade/port, old/new implementations, switch |
| Anti-corruption layer | Legacy/external model would contaminate the target | Explicit translation, error and lifecycle policy |
| Parallel read/shadow | New read can be evaluated without user-visible effects | Safe duplication, normalized comparison, load budget |
| Expand-contract | Schema or contract versions must coexist | Additive phase, migration, switch, delayed removal |

Do not create a distributed architecture merely to obtain a seam. A module boundary inside one deployable unit is often sufficient.

## Rule `TRANSITION-BOUNDARY-01`: temporary architecture is explicit debt

Every compatibility adapter, legacy facade, bridge, flag, duplicated path, or boundary exception must have:

- migration owner and reason;
- allowed callers and dependency direction;
- observability and failure policy;
- removal condition and target date;
- tracked debt/decision reference;
- architecture fitness exception that expires.

Do not export transitional internals broadly or let new features depend directly on the legacy path.

## Brownfield data cutover

Apply `MIGRATION-COMPAT-01`, `MIGRATION-SAFETY-01`, and `BACKFILL-RESUMABLE-01` from [12-data-lifecycle-migrations-and-recovery.md](12-data-lifecycle-migrations-and-recovery.md). The refactor-specific overlay is to route old/new representations behind the selected seam, declare the current source of truth, compare/reconcile before switching ownership, hold the rollback/repair window, and delay legacy contract deletion until `DECOMMISSION-01` passes.

## Rule `SHADOW-COMPARE-01`: compare without changing outcomes

Shadow reads or computations must not duplicate writes, notifications, charges, vendor calls, or other side effects.

- Normalize irrelevant values before comparison.
- Define field-level equality/tolerance and accepted exclusions.
- Sample safely and cap added load.
- Protect sensitive data in comparison logs.
- Track mismatch rate, category, cardinality, latency, and owner.
- Investigate mismatches; do not average away contract violations.

A zero-mismatch claim requires a representative window and declared comparison coverage.

## Rule `DUAL-WRITE-01`: dual write is an exceptional consistency design

Prefer one source of truth plus derived/backfilled projection. When dual write is unavoidable, define:

- authoritative system and conflict rule;
- ordering, idempotency key, retry, and deduplication;
- atomicity boundary and partial-failure behavior;
- durable repair queue and reconciliation cadence;
- lag/error metrics and escalation threshold;
- switch-off, rollback, and cleanup plan.

Do not claim rollback safety after irreversible writes to both models. The recovery path may be reconciliation or roll-forward rather than artifact rollback.

## Rule `MIGRATION-ROLLOUT-01`: cut over through proof gates

Apply `ROLLOUT-GATE-01` and `RECOVERY-DECISION-01` from [15-delivery-observability-and-operations.md](15-delivery-observability-and-operations.md). Define gates for:

- characterization/target contract suite;
- architecture fitness delta;
- shadow comparison and data reconciliation;
- latency, error, saturation, queue, and vendor impact;
- authorization/audit equivalence;
- schema/version compatibility;
- canary/cohort progression and observation time;
- pause, disable, rollback, or roll-forward trigger.

Advance only when the current gate has evidence. A passing build or quiet dashboard alone is insufficient.

## Rule `EVOLUTION-RATCHET-01`: each slice leaves the repo better

- Prevent new calls through the deprecated path.
- Do not increase scoped dependency/fitness violations.
- Reduce at least one declared architecture or operational debt item.
- Give unavoidable exceptions an owner, bounded scope, and expiry.
- Keep a compact checkpoint: completed slice, evidence, active transition, next safe step.

The target does not require fixing the entire repo before delivering value; it requires monotonic improvement in the touched capability.

## Rule `CONTRACT-DEPRECATION-01`: public contracts retire through a measured lifecycle

Apply this rule to externally or cross-module consumed APIs, events, jobs, configuration, CLI commands, data exports, schemas, and public module surfaces. Use phases equivalent to:

```text
supported -> deprecated/announced -> replacement + dual support
          -> default switched -> disabled -> removed
```

Not every contract needs every phase, but every skipped phase needs a risk-based reason. The deprecation record declares:

- contract/scope/version, reason, owner, announcement date, earliest disable/removal date, and security/support policy;
- supported replacement, migration guide/tooling, behavior/error/authorization differences, and compatibility window;
- known consumer inventory, contact/notification evidence, protocol warning or deprecation/sunset signal where supported, and privacy-safe usage telemetry;
- gates for blocking new adoption, switching defaults, rejecting old traffic, and removing storage/permissions/operations residue;
- exception approver, bounded consumer/scope, compensating control, and expiry;
- fallback or roll-forward behavior while old/new versions coexist under `RELEASE-COMPAT-01`.

Advance only after the current phase's deadline and evidence show applicable consumers migrated or explicitly accepted expiry. Security or legal urgency may shorten the window, but requires named authority, impact communication, and a containment/recovery plan. A warning in documentation or zero observed traffic without a representative observation window and consumer inventory is not removal proof.

## Rule `DECOMMISSION-01`: deletion requires consumer and recovery proof

Remove the old path only when:

- traffic/usage is zero for the declared observation window;
- known internal and external consumers have migrated or expired;
- queues, retries, scheduled jobs, caches, and old clients cannot revive it;
- data retention/export/audit obligations are satisfied;
- new behavior meets correctness, performance, and operational gates;
- rollback/roll-forward window has closed by decision;
- legacy flags, adapters, permissions, secrets, dashboards, alerts, tests, and docs are removed or updated.

Deleting code without removing operational and contract residue is not decommissioning.

## AI execution protocol

Capture one coherent migration seam with [templates/refactor-slice.md](templates/refactor-slice.md).

```text
INVENTORY
  -> CHARACTERIZE
  -> DEFINE TARGET DELTA
  -> SELECT SEAM + STRATEGY
  -> IMPLEMENT ONE REVERSIBLE SLICE
  -> TEST + FITNESS + COMPARE
  -> PROGRESSIVE CUTOVER
  -> OBSERVE + RECONCILE
  -> DECOMMISSION OR CHECKPOINT
```

## Acceptance evidence

```text
Inventory scope and consumers:
Frozen baseline revision, artifact groups, digests/checks, and authorized delta:
Candidate disposition closure and unresolved owners:
Characterization contracts/results:
Behavior/effect-equivalence matrix and negative evidence:
Target delta and selected seam:
Transition adapters/exceptions with expiry:
Deprecation phase, consumer/notification/usage evidence, and dates:
Schema/backfill/reconciliation evidence:
Shadow/dual-write metrics and limits:
Fitness before/after:
Rollout gates and recovery decision:
Decommission proof or next checkpoint:
Residual risk and owner:
```

## Stop conditions

Stop and re-scope when:

- a frozen group drifts outside the authorized delta or its baseline/check coverage is incomplete;
- an in-scope candidate is unclassified or `RECORD_ONLY` is counted as completed;
- current observable behavior is unknown and no safe characterization exists;
- the change mixes unclassified product behavior with structural migration;
- no seam can isolate a releasable slice;
- old and new schemas/contracts cannot coexist through deployment;
- a backfill is unbounded, destructive, non-resumable, or unreconciled;
- shadow execution can trigger side effects or unsafe production load;
- dual-write has no source of truth or repair path;
- rollout gates, monitoring, or recovery triggers are undefined;
- temporary debt has no owner/expiry;
- a consumed contract is disabled or removed without replacement/notification/observation evidence or an approved urgent-risk path;
- old code is deleted before consumer, data, queue, and observation proof.
