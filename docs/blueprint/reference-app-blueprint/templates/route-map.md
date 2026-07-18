---
template_id: REFAPP-TPL-ROUTE-MAP
template_version: 1.1.0
produces: route-map
owner_guide: ../07-app-routes-and-journeys.md
use_when: Mapping logical routes, channels and critical journeys into the selected framework.
---

# Reference application route and journey map

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: route-map`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `ROUTES-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Upstream IDs: optional `PRESET-*`, `STACK-*`, `COVERAGE-*`, `FEATURE-*`
- Selected `CAP-*` / `MOD-*` scope:

- Stack profile / router/runtime:
- Public-demo exposure policy:

## Routes and entrypoints

| `ROUTE-*` | Logical/concrete path | Access/resource/tenant | Runtime | Owning public/platform contract | Query/cache/freshness | States/a11y | SLI / `EVID-*` status |
| --- | --- | --- | --- | --- | --- | --- | --- |

Include only selected browser routes and auth/webhook/file/health/worker/schedule/migration/lab entrypoints; do not create placeholder routes for unselected capabilities.

## Route-to-surface compatibility

| `ROUTE-*` | Surface/input type | Emitted canonical request/values | Owning feature query/command | Consumed result/error | Server/browser/action boundary | Invalidation/focus/navigation `EVID-*` |
| --- | --- | --- | --- | --- | --- | --- |

For preset authoring, link each `verified` row to the exact walking slice. A framework route composes the feature contract; it does not recreate field aliases, columns, form schemas, authorization or repository policy.

Canonical request and result mapping must preserve meaningful `false`, `null`, `0`, empty and omitted/default states across browser/server/feature boundaries; use real identifier and timezone-sensitive examples where applicable.

## Surface state and action evidence

| `ROUTE-*` / surface | Loading / empty / error / stale / denied / success | Focus / keyboard / announcements | Responsive viewports/input | Pending / rapid repeat / double-submit / result behavior | `EVID-*` status |
| --- | --- | --- | --- | --- | --- |

Denied is not empty, stale is not current, and client duplicate prevention does not replace server idempotency/concurrency. Evidence includes slow/failing reads and mutations, validation/conflict/ambiguous results, retry/recovery, focus restoration, and committed-success invalidation/navigation.

## Critical journeys

| `JRN-*` | Persona/start | Route/command sequence | Data/event effects | Failure/degraded/action-result path | `EVID-*` status/layers |
| --- | --- | --- | --- | --- | --- |

## Navigation and capability visibility

| Persona/capability | Visible destinations/actions | Server authorization source | Denied/hidden policy |
| --- | --- | --- | --- |

## Framework mapping

- Layout/provider/composition boundaries:
- Server/browser serialization boundaries:
- Loading/error/not-found boundaries:
- Internal HTTP calls deliberately avoided:
