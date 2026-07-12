---
template_id: REFAPP-TPL-PLATFORM-PLAN
template_version: 1.0.0
produces: platform-plan
owner_guide: ../05-platform-and-integrations.md
use_when: Mapping platform mechanisms, adapters, executable roots, configuration, and integrations for the selected stack.
---

# Reference application platform plan

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: platform-plan`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `PLATFORM-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Upstream IDs: optional `PRESET-*`, `SYS-*`, `STACK-*`, `COVERAGE-*`
- Selected `CAP-*` / `MOD-*` consumers:

- Stack and system/risk profile links:

## Capability and adapter matrix

| Capability | Owning need/module | Application-owned port | Local | Test | Preview/demo | Production starter | Replacement seam |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Preset query, auth, and result seams

| Mechanism | Generic `lib`/platform contract | Feature/application-owned policy | Concrete adapter/runtime | Negative-path `EVID-*` |
| --- | --- | --- | --- | --- |
| Query parsing/translation | Bounds, canonicalization, operator primitives | Public aliases, relation/join map, required scope, budget | | |
| Database/transaction | Client lifecycle, transaction and error containment | Repository contract and business ownership | | |
| Identity/session | Session verification and trusted-subject facts | Resource/tenant authorization and denial policy | | |
| Result/error | Safe categories and correlation metadata | Business/field codes, copy and invalidation policy | | |

### Trusted identity path

- Identity/session adapter -> trusted subject:
- Route/action guard -> feature authorization:
- Mandatory repository subject/tenant scope:
- Expired/revoked/denied evidence:

## Executable composition

| Root | Selected by `CAP-*` | Runtime/deploy unit | Concrete adapters | Startup/shutdown | Health/owner |
| --- | --- | --- | --- | --- | --- |
| Web | Baseline | | | | |
| Worker | Conditional | | | | |
| Migration | Stored data | | | | |
| CLI/lab | Conditional | | | | |

## Configuration and trust

| Config/secret class | Server/public | Environments | Validation/rotation | Trust boundary | Owner |
| --- | --- | --- | --- | --- | --- |

## Failure and operations evidence

| Mechanism/integration | Deadline/retry/idempotency/degraded policy | Required `EVID-*` test/lab | Telemetry/alert/runbook | Evidence status/result/owner |
| --- | --- | --- | --- | --- |

## Acceptance

- Provider/ORM/framework types contained inside adapters:
- Demo side effects isolated:
- Selected migration and worker execution paths proven:
- Blocking gaps/expiry:
- Accepted / reviewer / date:
