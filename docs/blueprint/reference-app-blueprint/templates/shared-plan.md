---
template_id: REFAPP-TPL-SHARED-PLAN
template_version: 1.0.0
produces: shared-plan
owner_guide: ../04-shared-foundation.md
use_when: Planning shared kernel, UI, hook, formatting, or testing contracts for real reference-app consumers.
---

# Reference application shared plan

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: shared-plan`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `SHARED-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Upstream IDs: optional `PRESET-*`, `STACK-*`, `COVERAGE-*`
- Selected `CAP-*` / consumer `MOD-*` scope:

- Stack profile / capability coverage links:
- First implementation slice:

## Product and UI design brief

- Product type / target users / top tasks:
- Information hierarchy / content and data density:
- Brand, locale, copy and product constraints:
- Supported devices, input modes and narrow/wide breakpoints:
- Accessibility target / performance and motion budgets:
- Optional design-intelligence candidates accepted/rejected with rationale and source record:

## Contract inventory

| `SHARED-*` item | Category | Stable semantics | First two real consumers | Allowed dependencies | Must not own | Removal/merge trigger |
| --- | --- | --- | --- | --- | --- | --- |

## UI and interaction contract

| Item | Accessibility/focus/responsive behavior | Feature-owned inputs/policy | Component `EVID-*` / status | Runtime/bundle constraint |
| --- | --- | --- | --- | --- |

## Token and component-state contract

| Primitive token family | Semantic purpose mappings | Component/state tokens | Framework-native theme/API evidence | Light/dark/contrast/responsive evidence |
| --- | --- | --- | --- | --- |

| Component/surface | Default/hover/focus/active | Disabled/loading/invalid/denied | Empty/error/stale/success | Narrow/wide + keyboard/touch behavior | `EVID-*` |
| --- | --- | --- | --- | --- | --- |

## Preset UI capability matrix

Use `provided`, `verified`, `conditional`, or `unsupported` when this plan contributes to an `AUTHOR_PRESET`.

| Capability/category | Status | Shared public semantics | Emitted request/input | Consumed result | Feature-owned configuration | Walking-slice `EVID-*` |
| --- | --- | --- | --- | --- | --- | --- |
| Tokens/primitives | | | | | | |
| App/page layout | | | | | | |
| Feedback/async state | | | | | | |
| Form/input | | | | | | |
| Table/list | | | | | | |
| Masonry/calendar/transfer | | | | | | |
| Toolbar/overlay/action | | | | | | |
| Remote lifecycle adapters | | | | | | |

## Input normalization

| Value family/control | UI value | Canonical boundary value | Empty/null/delete semantics | Locale/timezone | Form/filter/toolbar modes | `EVID-*` |
| --- | --- | --- | --- | --- | --- | --- |

## Remote interaction and result mapping

| Flow | Feature callback/query key owner | Loading/empty/error/stale/success | Field/conflict/denied/dependency mapping | Focus/close/navigation | Invalidation/refetch owner |
| --- | --- | --- | --- | --- | --- |

## Design and outcome evidence

| Surface/flow | Exact UI API/source record | Objective accessibility/component checks | Viewport/state renders | Pattern-conformance result | Requested-outcome result |
| --- | --- | --- | --- | --- | --- |

Keep both final verdicts independent. A component gallery may prove tokens/states but not a feature payload, action result, authorization decision or user journey.

## Kernel, hooks, formatting, and testing

| Item | Pure/browser/test boundary | Determinism or locale contract | `EVID-*` / status | Owner |
| --- | --- | --- | --- | --- |

## Dependency and rollout check

- Import direction/architecture rule:
- Server/browser separation:
- Existing duplication to migrate or delete:
- Slice that introduces the item:
- Consumer migration and decommission evidence:
- Accepted / gaps / reviewer:
