---
template_id: REFAPP-TPL-FEATURE-PLAN
template_version: 1.0.0
produces: feature-plan
owner_guide: ../06-features-and-public-contracts.md
use_when: Planning one reference application module and its first vertical slice.
---

# Feature/module plan: `MOD-*` [name]

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: feature-plan`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `FEATURE-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Upstream IDs: optional `PRESET-*`, `COVERAGE-*`, `DATA-*`, `PLATFORM-*`
- Trace scope: selected `CAP-*`, owning `MOD-*`, `ROUTE-*` / `JRN-*`:

- Business capability / archetype:
- Authoritative `DATA-*` sets:
- In scope / out of scope:
- Allowed module dependencies:

## Concrete layer mapping

| Semantic role | Concrete path | Owns | May import | Must not own/import | Fitness `EVID-*` |
| --- | --- | --- | --- | --- | --- |
| Public contract | | | | | |
| Schema/validation | | | | | |
| Action/entrypoint | | | | | |
| Service/application | | | | | |
| Repository/adapter | | | | | |
| Client hook/config | | | | | |
| View/presentation | | | | | |

## Public contracts

| Kind | Name/version | Input/output/error | Authz/tenant | Idempotency/concurrency/freshness |
| --- | --- | --- | --- | --- |
| Command | | | | |
| Query | | | | |
| Event | | | | |

## Application and domain

- Use cases/state transitions/invariants:
- Transaction/partial-failure policy:
- Application-owned ports:
- Degraded/recovery behavior:

## Adapters and entrypoints

| Port/entrypoint | Local/test/deployed adapter | Protocol/runtime | Failure/retry/reconciliation |
| --- | --- | --- | --- |

## Presentation

| `ROUTE-*`/job | User outcome | Loading/empty/error/stale/denied behavior | Accessibility/responsive |
| --- | --- | --- | --- |

## Closed interaction flows

| Flow | Shared surface/input | Canonical request/values | Action/query -> service | Repository/data/provider | Stable result -> client/view | `EVID-*` |
| --- | --- | --- | --- | --- | --- | --- |

- Query alias/operator/join/access-scope owner:
- Form empty/date/number/option normalization:
- Mutation field/conflict/denied/dependency mapping:
- Success invalidation/refetch/focus/navigation owner:

## Evidence

| Failure mode/invariant | Lowest sufficient test/lab | `EVID-*` | Evidence status | Exit gate |
| --- | --- | --- | --- | --- |
