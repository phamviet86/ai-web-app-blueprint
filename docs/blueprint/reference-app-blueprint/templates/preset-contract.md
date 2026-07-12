---
template_id: REFAPP-TPL-PRESET-CONTRACT
template_version: 1.0.0
produces: preset-contract
owner_guide: ../10-preset-authoring-and-instantiation.md
use_when: Authoring or revising one versioned stack preset and proving its materialization and inter-layer compatibility.
---

# Preset contract: [preset ID and version]

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: preset-contract`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `PRESET-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Preset ID / semantic version / maturity:
- Blueprint version / revision:
- Source stack profile / exact lockfile provenance:
- Target archetype and supported capability tiers:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:

## Filesystem and materialization map

| Template source | Target path | Create / merge / replace | Conflict/idempotency policy | Upgrade/removal owner |
| --- | --- | --- | --- | --- |

- Framework scaffold/version command:
- Application-code root and framework-default root exceptions:
- Paths deliberately not materialized:
- Application preset-lock target:

## Capability matrix

Use `provided`, `verified`, `conditional`, or `unsupported`. Only `verified` rows may claim exact-version compatibility.

| Capability ID | Layer | Status | Public contract/consumer | Constraint or unsupported rationale | Walking-slice `EVID-*` |
| --- | --- | --- | --- | --- | --- |

## Inter-layer contract matrix

| Flow ID | Producer/surface | Versioned request/input | Action/query + service | Repository/adapter/data or provider | Result/UI behavior | Negative-path `EVID-*` |
| --- | --- | --- | --- | --- | --- | --- |

## Shared UI and input baseline

| Category/item | Required / conditional | Stable shared semantics | Feature-owned configuration | Input/output normalization | Accessibility/state evidence |
| --- | --- | --- | --- | --- | --- |

## Data, auth, feature, and app boundaries

| Boundary | Concrete path | Owns | May depend on | Must not own/import | Fitness evidence |
| --- | --- | --- | --- | --- | --- |

## AI guide routing

| User-task class | Guide path | Allowed paths | Required blueprint owner | Verification/stop condition |
| --- | --- | --- | --- | --- |
| Analyze request | `guides/analyze-request.md` | | | |
| Add/modify lib | `guides/lib.md` | | | |
| Add/modify shared | `guides/shared.md` | | | |
| Add/modify feature | `guides/feature.md` | | | |
| Add/modify app | `guides/app.md` | | | |
| Add/modify new pattern | `guides/new-pattern.md` | | | |

## Clean-room verification

| Gate | Command/lab | Environment | `EVID-*` status/result | Blocks acceptance? |
| --- | --- | --- | --- | --- |
| Scaffold/materialize | | | | Yes |
| Install/lockfile | | | | Yes |
| Database/migration | | | | When selected |
| Identity/session | | | | When selected |
| Lint/typecheck/test/build | | | | Yes |
| Browser walking slice | | | | Yes for verified UI flow |

## Versioning and handoff

- Local customization policy:
- Supported upgrade path / breaking changes:
- Deprecation/removal policy:
- Demo slice removal/replacement path:
- Unsupported capabilities and extension triggers:
- Accepted / gaps / reviewer:
