---
template_id: SKEL-TPL-REFACTOR-SLICE
template_version: 1.1.0
produces: refactor-plan
owner_guide: ../16-refactor-and-evolution.md
use_when: Moving one brownfield behavior/data/dependency path behind a target seam.
---

# Refactor slice: [seam/use case]

> Instantiate with schema `1.0` from [README.md](README.md).

- Owner / target module/public API:
- Current callers/dependencies/data/runtime:
- Observable contract to preserve/change:
- Baseline violations and target delta:

## Frozen boundary and authorized delta

- Baseline source revision/content identity:
- Final target revision/content identity:
- Structural-only scope:
- Separately authorized behavior changes/tasks:
- Baseline alignment, exclusions, and unparsed/unreadable scope:

| Boundary/artifact group | Frozen or allowed delta | Baseline digest/query | Final diff/check and negative proof | Result/owner |
| --- | --- | --- | --- | --- |

Undeclared drift, revision mismatch, unreadable scope, or a check that excludes part of a frozen group blocks the structural claim.

## Candidate disposition

Use `REFACTOR_CONFIRMED`, `INTENTIONAL_OWNER_LOCAL`, `FALSE_POSITIVE`, or `RECORD_ONLY` for every in-scope clone/hotspot/dependency candidate. A confirmed refactor may extract, split, invert, inline, delete, isolate effects, or retain a compatibility seam. A legitimate slice may mark a category N/A, but no observed finding remains unclassified.

| Finding/signal and tool identity | Disposition | Semantic/ownership rationale | Characterization and fitness target | Owner/status |
| --- | --- | --- | --- | --- |

## Characterization

| Observed behavior/path | Preserve / fix / retire | Evidence and authorized change | Owner |
| --- | --- | --- | --- |

| Behavior/failure/performance case | Evidence/test | Known ambiguity | Decision owner |
| --- | --- | --- | --- |

## Behavior-equivalence matrix

Include only material axes, but name the risk owner for every omitted axis. Export lists/digests alone prove identity or topology, not behavior.

| Observable/effect axis | Pinned baseline | Target expectation | Positive/negative evidence | Result/owner |
| --- | --- | --- | --- | --- |
| Callable/wire/auth contract and presence/default/error precedence |  |  |  |  |
| Persisted/emitted/remote effects and safety-critical dependency call count/order |  |  |  |  |
| Safety-critical transaction span, idempotency, retry, fencing, ambiguous outcome |  |  |  |  |
| Interaction/callback/reset/close timing and relevant UI states |  |  |  |  |
| Import/startup/build isolation and runtime-only dependencies |  |  |  |  |

## Checker coverage

If no automated checker applies, record `N/A` with the invariant, rationale, manual evidence, review owner, and next automation trigger.

- Roots, discovered/analyzed files, resolver and aliases:
- Supported import/re-export and dynamic/conditional/generated forms:
- Excluded, skipped and unparsed accounting:
- Conforming fixture and materially distinct negative fixtures:

## Transition

- Seam/facade/anti-corruption adapter:
- Caller migration batches:
- Data/schema migration:
- Current and next source of truth / switch condition:
- Shadow/compare or dual-path rule and repair path:
- Flag/owner/expiry:
- Fitness ratchet:
- Observation window and abort threshold:

## Cutover and deletion

| Gate | Metric/evidence | Abort/recovery | Owner |
| --- | --- | --- | --- |

Delete only after callers, data authority, jobs/events, telemetry, docs, flags, adapters, and exceptions no longer depend on the legacy path.

- Decommission evidence and deletion proof:
- Candidate-closure proof; `RECORD_ONLY` findings remain unresolved and are not completion evidence:
