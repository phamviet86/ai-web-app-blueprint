---
template_id: SKEL-TPL-REFACTOR-SLICE
template_version: 1.0.0
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

| Observed behavior/path | Preserve / fix / retire | Evidence and authorized change | Owner |
| --- | --- | --- | --- |

## Characterization

| Behavior/failure/performance case | Evidence/test | Known ambiguity | Decision owner |
| --- | --- | --- | --- |

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
